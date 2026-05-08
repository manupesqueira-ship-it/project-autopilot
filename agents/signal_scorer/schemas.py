"""Pydantic schemas for Signal Scorer inputs and outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class Classification(str, Enum):
    """Item classification based on signal score thresholds."""
    STRONG = "strong"       # >70: candidate for content production
    CONSIDER = "consider"   # 50-70: review manually
    DISCARD = "discard"     # <50: skip


class SignalBreakdown(BaseModel):
    """Per-category scores from the LLM evaluation.

    Matches MASTER_PLAN Anexo B rubric exactly.
    """
    relevancia_latam: float = Field(0.0, ge=0, le=20, description="¿Aplica a audiencia LATAM?")
    novedad: float = Field(0.0, ge=0, le=15, description="¿Es nuevo o ya circuló?")
    urgencia: float = Field(0.0, ge=0, le=10, description="¿Tiene ventana de tiempo?")
    credibilidad_fuente: float = Field(0.0, ge=0, le=15, description="¿Fuente confiable?")
    potencial_educativo: float = Field(0.0, ge=0, le=10, description="¿Enseña algo útil?")
    potencial_viral: float = Field(0.0, ge=0, le=10, description="¿Tiene hook fuerte?")
    fit_marca: float = Field(0.0, ge=0, le=10, description="¿Coincide con voz/posicionamiento?")
    riesgo: float = Field(0.0, ge=-10, le=0, description="Penalty por riesgo legal/reputacional")

    @property
    def total(self) -> float:
        return max(0.0, min(100.0, (
            self.relevancia_latam + self.novedad + self.urgencia +
            self.credibilidad_fuente + self.potencial_educativo +
            self.potencial_viral + self.fit_marca + self.riesgo
        )))


class ScoredItem(BaseModel):
    """A source item enriched with LLM-evaluated signal score."""
    # Source item fields (flattened for simplicity)
    item_id: str
    title: str
    url: str
    source_name: str
    snippet: str
    published_at: datetime
    preliminary_score: float = Field(description="Heuristic score from Source Monitor")

    # Signal Scorer fields
    signal_score: float = Field(0.0, ge=0.0, le=100.0, description="LLM-evaluated score")
    signal_breakdown: SignalBreakdown = Field(default_factory=SignalBreakdown)
    classification: Classification = Classification.DISCARD
    justification: str = Field(default="", description="2-3 sentence explanation in Spanish")
    suggested_angle: str = Field(default="", description="Brief editorial angle suggestion")
    risk_flags: list[str] = Field(default_factory=list)

    @staticmethod
    def classify(score: float) -> Classification:
        if score > 70:
            return Classification.STRONG
        if score >= 50:
            return Classification.CONSIDER
        return Classification.DISCARD


class ScorerStats(BaseModel):
    """Aggregate stats for a Signal Scorer run."""
    items_scored: int = 0
    items_strong: int = 0
    items_consider: int = 0
    items_discard: int = 0
    avg_signal_score: float = 0.0
    api_calls_made: int = 0
    api_calls_failed: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0


class SignalScorerResult(BaseModel):
    """Complete output of a Signal Scorer run."""
    run_id: str
    source_run_id: str = Field(description="Run ID of the Source Monitor run that produced the input")
    property: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    items: list[ScoredItem] = Field(default_factory=list)
    stats: ScorerStats = Field(default_factory=ScorerStats)
    errors: list[str] = Field(default_factory=list)
