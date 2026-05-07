from __future__ import annotations

import shutil

from config import ProjectConfig
from providers.base import ProviderInfo


def detect(project: ProjectConfig) -> ProviderInfo:
    command = project.claude_command or "claude"
    cli_path = shutil.which(command)
    cli_detected = cli_path is not None
    configured = project.builder_primary in {"claude", "claude_code"} or project.builder_fallback in {"claude", "claude_code"}
    status = "manual_handoff_ready" if configured else "available_if_selected"
    if not cli_detected:
        status = "manual_handoff_only_cli_not_detected"

    return ProviderInfo(
        provider_id="claude_code",
        display_name="Claude Code",
        provider_type="local_cli_or_manual_builder",
        configured=configured or cli_detected,
        capabilities=[
            "manual_prompt_handoff",
            "future_cli_non_interactive",
            "large_implementation_tasks",
            "post_builder_report_required",
        ],
        risks=[
            "Automatic execution is disabled.",
            "CLI output must be reviewed through Project Autopilot post-builder intake.",
            "Worktrees are required for parallel writes.",
        ],
        required_env_vars=[],
        missing_env_vars=[],
        supported_execution_modes=["manual_handoff", "future_cli_non_interactive"],
        current_status=status,
        notes=[
            f"Configured command name: {command}",
            "CLI detection is metadata-only and does not execute Claude.",
            "Automatic Claude execution remains disabled.",
        ],
        metadata={"cli_detected": cli_detected},
    )
