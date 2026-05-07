from __future__ import annotations

from config import ProjectConfig
from providers.base import ProviderInfo


def detect(project: ProjectConfig) -> ProviderInfo:
    configured = project.builder_primary == "codex" or project.builder_fallback == "codex"
    return ProviderInfo(
        provider_id="codex",
        display_name="Codex",
        provider_type="external_manual_builder",
        configured=configured,
        capabilities=[
            "prompt_handoff",
            "codebase_editing_in_current_environment",
            "local_validation_command_execution",
            "evidence_collection_via_project_autopilot",
        ],
        risks=[
            "Runs outside Project Autopilot process control.",
            "Requires post-builder intake and validation before commit.",
        ],
        required_env_vars=[],
        missing_env_vars=[],
        supported_execution_modes=["manual_handoff", "external_execution"],
        current_status="primary_builder" if project.builder_primary == "codex" else "available_fallback",
        notes=[
            "Codex is the current primary builder for Project Autopilot.",
            "Project Autopilot does not execute Codex directly; it generates prompts and validates results.",
        ],
    )
