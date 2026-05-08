"""Acceptance tests for Source Monitor agent.

These 5 tests correspond to the acceptance criteria in DESIGN.md section 9.
All tests use fixtures/mocks — no real network calls.

Run: pytest agents/source_monitor/tests/test_agent.py -v
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from agents.source_monitor.schemas import (
    SourceCategory,
    SourceConfig,
    SourceItem,
    SourceMonitorResult,
    SourceType,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_source_config() -> SourceConfig:
    """A minimal RSS source config for testing."""
    return SourceConfig(
        name="Test Tech Blog",
        url="https://example.com/feed.xml",
        type=SourceType.RSS,
        category=SourceCategory.OFICIAL,
        weight=1.5,
    )


@pytest.fixture
def sample_items() -> list[SourceItem]:
    """A batch of 5 sample items for scoring and dedup tests."""
    now = datetime.utcnow()
    base_items = []
    for i in range(5):
        base_items.append(
            SourceItem(
                id=f"item_{i:03d}",
                title=f"Test Article {i}: AI Startup Raises $10M",
                url=f"https://example.com/article-{i}",
                source_name="Test Tech Blog",
                source_category=SourceCategory.OFICIAL,
                published_at=now - timedelta(hours=i * 6),
                snippet=f"This is a test snippet for article {i}. " * 5,
                authors=["Test Author"],
                tags=["ai", "startup"],
                language="en",
            )
        )
    return base_items


@pytest.fixture
def seen_item_ids() -> set[str]:
    """IDs of items already in the dedup history."""
    return {"item_000", "item_002", "item_004"}


# ---------------------------------------------------------------------------
# T1 — Fetch RSS feed and parse items
# ---------------------------------------------------------------------------

class TestT1FetchRSS:
    """T1: Given a valid RSS feed, source_monitor extracts SourceItems."""

    @pytest.mark.skip(reason="TODO M2: Implement RSS fetching")
    def test_fetch_rss_returns_source_items(self, sample_source_config):
        """Fetch from a mocked RSS feed and verify SourceItem fields are populated."""
        # TODO: Mock HTTP response with a valid RSS XML fixture
        # TODO: Call fetcher._fetch_rss(source_config)
        # TODO: Assert items is a non-empty list of SourceItem
        # TODO: Assert each item has title, url, published_at populated
        # TODO: Assert no errors in result
        pass

    @pytest.mark.skip(reason="TODO M2: Implement RSS fetching")
    def test_fetch_rss_handles_malformed_feed(self, sample_source_config):
        """Malformed RSS returns empty list + error, not an exception."""
        # TODO: Mock HTTP response with invalid XML
        # TODO: Assert returns empty items list
        # TODO: Assert error captured in errors list
        pass


# ---------------------------------------------------------------------------
# T2 — Deduplication works
# ---------------------------------------------------------------------------

class TestT2Deduplication:
    """T2: Items already seen in history are filtered out."""

    @pytest.mark.skip(reason="TODO M2: Implement deduplication")
    def test_dedup_removes_seen_items(self, sample_items, seen_item_ids):
        """5 items with 3 already seen -> 2 new items returned."""
        # TODO: Initialize agent with seen_item_ids as history
        # TODO: Call agent._deduplicate(sample_items)
        # TODO: Assert exactly 2 items returned (item_001, item_003)
        # TODO: Assert returned items have is_duplicate=False
        pass

    @pytest.mark.skip(reason="TODO M2: Implement deduplication")
    def test_dedup_marks_duplicates(self, sample_items, seen_item_ids):
        """Duplicate items are marked with is_duplicate=True and duplicate_of set."""
        # TODO: Call agent._deduplicate(sample_items) with full output
        # TODO: Assert duplicates have is_duplicate=True
        # TODO: Assert duplicate_of points to original ID
        pass


# ---------------------------------------------------------------------------
# T3 — Preliminary scoring assigns scores
# ---------------------------------------------------------------------------

class TestT3PreliminaryScoring:
    """T3: Scorer assigns 0-100 scores with breakdown."""

    @pytest.mark.skip(reason="TODO M3: Implement scoring")
    def test_scoring_assigns_valid_scores(self, sample_items):
        """All items get a score between 0 and 100."""
        # TODO: Initialize PreliminaryScorer with default config
        # TODO: Call scorer.score_batch(sample_items)
        # TODO: Assert each item.preliminary_score is between 0 and 100
        # TODO: Assert each item.score_breakdown has expected keys
        pass

    @pytest.mark.skip(reason="TODO M3: Implement scoring")
    def test_scoring_orders_by_score_descending(self, sample_items):
        """Items are returned sorted by score, highest first."""
        # TODO: Score batch
        # TODO: Assert items[0].preliminary_score >= items[1].preliminary_score >= ...
        pass

    @pytest.mark.skip(reason="TODO M3: Implement scoring")
    def test_recency_affects_score(self, sample_items):
        """More recent items score higher on the recency dimension."""
        # TODO: Items spaced 6h apart — item_000 (now) should have higher recency
        #       than item_004 (24h ago)
        pass


# ---------------------------------------------------------------------------
# T4 — Graceful handling of source failures
# ---------------------------------------------------------------------------

class TestT4GracefulFailures:
    """T4: One source failing doesn't stop the whole scan."""

    @pytest.mark.skip(reason="TODO M2: Implement error handling")
    def test_failed_source_doesnt_stop_scan(self):
        """HTTP 500 from one source, other source works -> partial results."""
        # TODO: Mock 2 sources: one returns 500, one returns valid RSS
        # TODO: Call agent._fetch_all([source_ok, source_fail])
        # TODO: Assert items from working source are returned
        # TODO: Assert error for failed source is in errors list
        # TODO: Assert error.error_type == "connection"
        pass

    @pytest.mark.skip(reason="TODO M2: Implement error handling")
    def test_timeout_captured_as_error(self):
        """Source that times out is captured as error, not exception."""
        # TODO: Mock source with timeout
        # TODO: Assert error.error_type == "connection"
        pass


# ---------------------------------------------------------------------------
# T5 — End-to-end scan produces valid output
# ---------------------------------------------------------------------------

class TestT5EndToEnd:
    """T5: Full scan cycle produces valid SourceMonitorResult JSON."""

    @pytest.mark.skip(reason="TODO M2-M3: Implement full pipeline")
    def test_scan_produces_valid_result(self, tmp_path):
        """Complete scan cycle outputs valid JSON to evidence directory."""
        # TODO: Set up agent with mocked sources and tmp_path as config_dir
        # TODO: Call agent.run()
        # TODO: Assert evidence file exists at expected path
        # TODO: Assert file is valid JSON
        # TODO: Assert JSON parses as SourceMonitorResult
        # TODO: Assert at least 1 item with all required fields
        pass

    @pytest.mark.skip(reason="TODO M2-M3: Implement full pipeline")
    def test_scan_with_no_new_items_returns_empty(self, tmp_path):
        """Scan when all items are already seen returns empty items list, not error."""
        # TODO: Set up agent where all items are in dedup history
        # TODO: Call agent.run()
        # TODO: Assert result.items is empty
        # TODO: Assert result.stats.items_after_dedup == 0
        # TODO: Assert no errors
        pass
