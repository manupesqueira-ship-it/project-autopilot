"""LLM-based content generation using Claude API.

Takes a fact-checked editorial brief and generates publishable content:
Instagram carousel, newsletter section, and optional reel script.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

from agents.content_composer.schemas import (
    CarouselContent,
    CarouselSlide,
    ComposedContent,
    InstagramCaption,
    NewsletterSection,
    ReelScript,
)

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
Sos el content creator de AI Brief LATAM. Generás contenido publicable a partir \
de briefs editoriales ya verificados.

## Voz de marca (OBLIGATORIO)
- Smart Brevity: frases cortas, datos > opiniones
- Español neutro LATAM (NO peninsular, NO extremo MX/AR)
- Anti-hype: nada de "revolutionary" sin razón
- Cifras con contexto y fuente
- Técnico en inglés cuando es estándar (AI, LLM, agent, etc.)
- SÍ usar: ustedes, nuestro, está bien, listo, claro, dale
- NO usar: vosotros, chido, boludo, vale

## Formato de Instagram caption
- Hook en primeros 125 chars (lo visible antes de "more")
- Total bajo 150 chars + hashtags aparte
- 1-2 emojis estratégicos máx. Permitidos: ⚡ 🏦 💼 📊
- 5-10 hashtags niche (NO 30 broad)

## Formato de carousel (5-7 slides)
- Slide 1: HOOK (cifra grande / claim sorprendente)
- Slides 2-5: datos clave, antes/después, quién gana/pierde
- Slide penúltimo: ángulo LATAM
- Slide final: CTA + branding

## Formato de newsletter (250-400 palabras, Smart Brevity)
- Headline punchy
- "POR QUÉ IMPORTA" obligatorio
- "LO QUE PASÓ" con flechas →
- "QUÉ SIGNIFICA PARA LATAM" con acciones por audiencia
- "BOTTOM LINE" cierre accionable

## Formato de reel script (25-35 segundos)
- Hook 0-3s: pattern interrupt brutal
- Body 3-22s: hechos con jump cuts
- Close 22-30s: ángulo LATAM + CTA específico
- On-screen text para viewing sin sonido

## Respuesta JSON (sin markdown, sin ```):
{
  "carousel": {
    "slides": [
      {"slide_number": 1, "headline": "...", "body": "...", "visual_direction": "..."},
      ...
    ],
    "caption": {
      "hook": "<primeros 125 chars>",
      "body": "<1-2 frases>",
      "cta": "<CTA específico>",
      "hashtags": ["#IA", "#LATAM", "..."]
    }
  },
  "newsletter": {
    "headline": "<HEADLINE PUNCHY>",
    "intro": "<1-2 frases setup>",
    "por_que_importa": "<por qué importa>",
    "lo_que_paso": ["→ punto 1", "→ punto 2", "→ punto 3"],
    "que_significa_latam": "<ángulo LATAM con acciones>",
    "bottom_line": "<conclusión accionable>",
    "fuentes": ["fuente 1"]
  },
  "reel_script": {
    "hook": "<0-3s text>",
    "body": "<3-22s script>",
    "por_que_importa": "<axioma central>",
    "close": "<22-30s LATAM + CTA>",
    "cta": "<CTA text>",
    "estimated_duration_seconds": 30,
    "on_screen_text": ["text overlay 1", "text overlay 2", "..."]
  }
}
"""


