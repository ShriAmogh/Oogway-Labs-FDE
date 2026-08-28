# Product Requirements Document (PRD)
## The Lenny Growth Assistant

---

## 1. Executive Summary & Discovery Brief

### 1.1 User & Problem Framing
- **Primary User**: Product Managers, Growth Practitioners, Founders, and Strategy Operators.
- **The Core Problem**: Lenny Rachitsky's podcast repository contains over 200+ hours of tactical wisdom from world-class product leaders (Brian Chesky, Shreyas Doshi, Elena Verna, Nikita Bier, etc.). However, practitioners face high friction when searching for actionable frameworks during active sprint planning or strategy formulation. Existing generic LLMs hallucinate generic advice without citing specific guest experiences.
- **The Solution**: "The Lenny Growth Assistant" is an AI-powered conversational system that ingests transcripts from Lenny's Podcast, answers complex PM/growth questions strictly grounded in those transcripts with interactive citations, generates Ship 30 for 30–style atomic essays, and renders interactive sandboxed artifacts (calculators, checklists, frameworks) side-by-side with chat.

### 1.2 Measurable Success Metrics
1. **Grounded Retrieval Precision**: $\ge 90\%$ of retrieved chunks in the final reranked set are directly relevant to the user query.
2. **Zero-Hallucination Rate on Out-of-Domain Queries**: 100% of queries outside the scope of Lenny's transcripts (e.g. recipe inquiries, general trivia) are acknowledged as not present in the podcast rather than fabricated.
3. **Time-to-First-Token (TTFT)**: $< 1.2\text{s}$ on Google Gemini 2.5 Flash cloud streaming and $< 2.5\text{s}$ on local Ollama `llama3.2`.
4. **Artifact Usability**: 100% of generated HTML/CSS tools render natively and execute interactively inside the sandboxed iframe viewer without breaking parent application state.

### 1.3 Key Assumptions
- Transcripts follow standard markdown structure with YAML frontmatter or speaker prefixes.
- Evaluators require a local zero-cost mode (Ollama `llama3.2`) as well as a cloud model (Google Gemini SDK).
- Evaluators may run the system via Docker Compose or native Python/Node.

### 1.4 Scope Choices (What is Included vs Excluded)
| In Scope | Out of Scope (Intentional Trade-off) |
| :--- | :--- |
| • Hybrid RAG (pgvector Dense + PostgreSQL Full-Text Search + RRF Fusion + Reranking) | • Multi-tenant enterprise auth / SSO (Single user/team evaluator focus) |
| • Speaker-aware chunking with token overlap (600 tokens target, 150 token overlap) | • Direct live audio streaming transcription (uses pre-transcribed text) |
| • Google Gemini SDK & Local Ollama runtime toggle | • Fine-tuning custom base models (RAG provides higher ground truth fidelity) |
| • Dedicated Ship 30 for 30 essay generation skill | |
| • Sandboxed in-app Artifact Viewer (HTML/CSS & Markdown) | |
| • Complete session persistence in PostgreSQL | |

### 1.5 Risks & Mitigation Strategies
- **Risk 1: Hallucination of quotes or guest attributions.**
  - *Mitigation*: Strict system prompting enforcing that all factual advice must stem from provided `[Source N]` blocks; citations are programmatically extracted and validated against retrieved chunks.
- **Risk 2: XSS or parent DOM takeover via generated HTML artifacts.**
  - *Mitigation*: Multi-layer defense: DOMPurify/Bleach server-side sanitization, strict iframe sandboxing (`sandbox="allow-scripts"` without `allow-same-origin`), and restrictive Content-Security-Policy (CSP).
- **Risk 3: Local Ollama unavailability on evaluator's machine.**
  - *Mitigation*: Automatic health-check probing with graceful fallback to Google Gemini or clear user guidance in UI.

---

## 2. Functional Requirements

### 2.1 Conversational Chat & Streaming
- Real-time token streaming via Server-Sent Events (SSE) `/api/v1/chat/stream`.
- Real-time thinking and retrieval stage indicators (`retrieving`, `generating`).
- Independent conversational sessions with persistent message history in PostgreSQL.

### 2.2 Grounded Retrieval & Source Citations
- Every grounded answer displays interactive **Source Citation Pills** showing the episode title, guest name, and section header.
- Clicking a citation opens a modal displaying the exact transcript excerpt and link to the podcast episode.

### 2.3 Ship 30 for 30 Content Skill
- A dedicated toggle/prompt skill that structures answers into ~1,000–1,250 word atomic essays featuring:
  - Irresistible 1-sentence opening hook.
  - 1-3-1 sentence cadence and visual rhythm.
  - Skimmable subheadings, bullet points, and selective bolding.
  - Actionable tactical takeaways and explicit guest citations.

### 2.4 In-App Artifact Viewer
- Side-by-side split screen panel that automatically opens when an artifact is generated.
- Dual-tab interface: **Preview** (Live sandboxed HTML or rendered Markdown) and **Code** (raw syntax with Copy/Download buttons).
- Support for multiple artifacts generated in a single session with history tab navigation.

---

## 3. Acceptance Criteria

1. **AC-1 (Grounding & Citations)**: When asked "What is Brian Chesky's advice on Founder Mode?", the assistant responds with Chesky's specific insights and displays a citation badge referencing Brian Chesky's episode.
2. **AC-2 (Out-of-Domain Safety)**: When asked "How do I bake sourdough bread?", the assistant explicitly states that Lenny's podcast does not contain sourdough baking recipes.
3. **AC-3 (Model Switching)**: Switching the toggle from Gemini to Local Ollama successfully sends subsequent requests to the local Ollama instance at `localhost:11434`.
4. **AC-4 (Ship 30 Skill)**: Activating the Ship 30 for 30 skill outputs an essay formatted with a hook, 1-3-1 structure, bold highlights, and tactical framework.
5. **AC-5 (Sandboxed Artifacts)**: Asking for an interactive calculator produces an HTML artifact that executes interactive JavaScript inside the isolated iframe without accessing parent `localStorage` or cookies.
