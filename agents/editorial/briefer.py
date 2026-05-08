"""LLM-based brief generation using Claude API.

Takes a scored item and generates a full editorial brief following the
Anexo A template + brand_voice.md rules.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

import anthropic

from agents.editorial.schemas import (
    BriefStatus,
    CTAType,
    EditorialBrief,
    FactCheckItem,
    FormatRecommendation,
)

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
Sos el editor jefe de AI Brief LATAM. Tu tarea es convertir una noticia/item en un \
brief editorial interno completo. Este brief NO se publica directamente — es el documento \
de planificación que el equipo usa para producir contenido.

## Voz de marca (SIEMPRE seguir)
- Smart Brevity: frases cortas, "por qué importa" obligatorio, datos > opiniones
- Español neutro LATAM (NO peninsular, NO extremo mexicano/argentino)
- Anti-hype: nada de "revolutionary" o "game-changing" sin razón
- Cifras siempre con contexto y fuente
- Vocabulario técnico en inglés cuando es estándar (AI, LLM, agent, etc.)

## Hook framework (los 3 requisitos)
1. ATENCIÓN — número inesperado, frase contraintuitiva, claim sorprendente
2. TENSIÓN — vacío de información, problema sin resolver
3. PROMESA — anticipa recompensa concreta

## Formato de respuesta
Respondé SIEMPRE en JSON exacto con esta estructura (sin markdown, sin ```):
{
  "title": "<título working del brief>",
  "que_paso": "<3-5 frases con hechos puros>",
  "por_que_importa": "<2-4 frases — POR QUÉ importa, no qué pasó>",
  "que_cambia": "<antes vs después, 2-4 frases>",
  "quien_gana_pierde": {"gana": ["..."], "pierde": ["..."], "neutro": ["..."]},
  "datos_clave": ["dato 1 con cifra", "dato 2", "dato 3"],
  "angulo_latam": "<cómo conecta con LATAM específicamente>",
  "angulos_posibles": ["ángulo educativo", "ángulo de oportunidad", "ángulo de riesgo"],
  "angulo_elegido": "<cuál se elige y por qué>",
  "formato_recomendado": "<reel | carrusel | post estático | solo newsletter>",
  "hook_tentativo": "<frase corta para slide 1 / primer 3 segundos>",
  "cta_tentativo": "<save | share | comment | newsletter signup>",
  "riesgos": ["riesgo 1", "riesgo 2"],
  "fact_check_items": [{"claim": "...", "status": "pending"}]
}
"""


class BriefGenerator:
    """Generates editorial briefs using Claude API.

    Usage:
        gen = BriefGenerator(api_key="sk-...")
        brief = gen.generate_brief(scored_item_dict)
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-4-20250514",
        max_tokens: int = 1500,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls_made = 0
        self.api_calls_failed = 0

    def generate_brief(self, item_data: dict[str, Any]) -> dict[str, Any]:
        """Generate a full brief for a scored item via Claude API.

        Args:
            item_data: Dict with keys from ScoredItem (title, snippet, url, etc.)

        Returns:
            Dict with brief fields, or {"error": "..."} on failure.
        """
        user_message = (
            f"Generá un brief editorial completo para este item:\n\n"
            f"Título: {item_data['title']}\n"
            f"Fuente: {item_data['source_name']}\n"
            f"URL: {item_data['url']}\n"
            f"Fecha: {item_data.get('published_at', 'N/A')}\n"
            f"Snippet: {item_data.get('snippet', 'N/A')}\n"
            f"Signal Score: {item_data.get('signal_score', 'N/A')}\n"
            f"Justificación del scorer: {item_data.get('justification', 'N/A')}\n"
            f"Ángulo sugerido: {item_data.get('suggested_angle', 'N/A')}\n"
            f"Risk flags: {item_data.get('risk_flags', [])}\n"
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
            logger.warning(f"Failed to parse brief response for '{item_data['title']}': {e}")
            return {"error": f"JSON parse error: {e}"}
        except anthropic.APIError as e:
            self.api_calls_failed += 1
            logger.warning(f"API error generating brief for '{item_data['title']}': {e}")
            return {"error": f"API error: {e}"}
        except Exception as e:
            self.api_calls_failed += 1
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {"error": f"Unexpected: {e}"}

    def build_editorial_brief(
        self, item_data: dict[str, Any], llm_result: dict[str, Any], property_name: str
    ) -> EditorialBrief | None:
        """Convert LLM result into an EditorialBrief object.

        Returns None if LLM result contains an error.
        """
        if "error" in llm_result:
            return None

        now = datetime.now(timezone.utc)
        slug = f"{now.strftime('%Y-%m-%d')}_{self._slugify(llm_result.get('title', item_data['title']))}"

        # Map format string to enum
        format_map = {
            "reel": FormatRecommendation.REEL,
            "carrusel": FormatRecommendation.CAROUSEL,
            "post estático": FormatRecommendation.STATIC_POST,
            "solo newsletter": FormatRecommendation.NEWSLETTER_ONLY,
        }
        formato = format_map.get(
            llm_result.get("formato_recomendado", "carrusel"),
            FormatRecommendation.CAROUSEL,
        )

        # Map CTA string to enum
        cta_map = {
            "save": CTAType.SAVE,
            "share": CTAType.SHARE,
            "comment": CTAType.COMMENT,
            "newsletter signup": CTAType.NEWSLETTER,
        }
        cta = cta_map.get(llm_result.get("cta_tentativo", "save"), CTAType.SAVE)

        # Build fact check items
        fc_items = []
        for fc in llm_result.get("fact_check_items", []):
            if isinstance(fc, dict):
                fc_items.append(FactCheckItem(
                    claim=fc.get("claim", ""),
                    status=fc.get("status", "pending"),
                ))

        return EditorialBrief(
            slug=slug,
            date=now.strftime("%Y-%m-%d"),
            property=property_name,
            status=BriefStatus.DRAFT,
            source_item_id=item_data.get("item_id", item_data.get("id", "")),
            signal_score=item_data.get("signal_score", 0),
            title=llm_result.get("title", item_data["title"]),
            que_paso=llm_result.get("que_paso", ""),
            por_que_importa=llm_result.get("por_que_importa", ""),
            que_cambia=llm_result.get("que_cambia", ""),
            quien_gana_pierde=llm_result.get("quien_gana_pierde", {"gana": [], "pierde": [], "neutro": []}),
            datos_clave=llm_result.get("datos_clave", []),
            angulo_latam=llm_result.get("angulo_latam", ""),
            angulos_posibles=llm_result.get("angulos_posibles", []),
            angulo_elegido=llm_result.get("angulo_elegido", ""),
            formato_recomendado=formato,
            hook_tentativo=llm_result.get("hook_tentativo", ""),
            cta_tentativo=cta,
            fuentes=[item_data.get("url", "")],
            fact_check_items=fc_items,
            riesgos=llm_result.get("riesgos", []),
        )

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to a URL-friendly slug."""
        import re
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_]+", "-", text)
        return text[:50].rstrip("-")
