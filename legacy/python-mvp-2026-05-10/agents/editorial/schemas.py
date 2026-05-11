"""Pydantic schemas for Editorial agent inputs and outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class BriefStatus(str, Enum):
    DRAFT = "draft"
    FACT_CHECK_PENDING = "fact-check-pending"
    APPROVED = "approved"
    PUBLISHED = "published"


class FormatRecommendation(str, Enum):
    REEL = "reel"
    CAROUSEL = "carrusel"
    STATIC_POST = "post estático"
    NEWSLETTER_ONLY = "solo newsletter"


class CTAType(str, Enum):
    SAVE = "save"
    SHARE = "share"
    COMMENT = "comment"
    NEWSLETTER = "newsletter signup"


class FactCheckItem(BaseModel):
    """A single claim to be verified."""
    claim: str
    status: str = Field(default="pending", description="pending | verified | unverified | disputed")
    notes: str = ""


class EditorialBrief(BaseModel):
    """Complete editorial brief — output of the Editorial agent.

    Follows MASTER_PLAN Anexo A + brief_template.md structure.
    This is the internal planning document, NOT the published content.
    """
    # Metadata
    slug: str = Field(description="YYYY-MM-DD_short-slug")
    date: str
    property: str
    status: BriefStatus = BriefStatus.DRAFT
    source_item_id: str
    signal_score: float

    # Core content (Smart Brevity structure)
    title: str = Field(description="Working title for the brief")
    que_paso: str = Field(description="3-5 factual sentences about what happened")
    por_que_importa: str = Field(description="2-4 sentences on why it matters — the sacred ingredient")
    que_cambia: str = Field(description="Before vs after, 2-4 sentences")
    quien_gana_pierde: dict[str, list[str]] = Field(
        default_factory=lambda: {"gana": [], "pierde": [], "neutro": []},
        description="Who wins, loses, neutral"
    )
    datos_clave: list[str] = Field(default_factory=list, description="3-5 key data points")

    # Editorial angle
    angulo_latam: str = Field(default="", description="LATAM-specific angle")
    angulos_posibles: list[str] = Field(default_factory=list, description="3 possible angles")
    angulo_elegido: str = Field(default="", description="Chosen angle + reason")

    # Format & hooks
    formato_recomendado: FormatRecommendation = FormatRecommendation.CAROUSEL
    hook_tentativo: str = Field(default="", description="First 3 seconds / slide 1 text")
    cta_tentativo: CTAType = CTAType.SAVE

    # Sources & verification
    fuentes: list[str] = Field(default_factory=list, description="Source URLs")
    fact_check_items: list[FactCheckItem] = Field(default_factory=list)

    # Risk
    riesgos: list[str] = Field(default_factory=list)


class EditorialStats(BaseModel):
    """Aggregate stats for an Editorial run."""
    items_processed: int = 0
    briefs_generated: int = 0
    api_calls_made: int = 0
    api_calls_failed: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0


class EditorialResult(BaseModel):
    """Complete output of an Editorial agent run."""
    run_id: str
    score_run_id: str
    property: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    briefs: list[EditorialBrief] = Field(default_factory=list)
    stats: EditorialStats = Field(default_factory=EditorialStats)
    errors: list[str] = Field(default_factory=list)