class ContentGenerator:
    """Generates publishable content from editorial briefs via Claude API."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-4-20250514",
        max_tokens: int = 2500,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls_made = 0
        self.api_calls_failed = 0

    def compose(self, brief_data: dict[str, Any]) -> dict[str, Any]:
        """Generate all content pieces from a brief.

        Args:
            brief_data: Dict from EditorialBrief.

        Returns:
            Dict with carousel, newsletter, reel_script sections.
        """
        user_message = (
            f"Generá contenido publicable para este brief:\n\n"
            f"Título: {brief_data.get('title', 'N/A')}\n"
            f"Qué pasó: {brief_data.get('que_paso', 'N/A')}\n"
            f"Por qué importa: {brief_data.get('por_que_importa', 'N/A')}\n"
            f"Qué cambia: {brief_data.get('que_cambia', 'N/A')}\n"
            f"Quién gana/pierde: {brief_data.get('quien_gana_pierde', {})}\n"
            f"Datos clave: {brief_data.get('datos_clave', [])}\n"
            f"Ángulo LATAM: {brief_data.get('angulo_latam', 'N/A')}\n"
            f"Ángulo elegido: {brief_data.get('angulo_elegido', 'N/A')}\n"
            f"Hook tentativo: {brief_data.get('hook_tentativo', 'N/A')}\n"
            f"Formato recomendado: {brief_data.get('formato_recomendado', 'carrusel')}\n"
            f"CTA tentativo: {brief_data.get('cta_tentativo', 'save')}\n"
            f"Fuentes: {brief_data.get('fuentes', [])}\n"
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

    def build_composed_content(
        self, brief_data: dict[str, Any], llm_result: dict[str, Any]
    ) -> ComposedContent | None:
        """Convert LLM result into ComposedContent. Returns None on error."""
        if "error" in llm_result:
            return None

        # Carousel
        carousel_data = llm_result.get("carousel", {})
        slides = [
            CarouselSlide(
                slide_number=s.get("slide_number", i + 1),
                headline=s.get("headline", ""),
                body=s.get("body", ""),
                visual_direction=s.get("visual_direction", ""),
            )
            for i, s in enumerate(carousel_data.get("slides", []))
        ]
        caption_data = carousel_data.get("caption", {})
        hashtags = caption_data.get("hashtags", [])
        hook = caption_data.get("hook", "")
        body = caption_data.get("body", "")
        cta = caption_data.get("cta", "")
        full_caption = f"{hook}\n\n{body}\n\n→ {cta}\n\n{' '.join(hashtags)}".strip()

        carousel = CarouselContent(
            slides=slides,
            caption=InstagramCaption(
                hook=hook, body=body, cta=cta,
                hashtags=hashtags, full_text=full_caption,
            ),
            slide_count=len(slides),
        )

        # Newsletter
        nl_data = llm_result.get("newsletter", {})
        lo_que_paso = nl_data.get("lo_que_paso", [])
        fuentes = nl_data.get("fuentes", brief_data.get("fuentes", []))
        nl_full = (
            f"{nl_data.get('headline', '')}\n\n"
            f"{nl_data.get('intro', '')}\n\n"
            f"POR QUÉ IMPORTA: {nl_data.get('por_que_importa', '')}\n\n"
            f"LO QUE PASÓ:\n" + "\n".join(lo_que_paso) + "\n\n"
            f"QUÉ SIGNIFICA PARA LATAM:\n{nl_data.get('que_significa_latam', '')}\n\n"
            f"BOTTOM LINE: {nl_data.get('bottom_line', '')}\n\n"
            f"Fuentes: {', '.join(fuentes)}"
        )
        newsletter = NewsletterSection(
            headline=nl_data.get("headline", ""),
            intro=nl_data.get("intro", ""),
            por_que_importa=nl_data.get("por_que_importa", ""),
            lo_que_paso=lo_que_paso,
            que_significa_latam=nl_data.get("que_significa_latam", ""),
            bottom_line=nl_data.get("bottom_line", ""),
            fuentes=fuentes,
            full_text=nl_full,
        )

        # Reel script (optional)
        reel_script = None
        rs_data = llm_result.get("reel_script")
        if rs_data and isinstance(rs_data, dict):
            reel_script = ReelScript(
                hook=rs_data.get("hook", ""),
                body=rs_data.get("body", ""),
                por_que_importa=rs_data.get("por_que_importa", ""),
                close=rs_data.get("close", ""),
                cta=rs_data.get("cta", ""),
                estimated_duration_seconds=rs_data.get("estimated_duration_seconds", 30),
                on_screen_text=rs_data.get("on_screen_text", []),
            )

        return ComposedContent(
            brief_slug=brief_data.get("slug", "unknown"),
            brief_title=brief_data.get("title", "unknown"),
            carousel=carousel,
            newsletter=newsletter,
            reel_script=reel_script,
        )
