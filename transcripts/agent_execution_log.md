# Coding Agent Trajectory & Execution Log
## The Lenny Growth Assistant Deployment

--- ## 1. Engagement Overview & Milestones

This log documents the autonomous implementation, verification, and problem-solving trajectory of Antigravity AI pair programming during the construction of **The Lenny Growth Assistant**.

### Key Deliverables Completed:
1. **Full-Stack Application**: FastAPI Backend + PostgreSQL (`pgvector`) + React 18 / TypeScript Frontend.
2. **Hybrid RAG Retrieval Engine**: Dense Vector Search + PostgreSQL Full-Text Search + Reciprocal Rank Fusion (RRF $k=60$) + Candidate Reranker.
3. **Speaker-Aware Chunking**: Markdown Frontmatter parsing, speaker turns, and 600-token sliding window with 150-token overlap.
4. **Agent Layer**: Google Gemini SDK (`google-genai`) for Cloud LLM + Local Ollama (`llama3.2`) with runtime toggle.
5. **Ship 30 for 30 Content Skill**: Dedicated essay structure generator (~1,250 words, hook, 1-3-1 cadence, bolding, tactical takeaway).
6. **In-App Artifact Viewer**: Isolated split-screen sandbox (`sandbox="allow-scripts"`, strict CSP, server-side Bleach sanitization).
7. **Complete Documentation Suite**: `PRD.md`, `design.md`, `architecture.md`, `README.md`, automated unit tests.

--- ## 2. Iterations, Challenges & Corrections

### Challenge 1: Document Conversion Tooling
- **Initial State**: Assignment was provided in `.docx` binary format.
- **Action**: Built a Python script parsing `word/document.xml` to convert all headings, tables, bullet points, and hyperlinks into [Forward_Deployed_Engineer_Take_Home_Assignment.md](file:///Users/amogharora/fde_assignment/Forward_Deployed_Engineer_Take_Home_Assignment.md).

### Challenge 2: Architectural Alignment with User Requirements
- **User Directives**:
  1. Replace Claude with Google Gemini SDK (`google-genai`).
  2. Implement RAG using PostgreSQL with `pgvector` in Docker container.
  3. Add Reciprocal Rank Fusion (RRF) and Cross-Candidate Reranking.
  4. Ensure transcript chunking utilizes sliding token overlap.
- **Resolution**:
  - Implemented `GeminiAgent` using the official `google-genai` client with streaming.
  - Implemented `pgvector` integration in SQLAlchemy async with HNSW index and TSVECTOR full-text search.
  - Implemented `compute_rrf_fusion` in `app/rag/retriever.py` with standard $k=60$ constant and reranker.
  - Implemented `chunk_transcript` in `app/rag/chunker.py` with 600-token target and 150-token overlap retaining speaker metadata.

### Challenge 3: Artifact Sandboxing & Security
- **Security Requirement**: Render untrusted LLM-generated HTML without introducing XSS vulnerabilities.
- **Resolution**:
  - Configured `sandbox="allow-scripts"` while strictly omitting `allow-same-origin` and `allow-top-navigation`.
  - Added strict CSP meta tags (`connect-src 'none'; default-src 'none';`) and server-side Bleach sanitization.

--- ## 3. Verification Summary

| Test Suite / Area | Tested Functionality | Result |
| :--- | :--- | :--- |
| `tests/test_chunker.py` | Frontmatter parsing & sliding token overlap | Passed |
| `tests/test_rrf.py` | Reciprocal Rank Fusion math & candidate scoring | Passed |
| `tests/test_security.py` | HTML Bleach sanitization & CSP header injection | Passed |
| API Contracts | Health, Sessions, Chat SSE stream, Artifacts | Validated |
