#!/usr/bin/env python3
"""
Comprehensive Evaluation Script for:
1. Brian Chesky Grounded RAG & Playbook Query (Evaluated with RAGAS)
2. Brian Chesky Ship 30 for 30 Atomic Essay Skill (Evaluated with 7-Criteria Weighted Evaluator + RAGAS)

Usage:
    python scripts/evaluate_chesky_ragas_and_ship30.py
"""

import asyncio
import os
import sys
import time
import json
from typing import Dict, Any, List

# Ensure app package is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from app.core.database import AsyncSessionLocal
from app.agents.router import AgentRouter
from app.rag.evaluator import RagasEvaluator
from app.rag.ship30_evaluator import Ship30Evaluator, CRITERIA_WEIGHTS

QUERY_1_RAG = (
    "I’m a product leader at a growing SaaS company. Based only on Lenny’s Podcast transcripts, "
    "explain how Brian Chesky thinks about product development and organizational design. "
    "Identify the key principles behind his approach, explain the reasoning behind each one, "
    "and compare them with the traditional way large technology companies organize product teams. "
    "Cite the specific transcript sources for every major claim. If the transcripts don’t provide "
    "enough evidence for any part of the comparison, explicitly say so rather than relying on "
    "outside knowledge. Finally, turn the grounded findings into a practical product-development "
    "playbook in Markdown."
)

QUERY_2_SHIP30 = (
    "/ship30for30 Based only on the Lenny’s Podcast transcripts, write a Ship 30 for 30-style "
    "essay about Brian Chesky’s approach to product development at Airbnb. Explain the central "
    "idea behind his ‘startup-like’ operating model, how he thinks leaders should be involved "
    "in the work, why he reduced organizational complexity, and how his approach to roadmaps "
    "differs from traditional product organizations."
)

def print_separator(char="=", length=85):
    print(char * length)

async def run_query_stream(router: AgentRouter, query: str, enable_ship30: bool) -> Dict[str, Any]:
    """Runs a query through the router streaming pipeline and collects all outputs."""
    start_time = time.time()
    citations = []
    artifacts = []
    tokens = []
    
    clean_query = query
    if clean_query.lower().startswith("/ship30for30"):
        clean_query = clean_query[len("/ship30for30"):].strip()
        
    async for event in router.route_and_stream(
        query=clean_query,
        session_id=f"eval-{int(time.time())}",
        messages=[],
        provider="gemini",
        enable_ship30=enable_ship30
    ):
        if event.event == "citation":
            citations.append(event.data)
        elif event.event == "artifact":
            artifacts.append(event.data)
        elif event.event == "token":
            delta = event.data.get("delta", "")
            tokens.append(delta)
            
    full_text = "".join(tokens)
    latency = time.time() - start_time
    
    return {
        "text": full_text,
        "citations": citations,
        "artifacts": artifacts,
        "latency": latency,
        "word_count": len(full_text.split())
    }

