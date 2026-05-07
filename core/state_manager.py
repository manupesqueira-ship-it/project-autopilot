from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import ProjectConfig


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def file_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def append_markdown(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n### {utc_stamp()} - {title}\n\n{body.strip()}\n")


def record_blocker(project: ProjectConfig, title: str, body: str) -> None:
    append_markdown(project.project_control_path / "BLOCKERS.md", title, body)


def record_human_question(project: ProjectConfig, title: str, body: str) -> None:
    append_markdown(project.project_control_path / "HUMAN_QUESTIONS.md", title, body)


def _state_path(project: ProjectConfig) -> Path:
    return project.repo_path / project.logs_dir / f"{project.project_id}_autopilot_state.json"


def load_state(project: ProjectConfig) -> dict[str, Any]:
    path = _state_path(project)
    if not path.exists():
        return {"project_id": project.project_id, "cycles": 0, "last_status": "new"}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(project: ProjectConfig, state: dict[str, Any]) -> Path:
    path = _state_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_iteration_log(
    project: ProjectConfig,
    task_plan: str,
    builder_prompt: str,
    qa_review: str,
    correction_prompt: str,
    evidence: dict[str, Any],
    dry_run: bool,
    cycle: bool,
) -> Path:
    logs_dir = project.repo_path / project.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    path = logs_dir / f"{project.project_id}_autopilot_{file_stamp()}.md"
    prompt_path = logs_dir / f"{project.project_id}_latest_builder_prompt.md"
    prompt_path.write_text(builder_prompt, encoding="utf-8")

    changed = "\n".join(f"- {item}" for item in evidence.get("changed_files", [])) or "- None"
    command_sections: list[str] = []
    for name, result in evidence.get("commands", {}).items():
        command_sections.append(
            f"### {name}\n\nExit code: {result.get('exit_code')}\n\n```text\n{result.get('output', '').strip()}\n```"
        )

    content = f"""# Project Autopilot Iteration Log

Timestamp: {utc_stamp()}
Project: {project.project_name} ({project.project_id})
Autonomy mode: {project.autonomy_mode}
Dry run: {dry_run}
Cycle: {cycle}
Primary builder: {project.builder_primary}

## Planned Task

{task_plan.strip()}

## Changed Files

{changed}

## Git Status

```text
{evidence.get('git_status', '').strip()}
```

## Git Diff

```text
{evidence.get('git_diff', '').strip()}
```

## Command Evidence

{chr(10).join(command_sections) if command_sections else 'No commands executed.'}

## Builder Prompt

```text
{builder_prompt.strip()}
```

## QA Review

{qa_review.strip()}

## Correction Prompt

```text
{correction_prompt.strip()}
```
"""
    path.write_text(content, encoding="utf-8")
    return path


def write_failure_log(
    project: ProjectConfig,
    title: str,
    error: dict[str, Any],
    evidence: dict[str, Any],
    recommendation: str,
) -> Path:
    logs_dir = project.repo_path / project.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    path = logs_dir / f"{project.project_id}_autopilot_failure_{file_stamp()}.md"
    changed = "\n".join(f"- {item}" for item in evidence.get("changed_files", [])) or "- None"
    content = f"""# Project Autopilot Failure

Timestamp: {utc_stamp()}
Project: {project.project_name} ({project.project_id})
Title: {title}

## Error

```json
{json.dumps(error, indent=2, sort_keys=True)}
```

## Recommendation

{recommendation.strip()}

## Changed Files

{changed}

## Git Status

```text
{evidence.get('git_status', '').strip()}
```
"""
    path.write_text(content, encoding="utf-8")
    return path
