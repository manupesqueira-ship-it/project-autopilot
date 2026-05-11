"""Visual generation — creates carousel slide images from text content.

Generates 1080x1080 PNG images with:
- Dark background (brand aesthetic)
- Bold headline text (white)
- Body text (light gray)
- Accent color for emphasis
- Slide number indicator

Usage:
    from agents.content_composer.visual import CarouselRenderer
    renderer = CarouselRenderer()
    paths = renderer.render_carousel(slides_data, output_dir)
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


# Brand colors
_BG_COLOR = (15, 15, 20)          # Near-black
_HEADLINE_COLOR = (255, 255, 255)  # White
_BODY_COLOR = (200, 200, 210)      # Light gray
_ACCENT_COLOR = (99, 102, 241)     # Indigo/purple accent
_SLIDE_NUM_COLOR = (80, 80, 90)    # Dim gray for slide indicator
_CTA_COLOR = (34, 197, 94)         # Green for CTA/save

# Layout
_SIZE = (1080, 1080)
_PADDING = 80
_HEADLINE_Y = 200
_BODY_Y = 500
_MAX_HEADLINE_CHARS = 25
_MAX_BODY_CHARS = 38


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Get a font, falling back to default if system fonts aren't available."""
    font_names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


class CarouselRenderer:
    """Renders carousel slides as 1080x1080 PNG images."""

    def __init__(
        self,
        bg_color: tuple = _BG_COLOR,
        headline_color: tuple = _HEADLINE_COLOR,
        body_color: tuple = _BODY_COLOR,
        accent_color: tuple = _ACCENT_COLOR,
    ):
        self.bg_color = bg_color
        self.headline_color = headline_color
        self.body_color = body_color
        self.accent_color = accent_color

    def render_carousel(
        self, slides: list[dict[str, Any]], output_dir: Path
    ) -> list[Path]:
        """Render all slides as PNGs.

        Args:
            slides: List of dicts with slide_number, headline, body, visual_direction
            output_dir: Directory to save PNGs

        Returns:
            List of paths to generated PNG files.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        total = len(slides)

        for slide in slides:
            num = slide.get("slide_number", 1)
            headline = slide.get("headline", "")
            body = slide.get("body", "")
            is_last = num == total

            img = self._render_slide(
                headline=headline,
                body=body,
                slide_num=num,
                total_slides=total,
                is_cta=is_last,
            )

            path = output_dir / f"slide_{num:02d}.png"
            img.save(path, "PNG")
            paths.append(path)

        return paths

    def _render_slide(
        self,
        headline: str,
        body: str,
        slide_num: int,
        total_slides: int,
        is_cta: bool = False,
    ) -> Image.Image:
        """Render a single slide."""
        img = Image.new("RGB", _SIZE, self.bg_color)
        draw = ImageDraw.Draw(img)

        # Accent bar at top
        draw.rectangle([(0, 0), (_SIZE[0], 6)], fill=self.accent_color)

        # Slide number indicator (top right)
        font_small = _get_font(28)
        num_text = f"{slide_num}/{total_slides}"
        draw.text(
            (_SIZE[0] - _PADDING, 30),
            num_text,
            fill=_SLIDE_NUM_COLOR,
            font=font_small,
            anchor="ra",
        )

        # Headline
        font_headline = _get_font(52, bold=True)
        headline_wrapped = textwrap.fill(headline, width=_MAX_HEADLINE_CHARS)
        color = _CTA_COLOR if is_cta else self.headline_color
        draw.multiline_text(
            (_PADDING, _HEADLINE_Y),
            headline_wrapped,
            fill=color,
            font=font_headline,
            spacing=16,
        )

        # Body — respect original line breaks, then wrap each line
        if body:
            font_body = _get_font(34)
            lines = body.split("\n")
            wrapped_lines = []
            for line in lines:
                line = line.strip()
                if line:
                    wrapped_lines.append(textwrap.fill(line, width=_MAX_BODY_CHARS))
            body_text = "\n".join(wrapped_lines)
            draw.multiline_text(
                (_PADDING, _BODY_Y),
                body_text,
                fill=self.body_color,
                font=font_body,
                spacing=14,
            )

        # Bottom accent bar
        draw.rectangle([(0, _SIZE[1] - 4), (_SIZE[0], _SIZE[1])], fill=self.accent_color)

        # Brand watermark (bottom left)
        font_brand = _get_font(22)
        draw.text(
            (_PADDING, _SIZE[1] - 50),
            "@breiflatam",
            fill=_SLIDE_NUM_COLOR,
            font=font_brand,
        )

        return img


def render_from_compose_output(compose_output_path: Path, output_dir: Path) -> dict[str, list[Path]]:
    """Render all carousels from a composer output JSON.

    Args:
        compose_output_path: Path to composer_output.json
        output_dir: Base directory for rendered images

    Returns:
        Dict mapping brief_slug to list of generated PNG paths.
    """
    import json

    with open(compose_output_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    renderer = CarouselRenderer()
    results = {}

    for content in data.get("content", []):
        slug = content.get("brief_slug", "unknown")
        slides = content.get("carousel", {}).get("slides", [])
        if not slides:
            continue

        carousel_dir = output_dir / slug
        paths = renderer.render_carousel(slides, carousel_dir)
        results[slug] = paths

    return results
