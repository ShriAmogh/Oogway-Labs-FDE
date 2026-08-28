import asyncio
from typing import List
import numpy as np
from app.core.config import settings
from app.core.logging import logger

_model = None

def get_local_embedder():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local embedding model: {settings.LOCAL_EMBEDDING_MODEL}")
            _model = SentenceTransformer(settings.LOCAL_EMBEDDING_MODEL)
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}")
            raise e
    return _model

async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate dense vector embeddings for a list of strings.
    Uses local sentence-transformers running on CPU/GPU or Gemini API.
    """
    if not texts:
        return []
        
    if settings.EMBEDDING_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Batch call to Gemini embedding
            embeddings = []
            for text in texts:
                result = await asyncio.to_thread(
                    client.models.embed_content,
                    model="text-embedding-004",
                    contents=text
                )
                embeddings.append(result.embedding.values)
            return embeddings
        except Exception as e:
            logger.warning(f"Gemini embedding failed, falling back to local embedder: {e}")
            
    # Default: Fast, local CPU-friendly SentenceTransformer
    embedder = get_local_embedder()
    # Run CPU intensive embedding in threadpool with batch_size=64
    embeddings = await asyncio.to_thread(
        embedder.encode,
        texts,
        batch_size=64,
        show_progress_bar=False,
        normalize_embeddings=True
    )
    return [emb.tolist() for emb in embeddings]

async def generate_query_embedding(query: str) -> List[float]:
    """Generate embedding for a single search query."""
    embeddings = await generate_embeddings([query])
    return embeddings[0] if embeddings else [0.0] * settings.EMBEDDING_DIMENSION
