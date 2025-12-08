"""
This module contains the core agent logic:

- Planning: decide which actions to take based on classification + SOPs
- Execution: call mock tool functions
- Reply composition: generate the final message

MVP logic is intentionally simple.
"""

from typing import List
from src.models import ClassificationResult, RetrievalResult, ActionResult, AgentReply
from src.agent.tool_registry import get_tool

class SupportAgent:

    def plan(self, classification: ClassificationResult, retrieval: RetrievalResult) -> List[str]:
        """
        Minimal rule-based action planner.
        Later, we can replace this with LLM reasoning.
        """

        category = classification.category.lower()

        if "password" in category:
            return ["reset_password"]

        if "performance" in category or "slow" in category:
            return ["collect_logs", "restart_machine"]

        # fallback
        return []

    def execute_actions(self, actions: List[str]) -> List[ActionResult]:
        results = []

        for action_name in actions:
            tool = get_tool(action_name)

            if tool is None:
                results.append(ActionResult(
                    action_name=action_name,
                    success=False,
                    output="Action not implemented"
                ))
                continue

            output = tool()  # tools in MVP take no parameters
            results.append(ActionResult(
                action_name=action_name,
                success=True,
                output=output
            ))

        return results

    def compose_reply(self, ticket, classification, action_results) -> AgentReply:
        """
        Generates the final message shown to the user.
        For the MVP, this is simple template logic.
        """

        if not action_results:
            msg = (
                f"I reviewed your issue ('{ticket.text}'). "
                "No automated actions were needed. "
                "Let me know if you'd like further help."
            )
        else:
            executed = ", ".join([r.action_name for r in action_results])
            msg = (
                f"I’ve processed your request regarding '{ticket.text}'.\n"
                f"The following actions were completed: {executed}.\n"
                "Please check again and let me know if the issue persists."
            )

        return AgentReply(message=msg, actions=action_results)
