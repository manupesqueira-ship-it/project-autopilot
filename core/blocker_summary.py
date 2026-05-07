from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config import ProjectConfig


@dataclass(frozen=True)
class BlockerSummary:
    path: Path
    open_count: int
    resolved_count: int
    parked_count: int
    latest_open_title: str | None = None


def summarize_blockers(project: ProjectConfig) -> BlockerSummary:
    path = project.project_control_path / "BLOCKERS.md"
    if not path.exists():
        return BlockerSummary(path=path, open_count=0, resolved_count=0, parked_count=0)

    open_count = 0
    resolved_count = 0
    parked_count = 0
    latest_open_title: str | None = None
    current_title: str | None = None
    in_code_block = False

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if stripped.startswith("### "):
            current_title = stripped[4:].strip()
            continue
        if not current_title or not stripped.lower().startswith("status:"):
            continue
        status = stripped.split(":", 1)[1].strip().lower()
        if status == "open":
            open_count += 1
            latest_open_title = current_title
        elif status == "resolved":
            resolved_count += 1
        elif status == "parked":
            parked_count += 1

    return BlockerSummary(
        path=path,
        open_count=open_count,
        resolved_count=resolved_count,
        parked_count=parked_count,
        latest_open_title=latest_open_title,
    )
