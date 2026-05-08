"""Tests for Editorial agent.

Tests use mocked LLM responses — no real API calls.
Run: pytest agents/editorial/tests/test_agent.py -v
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

from agents.editorial.agent import EditorialAgent
from agents.editorial.briefer import BriefGenerator
from agents.editorial.schemas import (
    BriefStatus,
    CTAType,
    EditorialBrief,
    EditorialResult,
    FormatRecommendation,
)


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

MOCK_SCORED_ITEM = {
    "item_id": "abc123",
    "title": "OpenAI Testing Ads in ChatGPT",
    "url": "https://example.com/chatgpt-ads",
    "source_name": "OpenAI Blog",
    "snippet": "OpenAI announced it will begin testing ads in ChatGPT free tier.",
    "published_at": "2026-05-07T14:00:00+00:00",
    "preliminary_score": 62,
    "signal_score": 80,
    "classification": "strong",
    "justification": "Muy relevante para LATAM. Cambio de modelo de negocio.",
    "suggested_angle": "Impacto en usuarios LATAM del free tier.",
    "risk_flags": [],
}

MOCK_LLM_BRIEF = {
    "title": "ChatGPT tendrá publicidad: qué significa para LATAM",
    "que_paso": "OpenAI anunció que comenzará a probar anuncios en la versión gratuita de ChatGPT. Los ads aparecerán como resultados patrocinados dentro de las respuestas del modelo.",
    "por_que_importa": "LATAM tiene una de las bases de usuarios gratuitos más grandes de ChatGPT. La monetización por ads cambia el incentivo de OpenAI: antes necesitaban convertir free→paid, ahora el free tier genera revenue directamente.",
    "que_cambia": "Antes: el free tier era un funnel hacia Plus/Pro. Ahora: el free tier es un producto publicitario en sí mismo. Los usuarios gratuitos pasan de ser costo a ser activo.",
    "quien_gana_pierde": {
        "gana": ["OpenAI (nueva fuente de revenue)", "Anunciantes B2B"],
        "pierde": ["Usuarios free (experiencia degradada)", "Google Ads (nuevo competidor)"],
        "neutro": ["Usuarios Plus/Pro (sin cambios anunciados)"]
    },
    "datos_clave": [
        "ChatGPT tiene 400M+ usuarios activos semanales (OpenAI, mayo 2026)",
        "LATAM representa ~15% de usuarios globales de ChatGPT",
        "OpenAI gastó $8.5B en 2025 — necesita diversificar ingresos"
    ],
    "angulo_latam": "En LATAM, la mayoría usa el free tier porque el pricing de Plus ($20/mo) no es accesible. Los ads afectan desproporcionadamente a la región.",
    "angulos_posibles": [
        "Educativo: cómo funcionarán los ads y qué esperar",
        "Oportunidad: cómo empresas LATAM pueden anunciarse en ChatGPT",
        "Riesgo: degradación de experiencia para el mercado más price-sensitive"
    ],
    "angulo_elegido": "Riesgo + oportunidad: qué pierden los usuarios LATAM y qué ganan las empresas que se anuncien temprano.",
    "formato_recomendado": "carrusel",
    "hook_tentativo": "ChatGPT va a tener publicidad. Y LATAM es quien más lo va a sentir.",
    "cta_tentativo": "save",
    "riesgos": ["Cifra de 15% LATAM es estimación, verificar con fuente oficial"],
    "fact_check_items": [
        {"claim": "400M+ usuarios activos semanales", "status": "pending"},
        {"claim": "LATAM ~15% de usuarios globales", "status": "pending"},
        {"claim": "$8.5B gastados en 2025", "status": "pending"}
    ]
}


def _make_mock_response(content: dict) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text=json.dumps(content, ensure_ascii=False))]
    mock_resp.usage = MagicMock(input_tokens=400, output_tokens=800)
    return mock_resp


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

class TestSchemas:

    def test_editorial_brief_creates(self):
        brief = EditorialBrief(
            slug="2026-05-07_chatgpt-ads",
            date="2026-05-07",
            property="ai-brief-latam",
            source_item_id="abc123",
            signal_score=80,
            title="Test Brief",
            que_paso="Something happened.",
            por_que_importa="It matters because...",
            que_cambia="Before vs after.",
        )
        assert brief.status == BriefStatus.DRAFT
        assert brief.formato_recomendado == FormatRecommendation.CAROUSEL

    def test_format_and_cta_enums(self):
        assert FormatRecommendation.REEL.value == "reel"
        assert CTAType.SAVE.value == "save"


# ---------------------------------------------------------------------------
# T1 — Generate a single brief
# ---------------------------------------------------------------------------

class TestT1GenerateBrief:

    def test_generate_brief_returns_valid_json(self):
        gen = BriefGenerator(api_key="test-key")
        with patch.object(gen.client.messages, "create",
                          return_value=_make_mock_response(MOCK_LLM_BRIEF)):
            result = gen.generate_brief(MOCK_SCORED_ITEM)

        assert "title" in result
        assert "que_paso" in result
        assert "por_que_importa" in result
        assert "hook_tentativo" in result

    def test_build_editorial_brief(self):
        gen = BriefGenerator(api_key="test-key")
        brief = gen.build_editorial_brief(MOCK_SCORED_ITEM, MOCK_LLM_BRIEF, "ai-brief-latam")

        assert brief is not None
        assert brief.title == "ChatGPT tendrá publicidad: qué significa para LATAM"
        assert brief.status == BriefStatus.DRAFT
        assert brief.signal_score == 80
        assert brief.formato_recomendado == FormatRecommendation.CAROUSEL
        assert brief.cta_tentativo == CTAType.SAVE
        assert len(brief.datos_clave) == 3
        assert len(brief.fact_check_items) == 3
        assert brief.por_que_importa != ""
        assert "LATAM" in brief.angulo_latam

    def test_build_brief_returns_none_on_error(self):
        gen = BriefGenerator(api_key="test-key")
        brief = gen.build_editorial_brief(
            MOCK_SCORED_ITEM, {"error": "API failed"}, "ai-brief-latam"
        )
        assert brief is None


# ---------------------------------------------------------------------------
# T2 — API failure handling
# ---------------------------------------------------------------------------

class TestT2Failures:

    def test_api_error_captured(self):
        import anthropic
        gen = BriefGenerator(api_key="test-key")
        with patch.object(gen.client.messages, "create",
                          side_effect=anthropic.APIError(
                              message="overloaded", request=MagicMock(), body=None)):
            result = gen.generate_brief(MOCK_SCORED_ITEM)

        assert "error" in result
        assert gen.api_calls_failed == 1

    def test_json_parse_error_captured(self):
        gen = BriefGenerator(api_key="test-key")
        bad_response = MagicMock()
        bad_response.content = [MagicMock(text="not json at all")]
        bad_response.usage = MagicMock(input_tokens=100, output_tokens=50)
        with patch.object(gen.client.messages, "create", return_value=bad_response):
            result = gen.generate_brief(MOCK_SCORED_ITEM)

        assert "error" in result


# ---------------------------------------------------------------------------
# T3 — Brief to markdown rendering
# ---------------------------------------------------------------------------

class TestT3Markdown:

    def test_brief_renders_to_markdown(self, project_root):
        agent = EditorialAgent("ai-brief-latam", config_dir=project_root)
        gen = BriefGenerator(api_key="test-key")
        brief = gen.build_editorial_brief(MOCK_SCORED_ITEM, MOCK_LLM_BRIEF, "ai-brief-latam")
        md = agent._brief_to_markdown(brief)

        assert "# ChatGPT" in md
        assert "## Qué pasó" in md
        assert "## Por qué importa" in md
        assert "## Ángulo LATAM" in md
        assert "## Hook tentativo" in md
        assert "| Claim | Status |" in md

    @pytest.fixture
    def project_root(self) -> Path:
        return _project_root


# ---------------------------------------------------------------------------
# T4 — End-to-end with mocked LLM
# ---------------------------------------------------------------------------

class TestT4EndToEnd:

    def test_agent_generates_briefs(self, tmp_path):
        # Set up fake signal scorer output
        score_evidence = tmp_path / "agents" / "signal_scorer" / "evidence" / "test_run"
        score_evidence.mkdir(parents=True)
        with open(score_evidence / "signal_scorer_output.json", "w") as f:
            json.dump({
                "run_id": "test_run",
                "items": [MOCK_SCORED_ITEM, {**MOCK_SCORED_ITEM, "item_id": "def456", "signal_score": 45}],
            }, f)

        # Copy config
        config_dir = tmp_path / "agents" / "editorial"
        config_dir.mkdir(parents=True)
        import shutil
        shutil.copy(_project_root / "agents" / "editorial" / "config.yaml", config_dir / "config.yaml")
        # Fake MASTER_PLAN.md for root detection
        (tmp_path / "MASTER_PLAN.md").touch()

        agent = EditorialAgent("ai-brief-latam", config_dir=tmp_path)
        agent.api_key = "test-key"

        with patch("agents.editorial.agent.BriefGenerator") as MockGen:
            mock_gen = MagicMock(spec=BriefGenerator)
            mock_gen.api_calls_made = 1
            mock_gen.api_calls_failed = 0
            mock_gen.total_input_tokens = 400
            mock_gen.total_output_tokens = 800
            mock_gen.generate_brief.return_value = MOCK_LLM_BRIEF

            real_gen = BriefGenerator(api_key="test-key")
            mock_gen.build_editorial_brief = real_gen.build_editorial_brief
            MockGen.return_value = mock_gen

            result = agent.run(score_run_id="test_run", min_signal_score=60)

        # Only 1 brief (the 45-score item is filtered out)
        assert len(result.briefs) == 1
        assert result.briefs[0].signal_score == 80
        assert result.stats.briefs_generated == 1

        # Check evidence saved
        evidence_dirs = list((tmp_path / "agents" / "editorial" / "evidence").iterdir())
        assert len(evidence_dirs) == 1
        assert (evidence_dirs[0] / "editorial_output.json").exists()


# ---------------------------------------------------------------------------
# T5 — Config
# ---------------------------------------------------------------------------

class TestT5Config:

    def test_agent_initializes(self):
        agent = EditorialAgent("ai-brief-latam", config_dir=_project_root)
        assert agent.property_name == "ai-brief-latam"
        assert agent.agent_config["agent"]["name"] == "editorial"

    def test_config_defaults(self):
        agent = EditorialAgent("ai-brief-latam", config_dir=_project_root)
        cfg = agent.agent_config
        assert cfg["generation"]["max_briefs_per_run"] == 5
        assert cfg["generation"]["min_signal_score"] == 60.0
