from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from config import ProjectConfig

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


def _run_args(args: list[str], cwd: Path) -> dict[str, Any]:
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
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    return {"exit_code": proc.returncode, "output": (stdout + stderr).strip()}


def run_command(command: str, cwd: Path) -> dict[str, Any]:
    assert_safe_command(command)
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
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    return {"exit_code": proc.returncode, "output": (stdout + stderr).strip()}


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


def collect_evidence(project: ProjectConfig, dry_run: bool = False) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "framework": project.framework,
        "package_manager": project.package_manager,
        "commands": {},
    }

    status = _run_args(["git", "status", "--short", "--branch"], project.repo_path)
    evidence["git_status"] = status["output"]

    diff = _run_args(["git", "diff", "--", ".", ":(exclude).env", ":(exclude).env.local"], project.repo_path)
    evidence["git_diff"] = diff["output"]

    changed = _run_args(["git", "diff", "--name-only", "--", ".", ":(exclude).env", ":(exclude).env.local"], project.repo_path)
    names = [line for line in changed["output"].splitlines() if line and Path(line).name not in SENSITIVE_NAMES]
    evidence["changed_files"] = sorted(dict.fromkeys(names + _status_paths(status["output"])))

    if dry_run:
        evidence["commands"]["dry_run"] = {
            "exit_code": 0,
            "output": "Dry run: validation commands were not executed.",
        }
        return evidence

    if project.build_command:
        evidence["commands"]["build"] = run_command(project.build_command, project.repo_path)
    if project.typecheck_command:
        evidence["commands"]["typecheck"] = run_command(project.typecheck_command, project.repo_path)
    if project.lint_command:
        evidence["commands"]["lint"] = run_command(project.lint_command, project.repo_path)
    if project.test_command and package_has_script(project, "test"):
        evidence["commands"]["test"] = run_command(project.test_command, project.repo_path)
    elif project.test_command:
        evidence["commands"]["test"] = {"exit_code": 0, "output": "No package.json test script found; skipped."}

    if project.route_walk_urls:
        evidence["route_walk_urls"] = project.route_walk_urls
        evidence["screenshots"] = "Route walk/screenshot capture is configured for a future browser-enabled cycle."

    return evidence

