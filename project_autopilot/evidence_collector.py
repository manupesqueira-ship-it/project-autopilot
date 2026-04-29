from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from config import ProjectConfig
from run_history import append_event

FORBIDDEN_PATTERNS = [
    r"\brm\b",
    r"\bdel\b",
    r"\brmdir\b",
    r"Remove-Item",
    r"git\s+reset",
    r"git\s+clean",
    r"git\s+push",
    r"git\s+checkout\s+--",
    r"deploy",
    r"vercel\s+--prod",
]

SENSITIVE_NAMES = {".env", ".env.local"}


def assert_safe_command(command: str) -> None:
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, command, flags=re.IGNORECASE):
            raise ValueError(f"Refusing unsafe command: {command}")


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = "NUL"
    return env


def _run_args(
    args: list[str],
    cwd: Path,
    project: ProjectConfig | None = None,
    run_id: str | None = None,
    label: str | None = None,
) -> dict[str, Any]:
    started = perf_counter()
    if project and run_id:
        append_event(project, run_id, "command_started", {"label": label or args[0], "command": " ".join(args)})
    proc = subprocess.run(
        args,
        cwd=cwd,
        env=_git_env(),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=120,
    )
    duration = round(perf_counter() - started, 3)
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    if project and run_id:
        append_event(
            project,
            run_id,
            "command_finished",
            {
                "label": label or args[0],
                "command": " ".join(args),
                "duration_seconds": duration,
                "exit_code": proc.returncode,
            },
        )
    return {"exit_code": proc.returncode, "output": (stdout + stderr).strip(), "duration_seconds": duration}


def run_command(
    command: str,
    cwd: Path,
    project: ProjectConfig | None = None,
    run_id: str | None = None,
    label: str | None = None,
) -> dict[str, Any]:
    assert_safe_command(command)
    started = perf_counter()
    if project and run_id:
        append_event(project, run_id, "command_started", {"label": label or command, "command": command})
    proc = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=240,
    )
    duration = round(perf_counter() - started, 3)
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    if project and run_id:
        append_event(
            project,
            run_id,
            "command_finished",
            {
                "label": label or command,
                "command": command,
                "duration_seconds": duration,
                "exit_code": proc.returncode,
            },
        )
    return {"exit_code": proc.returncode, "output": (stdout + stderr).strip(), "duration_seconds": duration}


def package_has_script(project: ProjectConfig, script_name: str) -> bool:
    package_path = project.repo_path / "package.json"
    if not package_path.exists():
        return False
    package = json.loads(package_path.read_text(encoding="utf-8"))
    return script_name in package.get("scripts", {})


def _status_paths(status_output: str) -> list[str]:
    names: list[str] = []
    for line in status_output.splitlines():
        if not line or line.startswith("##") or len(line) < 4:
            continue
        candidate = line[3:].strip()
        if " -> " in candidate:
            candidate = candidate.split(" -> ", 1)[1].strip()
        if candidate and Path(candidate.rstrip("/")).name not in SENSITIVE_NAMES:
            names.append(candidate)
    return names


def calculate_git_metrics(project: ProjectConfig) -> dict[str, int]:
    status = _run_args(["git", "status", "--porcelain"], project.repo_path)
    metrics = {
        "files_created": 0,
        "files_modified": 0,
        "files_deleted": 0,
        "lines_added": 0,
        "lines_removed": 0,
    }
    for line in status["output"].splitlines():
        if not line or len(line) < 3:
            continue
        code = line[:2]
        path = line[3:].strip()
        if Path(path.rstrip("/")).name in SENSITIVE_NAMES:
            continue
        if code == "??" or "A" in code:
            metrics["files_created"] += 1
        elif "D" in code:
            metrics["files_deleted"] += 1
        elif "M" in code or "R" in code or "C" in code:
            metrics["files_modified"] += 1

    numstat = _run_args(["git", "diff", "--numstat", "--", ".", ":(exclude).env", ":(exclude).env.local"], project.repo_path)
    for line in numstat["output"].splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        added, removed = parts[0], parts[1]
        if added.isdigit():
            metrics["lines_added"] += int(added)
        if removed.isdigit():
            metrics["lines_removed"] += int(removed)
    return metrics


