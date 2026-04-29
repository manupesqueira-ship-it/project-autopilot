from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from config import ProjectConfig


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _human_time() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _template_path(project: ProjectConfig) -> Path:
    return project.repo_path / "project_autopilot" / "templates" / "PRODUCT_VALIDATION_REPORT.template.md"


def create_validation_report(project: ProjectConfig) -> tuple[Path, Path]:
    logs_dir = project.repo_path / project.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    latest_path = logs_dir / f"{project.project_id}_validation_report_latest.md"
    run_path = logs_dir / f"{project.project_id}_validation_report_{_stamp()}.md"
    template_path = _template_path(project)
    if template_path.exists():
        content = template_path.read_text(encoding="utf-8")
    else:
        content = "# Product Validation Report\n\n"
    content = content.replace("{{PROJECT_NAME}}", project.project_name)
    content = content.replace("{{PROJECT_ID}}", project.project_id)
    content = content.replace("{{TIMESTAMP_UTC}}", _human_time())
    content = content.replace("{{DEV_SERVER_URL}}", project.route_walk_urls[0] if project.route_walk_urls else "")
    latest_path.write_text(content, encoding="utf-8")
    run_path.write_text(content, encoding="utf-8")
    return latest_path, run_path
