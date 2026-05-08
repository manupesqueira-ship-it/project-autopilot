"""Preliminary scoring — fast, heuristic, no LLM.

Assigns a 0-100 score to each SourceItem based on configurable weights.
This is NOT the Signal Scorer (which uses LLM). This is a quick filter to
prioritize items before they reach the Signal Scorer.

Scoring rubric (from MASTER_PLAN Anexo B, adapted for preliminary use):
    - recency: How fresh is it? (0-20)
    - source_weight: How trusted/important is this source? (0-20)
    - keyword_match: Does the title/snippet match priority keywords? (0-20)
    - language_fit: Is it in the property's target language? (0-10)
    - length_signal: Does it have enough content to be substantive? (0-10)
    - category_bonus: Is it from a priority category? (0-10)
    - penalty_duplicate_topic: Deduction if similar topic already scored high today (0 to -10)
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from agents.source_monitor.schemas import SourceItem

logger = logging.getLogger(__name__)


class PreliminaryScorer:
    """Scores SourceItems using fast heuristics.

    All scoring is deterministic and runs without API calls.
    The weights and thresholds are loaded from config.yaml.

    Usage:
        scorer = PreliminaryScorer(config={...})
        scored_items = scorer.score_batch(items)
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize scorer with weights and keyword lists.

        Args:
            config: Scoring configuration from config.yaml.
                    Expected keys: weights, keywords, recency_hours, etc.
        """
        self.config = config or {}

        # TODO: Load weights from config (with sensible defaults)
        # TODO: Load priority keywords per property
        # TODO: Load source weight overrides

    def score_batch(self, items: list[SourceItem]) -> list[SourceItem]:
        """Score a batch of items and return them sorted by score descending.

        Args:
            items: List of SourceItems to score.

        Returns:
            Same items with preliminary_score and score_breakdown populated,
            sorted by score descending.
        """
        # TODO: Score each item
        # TODO: Sort by preliminary_score descending
        raise NotImplementedError("M3: Batch scoring")

    def score_item(self, item: SourceItem) -> SourceItem:
        """Score a single item across all dimensions.

        Modifies item in-place (sets preliminary_score and score_breakdown).

        Args:
            item: The SourceItem to score.

        Returns:
            The same item with scores populated.
        """
        breakdown = {}

        # TODO: Calculate each dimension
        breakdown["recency"] = self._score_recency(item)
        breakdown["source_weight"] = self._score_source_weight(item)
        breakdown["keyword_match"] = self._score_keywords(item)
        breakdown["language_fit"] = self._score_language(item)
        breakdown["length_signal"] = self._score_length(item)
        breakdown["category_bonus"] = self._score_category(item)

        # TODO: Sum and clamp to 0-100
        # item.preliminary_score = max(0.0, min(100.0, sum(breakdown.values())))
        # item.score_breakdown = breakdown

        raise NotImplementedError("M3: Item scoring")

    def _score_recency(self, item: SourceItem) -> float:
        """Score based on how recently the item was published.

        Items < 6 hours old get max score. Decays linearly to 0 at 72 hours.

        Returns:
            Score 0-20.
        """
        # TODO: Calculate hours since publication
        # TODO: Apply decay curve
        raise NotImplementedError("M3: Recency scoring")

    def _score_source_weight(self, item: SourceItem) -> float:
        """Score based on the source's configured weight/trustworthiness.

        Source weights come from sources.yaml (per-source weight field).

        Returns:
            Score 0-20.
        """
        # TODO: Look up source weight from config
        # TODO: Normalize to 0-20 range
        raise NotImplementedError("M3: Source weight scoring")

    def _score_keywords(self, item: SourceItem) -> float:
        """Score based on keyword matches in title and snippet.

        Keywords are loaded from config.yaml, specific to the property.
        Example keywords for ai-brief-latam: "anthropic", "openai", "latam",
        "regulacion", "startup", etc.

        Returns:
            Score 0-20.
        """
        # TODO: Check title and snippet against keyword list
        # TODO: Weight title matches higher than snippet matches
        # TODO: Normalize to 0-20
        raise NotImplementedError("M3: Keyword scoring")

    def _score_language(self, item: SourceItem) -> float:
        """Score based on language match with property's target.

        Items in the property's language get full score.
        Items in English get partial score (most AI content is in English).

        Returns:
            Score 0-10.
        """
        # TODO: Compare item.language with property target language
        raise NotImplementedError("M3: Language scoring")

    def _score_length(self, item: SourceItem) -> float:
        """Score based on snippet/content length as a proxy for substance.

        Very short items (tweets, one-liners) score lower.
        Substantial articles (200+ chars snippet) score higher.

        Returns:
            Score 0-10.
        """
        # TODO: Check len(item.snippet)
        raise NotImplementedError("M3: Length scoring")

    def _score_category(self, item: SourceItem) -> float:
        """Bonus score for items from priority source categories.

        For ai-brief-latam, "oficial" and "latam" categories get a bonus.

        Returns:
            Score 0-10.
        """
        # TODO: Check item.source_category against priority list
        raise NotImplementedError("M3: Category scoring")
