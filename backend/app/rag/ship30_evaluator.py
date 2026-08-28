"""
Ship 30 for 30 Atomic Essay Evaluator.
Scores essays against 7 weighted criteria:
- Grounding (30%)
- Useful Insight / Takeaway (20%)
- Narrative Progression (15%)
- Hook (10%)
- Structure (10%)
- Formatting (10%)
- Length (5%)
"""

import re
from typing import List, Dict, Any, Optional
from app.rag.evaluator import extract_sentences

CRITERIA_WEIGHTS = {
    "grounding": 0.30,
    "useful_insight": 0.20,
    "narrative": 0.15,
    "hook": 0.10,
    "structure": 0.10,
    "formatting": 0.10,
    "length": 0.05
}

class Ship30Evaluator:
    @staticmethod
    def evaluate_length(text: str) -> float:
        """Target length ~1,000 to 1,250 words."""
        word_count = len(text.split())
        if 900 <= word_count <= 1400:
            return 7.0
        elif 600 <= word_count < 900 or 1400 < word_count <= 1800:
            return 5.5
        elif word_count < 400:
            return 3.5
        return 4.5

    @staticmethod
    def evaluate_hook(text: str) -> float:
        """Evaluates opening sentence strength and provocative tension."""
        lines = [line.strip() for line in text.split("\n") if line.strip() and not line.startswith("#") and not line.startswith("*")]
        if not lines:
            return 3.0
        first_paragraph = lines[0]
        first_sentence = extract_sentences(first_paragraph)
        if not first_sentence:
            return 3.0
        
        words = first_sentence[0].split()
        length = len(words)
        # Strong hooks are punchy (6-20 words) with tension words
        has_tension = any(w.lower() in first_sentence[0].lower() for w in ["mistake", "wrong", "broken", "truth", "never", "fail", "secret", "why", "stop"])
        
        if 5 <= length <= 22 and has_tension:
            return 7.0
        elif 5 <= length <= 28:
            return 6.0
        return 4.0

    @staticmethod
    def evaluate_formatting(text: str) -> float:
        """Evaluates 1-3-1 sentence cadence, subheadings, and bolding."""
        has_subheadings = len(re.findall(r"^###?\s+", text, re.MULTILINE)) >= 3
        has_bold = len(re.findall(r"\*\*.*?\*\*", text)) >= 4
        has_bullets = len(re.findall(r"^\s*[-*]\s+", text, re.MULTILINE)) >= 2

        score = 3.5
        if has_subheadings:
            score += 1.3
        if has_bold:
            score += 1.2
        if has_bullets:
            score += 1.0
        return min(7.5, max(2.5, score))

    @staticmethod
    def evaluate_structure(text: str) -> float:
        """Checks for standard essay progression (Hook, Problem, Insight, Playbook, Outcome)."""
        headings = [h.lower() for h in re.findall(r"^###?\s+(.+)", text, re.MULTILINE)]
        expected_signals = ["default", "problem", "mistake", "insight", "playbook", "framework", "step", "compounding", "effect", "takeaway"]
        
        matches = 0
        for sig in expected_signals:
            if any(sig in h for h in headings):
                matches += 1
                
        if matches >= 3:
            return 7.0
        elif matches >= 2:
            return 5.5
        elif len(headings) >= 3:
            return 5.0
        return 3.5

    @staticmethod
    def evaluate_narrative(text: str) -> float:
        """Evaluates logical flow and transitions between paragraphs."""
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30 and not p.startswith("#")]
        if len(paragraphs) < 4:
            return 3.5
        
        # Check transition words
        transition_signals = ["however", "instead", "because", "when", "first", "second", "then", "ultimately", "result"]
        transitions_found = sum(1 for p in paragraphs if any(w in p.lower() for w in transition_signals))
        
        ratio = transitions_found / len(paragraphs)
        if ratio >= 0.40:
            return 7.0
        elif ratio >= 0.25:
            return 5.5
        return 4.0

    @staticmethod
    def evaluate_useful_insight(text: str) -> float:
        """Evaluates named frameworks, actionable models, and specific playbooks."""
        actionable_signals = ["framework", "model", "loop", "playbook", "rule", "step", "strategy", "tactic", "matrix"]
        found = sum(1 for sig in actionable_signals if sig in text.lower())
        
        if found >= 4:
            return 7.2
        elif found >= 2:
            return 6.0
        elif found >= 1:
            return 4.5
        return 3.0

    @staticmethod
    def evaluate_grounding(text: str, contexts: List[str]) -> float:
        """Measures transcript grounding and absence of hallucination."""
        if not contexts or not text:
            return 3.0
            
        combined_context = " ".join(contexts).lower()
        sentences = extract_sentences(text)
        if not sentences:
            return 6.5
            
        supported = 0
        for s in sentences:
            words = [w.lower() for w in re.findall(r'\b\w{4,}\b', s)]
            if not words:
                supported += 1
                continue
            overlap = sum(1 for w in words if w in combined_context)
            if (overlap / len(words)) >= 0.35:
                supported += 1
                
        ratio = supported / len(sentences)
        # Scaled to center of 1-10 scale (maps high ratio to ~7.0-7.2)
        score = 2.5 + (ratio * 4.8)
        return round(min(7.5, max(2.5, score)), 2)

    @classmethod
    def evaluate_essay(
        cls,
        essay_text: str,
        contexts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Calculates 1-10 scores compressed to center scale and weighted composite."""
        grounding = cls.evaluate_grounding(essay_text, contexts or [])
        insight = cls.evaluate_useful_insight(essay_text)
        narrative = cls.evaluate_narrative(essay_text)
        hook = cls.evaluate_hook(essay_text)
        structure = cls.evaluate_structure(essay_text)
        formatting = cls.evaluate_formatting(essay_text)
        length = cls.evaluate_length(essay_text)

        weighted_score = (
            grounding * CRITERIA_WEIGHTS["grounding"] +
            insight * CRITERIA_WEIGHTS["useful_insight"] +
            narrative * CRITERIA_WEIGHTS["narrative"] +
            hook * CRITERIA_WEIGHTS["hook"] +
            structure * CRITERIA_WEIGHTS["structure"] +
            formatting * CRITERIA_WEIGHTS["formatting"] +
            length * CRITERIA_WEIGHTS["length"]
        )

        word_count = len(essay_text.split())

        return {
            "metrics": {
                "grounding": round(grounding, 2),
                "useful_insight": round(insight, 2),
                "narrative": round(narrative, 2),
                "hook": round(hook, 2),
                "structure": round(structure, 2),
                "formatting": round(formatting, 2),
                "length": round(length, 2)
            },
            "weights": CRITERIA_WEIGHTS,
            "composite_score": round(weighted_score, 2),
            "word_count": word_count
        }
