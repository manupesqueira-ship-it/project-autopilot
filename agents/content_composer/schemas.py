"""Pydantic schemas for Content Composer agent."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class CarouselSlide(BaseModel):
    """A single slide in an Instagram carousel."""
    slide_number: int
    headline: str = Field(description="Bold text, 1-2 lines max")
    body: str = Field(default="", description="Supporting text, 2-3 lines max")
    visual_direction: str = Field(default="", description="What image/graphic to use")


class InstagramCaption(BaseModel):
    """Instagram caption following brand_voice.md rules."""
    hook: str = Field(default="", description="First 125 chars — must grab attention")
    body: str = Field(default="", description="1-2 supporting sentences")
    cta: str = Field(default="", description="Call to action")
    hashtags: list[str] = Field(default_factory=list, description="5-10 niche hashtags")
    full_text: str = Field(default="", description="Complete assembled caption")


class CarouselContent(BaseModel):
    """Complete Instagram carousel post."""
    slides: list[CarouselSlide] = Field(default_factory=list)
    caption: InstagramCaption = Field(default_factory=InstagramCaption)
    slide_count: int = 0


class NewsletterSection(BaseModel):
    """Newsletter section following Smart Brevity template (250-400 words)."""
    headline: str = Field(default="", description="Punchy headline in caps")
    intro: str = Field(default="", description="1-2 sentences of contextual setup")
    por_que_importa: str = Field(default="", description="Why it matters — the sacred ingredient")
    lo_que_paso: list[str] = Field(default_factory=list, description="Key points with → arrows")
    que_significa_latam: str = Field(default="", description="LATAM-specific angle with actionable advice")
    bottom_line: str = Field(default="", description="1-2 sentence actionable conclusion")
    fuentes: list[str] = Field(default_factory=list)
    full_text: str = Field(default="", description="Complete assembled section")


class ReelScript(BaseModel):
    """Video script for Instagram Reel (25-35 seconds)."""
    hook: str = Field(description="0-3s: pattern interrupt")
    body: str = Field(description="3-22s: key facts with jump cuts")
    por_que_importa: str = Field(description="Core axiom")
    close: str = Field(description="22-30s: LATAM angle + CTA")
    cta: str = Field(description="Specific CTA text")
    estimated_duration_seconds: int = 30
    on_screen_text: list[str] = Field(default_factory=list, description="Text overlays for muted viewing")


class ComposedContent(BaseModel):
    """All content pieces generated from one editorial brief."""
    brief_slug: str
    brief_title: str
    carousel: CarouselContent = Field(default_factory=CarouselContent)
    newsletter: NewsletterSection = Field(default_factory=NewsletterSection)
    reel_script: ReelScript | None = None


class ComposerStats(BaseModel):
    items_processed: int = 0
    carousels_generated: int = 0
    newsletters_generated: int = 0
    reel_scripts_generated: int = 0
    api_calls_made: int = 0
    api_calls_failed: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0


class ComposerOutput(BaseModel):
    """Complete output of a Content Composer run."""
    run_id: str
    editorial_run_id: str
    property: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content: list[ComposedContent] = Field(default_factory=list)
    stats: ComposerStats = Field(default_factory=ComposerStats)
    errors: list[str] = Field(default_factory=list)
