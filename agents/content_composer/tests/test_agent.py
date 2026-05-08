"""Tests for Content Composer agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.content_composer.agent import ContentComposerAgent
from agents.content_composer.composer import ContentGenerator
from agents.content_composer.schemas import ComposedContent, ComposerOutput


MOCK_BRIEF = {
    "slug": "2026-05-08_chatgpt-ads",
    "title": "ChatGPT tendrá publicidad",
    "que_paso": "OpenAI anunció que probará anuncios en ChatGPT free tier.",
    "por_que_importa": "LATAM tiene la base de usuarios gratuitos más grande.",
    "que_cambia": "El free tier pasa de costo a activo publicitario.",
    "quien_gana_pierde": {"gana": ["OpenAI"], "pierde": ["Usuarios free"], "neutro": []},
    "datos_clave": ["400M+ usuarios semanales", "LATAM ~15% usuarios"],
    "angulo_latam": "Mayoría usa free tier en LATAM por pricing de Plus.",
    "angulo_elegido": "Riesgo + oportunidad para LATAM.",
    "hook_tentativo": "ChatGPT va a tener publicidad.",
    "formato_recomendado": "carrusel",
    "cta_tentativo": "save",
    "fuentes": ["https://openai.com/index/testing-ads-in-chatgpt"],
}

MOCK_LLM_RESULT = {
    "carousel": {
        "slides": [
            {"slide_number": 1, "headline": "ChatGPT va a tener publicidad", "body": "Y LATAM es quien más lo va a sentir.", "visual_direction": "Dark bg, bold white text"},
            {"slide_number": 2, "headline": "400M+ usuarios semanales", "body": "OpenAI acaba de anunciar ads en el free tier.", "visual_direction": "Number focus, gradient bg"},
            {"slide_number": 3, "headline": "¿Quién gana?", "body": "OpenAI: nueva fuente de revenue.\nAnunciantes B2B: acceso a 400M usuarios.", "visual_direction": "Split green/red"},
            {"slide_number": 4, "headline": "¿Quién pierde?", "body": "Usuarios free en LATAM.\n$20/mo no es accesible para la región.", "visual_direction": "Red tones"},
            {"slide_number": 5, "headline": "¿Qué significa para LATAM?", "body": "La mayoría usa free tier. Los ads nos afectan más que a nadie.", "visual_direction": "LATAM map bg"},
            {"slide_number": 6, "headline": "Guardá esto", "body": "Compartí con tu equipo si usan ChatGPT para trabajo.", "visual_direction": "CTA slide, brand colors"},
        ],
        "caption": {
            "hook": "400M+ usuarios de ChatGPT van a ver publicidad. LATAM es la región más afectada.",
            "body": "OpenAI empieza a probar ads en el free tier. ⚡",
            "cta": "Guardá esto si usás ChatGPT para trabajo",
            "hashtags": ["#IA", "#ChatGPT", "#OpenAI", "#LATAM", "#InteligenciaArtificial", "#TechNews", "#AIBrief"]
        }
    },
    "newsletter": {
        "headline": "CHATGPT TENDRÁ PUBLICIDAD — Y LATAM ES QUIEN MÁS LO VA A SENTIR",
        "intro": "OpenAI anunció que comenzará a probar anuncios dentro de ChatGPT. El cambio aplica al free tier, que concentra la mayoría de usuarios.",
        "por_que_importa": "LATAM tiene una de las bases de usuarios gratuitos más grandes de ChatGPT. La monetización por ads cambia los incentivos de OpenAI.",
        "lo_que_paso": [
            "→ OpenAI confirmó testing de ads en ChatGPT free tier",
            "→ Los ads aparecerán como resultados patrocinados",
            "→ Usuarios Plus/Pro no verán cambios (por ahora)"
        ],
        "que_significa_latam": "En LATAM, $20/mo de Plus no es accesible para la mayoría. Eso significa que los ads afectan desproporcionadamente a la región.\n\n→ Si trabajás en marketing: nuevo canal publicitario con 400M usuarios\n→ Si usás ChatGPT gratis: preparate para ads en tus respuestas\n→ Si vendés SaaS B2B: evaluá anunciarte temprano",
        "bottom_line": "El free tier de ChatGPT ya no es gratis — ahora pagás con atención. Empresas LATAM tienen ventana para anunciarse antes que suba el costo.",
        "fuentes": ["https://openai.com/index/testing-ads-in-chatgpt"]
    },
    "reel_script": {
        "hook": "ChatGPT va a tener publicidad. Y en LATAM nos va a pegar más que a nadie.",
        "body": "OpenAI acaba de confirmar: ads en el free tier. 400 millones de usuarios van a ver anuncios en sus respuestas. El tema es que en LATAM, la mayoría usa el free tier. $20 al mes de Plus no es accesible.",
        "por_que_importa": "El free tier ya no es gratis — ahora pagás con tu atención.",
        "close": "Pero hay una oportunidad: si tenés empresa en LATAM, podés anunciarte en ChatGPT antes que suba el costo.",
        "cta": "Guardá esto si usás ChatGPT para trabajo.",
        "estimated_duration_seconds": 28,
        "on_screen_text": [
            "ChatGPT + publicidad",
            "400M+ usuarios",
            "LATAM = más afectada",
            "¿Oportunidad o problema?"
        ]
    }
}


def _make_mock_response(content: dict) -> MagicMock:
    mock = MagicMock()
    mock.content = [MagicMock(text=json.dumps(content, ensure_ascii=False))]
    mock.usage = MagicMock(input_tokens=600, output_tokens=1200)
    return mock


class TestSchemas:

    def test_composed_content_creates(self):
        cc = ComposedContent(brief_slug="test", brief_title="Test")
        assert cc.carousel.slide_count == 0
        assert cc.reel_script is None


class TestT1GenerateContent:

    def test_compose_returns_all_sections(self):
        gen = ContentGenerator(api_key="test-key")
        with patch.object(gen.client.messages, "create",
                          return_value=_make_mock_response(MOCK_LLM_RESULT)):
            result = gen.compose(MOCK_BRIEF)

        assert "carousel" in result
        assert "newsletter" in result
        assert "reel_script" in result

    def test_build_composed_content(self):
        gen = ContentGenerator(api_key="test-key")
        composed = gen.build_composed_content(MOCK_BRIEF, MOCK_LLM_RESULT)

        assert composed is not None
        # Carousel
        assert composed.carousel.slide_count == 6
        assert len(composed.carousel.slides) == 6
        assert "publicidad" in composed.carousel.slides[0].headline.lower()
        assert len(composed.carousel.caption.hashtags) >= 5
        assert composed.carousel.caption.hook != ""
        assert composed.carousel.caption.full_text != ""

        # Newsletter
        assert "CHATGPT" in composed.newsletter.headline
        assert composed.newsletter.por_que_importa != ""
        assert len(composed.newsletter.lo_que_paso) >= 3
        assert composed.newsletter.bottom_line != ""
        assert composed.newsletter.full_text != ""

        # Reel
        assert composed.reel_script is not None
        assert composed.reel_script.estimated_duration_seconds == 28
        assert len(composed.reel_script.on_screen_text) >= 3

    def test_build_returns_none_on_error(self):
        gen = ContentGenerator(api_key="test-key")
        result = gen.build_composed_content(MOCK_BRIEF, {"error": "API failed"})
        assert result is None


class TestT2Failures:

    def test_api_error_captured(self):
        import anthropic
        gen = ContentGenerator(api_key="test-key")
        with patch.object(gen.client.messages, "create",
                          side_effect=anthropic.APIError(
                              message="overloaded", request=MagicMock(), body=None)):
            result = gen.compose(MOCK_BRIEF)
        assert "error" in result
        assert gen.api_calls_failed == 1


class TestT3EndToEnd:

    def test_agent_composes_content(self, tmp_path):
        ed_evidence = tmp_path / "agents" / "editorial" / "evidence" / "test_run"
        ed_evidence.mkdir(parents=True)
        with open(ed_evidence / "editorial_output.json", "w") as f:
            json.dump({"run_id": "test_run", "briefs": [MOCK_BRIEF]}, f)

        config_dir = tmp_path / "agents" / "content_composer"
        config_dir.mkdir(parents=True)
        import shutil
        shutil.copy(_project_root / "agents" / "content_composer" / "config.yaml",
                     config_dir / "config.yaml")
        (tmp_path / "MASTER_PLAN.md").touch()
        (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=test-key")

        agent = ContentComposerAgent("ai-brief-latam", config_dir=tmp_path)

        with patch("agents.content_composer.agent.ContentGenerator") as MockGen:
            mock_gen = MagicMock(spec=ContentGenerator)
            mock_gen.api_calls_made = 1
            mock_gen.api_calls_failed = 0
            mock_gen.total_input_tokens = 600
            mock_gen.total_output_tokens = 1200
            mock_gen.compose.return_value = MOCK_LLM_RESULT
            real_gen = ContentGenerator(api_key="test-key")
            mock_gen.build_composed_content = real_gen.build_composed_content
            MockGen.return_value = mock_gen

            output = agent.run(editorial_run_id="test_run")

        assert len(output.content) == 1
        assert output.stats.carousels_generated == 1
        assert output.stats.newsletters_generated == 1
        assert output.stats.reel_scripts_generated == 1

        # Check evidence files
        evidence_dirs = list((tmp_path / "agents" / "content_composer" / "evidence").iterdir())
        assert len(evidence_dirs) == 1
        files = list(evidence_dirs[0].iterdir())
        filenames = {f.name for f in files}
        assert "composer_output.json" in filenames


class TestT4Config:

    def test_agent_initializes(self):
        agent = ContentComposerAgent("ai-brief-latam", config_dir=_project_root)
        assert agent.agent_config["agent"]["name"] == "content_composer"
