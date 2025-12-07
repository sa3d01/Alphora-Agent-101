# src/classifier.py

from dataclasses import dataclass
from typing import List, Tuple
import re


@dataclass
class Ticket:
    id: str
    client_id: str
    subject: str
    description: str
    priority: str


@dataclass
class TicketClassification:
    ticket_id: str
    label: str
    confidence: float
    reasons: List[str]


class RuleBasedClassifier:
    """
    Minimal rule-based classifier to keep the demo simple.
    In a real system, this would be replaced by an LLM or ML model.
    """

    def __init__(self) -> None:
        # Keyword patterns per class
        self.rules = {
            "password_reset": [
                r"cannot log in",
                r"can't log in",
                r"login issue",
                r"password reset",
                r"invalid credentials",
            ],
            "system_restart": [
                r"server (down|unresponsive)",
                r"blue screen",
                r"reboot",
                r"restart server",
            ],
            "performance_issue": [
                r"high cpu",
                r"cpu usage",
                r"slow performance",
                r"system running slow",
            ],
            "backup_failure": [
                r"backup failed",
                r"backup job failed",
                r"backup reported as failed",
            ],
        }

    def classify(self, ticket: Ticket) -> TicketClassification:
        text = f"{ticket.subject} {ticket.description}".lower()
        best_label = "unknown"
        best_score = 0.0
        reasons: List[str] = []

        for label, patterns in self.rules.items():
            hits = 0
            for pattern in patterns:
                if re.search(pattern, text):
                    hits += 1
                    reasons.append(f"Matched pattern '{pattern}' for label '{label}'")

            # simple score: hits per label
            score = hits / max(len(patterns), 1)
            if score > best_score:
                best_score = score
                best_label = label

        # if no good match, fallback to unknown
        if best_score == 0.0:
            reasons.append("No rule matched; defaulting to 'unknown'")

        confidence = round(min(0.2 + best_score, 0.99), 2)

        return TicketClassification(
            ticket_id=ticket.id,
            label=best_label,
            confidence=confidence,
            reasons=reasons,
        )
