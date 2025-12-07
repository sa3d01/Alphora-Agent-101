# src/actions.py

from dataclasses import dataclass
from typing import Dict, Any, List, Callable
import datetime as dt


@dataclass
class ActionResult:
    name: str
    success: bool
    details: str
    metadata: Dict[str, Any]


def restart_system(context: Dict[str, Any]) -> ActionResult:
    target = context.get("target", "unknown-host")
    return ActionResult(
        name="restart_system",
        success=True,
        details=f"Simulated restart of system '{target}'. No real system was harmed.",
        metadata={"timestamp": dt.datetime.utcnow().isoformat() + "Z"},
    )


def reset_password(context: Dict[str, Any]) -> ActionResult:
    username = context.get("username", "unknown-user")
    temp_password = "Temp#1234"  # demo only
    return ActionResult(
        name="reset_password",
        success=True,
        details=f"Simulated password reset for '{username}' with a temporary password.",
        metadata={
            "timestamp": dt.datetime.utcnow().isoformat() + "Z",
            "temporary_password": temp_password,
        },
    )


def check_backup_status(context: Dict[str, Any]) -> ActionResult:
    job = context.get("backup_job", "default-backup-job")
    return ActionResult(
        name="check_backup_status",
        success=True,
        details=f"Simulated check of backup job '{job}'. Last run reported SUCCESS.",
        metadata={
            "timestamp": dt.datetime.utcnow().isoformat() + "Z",
            "last_status": "SUCCESS",
        },
    )


class ToolExecutor:
    """
    Extremely thin abstraction around a tool/workbench.
    In real life, each of these would be remote calls, scripts, or RMM actions.
    """

    def __init__(self) -> None:
        self.registry: Dict[str, Callable[[Dict[str, Any]], ActionResult]] = {
            "restart_system": restart_system,
            "reset_password": reset_password,
            "check_backup_status": check_backup_status,
        }

    def execute(self, action_name: str, context: Dict[str, Any]) -> ActionResult:
        if action_name not in self.registry:
            return ActionResult(
                name=action_name,
                success=False,
                details=f"Unknown action '{action_name}'",
                metadata={},
            )
        return self.registry[action_name](context)

    def list_actions(self) -> List[str]:
        return sorted(self.registry.keys())
