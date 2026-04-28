from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import ProjectConfig

STATES = {"planned", "assigned", "implemented", "validating", "needs_fix", "blocked", "passed", "committed", "parked"}

ALLOWED_TRANSITIONS = {
    "planned": {"assigned", "implemented", "validating", "blocked", "parked"},
    "assigned": {"implemented", "blocked", "parked"},
    "implemented": {"validating", "needs_fix", "blocked", "passed"},
    "validating": {"passed", "needs_fix", "blocked", "parked"},
    "needs_fix": {"assigned", "implemented", "validating", "blocked", "parked"},
    "blocked": {"planned", "assigned", "validating", "parked"},
    "passed": {"planned", "committed", "needs_fix", "validating"},
    "committed": {"planned", "validating", "parked"},
    "parked": {"planned", "assigned", "blocked"},
}


def validate_transition(from_state: str, to_state: str) -> bool:
    if from_state not in STATES or to_state not in STATES:
        return False
    return to_state in ALLOWED_TRANSITIONS.get(from_state, set())


def task_state_path(project: ProjectConfig) -> Path:
    return project.repo_path / project.logs_dir / f"{project.project_id}_task_state.json"


def load_task_state(project: ProjectConfig) -> dict[str, Any]:
    path = task_state_path(project)
    if not path.exists():
        return {
            "project_id": project.project_id,
            "state": "planned",
            "history": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def save_task_state(project: ProjectConfig, state: dict[str, Any]) -> Path:
    path = task_state_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return path


def transition_task_state(project: ProjectConfig, to_state: str, reason: str) -> dict[str, Any]:
    state = load_task_state(project)
    from_state = state.get("state", "planned")
    if from_state != to_state and not validate_transition(from_state, to_state):
        raise ValueError(f"Invalid task state transition: {from_state} -> {to_state}")
    state["state"] = to_state
    state.setdefault("history", []).append(
        {
            "at": datetime.now(timezone.utc).isoformat(),
            "from": from_state,
            "to": to_state,
            "reason": reason,
        }
    )
    save_task_state(project, state)
    return state
