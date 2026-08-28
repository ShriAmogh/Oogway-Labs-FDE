from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

from app.core.database import get_db, AsyncSessionLocal
from app.core.logging import logger
from app.models.schemas import IngestRequest, IngestionStatusResponse
from app.rag.ingest import seed_sample_transcripts_if_empty, ingest_transcripts_from_directory

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

# In-memory ingestion state tracking
_INGESTION_STATE = {
    "is_ingesting": False,
    "last_ingested_at": None,
    "status_message": "Ready"
}

async def _run_ingest_task(use_sample: bool, limit: int = None):
    global _INGESTION_STATE
    _INGESTION_STATE["is_ingesting"] = True
    _INGESTION_STATE["status_message"] = "Ingestion in progress..."
    
    try:
        async with AsyncSessionLocal() as db:
            if use_sample:
                await seed_sample_transcripts_if_empty(db)
            else:
                await ingest_transcripts_from_directory(db, limit=limit)
                
        _INGESTION_STATE["last_ingested_at"] = datetime.utcnow()
        _INGESTION_STATE["status_message"] = "Ingestion completed successfully."
    except Exception as e:
        logger.error(f"Background ingestion failed: {e}")
        _INGESTION_STATE["status_message"] = f"Ingestion error: {str(e)}"
    finally:
        _INGESTION_STATE["is_ingesting"] = False

from app.rag.ingest import seed_sample_transcripts_if_empty, ingest_transcripts_from_directory, _INGESTION_PROGRESS

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

@router.get("/status", response_model=IngestionStatusResponse)
async def get_ingestion_status(db: AsyncSession = Depends(get_db)):
    """Check current transcript indexing progress and chunk statistics."""
    total_chunks = 0
    total_episodes = 0
    
    try:
        c_res = await db.execute(text("SELECT COUNT(*) FROM transcript_chunks;"))
        total_chunks = c_res.scalar() or 0
        
        e_res = await db.execute(text("SELECT COUNT(DISTINCT episode_slug) FROM transcript_chunks;"))
        total_episodes = e_res.scalar() or 0
    except Exception as e:
        logger.error(f"Error querying ingestion stats: {e}")

    is_ingesting = _INGESTION_PROGRESS.get("is_ingesting", False)
    if is_ingesting:
        cur = _INGESTION_PROGRESS.get("current_file", 0)
        tot = _INGESTION_PROGRESS.get("total_files", 0)
        guest = _INGESTION_PROGRESS.get("current_guest", "")
        status_msg = f"Indexing [{cur}/{tot}] {guest} ({total_chunks} chunks)..."
    else:
        status_msg = f"Ready ({total_chunks} chunks indexed across {total_episodes} episodes)"

    return IngestionStatusResponse(
        is_ingesting=is_ingesting,
        total_episodes=total_episodes,
        total_chunks=total_chunks,
        last_ingested_at=datetime.utcnow() if total_chunks > 0 else None,
        status_message=status_msg
    )

@router.post("/trigger")
async def trigger_ingestion(
    req: IngestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger background transcript ingestion."""
    global _INGESTION_STATE
    if _INGESTION_STATE["is_ingesting"]:
        raise HTTPException(status_code=409, detail="Ingestion is already running")
        
    background_tasks.add_task(_run_ingest_task, req.use_sample_data, req.limit_episodes)
    return {"message": "Ingestion job started in background", "use_sample": req.use_sample_data}
