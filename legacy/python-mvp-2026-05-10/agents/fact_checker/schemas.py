"""Pydantic schemas for Fact-Checker agent."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    DISPUTED = "disputed"
    PARTIALLY_VERIFIED = "partially_verified"
    UNABLE_TO_VERIFY = "unable_to_verify"


class Severity(str, Enum):
    """How critical is this claim for publication safety."""
    CRITICAL = "critical"      # Must be verified before publishing
    HIGH = "high"              # Should be verified, or add qualifier
    MEDIUM = "medium"          # Verify if possible, not blocking
    LOW = "low"                # Nice to verify, not blocking


class VerifiedClaim(BaseModel):
    """A single claim after verification attempt."""
    claim: str
    status: VerificationStatus
    severity: Severity = Severity.MEDIUM
    source_url: str = Field(default="", description="URL that confirms/denies the claim")
    source_name: str = Field(default="", description="Name of verification source")
    notes: str = Field(default="", description="Explanation of verification result")
    suggested_rewrite: str = Field(default="", description="Safer phrasing if claim is disputed/unverified")
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BriefVerdict(str, Enum):
    """Overall verdict for a brief after fact-checking."""
    PASS = "pass"                     # All critical claims verified, safe to publish
    PASS_WITH_EDITS = "pass_with_edits"  # Minor rewrites needed, then safe
    NEEDS_REVIEW = "needs_review"     # Some claims unverified, human must decide
    FAIL = "fail"                     # Critical claims disputed/unverified, do not publish


class FactCheckResult(BaseModel):
    """Fact-check result for a single editorial brief."""
    brief_slug: str
    brief_title: str
    verdict: BriefVerdict
    claims: list[VerifiedClaim] = Field(default_factory=list)
    summary: str = Field(default="", description="1-3 sentence summary of findings in Spanish")
    recommended_edits: list[str] = Field(default_factory=list, description="Specific text changes")
    critical_issues: list[str] = Field(default_factory=list)


class FactCheckerStats(BaseModel):
    """Aggregate stats for a Fact-Checker run."""
    briefs_checked: int = 0
    claims_total: int = 0
    claims_verified: int = 0
    claims_disputed: int = 0
    claims_unverified: int = 0
    verdicts_pass: int = 0
    verdicts_pass_with_edits: int = 0
    verdicts_needs_review: int = 0
    verdicts_fail: int = 0
    api_calls_made: int = 0
    api_calls_failed: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0


class FactCheckerOutput(BaseModel):
    """Complete output of a Fact-Checker run."""
    run_id: str
    editorial_run_id: str
    property: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    results: list[FactCheckResult] = Field(default_factory=list)
    stats: FactCheckerStats = Field(default_factory=FactCheckerStats)
    errors: list[str] = Field(default_factory=list)
