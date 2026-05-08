"""Pydantic schemas for Source Monitor inputs and outputs.

All data flowing through Source Monitor is validated against these schemas.
See DESIGN.md section 4 for full schema documentation.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class SourceCategory(str, Enum):
    """Categories matching projects/<property>/sources.yaml structure."""
    OFICIAL = "oficial"
    NEWSLETTERS = "newsletters"
    COMMUNITY = "community"
    LATAM = "latam"
    CUSTOM = "custom"


class SourceType(str, Enum):
    """How the source is fetched."""
    RSS = "rss"
    INOREADER = "inoreader"
    SCRAPE = "scrape"


class ErrorType(str, Enum):
    """Classification of source fetch errors."""
    CONNECTION = "connection"
    PARSE = "parse"
    RATE_LIMIT = "rate_limit"
    AUTH = "auth"
    UNKNOWN = "unknown"


class SourceConfig(BaseModel):
    """Configuration for a single source, loaded from sources.yaml."""
    name: str
    url: str
    type: SourceType
    category: SourceCategory = SourceCategory.CUSTOM
    weight: float = Field(default=1.0, ge=0.0, le=5.0, description="Multiplier for scoring")
    enabled: bool = True


class SourceItem(BaseModel):
    """A single content item discovered from a source.

    This is the core data unit that flows through the entire pipeline.
    Source Monitor produces these; Signal Scorer consumes and enriches them.
    """
    id: str = Field(description="Deterministic hash of url + published_at")
    title: str
    url: HttpUrl
    source_name: str
    source_category: SourceCategory
    published_at: datetime
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    snippet: str = Field(default="", max_length=500, description="First ~300 chars of content")
    authors: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    language: str = Field(default="en", pattern=r"^(en|es|pt)$")
    preliminary_score: float = Field(default=0.0, ge=0.0, le=100.0)
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    is_duplicate: bool = False
    duplicate_of: str | None = None
    raw_metadata: dict = Field(default_factory=dict)


class SourceError(BaseModel):
    """Record of a source that failed during fetch."""
    source_name: str
    error_type: ErrorType
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RunStats(BaseModel):
    """Aggregate statistics for a single Source Monitor run."""
    sources_checked: int = 0
    sources_failed: int = 0
    items_found: int = 0
    items_after_dedup: int = 0
    dedup_removed: int = 0
    avg_preliminary_score: float = 0.0


class SourceMonitorResult(BaseModel):
    """Complete output of a Source Monitor run.

    Serialized to evidence/{run_id}/source_monitor_output.json
    """
    run_id: str
    property: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    items: list[SourceItem] = Field(default_factory=list)
    errors: list[SourceError] = Field(default_factory=list)
    stats: RunStats = Field(default_factory=RunStats)
