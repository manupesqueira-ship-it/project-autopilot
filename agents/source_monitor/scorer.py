"""Preliminary scoring — fast, heuristic, no LLM.

Assigns a 0-100 score to each SourceItem based on configurable weights.
This is NOT the Signal Scorer (which uses LLM). This is a quick filter to
prioritize items before they reach the Signal Scorer.

Scoring dimensions (from MASTER_PLAN Anexo B, adapted for preliminary use):
    - recency: How fresh is it? (0-20)
    - source_weight: How trusted/important is this source? (0-20)
    - keyword_match: Does the title/snippet match priority keywords? (0-20)
    - language_fit: Is it in the property's target language? (0-10)
    - length_signal: Does it have enough content to be substantive? (0-10)
    - category_bonus: Is it from a priority category? (0-10)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from agents.source_monitor.schemas import SourceItem

logger = logging.getLogger(__name__)

# Defaults if config is missing
_DEFAULT_WEIGHTS = {
    "recency": 20,
    "source_weight": 20,
    "keyword_match": 20,
    "language_fit": 10,
    "length_signal": 10,
    "category_bonus": 10,
}
_DEFAULT_RECENCY = {"max_score_hours": 6, "zero_score_hours": 72}

# If keyword_match falls below the configured gate threshold, optional bonuses
# (language_fit, length_signal, category_bonus) are zeroed out — prevents
# topically-irrelevant items from ranking high on bonuses alone.
# Read from scoring.keyword_gate_threshold in config.yaml; falls back here.
_DEFAULT_KEYWORD_GATE_THRESHOLD = 1.0


class PreliminaryScorer:
    """Scores SourceItems using fast heuristics.

    All scoring is deterministic and runs without API calls.
    The weights and thresholds are loaded from config.yaml.

    Usage:
        scorer = PreliminaryScorer(config=agent.get_scoring_config(),
                                   property_name="ai-brief-latam")
        scored_items = scorer.score_batch(items)
    """

    def __init__(self, config: dict[str, Any] | None = None, property_name: str = ""):
        """Initialize scorer with weights and keyword lists.

        Args:
            config: The "scoring" section from agent config.yaml.
            property_name: Property name for keyword/category lookup.
        """
        config = config or {}
        self.property_name = property_name
        self.weights = config.get("weights", _DEFAULT_WEIGHTS)
        self.recency_cfg = config.get("recency", _DEFAULT_RECENCY)
        self.keyword_gate_threshold = float(
            config.get("keyword_gate_threshold", _DEFAULT_KEYWORD_GATE_THRESHOLD)
        )

        # Keywords
        kw_all = config.get("keywords", {}).get(property_name, {})
        self.keywords_high: list[str] = [k.lower() for k in kw_all.get("high_priority", [])]
        self.keywords_normal: list[str] = [k.lower() for k in kw_all.get("normal", [])]

        # Priority categories
        self.priority_categories: list[str] = (
            config.get("priority_categories", {}).get(property_name, [])
        )

    def score_batch(self, items: list[SourceItem]) -> list[SourceItem]:
        """Score a batch of items and return them sorted by score descending."""
        for item in items:
            self.score_item(item)
        items.sort(key=lambda x: x.preliminary_score, reverse=True)
        return items

    def score_item(self, item: SourceItem) -> SourceItem:
        """Score a single item across all dimensions. Modifies in-place."""
        breakdown = {
            "recency": self._score_recency(item),
            "source_weight": self._score_source_weight(item),
            "keyword_match": self._score_keywords(item),
            "language_fit": self._score_language(item),
            "length_signal": self._score_length(item),
            "category_bonus": self._score_category(item),
        }
        # Keyword gate: if topical relevance is too weak, drop the optional bonuses.
        if breakdown["keyword_match"] < self.keyword_gate_threshold:
            breakdown["language_fit"] = 0.0
            breakdown["length_signal"] = 0.0
            breakdown["category_bonus"] = 0.0
        total = max(0.0, min(100.0, sum(breakdown.values())))
        item.preliminary_score = round(total, 2)
        item.score_breakdown = {k: round(v, 2) for k, v in breakdown.items()}
        return item

    # ------------------------------------------------------------------
    # Individual scoring dimensions
    # ------------------------------------------------------------------

    def _score_recency(self, item: SourceItem) -> float:
        """Score 0-{max_weight} based on freshness. Linear decay."""
        max_w = self.weights.get("recency", 20)
        max_hours = self.recency_cfg.get("max_score_hours", 6)
        zero_hours = self.recency_cfg.get("zero_score_hours", 72)

        now = datetime.now(timezone.utc)
        pub = item.published_at
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)

        age_hours = (now - pub).total_seconds() / 3600.0

        if age_hours <= max_hours:
            return float(max_w)
        if age_hours >= zero_hours:
            return 0.0
        # Linear decay between max_hours and zero_hours
        ratio = 1.0 - (age_hours - max_hours) / (zero_hours - max_hours)
        return max_w * ratio

    def _score_source_weight(self, item: SourceItem) -> float:
        """Score 0-{max_weight} based on source's configured weight.

        Source weight is stored in raw_metadata.source_weight (set by SourceFetcher).
        Range 0.0-5.0 from sources.yaml, normalized to 0-max_weight.
        Default weight=1.0 -> 40% of max.
        """
        max_w = self.weights.get("source_weight", 20)
        weight = item.raw_metadata.get("source_weight", 1.0)
        # Normalize: weight range is 0-5, so weight/5 * max_w
        # But typical range is 1.0-2.0, so use weight/2.5 for better spread
        return min(max_w, max_w * (weight / 2.5))

    def _score_keywords(self, item: SourceItem) -> float:
        """Score 0-{max_weight} based on keyword matches in title + snippet.

        Title matches count 3x. High-priority keywords count 2x.
        Score is capped at max_weight to prevent keyword-stuffed items
        from dominating.
        """
        max_w = self.weights.get("keyword_match", 20)
        if not self.keywords_high and not self.keywords_normal:
            return max_w * 0.5  # No keywords configured = neutral score

        title_lower = item.title.lower()
        snippet_lower = item.snippet.lower()
        score = 0.0

        # High-priority keywords: 2 points each, 3x if in title
        for kw in self.keywords_high:
            if kw in title_lower:
                score += 6.0  # 2 * 3 (title multiplier)
            elif kw in snippet_lower:
                score += 2.0

        # Normal keywords: 1 point each, 3x if in title
        for kw in self.keywords_normal:
            if kw in title_lower:
                score += 3.0
            elif kw in snippet_lower:
                score += 1.0

        # Normalize: a "great" item has ~5-8 keyword hits = ~15-30 raw points
        # Map 0-30 raw -> 0-max_w
        return min(max_w, max_w * (score / 30.0))

    def _score_language(self, item: SourceItem) -> float:
        """Score 0-{max_weight} based on language match.

        - Spanish ("es") = full score (target audience is LATAM)
        - English ("en") = 70% (most AI content is English, still valuable)
        - Portuguese ("pt") = 50% (LATAM but not primary)
        """
        max_w = self.weights.get("language_fit", 10)
        lang_scores = {"es": 1.0, "en": 0.7, "pt": 0.5}
        return max_w * lang_scores.get(item.language, 0.3)

    def _score_length(self, item: SourceItem) -> float:
        """Score 0-{max_weight} based on snippet length as substance proxy.

        <50 chars = very thin (tweet-like) = 20%
        50-150 chars = short = 50%
        150-300 chars = decent = 80%
        300+ chars = substantive = 100%
        """
        max_w = self.weights.get("length_signal", 10)
        length = len(item.snippet)

        if length >= 300:
            return float(max_w)
        if length >= 150:
            return max_w * 0.8
        if length >= 50:
            return max_w * 0.5
        return max_w * 0.2

    def _score_category(self, item: SourceItem) -> float:
        """Score 0-{max_weight} bonus for priority source categories.

        For ai-brief-latam: "oficial" and "latam" sources get full bonus.
        Others get 0.
        """
        max_w = self.weights.get("category_bonus", 10)
        if item.source_category.value in self.priority_categories:
            return float(max_w)
        return 0.0
