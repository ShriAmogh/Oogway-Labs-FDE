from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional
from pydantic import BaseModel

class AgentEvent(BaseModel):
    event: str # 'thinking', 'token', 'citation', 'artifact', 'done', 'error'
    data: Dict[str, Any]

class BaseAgent(ABC):
    """Abstract base class for conversational agents."""
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        query: str,
        session_id: str,
        model_name: Optional[str] = None,
        enable_ship30: bool = False,
        system_prompt_override: Optional[str] = None
    ) -> AsyncGenerator[AgentEvent, None]:
        """Stream conversational response with tool execution events."""
        pass
