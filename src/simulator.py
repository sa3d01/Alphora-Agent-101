# src/simulator.py

import json
from pathlib import Path

from .classifier import Ticket, RuleBasedClassifier
from .rag import RAGKnowledgeBase
from .actions import ToolExecutor
from .agent import SupportAgent


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_tickets(path: str) -> list[Ticket]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        Ticket(
            id=item["id"],
            client_id=item["client_id"],
            subject=item["subject"],
            description=item["description"],
            priority=item.get("priority", "P3"),
        )
        for item in raw
    ]


def print_decision(agent: SupportAgent, idx: int, ticket: Ticket) -> None:
    print("=" * 80)
    print(f"🎫  Demo Ticket #{idx+1}: {ticket.id} ({ticket.client_id})")
    print("-" * 80)
    print(f"Subject   : {ticket.subject}")
    print(f"Priority  : {ticket.priority}")
    print(f"Desc      : {ticket.description}")
    print()

    decision = agent.handle_ticket(ticket)

    # 6.2 show classification
    print("🔎 Classification")
    print(f"  Label      : {decision.classification.label}")
    print(f"  Confidence : {decision.classification.confidence}")
    for reason in decision.classification.reasons:
        print(f"   - {reason}")
    print()

    # 6.3 show RAG retrieval
    print("📚 RAG Retrieval (top SOPs)")
    if not decision.rag_results:
        print("  No SOPs found.")
    else:
        for res in decision.rag_results:
            print(f"  - {res.sop.title} [client={res.sop.client_id}] (score={res.score})")
    print()

    # 6.4 show action plan
    print("🛠  Proposed Action Plan (tools/actions)")
    if not decision.action_plan:
        print("  No automated actions proposed (requires human triage).")
    else:
        for step in decision.action_plan:
            approval = "YES" if step.human_approval_required else "NO"
            print(
                f"  - {step.action_name} | human_approval_required={approval} | context={step.context}"
            )
    print()

    # 6.1 Email / reply template
    print("✉️  Draft Email / Reply Template")
    print("-" * 80)
    print(decision.draft_reply)
    print("-" * 80)
    print()

    # simulate executing actions (as if human approved)
    if decision.action_plan:
        print("⚙️  Simulated Tool Execution (assuming human approved)")
        results = agent.execute_action_plan(decision)
        for res in results:
            print(f"  - {res.name}: success={res.success}, details={res.details}")
        print()

    print(f"Requires human technician? {'YES' if decision.requires_human else 'NO'}")
    print("=" * 80)
    print("\n\n")


def main() -> None:
    tickets = load_tickets(str(DATA_DIR / "tickets.json"))
    kb = RAGKnowledgeBase.from_file(str(DATA_DIR / "sops.json"))
    classifier = RuleBasedClassifier()
    tools = ToolExecutor()
    agent = SupportAgent(kb=kb, classifier=classifier, tools=tools)

    print("Alphora Agent 101 — Mock Demo")
    print("Knowledge base stats:", kb.to_dict())
    print("Available actions:", tools.list_actions())
    print()

    for idx, ticket in enumerate(tickets):
        print_decision(agent, idx, ticket)


if __name__ == "__main__":
    main()
