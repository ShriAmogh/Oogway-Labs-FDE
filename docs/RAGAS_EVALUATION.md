# 🏆 RAGAS Benchmark Evaluation Report
**System:** Lenny's Growth Assistant (Hybrid pgvector + FTS + RRF)  
**Dataset:** 303 Episodes • 14,202 Dense Chunks • 6 Golden Multi-Guest Test Queries  
**Date:** August 2026  

---

## 📊 Executive Summary Metrics

| Metric | Score | What It Verifies |
| :--- | :---: | :--- |
| **Faithfulness** | **0.94** | Is the answer actually supported by retrieved context? (Hallucination detection) |
| **Answer Relevancy** | **0.93** | Does the answer address the user's question directly? |
| **Context Precision** | **0.79** | Did hybrid retrieval rank relevant chunks at positions #1–#3? |
| **Context Recall** | **0.72** | Did retrieval find all the information needed to answer? |
| **Composite RAGAS Score** | **0.84** | **Overall End-to-End System Performance** |

---

## 🧪 Detailed Per-Query Results

| Test Query & Guest | Faithfulness | Relevancy | Precision | Recall | RAGAS Score |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Brian Chesky**<br>*What is Brian Chesky's philosophy on Founder Mode ...* | `0.97` | `0.96` | `1.00` | `1.00` | **`0.98`** |
| **Shreyas Doshi**<br>*How does Shreyas Doshi explain the LNO Framework f...* | `0.97` | `0.96` | `1.00` | `1.00` | **`0.98`** |
| **Elena Verna**<br>*What are Elena Verna's key principles for B2B Prod...* | `0.97` | `0.96` | `1.00` | `1.00` | **`0.98`** |
| **Nikita Bier**<br>*How did Nikita Bier engineer viral app growth for ...* | `0.94` | `0.89` | `0.75` | `0.33` | **`0.73`** |
| **Marty Cagan**<br>*What is the difference between a product operating...* | `0.97` | `0.96` | `1.00` | `1.00` | **`0.98`** |
| **None**<br>*How do I calculate the gravitational constant of J...* | `0.85` | `0.86` | `0.00` | `0.00` | **`0.43`** |

---

## 🔬 Methodology
1. **Faithfulness**: Atomic claim verification against combined retrieved transcript context strings.
2. **Answer Relevancy**: Cosine embedding similarity between query semantic intent and synthesized answer takeaways.
3. **Context Precision**: Rank-weighted Mean Average Precision ($MAP@K$) of relevant chunks returned by RRF fusion ($k=60$).
4. **Context Recall**: Coverage of golden reference statements by the retrieved context chunks.
