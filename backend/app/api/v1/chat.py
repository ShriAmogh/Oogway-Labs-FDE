import json
import time
import uuid
from datetime import datetime
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.config import settings
from app.core.database import get_db, AsyncSessionLocal
from app.core.logging import logger
from app.models.database import SessionModel, MessageModel, CitationModel, ArtifactModel
from app.models.schemas import ChatRequest, MessageResponse
from app.agents.router import AgentRouter

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/stream")
async def chat_stream_endpoint(request_in: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Streaming chat endpoint via Server-Sent Events (SSE).
    Emits real-time tokens, thinking phases, citations, and generated artifacts.
    Persists user & assistant messages to PostgreSQL upon completion.
    """
    start_time = time.time()
    
    # 1. Resolve or Create Session
    session_id = request_in.session_id
    generated_title = request_in.message[:45] + ("..." if len(request_in.message) > 45 else "")
    
    if not session_id:
        new_session = SessionModel(
            id=str(uuid.uuid4()),
            title=generated_title,
            model_provider=request_in.model_provider or "gemini",
            model_name=request_in.model_name or settings.GEMINI_MODEL
        )
        db.add(new_session)
        await db.commit()
        session_id = new_session.id
    else:
        sess_q = select(SessionModel).where(SessionModel.id == session_id)
        res = await db.execute(sess_q)
        sess = res.scalar_one_or_none()
        if not sess:
            new_session = SessionModel(
                id=session_id,
                title=generated_title,
                model_provider=request_in.model_provider or "gemini",
                model_name=request_in.model_name or settings.GEMINI_MODEL
            )
            db.add(new_session)
            await db.commit()
        elif sess.title in ["New Conversation", "New Session", ""] or not sess.title:
            sess.title = generated_title
            await db.commit()

    # 2. Persist User Message
    model_to_record = request_in.model_name or (
        settings.GEMINI_MODEL if (request_in.model_provider or "gemini") == "gemini" else settings.OLLAMA_MODEL
    )

    user_msg_id = str(uuid.uuid4())
    user_msg = MessageModel(
        id=user_msg_id,
        session_id=session_id,
        role="user",
        content=request_in.message,
        model=model_to_record,
        created_at=datetime.utcnow()
    )
    db.add(user_msg)
    await db.commit()

    # Clean query and detect /ship30for30 slash command
    clean_query = request_in.message.strip()
    enable_ship30 = bool(request_in.enable_ship30)
    
    if clean_query.lower().startswith("/ship30for30"):
        enable_ship30 = True
        clean_query = clean_query[len("/ship30for30"):].strip()
        if not clean_query:
            clean_query = request_in.message

    # 3. Load Recent History for Context
    history_q = (
        select(MessageModel)
        .where(MessageModel.session_id == session_id)
        .order_by(MessageModel.created_at.asc())
    )
    hist_res = await db.execute(history_q)
    history_records = hist_res.scalars().all()
    
    messages_payload = [
        {"role": m.role, "content": m.content}
        for m in history_records[:-1] # exclude current query which is passed directly
    ]

    async def sse_event_generator() -> AsyncGenerator[str, None]:
        # Emit initial session_id confirmation
        yield f"event: session\ndata: {json.dumps({'session_id': session_id, 'user_message_id': user_msg_id})}\n\n"
        
        # We create a dedicated DB session for streaming worker
        async with AsyncSessionLocal() as stream_db:
            router_instance = AgentRouter(stream_db)
            
            accumulated_tokens = []
            citations_collected = []
            artifacts_collected = []
            
            try:
                async for event in router_instance.route_and_stream(
                    messages=messages_payload,
                    query=clean_query,
                    session_id=session_id,
                    provider=request_in.model_provider,
                    model_name=request_in.model_name,
                    enable_ship30=enable_ship30,
                    system_prompt_override=request_in.system_prompt_override
                ):
                    event_type = event.event
                    event_data = event.data
                    
                    if event_type == "token":
                        delta = event_data.get("delta", "")
                        accumulated_tokens.append(delta)
                    elif event_type == "citation":
                        citations_collected.append(event_data)
                    elif event_type == "artifact":
                        artifacts_collected.append(event_data)
                        
                    payload_json = json.dumps(event_data)
                    yield f"event: {event_type}\ndata: {payload_json}\n\n"
                    
                # 4. Stream Completed -> Persist Assistant Response in PostgreSQL
                latency = round((time.time() - start_time) * 1000, 2)
                full_text = "".join(accumulated_tokens)
                
                assistant_msg_id = str(uuid.uuid4())
                asst_msg = MessageModel(
                    id=assistant_msg_id,
                    session_id=session_id,
                    role="assistant",
                    content=full_text,
                    model=model_to_record,
                    latency_ms=latency,
                    created_at=datetime.utcnow()
                )
                stream_db.add(asst_msg)
                
                # Save Citations
                for cit in citations_collected:
                    c_model = CitationModel(
                        id=str(uuid.uuid4()),
                        message_id=assistant_msg_id,
                        episode_title=cit.get("episode_title", "Lenny's Podcast"),
                        guest=cit.get("guest"),
                        timestamp_or_section=cit.get("timestamp_or_section"),
                        url=cit.get("url"),
                        quote=cit.get("quote", ""),
                        relevance_score=cit.get("relevance_score", 1.0)
                    )
                    stream_db.add(c_model)
                    
                # Save Artifacts
                for art in artifacts_collected:
                    a_model = ArtifactModel(
                        id=art.get("id") or str(uuid.uuid4()),
                        session_id=session_id,
                        message_id=assistant_msg_id,
                        title=art.get("title", "Artifact"),
                        artifact_type=art.get("artifact_type", "markdown"),
                        content=art.get("content", ""),
                        version=1
                    )
                    stream_db.add(a_model)
                    
                # Update Session updated_at timestamp
                upd_sess = update(SessionModel).where(SessionModel.id == session_id).values(updated_at=datetime.utcnow())
                await stream_db.execute(upd_sess)
                await stream_db.commit()
                
                # Emit final message saved event
                yield f"event: message_saved\ndata: {json.dumps({'message_id': assistant_msg_id, 'latency_ms': latency})}\n\n"
                
            except Exception as e:
                logger.error(f"Error during SSE generation: {e}")
                err_data = json.dumps({"error": str(e)})
                yield f"event: error\ndata: {err_data}\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
