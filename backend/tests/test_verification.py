import pytest
import uuid
from datetime import datetime
from app.models.database import CitationModel, MessageModel, ArtifactModel, SessionModel
from app.models.schemas import CitationSchema, MessageResponse, ArtifactSchema, SessionDetailResponse
from app.rag.chunker import parse_transcript_markdown, chunk_transcript
from app.rag.retriever import compute_rrf_fusion
from app.core.security import sanitize_html, wrap_sandboxed_html_document
from app.agents.tools.ship30_essay_tool import format_ship30_prompt

def test_citation_model_validation():
    cit = CitationModel(
        id=str(uuid.uuid4()),
        message_id=str(uuid.uuid4()),
        episode_title="Brian Chesky on Founder Mode",
        guest="Brian Chesky",
        timestamp_or_section="Founder Mode",
        url="https://lennyspodcast.com/brian-chesky",
        quote="Founder Mode means staying in the details.",
        relevance_score=0.95,
        created_at=datetime.utcnow()
    )
    # Validate from ORM model
    schema = CitationSchema.model_validate(cit)
    assert schema.episode_title == "Brian Chesky on Founder Mode"
    assert schema.guest == "Brian Chesky"
    assert schema.relevance_score == 0.95

def test_message_response_with_citations_and_artifacts():
    msg_id = str(uuid.uuid4())
    sess_id = str(uuid.uuid4())
    
    msg = MessageModel(
        id=msg_id,
        session_id=sess_id,
        role="assistant",
        content="Here is Chesky's advice on Founder Mode.",
        model="gemini-2.5-flash",
        tokens_used=150,
        latency_ms=1250.0,
        created_at=datetime.utcnow()
    )
    
    cit = CitationModel(
        id=str(uuid.uuid4()),
        message_id=msg_id,
        episode_title="Brian Chesky",
        guest="Brian Chesky",
        timestamp_or_section="Introduction",
        url="https://lennyspodcast.com",
        quote="Quote text",
        relevance_score=1.0,
        created_at=datetime.utcnow()
    )
    
    art = ArtifactModel(
        id=str(uuid.uuid4()),
        session_id=sess_id,
        message_id=msg_id,
        title="2-Release Roadmap",
        artifact_type="markdown",
        content="# Roadmap",
        version=1,
        created_at=datetime.utcnow()
    )
    
    msg_resp = MessageResponse(
        id=msg.id,
        session_id=msg.session_id,
        role=msg.role,
        content=msg.content,
        model=msg.model,
        tokens_used=msg.tokens_used,
        latency_ms=msg.latency_ms,
        citations=[CitationSchema.model_validate(cit)],
        artifacts=[ArtifactSchema.model_validate(art)],
        created_at=msg.created_at
    )
    assert len(msg_resp.citations) == 1
    assert msg_resp.citations[0].guest == "Brian Chesky"
    assert len(msg_resp.artifacts) == 1
    assert msg_resp.artifacts[0].title == "2-Release Roadmap"

def test_rrf_math():
    dense = [{"id": "doc1", "episode_title": "A", "guest": "A", "speaker": "A", "header_section": "A", "url": "", "content": ""}]
    sparse = [{"id": "doc1", "episode_title": "A", "guest": "A", "speaker": "A", "header_section": "A", "url": "", "content": ""}]
    fused = compute_rrf_fusion(dense, sparse, k=60)
    assert len(fused) == 1
    assert round(fused[0].rrf_score, 6) == round((1/61) + (1/61), 6)

def test_security_sanitization():
    xss = "<script>alert(1)</script><div class='test'>Safe Content</div>"
    sanitized = sanitize_html(xss)
    assert "<script>" not in sanitized
    assert "Safe Content" in sanitized
