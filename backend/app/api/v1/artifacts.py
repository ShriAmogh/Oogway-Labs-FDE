from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.security import wrap_sandboxed_html_document
from app.models.database import ArtifactModel
from app.models.schemas import ArtifactSchema

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])

@router.get("/{artifact_id}", response_model=ArtifactSchema)
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve an artifact by its unique ID."""
    q = select(ArtifactModel).where(ArtifactModel.id == artifact_id)
    res = await db.execute(q)
    art = res.scalar_one_or_none()
    
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    return ArtifactSchema.model_validate(art)

@router.get("/{artifact_id}/raw")
async def get_artifact_raw_html(artifact_id: str, db: AsyncSession = Depends(get_db)):
    """
    Renders the artifact as a complete, sandboxed HTML document with CSP.
    Used for safe embedding inside isolated iframe components.
    """
    q = select(ArtifactModel).where(ArtifactModel.id == artifact_id)
    res = await db.execute(q)
    art = res.scalar_one_or_none()
    
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    if art.artifact_type == "html":
        full_html = wrap_sandboxed_html_document(art.content, title=art.title)
    else:
        # Markdown or raw content fallback
        escaped_content = art.content.replace("<", "&lt;").replace(">", "&gt;")
        full_html = wrap_sandboxed_html_document(f"<pre>{escaped_content}</pre>", title=art.title)
        
    return Response(
        content=full_html,
        media_type="text/html",
        headers={
            "Content-Security-Policy": (
                "default-src 'none'; "
                "style-src 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
                "font-src https://fonts.gstatic.com; "
                "script-src 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src data: https:; "
                "connect-src 'none';"
            ),
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN"
        }
    )

@router.get("/session/{session_id}", response_model=List[ArtifactSchema])
async def list_session_artifacts(session_id: str, db: AsyncSession = Depends(get_db)):
    """List all artifacts generated within a session."""
    q = select(ArtifactModel).where(ArtifactModel.id == session_id).order_by(ArtifactModel.created_at.desc())
    res = await db.execute(q)
    return [ArtifactSchema.model_validate(a) for a in res.scalars().all()]
