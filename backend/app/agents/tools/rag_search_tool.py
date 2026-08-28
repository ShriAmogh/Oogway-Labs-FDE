import re
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.rag.retriever import retrieve_hybrid_grounded_chunks, RetrievedChunk
from app.core.logging import logger

META_CONVERSATION_PATTERNS = [
    r"what\s+(was|were|is|are)\s+(the\s+)?(previous|last|prior|earlier|first|second)\s+(question|questions|prompt|prompts|query|queries|message|messages|topic|topics)",
    r"what\s+did\s+(i|we|you)\s+(just\s+)?(ask|say|discuss|talk\s+about|mention|tell\s+me)",
    r"repeat\s+(the\s+)?(previous|last|prior)\s+(question|questions|answer|response)",
    r"summarize\s+(our\s+)?(chat|conversation|discussion|history|thread)",
    r"what\s+have\s+we\s+(talked|discussed|covered)",
    r"what\s+was\s+my\s+(first|last|previous|prior)\s+question",
    r"who\s+are\s+you",
    r"what\s+can\s+you\s+do",
]

def is_meta_conversational_query(query: str) -> bool:
    """Detects if a query is asking about the conversation history/memory itself."""
    q_clean = query.strip().lower()
    for pat in META_CONVERSATION_PATTERNS:
        if re.search(pat, q_clean):
            return True
    return False

def contextualize_search_query(query: str, messages: Optional[List[Dict[str, str]]] = None) -> str:
    """Enriches short or pronoun-heavy follow-up queries with recent conversation context."""
    if not messages or len(messages) == 0:
        return query

    q_clean = query.strip()
    pronoun_pattern = r"\b(he|she|they|his|her|their|it|that|this|the\s+second|the\s+first|the\s+last|above)\b"
    is_short_followup = len(q_clean.split()) <= 6 or bool(re.search(pronoun_pattern, q_clean.lower()))

    if is_short_followup:
        recent_user_texts = [
            m.get("content", "") for m in messages[-4:] 
            if m.get("role") == "user" and not m.get("content", "").startswith("/")
        ]
        if recent_user_texts:
            last_topic = recent_user_texts[-1][:80]
            return f"{last_topic} {q_clean}"

    return query

async def execute_rag_search(
    db: AsyncSession,
    query: str,
    messages: Optional[List[Dict[str, str]]] = None,
    top_k: int = 5
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Executes hybrid RAG search over Lenny's Podcast transcripts with conversational context awareness.
    Returns:
        context_str: Formatted context string for LLM injection
        citations: List of citation metadata objects
    """
    if is_meta_conversational_query(query):
        return ("", [])

    search_query = contextualize_search_query(query, messages)
    chunks = await retrieve_hybrid_grounded_chunks(db, search_query, top_k=top_k)
    
    if not chunks:
        return (
            "NO_GROUNDED_TRANSCRIPTS_FOUND: The internal podcast knowledge base does not contain direct information for this query.",
            []
        )
        
    context_blocks = []
    citations = []
    
    for idx, c in enumerate(chunks, start=1):
        block = (
            f"[Source {idx}]\n"
            f"Episode: {c.episode_title}\n"
            f"Guest: {c.guest or 'Lenny'}\n"
            f"Section: {c.header_section or 'General'}\n"
            f"Content:\n{c.content}\n"
        )
        context_blocks.append(block)
        
        citations.append({
            "episode_title": c.episode_title,
            "guest": c.guest,
            "timestamp_or_section": c.header_section,
            "url": c.url,
            "quote": c.content[:200] + "..." if len(c.content) > 200 else c.content,
            "relevance_score": round(c.final_score, 4)
        })
        
    context_str = "\n---\n".join(context_blocks)
    return context_str, citations
