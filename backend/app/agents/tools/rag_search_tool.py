from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.rag.retriever import retrieve_hybrid_grounded_chunks, RetrievedChunk
from app.core.logging import logger

async def execute_rag_search(
    db: AsyncSession,
    query: str,
    top_k: int = 5
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Executes hybrid RAG search over Lenny's Podcast transcripts.
    Returns:
        context_str: Formatted context string for LLM injection
        citations: List of citation metadata objects
    """
    chunks = await retrieve_hybrid_grounded_chunks(db, query, top_k=top_k)
    
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
        
        # Build citation object
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