def collect_evidence(project: ProjectConfig, dry_run: bool = False, run_id: str | None = None) -> dict[str, Any]:
    started_at = datetime.now(timezone.utc)
    command_results: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "framework": project.framework,
        "package_manager": project.package_manager,
        "run_id": run_id,
        "started_at": started_at.isoformat(),
        "commands": {},
    }

    status = _run_args(["git", "status", "--short", "--branch"], project.repo_path, project, run_id, "git_status")
    command_results.append(status)
    evidence["git_status"] = status["output"]

    diff = _run_args(["git", "diff", "--", ".", ":(exclude).env", ":(exclude).env.local"], project.repo_path, project, run_id, "git_diff")
    command_results.append(diff)
    evidence["git_diff"] = diff["output"]

    diff_stat = _run_args(["git", "diff", "--stat", "--", ".", ":(exclude).env", ":(exclude).env.local"], project.repo_path, project, run_id, "git_diff_stat")
    command_results.append(diff_stat)
    evidence["git_diff_stat"] = diff_stat["output"]

    changed = _run_args(["git", "diff", "--name-only", "--", ".", ":(exclude).env", ":(exclude).env.local"], project.repo_path, project, run_id, "git_changed_files")
    command_results.append(changed)
    names = [line for line in changed["output"].splitlines() if line and Path(line).name not in SENSITIVE_NAMES]
    evidence["changed_files"] = sorted(dict.fromkeys(names + _status_paths(status["output"])))
    evidence["file_change_metrics"] = calculate_git_metrics(project)

    if dry_run:
        evidence["commands"]["dry_run"] = {
            "exit_code": 0,
            "output": "Dry run: validation commands were not executed.",
            "duration_seconds": 0,
        }
        finished_at = datetime.now(timezone.utc)
        evidence["finished_at"] = finished_at.isoformat()
        evidence["duration_seconds"] = round((finished_at - started_at).total_seconds(), 3)
        evidence["command_count"] = len(command_results)
        evidence["failed_command_count"] = len([result for result in command_results if result.get("exit_code") not in (0, None)])
        return evidence

    if project.build_command:
        evidence["commands"]["build"] = run_command(project.build_command, project.repo_path, project, run_id, "build")
        command_results.append(evidence["commands"]["build"])
    if project.typecheck_command:
        evidence["commands"]["typecheck"] = run_command(project.typecheck_command, project.repo_path, project, run_id, "typecheck")
        command_results.append(evidence["commands"]["typecheck"])
    if project.lint_command:
        evidence["commands"]["lint"] = run_command(project.lint_command, project.repo_path, project, run_id, "lint")
        command_results.append(evidence["commands"]["lint"])
    if project.test_command and package_has_script(project, "test"):
        evidence["commands"]["test"] = run_command(project.test_command, project.repo_path, project, run_id, "test")
        command_results.append(evidence["commands"]["test"])
    elif project.test_command:
        evidence["commands"]["test"] = {"exit_code": 0, "output": "No package.json test script found; skipped.", "duration_seconds": 0}

    if project.route_walk_urls:
        evidence["route_walk_urls"] = project.route_walk_urls

    # Include latest browser QA report if available
    browser_qa_path = project.repo_path / project.logs_dir / f"{project.project_id}_browser_qa_latest.md"
    if browser_qa_path.exists():
        evidence["browser_qa_report"] = str(browser_qa_path.relative_to(project.repo_path))
    else:
        evidence["browser_qa_report"] = None

    finished_at = datetime.now(timezone.utc)
    evidence["finished_at"] = finished_at.isoformat()
    evidence["duration_seconds"] = round((finished_at - started_at).total_seconds(), 3)
    evidence["command_count"] = len(command_results)
    evidence["failed_command_count"] = len([result for result in command_results if result.get("exit_code") not in (0, None)])
    return evidence

