from typing import AsyncGenerator, Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.agents.base import BaseAgent, AgentEvent
from app.agents.gemini_agent import GeminiAgent
from app.agents.ollama_agent import OllamaAgent

class AgentRouter:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.gemini_agent = GeminiAgent(db)
        self.ollama_agent = OllamaAgent(db)
        
    async def route_and_stream(
        self,
        messages: List[Dict[str, str]],
        query: str,
        session_id: str,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        enable_ship30: bool = False,
        system_prompt_override: Optional[str] = None
    ) -> AsyncGenerator[AgentEvent, None]:
        selected_provider = (provider or settings.DEFAULT_PROVIDER or "gemini").lower()
        
        logger.info(f"Routing request to provider: {selected_provider}, model: {model_name}")
        
        if selected_provider == "ollama":
            # Check if Ollama is responsive; if not, warn or fallback
            is_healthy = await self.ollama_agent.check_health()
            if not is_healthy:
                logger.warning("Ollama is not running locally. Attempting fallback to Gemini if configured.")
                if settings.GEMINI_API_KEY:
                    yield AgentEvent(event="thinking", data={
                        "stage": "fallback",
                        "message": "Local Ollama is offline. Automatically failing over to Google Gemini..."
                    })
                    async for event in self.gemini_agent.chat_stream(
                        messages=messages,
                        query=query,
                        session_id=session_id,
                        model_name=None,
                        enable_ship30=enable_ship30,
                        system_prompt_override=system_prompt_override
                    ):
                        yield event
                    return
                    
            async for event in self.ollama_agent.chat_stream(
                messages=messages,
                query=query,
                session_id=session_id,
                model_name=model_name,
                enable_ship30=enable_ship30,
                system_prompt_override=system_prompt_override
            ):
                yield event
        else:
            # Default: Gemini Cloud Agent
            async for event in self.gemini_agent.chat_stream(
                messages=messages,
                query=query,
                session_id=session_id,
                model_name=model_name,
                enable_ship30=enable_ship30,
                system_prompt_override=system_prompt_override
            ):
                yield event
