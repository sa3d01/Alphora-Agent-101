"""
Maps action names to Python functions.

This abstraction makes it easy for:
- the agent to call tools dynamically
- future extension (parameterized tools)
"""

from src.actions.restart_machine import restart_machine
from src.actions.reset_password import reset_password
from src.actions.collect_logs import collect_logs


TOOLS = {
    "restart_machine": restart_machine,
    "reset_password": reset_password,
    "collect_logs": collect_logs,
}


def get_tool(name: str):
    return TOOLS.get(name)
