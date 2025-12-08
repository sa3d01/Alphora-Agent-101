"""
Core data structures used across the system.

These are intentionally simple dataclasses that model:
- the incoming ticket
- classification results
- retrieval results
- action execution responses
- the final agent reply
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Ticket:
    text: str


@dataclass
class ClassificationResult:
    category: str
    confidence: float
    reason: str  # brief explanation, useful for debugging


@dataclass
class RetrievalResult:
    documents: List[str]  # list of retrieved SOP contents
    doc_names: List[str]  # filenames for transparency


@dataclass
class ActionResult:
    action_name: str
    success: bool
    output: str


@dataclass
class AgentReply:
    message: str
    actions: List[ActionResult]
