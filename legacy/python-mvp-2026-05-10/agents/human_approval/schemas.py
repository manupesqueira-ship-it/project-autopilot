"""Pydantic schemas for Human Approval agent."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class Decision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    EDIT_REQUESTED = "edit_requested"
    DEFERRED = "deferred"


class ContentDecision(BaseModel):
    """Human decision on a single content piece."""
    brief_slug: str
    brief_title: str
    content_type: str = Field(description="carousel_caption | newsletter | reel_script")
    decision: Decision
    notes: str = Field(default="", description="Editor notes")
    edits_made: list[str] = Field(default_factory=list, description="What was changed")
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decided_by: str = Field(default="manuel", description="Who made the decision")


class ApprovalStats(BaseModel):
    items_reviewed: int = 0
    items_approved: int = 0
    items_rejected: int = 0
    items_edit_requested: int = 0
    items_deferred: int = 0


class ApprovalOutput(BaseModel):
    """Complete output of a Human Approval session."""
    run_id: str
    compliance_run_id: str
    property: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decisions: list[ContentDecision] = Field(default_factory=list)
    stats: ApprovalStats = Field(default_factory=ApprovalStats)
