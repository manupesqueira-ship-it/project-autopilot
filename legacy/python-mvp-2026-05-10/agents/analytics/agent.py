"""Analytics Agent — collects metrics and produces reports.

Scans evidence directories across all agents to aggregate pipeline stats,
API costs, and content performance. Produces weekly reports.

In Fase 5, this agent also provides recommendations for improving content
strategy based on performance data.

Usage:
    autopilot analytics --property ai-brief-latam
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from agents.analytics.schemas import (
    AnalyticsOutput,
    PipelineRunSummary,
    WeeklyReport,
)

logger = logging.getLogger(__name__)

# Approximate cost per token (Opus pricing as of 2026)
_INPUT_COST_PER_TOKEN = 15.0 / 1_000_000   # $15/M input tokens
_OUTPUT_COST_PER_TOKEN = 75.0 / 1_000_000   # $75/M output tokens


class AnalyticsAgent:
    """Collects pipeline metrics and produces reports."""

    def __init__(self, property_name: str, config_dir: Path | None = None):
        self.property_name = property_name
        self.config_dir = config_dir or self._find_project_root()
        self.agent_config = self._load_agent_config()

    def run(self) -> AnalyticsOutput:
        """Aggregate stats from all agent evidence directories."""
        run_id = self._generate_run_id()

        pipeline_runs = self._collect_pipeline_runs()
        weekly_report = self._build_weekly_report(pipeline_runs)

        output = AnalyticsOutput(
            run_id=run_id,
            property=self.property_name,
            pipeline_runs=pipeline_runs,
            weekly_report=weekly_report,
        )

        self._save_output(output)
        logger.info(f"Analytics: {len(pipeline_runs)} pipeline runs analyzed")
        return output

    def _collect_pipeline_runs(self) -> list[PipelineRunSummary]:
        """Scan evidence dirs to find pipeline run data."""
        runs: list[PipelineRunSummary] = []

        # Scan source monitor evidence
        sm_evidence = self.config_dir / "agents" / "source_monitor" / "evidence"
        if not sm_evidence.exists():
            return runs

        for run_dir in sorted(sm_evidence.iterdir()):
            if not run_dir.is_dir():
                continue

            stats_file = run_dir / "source_monitor_stats.json"
            if not stats_file.exists():
                continue

            try:
                with open(stats_file, "r", encoding="utf-8") as f:
                    stats = json.load(f)

                date = run_dir.name[:8]  # YYYYMMDD from run_id
                date_formatted = f"{date[:4]}-{date[4:6]}-{date[6:8]}"

                run_summary = PipelineRunSummary(
                    date=date_formatted,
                    source_items_found=stats.get("items_found", 0),
                )

                # Try to find corresponding scorer run
                scorer_tokens = self._find_agent_tokens("signal_scorer", date)
                editorial_tokens = self._find_agent_tokens("editorial", date)
                composer_tokens = self._find_agent_tokens("content_composer", date)
                compliance_tokens = self._find_agent_tokens("compliance", date)

                total_tokens = scorer_tokens + editorial_tokens + composer_tokens + compliance_tokens
                run_summary.total_api_tokens = total_tokens
                # Rough estimate: assume 40% input, 60% output
                run_summary.total_api_cost_estimate = round(
                    total_tokens * 0.4 * _INPUT_COST_PER_TOKEN +
                    total_tokens * 0.6 * _OUTPUT_COST_PER_TOKEN, 4
                )

                runs.append(run_summary)
            except (json.JSONDecodeError, KeyError) as e:
                logger.debug(f"Skipping malformed run {run_dir.name}: {e}")

        return runs

    def _find_agent_tokens(self, agent_name: str, date_prefix: str) -> int:
        """Find total tokens used by an agent on a given date."""
        evidence_dir = self.config_dir / "agents" / agent_name / "evidence"
        if not evidence_dir.exists():
            return 0

        total = 0
        for run_dir in evidence_dir.iterdir():
            if not run_dir.is_dir() or not run_dir.name.startswith(date_prefix):
                continue

            # Look for any output file with stats
            for f in run_dir.iterdir():
                if f.suffix == ".json" and "output" in f.name:
                    try:
                        with open(f, "r", encoding="utf-8") as fh:
                            data = json.load(fh)
                        stats = data.get("stats", {})
                        total += stats.get("total_input_tokens", 0)
                        total += stats.get("total_output_tokens", 0)
                    except (json.JSONDecodeError, KeyError):
                        pass
        return total

    def _build_weekly_report(self, runs: list[PipelineRunSummary]) -> WeeklyReport:
        """Build a weekly summary from pipeline runs."""
        if not runs:
            return WeeklyReport(
                week_start="", week_end="", property=self.property_name
            )

        dates = [r.date for r in runs]
        return WeeklyReport(
            week_start=min(dates),
            week_end=max(dates),
            property=self.property_name,
            total_scans=len(runs),
            total_items_discovered=sum(r.source_items_found for r in runs),
            total_briefs_generated=sum(r.briefs_generated for r in runs),
            total_pieces_published=sum(r.items_published for r in runs),
            total_api_tokens=sum(r.total_api_tokens for r in runs),
            total_api_cost_estimate=round(sum(r.total_api_cost_estimate for r in runs), 4),
            recommendations=self._generate_recommendations(runs),
        )

    def _generate_recommendations(self, runs: list[PipelineRunSummary]) -> list[str]:
        """Generate basic recommendations from pipeline data."""
        recs = []
        if not runs:
            return ["No pipeline runs found. Run 'autopilot scan' to start."]

        total_items = sum(r.source_items_found for r in runs)
        if total_items == 0:
            recs.append("No items discovered. Check RSS sources configuration.")
        elif total_items > 500:
            recs.append(f"{total_items} items discovered — consider raising min_preliminary_score to reduce noise.")

        total_cost = sum(r.total_api_cost_estimate for r in runs)
        if total_cost > 5.0:
            recs.append(f"API cost this period: ${total_cost:.2f}. Consider reducing max_items_to_score if budget-constrained.")

        if not recs:
            recs.append("Pipeline running healthy. No issues detected.")

        return recs

    def _save_output(self, output: AnalyticsOutput) -> Path:
        evidence_dir = (
            self.config_dir / "agents" / "analytics" / "evidence" / output.run_id
        )
        evidence_dir.mkdir(parents=True, exist_ok=True)
        output_path = evidence_dir / "analytics_output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output.model_dump_json(indent=2))
        logger.info(f"Saved output to {output_path}")
        return output_path

    def _load_agent_config(self) -> dict[str, Any]:
        config_path = self.config_dir / "agents" / "analytics" / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _generate_run_id(self) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return f"{ts}_{self.property_name}_analytics"

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
