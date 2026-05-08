"""Acceptance tests for Source Monitor agent.

These 5 tests correspond to the acceptance criteria in DESIGN.md section 9.
All tests use fixtures/mocks — no real network calls.

Run: pytest agents/source_monitor/tests/test_agent.py -v
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure project root is on sys.path for imports
_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.source_monitor.agent import SourceMonitorAgent
from agents.source_monitor.schemas import (
    ErrorType,
    SourceCategory,
    SourceConfig,
    SourceError,
    SourceItem,
    SourceMonitorResult,
    SourceType,
)
from agents.source_monitor.scorer import PreliminaryScorer
from agents.source_monitor.sources import SourceFetcher

# ---------------------------------------------------------------------------
# RSS fixture data
# ---------------------------------------------------------------------------

SAMPLE_RSS_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com</link>
    <item>
      <title>OpenAI Launches GPT-5 for Enterprise</title>
      <link>https://example.com/gpt5-enterprise</link>
      <pubDate>Wed, 07 May 2026 14:00:00 GMT</pubDate>
      <description>&lt;p&gt;OpenAI announced GPT-5 for enterprise customers today, featuring improved reasoning.&lt;/p&gt;</description>
      <author>Jane Doe</author>
      <category>AI</category>
      <category>Enterprise</category>
    </item>
    <item>
      <title>Anthropic Raises $3B Series D</title>
      <link>https://example.com/anthropic-3b</link>
      <pubDate>Tue, 06 May 2026 10:00:00 GMT</pubDate>
      <description>Anthropic secured $3 billion in new funding for Claude development.</description>
      <author>John Smith</author>
      <category>Funding</category>
    </item>
    <item>
      <title>Mercado Libre integra IA para vendedores LATAM</title>
      <link>https://example.com/meli-ia</link>
      <pubDate>Mon, 05 May 2026 08:00:00 GMT</pubDate>
      <description>Mercado Libre lanzó herramientas de inteligencia artificial para vendedores en la región.</description>
    </item>
  </channel>
</rss>
"""

MALFORMED_RSS_XML = "this is not xml at all {{{}}}"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def project_root() -> Path:
    return _project_root


@pytest.fixture
def sample_source_config() -> SourceConfig:
    return SourceConfig(
        name="Test Tech Blog",
        url="https://example.com/feed.xml",
        type=SourceType.RSS,
        category=SourceCategory.OFICIAL,
        weight=1.5,
    )


