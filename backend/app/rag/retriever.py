from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.rag.embedder import generate_query_embedding

class RetrievedChunk:
    def __init__(
        self,
        chunk_id: str,
        episode_title: str,
        guest: Optional[str],
        speaker: Optional[str],
        header_section: Optional[str],
        url: Optional[str],
        content: str,
        dense_rank: Optional[int] = None,
        sparse_rank: Optional[int] = None,
        rrf_score: float = 0.0,
        final_score: float = 0.0
    ):
        self.chunk_id = chunk_id
        self.episode_title = episode_title
        self.guest = guest
        self.speaker = speaker
        self.header_section = header_section
        self.url = url
        self.content = content
        self.dense_rank = dense_rank
        self.sparse_rank = sparse_rank
        self.rrf_score = rrf_score
        self.final_score = final_score

from sqlalchemy import text, select, func
from app.models.database import TranscriptChunkModel

async def search_dense(
    db: AsyncSession,
    query_embedding: List[float],
    top_k: int = settings.DENSE_TOP_K,
    min_similarity: float = 0.28
) -> List[Dict[str, Any]]:
    """Dense vector search using native pgvector ORM cosine distance with similarity threshold."""
    try:
        stmt = (
            select(
                TranscriptChunkModel,
                (1 - TranscriptChunkModel.embedding.cosine_distance(query_embedding)).label("similarity")
            )
            .where(TranscriptChunkModel.embedding.isnot(None))
            .where((1 - TranscriptChunkModel.embedding.cosine_distance(query_embedding)) >= min_similarity)
            .order_by(TranscriptChunkModel.embedding.cosine_distance(query_embedding).asc())
            .limit(top_k)
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [
            {
                "id": str(r[0].id),
                "episode_title": r[0].episode_title,
                "guest": r[0].guest,
                "speaker": r[0].speaker,
                "header_section": r[0].header_section,
                "url": r[0].url,
                "content": r[0].content,
                "similarity": float(r[1]) if r[1] is not None else 1.0
            }
            for r in rows
        ]
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in dense search: {e}")
        return []

async def search_sparse(
    db: AsyncSession,
    query_text: str,
    top_k: int = settings.SPARSE_TOP_K
) -> List[Dict[str, Any]]:
    """Sparse keyword search using PostgreSQL Full-Text Search with ts_rank."""
    import re
    # Extract substantive words if query is long
    words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', query_text) if w.lower() not in {"and", "the", "for", "with", "from", "that", "this", "what", "how", "why", "only", "based", "explain"}]
    clean_keyword_query = " ".join(words[:12]) if words else query_text

    query = text("""
        SELECT 
            id, episode_title, guest, speaker, header_section, url, content,
            GREATEST(
                ts_rank_cd(tsv, plainto_tsquery('english', :query_text)),
                ts_rank_cd(tsv, plainto_tsquery('english', :clean_query)),
                ts_rank_cd(tsv, websearch_to_tsquery('english', :clean_query))
            ) AS rank_score
        FROM transcript_chunks
        WHERE tsv @@ plainto_tsquery('english', :query_text)
           OR tsv @@ plainto_tsquery('english', :clean_query)
           OR tsv @@ websearch_to_tsquery('english', :clean_query)
        ORDER BY rank_score DESC
        LIMIT :limit;
    """)
    
    try:
        result = await db.execute(query, {
            "query_text": query_text,
            "clean_query": clean_keyword_query,
            "limit": top_k
        })
        rows = result.fetchall()
        return [
            {
                "id": str(r.id),
                "episode_title": r.episode_title,
                "guest": r.guest,
                "speaker": r.speaker,
                "header_section": r.header_section,
                "url": r.url,
                "content": r.content,
                "rank_score": float(r.rank_score)
            }
            for r in rows
        ]
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in sparse keyword search: {e}")
        return []

def compute_rrf_fusion(
    dense_results: List[Dict[str, Any]],
    sparse_results: List[Dict[str, Any]],
    k: int = settings.RRF_K
) -> List[RetrievedChunk]:
    """
    Combines dense and sparse search rankings using Reciprocal Rank Fusion (RRF).
    Formula: RRF_Score = 1/(k + rank_dense) + 1/(k + rank_sparse)
    """
    chunk_map: Dict[str, RetrievedChunk] = {}
    
    # Process Dense Ranks
    for rank, item in enumerate(dense_results, start=1):
        c_id = item["id"]
        if c_id not in chunk_map:
            chunk_map[c_id] = RetrievedChunk(
                chunk_id=c_id,
                episode_title=item["episode_title"],
                guest=item["guest"],
                speaker=item["speaker"],
                header_section=item["header_section"],
                url=item["url"],
                content=item["content"],
                dense_rank=rank
            )
        else:
            chunk_map[c_id].dense_rank = rank
            
        chunk_map[c_id].rrf_score += 1.0 / (k + rank)

    # Process Sparse Ranks
    for rank, item in enumerate(sparse_results, start=1):
        c_id = item["id"]
        if c_id not in chunk_map:
            chunk_map[c_id] = RetrievedChunk(
                chunk_id=c_id,
                episode_title=item["episode_title"],
                guest=item["guest"],
                speaker=item["speaker"],
                header_section=item["header_section"],
                url=item["url"],
                content=item["content"],
                sparse_rank=rank
            )
        else:
            chunk_map[c_id].sparse_rank = rank
            
        chunk_map[c_id].rrf_score += 1.0 / (k + rank)

    # Sort all merged candidates by RRF score descending
    sorted_chunks = sorted(chunk_map.values(), key=lambda x: x.rrf_score, reverse=True)
    for c in sorted_chunks:
        c.final_score = c.rrf_score
    return sorted_chunks

async def rerank_candidates(
    query_text: str,
    candidates: List[RetrievedChunk],
    top_k: int = settings.FINAL_TOP_K
) -> List[RetrievedChunk]:
    """
    Reranks candidates for maximum precision.
    Applies keyword match density and guest-query relevance boost.
    """
    import re
    if not candidates:
        return []
        
    query_lower = query_text.lower()
    query_words = set(re.findall(r'\b\w{3,}\b', query_lower))
    
    for item in candidates:
        boost = 1.0
        # High boost if full guest name or substantive guest surname appears in query
        if item.guest:
            g_lower = item.guest.lower()
            if g_lower in query_lower:
                boost += 3.0
            elif any(part.lower() in query_words for part in item.guest.split() if len(part) > 3):
                boost += 2.0
                
        # Boost if episode title matches
        ep_lower = item.episode_title.lower()
        title_matches = sum(1 for w in query_words if len(w) > 3 and w in ep_lower)
        boost += title_matches * 0.25
        
        # Content keyword density
        c_lower = item.content.lower()
        content_matches = sum(1 for w in query_words if len(w) > 4 and w in c_lower)
        boost += min(1.0, content_matches * 0.05)
        
        item.final_score = item.rrf_score * boost
        
    reranked = sorted(candidates, key=lambda x: x.final_score, reverse=True)
    return reranked[:top_k]

async def retrieve_hybrid_grounded_chunks(
    db: AsyncSession,
    query_text: str,
    top_k: int = settings.FINAL_TOP_K
) -> List[RetrievedChunk]:
    """
    Full hybrid retrieval pipeline:
    1. Dense Vector search (pgvector with min similarity threshold)
    2. Sparse Keyword search (PostgreSQL FTS)
    3. Reciprocal Rank Fusion (RRF, k=60)
    4. Reranking and top-k selection
    """
    query_emb = await generate_query_embedding(query_text)
    
    dense_hits = await search_dense(db, query_emb, top_k=settings.DENSE_TOP_K)
    sparse_hits = await search_sparse(db, query_text, top_k=settings.SPARSE_TOP_K)
    
    fused_candidates = compute_rrf_fusion(dense_hits, sparse_hits, k=settings.RRF_K)
    
    if settings.ENABLE_RERANKING and fused_candidates:
        final_results = await rerank_candidates(query_text, fused_candidates, top_k=top_k)
    else:
        final_results = fused_candidates[:top_k]
        
    logger.info(
        f"Hybrid retrieval for query '{query_text[:50]}...': "
        f"Dense hits={len(dense_hits)}, Sparse hits={len(sparse_hits)}, "
        f"Selected={len(final_results)}"
    )
    return final_results
