"""Fact-Checker agent — Capa 2, Fase 4.

Verifies claims in editorial briefs before publication.
"""

from agents.fact_checker.agent import FactCheckerAgent
from agents.fact_checker.schemas import FactCheckResult, FactCheckerOutput

__all__ = ["FactCheckerAgent", "FactCheckResult", "FactCheckerOutput"]
