"""Pydantic schemas for Analytics agent."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class PipelineRunSummary(BaseModel):
    """Summary of a single pipeline run (scan → publish)."""
    date: str
    source_items_found: int = 0
    items_scored: int = 0
    items_strong: int = 0
    briefs_generated: int = 0
    content_composed: int = 0
    compliance_approved: int = 0
    compliance_blocked: int = 0
    items_published: int = 0
    total_api_tokens: int = 0
    total_api_cost_estimate: float = 0.0


class ContentPerformance(BaseModel):
    """Performance metrics for a published piece (filled manually for now)."""
    brief_slug: str
    brief_title: str
    channel: str
    published_at: str = ""
    # Instagram metrics
    reach_24h: int = 0
    likes_24h: int = 0
    comments_24h: int = 0
    saves_24h: int = 0
    shares_24h: int = 0
    followers_gained_24h: int = 0
    # Newsletter metrics
    newsletter_sends: int = 0
    newsletter_opens: int = 0
    newsletter_clicks: int = 0
    newsletter_signups: int = 0


class WeeklyReport(BaseModel):
    """Weekly analytics summary."""
    week_start: str
    week_end: str
    property: str

    # Pipeline stats
    total_scans: int = 0
    total_items_discovered: int = 0
    total_briefs_generated: int = 0
    total_pieces_published: int = 0

    # Cost
    total_api_tokens: int = 0
    total_api_cost_estimate: float = 0.0

    # Performance (aggregated)
    total_reach: int = 0
    total_engagement: int = 0
    avg_engagement_rate: float = 0.0
    followers_gained: int = 0
    newsletter_signups: int = 0

    # Top performers
    top_pieces: list[ContentPerformance] = Field(default_factory=list)

    # Recommendations
    recommendations: list[str] = Field(default_factory=list)


class AnalyticsOutput(BaseModel):
    """Complete output of an Analytics run."""
    run_id: str
    property: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pipeline_runs: list[PipelineRunSummary] = Field(default_factory=list)
    weekly_report: WeeklyReport | None = None
    errors: list[str] = Field(default_factory=list)
