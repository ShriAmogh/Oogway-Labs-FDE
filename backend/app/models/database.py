import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Integer, Float, Computed
)
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base
from app.core.config import settings

class SessionModel(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, default="New Conversation")
    model_provider = Column(String(50), nullable=False, default="gemini")
    model_name = Column(String(100), nullable=False, default="gemini-2.5-flash")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", order_by="MessageModel.created_at")
    artifacts = relationship("ArtifactModel", back_populates="session", cascade="all, delete-orphan", order_by="ArtifactModel.created_at")

class MessageModel(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False) # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    model = Column(String(100), nullable=True)
    tokens_used = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("SessionModel", back_populates="messages")
    citations = relationship("CitationModel", back_populates="message", cascade="all, delete-orphan")
    artifacts = relationship("ArtifactModel", back_populates="message", cascade="all, delete-orphan")

class CitationModel(Base):
    __tablename__ = "citations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    episode_title = Column(String(255), nullable=False)
    guest = Column(String(255), nullable=True)
    timestamp_or_section = Column(String(100), nullable=True)
    url = Column(Text, nullable=True)
    quote = Column(Text, nullable=False)
    relevance_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    message = relationship("MessageModel", back_populates="citations")

class ArtifactModel(Base):
    __tablename__ = "artifacts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(String, ForeignKey("messages.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    artifact_type = Column(String(50), nullable=False) # 'markdown', 'html', 'svg'
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("SessionModel", back_populates="artifacts")
    message = relationship("MessageModel", back_populates="artifacts")

class TranscriptChunkModel(Base):
    __tablename__ = "transcript_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_slug = Column(String(255), nullable=False, index=True)
    episode_title = Column(String(255), nullable=False)
    guest = Column(String(255), nullable=True, index=True)
    publish_date = Column(String(50), nullable=True)
    url = Column(Text, nullable=True)
    chunk_index = Column(Integer, nullable=False)
    speaker = Column(String(100), nullable=True)
    header_section = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    
    # pgvector embedding column
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    
    # Generated column for PostgreSQL Full-Text Search
    tsv = Column(
        TSVECTOR,
        Computed("to_tsvector('english', coalesce(episode_title, '') || ' ' || coalesce(guest, '') || ' ' || coalesce(header_section, '') || ' ' || content)", persisted=True)
    )
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
