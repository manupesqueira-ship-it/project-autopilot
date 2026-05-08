"""Acceptance tests for Source Monitor agent.

These 5 tests correspond to the acceptance criteria in DESIGN.md section 9.
All tests use fixtures/mocks — no real network calls.

Run: pytest agents/source_monitor/tests/test_agent.py -v
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Ensure project root is on sys.path for imports
_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.source_monitor.agent import SourceMonitorAgent
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
def project_root() -> Path:
    """Return the real project root for config loading tests."""
    return _project_root


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
# M1 — Config loading and project root detection
# ---------------------------------------------------------------------------

class TestM1ConfigLoading:
    """M1 tests: agent initializes, finds project root, loads config and sources."""

    def test_find_project_root(self):
        """Agent auto-detects the project root via MASTER_PLAN.md."""
        root = SourceMonitorAgent._find_project_root()
        assert root.exists()
        assert (root / "MASTER_PLAN.md").exists()

    def test_agent_initializes(self, project_root):
        """Agent initializes successfully for ai-brief-latam."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        assert agent.property_name == "ai-brief-latam"
        assert agent.config_dir == project_root

    def test_agent_config_loaded(self, project_root):
        """Agent loads its own config.yaml with expected structure."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        assert agent.agent_config["agent"]["name"] == "source_monitor"
        assert "scoring" in agent.agent_config
        assert "weights" in agent.agent_config["scoring"]

    def test_sources_loaded(self, project_root):
        """Agent loads property sources from sources.yaml."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        assert len(agent.sources) > 0
        # All loaded sources must be enabled and have valid URLs
        for source in agent.sources:
            assert source.enabled is True
            assert source.url != "TBD"
            assert source.name

    def test_sources_have_categories(self, project_root):
        """Each source has a valid category from the enum."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        categories = {s.category for s in agent.sources}
        # We expect at least oficial and tech_media
        assert SourceCategory.OFICIAL in categories

    def test_sources_skip_tbd_urls(self, project_root):
        """Sources with TBD URLs are not included in the loaded list."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        for source in agent.sources:
            assert "TBD" not in source.url.upper()

    def test_keywords_loaded(self, project_root):
        """Agent loads keyword lists for the property."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        kw = agent.get_property_keywords()
        assert len(kw.get("high_priority", [])) > 0
        assert len(kw.get("normal", [])) > 0
        # Spot-check a few keywords
        hp = [k.lower() for k in kw["high_priority"]]
        assert "anthropic" in hp
        assert "openai" in hp

    def test_scoring_config_loaded(self, project_root):
        """Agent loads scoring weights from config."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        sc = agent.get_scoring_config()
        weights = sc["weights"]
        assert weights["recency"] == 20
        assert weights["keyword_match"] == 20
        assert sum(weights.values()) == 90

    def test_invalid_property_raises(self, project_root):
        """Agent raises FileNotFoundError for non-existent property."""
        with pytest.raises(FileNotFoundError, match="Sources config not found"):
            SourceMonitorAgent("nonexistent-property", config_dir=project_root)

    def test_generate_item_id_deterministic(self):
        """generate_item_id produces the same hash for the same input."""
        dt = datetime(2026, 5, 7, 12, 0, 0)
        id1 = SourceMonitorAgent.generate_item_id("https://example.com/article", dt)
        id2 = SourceMonitorAgent.generate_item_id("https://example.com/article", dt)
        assert id1 == id2
        assert len(id1) == 16

    def test_generate_item_id_different_for_different_input(self):
        """Different URLs produce different IDs."""
        dt = datetime(2026, 5, 7, 12, 0, 0)
        id1 = SourceMonitorAgent.generate_item_id("https://example.com/a", dt)
        id2 = SourceMonitorAgent.generate_item_id("https://example.com/b", dt)
        assert id1 != id2


# ---------------------------------------------------------------------------
# T1 — Fetch RSS feed and parse items
# ---------------------------------------------------------------------------

class TestT1FetchRSS:
    """T1: Given a valid RSS feed, source_monitor extracts SourceItems."""

    @pytest.mark.skip(reason="TODO M2: Implement RSS fetching")
    def test_fetch_rss_returns_source_items(self, sample_source_config):
        """Fetch from a mocked RSS feed and verify SourceItem fields are populated."""
        pass

    @pytest.mark.skip(reason="TODO M2: Implement RSS fetching")
    def test_fetch_rss_handles_malformed_feed(self, sample_source_config):
        """Malformed RSS returns empty list + error, not an exception."""
        pass


# ---------------------------------------------------------------------------
# T2 — Deduplication works
# ---------------------------------------------------------------------------

class TestT2Deduplication:
    """T2: Items already seen in history are filtered out."""

    @pytest.mark.skip(reason="TODO M2: Implement deduplication")
    def test_dedup_removes_seen_items(self, sample_items, seen_item_ids):
        """5 items with 3 already seen -> 2 new items returned."""
        pass

    @pytest.mark.skip(reason="TODO M2: Implement deduplication")
    def test_dedup_marks_duplicates(self, sample_items, seen_item_ids):
        """Duplicate items are marked with is_duplicate=True and duplicate_of set."""
        pass


# ---------------------------------------------------------------------------
# T3 — Preliminary scoring assigns scores
# ---------------------------------------------------------------------------

class TestT3PreliminaryScoring:
    """T3: Scorer assigns 0-100 scores with breakdown."""

    @pytest.mark.skip(reason="TODO M3: Implement scoring")
    def test_scoring_assigns_valid_scores(self, sample_items):
        """All items get a score between 0 and 100."""
        pass

    @pytest.mark.skip(reason="TODO M3: Implement scoring")
    def test_scoring_orders_by_score_descending(self, sample_items):
        """Items are returned sorted by score, highest first."""
        pass

    @pytest.mark.skip(reason="TODO M3: Implement scoring")
    def test_recency_affects_score(self, sample_items):
        """More recent items score higher on the recency dimension."""
        pass


# ---------------------------------------------------------------------------
# T4 — Graceful handling of source failures
# ---------------------------------------------------------------------------

class TestT4GracefulFailures:
    """T4: One source failing doesn't stop the whole scan."""

    @pytest.mark.skip(reason="TODO M2: Implement error handling")
    def test_failed_source_doesnt_stop_scan(self):
        """HTTP 500 from one source, other source works -> partial results."""
        pass

    @pytest.mark.skip(reason="TODO M2: Implement error handling")
    def test_timeout_captured_as_error(self):
        """Source that times out is captured as error, not exception."""
        pass


# ---------------------------------------------------------------------------
# T5 — End-to-end scan produces valid output
# ---------------------------------------------------------------------------

class TestT5EndToEnd:
    """T5: Full scan cycle produces valid SourceMonitorResult JSON."""

    @pytest.mark.skip(reason="TODO M2-M3: Implement full pipeline")
    def test_scan_produces_valid_result(self, tmp_path):
        """Complete scan cycle outputs valid JSON to evidence directory."""
        pass

    @pytest.mark.skip(reason="TODO M2-M3: Implement full pipeline")
    def test_scan_with_no_new_items_returns_empty(self, tmp_path):
        """Scan when all items are already seen returns empty items list, not error."""
        pass
