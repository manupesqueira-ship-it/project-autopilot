from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProviderInfo:
    provider_id: str
    display_name: str
    provider_type: str
    configured: bool
    capabilities: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    required_env_vars: list[str] = field(default_factory=list)
    missing_env_vars: list[str] = field(default_factory=list)
    supported_execution_modes: list[str] = field(default_factory=list)
    current_status: str = "unknown"
    notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
