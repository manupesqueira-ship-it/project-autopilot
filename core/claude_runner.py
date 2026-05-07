"""Claude Code runner for Project Autopilot.

Handles the handoff between Project Autopilot (planning/QA) and Claude Code
(heavy implementation).  Two modes:

- **manual**: Prints the prompt path and instructions.  The human pastes the
  prompt into Claude Code.  This is the default and the safest option.

- **execute**: Invokes the Claude CLI directly.  Disabled by default.
  Requires ``allow_automatic_builder_execution: true`` in the project config.
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from config import ProjectConfig


@dataclass
class HandoffResult:
    mode: str          # "manual" | "execute" | "blocked"
    prompt_path: Path
    claude_available: bool
    executed: bool
    message: str


def detect_claude_cli(project: ProjectConfig) -> tuple[bool, str]:
    """Check whether the Claude CLI binary is on PATH."""
    cmd = project.claude_command or "claude"
    resolved = shutil.which(cmd)
    if resolved:
        return True, resolved
    return False, ""


def resolve_prompt_path(project: ProjectConfig) -> Path:
    """Return the absolute path to the latest builder prompt."""
    if project.latest_prompt_path:
        candidate = project.repo_path / project.latest_prompt_path
        if candidate.exists():
            return candidate
    # Fallback: standard naming convention
    return project.repo_path / project.logs_dir / f"{project.project_id}_latest_builder_prompt.md"


def handoff_manual(project: ProjectConfig) -> HandoffResult:
    """Manual mode: print the prompt path for the human to paste into Claude."""
    prompt_path = resolve_prompt_path(project)
    claude_ok, claude_path = detect_claude_cli(project)

    if not prompt_path.exists():
        return HandoffResult(
            mode="manual",
            prompt_path=prompt_path,
            claude_available=claude_ok,
            executed=False,
            message=f"No builder prompt found at {prompt_path}.\nRun --local-plan or --cycle first to generate one.",
        )

    lines = [
        f"Builder prompt ready: {prompt_path}",
        "",
        "To hand off to Claude Code:",
        f"  1. Open Claude Code in the project directory: {project.repo_path}",
        f"  2. Paste the contents of: {prompt_path}",
        "  3. Review Claude's output before approving any changes.",
    ]

    if claude_ok:
        lines.append("")
        lines.append(f"Claude CLI detected at: {claude_path}")
        lines.append(f"You can also run:  {project.claude_command} < {prompt_path}")
    else:
        lines.append("")
        lines.append(f"Claude CLI ('{project.claude_command}') not found on PATH.")
        lines.append("Install: https://docs.anthropic.com/en/docs/claude-code")

    return HandoffResult(
        mode="manual",
        prompt_path=prompt_path,
        claude_available=claude_ok,
        executed=False,
        message="\n".join(lines),
    )


def handoff_execute(project: ProjectConfig) -> HandoffResult:
    """Execute mode: invoke Claude CLI with the builder prompt.

    Blocked by default unless the project config explicitly allows it.
    """
    prompt_path = resolve_prompt_path(project)
    claude_ok, claude_path = detect_claude_cli(project)

    if not project.allow_automatic_builder_execution:
        return HandoffResult(
            mode="blocked",
            prompt_path=prompt_path,
            claude_available=claude_ok,
            executed=False,
            message=(
                "Automatic Claude execution is disabled by Project Autopilot config.\n"
                f"Set 'allow_automatic_builder_execution: true' in the project YAML to enable.\n"
                f"Current config: {project.builder_handoff_mode} mode, execution={'allowed' if project.allow_automatic_builder_execution else 'blocked'}."
            ),
        )

    if not prompt_path.exists():
        return HandoffResult(
            mode="execute",
            prompt_path=prompt_path,
            claude_available=claude_ok,
            executed=False,
            message=f"No builder prompt found at {prompt_path}.\nRun --local-plan or --cycle first.",
        )

    if not claude_ok:
        return HandoffResult(
            mode="execute",
            prompt_path=prompt_path,
            claude_available=False,
            executed=False,
            message=f"Claude CLI ('{project.claude_command}') not found on PATH. Cannot execute automatically.",
        )

    # Execute Claude CLI with the prompt piped to stdin
    prompt_text = prompt_path.read_text(encoding="utf-8")
    cmd = project.claude_command or "claude"
    try:
        result = subprocess.run(
            [cmd, "--print"],
            input=prompt_text,
            cwd=project.repo_path,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=600,
        )
        return HandoffResult(
            mode="execute",
            prompt_path=prompt_path,
            claude_available=True,
            executed=True,
            message=f"Claude Code finished (exit {result.returncode}).\nOutput length: {len(result.stdout)} chars.",
        )
    except subprocess.TimeoutExpired:
        return HandoffResult(
            mode="execute",
            prompt_path=prompt_path,
            claude_available=True,
            executed=False,
            message="Claude Code timed out after 600 seconds.",
        )
    except Exception as exc:
        return HandoffResult(
            mode="execute",
            prompt_path=prompt_path,
            claude_available=True,
            executed=False,
            message=f"Claude Code invocation failed: {exc}",
        )
