import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "The Lenny Growth Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = Field(default="development", env="ENV")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    # Database (PostgreSQL with pgvector)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_growth",
        env="DATABASE_URL"
    )
    
    # Cloud Model Provider: Google Gemini
    GEMINI_API_KEY: str = Field(env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(env="GEMINI_MODEL")
    
    # Local Model Provider: Ollama
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    OLLAMA_MODEL: str = Field(env="OLLAMA_MODEL")
    DEFAULT_PROVIDER: str = Field(default="gemini", env="DEFAULT_PROVIDER") # "gemini" or "ollama"
    
    # Embeddings & RAG
    EMBEDDING_PROVIDER: str = Field(default="local", env="EMBEDDING_PROVIDER") # "local" or "gemini"
    LOCAL_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384 # 384 for all-MiniLM-L6-v2, 768 for text-embedding-004
    
    # Chunking & Overlap
    CHUNK_SIZE_TOKENS: int = 600
    CHUNK_OVERLAP_TOKENS: int = 150
    
    # Retrieval & RRF
    RRF_K: int = 60
    DENSE_TOP_K: int = 15
    SPARSE_TOP_K: int = 15
    FINAL_TOP_K: int = 5
    MIN_SIMILARITY_THRESHOLD: float = 0.50
    ENABLE_RERANKING: bool = True
    
    # Data Sources
    TRANSCRIPTS_REPO_URL: str = "https://github.com/ChatPRD/lennys-podcast-transcripts"
    TRANSCRIPTS_DIR: str = "/transcripts_data/episodes" if os.path.exists("/transcripts_data/episodes") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "transcripts_data", "episodes")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"

settings = Settings()
