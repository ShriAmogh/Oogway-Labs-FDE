from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import httpx
from app.core.database import get_db
from app.core.config import settings
from app.models.schemas import HealthResponse
from app.rag.ingest import seed_sample_transcripts_if_empty

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """System health check and dependency connectivity verification."""
    db_status = "connected"
    pgvector_status = False
    total_chunks = 0
    
    try:
        res = await db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
        pgvector_status = bool(res.scalar())
        
        count_res = await db.execute(text("SELECT COUNT(*) FROM transcript_chunks;"))
        total_chunks = count_res.scalar() or 0
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    # Check Ollama connectivity across host and localhost
    ollama_ok = False
    urls_to_check = [
        settings.OLLAMA_BASE_URL,
        "http://host.docker.internal:11434",
        "http://localhost:11434"
    ]
    for u in urls_to_check:
        if not u:
            continue
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                r = await client.get(f"{u.rstrip('/')}/api/tags")
                if r.status_code == 200:
                    ollama_ok = True
                    break
        except Exception:
            continue
        
    gemini_configured = bool(settings.GEMINI_API_KEY)
    
    overall_status = "healthy" if db_status == "connected" and pgvector_status else "degraded"
    
    return HealthResponse(
        status=overall_status,
        database=db_status,
        pgvector=pgvector_status,
        ollama_connected=ollama_ok,
        gemini_configured=gemini_configured,
        total_indexed_chunks=total_chunks,
        gemini_model=settings.GEMINI_MODEL,
        ollama_model=settings.OLLAMA_MODEL
    )
