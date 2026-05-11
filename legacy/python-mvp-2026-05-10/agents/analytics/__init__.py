"""Analytics agent — Capa 2, Fase 5.

Collects pipeline metrics, API costs, and content performance data.
Produces weekly reports with recommendations.
"""

from agents.analytics.agent import AnalyticsAgent
from agents.analytics.schemas import AnalyticsOutput, WeeklyReport

__all__ = ["AnalyticsAgent", "AnalyticsOutput", "WeeklyReport"]
