"""
This script simulates an end-to-end support ticket flow:

1. Read a ticket from user input
2. Classify the issue (LLM + heuristics)
3. Retrieve relevant SOPs from the RAG database
4. Let the agent plan actions based on classification + SOPs
5. Execute mock actions
6. Generate final reply

As we build the system, each step will be replaced
with real logic from the corresponding modules.
"""


from src.models import Ticket
from src.classification.classifier import HybridClassifier
from rag.retriever import Retriever
from src.agent.agent_core import SupportAgent

def main():

    print("\n--- Alphora Agent 101 Simulator ---")
    user_input = input("Enter ticket description:\n> ").strip()

    ticket = Ticket(text=user_input)

    # ------------------------------
    # Step 1: Classification
    # ------------------------------
    classifier = HybridClassifier()
    classification = classifier.classify(ticket.text)

    print("\n--- Classification ---")
    print(f"Category: {classification.category} (confidence: {classification.confidence:.2f})")
    print(f"Reason: {classification.reason}")

    # ------------------------------
    # Step 2: Retrieval (RAG)
    # ------------------------------
    retriever = Retriever()
    retrieval = retriever.retrieve(ticket.text)

    print("\n--- Retrieved SOPs ---")
    if retrieval.doc_names:
        for name in retrieval.doc_names:
            print(f"• {name}")
    else:
        print("No SOPs found")

    # ------------------------------
    # Step 3: Agent Planning + Actions
    # ------------------------------
    agent = SupportAgent()
    action_plan = agent.plan(classification, retrieval)

    print("\n--- Planned Actions ---")
    if not action_plan:
        print("No actions needed.")
    else:
        for a in action_plan:
            print(f"- {a}")

    # ------------------------------
    # Step 4: Execute Actions
    # ------------------------------
    results = agent.execute_actions(action_plan)

    print("\n--- Executed ---")
    for result in results:
        status = "✔" if result.success else "✖"
        print(f"{status} {result.action_name} → {result.output}")

    # ------------------------------
    # Step 5: Final Reply
    # ------------------------------
    reply = agent.compose_reply(ticket, classification, results)

    print("\n--- Agent Reply ---")
    print(reply.message)


if __name__ == "__main__":
    main()
