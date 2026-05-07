from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import ProjectConfig
from run_history import append_event

VALID_RESEARCH_MODES = {"quick_check", "standard_research", "deep_research"}
VALID_RESEARCH_STATUSES = {"requested", "approved", "in_progress", "completed", "rejected", "parked"}

MODE_DEFAULTS = {
    "quick_check": {"estimated_minutes": 15, "requires_human_approval": False, "range": "10-15 min"},
    "standard_research": {"estimated_minutes": 45, "requires_human_approval": False, "range": "30-45 min"},
    "deep_research": {"estimated_minutes": 90, "requires_human_approval": True, "range": "90+ min"},
}


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def research_index_path(project: ProjectConfig) -> Path:
    return project.repo_path / project.logs_dir / "research" / f"{project.project_id}_research_index.jsonl"


def legacy_research_index_path(project: ProjectConfig) -> Path:
    return project.repo_path / project.logs_dir / "research_index.jsonl"


def record_research_request(
    project: ProjectConfig,
    run_id: str,
    topic: str,
    reason: str,
    mode: str = "quick_check",
    estimated_duration_minutes: int | None = None,
    estimated_minutes: int | None = None,
    requires_human_approval: bool | None = None,
    requested_by: str = "Project Autopilot",
    status: str = "requested",
    result_file: str | None = None,
    sources_count: int | None = None,
    linked_task: str | None = None,
) -> dict[str, Any]:
    if mode not in VALID_RESEARCH_MODES:
        raise ValueError(f"Invalid research mode: {mode}")
    if status not in VALID_RESEARCH_STATUSES:
        raise ValueError(f"Invalid research status: {status}")

    defaults = MODE_DEFAULTS[mode]
    minutes = estimated_minutes or estimated_duration_minutes or int(defaults["estimated_minutes"])
    approval = bool(defaults["requires_human_approval"]) if requires_human_approval is None else requires_human_approval
    if mode == "deep_research":
        approval = True

    record = {
        "research_id": f"{project.project_id}_research_{_stamp()}",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        "topic": topic,
        "mode": mode,
        "estimated_minutes": minutes,
        "requested_by": requested_by,
        "reason": reason,
        "status": status,
        "requires_human_approval": approval,
        "result_file": result_file,
        "sources_count": sources_count,
        "linked_task": linked_task,
    }
    path = research_index_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    append_event(project, run_id, "research_requested", record, task_title=linked_task, status=status)
    return record


def read_research_entries(project: ProjectConfig) -> list[dict[str, Any]]:
    entries = [_normalize_entry(item) for item in _read_jsonl(legacy_research_index_path(project)) + _read_jsonl(research_index_path(project))]
    entries = [entry for entry in entries if entry.get("project_id") == project.project_id]
    return sorted(entries, key=lambda entry: entry.get("timestamp_utc") or "")


def summarize_research(project: ProjectConfig) -> dict[str, Any]:
    entries = read_research_entries(project)
    deep_pending = [
        entry for entry in entries
        if entry.get("mode") == "deep_research"
        and entry.get("requires_human_approval")
        and entry.get("status") in {"requested", "parked"}
    ]
    completed = [entry for entry in entries if entry.get("status") == "completed"]
    latest = entries[-1] if entries else None
    return {
        "count": len(entries),
        "deep_research_pending_approval": len(deep_pending),
        "completed_count": len(completed),
        "latest": latest,
        "entries": entries,
    }


def count_research_index(project: ProjectConfig) -> int:
    return len(read_research_entries(project))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    if "timestamp_utc" in entry:
        return entry
    return {
        "research_id": entry.get("research_id"),
        "timestamp_utc": entry.get("timestamp"),
        "project_id": entry.get("project_id"),
        "topic": entry.get("topic"),
        "mode": entry.get("mode"),
        "estimated_minutes": entry.get("estimated_minutes") or entry.get("estimated_duration_minutes"),
        "requested_by": entry.get("requested_by", "Project Autopilot"),
        "reason": entry.get("reason"),
        "status": entry.get("status"),
        "requires_human_approval": entry.get("requires_human_approval"),
        "result_file": entry.get("result_file"),
        "sources_count": entry.get("sources_count"),
        "linked_task": entry.get("linked_task"),
    }
