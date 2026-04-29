from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import ProjectConfig
from run_history import append_event

VALID_RESEARCH_MODES = {"quick_check", "standard_research", "deep_research"}


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def research_index_path(project: ProjectConfig) -> Path:
    return project.repo_path / project.logs_dir / "research_index.jsonl"


def record_research_request(
    project: ProjectConfig,
    run_id: str,
    topic: str,
    reason: str,
    mode: str = "quick_check",
    estimated_duration_minutes: int = 15,
    requires_human_approval: bool = True,
    status: str = "requested",
    result_file: str | None = None,
) -> dict[str, Any]:
    if mode not in VALID_RESEARCH_MODES:
        raise ValueError(f"Invalid research mode: {mode}")
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        "research_id": f"{project.project_id}_research_{_stamp()}",
        "mode": mode,
        "topic": topic,
        "reason": reason,
        "status": status,
        "estimated_duration_minutes": estimated_duration_minutes,
        "requires_human_approval": requires_human_approval,
        "result_file": result_file,
    }
    path = research_index_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    append_event(project, run_id, "research_requested", record)
    return record


def count_research_index(project: ProjectConfig) -> int:
    path = research_index_path(project)
    if not path.exists():
        return 0
    return len([line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()])
