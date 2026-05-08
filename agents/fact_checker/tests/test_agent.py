"""Tests for Fact-Checker agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.fact_checker.agent import FactCheckerAgent
from agents.fact_checker.checker import ClaimChecker
from agents.fact_checker.schemas import (
    BriefVerdict,
    FactCheckResult,
    Severity,
    VerificationStatus,
)


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

MOCK_BRIEF = {
    "slug": "2026-05-08_chatgpt-ads",
    "title": "ChatGPT tendrá publicidad",
    "que_paso": "OpenAI anunció que probará anuncios en ChatGPT free tier.",
    "datos_clave": [
        "ChatGPT tiene 400M+ usuarios activos semanales",
        "LATAM representa ~15% de usuarios globales",
        "OpenAI gastó $8.5B en 2025",
    ],
    "fact_check_items": [
        {"claim": "400M+ usuarios activos semanales", "status": "pending"},
        {"claim": "LATAM ~15% de usuarios globales", "status": "pending"},
    ],
    "fuentes": ["https://openai.com/index/testing-ads-in-chatgpt"],
}

MOCK_LLM_PASS = {
    "claims": [
        {
            "claim": "400M+ usuarios activos semanales",
            "status": "verified",
            "severity": "critical",
            "source_url": "https://openai.com/blog/chatgpt-weekly-users",
            "source_name": "OpenAI official blog",
            "notes": "Confirmado por OpenAI en mayo 2026.",
            "suggested_rewrite": "",
        },
        {
            "claim": "LATAM ~15% de usuarios globales",
            "status": "unverified",
            "severity": "high",
            "source_url": "",
            "source_name": "",
            "notes": "No hay fuente pública para este dato. Es estimación.",
            "suggested_rewrite": "LATAM representa una proporción significativa de usuarios (estimado ~15%, sin fuente oficial)",
        },
        {
            "claim": "OpenAI gastó $8.5B en 2025",
            "status": "verified",
            "severity": "critical",
            "source_url": "https://www.nytimes.com/2025/openai-spending",
            "source_name": "NYT reporting",
            "notes": "Reportado por NYT, no confirmado oficialmente por OpenAI.",
            "suggested_rewrite": "OpenAI gastó $8.5B en 2025, según reportes de NYT",
        },
    ],
    "verdict": "pass_with_edits",
    "summary": "2 de 3 claims verificados. El dato de LATAM 15% no tiene fuente oficial y debe calificarse como estimación.",
    "recommended_edits": [
        "Agregar 'estimado' al dato de 15% LATAM",
        "Agregar 'según reportes de NYT' al dato de $8.5B",
    ],
    "critical_issues": [],
}

MOCK_LLM_FAIL = {
    "claims": [
        {
            "claim": "OpenAI confirma que los ads saldrán en junio 2026",
            "status": "disputed",
            "severity": "critical",
            "source_url": "",
            "source_name": "",
            "notes": "OpenAI solo dijo 'testing', no confirmó fecha de lanzamiento.",
            "suggested_rewrite": "OpenAI comenzó a probar anuncios, sin fecha confirmada de lanzamiento general.",
        },
    ],
    "verdict": "fail",
    "summary": "Claim crítico disputado. El brief afirma fecha de lanzamiento no confirmada.",
    "recommended_edits": ["Remover fecha de junio, reemplazar con 'fase de prueba sin fecha definida'"],
    "critical_issues": ["Afirmación de fecha no respaldada por fuente"],
}


def _make_mock_response(content: dict) -> MagicMock:
    mock = MagicMock()
    mock.content = [MagicMock(text=json.dumps(content, ensure_ascii=False))]
    mock.usage = MagicMock(input_tokens=300, output_tokens=600)
    return mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSchemas:

    def test_verdict_enum(self):
        assert BriefVerdict.PASS.value == "pass"
        assert BriefVerdict.FAIL.value == "fail"

    def test_severity_enum(self):
        assert Severity.CRITICAL.value == "critical"


class TestT1CheckSingleBrief:

    def test_check_returns_valid_result(self):
        checker = ClaimChecker(api_key="test-key")
        with patch.object(checker.client.messages, "create",
                          return_value=_make_mock_response(MOCK_LLM_PASS)):
            result = checker.check_brief(MOCK_BRIEF)

        assert "claims" in result
        assert "verdict" in result
        assert len(result["claims"]) == 3

    def test_build_result_pass_with_edits(self):
        checker = ClaimChecker(api_key="test-key")
        fc_result = checker.build_fact_check_result(MOCK_BRIEF, MOCK_LLM_PASS)

        assert fc_result.verdict == BriefVerdict.PASS_WITH_EDITS
        assert len(fc_result.claims) == 3
        assert fc_result.claims[0].status == VerificationStatus.VERIFIED
        assert fc_result.claims[1].status == VerificationStatus.UNVERIFIED
        assert fc_result.claims[1].suggested_rewrite != ""
        assert len(fc_result.recommended_edits) == 2

    def test_build_result_fail(self):
        checker = ClaimChecker(api_key="test-key")
        fc_result = checker.build_fact_check_result(MOCK_BRIEF, MOCK_LLM_FAIL)

        assert fc_result.verdict == BriefVerdict.FAIL
        assert fc_result.claims[0].status == VerificationStatus.DISPUTED
        assert len(fc_result.critical_issues) == 1


class TestT2APIFailure:

    def test_api_error_returns_needs_review(self):
        checker = ClaimChecker(api_key="test-key")
        fc_result = checker.build_fact_check_result(
            MOCK_BRIEF, {"error": "API overloaded"}
        )
        assert fc_result.verdict == BriefVerdict.NEEDS_REVIEW
        assert "[Error]" in fc_result.summary

    def test_api_exception_captured(self):
        import anthropic
        checker = ClaimChecker(api_key="test-key")
        with patch.object(checker.client.messages, "create",
                          side_effect=anthropic.APIError(
                              message="timeout", request=MagicMock(), body=None)):
            result = checker.check_brief(MOCK_BRIEF)

        assert "error" in result
        assert checker.api_calls_failed == 1


class TestT3EndToEnd:

    def test_agent_checks_briefs(self, tmp_path):
        # Set up fake editorial output
        ed_evidence = tmp_path / "agents" / "editorial" / "evidence" / "test_run"
        ed_evidence.mkdir(parents=True)
        with open(ed_evidence / "editorial_output.json", "w") as f:
            json.dump({"run_id": "test_run", "briefs": [MOCK_BRIEF]}, f)

        # Config
        config_dir = tmp_path / "agents" / "fact_checker"
        config_dir.mkdir(parents=True)
        import shutil
        shutil.copy(_project_root / "agents" / "fact_checker" / "config.yaml",
                     config_dir / "config.yaml")
        (tmp_path / "MASTER_PLAN.md").touch()
        (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=test-key")

        agent = FactCheckerAgent("ai-brief-latam", config_dir=tmp_path)

        with patch("agents.fact_checker.agent.ClaimChecker") as MockChecker:
            mock_checker = MagicMock(spec=ClaimChecker)
            mock_checker.api_calls_made = 1
            mock_checker.api_calls_failed = 0
            mock_checker.total_input_tokens = 300
            mock_checker.total_output_tokens = 600
            mock_checker.check_brief.return_value = MOCK_LLM_PASS

            real_checker = ClaimChecker(api_key="test-key")
            mock_checker.build_fact_check_result = real_checker.build_fact_check_result
            MockChecker.return_value = mock_checker

            output = agent.run(editorial_run_id="test_run")

        assert len(output.results) == 1
        assert output.results[0].verdict == BriefVerdict.PASS_WITH_EDITS
        assert output.stats.briefs_checked == 1
        assert output.stats.claims_verified == 2


class TestT4Config:

    def test_agent_initializes(self):
        agent = FactCheckerAgent("ai-brief-latam", config_dir=_project_root)
        assert agent.agent_config["agent"]["name"] == "fact_checker"
