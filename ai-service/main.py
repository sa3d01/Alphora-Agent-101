"""
AI Service - FastAPI application with RAG integration
Handles ticket classification, RAG retrieval, and action planning
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
import os

# Import RAG modules
from rag.retrieval import SOPRetriever
from rag.embeddings import get_embedding_service

app = FastAPI(
    title="Alphora Agent 101 - AI Service",
    description="AI-powered ticket classification and action planning",
    version="1.0.0"
)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'alphora_agent'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Initialize RAG retriever
retriever = SOPRetriever(DB_CONFIG)


# ============================================================================
# Models
# ============================================================================

class Intent(str, Enum):
    PASSWORD_RESET = "PASSWORD_RESET"
    SYSTEM_RESTART = "SYSTEM_RESTART"
    VPN_ACCESS = "VPN_ACCESS"
    BACKUP_VERIFICATION = "BACKUP_VERIFICATION"
    SOFTWARE_INSTALLATION = "SOFTWARE_INSTALLATION"
    PRINTER_ISSUE = "PRINTER_ISSUE"
    EMAIL_ISSUE = "EMAIL_ISSUE"
    NETWORK_CONNECTIVITY = "NETWORK_CONNECTIVITY"
    UNKNOWN = "UNKNOWN"


class TicketRequest(BaseModel):
    ticketId: str
    tenantId: str
    subject: str
    description: str
    priority: Optional[str] = "MEDIUM"
    requester_email: Optional[str] = None


class ClassificationResponse(BaseModel):
    intent: Intent
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    sub_category: Optional[str] = None
    is_automatable: bool = Field(description="Whether this ticket can be safely automated")
    reasoning: str = Field(description="Explanation for the classification")


class SOPResult(BaseModel):
    sop_id: int
    title: str
    content: str
    category: str
    similarity: float
    chunk_index: int


class RAGResponse(BaseModel):
    query: str
    tenant_id: str
    results: List[SOPResult]
    total_results: int


class ActionStep(BaseModel):
    step_number: int
    description: str
    estimated_time_seconds: int
    requires_approval: bool = False


class PlanResponse(BaseModel):
    ticket_id: str
    intent: Intent
    action_steps: List[ActionStep]
    total_estimated_time: int
    requires_human_approval: bool
    risk_level: str


# ============================================================================
# Intent Classification
# ============================================================================

def classify_ticket_intent(subject: str, description: str) -> ClassificationResponse:
    """
    Classify ticket intent based on subject and description.
    In production, this would use an LLM or fine-tuned model.
    For MVP, using rule-based classification with confidence scoring.
    """
    text = f"{subject} {description}".lower()

    # Rule-based classification with confidence scoring
    classification_rules = [
        {
            "intent": Intent.PASSWORD_RESET,
            "keywords": ["password", "reset", "forgot", "login", "cannot log in", "locked out", "credentials"],
            "confidence_base": 0.9
        },
        {
            "intent": Intent.SYSTEM_RESTART,
            "keywords": ["restart", "reboot", "slow", "frozen", "hung", "not responding", "performance"],
            "confidence_base": 0.85
        },
        {
            "intent": Intent.VPN_ACCESS,
            "keywords": ["vpn", "remote access", "work from home", "connect remotely", "access network"],
            "confidence_base": 0.9
        },
        {
            "intent": Intent.BACKUP_VERIFICATION,
            "keywords": ["backup", "restore", "data recovery", "backup failed"],
            "confidence_base": 0.85
        },
        {
            "intent": Intent.SOFTWARE_INSTALLATION,
            "keywords": ["install", "software", "application", "program", "need access to"],
            "confidence_base": 0.8
        },
        {
            "intent": Intent.PRINTER_ISSUE,
            "keywords": ["printer", "print", "printing", "cant print", "print job"],
            "confidence_base": 0.85
        },
        {
            "intent": Intent.EMAIL_ISSUE,
            "keywords": ["email", "outlook", "cannot send", "cannot receive", "mailbox"],
            "confidence_base": 0.85
        },
        {
            "intent": Intent.NETWORK_CONNECTIVITY,
            "keywords": ["network", "internet", "wifi", "connection", "cannot connect", "offline"],
            "confidence_base": 0.8
        }
    ]

    # Find matching intent
    best_match = None
    best_confidence = 0.0

    for rule in classification_rules:
        matches = sum(1 for keyword in rule["keywords"] if keyword in text)
        if matches > 0:
            # Confidence increases with number of keyword matches
            confidence = min(rule["confidence_base"] + (matches - 1) * 0.05, 0.98)
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = rule["intent"]

    if best_match is None:
        return ClassificationResponse(
            intent=Intent.UNKNOWN,
            confidence=0.0,
            is_automatable=False,
            reasoning="Could not classify ticket based on available keywords. Human review required."
        )

    # Determine if automatable based on intent and confidence
    automatable_intents = [
        Intent.PASSWORD_RESET,
        Intent.SYSTEM_RESTART,
        Intent.BACKUP_VERIFICATION,
        Intent.PRINTER_ISSUE
    ]

    is_automatable = best_match in automatable_intents and best_confidence >= 0.75

    return ClassificationResponse(
        intent=best_match,
        confidence=best_confidence,
        sub_category=None,
        is_automatable=is_automatable,
        reasoning=f"Classified as {best_match.value} based on keyword matching with {best_confidence:.2%} confidence."
    )


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Alphora Agent 101 - AI Service",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/classify", response_model=ClassificationResponse)
async def classify_ticket(ticket: TicketRequest):
    """
    Classify incoming ticket intent with confidence scoring.
    
    This endpoint determines what type of issue the ticket represents
    and whether it can be safely automated.
    """
    classification = classify_ticket_intent(ticket.subject, ticket.description)
    return classification


@app.post("/rag", response_model=RAGResponse)
async def retrieve_sops(ticket: TicketRequest, intent: Optional[Intent] = None):
    """
    Retrieve relevant SOPs using semantic search (RAG).
    
    Uses vector similarity search to find the most relevant procedures
    for the given ticket.
    """
    try:
        # Classify if intent not provided
        if intent is None:
            classification = classify_ticket_intent(ticket.subject, ticket.description)
            intent = classification.intent

        # Build search query
        query = f"{ticket.subject} {ticket.description}"

        # Map intent to category for hybrid search
        category_map = {
            Intent.PASSWORD_RESET: "password_reset",
            Intent.SYSTEM_RESTART: "system_restart",
            Intent.VPN_ACCESS: "vpn_access",
            Intent.BACKUP_VERIFICATION: "backup_verification",
        }

        category = category_map.get(intent)

        # Perform search
        if category:
            # Hybrid search: filter by category first
            results = retriever.hybrid_search(
                query=query,
                tenant_id=ticket.tenantId,
                category=category,
                top_k=3
            )
        else:
            # General semantic search
            results = retriever.search(
                query=query,
                tenant_id=ticket.tenantId,
                top_k=5,
                similarity_threshold=0.5
            )

        # Convert to response model
        sop_results = [
            SOPResult(
                sop_id=r['id'],
                title=r['title'],
                content=r['content'],
                category=r['category'],
                similarity=r['similarity'],
                chunk_index=r['chunk_index']
            )
            for r in results
        ]

        return RAGResponse(
            query=query,
            tenant_id=ticket.tenantId,
            results=sop_results,
            total_results=len(sop_results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG retrieval failed: {str(e)}")


@app.post("/plan", response_model=PlanResponse)
async def generate_action_plan(ticket: TicketRequest):
    """
    Generate action plan based on ticket classification and retrieved SOPs.
    
    This endpoint creates a step-by-step plan for resolving the ticket,
    including time estimates and approval requirements.
    """
    # Classify ticket
    classification = classify_ticket_intent(ticket.subject, ticket.description)

    # Retrieve relevant SOPs
    rag_response = await retrieve_sops(ticket, intent=classification.intent)

    # Generate action steps based on intent
    # In production, this would parse SOPs and use LLM for planning
    action_plans = {
        Intent.PASSWORD_RESET: [
            ActionStep(step_number=1, description="Verify user identity via email", estimated_time_seconds=120, requires_approval=False),
            ActionStep(step_number=2, description="Check account status in directory", estimated_time_seconds=60, requires_approval=False),
            ActionStep(step_number=3, description="Generate temporary password", estimated_time_seconds=30, requires_approval=False),
            ActionStep(step_number=4, description="Reset password in identity provider", estimated_time_seconds=60, requires_approval=True),
            ActionStep(step_number=5, description="Send temporary password to user securely", estimated_time_seconds=90, requires_approval=False),
            ActionStep(step_number=6, description="Verify successful login and password change", estimated_time_seconds=120, requires_approval=False),
        ],
        Intent.SYSTEM_RESTART: [
            ActionStep(step_number=1, description="Check system status and running processes", estimated_time_seconds=90, requires_approval=False),
            ActionStep(step_number=2, description="Notify user of pending restart", estimated_time_seconds=120, requires_approval=False),
            ActionStep(step_number=3, description="Save system state and logs", estimated_time_seconds=60, requires_approval=False),
            ActionStep(step_number=4, description="Initiate system restart via RMM", estimated_time_seconds=180, requires_approval=True),
            ActionStep(step_number=5, description="Verify system comes back online", estimated_time_seconds=300, requires_approval=False),
            ActionStep(step_number=6, description="Check all services started correctly", estimated_time_seconds=120, requires_approval=False),
        ],
        Intent.VPN_ACCESS: [
            ActionStep(step_number=1, description="Validate request and manager approval", estimated_time_seconds=180, requires_approval=False),
            ActionStep(step_number=2, description="Verify device security compliance", estimated_time_seconds=120, requires_approval=False),
            ActionStep(step_number=3, description="Create VPN user profile", estimated_time_seconds=180, requires_approval=True),
            ActionStep(step_number=4, description="Configure multi-factor authentication", estimated_time_seconds=240, requires_approval=False),
            ActionStep(step_number=5, description="Deploy VPN client to user device", estimated_time_seconds=300, requires_approval=False),
            ActionStep(step_number=6, description="Test connection with user", estimated_time_seconds=420, requires_approval=False),
        ],
        Intent.BACKUP_VERIFICATION: [
            ActionStep(step_number=1, description="Access backup management console", estimated_time_seconds=60, requires_approval=False),
            ActionStep(step_number=2, description="Review last 24 hours of backup jobs", estimated_time_seconds=180, requires_approval=False),
            ActionStep(step_number=3, description="Verify backup integrity and file sizes", estimated_time_seconds=240, requires_approval=False),
            ActionStep(step_number=4, description="Perform test restore if needed", estimated_time_seconds=600, requires_approval=True),
            ActionStep(step_number=5, description="Document verification results", estimated_time_seconds=120, requires_approval=False),
        ]
    }

    # Get appropriate action plan
    steps = action_plans.get(
        classification.intent,
        [ActionStep(step_number=1, description="Manual investigation required", estimated_time_seconds=1800, requires_approval=True)]
    )

    # Calculate totals
    total_time = sum(step.estimated_time_seconds for step in steps)
    requires_approval = any(step.requires_approval for step in steps) or not classification.is_automatable

    # Determine risk level
    risk_level = "LOW" if classification.is_automatable and classification.confidence > 0.85 else "MEDIUM"
    if classification.confidence < 0.6 or classification.intent == Intent.UNKNOWN:
        risk_level = "HIGH"

    return PlanResponse(
        ticket_id=ticket.ticketId,
        intent=classification.intent,
        action_steps=steps,
        total_estimated_time=total_time,
        requires_human_approval=requires_approval,
        risk_level=risk_level
    )


@app.get("/stats/{tenant_id}")
async def get_rag_statistics(tenant_id: str):
    """Get statistics about the RAG database for a tenant."""
    try:
        stats = retriever.get_statistics(tenant_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)