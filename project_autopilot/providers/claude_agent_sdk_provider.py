from __future__ import annotations

import importlib.util

from config import ProjectConfig
from providers.base import ProviderInfo
from secret_status import env_var_status


def detect(project: ProjectConfig) -> ProviderInfo:
    required = ["ANTHROPIC_API_KEY"]
    key_status = env_var_status("ANTHROPIC_API_KEY", min_length=16)
    missing = [] if key_status["status"] == "PRESENT_VALUE_HIDDEN" else required
    configured = not missing
    sdk_package_detected = importlib.util.find_spec("anthropic") is not None
    return ProviderInfo(
        provider_id="claude_agent_sdk",
        display_name="Claude Agent SDK",
        provider_type="future_formal_agent_provider",
        configured=configured,
        capabilities=[
            "codebase analysis",
            "design review assistance",
            "refactor planning",
            "architecture review",
            "future builder execution",
        ],
        risks=[
            "Token cost if live calls are enabled.",
            "Undesired file edits if automatic execution is enabled.",
            "Runaway loops without retry and budget gates.",
            "Secrets exposure if prompts are unsafe.",
            "Overlapping writes without worktrees.",
        ],
        required_env_vars=required,
        missing_env_vars=missing,
        supported_execution_modes=["dry_run", "controlled_analysis_call_future", "sandboxed_builder_future"],
        current_status="dry_run_only_configured" if configured else "dry_run_only_missing_credentials",
        notes=[
            f"ANTHROPIC_API_KEY status: {key_status['status']}.",
            "Project Autopilot makes no Anthropic API calls in dry-run mode.",
            "Live Claude calls require explicit human approval in a future sprint.",
            "Automatic Claude execution remains disabled.",
        ],
        metadata={
            "env_status": key_status["status"],
            "sdk_package_detected": sdk_package_detected,
            "current_execution_mode": "dry_run_only",
            "automatic_execution_enabled": False,
            "external_calls_enabled": False,
            "requires_explicit_approval_for_live_call": True,
        },
    )
