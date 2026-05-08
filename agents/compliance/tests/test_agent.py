"""Tests for Compliance agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.compliance.agent import ComplianceAgent
from agents.compliance.reviewer import ComplianceReviewer
from agents.compliance.schemas import (
    CheckSeverity,
    ComplianceVerdict,
    ContentComplianceResult,
)


MOCK_LLM_APPROVED = {
    "checks": [
        {"rule": "no_financial_claims", "passed": True, "severity": "info", "detail": "No financial claims found", "suggested_fix": ""},
        {"rule": "no_copy_textual", "passed": True, "severity": "info", "detail": "Content is original", "suggested_fix": ""},
        {"rule": "hashtags_count", "passed": True, "severity": "info", "detail": "7 hashtags, within limit", "suggested_fix": ""},
        {"rule": "no_hype", "passed": True, "severity": "info", "detail": "Tone is sobrio and factual", "suggested_fix": ""},
        {"rule": "cifras_con_contexto", "passed": True, "severity": "info", "detail": "Numbers cited with source", "suggested_fix": ""},
    ],
    "verdict": "approved",
    "summary": "Contenido aprobado. Cumple todas las reglas de plataforma y marca.",
    "blocks": [],
    "warnings": [],
}

MOCK_LLM_BLOCKED = {
    "checks": [
        {"rule": "no_hype", "passed": False, "severity": "block", "detail": "Usa 'revolutionary' sin justificación", "suggested_fix": "Reemplazar con descripción factual"},
        {"rule": "forbidden_patterns", "passed": False, "severity": "block", "detail": "Contiene 'esto va a cambiar el mundo'", "suggested_fix": "Eliminar o reemplazar con claim verificable"},
        {"rule": "cifras_con_contexto", "passed": False, "severity": "warning", "detail": "Cifra de $10B sin fuente", "suggested_fix": "Agregar '(según NYT)' o similar"},
    ],
    "verdict": "blocked",
    "summary": "Contenido bloqueado. Contiene hype injustificado y patrones prohibidos.",
    "blocks": ["Hype: 'revolutionary'", "Patrón prohibido: 'esto va a cambiar el mundo'"],
    "warnings": ["Cifra sin fuente"],
}

MOCK_CONTENT = {
    "brief_slug": "2026-05-08_test",
    "brief_title": "Test Brief",
    "carousel": {
        "caption": {
            "full_text": "OpenAI lanza GPT-5.5-Cyber. IA para ciberseguridad.\n→ Guardá esto\n#IA #LATAM"
        }
    },
    "newsletter": {
        "full_text": "HEADLINE\nIntro text.\nPOR QUÉ IMPORTA: Matters because...\nBOTTOM LINE: Act now."
    },
    "reel_script": {
        "hook": "OpenAI creó algo que no podés usar",
        "body": "GPT-5.5-Cyber es exclusivo.",
        "close": "LATAM necesita esto.",
        "cta": "Guardá esto.",
    },
    "fuentes": ["https://openai.com"],
    "risk_flags": [],
}


def _make_mock_response(content: dict) -> MagicMock:
    mock = MagicMock()
    mock.content = [MagicMock(text=json.dumps(content, ensure_ascii=False))]
    mock.usage = MagicMock(input_tokens=300, output_tokens=500)
    return mock


class TestSchemas:

    def test_verdict_enum(self):
        assert ComplianceVerdict.APPROVED.value == "approved"
        assert ComplianceVerdict.BLOCKED.value == "blocked"

    def test_severity_enum(self):
        assert CheckSeverity.BLOCK.value == "block"


class TestT1ReviewContent:

    def test_review_returns_checks(self):
        reviewer = ComplianceReviewer(api_key="test-key")
        with patch.object(reviewer.client.messages, "create",
                          return_value=_make_mock_response(MOCK_LLM_APPROVED)):
            result = reviewer.review_content("Test content", "carousel_caption", MOCK_CONTENT)

        assert "checks" in result
        assert result["verdict"] == "approved"

    def test_build_approved_result(self):
        reviewer = ComplianceReviewer(api_key="test-key")
        cr = reviewer.build_compliance_result(
            MOCK_LLM_APPROVED, "carousel_caption", "test-slug", "Test Brief"
        )
        assert cr.verdict == ComplianceVerdict.APPROVED
        assert len(cr.checks) == 5
        assert all(c.passed for c in cr.checks)
        assert len(cr.blocks) == 0

    def test_build_blocked_result(self):
        reviewer = ComplianceReviewer(api_key="test-key")
        cr = reviewer.build_compliance_result(
            MOCK_LLM_BLOCKED, "newsletter", "test-slug", "Test Brief"
        )
        assert cr.verdict == ComplianceVerdict.BLOCKED
        assert len(cr.blocks) == 2
        failed = [c for c in cr.checks if not c.passed]
        assert len(failed) == 3
        assert any(c.severity == CheckSeverity.BLOCK for c in failed)


class TestT2Failures:

    def test_api_error_returns_blocked(self):
        reviewer = ComplianceReviewer(api_key="test-key")
        cr = reviewer.build_compliance_result(
            {"error": "API overloaded"}, "caption", "slug", "Title"
        )
        assert cr.verdict == ComplianceVerdict.BLOCKED
        assert "[Error]" in cr.summary

    def test_api_exception_captured(self):
        import anthropic
        reviewer = ComplianceReviewer(api_key="test-key")
        with patch.object(reviewer.client.messages, "create",
                          side_effect=anthropic.APIError(
                              message="timeout", request=MagicMock(), body=None)):
            result = reviewer.review_content("text", "caption", {})
        assert "error" in result


class TestT3EndToEnd:

    def test_agent_reviews_all_content_types(self, tmp_path):
        # Set up fake composer output
        comp_evidence = tmp_path / "agents" / "content_composer" / "evidence" / "test_run"
        comp_evidence.mkdir(parents=True)
        with open(comp_evidence / "composer_output.json", "w") as f:
            json.dump({"run_id": "test_run", "content": [MOCK_CONTENT]}, f)

        config_dir = tmp_path / "agents" / "compliance"
        config_dir.mkdir(parents=True)
        import shutil
        shutil.copy(_project_root / "agents" / "compliance" / "config.yaml",
                     config_dir / "config.yaml")
        (tmp_path / "MASTER_PLAN.md").touch()
        (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=test-key")

        agent = ComplianceAgent("ai-brief-latam", config_dir=tmp_path)

        with patch("agents.compliance.agent.ComplianceReviewer") as MockReviewer:
            mock_reviewer = MagicMock(spec=ComplianceReviewer)
            mock_reviewer.api_calls_made = 3
            mock_reviewer.api_calls_failed = 0
            mock_reviewer.total_input_tokens = 900
            mock_reviewer.total_output_tokens = 1500
            mock_reviewer.review_content.return_value = MOCK_LLM_APPROVED
            real_reviewer = ComplianceReviewer(api_key="test-key")
            mock_reviewer.build_compliance_result = real_reviewer.build_compliance_result
            MockReviewer.return_value = mock_reviewer

            output = agent.run(composer_run_id="test_run")

        # 3 content types reviewed: caption, newsletter, reel
        assert len(output.results) == 3
        assert output.stats.items_checked == 3
        assert output.stats.items_approved == 3


class TestT4Config:

    def test_agent_initializes(self):
        agent = ComplianceAgent("ai-brief-latam", config_dir=_project_root)
        assert agent.agent_config["agent"]["name"] == "compliance"
