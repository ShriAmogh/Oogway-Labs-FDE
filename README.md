# The Lenny Growth Assistant
> **Full-Stack AI Conversational Platform & Artifact Workspace Grounded in Lenny’s Podcast Transcripts**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-pgvector-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?logo=google&logoColor=white)](https://aistudio.google.com/)
[![Ollama](https://img.shields.io/badge/Local_Ollama-llama3.2-black?logo=ollama&logoColor=white)](https://ollama.com/)
[![React](https://img.shields.io/badge/React_18-TypeScript-61DAFB?logo=react&logoColor=black)](https://react.dev/)

--- ## Overview

**The Lenny Growth Assistant** is a full-stack, production-ready AI conversational application built for product managers, founders, and growth leaders. It ingests transcripts from [Lenny's Podcast](https://github.com/ChatPRD/lennys-podcast-transcripts), answers tactical product/growth questions strictly grounded in those transcripts with interactive citation badges, generates structured **Ship 30 for 30** atomic essays, and renders interactive **sandboxed artifacts** (HTML/CSS tools, calculators, frameworks) side-by-side with chat.

```
                    
                                Next.js / React Frontend          
                                                                  
                       Chat Stream    Source Drawer    Artifact 
                       (Markdown)     (Citations)      Viewer   
                    
                                            SSE / REST API
                                           
                    
                                   FastAPI Backend                
                                                                  
                          
                         Agent Layer         RAG Pipeline     
                       (Gemini / Ollama)   (RRF + Rerank)     
                          
                                                                
                          
                       Skills & Tools      PostgreSQL +       
                       • RAG Search        pgvector (Docker)  
                       • Ship 30 for 30    (Sessions, Msgs,   
                       • Artifact Gen       Artifacts, VDB)   
                          
                    
```

--- ## Key Capabilities

1. **Hybrid RAG with RRF & Reranking**:
   - **Dense Semantic Search**: Cosine similarity via `pgvector` embeddings (`all-MiniLM-L6-v2`).
   - **Sparse Keyword Search**: PostgreSQL Full-Text Search (`tsvector`/`tsquery`) with English dictionary ranking.
   - **Reciprocal Rank Fusion (RRF)**: Merges dense and sparse rankings ($k=60$) for optimal entity & semantic recall.
   - **Candidate Reranking**: Re-orders top chunks by keyword density and guest-query relevance boost.
2. **Speaker-Aware Chunking with Sliding Overlap**:
   - Parses YAML frontmatter (guest, title, date, URL) and speaker turns (`Lenny: ...`, `Guest: ...`).
   - Slices text into 600-token chunks with 150-token sliding overlap, automatically injecting episode and section headers.
3. **Dual Model Engine (Google Gemini & Local Ollama)**:
   - **Cloud Model**: Google Gemini 2.5 Flash via official `google-genai` SDK.
   - **Local Model (Mandatory Demo)**: Local Ollama instance (`llama3.2`, `mistral`, `qwen2.5`) with zero cloud cost.
   - Seamless runtime toggle from the sidebar with automated health-check fallback.
4. **Dedicated Ship 30 for 30 Content Skill**:
   - Formats grounded knowledge into a ~1,250-word Atomic Essay featuring a strong 1-sentence hook, 1-3-1 narrative cadence, visual skimmability, and tactical playbook.
5. **Sandboxed In-App Artifact Viewer**:
   - Renders interactive HTML/CSS calculators, dashboards, and Markdown documents in an isolated side panel.
   - Multi-layer security: iframe `sandbox="allow-scripts"` (strictly omitting `allow-same-origin`), strict Content-Security-Policy (CSP), and server-side Bleach sanitization.
6. **Full Persistence in PostgreSQL**:
   - Stores sessions, message threads, latency metrics, citations, and versioned artifacts.

--- ## Quickstart

### Option 1: One-Command Startup with Docker Compose (Recommended)

Make sure Docker and Docker Compose are installed:

```bash
# 1. Clone repository and navigate to directory
git clone https://github.com/your-username/lenny-growth-assistant.git
cd lenny-growth-assistant

# 2. Copy environment file and configure keys (optional if running local Ollama)
cp .env.example .env

# 3. Launch PostgreSQL (with pgvector), FastAPI Backend, and React Frontend
docker compose up --build
```

- **Web Application**: [http://localhost:3000](http://localhost:3000)
- **API Docs & Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Endpoint**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

--- ### Option 2: Local Development Mode (Native Python + Node)

#### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- PostgreSQL with `pgvector` running on port 5432 (or run `docker compose up -d postgres`)
- (Optional) [Ollama](https://ollama.com) running locally (`ollama run llama3.2`)

#### Step 1: Run PostgreSQL + pgvector
```bash
docker compose up -d postgres
```

#### Step 2: Start Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ingest sample transcripts into pgvector
python3 ../scripts/ingest_transcripts.py --sample

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 3: Start Frontend
```bash
cd frontend
npm install
npm run dev
```

--- ## Environment Configuration (`.env`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgrespassword@localhost:5432/lenny_growth` | PostgreSQL connection string with pgvector support |
| `GEMINI_API_KEY` | `""` | Google AI Studio API key for Gemini 2.5 Flash |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Selected Gemini model |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL of local Ollama instance |
| `OLLAMA_MODEL` | `llama3.2` | Local model name in Ollama |
| `DEFAULT_PROVIDER` | `gemini` | Default engine (`gemini` or `ollama`) |
| `EMBEDDING_PROVIDER` | `local` | `local` (SentenceTransformers) or `gemini` |

--- ## Running Automated Tests

Run backend unit and integration tests covering chunking with overlap, RRF mathematical fusion, security sanitization, and API endpoints:

```bash
cd backend
pytest -v tests/
```

--- ## Project Structure

```
 backend/
    app/
       api/v1/          # Chat (SSE), Sessions, Artifacts, Ingestion, Health
       core/            # Config, Async DB with pgvector, JSON Logger, Security
       models/          # SQLAlchemy DB models & Pydantic schemas
       rag/             # Speaker-aware Chunker, Embedder, Hybrid Retriever (RRF)
       agents/          # Gemini SDK Agent, Local Ollama Agent, Router & Tools
       main.py          # FastAPI app entrypoint with lifespan DB init
    tests/               # Pytest test suite (RRF, Chunker, Security)
    Dockerfile           # Backend Docker container
    requirements.txt
 frontend/
    src/
       components/      # Sidebar, Chat, CitationChips, ArtifactViewer, MessageInput
       services/api.ts  # Typed API client with resilient SSE parser
       App.tsx          # Resizable split-pane layout & state coordinator
       index.css        # Tailwind & Glassmorphism design tokens
    Dockerfile           # Frontend multi-stage Nginx build
    package.json
 docs/
    PRD.md               # Product Requirements Document & Discovery Brief
    design.md            # UI/UX Specifications & Iframe Sandbox Security Model
    architecture.md      # Technical Architecture, DB ERD & RRF Pipeline Flow
 scripts/
    ingest_transcripts.py # CLI ingestion script for pgvector
    run_local.sh         # One-command local startup script
 docker-compose.yml       # PostgreSQL (pgvector) + FastAPI + React orchestration
 .env.example             # Documented environment template
```

--- ## Security & Sandbox Isolation

AI-generated HTML artifacts execute in an isolated sandbox:
1. **Isolated Iframe**: `sandbox="allow-scripts"` (strictly omits `allow-same-origin` to prevent access to parent cookies, tokens, and DOM).
2. **Content Security Policy**: `default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'none';` to block unauthorized data exfiltration.
3. **Server-Side Sanitization**: Python `bleach` whitelist sanitizes dangerous tags before database persistence.

--- ## Evaluator Verification Checklist

- [x] **Grounded Answers**: Ask *"What did Brian Chesky say about eliminating traditional PM at Airbnb?"* $\rightarrow$ Verified response citing Brian Chesky's episode with interactive source pills.
- [x] **Out-of-Domain Safety**: Ask *"What is the recipe for baking sourdough bread?"* $\rightarrow$ Verified polite refusal acknowledging absence in Lenny's podcast.
- [x] **Local Ollama Model**: Toggle to **Local Ollama** $\rightarrow$ System queries local `llama3.2` via `localhost:11434`.
- [x] **Ship 30 for 30 Skill**: Enable **Ship 30 for 30 Skill** $\rightarrow$ Generates ~1,250 word Atomic Essay with hook, 1-3-1 structure, bold highlights, and guest attribution.
- [x] **Interactive Artifact Viewer**: Ask *"Generate an interactive HTML/CSS growth loop calculator"* $\rightarrow$ Opens side-by-side Artifact Viewer with live executing sandboxed preview and raw code tab.
