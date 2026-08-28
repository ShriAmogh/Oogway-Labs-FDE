import pytest
from app.rag.retriever import compute_rrf_fusion

def test_rrf_fusion_logic():
    dense_results = [
        {"id": "doc1", "episode_title": "Ep 1", "guest": "Guest A", "speaker": "A", "header_section": "Sec 1", "url": "url1", "content": "Content 1"},
        {"id": "doc2", "episode_title": "Ep 2", "guest": "Guest B", "speaker": "B", "header_section": "Sec 2", "url": "url2", "content": "Content 2"},
    ]
    sparse_results = [
        {"id": "doc2", "episode_title": "Ep 2", "guest": "Guest B", "speaker": "B", "header_section": "Sec 2", "url": "url2", "content": "Content 2"},
        {"id": "doc3", "episode_title": "Ep 3", "guest": "Guest C", "speaker": "C", "header_section": "Sec 3", "url": "url3", "content": "Content 3"},
    ]
    
    fused = compute_rrf_fusion(dense_results, sparse_results, k=60)
    assert len(fused) == 3
    # doc2 appeared in both rankings (rank 2 dense, rank 1 sparse), so it should have highest RRF score
    # Score doc2: 1/(60+2) + 1/(60+1) = 1/62 + 1/61 = 0.016129 + 0.016393 = 0.03252
    # Score doc1: 1/(60+1) = 0.016393
    assert fused[0].chunk_id == "doc2"
    assert fused[0].dense_rank == 2
    assert fused[0].sparse_rank == 1
