from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Citation Schemas
class CitationSchema(BaseModel):
    id: Optional[str] = None
    episode_title: str
    guest: Optional[str] = None
    timestamp_or_section: Optional[str] = None
    url: Optional[str] = None
    quote: str
    relevance_score: float = 1.0

    class Config:
        from_attributes = True

# Artifact Schemas
class ArtifactSchema(BaseModel):
    id: Optional[str] = None
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    title: str
    artifact_type: str = "markdown" # 'markdown', 'html', 'svg'
    content: str
    version: int = 1
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Message Schemas
class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    model: Optional[str] = None
    tokens_used: int = 0
    latency_ms: float = 0.0
    citations: List[CitationSchema] = []
    artifacts: List[ArtifactSchema] = []
    created_at: datetime

    class Config:
        from_attributes = True

# Session Schemas
class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    model_provider: Optional[str] = "gemini"
    model_name: Optional[str] = "gemini-2.5-flash"

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None

class SessionResponse(BaseModel):
    id: str
    title: str
    model_provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True

class SessionDetailResponse(BaseModel):
    id: str
    title: str
    model_provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    artifacts: List[ArtifactSchema] = []

    class Config:
        from_attributes = True

# Chat Stream / Request Schemas
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    model_provider: Optional[str] = "gemini" # 'gemini' or 'ollama'
    model_name: Optional[str] = None
    enable_ship30: Optional[bool] = False
    system_prompt_override: Optional[str] = None

class StreamChunkResponse(BaseModel):
    event: str # 'thinking', 'token', 'citation', 'artifact', 'done', 'error'
    data: Dict[str, Any]

# Ingestion Schemas
class IngestRequest(BaseModel):
    force_refresh: bool = False
    limit_episodes: Optional[int] = None
    use_sample_data: bool = False

class IngestionStatusResponse(BaseModel):
    is_ingesting: bool
    total_episodes: int
    total_chunks: int
    last_ingested_at: Optional[datetime] = None
    status_message: str

# Health Check Schemas
class HealthResponse(BaseModel):
    status: str
    database: str
    pgvector: bool
    ollama_connected: bool
    gemini_configured: bool
    total_indexed_chunks: int
    gemini_model: Optional[str] = None
    ollama_model: Optional[str] = None
