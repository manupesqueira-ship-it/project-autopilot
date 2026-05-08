"""Pydantic schemas for Compliance agent."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class CheckSeverity(str, Enum):
    BLOCK = "block"          # Must fix before publishing
    WARNING = "warning"      # Should fix, not blocking
    INFO = "info"            # FYI, no action needed


class ComplianceVerdict(str, Enum):
    APPROVED = "approved"              # All checks pass
    APPROVED_WITH_WARNINGS = "approved_with_warnings"  # Minor issues, OK to publish
    BLOCKED = "blocked"                # Must fix before publishing


class ComplianceCheck(BaseModel):
    """A single compliance rule evaluation."""
    rule: str = Field(description="Rule name from checklist")
    passed: bool
    severity: CheckSeverity = CheckSeverity.INFO
    detail: str = Field(default="", description="Explanation")
    suggested_fix: str = Field(default="", description="How to fix if failed")


class ContentComplianceResult(BaseModel):
    """Compliance result for one content piece (caption, newsletter, etc.)."""
    content_type: str = Field(description="carousel_caption | newsletter | reel_script")
    brief_slug: str
    brief_title: str
    verdict: ComplianceVerdict
    checks: list[ComplianceCheck] = Field(default_factory=list)
    summary: str = Field(default="", description="1-2 sentence summary in Spanish")
    blocks: list[str] = Field(default_factory=list, description="Blocking issues")
    warnings: list[str] = Field(default_factory=list, description="Non-blocking warnings")


class ComplianceStats(BaseModel):
    items_checked: int = 0
    items_approved: int = 0
    items_approved_with_warnings: int = 0
    items_blocked: int = 0
    total_checks: int = 0
    checks_passed: int = 0
    checks_failed: int = 0
    api_calls_made: int = 0
    api_calls_failed: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0


class ComplianceOutput(BaseModel):
    """Complete output of a Compliance run."""
    run_id: str
    composer_run_id: str
    property: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    results: list[ContentComplianceResult] = Field(default_factory=list)
    stats: ComplianceStats = Field(default_factory=ComplianceStats)
    errors: list[str] = Field(default_factory=list)
