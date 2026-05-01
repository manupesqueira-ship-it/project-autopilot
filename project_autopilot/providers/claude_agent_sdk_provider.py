from __future__ import annotations

import importlib.util
import json

from config import ProjectConfig
from providers.base import ProviderInfo
from secret_status import env_var_status


def _latest_analysis_status(project: ProjectConfig) -> dict[str, object]:
    path = project.repo_path / project.logs_dir / "claude" / project.project_id / "latest" / "claude_analysis_metadata.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"verdict": "NOT_RUN", "live_call_made": False, "path": str(path)}
    return {
        "verdict": payload.get("verdict", "UNKNOWN"),
        "live_call_made": bool(payload.get("live_call_made", False)),
        "anthropic_call_count": payload.get("anthropic_call_count", 0),
        "secrets_sent": bool(payload.get("secrets_sent", False)),
        "path": str(path),
    }


def detect(project: ProjectConfig) -> ProviderInfo:
    required = ["ANTHROPIC_API_KEY"]
    key_status = env_var_status("ANTHROPIC_API_KEY", min_length=16)
    missing = [] if key_status["status"] == "PRESENT_VALUE_HIDDEN" else required
    configured = not missing
    sdk_package_detected = importlib.util.find_spec("anthropic") is not None
    latest_analysis = _latest_analysis_status(project)
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
            "controlled analysis call",
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
        supported_execution_modes=["dry_run", "controlled_analysis_call", "sandboxed_builder_future"],
        current_status="controlled_analysis_ready" if configured else "dry_run_only_missing_credentials",
        notes=[
            f"ANTHROPIC_API_KEY status: {key_status['status']}.",
            "Provider registry never calls Anthropic.",
            "Controlled analysis calls require explicit approval.",
            "Automatic Claude execution remains disabled.",
        ],
        metadata={
            "env_status": key_status["status"],
            "sdk_package_detected": sdk_package_detected,
            "current_execution_mode": "controlled_analysis_only",
            "automatic_execution_enabled": False,
            "external_calls_enabled": "controlled_analysis_only_with_explicit_approval",
            "requires_explicit_approval_for_live_call": True,
            "live_analysis_capability": "controlled_only",
            "builder_execution_capability": "disabled",
            "latest_analysis": latest_analysis,
        },
    )
