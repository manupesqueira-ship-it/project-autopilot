"""Editorial Agent — converts scored items into editorial briefs.

Reads Signal Scorer output, takes the top N strong items, and generates
full editorial briefs following the Anexo A template + brand voice rules.

Usage:
    autopilot brief --property ai-brief-latam
    autopilot brief --property ai-brief-latam --items 3
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

from agents.editorial.briefer import BriefGenerator
from agents.editorial.schemas import (
    EditorialBrief,
    EditorialResult,
    EditorialStats,
)

logger = logging.getLogger(__name__)


class EditorialAgent:
    """Generates editorial briefs from scored items.

    Lifecycle:
        1. Load latest Signal Scorer output (or specified run)
        2. Filter to strong/consider items
        3. Generate brief for each via Claude API
        4. Save briefs to evidence/
    """

    def __init__(self, property_name: str, config_dir: Path | None = None):
        self.property_name = property_name
        self.config_dir = config_dir or self._find_project_root()
        load_dotenv(self.config_dir / ".env")
        self.agent_config = self._load_agent_config()
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set — brief generation will fail")

    def run(
        self,
        score_run_id: str | None = None,
        max_items: int | None = None,
        min_signal_score: float | None = None,
    ) -> EditorialResult:
        """Execute a brief generation run.

        Args:
            score_run_id: Specific Signal Scorer run to use. If None, uses latest.
            max_items: Max items to generate briefs for (default from config).
            min_signal_score: Only brief items above this signal score (default: 60).

        Returns:
            EditorialResult with generated briefs.
        """
        run_id = self._generate_run_id()
        cfg = self.agent_config

        if max_items is None:
            max_items = cfg.get("generation", {}).get("max_briefs_per_run", 5)
        if min_signal_score is None:
            min_signal_score = cfg.get("generation", {}).get("min_signal_score", 60.0)

        # Step 1: Load signal scorer output
        score_data = self._load_score_output(score_run_id)
        score_run = score_data.get("run_id", "unknown")
        all_items = score_data.get("items", [])
        logger.info(f"Loaded {len(all_items)} scored items from run '{score_run}'")

        # Step 2: Filter to briefable items
        candidates = [
            i for i in all_items
            if i.get("signal_score", 0) >= min_signal_score
        ]
        candidates.sort(key=lambda x: x.get("signal_score", 0), reverse=True)
        candidates = candidates[:max_items]
        logger.info(f"Generating briefs for {len(candidates)} items (min_score={min_signal_score})")

        # Step 3: Generate briefs
        model = cfg.get("llm", {}).get("model", "claude-opus-4-20250514")
        max_tokens = cfg.get("llm", {}).get("max_tokens", 1500)
        generator = BriefGenerator(api_key=self.api_key, model=model, max_tokens=max_tokens)

        briefs: list[EditorialBrief] = []
        errors: list[str] = []

        for i, item in enumerate(candidates):
            logger.debug(f"Briefing [{i+1}/{len(candidates)}]: {item['title'][:60]}")
            llm_result = generator.generate_brief(item)
            brief = generator.build_editorial_brief(item, llm_result, self.property_name)

            if brief:
                briefs.append(brief)
            else:
                errors.append(f"{item['title'][:60]}: {llm_result.get('error', 'unknown')}")

        # Step 4: Save
        stats = EditorialStats(
            items_processed=len(candidates),
            briefs_generated=len(briefs),
            api_calls_made=generator.api_calls_made,
            api_calls_failed=generator.api_calls_failed,
            total_input_tokens=generator.total_input_tokens,
            total_output_tokens=generator.total_output_tokens,
        )

        result = EditorialResult(
            run_id=run_id,
            score_run_id=score_run,
            property=self.property_name,
            briefs=briefs,
            stats=stats,
            errors=errors,
        )

        self._save_output(result)
        logger.info(f"Generated {len(briefs)} briefs ({len(errors)} errors)")
        return result

    def _load_score_output(self, run_id: str | None = None) -> dict:
        """Load Signal Scorer output JSON."""
        evidence_dir = self.config_dir / "agents" / "signal_scorer" / "evidence"
        if not evidence_dir.exists():
            raise FileNotFoundError(
                f"No Signal Scorer evidence at {evidence_dir}. Run 'autopilot score' first."
            )

        if run_id:
            run_dir = evidence_dir / run_id
        else:
            runs = sorted(
                [r for r in evidence_dir.iterdir() if r.is_dir()], reverse=True
            )
            if not runs:
                raise FileNotFoundError("No Signal Scorer runs found.")
            run_dir = runs[0]

        output_file = run_dir / "signal_scorer_output.json"
        if not output_file.exists():
            raise FileNotFoundError(f"Signal Scorer output not found: {output_file}")

        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_output(self, result: EditorialResult) -> Path:
        evidence_dir = (
            self.config_dir / "agents" / "editorial" / "evidence" / result.run_id
        )
        evidence_dir.mkdir(parents=True, exist_ok=True)

        output_path = evidence_dir / "editorial_output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))

        # Also save each brief as individual markdown for easy reading
        for brief in result.briefs:
            md_path = evidence_dir / f"{brief.slug}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(self._brief_to_markdown(brief))

        logger.info(f"Saved output to {output_path}")
        return output_path

    def _brief_to_markdown(self, brief: EditorialBrief) -> str:
        """Render a brief as readable markdown."""
        lines = [
            f"# {brief.title}",
            "",
            f"**Slug:** {brief.slug}",
            f"**Fecha:** {brief.date}",
            f"**Property:** {brief.property}",
            f"**Signal Score:** {brief.signal_score}",
            f"**Formato:** {brief.formato_recomendado.value}",
            f"**Status:** {brief.status.value}",
            "",
            "## Qué pasó",
            brief.que_paso,
            "",
            "## Por qué importa",
            brief.por_que_importa,
            "",
            "## Qué cambia",
            brief.que_cambia,
            "",
            "## Quién gana / pierde",
            f"- **Gana:** {', '.join(brief.quien_gana_pierde.get('gana', []))}",
            f"- **Pierde:** {', '.join(brief.quien_gana_pierde.get('pierde', []))}",
            f"- **Neutro:** {', '.join(brief.quien_gana_pierde.get('neutro', []))}",
            "",
            "## Datos clave",
        ]
        for d in brief.datos_clave:
            lines.append(f"- {d}")
        lines += [
            "",
            "## Ángulo LATAM",
            brief.angulo_latam,
            "",
            "## Ángulos posibles",
        ]
        for i, a in enumerate(brief.angulos_posibles, 1):
            lines.append(f"{i}. {a}")
        lines += [
            "",
            f"## Ángulo elegido",
            brief.angulo_elegido,
            "",
            f"## Hook tentativo",
            f'"{brief.hook_tentativo}"',
            "",
            f"## CTA: {brief.cta_tentativo.value}",
            "",
            "## Fuentes",
        ]
        for f in brief.fuentes:
            lines.append(f"- {f}")
        lines += ["", "## Riesgos"]
        for r in brief.riesgos:
            lines.append(f"- {r}")
        lines += ["", "## Fact-check"]
        lines.append("| Claim | Status |")
        lines.append("|---|---|")
        for fc in brief.fact_check_items:
            lines.append(f"| {fc.claim} | {fc.status} |")

        return "\n".join(lines) + "\n"

    def _load_agent_config(self) -> dict[str, Any]:
        config_path = self.config_dir / "agents" / "editorial" / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _generate_run_id(self) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return f"{ts}_{self.property_name}_brief"

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
