from __future__ import annotations

from pathlib import Path

from config import ProjectConfig, load_project_config

CONTROL_FILE_ORDER = [
    "MASTER_PLAN.md",
    "CURRENT_STATE.md",
    "TASK_QUEUE.md",
    "QUALITY_BAR.md",
    "DESIGN_REFERENCES.md",
    "TECHNICAL_ARCHITECTURE.md",
    "COST_POLICY.md",
    "DECISIONS.md",
    "BLOCKERS.md",
    "HUMAN_QUESTIONS.md",
    "AGENT_RULES.md",
    "AUTONOMY_PROTOCOL.md",
]


def load_project(project_id: str) -> ProjectConfig:
    return load_project_config(project_id)


def read_project_control(project: ProjectConfig) -> dict[str, str]:
    docs: dict[str, str] = {}
    for name in CONTROL_FILE_ORDER:
        path = project.project_control_path / name
        docs[name] = path.read_text(encoding="utf-8") if path.exists() else ""
    return docs


def ensure_project_dirs(project: ProjectConfig) -> None:
    (project.repo_path / project.logs_dir).mkdir(parents=True, exist_ok=True)
    (project.repo_path / project.screenshots_dir).mkdir(parents=True, exist_ok=True)
    project.project_control_path.mkdir(parents=True, exist_ok=True)


def relative_to_repo(project: ProjectConfig, path: Path) -> str:
    try:
        return str(path.relative_to(project.repo_path))
    except ValueError:
        return str(path)

