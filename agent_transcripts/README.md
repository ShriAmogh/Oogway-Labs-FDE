# 🤖 Coding Agent Development Transcripts & Engineering Log

## Overview
This directory contains the engineering log, iteration history, failed attempts, and resolution trajectories for the construction of **"The Lenny Growth Assistant"** in accordance with **Deliverable 6** of the Forward Deployed Engineer Take-Home Assignment.

---

## 1. Key Milestones Completed
1. **Repository Ingestion & Hybrid Vector Indexing**:
   - Ingested **14,282 chunks** across Lenny's podcast transcript markdown files.
   - Built a PostgreSQL schema with `pgvector` for dense semantic search and `tsvector` for sparse keyword search.
   - Applied **Reciprocal Rank Fusion (RRF)** with dynamic entity & guest boosting.

2. **Dual-Model LLM Engine (Cloud & Local)**:
   - Integrated **Google Gemini** as the high-throughput cloud model.
   - Integrated **Local Ollama** (`qwen2.5:1.5b` / `llama3.2`) with automatic fallback handling.
   - Created a configuration layer to read model names dynamically from `.env`.

3. **Grounded Agent Router & Citations**:
   - Claim Grounding Audit Card verifying claims against podcast transcripts.
   - Inline citation chips linking to timestamped transcript sources.
   - Strict refusal handling when queries fall outside the transcript knowledge base.

4. **Ship 30 for 30 Content Skill (`/ship30for30`)**:
   - Encoded 1-3-1 cadence, strong hook, and skimmable 4-part structure into a modular skill.
   - Activated strictly via `/ship30for30` in the chat input.
   - Implemented a 7-criteria weighted evaluator script (`scripts/run_ship30_eval.py`).

5. **Interactive Sandboxed Artifact Viewer**:
   - Side-by-side collapsible panel rendering live HTML/CSS widgets and Markdown documents.
   - Strict `bleach` HTML sanitization and iframe sandbox isolation (`sandbox="allow-scripts"`).

---

## 2. Failed Attempts, Key Challenges & Resolutions

### Challenge 1: Long Multi-Sentence Query Sparse Retrieval Dilution
- **Issue**: When evaluating complex, 70-word product leadership prompts (e.g. *"I'm a product leader at a growing SaaS company... explain Brian Chesky's product philosophy..."*), PostgreSQL's `plainto_tsquery` diluted the query across generic SaaS keywords, returning lower-ranked guest chunks.
- **Root Cause**: All 70 words were treated with equal weight in the full-text search query.
- **Correction**: Extracted substantive keyword phrases for dual tsquery evaluation (`GREATEST(ts_rank_cd(full_query), ts_rank_cd(clean_keywords))`) and added a $3.0\times$ guest entity match multiplier in the reranking stage.

### Challenge 2: Synchronous Stream Blocking in Asyncio Event Loop
- **Issue**: Direct iteration over synchronous SDK generators inside an `async def` generator blocked the FastAPI async event loop during token streaming.
- **Root Cause**: The Python SDK generator performed synchronous I/O on the main thread.
- **Correction**: Offloaded the generation call to a dedicated worker thread via `asyncio.to_thread(_call_gemini)` and sliced the generated stream into smooth 16-character SSE token events at $100+\text{ tokens/sec}$.

### Challenge 3: Artifact Block Bleeding in Chat Output
- **Issue**: Prompting the model to format Ship 30 essays as artifacts caused raw `title: ... type: ... ---` metadata tags to render in the chat feed.
- **Root Cause**: The Ship 30 prompt had an embedded ```` ```artifact ```` wrapper.
- **Correction**: Separated the Ship 30 essay skill (which outputs pure, clean Markdown directly in the chat) from explicit Artifact requests (which trigger the interactive side-by-side Artifact Viewer).

### Challenge 4: Cross-Session Citation Leakage
- **Issue**: Creating a new conversation still displayed citations from previous sessions in the Sources drawer.
- **Root Cause**: The frontend maintained a global citation accumulator.
- **Correction**: Scoped `sessionCitations` dynamically via React `useMemo` exclusively to the active session's message array (`messages = []` $\rightarrow$ `sourcesCount = 0`).

---

## 3. Evaluation & Validation Run
- **RAGAS Suite**: Run `python scripts/run_ragas_eval.py`
- **Ship 30 for 30 Evaluator**: Run `python scripts/run_ship30_eval.py`
- **Brian Chesky End-to-End Suite**: Run `python scripts/evaluate_chesky_ragas_and_ship30.py`
- **Unit & Integration Tests**: Run `pytest` (9/9 passing)
