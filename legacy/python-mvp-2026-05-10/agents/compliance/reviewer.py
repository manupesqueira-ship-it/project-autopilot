"""LLM-based compliance review using Claude API.

Reviews composed content against:
- Meta/Instagram platform rules (Anexo D)
- Property-specific compliance rules (compliance_rules.yaml)
- Property risk profile (risk_profile.yaml)
- Brand voice forbidden patterns (brand_voice.md Hard NO's)
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

from agents.compliance.schemas import (
    CheckSeverity,
    ComplianceCheck,
    ComplianceVerdict,
    ContentComplianceResult,
)

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
Sos el compliance officer de AI Brief LATAM. Revisás contenido antes de publicar \
en Instagram y newsletter para asegurar cumplimiento de reglas de plataforma y marca.

## Checklist Instagram/Meta (Anexo D)
1. Caption no contiene claims financieros sin disclaimer
2. No hay copia textual de otra fuente (transformación sustancial requerida)
3. Hashtags son <30 y relevantes
4. No se prometen resultados
5. Si reseña herramienta: claim verificable
6. No hay info personal de terceros sin consentimiento
7. No hay enlace a contenido prohibido por Meta

## Reglas de marca AI Brief LATAM
8. NO hype injustificado ("revolutionary", "game-changing" sin razón)
9. NO predicciones irresponsables ("va a destruir X industria")
10. NO listicles sin sustancia
11. NO más de 1 emoji por frase
12. Español neutro LATAM (no peninsular, no extremo regional)
13. Cifras siempre con contexto y fuente
14. "Por qué importa" presente en newsletter
15. Forbidden patterns: "esto va a cambiar el mundo", "el fin de [industria]", "reemplaza completamente a"

## Severidad
- block: DEBE corregirse antes de publicar
- warning: DEBERÍA corregirse, no bloquea
- info: observación, sin acción requerida

## Respuesta JSON (sin markdown, sin ```):
{
  "checks": [
    {
      "rule": "<nombre de la regla>",
      "passed": true/false,
      "severity": "block | warning | info",
      "detail": "<explicación>",
      "suggested_fix": "<cómo arreglar, o '' si passed>"
    }
  ],
  "verdict": "approved | approved_with_warnings | blocked",
  "summary": "<1-2 oraciones resumen en español>",
  "blocks": ["<issue bloqueante 1>"],
  "warnings": ["<warning 1>"]
}
"""


class ComplianceReviewer:
    """Reviews content for compliance using Claude API."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-4-20250514",
        max_tokens: int = 1200,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls_made = 0
        self.api_calls_failed = 0

    def review_content(
        self, content_text: str, content_type: str, brief_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Review a single content piece for compliance.

        Args:
            content_text: The actual text to review (caption, newsletter, etc.)
            content_type: "carousel_caption" | "newsletter" | "reel_script"
            brief_data: Dict with brief context (title, fuentes, risk_flags, etc.)
        """
        user_message = (
            f"Revisá este contenido para compliance:\n\n"
            f"Tipo: {content_type}\n"
            f"Brief: {brief_data.get('title', 'N/A')}\n"
            f"Fuentes citadas: {brief_data.get('fuentes', [])}\n"
            f"Risk flags previos: {brief_data.get('risk_flags', [])}\n\n"
            f"--- CONTENIDO A REVISAR ---\n{content_text}\n--- FIN ---"
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
            logger.warning(f"JSON parse error: {e}")
            return {"error": f"JSON parse error: {e}"}
        except anthropic.APIError as e:
            self.api_calls_failed += 1
            logger.warning(f"API error: {e}")
            return {"error": f"API error: {e}"}
        except Exception as e:
            self.api_calls_failed += 1
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {"error": f"Unexpected: {e}"}

    def build_compliance_result(
        self,
        llm_result: dict[str, Any],
        content_type: str,
        brief_slug: str,
        brief_title: str,
    ) -> ContentComplianceResult:
        """Convert LLM result into ContentComplianceResult."""
        if "error" in llm_result:
            return ContentComplianceResult(
                content_type=content_type,
                brief_slug=brief_slug,
                brief_title=brief_title,
                verdict=ComplianceVerdict.BLOCKED,
                summary=f"[Error] Compliance review failed: {llm_result['error']}",
                blocks=["Compliance review could not be completed"],
            )

        checks = []
        for c in llm_result.get("checks", []):
            if not isinstance(c, dict):
                continue
            try:
                severity = CheckSeverity(c.get("severity", "info"))
            except ValueError:
                severity = CheckSeverity.INFO
            checks.append(ComplianceCheck(
                rule=c.get("rule", ""),
                passed=c.get("passed", True),
                severity=severity,
                detail=c.get("detail", ""),
                suggested_fix=c.get("suggested_fix", ""),
            ))

        try:
            verdict = ComplianceVerdict(llm_result.get("verdict", "blocked"))
        except ValueError:
            verdict = ComplianceVerdict.BLOCKED

        return ContentComplianceResult(
            content_type=content_type,
            brief_slug=brief_slug,
            brief_title=brief_title,
            verdict=verdict,
            checks=checks,
            summary=llm_result.get("summary", ""),
            blocks=llm_result.get("blocks", []),
            warnings=llm_result.get("warnings", []),
        )
