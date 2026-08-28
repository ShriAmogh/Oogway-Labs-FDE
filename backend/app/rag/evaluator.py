"""
RAGAS Metric Evaluator for Lenny's Growth Assistant.
Computes Faithfulness, Answer Relevancy, Context Precision, and Context Recall.
"""

import math
import re
from typing import List, Dict, Any, Optional, Tuple
from app.core.logging import logger
from app.rag.embedder import generate_query_embedding
import numpy as np

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    a = np.array(v1)
    b = np.array(v2)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

def extract_sentences(text: str) -> List[str]:
    """Split text into distinct sentences/statements."""
    clean = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    clean = re.sub(r'#+\s.*', '', clean)
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', clean) if len(s.strip()) > 15]
    return sentences

class RagasEvaluator:
    @staticmethod
    def evaluate_faithfulness(answer: str, contexts: List[str]) -> float:
        """
        Faithfulness: Measures whether claims in the generated answer are grounded in the retrieved context.
        Formula: (Number of supported claims) / (Total claims in answer)
        """
        if not contexts or not answer:
            return 0.0
            
        combined_context = " ".join(contexts).lower()
        sentences = extract_sentences(answer)
        if not sentences:
            return 1.0
            
        supported_count = 0
        for sent in sentences:
            words = [w.lower() for w in re.findall(r'\b\w{4,}\b', sent)]
            if not words:
                supported_count += 1
                continue
            # Check overlap of substantive terms
            overlap = sum(1 for w in words if w in combined_context)
            ratio = overlap / len(words)
            if ratio >= 0.40:
                supported_count += 1
                
        score = supported_count / len(sentences)
        return round(min(1.0, max(0.0, score)), 2)

    @staticmethod
    async def evaluate_answer_relevancy(question: str, answer: str) -> float:
        """
        Answer Relevancy: Measures semantic alignment between the prompt and generated response.
        """
        if not question or not answer:
            return 0.0
            
        q_emb = await generate_query_embedding(question)
        # Sample the key opening & summary of the answer for relevancy
        summary = answer[:600]
        a_emb = await generate_query_embedding(summary)
        
        sim = cosine_similarity(q_emb, a_emb)
        # Normalize typical embedding similarity into 0.0 - 1.0 range
        normalized = (sim - 0.2) / 0.7
        return round(min(1.0, max(0.0, normalized)), 2)

    @staticmethod
    def evaluate_context_precision(
        question: str,
        contexts: List[Dict[str, Any]],
        expected_guest: Optional[str] = None,
        expected_keywords: Optional[List[str]] = None
    ) -> float:
        """
        Context Precision: Measures whether relevant chunks are prioritized at top ranks.
        Evaluates Precision@K weighted by position.
        """
        if not contexts:
            return 0.0
            
        total_chunks = len(contexts)
        relevant_at_k = []
        cumulative_hits = 0
        precisions = []
        
        q_words = set(question.lower().split())
        keywords = set(expected_keywords or [])
        
        for k, c in enumerate(contexts, start=1):
            content = (c.get("content") or "").lower()
            guest = (c.get("guest") or "").lower()
            title = (c.get("episode_title") or "").lower()
            
            is_relevant = False
            # Check guest match
            if expected_guest and expected_guest.lower() in guest:
                is_relevant = True
            elif any(kw.lower() in content or kw.lower() in title for kw in keywords):
                is_relevant = True
            elif sum(1 for qw in q_words if len(qw) > 4 and qw in content) >= 2:
                is_relevant = True
                
            if is_relevant:
                cumulative_hits += 1
                precisions.append(cumulative_hits / k)
            else:
                precisions.append(0.0)
                
        if cumulative_hits == 0:
            return 0.20 # baseline floor
            
        score = sum(precisions) / cumulative_hits
        return round(min(1.0, max(0.0, score)), 2)

    @staticmethod
    def evaluate_context_recall(
        ground_truth: str,
        contexts: List[Dict[str, Any]]
    ) -> float:
        """
        Context Recall: Measures whether the retrieved context covers all ground truth statements.
        """
        if not contexts or not ground_truth:
            return 0.0
            
        combined_context = " ".join([(c.get("content") or c.get("quote") or "") for c in contexts]).lower()
        gt_sentences = extract_sentences(ground_truth)
        if not gt_sentences:
            gt_sentences = [s.strip() for s in ground_truth.split("\n") if len(s.strip()) > 10] or [ground_truth]
            
        covered_count = 0
        for sent in gt_sentences:
            key_words = [w.lower() for w in re.findall(r'\b\w{4,}\b', sent)]
            if not key_words:
                covered_count += 1
                continue
            matched = sum(1 for w in key_words if w in combined_context)
            if (matched / len(key_words)) >= 0.25:
                covered_count += 1
                
        score = covered_count / len(gt_sentences)
        return round(min(1.0, max(0.0, score)), 2)

    @classmethod
    async def evaluate_full_turn(
        cls,
        question: str,
        answer: str,
        citations: List[Dict[str, Any]],
        expected_guest: Optional[str] = None,
        expected_keywords: Optional[List[str]] = None,
        ground_truth: Optional[str] = None
    ) -> Dict[str, Any]:
        """Runs all 4 RAGAS metrics for a single RAG turn."""
        context_texts = [c.get("content") or c.get("quote") or "" for c in citations]
        
        faithfulness = cls.evaluate_faithfulness(answer, context_texts)
        relevancy = await cls.evaluate_answer_relevancy(question, answer)
        precision = cls.evaluate_context_precision(question, citations, expected_guest, expected_keywords)
        
        gt = ground_truth or (" ".join(context_texts[:2]) if context_texts else "")
        recall = cls.evaluate_context_recall(gt, citations)
        
        # Overall RAGAS Harmonic Mean Score
        metrics = [faithfulness, relevancy, precision, recall]
        if all(m > 0 for m in metrics):
            ragas_score = round(4.0 / sum(1.0 / m for m in metrics), 2)
        else:
            ragas_score = round(sum(metrics) / 4.0, 2)
            
        return {
            "faithfulness": faithfulness,
            "answer_relevancy": relevancy,
            "context_precision": precision,
            "context_recall": recall,
            "ragas_score": ragas_score
        }
