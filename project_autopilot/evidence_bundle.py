from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import ProjectConfig
from run_history import append_event


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text or "", encoding="utf-8")


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def create_evidence_bundle(
    project: ProjectConfig,
    evidence: dict[str, Any],
    task_plan: str | None = None,
    builder_prompt: str | None = None,
    qa_review: str | None = None,
    risk_summary: dict[str, Any] | None = None,
    cost_snapshot: dict[str, Any] | None = None,
    task_state: dict[str, Any] | None = None,
) -> Path:
    """Create a structured, secret-safe evidence bundle for one run."""
    bundle_dir = project.repo_path / project.logs_dir / "evidence" / project.project_id / _stamp()
    bundle_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "run_id": evidence.get("run_id"),
        "project_id": project.project_id,
        "project_name": project.project_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "started_at": evidence.get("started_at"),
        "finished_at": evidence.get("finished_at"),
        "duration_seconds": evidence.get("duration_seconds"),
        "framework": project.framework,
        "package_manager": project.package_manager,
        "autonomy_mode": project.autonomy_mode,
        "intensity_mode": project.intensity_mode,
        "changed_file_count": len(evidence.get("changed_files", [])),
        "command_count": evidence.get("command_count", len(evidence.get("commands", {}))),
        "failed_command_count": evidence.get(
            "failed_command_count",
            len([result for result in evidence.get("commands", {}).values() if result.get("exit_code") not in (0, None)]),
        ),
        "file_change_metrics": evidence.get("file_change_metrics", {}),
        "browser_qa_report": evidence.get("browser_qa_report"),
        "backend_audit_report": evidence.get("backend_audit_report"),
        "risk_summary": risk_summary,
        "cost_snapshot": cost_snapshot,
        "task_state": task_state,
    }
    (bundle_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")

    if task_plan is not None:
        _write_text(bundle_dir / "task_plan.md", task_plan)
    if builder_prompt is not None:
        _write_text(bundle_dir / "builder_prompt.md", builder_prompt)
    if qa_review is not None:
        _write_text(bundle_dir / "qa_verdict.md", qa_review)

    _write_text(bundle_dir / "git_status.txt", evidence.get("git_status", ""))
    _write_text(bundle_dir / "changed_files.txt", "\n".join(evidence.get("changed_files", [])))
    _write_text(bundle_dir / "git_diff_stat.txt", evidence.get("git_diff_stat", ""))
    (bundle_dir / "command_results.json").write_text(
        json.dumps(_json_safe(evidence.get("commands", {})), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    blockers_path = project.project_control_path / "BLOCKERS.md"
    questions_path = project.project_control_path / "HUMAN_QUESTIONS.md"
    _write_text(bundle_dir / "blockers_snapshot.md", blockers_path.read_text(encoding="utf-8") if blockers_path.exists() else "")
    _write_text(bundle_dir / "human_questions_snapshot.md", questions_path.read_text(encoding="utf-8") if questions_path.exists() else "")

    run_id = evidence.get("run_id")
    if run_id:
        append_event(
            project,
            run_id,
            "evidence_bundle_created",
            {
                "path": str(bundle_dir.relative_to(project.repo_path)),
                "command_count": metadata["command_count"],
                "failed_command_count": metadata["failed_command_count"],
                "file_change_metrics": metadata["file_change_metrics"],
            },
        )

    return bundle_dir