@pytest.fixture
def sample_items() -> list[SourceItem]:
    now = datetime.now(tz=timezone.utc)
    items = []
    for i in range(5):
        items.append(
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
    return items


@pytest.fixture
def seen_item_ids() -> set[str]:
    return {"item_000", "item_002", "item_004"}


@pytest.fixture
def fetcher() -> SourceFetcher:
    return SourceFetcher(timeout=10)


def _mock_response(text: str, status_code: int = 200):
    """Create a mock httpx.Response-like object."""
    import httpx
    return httpx.Response(
        status_code=status_code,
        text=text,
        request=httpx.Request("GET", "https://example.com/feed.xml"),
    )


# ---------------------------------------------------------------------------
# M1 — Config loading and project root detection
# ---------------------------------------------------------------------------

class TestM1ConfigLoading:
    """M1 tests: agent initializes, finds project root, loads config and sources."""

    def test_find_project_root(self):
        root = SourceMonitorAgent._find_project_root()
        assert root.exists()
        assert (root / "MASTER_PLAN.md").exists()

    def test_agent_initializes(self, project_root):
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        assert agent.property_name == "ai-brief-latam"
        assert agent.config_dir == project_root

    def test_agent_config_loaded(self, project_root):
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        assert agent.agent_config["agent"]["name"] == "source_monitor"
        assert "scoring" in agent.agent_config
        assert "weights" in agent.agent_config["scoring"]

    def test_sources_loaded(self, project_root):
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        assert len(agent.sources) > 0
        for source in agent.sources:
            assert source.enabled is True
            assert source.url != "TBD"
            assert source.name

    def test_sources_have_categories(self, project_root):
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        categories = {s.category for s in agent.sources}
        assert SourceCategory.OFICIAL in categories

    def test_sources_skip_tbd_urls(self, project_root):
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        for source in agent.sources:
            assert "TBD" not in source.url.upper()

    def test_keywords_loaded(self, project_root):
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        kw = agent.get_property_keywords()
        assert len(kw.get("high_priority", [])) > 0
        assert len(kw.get("normal", [])) > 0
        hp = [k.lower() for k in kw["high_priority"]]
        assert "anthropic" in hp
        assert "openai" in hp

    def test_scoring_config_loaded(self, project_root):
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        sc = agent.get_scoring_config()
        weights = sc["weights"]
        assert weights["recency"] == 20
        assert weights["keyword_match"] == 20
        assert sum(weights.values()) == 90

    def test_invalid_property_raises(self, project_root):
        with pytest.raises(FileNotFoundError, match="Sources config not found"):
            SourceMonitorAgent("nonexistent-property", config_dir=project_root)

    def test_generate_item_id_deterministic(self):
        dt = datetime(2026, 5, 7, 12, 0, 0)
        id1 = SourceMonitorAgent.generate_item_id("https://example.com/article", dt)
        id2 = SourceMonitorAgent.generate_item_id("https://example.com/article", dt)
        assert id1 == id2
        assert len(id1) == 16

    def test_generate_item_id_different_for_different_input(self):
        dt = datetime(2026, 5, 7, 12, 0, 0)
        id1 = SourceMonitorAgent.generate_item_id("https://example.com/a", dt)
        id2 = SourceMonitorAgent.generate_item_id("https://example.com/b", dt)
        assert id1 != id2


# ---------------------------------------------------------------------------
# T1 — Fetch RSS feed and parse items
# ---------------------------------------------------------------------------

class TestT1FetchRSS:
    """T1: Given a valid RSS feed, source_monitor extracts SourceItems."""

    def test_fetch_rss_returns_source_items(self, sample_source_config, fetcher):
        """Fetch from a mocked RSS feed and verify SourceItem fields are populated."""
        with patch.object(fetcher._client, "get", return_value=_mock_response(SAMPLE_RSS_XML)):
            items, errors = fetcher.fetch(sample_source_config)

        assert len(errors) == 0
        assert len(items) == 3

        # Check first item fields
        item = items[0]
        assert item.title == "OpenAI Launches GPT-5 for Enterprise"
        assert str(item.url) == "https://example.com/gpt5-enterprise"
        assert item.source_name == "Test Tech Blog"
        assert item.source_category == SourceCategory.OFICIAL
        assert item.published_at is not None
        assert len(item.id) == 16
        assert "OpenAI" in item.snippet or "GPT-5" in item.snippet

    def test_fetch_rss_extracts_authors_and_tags(self, sample_source_config, fetcher):
        """Authors and tags are extracted from RSS entries."""
        with patch.object(fetcher._client, "get", return_value=_mock_response(SAMPLE_RSS_XML)):
            items, _ = fetcher.fetch(sample_source_config)

        assert "Jane Doe" in items[0].authors
        assert "ai" in items[0].tags

    def test_fetch_rss_detects_spanish(self, sample_source_config, fetcher):
        """Spanish-language items are detected via heuristic."""
        with patch.object(fetcher._client, "get", return_value=_mock_response(SAMPLE_RSS_XML)):
            items, _ = fetcher.fetch(sample_source_config)

        # Third item is in Spanish
        meli_item = [i for i in items if "Mercado Libre" in i.title][0]
        assert meli_item.language == "es"

    def test_fetch_rss_handles_malformed_feed(self, sample_source_config, fetcher):
        """Malformed RSS returns empty list + error, not an exception."""
        with patch.object(fetcher._client, "get", return_value=_mock_response(MALFORMED_RSS_XML)):
            items, errors = fetcher.fetch(sample_source_config)

        assert len(items) == 0
        assert len(errors) == 1
        assert errors[0].source_name == "Test Tech Blog"

    def test_fetch_rss_handles_http_500(self, sample_source_config, fetcher):
        """HTTP 500 returns error, not exception."""
        import httpx
        resp = _mock_response("Server Error", status_code=500)
        with patch.object(fetcher._client, "get", side_effect=httpx.HTTPStatusError(
            "500", request=resp.request, response=resp
        )):
            items, errors = fetcher.fetch(sample_source_config)

        assert len(items) == 0
        assert len(errors) == 1
        assert errors[0].error_type == ErrorType.CONNECTION


# ---------------------------------------------------------------------------
# T2 — Deduplication works
# ---------------------------------------------------------------------------

class TestT2Deduplication:
    """T2: Items already seen in history are filtered out."""

    def test_dedup_removes_seen_items(self, project_root, sample_items, seen_item_ids):
        """5 items with 3 already seen -> 2 new items returned."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        agent._seen_ids = seen_item_ids

        unique = agent._deduplicate(sample_items)

        assert len(unique) == 2
        unique_ids = {i.id for i in unique}
        assert "item_001" in unique_ids
        assert "item_003" in unique_ids

    def test_dedup_within_batch(self, project_root, sample_items):
        """Duplicate items within the same batch are also deduplicated."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        agent._seen_ids = set()

        # Duplicate item_000 in the batch
        dupe = sample_items[0].model_copy()
        sample_items.append(dupe)

        unique = agent._deduplicate(sample_items)
        assert len(unique) == 5  # 5 unique, 1 intra-batch dupe removed

    def test_dedup_history_persistence(self, project_root, tmp_path):
        """Dedup history is saved and loaded correctly."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        # Override history path to tmp
        history_path = tmp_path / "seen_items.json"
        agent.agent_config["dedup"] = {
            "history_file": str(history_path),
            "history_max_age_days": 30,
        }

        now = datetime.now(tz=timezone.utc)
        items = [
            SourceItem(
                id="persist_001",
                title="Test",
                url="https://example.com/persist",
                source_name="Test",
                source_category=SourceCategory.OFICIAL,
                published_at=now,
            )
        ]
        agent._update_dedup_history(items)

        # Verify file was written
        assert history_path.exists()
        data = json.loads(history_path.read_text())
        assert any(e["id"] == "persist_001" for e in data)


# ---------------------------------------------------------------------------
# T3 — Preliminary scoring assigns scores
# ---------------------------------------------------------------------------

class TestT3PreliminaryScoring:
    """T3: Scorer assigns 0-100 scores with breakdown."""

    @pytest.fixture
    def scorer(self, project_root) -> PreliminaryScorer:
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        return agent.scorer

    def test_scoring_assigns_valid_scores(self, scorer, sample_items):
        """All items get a score between 0 and 100 with breakdown."""
        scored = scorer.score_batch(sample_items)
        expected_keys = {"recency", "source_weight", "keyword_match",
                         "language_fit", "length_signal", "category_bonus"}
        for item in scored:
            assert 0 <= item.preliminary_score <= 100
            assert set(item.score_breakdown.keys()) == expected_keys
            # Breakdown should sum to match total (within rounding)
            assert abs(sum(item.score_breakdown.values()) - item.preliminary_score) < 0.1

    def test_scoring_orders_by_score_descending(self, scorer, sample_items):
        """Items are returned sorted by score, highest first."""
        scored = scorer.score_batch(sample_items)
        for i in range(len(scored) - 1):
            assert scored[i].preliminary_score >= scored[i + 1].preliminary_score

    def test_recency_affects_score(self, scorer, sample_items):
        """More recent items score higher on the recency dimension."""
        scorer.score_batch(sample_items)
        # sample_items[0] is now, sample_items[4] is 24h ago
        assert sample_items[0].score_breakdown["recency"] > sample_items[4].score_breakdown["recency"]

    def test_keyword_match_boosts_score(self, scorer):
        """Items with AI keywords in title score higher than generic items."""
        now = datetime.now(tz=timezone.utc)
        ai_item = SourceItem(
            id="kw_001", title="OpenAI Launches GPT-5 Claude Integration",
            url="https://example.com/ai", source_name="Test",
            source_category=SourceCategory.OFICIAL, published_at=now,
            snippet="Anthropic and OpenAI collaborate on multi-agent systems.",
        )
        generic_item = SourceItem(
            id="kw_002", title="Weather Report for Tuesday",
            url="https://example.com/weather", source_name="Test",
            source_category=SourceCategory.OFICIAL, published_at=now,
            snippet="It will be sunny with a high of 75 degrees.",
        )
        scorer.score_item(ai_item)
        scorer.score_item(generic_item)
        assert ai_item.score_breakdown["keyword_match"] > generic_item.score_breakdown["keyword_match"]

    def test_latam_source_gets_category_bonus(self, scorer):
        """Items from LATAM category sources get the category bonus."""
        now = datetime.now(tz=timezone.utc)
        latam_item = SourceItem(
            id="cat_001", title="Test", url="https://example.com/1",
            source_name="Contxto", source_category=SourceCategory.LATAM,
            published_at=now,
        )
        community_item = SourceItem(
            id="cat_002", title="Test", url="https://example.com/2",
            source_name="HN", source_category=SourceCategory.COMMUNITY,
            published_at=now,
        )
        scorer.score_item(latam_item)
        scorer.score_item(community_item)
        assert latam_item.score_breakdown["category_bonus"] == 10.0
        assert community_item.score_breakdown["category_bonus"] == 0.0

    def test_spanish_language_scores_higher(self, scorer):
        """Spanish items score higher on language_fit than English."""
        now = datetime.now(tz=timezone.utc)
        es_item = SourceItem(
            id="lang_001", title="Test", url="https://example.com/1",
            source_name="T", source_category=SourceCategory.OFICIAL,
            published_at=now, language="es",
        )
        en_item = SourceItem(
            id="lang_002", title="Test", url="https://example.com/2",
            source_name="T", source_category=SourceCategory.OFICIAL,
            published_at=now, language="en",
        )
        scorer.score_item(es_item)
        scorer.score_item(en_item)
        assert es_item.score_breakdown["language_fit"] > en_item.score_breakdown["language_fit"]

    def test_end_to_end_scoring_in_pipeline(self, project_root, tmp_path):
        """Full scan with scoring produces items with non-zero scores."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        agent.agent_config["output"] = {"evidence_dir": str(tmp_path / "evidence")}
        agent.agent_config["dedup"] = {
            "history_file": str(tmp_path / "seen.json"),
            "history_max_age_days": 30,
        }
        agent.sources = [SourceConfig(
            name="Mock Feed", url="https://mock.example.com/feed.xml",
            type=SourceType.RSS, category=SourceCategory.OFICIAL, weight=2.0,
        )]

        with patch.object(agent.fetcher._client, "get", return_value=_mock_response(SAMPLE_RSS_XML)):
            result = agent.run()

        assert len(result.items) == 3
        # All items should have non-zero scores (they have AI keywords)
        for item in result.items:
            assert item.preliminary_score > 0
            assert len(item.score_breakdown) == 6
        # Items should be sorted descending
        scores = [i.preliminary_score for i in result.items]
        assert scores == sorted(scores, reverse=True)
        # Stats should reflect scoring
        assert result.stats.avg_preliminary_score > 0


# ---------------------------------------------------------------------------
# T4 — Graceful handling of source failures
# ---------------------------------------------------------------------------

class TestT4GracefulFailures:
    """T4: One source failing doesn't stop the whole scan."""

    def test_failed_source_doesnt_stop_scan(self, project_root):
        """HTTP 500 from one source, other source works -> partial results."""
        import httpx

        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)

        source_ok = SourceConfig(
            name="Good Feed", url="https://good.example.com/feed.xml",
            type=SourceType.RSS, category=SourceCategory.OFICIAL,
        )
        source_fail = SourceConfig(
            name="Bad Feed", url="https://bad.example.com/feed.xml",
            type=SourceType.RSS, category=SourceCategory.OFICIAL,
        )

        call_count = 0
        def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if "bad" in str(url):
                resp = _mock_response("Error", 500)
                raise httpx.HTTPStatusError("500", request=resp.request, response=resp)
            return _mock_response(SAMPLE_RSS_XML)

        with patch.object(agent.fetcher._client, "get", side_effect=mock_get):
            items, errors = agent._fetch_all([source_ok, source_fail])

        assert len(items) == 3  # from good feed
        assert len(errors) == 1
        assert errors[0].source_name == "Bad Feed"
        assert errors[0].error_type == ErrorType.CONNECTION

    def test_timeout_captured_as_error(self, project_root):
        """Source that times out is captured as error, not exception."""
        import httpx

        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        source = SourceConfig(
            name="Slow Feed", url="https://slow.example.com/feed.xml",
            type=SourceType.RSS, category=SourceCategory.OFICIAL,
        )

        with patch.object(
            agent.fetcher._client, "get",
            side_effect=httpx.ReadTimeout("timeout")
        ):
            items, errors = agent._fetch_all([source])

        assert len(items) == 0
        assert len(errors) == 1
        assert errors[0].error_type == ErrorType.CONNECTION
        assert "timeout" in errors[0].message.lower()


