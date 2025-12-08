"""
Hybrid classifier that combines:
1. Heuristic classifier (deterministic, reliable)
2. LLM classifier (context-aware)

Logic:
- Try LLM first (if available)
- If LLM confidence < threshold → fallback to heuristics
- If LLM unavailable → use heuristics only

This ensures stable behavior and predictable categories.
"""

from src.classification.heuristics import HeuristicClassifier
from src.classification.llm_classifier import LLMClassifier
from src.models import ClassificationResult

LOW_CONFIDENCE_THRESHOLD = 0.55


class HybridClassifier:

    def __init__(self):
        self.heuristic = HeuristicClassifier()
        self.llm = LLMClassifier()

    def classify(self, text: str) -> ClassificationResult:

        # ---------------------------
        # Try LLM first
        # ---------------------------
        llm_result = self.llm.classify(text)

        if llm_result:
            if llm_result.confidence >= LOW_CONFIDENCE_THRESHOLD:
                return llm_result
            else:
                # fallback to heuristics
                heur = self.heuristic.classify(text)
                return ClassificationResult(
                    category=heur.category,
                    confidence=heur.confidence,
                    reason=f"LLM result too weak → {llm_result.reason}; fallback: {heur.reason}"
                )

        # ---------------------------
        # If LLM is unavailable
        # ---------------------------
        return self.heuristic.classify(text)
