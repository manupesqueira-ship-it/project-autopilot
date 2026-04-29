from __future__ import annotations

import json
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import ProjectConfig, load_project_config


PROMOTED_KEYS = {
    "task_title",
    "command",
    "file_path",
    "path",
    "status",
    "outcome",
    "duration_seconds",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_run_id(project_id: str, label: str = "run") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{project_id}_{label}_{stamp}"


def history_path(project: ProjectConfig) -> Path:
    return project.repo_path / project.logs_dir / "run_history" / f"{project.project_id}.jsonl"


def legacy_history_path(project: ProjectConfig) -> Path:
    return project.repo_path / project.logs_dir / "run_history.jsonl"


def append_event(
    project: ProjectConfig,
    run_id: str,
    event_type: str,
    details: dict[str, Any] | None = None,
    *,
    task_title: str | None = None,
    command: str | None = None,
    file_path: str | None = None,
    status: str | None = None,
    duration_seconds: float | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Append one secret-safe event to per-project JSONL run history.

    `details` is kept for backward compatibility with older call sites. Common
    keys are promoted to top-level fields while the full payload remains under
    `metadata` so existing summaries continue to work.
    """
    payload = dict(details or {})
    if metadata:
        payload.update(metadata)

    event = {
        "timestamp_utc": utc_now(),
        "project_id": project.project_id,
        "run_id": run_id,
        "event_type": event_type,
        "task_title": task_title or payload.get("task_title"),
        "command": command or payload.get("command"),
        "file_path": file_path or payload.get("file_path") or payload.get("path") or payload.get("report"),
        "status": status or payload.get("status") or payload.get("outcome"),
        "duration_seconds": duration_seconds if duration_seconds is not None else payload.get("duration_seconds"),
        "metadata": payload,
    }
    path = history_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_json_safe(event), sort_keys=True) + "\n")


def record_run_started(project: ProjectConfig, run_id: str, mode: str, task_title: str | None = None) -> None:
    append_event(project, run_id, "run_started", {"mode": mode}, task_title=task_title, status="started")


def record_run_finished(project: ProjectConfig, run_id: str, status: str, details: dict[str, Any] | None = None) -> None:
    payload = {"status": status}
    if details:
        payload.update(details)
    append_event(project, run_id, "run_finished", payload, status=status)


def read_events(project: ProjectConfig) -> list[dict[str, Any]]:
    events = _read_jsonl(history_path(project))
    legacy = _read_jsonl(legacy_history_path(project))
    combined = [_normalize_event(event) for event in legacy + events]
    combined = [event for event in combined if event.get("project_id") == project.project_id]
    return sorted(combined, key=lambda event: event.get("timestamp_utc") or "")


def recent_events(project: ProjectConfig, limit: int = 10) -> list[dict[str, Any]]:
    return read_events(project)[-limit:][::-1]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    if "metadata" in event:
        return event
    details = event.get("details", {})
    return {
        "timestamp_utc": event.get("timestamp_utc") or event.get("timestamp") or event.get("at"),
        "project_id": event.get("project_id"),
        "run_id": event.get("run_id"),
        "event_type": event.get("event_type"),
        "task_title": details.get("task_title"),
        "command": details.get("command"),
        "file_path": details.get("file_path") or details.get("path") or details.get("report"),
        "status": details.get("status") or details.get("outcome"),
        "duration_seconds": details.get("duration_seconds"),
        "metadata": details,
    }


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
        "active_duration_seconds": 0.0,
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
        "blockers_opened": 0,
        "research_requests": 0,
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
        metadata = event.get("metadata", {})
        timestamp = event.get("timestamp_utc")

        if event_type == "run_started":
            summary["started_at"] = timestamp
        elif event_type == "run_finished":
            summary["finished_at"] = timestamp
            summary["status"] = event.get("status") or metadata.get("status")
            summary["outcome"] = metadata.get("outcome", summary["status"])
            _merge_file_metrics(summary, metadata.get("file_change_metrics", {}))
            summary["estimated_model_cost"] = metadata.get("estimated_model_cost", summary.get("estimated_model_cost"))
            summary["paid_api_calls"] = metadata.get("paid_api_calls", summary.get("paid_api_calls"))
        elif event_type == "command_finished":
            summary["commands_count"] += 1
            duration = event.get("duration_seconds")
            if isinstance(duration, (int, float)):
                summary["active_duration_seconds"] = round(summary["active_duration_seconds"] + float(duration), 3)
            if metadata.get("exit_code") not in (0, None):
                summary["failed_commands_count"] += 1
        elif event_type == "evidence_bundle_created":
            summary["evidence_bundle_path"] = event.get("file_path") or metadata.get("path")
            _merge_file_metrics(summary, metadata.get("file_change_metrics", {}))
        elif event_type == "qa_verdict_created":
            summary["qa_verdict"] = metadata.get("verdict")
            summary["risk_level"] = metadata.get("risk_level")
        elif event_type == "blocker_recorded":
            summary["blockers_opened"] += 1
        elif event_type == "research_requested":
            summary["research_requests"] += 1
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
    return sum(1 for event in read_events(project) if event.get("event_type") == "research_requested")


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value
