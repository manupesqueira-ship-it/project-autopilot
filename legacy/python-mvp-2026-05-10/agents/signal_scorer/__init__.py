"""Signal Scorer agent — Wave 1, Capa 2.

Evaluates source items against the Signal Scoring Rubric using Claude API.
Produces ranked shortlist with justifications for editorial review.
"""

from agents.signal_scorer.agent import SignalScorerAgent
from agents.signal_scorer.schemas import ScoredItem, SignalScorerResult

__all__ = ["SignalScorerAgent", "ScoredItem", "SignalScorerResult"]
