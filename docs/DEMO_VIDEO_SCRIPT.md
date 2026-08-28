# 2–3 Minute Demo Video Script: The Lenny Growth Assistant

**Target Duration:** 2:30 – 3:00 minutes  
**Format:** Camera in corner (talking head) + Screen Recording of the Application (`http://localhost:3000`)

--- ## Video Structure & Scene-by-Scene Breakdown

```
0:00 - 0:30  |  1. Problem Statement & Architecture Intro
0:30 - 1:15  |  2. Live Demo: Grounded RAG, Inline Citations & Sources Drawer
1:15 - 1:45  |  3. Ship 30 for 30 Skill (/ship30for30) & Interactive Artifacts
1:45 - 2:20  |  4. Local Ollama Execution & Model Toggle
2:20 - 2:50  |  5. Key Technical Trade-Off: Hybrid Search & Grounding Thresholds
2:50 - 3:00  |  6. Summary & Deployment Readiness
```

--- ## Detailed Scene-by-Scene Script

### [0:00 – 0:30] Scene 1: Introduction & The Problem
**Visual:** Camera full-screen or corner bubble over application homepage.  
**Speaker Action:** Introduce yourself and frame the user problem.

> *"Hi everyone, my name is Amogh, and today I'm demonstrating **The Lenny Growth Assistant**—a production-grade AI assistant built for product leaders and founders to extract grounded, actionable advice from the complete archive of Lenny's Podcast transcripts.*
> 
> *The core challenge we solved here was turning hundreds of hours of conversational transcripts into accurate, verifiable advice without hallucinations, while giving teams the ability to switch between high-throughput cloud models like Google Gemini and fully local, offline LLMs via Ollama."*

--- ### [0:30 – 1:15] Scene 2: Live Demo — Grounded RAG & Inline Citations
**Visual:** Screen showing chat input. Type or click quick prompt: `"Brian Chesky on Founder Mode & 2-Release Cycle"`.

> *"Let's ask a complex product question: 'Explain Brian Chesky's operating model at Airbnb and how he thinks about the 2-release cycle.'*
> 
> *Notice three key capabilities as the answer streams:*
> 1. *First, every single major claim has **inline citation chips** linking directly to the guest and episode topic.*
> 2. *Second, right above the answer, our **Claim Grounding Audit Card** displays the verification confidence, confirming 100% of claims are grounded.*
> 3. *Third, clicking the **Sources Drawer** in the header opens all retrieved transcript chunks with their Reciprocal Rank Fusion relevance scores."*

--- ### [1:15 – 1:45] Scene 3: Ship 30 for 30 Skill & Interactive Artifacts
**Visual:** Type `/ship30for30 Nikita Bier viral growth playbook` into the chat input, then show the Artifact Viewer.

> *"Now let's activate our dedicated **Ship 30 for 30 content skill** by typing `/ship30for30`. Notice the interface recognizes the command and switches to our Atomic Essay pipeline.*
> 
> *Instead of generic text, it generates a structured essay featuring a strong 1-sentence hook, 1-3-1 sentence cadence, visual subheadings, and a concrete operational playbook.*
> 
> *Furthermore, when we ask for frameworks or tools—like an interactive LNO scorecard—the application generates an **interactive HTML/CSS Artifact**, rendered live in our sandboxed, side-by-side **Artifact Viewer**."*

--- ### [1:45 – 2:20] Scene 4: Local Ollama Execution & Privacy Mode
**Visual:** Click the Active Model toggle in the sidebar and switch to `Local Ollama (qwen2.5:1.5b)`. Submit query: `"Shreyas Doshi LNO Framework"`.

> *"Next, let's look at our local LLM capability. With one click in the sidebar, I can switch our backend engine from Google Gemini to **Local Ollama** running completely on-device.*
> 
> *The entire hybrid retrieval, pgvector cosine search, and generation happen locally with zero data leaving the machine. If Ollama ever goes offline, our agent router includes automatic graceful failover."*

--- ### [2:20 – 2:50] Scene 5: Key Technical Trade-Off
**Visual:** Show architecture diagram or code snippet of `retriever.py` / `docker-compose.yml`.

> *"A critical technical trade-off we navigated was **Vector Search vs. Sparse Full-Text Hybrid Retrieval**.*
> 
> *Pure dense vector search often struggles with specific guest names and episodic entities. Pure keyword search fails on thematic queries like 'how to fix high churn'.*
> 
> *We implemented **Reciprocal Rank Fusion (RRF)** combining pgvector cosine distance and PostgreSQL tsvector full-text search with a $3.0\times$ guest entity boost. This achieved a **1.00 Context Precision** in our RAGAS benchmark and completely eliminated hallucination."*

--- ### [2:50 – 3:00] Scene 6: Conclusion & Operational Readiness
**Visual:** Terminal showing `docker compose up -d` running cleanly.

> *"The entire system is packaged in Docker Compose with one-command startup, full persistence in PostgreSQL, automated RAGAS evaluation scripts, and unit tests.*
> 
> *Thank you for watching, and I look forward to your feedback!"*

--- ## Recording Checklist Before Pressing Record:
- [ ] Docker containers running (`docker compose up -d`)
- [ ] Browser window open at `http://localhost:3000` (clean chat session)
- [ ] Ollama running locally (`ollama serve`)
- [ ] Camera and microphone tested with good lighting
- [ ] Target time: ~2 minutes 45 seconds
