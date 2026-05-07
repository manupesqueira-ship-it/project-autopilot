from __future__ import annotations

from typing import Any

from blocker_summary import summarize_blockers
from config import ProjectConfig, load_project_config
from research_log import summarize_research
from run_history import read_events, summarize_events, summarize_recent_runs
from task_state import load_task_state


def latest_run_metrics(project: ProjectConfig) -> dict[str, Any] | None:
    recent = summarize_recent_runs(project.project_id, limit=1)
    if not recent:
        return None
    return enrich_run_metrics(project, recent[0])


def recent_run_metrics(project_id: str, limit: int = 5) -> list[dict[str, Any]]:
    project = load_project_config(project_id)
    return [enrich_run_metrics(project, run) for run in summarize_recent_runs(project_id, limit=limit)]


def enrich_run_metrics(project: ProjectConfig, run: dict[str, Any]) -> dict[str, Any]:
    blockers = summarize_blockers(project)
    research = summarize_research(project)
    task_state = load_task_state(project)
    return {
        "run_id": run.get("run_id"),
        "active_duration_seconds": run.get("active_duration_seconds", 0),
        "total_duration_seconds": run.get("duration_seconds"),
        "commands_executed": run.get("commands_count", 0),
        "commands_failed": run.get("failed_commands_count", 0),
        "files_created": run.get("files_created", 0),
        "files_modified": run.get("files_modified", 0),
        "files_deleted": run.get("files_deleted", 0),
        "lines_added": run.get("lines_added", 0),
        "lines_removed": run.get("lines_removed", 0),
        "evidence_bundle_path": run.get("evidence_bundle_path"),
        "qa_verdict": run.get("qa_verdict"),
        "risk_level": run.get("risk_level"),
        "blockers_opened": run.get("blockers_opened", 0),
        "open_blockers": blockers.open_count,
        "research_requests": research["count"],
        "cost_estimate_usd": run.get("estimated_model_cost"),
        "task_state": task_state.get("state", "unknown"),
        "outcome": run.get("outcome") or run.get("status"),
    }


def summarize_latest_run_from_events(project: ProjectConfig) -> dict[str, Any] | None:
    summaries = summarize_events(read_events(project), project.project_id, limit=1)
    if not summaries:
        return None
    return enrich_run_metrics(project, summaries[0])
