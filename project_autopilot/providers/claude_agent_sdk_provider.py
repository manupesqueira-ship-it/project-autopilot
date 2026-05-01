from __future__ import annotations

import os

from config import ProjectConfig
from providers.base import ProviderInfo


def detect(project: ProjectConfig) -> ProviderInfo:
    required = ["ANTHROPIC_API_KEY"]
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    configured = not missing
    return ProviderInfo(
        provider_id="claude_agent_sdk",
        display_name="Claude Agent SDK",
        provider_type="future_api_agent_provider",
        configured=configured,
        capabilities=[
            "future_structured_agent_sessions",
            "future_tool_orchestration",
            "future_cloud_or_local_agent_runtime",
        ],
        risks=[
            "Would require API credentials and budget controls before use.",
            "No API calls are allowed in this sprint.",
            "Automatic execution is not enabled.",
        ],
        required_env_vars=required,
        missing_env_vars=missing,
        supported_execution_modes=["future_api_managed"],
        current_status="future_config_present_not_enabled" if configured else "future_not_configured",
        notes=[
            "Claude Agent SDK is a future formal provider.",
            "ANTHROPIC_API_KEY presence is checked without printing values.",
            "Project Autopilot makes no Anthropic API calls here.",
        ],
    )
