from fastapi import FastAPI
from models import IncomingTicket, ClassificationResult, RagResult, PlanRequest, ActionPlan, ExecutionLog
from sop_data import SOPS

app = FastAPI(title="AI Service Mock")


@app.post("/classify", response_model=ClassificationResult)
def classify(ticket: IncomingTicket):
    text = (ticket.subject + " " + ticket.description).lower()

    if "password" in text or "reset" in text:
        intent = "PASSWORD_RESET"
    elif "printer" in text:
        intent = "PRINTER_ISSUE"
    elif "vpn" in text or "remote access" in text:
        intent = "VPN_ACCESS"
    else:
        intent = "UNKNOWN"

    risk = "LOW" if intent in {"PASSWORD_RESET", "PRINTER_ISSUE", "VPN_ACCESS"} else "HIGH"
    confidence = 0.9 if intent != "UNKNOWN" else 0.4

    return ClassificationResult(intent=intent, riskLevel=risk, confidence=confidence)


@app.post("/rag", response_model=RagResult)
def rag(ticket: IncomingTicket):
    # MVP: just map according to simple heuristic from classify
    classification = classify(ticket)
    steps = SOPS.get(classification.intent, ["No SOP found, escalate to human."])
    return RagResult(tenantId=ticket.tenantId, intent=classification.intent, sopSteps=steps)


@app.post("/plan", response_model=ActionPlan)
def plan(req: PlanRequest):
    # For MVP: action plan = SOP steps as-is
    return ActionPlan(
        ticketId=req.ticketId,
        intent=req.classification.intent,
        steps=req.ragResult.sopSteps,
        decision=None  # Orchestrator decides
    )


@app.post("/execute-mock")
def execute_mock(plan: ActionPlan):
    # In a real system, this would call tools; here we just print/log
    print(f"[MOCK EXEC] Ticket {plan.ticketId}:")
    for step in plan.steps:
        print(f" - {step}")
    return {"status": "ok"}
