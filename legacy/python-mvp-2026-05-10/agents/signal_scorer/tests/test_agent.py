"""Tests for Signal Scorer agent.

Tests use mocked LLM responses — no real API calls.
Run: pytest agents/signal_scorer/tests/test_agent.py -v
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.signal_scorer.agent import SignalScorerAgent
from agents.signal_scorer.schemas import (
    Classification,
    ScoredItem,
    ScorerStats,
    SignalBreakdown,
    SignalScorerResult,
)
from agents.signal_scorer.scorer import LLMScorer


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

MOCK_LLM_RESPONSE_STRONG = {
    "relevancia_latam": 16,
    "novedad": 13,
    "urgencia": 7,
    "credibilidad_fuente": 14,
    "potencial_educativo": 8,
    "potencial_viral": 8,
    "fit_marca": 8,
    "riesgo": -2,
    "justification": "Anthropic levanta $3B en Serie D, una señal fuerte del mercado de IA. Relevante para LATAM porque Anthropic opera Claude que ya tiene usuarios en la región.",
    "suggested_angle": "Comparar la ronda con las de OpenAI y Google para dar contexto de escala.",
    "risk_flags": [],
}

MOCK_LLM_RESPONSE_DISCARD = {
    "relevancia_latam": 3,
    "novedad": 5,
    "urgencia": 2,
    "credibilidad_fuente": 10,
    "potencial_educativo": 4,
    "potencial_viral": 3,
    "fit_marca": 5,
    "riesgo": 0,
    "justification": "Noticia sobre clima en California sin relevancia para la audiencia LATAM de AI Brief.",
    "suggested_angle": "",
    "risk_flags": [],
}

MOCK_LLM_RESPONSE_RISKY = {
    "relevancia_latam": 12,
    "novedad": 10,
    "urgencia": 5,
    "credibilidad_fuente": 8,
    "potencial_educativo": 6,
    "potencial_viral": 9,
    "fit_marca": 4,
    "riesgo": -8,
    "justification": "Promete rendimientos de 200% en staking, contenido riesgoso que podría confundirse con asesoría financiera.",
    "suggested_angle": "Solo cubrir si se enmarca como advertencia sobre scams.",
    "risk_flags": ["claims financieros sin respaldo", "potencial asesoría financiera"],
}

SAMPLE_SOURCE_ITEM = {
    "id": "abc123",
    "title": "Anthropic Raises $3B Series D",
    "url": "https://example.com/anthropic-3b",
    "source_name": "TechCrunch AI",
    "source_category": "tech_media",
    "published_at": "2026-05-07T14:00:00+00:00",
    "snippet": "Anthropic secured $3 billion in new funding for Claude development.",
    "preliminary_score": 55.0,
    "tags": ["ai", "funding"],
}

SAMPLE_SOURCE_ITEMS = [
    {**SAMPLE_SOURCE_ITEM, "id": f"item_{i}", "title": f"Article {i}", "preliminary_score": 60 - i * 5}
    for i in range(5)
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def project_root() -> Path:
    return _project_root


def _make_mock_anthropic_response(content: dict) -> MagicMock:
    """Create a mock Anthropic API response."""
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text=json.dumps(content))]
    mock_resp.usage = MagicMock(input_tokens=150, output_tokens=200)
    return mock_resp


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

class TestSchemas:

    def test_signal_breakdown_total(self):
        bd = SignalBreakdown(
            relevancia_latam=15, novedad=10, urgencia=5,
            credibilidad_fuente=12, potencial_educativo=7,
            potencial_viral=6, fit_marca=8, riesgo=-3,
        )
        assert bd.total == 60.0

    def test_signal_breakdown_clamps(self):
        bd = SignalBreakdown(
            relevancia_latam=20, novedad=15, urgencia=10,
            credibilidad_fuente=15, potencial_educativo=10,
            potencial_viral=10, fit_marca=10, riesgo=0,
        )
        assert bd.total == 90.0  # Max possible

    def test_classification_thresholds(self):
        assert ScoredItem.classify(75) == Classification.STRONG
        assert ScoredItem.classify(70.1) == Classification.STRONG
        assert ScoredItem.classify(70) == Classification.CONSIDER
        assert ScoredItem.classify(50) == Classification.CONSIDER
        assert ScoredItem.classify(49.9) == Classification.DISCARD


# ---------------------------------------------------------------------------
# T1 — Score a single item with valid breakdown
# ---------------------------------------------------------------------------

class TestT1ScoreSingleItem:

    def test_score_item_returns_valid_breakdown(self):
        scorer = LLMScorer(api_key="test-key")
        with patch.object(scorer.client.messages, "create",
                          return_value=_make_mock_anthropic_response(MOCK_LLM_RESPONSE_STRONG)):
            result = scorer.score_item(SAMPLE_SOURCE_ITEM)

        assert "relevancia_latam" in result
        assert "justification" in result
        assert result["relevancia_latam"] == 16

    def test_build_scored_item_strong(self):
        scorer = LLMScorer(api_key="test-key")
        scored = scorer.build_scored_item(SAMPLE_SOURCE_ITEM, MOCK_LLM_RESPONSE_STRONG)

        assert scored.signal_score == 72.0
        assert scored.classification == Classification.STRONG
        assert "Anthropic" in scored.justification
        assert scored.signal_breakdown.relevancia_latam == 16
        assert scored.item_id == "abc123"

    def test_build_scored_item_discard(self):
        scorer = LLMScorer(api_key="test-key")
        scored = scorer.build_scored_item(SAMPLE_SOURCE_ITEM, MOCK_LLM_RESPONSE_DISCARD)

        assert scored.signal_score == 32.0
        assert scored.classification == Classification.DISCARD


# ---------------------------------------------------------------------------
# T2 — Batch scoring produces ranked shortlist
# ---------------------------------------------------------------------------

class TestT2BatchScoring:

    def test_agent_scores_and_ranks(self, project_root, tmp_path):
        """Score multiple items and verify ranking."""
        # Write a fake source monitor output
        source_evidence = tmp_path / "agents" / "source_monitor" / "evidence" / "test_run"
        source_evidence.mkdir(parents=True)
        with open(source_evidence / "source_monitor_output.json", "w") as f:
            json.dump({"run_id": "test_run", "items": SAMPLE_SOURCE_ITEMS}, f)

        agent = SignalScorerAgent("ai-brief-latam", config_dir=project_root)
        agent.config_dir = tmp_path  # Override for evidence paths

        # Copy config to tmp
        config_dir = tmp_path / "agents" / "signal_scorer"
        config_dir.mkdir(parents=True)
        import shutil
        shutil.copy(project_root / "agents" / "signal_scorer" / "config.yaml",
                     config_dir / "config.yaml")

        agent.agent_config = agent._load_agent_config()
        agent.api_key = "test-key"

        # Mock LLM — return different scores for different items
        responses = [MOCK_LLM_RESPONSE_STRONG, MOCK_LLM_RESPONSE_DISCARD,
                     MOCK_LLM_RESPONSE_STRONG, MOCK_LLM_RESPONSE_RISKY,
                     MOCK_LLM_RESPONSE_DISCARD]

        call_idx = 0
        def mock_create(**kwargs):
            nonlocal call_idx
            resp = _make_mock_anthropic_response(responses[call_idx % len(responses)])
            call_idx += 1
            return resp

        scorer_instance = LLMScorer(api_key="test-key")
        with patch("agents.signal_scorer.agent.LLMScorer") as MockScorer:
            mock_scorer = MagicMock(spec=LLMScorer)
            mock_scorer.api_calls_made = 5
            mock_scorer.api_calls_failed = 0
            mock_scorer.total_input_tokens = 750
            mock_scorer.total_output_tokens = 1000

            real_scorer = LLMScorer(api_key="test-key")
            mock_scorer.score_item = MagicMock(side_effect=[
                MOCK_LLM_RESPONSE_STRONG, MOCK_LLM_RESPONSE_DISCARD,
                MOCK_LLM_RESPONSE_STRONG, MOCK_LLM_RESPONSE_RISKY,
                MOCK_LLM_RESPONSE_DISCARD,
            ])
            mock_scorer.build_scored_item = real_scorer.build_scored_item
            MockScorer.return_value = mock_scorer

            result = agent.run(source_run_id="test_run", min_preliminary_score=0)

        assert len(result.items) == 5
        # Items should be sorted by signal score descending
        scores = [i.signal_score for i in result.items]
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# T3 — API failure falls back gracefully
# ---------------------------------------------------------------------------

class TestT3APIFailure:

    def test_api_error_falls_back_to_preliminary(self):
        scorer = LLMScorer(api_key="test-key")
        error_result = {"error": "API error: rate limited"}

        scored = scorer.build_scored_item(SAMPLE_SOURCE_ITEM, error_result)

        assert scored.signal_score == 55.0  # Falls back to preliminary_score
        assert "[Fallback]" in scored.justification
        assert scorer.api_calls_failed == 0  # build doesn't increment

    def test_api_exception_captured(self):
        import anthropic
        scorer = LLMScorer(api_key="test-key")
        with patch.object(scorer.client.messages, "create",
                          side_effect=anthropic.APIError(
                              message="rate limited",
                              request=MagicMock(),
                              body=None,
                          )):
            result = scorer.score_item(SAMPLE_SOURCE_ITEM)

        assert "error" in result
        assert scorer.api_calls_failed == 1


# ---------------------------------------------------------------------------
# T4 — Risk flags are detected
# ---------------------------------------------------------------------------

class TestT4RiskFlags:

    def test_risk_flags_populated(self):
        scorer = LLMScorer(api_key="test-key")
        scored = scorer.build_scored_item(SAMPLE_SOURCE_ITEM, MOCK_LLM_RESPONSE_RISKY)

        assert len(scored.risk_flags) == 2
        assert any("financiero" in f for f in scored.risk_flags)
        assert scored.signal_breakdown.riesgo == -8
        # Risk penalty should reduce score
        assert scored.signal_score < 55  # Lower than without penalty


# ---------------------------------------------------------------------------
# T5 — Config and initialization
# ---------------------------------------------------------------------------

class TestT5Config:

    def test_agent_initializes(self, project_root):
        agent = SignalScorerAgent("ai-brief-latam", config_dir=project_root)
        assert agent.property_name == "ai-brief-latam"
        assert agent.agent_config["agent"]["name"] == "signal_scorer"

    def test_config_has_expected_fields(self, project_root):
        agent = SignalScorerAgent("ai-brief-latam", config_dir=project_root)
        cfg = agent.agent_config
        assert "llm" in cfg
        assert "scoring" in cfg
        assert cfg["scoring"]["max_items_to_score"] == 20