# ---------------------------------------------------------------------------
# T5 — End-to-end scan produces valid output
# ---------------------------------------------------------------------------

class TestT5EndToEnd:
    """T5: Full scan cycle produces valid SourceMonitorResult JSON."""

    def test_scan_produces_valid_result(self, project_root, tmp_path):
        """Complete scan cycle outputs valid JSON to evidence directory."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        # Override evidence dir to tmp
        agent.agent_config["output"] = {
            "evidence_dir": str(tmp_path / "evidence"),
        }
        # Override dedup to tmp
        agent.agent_config["dedup"] = {
            "history_file": str(tmp_path / "seen.json"),
            "history_max_age_days": 30,
        }
        # Use only one mocked source
        agent.sources = [SourceConfig(
            name="Mock Feed", url="https://mock.example.com/feed.xml",
            type=SourceType.RSS, category=SourceCategory.OFICIAL,
        )]

        with patch.object(agent.fetcher._client, "get", return_value=_mock_response(SAMPLE_RSS_XML)):
            result = agent.run()

        # Validate result object
        assert isinstance(result, SourceMonitorResult)
        assert result.property == "ai-brief-latam"
        assert len(result.items) == 3
        assert result.stats.items_found == 3
        assert result.stats.items_after_dedup == 3
        assert result.stats.dedup_removed == 0

        # Validate each item
        for item in result.items:
            assert item.title
            assert str(item.url).startswith("https://")
            assert item.source_name == "Mock Feed"
            assert item.published_at is not None
            assert len(item.id) == 16

        # Validate evidence file
        evidence_dirs = list((tmp_path / "evidence").iterdir())
        assert len(evidence_dirs) == 1
        output_file = evidence_dirs[0] / "source_monitor_output.json"
        assert output_file.exists()
        parsed = SourceMonitorResult.model_validate_json(output_file.read_text())
        assert len(parsed.items) == 3

    def test_scan_second_run_deduplicates(self, project_root, tmp_path):
        """Running scan twice deduplicates items from first run."""
        agent = SourceMonitorAgent("ai-brief-latam", config_dir=project_root)
        agent.agent_config["output"] = {"evidence_dir": str(tmp_path / "evidence")}
        agent.agent_config["dedup"] = {
            "history_file": str(tmp_path / "seen.json"),
            "history_max_age_days": 30,
        }
        agent.sources = [SourceConfig(
            name="Mock Feed", url="https://mock.example.com/feed.xml",
            type=SourceType.RSS, category=SourceCategory.OFICIAL,
        )]

        with patch.object(agent.fetcher._client, "get", return_value=_mock_response(SAMPLE_RSS_XML)):
            result1 = agent.run()
            result2 = agent.run()

        assert len(result1.items) == 3
        assert len(result2.items) == 0  # all deduped
        assert result2.stats.dedup_removed == 3
