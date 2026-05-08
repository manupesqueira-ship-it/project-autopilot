"""Signal Scorer Agent — LLM-based item evaluation.

Reads Source Monitor output, scores each item against the Signal Scoring Rubric
using Claude API, and produces a ranked shortlist with justifications.

Usage:
    autopilot score --property ai-brief-latam
    autopilot score --property ai-brief-latam --run-id 20260508T050000_ai-brief-latam
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

from agents.signal_scorer.schemas import (
    Classification,
    ScoredItem,
    ScorerStats,
    SignalScorerResult,
)
from agents.signal_scorer.scorer import LLMScorer

logger = logging.getLogger(__name__)


class SignalScorerAgent:
    """Evaluates source items using LLM-based signal scoring.

    Lifecycle:
        1. Load latest Source Monitor output (or specified run)
        2. Filter to items worth scoring (above preliminary threshold)
        3. Score each item via Claude API
        4. Sort by signal_score descending
        5. Save output to evidence/
    """

    def __init__(self, property_name: str, config_dir: Path | None = None):
        self.property_name = property_name
        self.config_dir = config_dir or self._find_project_root()
        # Load .env from project root
        load_dotenv(self.config_dir / ".env")
        self.agent_config = self._load_agent_config()
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set — LLM scoring will fail")

    def run(
        self,
        source_run_id: str | None = None,
        min_preliminary_score: float | None = None,
        max_items: int | None = None,
    ) -> SignalScorerResult:
        """Execute a scoring run.

        Args:
            source_run_id: Specific Source Monitor run to score. If None, uses latest.
            min_preliminary_score: Only score items above this preliminary score.
                                   Defaults to config value.
            max_items: Maximum items to score (to control API costs).
                       Defaults to config value.

        Returns:
            SignalScorerResult with scored items.
        """
        run_id = self._generate_run_id()
        cfg = self.agent_config

        if min_preliminary_score is None:
            min_preliminary_score = cfg.get("scoring", {}).get("min_preliminary_score", 30.0)
        if max_items is None:
            max_items = cfg.get("scoring", {}).get("max_items_to_score", 20)

        # Step 1: Load source monitor output
        source_data = self._load_source_output(source_run_id)
        source_run = source_data.get("run_id", "unknown")
        all_items = source_data.get("items", [])
        logger.info(f"Loaded {len(all_items)} items from Source Monitor run '{source_run}'")

        # Step 2: Filter to scorable items
        candidates = [
            i for i in all_items
            if i.get("preliminary_score", 0) >= min_preliminary_score
        ]
        candidates.sort(key=lambda x: x.get("preliminary_score", 0), reverse=True)
        candidates = candidates[:max_items]
        logger.info(
            f"Scoring {len(candidates)} items "
            f"(filtered from {len(all_items)}, min_score={min_preliminary_score}, max={max_items})"
        )

        # Step 3: Score via LLM
        model = cfg.get("llm", {}).get("model", "claude-sonnet-4-20250514")
        max_tokens = cfg.get("llm", {}).get("max_tokens", 500)
        scorer = LLMScorer(api_key=self.api_key, model=model, max_tokens=max_tokens)

        scored_items: list[ScoredItem] = []
        errors: list[str] = []

        for i, item in enumerate(candidates):
            logger.debug(f"Scoring [{i+1}/{len(candidates)}]: {item['title'][:60]}")
            llm_result = scorer.score_item(item)
            scored = scorer.build_scored_item(item, llm_result)
            scored_items.append(scored)

            if "error" in llm_result:
                errors.append(f"{item['title'][:60]}: {llm_result['error']}")

        # Step 4: Sort by signal score
        scored_items.sort(key=lambda x: x.signal_score, reverse=True)

        # Step 5: Build result
        stats = self._compute_stats(scored_items, scorer)
        result = SignalScorerResult(
            run_id=run_id,
            source_run_id=source_run,
            property=self.property_name,
            items=scored_items,
            stats=stats,
            errors=errors,
        )

        self._save_output(result)

        logger.info(
            f"Scoring complete: {stats.items_scored} scored, "
            f"{stats.items_strong} strong, {stats.items_consider} consider, "
            f"{stats.items_discard} discard"
        )
        return result

    def _load_source_output(self, run_id: str | None = None) -> dict:
        """Load Source Monitor output JSON.

        Args:
            run_id: Specific run ID. If None, loads the most recent.

        Returns:
            Parsed JSON dict.
        """
        source_evidence_dir = self.config_dir / "agents" / "source_monitor" / "evidence"
        if not source_evidence_dir.exists():
            raise FileNotFoundError(
                f"No Source Monitor evidence found at {source_evidence_dir}. "
                "Run 'autopilot scan' first."
            )

        if run_id:
            run_dir = source_evidence_dir / run_id
        else:
            # Find the most recent run
            runs = sorted(source_evidence_dir.iterdir(), reverse=True)
            runs = [r for r in runs if r.is_dir()]
            if not runs:
                raise FileNotFoundError("No Source Monitor runs found.")
            run_dir = runs[0]

        output_file = run_dir / "source_monitor_output.json"
        if not output_file.exists():
            raise FileNotFoundError(f"Source Monitor output not found: {output_file}")

        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _compute_stats(self, items: list[ScoredItem], scorer: LLMScorer) -> ScorerStats:
        scores = [i.signal_score for i in items]
        return ScorerStats(
            items_scored=len(items),
            items_strong=sum(1 for i in items if i.classification == Classification.STRONG),
            items_consider=sum(1 for i in items if i.classification == Classification.CONSIDER),
            items_discard=sum(1 for i in items if i.classification == Classification.DISCARD),
            avg_signal_score=sum(scores) / len(scores) if scores else 0.0,
            api_calls_made=scorer.api_calls_made,
            api_calls_failed=scorer.api_calls_failed,
            total_input_tokens=scorer.total_input_tokens,
            total_output_tokens=scorer.total_output_tokens,
        )

    def _save_output(self, result: SignalScorerResult) -> Path:
        evidence_dir = (
            self.config_dir / "agents" / "signal_scorer" / "evidence" / result.run_id
        )
        evidence_dir.mkdir(parents=True, exist_ok=True)

        output_path = evidence_dir / "signal_scorer_output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))

        logger.info(f"Saved output to {output_path}")
        return output_path

    def _load_agent_config(self) -> dict[str, Any]:
        config_path = self.config_dir / "agents" / "signal_scorer" / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _generate_run_id(self) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return f"{ts}_{self.property_name}_score"

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
        raise FileNotFoundError(
            "Could not find project root. Pass config_dir explicitly."
        )
