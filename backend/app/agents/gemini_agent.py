import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.agents.base import BaseAgent, AgentEvent
from app.agents.tools.rag_search_tool import execute_rag_search
from app.agents.tools.ship30_essay_tool import SHIP30_SYSTEM_PROMPT, format_ship30_prompt
from app.agents.tools.artifact_gen_tool import parse_generated_artifacts

DEFAULT_SYSTEM_PROMPT = """You are "The Lenny Growth Assistant", a world-class AI advisor for Product Managers, Founders, and Growth Leaders.
Your expertise is strictly grounded in the knowledge base of Lenny's Podcast transcripts.

Guidelines:
1. Synthesize & Explain: When relevant transcript excerpts are provided in the context below, synthesize a comprehensive, tactical, and structured response explaining the guest's core frameworks, examples, and advice.
2. Inline Citations: ALWAYS insert inline citations in square brackets directly after factual claims, frameworks, or advice, formatted as `[<Guest Name> – <Episode Topic>, Source <N>]` or `[Source <N>]` (e.g. `[Brian Chesky – New Playbook, Source 1]`).
3. Strict Refusal Rule: ONLY refuse if the retrieved context is empty or marked as NO_GROUNDED_TRANSCRIPTS_FOUND (i.e. the topic is not covered in Lenny's podcast archive). In that case, respond exactly:
"I don't have sufficient evidence in the transcript knowledge base to answer that."
4. When transcript sources are present in the context, ALWAYS answer by breaking down the insights, playbooks, and frameworks from those sources.
5. When asked for frameworks, checklists, or interactive tools, you can create structured artifacts using the syntax:
```artifact
title: "<Title>"
type: "markdown" | "html"
---
<Content>
```
For HTML artifacts, provide clean, standalone, responsive HTML/CSS using dark modern styling.
"""

class GeminiAgent(BaseAgent):
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = settings.GEMINI_API_KEY
        
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        query: str,
        session_id: str,
        model_name: Optional[str] = None,
        enable_ship30: bool = False,
        system_prompt_override: Optional[str] = None
    ) -> AsyncGenerator[AgentEvent, None]:
        selected_model = model_name or settings.GEMINI_MODEL 
        
        # Step 1: Execute Hybrid RAG Search
        yield AgentEvent(event="thinking", data={"stage": "retrieving", "message": "Searching transcript knowledge base..."})
        
        context_str, citations = await execute_rag_search(self.db, query, top_k=settings.FINAL_TOP_K)
        
        # Emit citations to client early
        for cit in citations:
            yield AgentEvent(event="citation", data=cit)
            
        yield AgentEvent(event="thinking", data={"stage": "generating", "message": f"Synthesizing response with {selected_model}..."})

        # Step 2: Prepare Prompt
        system_inst = system_prompt_override or (SHIP30_SYSTEM_PROMPT if enable_ship30 else DEFAULT_SYSTEM_PROMPT)
        
        if enable_ship30:
            user_content = format_ship30_prompt(query, context_str)
        else:
            grounding_prompt = f"""
Transcript Knowledge Base:
---
{context_str}
---

User Query: {query}
"""
            user_content = grounding_prompt
            
        full_response_text = ""
        
        # Step 3: Stream from Gemini API using google-genai
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=self.api_key or "dummy_key")
            
            # Use configured model from env
            model_to_use = selected_model or settings.GEMINI_MODEL 
            
            # Format chat history
            contents = []
            for m in messages[-6:]: # Keep last 6 context messages
                role = "user" if m.get("role") == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=m.get("content", ""))]
                ))
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_content)]
            ))
            
            config = types.GenerateContentConfig(
                system_instruction=system_inst,
                temperature=0.3 if not enable_ship30 else 0.7,
                max_output_tokens=3500 if enable_ship30 else 2048,
            )
            
            def _call_gemini():
                return client.models.generate_content(
                    model=model_to_use,
                    contents=contents,
                    config=config
                )
            
            response = await asyncio.to_thread(_call_gemini)
            if response.text:
                full_response_text = response.text
                # Stream out tokens smoothly to SSE subscribers
                step = 16
                for i in range(0, len(full_response_text), step):
                    chunk_text = full_response_text[i:i+step]
                    yield AgentEvent(event="token", data={"delta": chunk_text})
                    await asyncio.sleep(0.005)
                    
        except Exception as e:
            logger.error(f"Error in Gemini streaming generation: {e}")
            if not citations or "NO_GROUNDED_TRANSCRIPTS_FOUND" in context_str:
                fallback_msg = "I don't have sufficient evidence in the transcript knowledge base to answer that."
            else:
                fallback_msg = f"*(Note: Gemini API generation encountered: {str(e)}. Displaying grounded transcript context below:)*\n\n{context_str}"
            full_response_text += fallback_msg
            yield AgentEvent(event="token", data={"delta": fallback_msg})

        # Step 4: Parse Artifacts if any
        cleaned_text, artifacts = parse_generated_artifacts(full_response_text)
        for art in artifacts:
            yield AgentEvent(event="artifact", data=art)
            
        yield AgentEvent(event="done", data={
            "final_text": full_response_text,
            "citations_count": len(citations),
            "artifacts_count": len(artifacts)
        })
