"""
LLM-based ticket classifier.

This is intentionally minimal:
- Small prompt
- Low temperature
- Output is a simple JSON with {category, confidence}

Later this can be replaced with a more advanced agent.
"""

import json
from typing import Optional
from src.models import ClassificationResult

try:
    from openai import OpenAI
    client = OpenAI()
except Exception:
    client = None  # repo still works without API keys


CLASS_LABELS = [
    "PASSWORD_RESET",
    "PERFORMANCE_ISSUE",
    "NETWORK_ISSUE",
    "APPLICATION_ERROR",
    "OTHER"
]


class LLMClassifier:

    def classify(self, text: str) -> Optional[ClassificationResult]:
        """
        Returns None if:
        - API key not available
        - Request fails
        """

        if client is None:
            return None  # gracefully degrade

        prompt = f"""
You are a support agent. Classify the following ticket into one of these categories:
{CLASS_LABELS}

Ticket:
\"\"\"{text}\"\"\"

Respond ONLY in JSON:
{{
 "category": "...",
 "confidence": 0.0,
 "reason": "..."
}}
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )

            content = response.choices[0].message["content"]
            parsed = json.loads(content)

            return ClassificationResult(
                category=parsed.get("category", "OTHER"),
                confidence=float(parsed.get("confidence", 0.5)),
                reason=parsed.get("reason", "LLM decision")
            )

        except Exception:
            return None
