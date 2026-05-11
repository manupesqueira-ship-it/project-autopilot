"""Pydantic schemas for Publisher agent."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class PublishChannel(str, Enum):
    INSTAGRAM = "instagram"
    NEWSLETTER = "newsletter"
    BOTH = "both"


class PublishStatus(str, Enum):
    READY = "ready"                  # Files exported, ready to copy-paste
    SCHEDULED = "scheduled"          # Scheduled via Buffer/Later (future)
    PUBLISHED = "published"          # Confirmed published
    FAILED = "failed"                # Publishing failed


class PublishableItem(BaseModel):
    """A single content piece ready for publication."""
    brief_slug: str
    brief_title: str
    channel: PublishChannel
    status: PublishStatus = PublishStatus.READY

    # File paths (relative to evidence dir)
    caption_file: str = ""
    slides_file: str = ""
    newsletter_file: str = ""
    reel_file: str = ""

    # Metadata
    approved_at: str = ""
    scheduled_for: str = Field(default="", description="ISO datetime if scheduled")
    published_at: str = ""
    notes: str = ""


class PublisherStats(BaseModel):
    items_processed: int = 0
    items_ready: int = 0
    items_instagram: int = 0
    items_newsletter: int = 0
    files_exported: int = 0


class PublisherOutput(BaseModel):
    """Complete output of a Publisher run."""
    run_id: str
    approval_run_id: str
    property: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    items: list[PublishableItem] = Field(default_factory=list)
    stats: PublisherStats = Field(default_factory=PublisherStats)
    export_dir: str = Field(default="", description="Path to exported files")
    errors: list[str] = Field(default_factory=list)
