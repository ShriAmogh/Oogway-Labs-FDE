import pytest
from app.rag.chunker import parse_transcript_markdown, chunk_transcript, count_tokens

SAMPLE_DOC = """---
title: Testing Growth Loops
guest: Elena Verna
date: 2023-11-20
url: https://lennyspodcast.com/test
---

# Testing Growth Loops

## Section 1: Introduction
Lenny: Welcome Elena.
Elena Verna: Hi Lenny, great to be here.

## Section 2: Core Strategy
Elena Verna: PLG is about instant time to value. You have to remove all friction in the first 5 minutes.
"""

def test_parse_frontmatter():
    fm, body = parse_transcript_markdown(SAMPLE_DOC)
    assert fm.get("title") == "Testing Growth Loops"
    assert fm.get("guest") == "Elena Verna"
    assert "Section 1: Introduction" in body

def test_chunking_with_overlap():
    chunks = chunk_transcript(
        SAMPLE_DOC,
        episode_slug="test-slug",
        target_chunk_tokens=50,
        overlap_tokens=15
    )
    assert len(chunks) >= 1
    assert chunks[0].episode_title == "Testing Growth Loops"
    assert chunks[0].guest == "Elena Verna"
    assert "Elena Verna" in chunks[0].content
