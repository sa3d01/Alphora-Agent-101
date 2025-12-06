from pydantic import BaseModel
from typing import List


class IncomingTicket(BaseModel):
    ticketId: str | None = None
    tenantId: str
    subject: str
    description: str
    requesterEmail: str | None = None


class ClassificationResult(BaseModel):
    intent: str
    riskLevel: str
    confidence: float


class RagResult(BaseModel):
    tenantId: str
    intent: str
    sopSteps: List[str]


class PlanRequest(BaseModel):
    ticketId: str
    classification: ClassificationResult
    ragResult: RagResult


class ActionPlan(BaseModel):
    ticketId: str
    intent: str
    decision: str | None = None
    steps: List[str]


class ExecutionLog(BaseModel):
    ticketId: str
    steps: List[str]
