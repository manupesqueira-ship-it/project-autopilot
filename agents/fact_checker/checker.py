"""LLM-based fact-checking using Claude API.

Takes claims from editorial briefs and evaluates their verifiability,
accuracy, and risk level. Does NOT browse the web — uses the LLM's knowledge
plus the source URL context to assess claims.

Future: integrate Perplexity/Tavily for real-time web verification.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

from agents.fact_checker.schemas import (
    BriefVerdict,
    FactCheckResult,
    Severity,
    VerificationStatus,
    VerifiedClaim,
)

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
Sos un fact-checker profesional para AI Brief LATAM. Tu trabajo es verificar claims \
de briefs editoriales antes de publicación.

Para CADA claim que recibas, evaluá:
1. ¿Es verificable? ¿Tiene fuente citada?
2. ¿Es preciso según tu conocimiento? (corte mayo 2025)
3. ¿Hay riesgo de desinformación si se publica así?
4. ¿Necesita un qualifier ("reportado por...", "según...", "estimado")?

## Reglas de AI Brief LATAM:
- SIEMPRE distinguir "anunciado" vs "lanzado" vs "rumor"
- NUNCA claims sin fuente verificable
- Cifras SIEMPRE con contexto ("$1.5B reportado por WSJ")
- Si no podés verificar, decilo explícitamente

## Niveles de severidad:
- critical: debe verificarse antes de publicar (cifras de funding, fechas de lanzamiento, claims de capacidades)
- high: debería verificarse o agregar qualifier
- medium: verificar si es posible, no bloquea
- low: nice-to-have, no bloquea

## Formato de respuesta
Respondé SIEMPRE en JSON exacto (sin markdown, sin ```):
{
  "claims": [
    {
      "claim": "<el claim original>",
      "status": "<verified | unverified | disputed | partially_verified | unable_to_verify>",
      "severity": "<critical | high | medium | low>",
      "source_url": "<URL de verificación si la tenés, o '' si no>",
      "source_name": "<nombre de la fuente de verificación>",
      "notes": "<explicación de por qué este status>",
      "suggested_rewrite": "<frase más segura si el claim es disputado/no verificado, o '' si OK>"
    }
  ],
  "verdict": "<pass | pass_with_edits | needs_review | fail>",
  "summary": "<1-3 oraciones resumen en español>",
  "recommended_edits": ["<edición 1>", "<edición 2>"],
  "critical_issues": ["<issue 1>"] o []
}
"""


class ClaimChecker:
    """Verifies claims from editorial briefs using Claude API.

    Usage:
        checker = ClaimChecker(api_key="sk-...")
        result = checker.check_brief(brief_data)
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1200,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls_made = 0
        self.api_calls_failed = 0

    def check_brief(self, brief_data: dict[str, Any]) -> dict[str, Any]:
        """Fact-check all claims in a brief.

        Args:
            brief_data: Dict from EditorialBrief with que_paso, datos_clave,
                       fact_check_items, fuentes, etc.

        Returns:
            Dict with verified claims and verdict, or {"error": "..."}.
        """
        # Build the claims list from the brief
        claims_text = self._extract_claims_text(brief_data)

        user_message = (
            f"Brief: {brief_data.get('title', 'N/A')}\n"
            f"Fuentes citadas: {brief_data.get('fuentes', [])}\n\n"
            f"Claims a verificar:\n{claims_text}\n\n"
            f"Contexto adicional del brief:\n"
            f"- Qué pasó: {brief_data.get('que_paso', 'N/A')}\n"
            f"- Datos clave: {brief_data.get('datos_clave', [])}\n"
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            self.api_calls_made += 1
            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens

            raw_text = response.content[0].text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

            return json.loads(raw_text)

        except json.JSONDecodeError as e:
            self.api_calls_failed += 1
            logger.warning(f"Failed to parse fact-check response: {e}")
            return {"error": f"JSON parse error: {e}"}
        except anthropic.APIError as e:
            self.api_calls_failed += 1
            logger.warning(f"API error during fact-check: {e}")
            return {"error": f"API error: {e}"}
        except Exception as e:
            self.api_calls_failed += 1
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {"error": f"Unexpected: {e}"}

    def build_fact_check_result(
        self, brief_data: dict[str, Any], llm_result: dict[str, Any]
    ) -> FactCheckResult:
        """Convert LLM result into a FactCheckResult."""
        if "error" in llm_result:
            return FactCheckResult(
                brief_slug=brief_data.get("slug", "unknown"),
                brief_title=brief_data.get("title", "unknown"),
                verdict=BriefVerdict.NEEDS_REVIEW,
                summary=f"[Error] Fact-check failed: {llm_result['error']}",
            )

        claims = []
        for c in llm_result.get("claims", []):
            if not isinstance(c, dict):
                continue
            try:
                status = VerificationStatus(c.get("status", "unable_to_verify"))
            except ValueError:
                status = VerificationStatus.UNABLE_TO_VERIFY
            try:
                severity = Severity(c.get("severity", "medium"))
            except ValueError:
                severity = Severity.MEDIUM

            claims.append(VerifiedClaim(
                claim=c.get("claim", ""),
                status=status,
                severity=severity,
                source_url=c.get("source_url", ""),
                source_name=c.get("source_name", ""),
                notes=c.get("notes", ""),
                suggested_rewrite=c.get("suggested_rewrite", ""),
            ))

        try:
            verdict = BriefVerdict(llm_result.get("verdict", "needs_review"))
        except ValueError:
            verdict = BriefVerdict.NEEDS_REVIEW

        return FactCheckResult(
            brief_slug=brief_data.get("slug", "unknown"),
            brief_title=brief_data.get("title", "unknown"),
            verdict=verdict,
            claims=claims,
            summary=llm_result.get("summary", ""),
            recommended_edits=llm_result.get("recommended_edits", []),
            critical_issues=llm_result.get("critical_issues", []),
        )

    def _extract_claims_text(self, brief_data: dict[str, Any]) -> str:
        """Build a numbered list of claims to verify from the brief."""
        claims = []

        # From explicit fact_check_items
        for fc in brief_data.get("fact_check_items", []):
            if isinstance(fc, dict) and fc.get("claim"):
                claims.append(fc["claim"])

        # From datos_clave (these are often verifiable claims with numbers)
        for dato in brief_data.get("datos_clave", []):
            if dato and dato not in claims:
                claims.append(dato)

        if not claims:
            # Fall back to extracting from que_paso
            que_paso = brief_data.get("que_paso", "")
            if que_paso:
                claims.append(f"[del brief] {que_paso[:300]}")

        return "\n".join(f"{i+1}. {c}" for i, c in enumerate(claims))
