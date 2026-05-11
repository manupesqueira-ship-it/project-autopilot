"""LLM-based signal scoring using Claude API.

Evaluates each SourceItem against the Signal Scoring Rubric (MASTER_PLAN Anexo B)
using Claude Sonnet. Returns structured scores with justification.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

from agents.signal_scorer.schemas import (
    Classification,
    ScoredItem,
    SignalBreakdown,
)

logger = logging.getLogger(__name__)

# Rubric included in the system prompt so the LLM scores consistently
_SYSTEM_PROMPT = """\
Sos un editor jefe de AI Brief LATAM, una media property que cubre inteligencia artificial \
para founders, operadores y profesionales de Latinoamérica.

Tu tarea es evaluar un artículo/noticia y asignar un score 0-100 según esta rubrica:

| Categoría | Rango | Criterio |
|---|---|---|
| relevancia_latam | 0-20 | ¿Aplica a la audiencia LATAM? ¿Tiene ángulo regional? |
| novedad | 0-15 | ¿Es noticia nueva o ya circuló ampliamente? |
| urgencia | 0-10 | ¿Tiene ventana de tiempo? ¿Hay que publicar rápido? |
| credibilidad_fuente | 0-15 | ¿La fuente es confiable y verificable? |
| potencial_educativo | 0-10 | ¿Enseña algo útil a la audiencia? |
| potencial_viral | 0-10 | ¿Tiene hook fuerte para Instagram/newsletter? |
| fit_marca | 0-10 | ¿Coincide con la voz anti-hype, sobria, práctica de AI Brief? |
| riesgo | -10 a 0 | Penalty si hay riesgo legal, reputacional o de desinformación |

Voz de la marca: práctica, sobria, anti-humo, técnicamente precisa. NO entusiasta ingenuo. \
SÍ "esto sirve para X, así se usa". Datos > opiniones. Siempre "por qué importa".

Respondé SIEMPRE en JSON exacto con esta estructura (sin markdown, sin ```):
{
  "relevancia_latam": <float 0-20>,
  "novedad": <float 0-15>,
  "urgencia": <float 0-10>,
  "credibilidad_fuente": <float 0-15>,
  "potencial_educativo": <float 0-10>,
  "potencial_viral": <float 0-10>,
  "fit_marca": <float 0-10>,
  "riesgo": <float -10 to 0>,
  "justification": "<2-3 oraciones en español explicando el score>",
  "suggested_angle": "<1 oración: ángulo editorial sugerido para AI Brief LATAM>",
  "risk_flags": ["<flag1>", "<flag2>"] o []
}
"""


class LLMScorer:
    """Scores items using Claude API against the Signal Scoring Rubric.

    Usage:
        scorer = LLMScorer(api_key="sk-...")
        scored = scorer.score_item(source_item_dict)
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-4-20250514",
        max_tokens: int = 500,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls_made = 0
        self.api_calls_failed = 0

    def score_item(self, item_data: dict[str, Any]) -> dict[str, Any]:
        """Score a single item via Claude API.

        Args:
            item_data: Dict with keys: title, snippet, source_name, url, published_at

        Returns:
            Dict with scoring fields (breakdown, justification, etc.)
            On failure, returns a minimal dict with error info.
        """
        user_message = (
            f"Título: {item_data['title']}\n"
            f"Fuente: {item_data['source_name']}\n"
            f"URL: {item_data['url']}\n"
            f"Fecha publicación: {item_data['published_at']}\n"
            f"Snippet: {item_data.get('snippet', 'N/A')}\n"
            f"Tags: {', '.join(item_data.get('tags', []))}\n"
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
            # Strip markdown code fences if present
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

            result = json.loads(raw_text)
            return result

        except json.JSONDecodeError as e:
            self.api_calls_failed += 1
            logger.warning(f"Failed to parse LLM response for '{item_data['title']}': {e}")
            return {"error": f"JSON parse error: {e}"}
        except anthropic.APIError as e:
            self.api_calls_failed += 1
            logger.warning(f"API error scoring '{item_data['title']}': {e}")
            return {"error": f"API error: {e}"}
        except Exception as e:
            self.api_calls_failed += 1
            logger.error(f"Unexpected error scoring '{item_data['title']}': {e}", exc_info=True)
            return {"error": f"Unexpected: {e}"}

    def build_scored_item(
        self, source_item: dict[str, Any], llm_result: dict[str, Any]
    ) -> ScoredItem:
        """Convert a source item + LLM result into a ScoredItem.

        If the LLM result contains an error, falls back to the preliminary score.
        """
        if "error" in llm_result:
            # Fallback: use preliminary score
            score = source_item.get("preliminary_score", 0.0)
            return ScoredItem(
                item_id=source_item["id"],
                title=source_item["title"],
                url=str(source_item["url"]),
                source_name=source_item["source_name"],
                snippet=source_item.get("snippet", ""),
                published_at=source_item["published_at"],
                preliminary_score=source_item.get("preliminary_score", 0.0),
                signal_score=score,
                classification=ScoredItem.classify(score),
                justification=f"[Fallback] LLM scoring failed: {llm_result['error']}",
            )

        breakdown = SignalBreakdown(
            relevancia_latam=float(llm_result.get("relevancia_latam", 0)),
            novedad=float(llm_result.get("novedad", 0)),
            urgencia=float(llm_result.get("urgencia", 0)),
            credibilidad_fuente=float(llm_result.get("credibilidad_fuente", 0)),
            potencial_educativo=float(llm_result.get("potencial_educativo", 0)),
            potencial_viral=float(llm_result.get("potencial_viral", 0)),
            fit_marca=float(llm_result.get("fit_marca", 0)),
            riesgo=float(llm_result.get("riesgo", 0)),
        )
        score = breakdown.total

        return ScoredItem(
            item_id=source_item["id"],
            title=source_item["title"],
            url=str(source_item["url"]),
            source_name=source_item["source_name"],
            snippet=source_item.get("snippet", ""),
            published_at=source_item["published_at"],
            preliminary_score=source_item.get("preliminary_score", 0.0),
            signal_score=round(score, 2),
            signal_breakdown=breakdown,
            classification=ScoredItem.classify(score),
            justification=llm_result.get("justification", ""),
            suggested_angle=llm_result.get("suggested_angle", ""),
            risk_flags=llm_result.get("risk_flags", []),
        )
