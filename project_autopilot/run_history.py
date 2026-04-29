from __future__ import annotations

import json
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import ProjectConfig, load_project_config


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_run_id(project_id: str, label: str = "run") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{project_id}_{label}_{stamp}"


def history_path(project: ProjectConfig) -> Path:
    return project.repo_path / project.logs_dir / "run_history.jsonl"


def append_event(project: ProjectConfig, run_id: str, event_type: str, details: dict[str, Any] | None = None) -> None:
    path = history_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp_utc": utc_now(),
        "project_id": project.project_id,
        "run_id": run_id,
        "event_type": event_type,
        "details": details or {},
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def record_run_started(project: ProjectConfig, run_id: str, mode: str) -> None:
    append_event(project, run_id, "run_started", {"mode": mode})


def record_run_finished(project: ProjectConfig, run_id: str, status: str, details: dict[str, Any] | None = None) -> None:
    payload = {"status": status}
    if details:
        payload.update(details)
    append_event(project, run_id, "run_finished", payload)


def read_events(project: ProjectConfig) -> list[dict[str, Any]]:
    path = history_path(project)
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _empty_summary(project_id: str, run_id: str) -> dict[str, Any]:
    return {
        "project_id": project_id,
        "run_id": run_id,
        "started_at": None,
        "finished_at": None,
        "duration_seconds": None,
        "status": None,
        "outcome": None,
        "commands_count": 0,
        "failed_commands_count": 0,
        "files_created": 0,
        "files_modified": 0,
        "files_deleted": 0,
        "lines_added": 0,
        "lines_removed": 0,
        "evidence_bundle_path": None,
        "qa_verdict": None,
        "risk_level": None,
        "estimated_model_cost": None,
        "paid_api_calls": None,
    }


def summarize_events(events: list[dict[str, Any]], project_id: str, limit: int = 5) -> list[dict[str, Any]]:
    grouped: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for event in events:
        if event.get("project_id") != project_id:
            continue
        run_id = event.get("run_id")
        if not run_id:
            continue
        summary = grouped.setdefault(run_id, _empty_summary(project_id, run_id))
        event_type = event.get("event_type")
        details = event.get("details", {})
        timestamp = event.get("timestamp_utc")

        if event_type == "run_started":
            summary["started_at"] = timestamp
        elif event_type == "run_finished":
            summary["finished_at"] = timestamp
            summary["status"] = details.get("status")
            summary["outcome"] = details.get("outcome", details.get("status"))
            _merge_file_metrics(summary, details.get("file_change_metrics", {}))
            if "estimated_model_cost" in details:
                summary["estimated_model_cost"] = details["estimated_model_cost"]
            if "paid_api_calls" in details:
                summary["paid_api_calls"] = details["paid_api_calls"]
        elif event_type == "command_finished":
            summary["commands_count"] += 1
            if details.get("exit_code") not in (0, None):
                summary["failed_commands_count"] += 1
        elif event_type == "evidence_bundle_created":
            summary["evidence_bundle_path"] = details.get("path")
            _merge_file_metrics(summary, details.get("file_change_metrics", {}))
        elif event_type == "qa_verdict_created":
            summary["qa_verdict"] = details.get("verdict")
            summary["risk_level"] = details.get("risk_level")
        elif event_type == "research_requested":
            summary["outcome"] = summary.get("outcome") or "research_requested"
        elif event_type == "error":
            summary["outcome"] = "error"

    summaries = list(grouped.values())
    for summary in summaries:
        started = _parse_time(summary.get("started_at"))
        finished = _parse_time(summary.get("finished_at"))
        if started and finished:
            summary["duration_seconds"] = round((finished - started).total_seconds(), 3)
    return summaries[-limit:][::-1]


def _merge_file_metrics(summary: dict[str, Any], metrics: dict[str, Any]) -> None:
    for key in ["files_created", "files_modified", "files_deleted", "lines_added", "lines_removed"]:
        if key in metrics:
            summary[key] = metrics[key]


def summarize_recent_runs(project_id: str, limit: int = 5) -> list[dict[str, Any]]:
    project = load_project_config(project_id)
    return summarize_events(read_events(project), project_id, limit=limit)


def count_research_requests(project: ProjectConfig) -> int:
    return sum(1 for event in read_events(project) if event.get("project_id") == project.project_id and event.get("event_type") == "research_requested")

