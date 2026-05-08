"""Content Composer Agent — generates publishable content from briefs.

Reads Editorial agent output (fact-checked briefs) and generates:
- Instagram carousel (slides + caption + hashtags)
- Newsletter section (Smart Brevity format)
- Reel script (25-35s with on-screen text)

Usage:
    autopilot compose --property ai-brief-latam
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from agents.content_composer.composer import ContentGenerator
from agents.content_composer.schemas import (
    ComposedContent,
    ComposerOutput,
    ComposerStats,
)

logger = logging.getLogger(__name__)


class ContentComposerAgent:
    """Generates publishable content from editorial briefs."""

    def __init__(self, property_name: str, config_dir: Path | None = None):
        self.property_name = property_name
        self.config_dir = config_dir or self._find_project_root()
        load_dotenv(self.config_dir / ".env")
        self.agent_config = self._load_agent_config()
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set")

    def run(self, editorial_run_id: str | None = None) -> ComposerOutput:
        """Generate content for all briefs in an editorial run."""
        run_id = self._generate_run_id()

        editorial_data = self._load_editorial_output(editorial_run_id)
        editorial_run = editorial_data.get("run_id", "unknown")
        briefs = editorial_data.get("briefs", [])
        logger.info(f"Composing content for {len(briefs)} briefs from '{editorial_run}'")

        model = self.agent_config.get("llm", {}).get("model", "claude-opus-4-20250514")
        max_tokens = self.agent_config.get("llm", {}).get("max_tokens", 2500)
        generator = ContentGenerator(api_key=self.api_key, model=model, max_tokens=max_tokens)

        content_list: list[ComposedContent] = []
        errors: list[str] = []

        for i, brief in enumerate(briefs):
            logger.debug(f"Composing [{i+1}/{len(briefs)}]: {brief.get('title', '?')[:60]}")
            llm_result = generator.compose(brief)
            composed = generator.build_composed_content(brief, llm_result)

            if composed:
                content_list.append(composed)
            else:
                errors.append(f"{brief.get('title', '?')[:60]}: {llm_result.get('error', 'unknown')}")

        stats = ComposerStats(
            items_processed=len(briefs),
            carousels_generated=sum(1 for c in content_list if c.carousel.slide_count > 0),
            newsletters_generated=sum(1 for c in content_list if c.newsletter.headline),
            reel_scripts_generated=sum(1 for c in content_list if c.reel_script is not None),
            api_calls_made=generator.api_calls_made,
            api_calls_failed=generator.api_calls_failed,
            total_input_tokens=generator.total_input_tokens,
            total_output_tokens=generator.total_output_tokens,
        )

        output = ComposerOutput(
            run_id=run_id,
            editorial_run_id=editorial_run,
            property=self.property_name,
            content=content_list,
            stats=stats,
            errors=errors,
        )

        self._save_output(output)
        logger.info(f"Composed {len(content_list)} content sets ({len(errors)} errors)")
        return output

    def _load_editorial_output(self, run_id: str | None = None) -> dict:
        evidence_dir = self.config_dir / "agents" / "editorial" / "evidence"
        if not evidence_dir.exists():
            raise FileNotFoundError(f"No Editorial evidence at {evidence_dir}.")
        if run_id:
            run_dir = evidence_dir / run_id
        else:
            runs = sorted([r for r in evidence_dir.iterdir() if r.is_dir()], reverse=True)
            if not runs:
                raise FileNotFoundError("No Editorial runs found.")
            run_dir = runs[0]
        output_file = run_dir / "editorial_output.json"
        if not output_file.exists():
            raise FileNotFoundError(f"Editorial output not found: {output_file}")
        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_output(self, output: ComposerOutput) -> Path:
        evidence_dir = (
            self.config_dir / "agents" / "content_composer" / "evidence" / output.run_id
        )
        evidence_dir.mkdir(parents=True, exist_ok=True)

        output_path = evidence_dir / "composer_output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output.model_dump_json(indent=2))

        # Save individual content files for easy copy-paste
        for content in output.content:
            slug = content.brief_slug.split("/")[-1] if "/" in content.brief_slug else content.brief_slug
            # Caption file
            if content.carousel.caption.full_text:
                (evidence_dir / f"{slug}_caption.txt").write_text(
                    content.carousel.caption.full_text, encoding="utf-8"
                )
            # Newsletter file
            if content.newsletter.full_text:
                (evidence_dir / f"{slug}_newsletter.md").write_text(
                    content.newsletter.full_text, encoding="utf-8"
                )
            # Carousel slides
            if content.carousel.slides:
                slides_text = "\n\n---\n\n".join(
                    f"SLIDE {s.slide_number}\n{s.headline}\n\n{s.body}\n\n[Visual: {s.visual_direction}]"
                    for s in content.carousel.slides
                )
                (evidence_dir / f"{slug}_slides.md").write_text(
                    slides_text, encoding="utf-8"
                )
            # Reel script
            if content.reel_script:
                rs = content.reel_script
                script = (
                    f"REEL SCRIPT ({rs.estimated_duration_seconds}s)\n\n"
                    f"[HOOK · 0-3s]\n{rs.hook}\n\n"
                    f"[BODY · 3-22s]\n{rs.body}\n\n"
                    f"POR QUÉ IMPORTA:\n{rs.por_que_importa}\n\n"
                    f"[CLOSE · 22-30s]\n{rs.close}\n\n"
                    f"CTA: {rs.cta}\n\n"
                    f"ON-SCREEN TEXT:\n" + "\n".join(f"  - {t}" for t in rs.on_screen_text)
                )
                (evidence_dir / f"{slug}_reel.md").write_text(script, encoding="utf-8")

        logger.info(f"Saved output to {evidence_dir}")
        return output_path

    def _load_agent_config(self) -> dict[str, Any]:
        config_path = self.config_dir / "agents" / "content_composer" / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _generate_run_id(self) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return f"{ts}_{self.property_name}_compose"

    @staticmethod
    def _find_project_root() -> Path:
        current = Path(__file__).resolve().parent
        for _ in range(10):
            if (current / "MASTER_PLAN.md").exists():
                return current
            parent = current.parent
            if parent == current:
                break
            current = parent
        raise FileNotFoundError("Could not find project root.")