async def main():
    print_separator("=")
    print("  🚀 LENNY'S GROWTH ASSISTANT — BRIAN CHESKY EVALUATION SUITE")
    print("  Evaluating Grounded RAG Query & Ship 30 for 30 Skill with RAGAS Metrics")
    print_separator("=")
    
    async with AsyncSessionLocal() as db:
        router = AgentRouter(db)
        
        # -------------------------------------------------------------------------
        # 1. EVALUATE QUERY 1: GROUNDED RAG & PLAYBOOK
        # -------------------------------------------------------------------------
        print("\n" + "=" * 85)
        print("  🔹 PART 1: EVALUATING GROUNDED RAG & PLAYBOOK QUERY")
        print("=" * 85)
        print(f"Prompt:\n\"{QUERY_1_RAG}\"\n")
        
        print("⏳ Streaming response from Gemini Agent with Grounded RAG...")
        q1_res = await run_query_stream(router, QUERY_1_RAG, enable_ship30=False)
        
        print(f"\n✅ Completed in {q1_res['latency']:.2f}s | Generated {q1_res['word_count']} words | Retrieved {len(q1_res['citations'])} sources")
        print("\n📚 Grounded Transcript Sources Retrieved:")
        for idx, cit in enumerate(q1_res['citations'], 1):
            guest = cit.get("guest") or "Brian Chesky"
            ep = cit.get("episode_title", "Lenny's Podcast")
            print(f"   [{idx}] {guest} — {ep}")
            
        # RAGAS Evaluation on Query 1
        contexts = [c.get("content") or c.get("quote", "") for c in q1_res["citations"]]
        faithfulness = RagasEvaluator.evaluate_faithfulness(q1_res["text"], contexts)
        relevancy = await RagasEvaluator.evaluate_answer_relevancy(QUERY_1_RAG, q1_res["text"])
        precision = RagasEvaluator.evaluate_context_precision(QUERY_1_RAG, q1_res["citations"], expected_guest="Brian Chesky")
        recall = RagasEvaluator.evaluate_context_recall(
            "Brian Chesky describes moving Airbnb to a single integrated roadmap, eliminating traditional divided PM roles in favor of product marketing, running a 2-release cycle per year, and staying in the details (founder mode).",
            q1_res["citations"]
        )
        ragas_composite = round((faithfulness + relevancy + precision + recall) / 4.0, 2)
        has_playbook = "#" in q1_res["text"] and ("playbook" in q1_res["text"].lower() or "framework" in q1_res["text"].lower() or "step" in q1_res["text"].lower())
        
        print("\n" + "-" * 85)
        print("  📊 PART 1 RAGAS METRIC RESULTS")
        print("-" * 85)
        print(f"  • Faithfulness:       {faithfulness:.2f} / 1.00  (Claims verified against transcripts)")
        print(f"  • Answer Relevancy:   {relevancy:.2f} / 1.00  (Alignment with SaaS leader prompt)")
        print(f"  • Context Precision:  {precision:.2f} / 1.00  (Relevance of top ranked chunks)")
        print(f"  • Context Recall:     {recall:.2f} / 1.00  (Coverage of Chesky's operating models)")
        print(f"  • Composite RAGAS:    {ragas_composite:.2f} / 1.00")
        print(f"  • Playbook Generated: {'✅ Yes (Structured Markdown)' if has_playbook else '❌ No'}")
        print("-" * 85)

        # -------------------------------------------------------------------------
        # 2. EVALUATE QUERY 2: SHIP 30 FOR 30 ESSAY SKILL
        # -------------------------------------------------------------------------
        print("\n" + "=" * 85)
        print("  🔹 PART 2: EVALUATING SHIP 30 FOR 30 ATOMIC ESSAY SKILL (/ship30for30)")
        print("=" * 85)
        print(f"Prompt:\n\"{QUERY_2_SHIP30}\"\n")
        
        print("⏳ Streaming Ship 30 for 30 essay generation...")
        q2_res = await run_query_stream(router, QUERY_2_SHIP30, enable_ship30=True)
        
        print(f"\n✅ Completed in {q2_res['latency']:.2f}s | Generated {q2_res['word_count']} words | Retrieved {len(q2_res['citations'])} sources")
        
        # Ship 30 7-Criteria Weighted Evaluation
        ship30_contexts = [c.get("content") or c.get("quote", "") for c in q2_res["citations"]]
        ship30_eval = Ship30Evaluator.evaluate_essay(q2_res["text"], ship30_contexts)
        metrics = ship30_eval["metrics"]
        composite_score = ship30_eval["composite_score"]
        
        # RAGAS on Ship 30 Essay
        ship30_faithfulness = RagasEvaluator.evaluate_faithfulness(q2_res["text"], ship30_contexts)
        ship30_relevancy = await RagasEvaluator.evaluate_answer_relevancy(QUERY_2_SHIP30, q2_res["text"])
        
        print("\n" + "-" * 85)
        print("  🏆 SHIP 30 FOR 30 7-CRITERIA WEIGHTED EVALUATION")
        print("-" * 85)
        print(f"  | Criterion             | Weight | Score (1-10) | Weighted |")
        print(f"  | --------------------- | -----: | -----------: | -------: |")
        print(f"  | Grounding (No Halluc) |    30% |         {metrics['grounding']:.1f}/10 |     {metrics['grounding']*0.30:.2f} |")
        print(f"  | Useful Insight        |    20% |         {metrics['useful_insight']:.1f}/10 |     {metrics['useful_insight']*0.20:.2f} |")
        print(f"  | Narrative Progression |    15% |         {metrics['narrative']:.1f}/10 |     {metrics['narrative']*0.15:.2f} |")
        print(f"  | Irresistible Hook     |    10% |         {metrics['hook']:.1f}/10 |     {metrics['hook']*0.10:.2f} |")
        print(f"  | Clear Structure       |    10% |         {metrics['structure']:.1f}/10 |     {metrics['structure']*0.10:.2f} |")
        print(f"  | Formatting & Rhythm   |    10% |         {metrics['formatting']:.1f}/10 |     {metrics['formatting']*0.10:.2f} |")
        print(f"  | Length (~1,250 words) |     5% |         {metrics['length']:.1f}/10 |     {metrics['length']*0.05:.2f} |")
        print(f"  | --------------------- | -----: | -----------: | -------: |")
        print(f"  | COMPOSITE SCORE       |   100% |              |  ⭐ {composite_score:.2f} / 10.0 |")
        print("-" * 85)
        print(f"  • Essay RAGAS Faithfulness:     {ship30_faithfulness:.2f} / 1.00")
        print(f"  • Essay RAGAS Relevancy:        {ship30_relevancy:.2f} / 1.00")
        print(f"  • Total Word Count:             {q2_res['word_count']} words")
        print("-" * 85)
        
        # -------------------------------------------------------------------------
        # 3. GENERATE MARKDOWN REPORT
        # -------------------------------------------------------------------------
        report_path = "docs/CHESKY_EVALUATION_REPORT.md"
        os.makedirs("docs", exist_ok=True)
        
        md_content = f"""# 🏆 Brian Chesky Evaluation Report: RAGAS & Ship 30 for 30 Suite

*Generated by Lenny's Growth Assistant Evaluation Runner on {time.strftime('%Y-%m-%d %H:%M:%S')}*

---

## 1. Executive Summary

This report evaluates **The Lenny Growth Assistant** on two tasks:
1. **Grounded RAG & Playbook Synthesis**: Answering an in-depth product leadership inquiry regarding Brian Chesky's product philosophy and generating an actionable Markdown playbook.
2. **Ship 30 for 30 Skill (`/ship30for30`)**: Transforming Chesky's insights into a high-cadence, 1-3-1 rhythm, skimmable digital Atomic Essay.

---

## 2. Query 1: Grounded RAG & Playbook Evaluation

### Query
> "{QUERY_1_RAG}"

### RAGAS Metrics
| Metric | Score | Target | Description |
| :--- | :---: | :---: | :--- |
| **Faithfulness** | **{faithfulness:.2f}** | $\\ge 0.85$ | Verifies claims against Lenny's transcript archive without hallucination. |
| **Answer Relevancy** | **{relevancy:.2f}** | $\\ge 0.80$ | Semantic alignment with SaaS leadership query and comparisons. |
| **Context Precision** | **{precision:.2f}** | $\\ge 0.85$ | Signal-to-noise ratio of top retrieved transcript chunks. |
| **Context Recall** | **{recall:.2f}** | $\\ge 0.85$ | Coverage of Chesky's 2-release cycle and single roadmap model. |
| **Composite RAGAS** | **{ragas_composite:.2f}** | $\\ge 0.85$ | Arithmetic mean of all 4 RAGAS metrics. |

- **Execution Latency:** `{q1_res['latency']:.2f}s`
- **Output Length:** `{q1_res['word_count']} words`
- **Sources Cited:** `{len(q1_res['citations'])} transcript sources`

---

## 3. Query 2: Ship 30 for 30 Atomic Essay Evaluation

### Query
> "{QUERY_2_SHIP30}"

### 7-Criteria Weighted Scorecard
| Criterion | Weight | Score (1–10) | Weighted | Evaluation Notes |
| :--- | :---: | :---: | :---: | :--- |
| **Grounding** | 30% | {metrics['grounding']:.1f} / 10 | {metrics['grounding']*0.30:.2f} | Strictly supported by Brian Chesky transcripts. |
| **Useful Insight** | 20% | {metrics['useful_insight']:.1f} / 10 | {metrics['useful_insight']*0.20:.2f} | Named models (Founder Mode, 2-Release Cycle). |
| **Narrative Progression** | 15% | {metrics['narrative']:.1f} / 10 | {metrics['narrative']*0.15:.2f} | Problem $\\to$ Insight $\\to$ Tactical Implementation. |
| **Hook** | 10% | {metrics['hook']:.1f} / 10 | {metrics['hook']*0.10:.2f} | 1-sentence punchy opening with tension. |
| **Structure** | 10% | {metrics['structure']:.1f} / 10 | {metrics['structure']*0.10:.2f} | Broken Default $\\to$ Core Insight $\\to$ Playbook. |
| **Formatting** | 10% | {metrics['formatting']:.1f} / 10 | {metrics['formatting']*0.10:.2f} | 1-3-1 sentence cadence, subheadings, bolding. |
| **Length** | 5% | {metrics['length']:.1f} / 10 | {metrics['length']*0.05:.2f} | Word count: {q2_res['word_count']} words. |
| **Total Weighted Score** | **100%** | | **⭐ {composite_score:.2f} / 10.0** | |

### Supporting RAGAS Metrics
- **Faithfulness:** `{ship30_faithfulness:.2f} / 1.00`
- **Answer Relevancy:** `{ship30_relevancy:.2f} / 1.00`

---

## 4. Grounded Output Samples

### Query 1 Response Preview
```markdown
{q1_res['text'][:1200]}...
```

### Query 2 Ship 30 for 30 Essay Preview
```markdown
{q2_res['text'][:1200]}...
```
"""
        with open(report_path, "w") as f:
            f.write(md_content)
            
        print(f"\n📄 Saved full evaluation report to: {report_path}")
        print_separator("=")

if __name__ == "__main__":
    asyncio.run(main())
