from __future__ import annotations

from config import ProjectConfig
from providers.base import ProviderInfo
from providers import claude_agent_sdk_provider, claude_code_provider, codex_provider, openai_auditor_provider


def discover_providers(project: ProjectConfig) -> list[ProviderInfo]:
    return [
        codex_provider.detect(project),
        openai_auditor_provider.detect(project),
        claude_code_provider.detect(project),
        claude_agent_sdk_provider.detect(project),
    ]
