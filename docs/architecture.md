# Technical Architecture Document
## The Lenny Growth Assistant

---

## 1. System Topology

```mermaid
graph TD
    Client["React / Vite Web App (:3000)"] -->|REST & SSE Stream| API["FastAPI Backend (:8000)"]
    
    subgraph Backend_Services ["Backend Services"]
        API --> AgentRouter["Agent Router"]
        API --> DB[("PostgreSQL 16 + pgvector (:5432)")]
        
        AgentRouter -->|Cloud Option| GeminiAgent["Google Gemini 2.5 Flash"]
        AgentRouter -->|Local Option| OllamaAgent["Local Ollama Client (:11434)"]
        
        GeminiAgent --> RAG["Hybrid RAG Pipeline"]
        OllamaAgent --> RAG
        
        subgraph RAG_Engine ["RAG Retrieval Engine"]
            RAG --> Embedder["SentenceTransformer Embedder"]
            RAG --> DenseSearch["pgvector Cosine Search"]
            RAG --> SparseSearch["PostgreSQL Full-Text Search (ts_rank)"]
            DenseSearch --> RRF["Reciprocal Rank Fusion (RRF k=60)"]
            SparseSearch --> RRF
            RRF --> Reranker["Cross-Candidate Reranker"]
        end
    end
    
    subgraph Data_Stores ["Data Stores"]
        DB --> SessionsTbl["sessions"]
        DB --> MessagesTbl["messages"]
        DB --> CitationsTbl["citations"]
        DB --> ArtifactsTbl["artifacts"]
        DB --> ChunksTbl["transcript_chunks (pgvector + FTS)"]
    end
```

---

## 2. Database Schema (PostgreSQL with `pgvector`)

### 2.1 Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    sessions ||--o{ messages : "contains"
    sessions ||--o{ artifacts : "produces"
    messages ||--o{ citations : "references"
    messages ||--o{ artifacts : "generates"

    sessions {
        uuid id PK
        string title
        string model_provider
        string model_name
        timestamp created_at
        timestamp updated_at
    }

    messages {
        uuid id PK
        uuid session_id FK
        string role
        text content
        string model
        float latency_ms
        timestamp created_at
    }

    citations {
        uuid id PK
        uuid message_id FK
        string episode_title
        string guest
        string timestamp_or_section
        text url
        text quote
        float relevance_score
    }

    artifacts {
        uuid id PK
        uuid session_id FK
        uuid message_id FK
        string title
        string artifact_type
        text content
        int version
        timestamp created_at
    }

    transcript_chunks {
        uuid id PK
        string episode_slug
        string episode_title
        string guest
        string publish_date
        text url
        int chunk_index
        string speaker
        string header_section
        text content
        int token_count
        vector embedding
        tsvector tsv
    }
```

---

## 3. Hybrid RAG Retrieval Pipeline (Dense + FTS + RRF + Reranking)

```mermaid
flowchart TD
    Query["User Query"] --> Embed["Dense Embedder (SentenceTransformer)"]
    Query --> Norm["Query Normalizer & Keyword Extractor"]

    Embed --> DenseSearch["pgvector Cosine Search<br/>ORDER BY embedding <=> q<br/>LIMIT 20 (Dense Hits)"]
    Norm --> SparseSearch["PostgreSQL Full-Text Search<br/>ORDER BY ts_rank_cd(tsv, q)<br/>LIMIT 20 (Sparse Hits)"]

    DenseSearch --> RRF["Reciprocal Rank Fusion (RRF k=60)<br/>Score = 1/(60 + r_dense) + 1/(60 + r_sparse)"]
    SparseSearch --> RRF

    RRF --> Rerank["Candidate Reranker<br/>(Speaker Match Boost + Title Overlap + Keyword Density)"]
    Rerank --> Output["Top-5 Grounded Chunks + Verified Citations"]
```

### 3.1 Reciprocal Rank Fusion (RRF) Formula
$$RRF(d) = \sum_{m \in \{\text{dense}, \text{sparse}\}} \frac{1}{k + rank_m(d)}$$

Where $k = 60$. Chunks matching both semantic intent and exact named entities (e.g. "Brian Chesky", "LNO framework") achieve maximum composite scores.

---

## 4. Transcript Chunking with Sliding Window Overlap

- **Target Size**: 600 tokens per chunk.
- **Sliding Overlap**: 150 tokens retained across chunk transitions.
- **Context Injection**: Every chunk automatically prepends the Episode Title, Guest Name, and Active Section Header to maintain semantic grounding.

---

## 5. Model Routing & Automatic Failover

| Selected Provider | Primary Execution | Fallback Strategy |
| :--- | :--- | :--- |
| **Google Gemini (Cloud)** | `google-genai` SDK streaming (`gemini-2.5-flash`) | Emits grounded context directly if API key is invalid/missing. |
| **Local Ollama (Local)** | Local streaming via `http://localhost:11434/api/chat` | Automatic ping health-check; fails over to Gemini if Ollama is unreachable. |

---

## 6. API Endpoints Contract

- `POST /api/v1/chat/stream`: Initiates SSE streaming session with real-time token, citation, and artifact emission.
- `GET /api/v1/sessions`: Lists all conversational sessions.
- `GET /api/v1/sessions/{id}`: Retrieves complete session history with messages, citations, and artifacts.
- `GET /api/v1/artifacts/{id}/raw`: Serves sandboxed HTML document with strict CSP headers for iframe preview.
- `GET /api/v1/health`: Verifies PostgreSQL, pgvector extension, Ollama, and Gemini connectivity.
- `POST /api/v1/ingestion/trigger`: Triggers background indexing of transcripts.
