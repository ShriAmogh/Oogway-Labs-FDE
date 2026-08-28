import asyncio
import json
import httpx
from typing import AsyncGenerator, Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.agents.base import BaseAgent, AgentEvent
from app.agents.tools.rag_search_tool import execute_rag_search, is_meta_conversational_query
from app.agents.tools.ship30_essay_tool import SHIP30_SYSTEM_PROMPT, format_ship30_prompt
from app.agents.tools.artifact_gen_tool import parse_generated_artifacts

DEFAULT_OLLAMA_SYSTEM_PROMPT = """You are "The Lenny Growth Assistant", a local AI advisor for Product Managers and Growth Leaders.
Your expertise is grounded in the knowledge base of Lenny's Podcast transcripts.

Guidelines:
1. Synthesize & Ground: When transcript excerpts are provided in the context below, synthesize a comprehensive, tactical, and structured response explaining the guest's core frameworks, examples, and advice.
2. Inline Citations: When citing transcript sources, insert inline citations formatted as `[<Guest Name> – <Episode Topic>, Source <N>]` or `[Source <N>]`.
3. Conversational Context & Memory: You have full memory of this ongoing conversation. When the user asks about previous questions, earlier discussion points, or refers back to something said earlier in this conversation (e.g. 'what was the previous question asked', 'explain point 2 further'), answer accurately and directly from the conversation history.
4. Strict Refusal Rule: ONLY refuse if the topic is not covered in Lenny's podcast archive (context is NO_GROUNDED_TRANSCRIPTS_FOUND) and the question is not a conversational history question. In that case, respond exactly:
"I don't have sufficient evidence in the transcript knowledge base to answer that."
5. Artifacts: You can generate formatted artifacts using:
```artifact
title: "<Title>"
type: "markdown" | "html"
---
<Content>
```
"""

class OllamaAgent(BaseAgent):
    def __init__(self, db: AsyncSession):
        self.db = db
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        
    async def get_working_url(self) -> str:
        """Resolve accessible Ollama URL across docker gateway and localhost."""
        urls_to_try = [
            self.base_url,
            "http://host.docker.internal:11434",
            "http://localhost:11434",
            "http://127.0.0.1:11434"
        ]
        for u in urls_to_try:
            if not u:
                continue
            try:
                async with httpx.AsyncClient(timeout=1.0) as client:
                    res = await client.get(f"{u.rstrip('/')}/api/tags")
                    if res.status_code == 200:
                        return u.rstrip('/')
            except Exception:
                continue
        return self.base_url

    async def check_health(self) -> bool:
        """Check if local Ollama server is running and accessible."""
        try:
            url = await self.get_working_url()
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        query: str,
        session_id: str,
        model_name: Optional[str] = None,
        enable_ship30: bool = False,
        system_prompt_override: Optional[str] = None
    ) -> AsyncGenerator[AgentEvent, None]:
        selected_model = model_name or settings.OLLAMA_MODEL or "llama3.2"
        full_response_text = ""
        is_meta = is_meta_conversational_query(query)
        
        # Step 1: Execute Hybrid RAG Search
        yield AgentEvent(event="thinking", data={"stage": "retrieving", "message": "Searching local transcript index..." if not is_meta else "Reviewing conversation history..."})
        
        context_str, citations = await execute_rag_search(self.db, query, messages=messages, top_k=settings.FINAL_TOP_K)
        
        for cit in citations:
            yield AgentEvent(event="citation", data=cit)
            
        yield AgentEvent(event="thinking", data={"stage": "generating", "message": f"Streaming from Local Ollama ({selected_model})..."})

        # Step 2: Prepare Prompt
        system_prompt = system_prompt_override or (SHIP30_SYSTEM_PROMPT if enable_ship30 else DEFAULT_OLLAMA_SYSTEM_PROMPT)
        
        if enable_ship30:
            user_content = format_ship30_prompt(query, context_str)
        elif is_meta or not context_str:
            user_content = query
        else:
            user_content = f"""
[Lenny's Podcast Transcript Knowledge Base]
---
{context_str}
---

Question: {query}
"""

        # Step 3: Stream from Ollama API
        ollama_messages = [{"role": "system", "content": system_prompt}]
        for m in messages[-6:]:
            role = "assistant" if m.get("role") in ["assistant", "model"] else "user"
            ollama_messages.append({"role": role, "content": m.get("content", "")})
        ollama_messages.append({"role": "user", "content": user_content})

        try:
            target_url = await self.get_working_url()
            
            # Verify or resolve model from local tags
            model_to_use = selected_model
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    tags_res = await client.get(f"{target_url}/api/tags")
                    if tags_res.status_code == 200:
                        tags_data = tags_res.json()
                        available_names = [m.get("name", "") for m in tags_data.get("models", [])]
                        if model_to_use not in available_names:
                            for av in available_names:
                                if model_to_use.split(":")[0] in av or av.split(":")[0] in model_to_use:
                                    model_to_use = av
                                    break
                            else:
                                if available_names:
                                    model_to_use = available_names[0]
            except Exception:
                pass
                
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{target_url}/api/chat",
                    json={
                        "model": model_to_use,
                        "messages": ollama_messages,
                        "stream": True,
                        "options": {
                            "temperature": 0.3 if not enable_ship30 else 0.7,
                            "num_predict": 2048
                        }
                    }
                ) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        raise Exception(f"Ollama returned HTTP {response.status_code}: {err_text.decode('utf-8')}")
                        
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            chunk_msg = data.get("message", {}).get("content", "")
                            if chunk_msg:
                                full_response_text += chunk_msg
                                yield AgentEvent(event="token", data={"delta": chunk_msg})
                                
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Error streaming from Ollama: {e}")
            if not citations or "NO_GROUNDED_TRANSCRIPTS_FOUND" in context_str:
                fallback_msg = "I don't have sufficient evidence in the transcript knowledge base to answer that."
            else:
                fallback_msg = (
                    f"\n\n> ⚠️ **Ollama Connection Notice:** Unable to reach local Ollama instance at `{self.base_url}` ({str(e)}).\n"
                    f"> **Grounded Context Retrieved from Knowledge Base:**\n\n{context_str}"
                )
            full_response_text += fallback_msg
            yield AgentEvent(event="token", data={"delta": fallback_msg})

        # Step 4: Parse Artifacts
        cleaned_text, artifacts = parse_generated_artifacts(full_response_text)
        for art in artifacts:
            yield AgentEvent(event="artifact", data=art)
            
        yield AgentEvent(event="done", data={
            "final_text": full_response_text,
            "citations_count": len(citations),
            "artifacts_count": len(artifacts)
        })
