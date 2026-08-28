#!/usr/bin/env python3
"""
CLI Runner for Ship 30 for 30 Atomic Essay Evaluation.
Evaluates essay quality across the 7 weighted criteria.
"""

import asyncio
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from app.core.database import AsyncSessionLocal
from app.rag.retriever import retrieve_hybrid_grounded_chunks
from app.rag.ship30_evaluator import Ship30Evaluator, CRITERIA_WEIGHTS

SAMPLE_ESSAY = """# The Illusion of Management: Why Modern Tech Leaders Must Return to Founder Mode
*By The Lenny Growth Assistant • Grounded in Lenny's Podcast with Brian Chesky*

Most CEOs run their companies like business managers—and it is quietly killing product craft.

They delegate strategy to autonomous business units. They hire professional managers who optimize metrics rather than building great products. Then they wonder why innovation grinds to a halt.

### 1. The Broken Default: The Modular Matrix
At scale, standard Silicon Valley advice dictates that founders should "hire great people and get out of the way." 

Airbnb followed this traditional playbook for years. They created siloed business units with decentralized product managers. The result? A fragmented user experience and rising operational overhead.

### 2. The Core Insight: The Functional Operating Model
Brian Chesky broke the matrix. He restructured Airbnb into a functional organization where leaders are subject matter experts, not general administrators.

Under this model, founders stay deeply involved in the details of the product. Eliminating traditional product managers allowed Airbnb to merge product management with product marketing.

### 3. The Step-by-Step Playbook: The 2-Release Roadmap
To implement this operating system, Airbnb uses a centralized roadmap:
* **Synchronized Launches**: The entire company aligns around two major release cycles per year.
* **Founder Reviews**: Every key feature is reviewed directly by leadership for design consistency.
* **Shared Shared Narrative**: Marketing and engineering ship cohesive customer stories together.

### 4. The Compounding Effect: Velocity Through Clarity
When leaders stay in the details, decision latency collapses. 

Great companies are not built by consensus management. They are built through shared obsession with product excellence.
"""

async def run_ship30_evaluation(query: str = "Brian Chesky on Founder Mode"):
    print("=" * 75)
    print("  ✍️ SHIP 30 FOR 30 ATOMIC ESSAY EVALUATOR")
    print("=" * 75)
    print(f"Topic: {query}\n")

    async with AsyncSessionLocal() as db:
        chunks = await retrieve_hybrid_grounded_chunks(db, query, top_k=5)
        contexts = [c.content for c in chunks]

    eval_result = Ship30Evaluator.evaluate_essay(SAMPLE_ESSAY, contexts)
    metrics = eval_result["metrics"]

    print("| Criterion      | Weight | Score (1-10) | Weighted |")
    print("| :------------- | -----: | -----------: | -------: |")
    for key, weight in CRITERIA_WEIGHTS.items():
        score = metrics[key]
        weighted_val = round(score * weight, 2)
        label = key.replace("_", " ").title()
        print(f"| {label:<14} |  {int(weight*100):>3}%  |         {score:>4.1f} |     {weighted_val:>4.2f} |")

    print("-" * 75)
    print(f"  Word Count:      {eval_result['word_count']} words")
    print(f"  Composite Score: {eval_result['composite_score']} / 10.0")
    print("=" * 75)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ship 30 for 30 Evaluator CLI")
    parser.add_argument("--query", "-q", type=str, default="Brian Chesky on Founder Mode")
    args = parser.parse_args()

    asyncio.run(run_ship30_evaluation(args.query))
