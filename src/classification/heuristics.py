"""
Heuristic classifier:
A simple keyword-based fallback that guarantees deterministic behavior.

This is useful for:
- low-confidence LLM outputs
- pre-filtering categories
- transparent debugging
"""

from src.models import ClassificationResult

HEURISTIC_RULES = {
    "PASSWORD_RESET": ["password", "reset", "forgot"],
    "PERFORMANCE_ISSUE": ["slow", "lag", "freeze"],
    "NETWORK_ISSUE": ["network", "vpn", "connection", "wifi"],
    "APPLICATION_ERROR": ["error", "crash", "bug"],
}


class HeuristicClassifier:

    def classify(self, text: str) -> ClassificationResult:
        text_lower = text.lower()

        for category, keywords in HEURISTIC_RULES.items():
            if any(word in text_lower for word in keywords):
                return ClassificationResult(
                    category=category,
                    confidence=0.80,     # high because it's deterministic
                    reason=f"Matched heuristic keywords: {keywords}"
                )

        return ClassificationResult(
            category="UNKNOWN",
            confidence=0.20,
            reason="No heuristic rule matched"
        )
