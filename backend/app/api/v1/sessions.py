from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from typing import List
import uuid

from app.core.config import settings
from app.core.database import get_db
from app.models.database import SessionModel, MessageModel, ArtifactModel, CitationModel
from app.models.schemas import (
    SessionCreate, SessionUpdate, SessionResponse, SessionDetailResponse,
    MessageResponse, ArtifactSchema, CitationSchema
)

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(session_in: SessionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new conversational session."""
    new_session = SessionModel(
        id=str(uuid.uuid4()),
        title=session_in.title or "New Conversation",
        model_provider=session_in.model_provider or "gemini",
        model_name=session_in.model_name or settings.GEMINI_MODEL
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session

@router.get("", response_model=List[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all user sessions ordered by last updated."""
    query = (
        select(SessionModel, func.count(MessageModel.id).label("msg_count"))
        .outerjoin(MessageModel, SessionModel.id == MessageModel.session_id)
        .group_by(SessionModel.id)
        .order_by(SessionModel.updated_at.desc())
    )
    result = await db.execute(query)
    rows = result.all()
    
    sessions_out = []
    for sess, count in rows:
        item = SessionResponse.model_validate(sess)
        item.message_count = count
        sessions_out.append(item)
    return sessions_out

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get complete session history with messages, citations, and artifacts."""
    sess_query = select(SessionModel).where(SessionModel.id == session_id)
    res = await db.execute(sess_query)
    session_obj = res.scalar_one_or_none()
    
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Load messages
    msg_query = (
        select(MessageModel)
        .where(MessageModel.session_id == session_id)
        .order_by(MessageModel.created_at.asc())
    )
    msg_res = await db.execute(msg_query)
    messages = msg_res.scalars().all()
    
    # Load citations for each message
    message_responses = []
    for msg in messages:
        cit_query = select(CitationModel).where(CitationModel.message_id == msg.id)
        cit_res = await db.execute(cit_query)
        citations = cit_res.scalars().all()
        
        art_query = select(ArtifactModel).where(ArtifactModel.message_id == msg.id)
        art_res = await db.execute(art_query)
        artifacts = art_res.scalars().all()
        
        message_responses.append(MessageResponse(
            id=msg.id,
            session_id=msg.session_id,
            role=msg.role,
            content=msg.content,
            model=msg.model,
            tokens_used=msg.tokens_used,
            latency_ms=msg.latency_ms,
            citations=[CitationSchema.model_validate(c) for c in citations],
            artifacts=[ArtifactSchema.model_validate(a) for a in artifacts],
            created_at=msg.created_at
        ))
        
    # Load all session artifacts
    art_all_query = select(ArtifactModel).where(ArtifactModel.session_id == session_id).order_by(ArtifactModel.created_at.asc())
    art_all_res = await db.execute(art_all_query)
    all_artifacts = [ArtifactSchema.model_validate(a) for a in art_all_res.scalars().all()]
    
    return SessionDetailResponse(
        id=session_obj.id,
        title=session_obj.title,
        model_provider=session_obj.model_provider,
        model_name=session_obj.model_name,
        created_at=session_obj.created_at,
        updated_at=session_obj.updated_at,
        messages=message_responses,
        artifacts=all_artifacts
    )

@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, patch_in: SessionUpdate, db: AsyncSession = Depends(get_db)):
    """Update session title or model parameters."""
    sess_query = select(SessionModel).where(SessionModel.id == session_id)
    res = await db.execute(sess_query)
    session_obj = res.scalar_one_or_none()
    
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if patch_in.title is not None:
        session_obj.title = patch_in.title
    if patch_in.model_provider is not None:
        session_obj.model_provider = patch_in.model_provider
    if patch_in.model_name is not None:
        session_obj.model_name = patch_in.model_name
        
    await db.commit()
    await db.refresh(session_obj)
    return session_obj

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a session and all associated messages and artifacts."""
    del_stmt = delete(SessionModel).where(SessionModel.id == session_id)
    await db.execute(del_stmt)
    await db.commit()
    return None
