"""Fact-Checker Agent — verifies claims in editorial briefs.

Reads Editorial agent output, extracts verifiable claims, and evaluates
their accuracy using Claude API. Produces a verdict per brief.

Usage:
    autopilot check --property ai-brief-latam
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

from agents.fact_checker.checker import ClaimChecker
from agents.fact_checker.schemas import (
    BriefVerdict,
    FactCheckResult,
    FactCheckerOutput,
    FactCheckerStats,
    VerificationStatus,
)

logger = logging.getLogger(__name__)


class FactCheckerAgent:
    """Verifies claims in editorial briefs before publication.

    Lifecycle:
        1. Load latest Editorial output (or specified run)
        2. For each brief, extract claims and verify via LLM
        3. Assign verdict (pass / pass_with_edits / needs_review / fail)
        4. Save results with recommended edits
    """

    def __init__(self, property_name: str, config_dir: Path | None = None):
        self.property_name = property_name
        self.config_dir = config_dir or self._find_project_root()
        load_dotenv(self.config_dir / ".env")
        self.agent_config = self._load_agent_config()
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set — fact-checking will fail")

    def run(self, editorial_run_id: str | None = None) -> FactCheckerOutput:
        """Execute a fact-check run on editorial briefs.

        Args:
            editorial_run_id: Specific Editorial run. If None, uses latest.

        Returns:
            FactCheckerOutput with verification results per brief.
        """
        run_id = self._generate_run_id()
        cfg = self.agent_config

        # Load editorial output
        editorial_data = self._load_editorial_output(editorial_run_id)
        editorial_run = editorial_data.get("run_id", "unknown")
        briefs = editorial_data.get("briefs", [])
        logger.info(f"Checking {len(briefs)} briefs from editorial run '{editorial_run}'")

        # Fact-check each brief
        model = cfg.get("llm", {}).get("model", "claude-sonnet-4-20250514")
        max_tokens = cfg.get("llm", {}).get("max_tokens", 1200)
        checker = ClaimChecker(api_key=self.api_key, model=model, max_tokens=max_tokens)

        results: list[FactCheckResult] = []
        errors: list[str] = []

        for i, brief in enumerate(briefs):
            logger.debug(f"Checking [{i+1}/{len(briefs)}]: {brief.get('title', '?')[:60]}")
            llm_result = checker.check_brief(brief)
            fc_result = checker.build_fact_check_result(brief, llm_result)
            results.append(fc_result)

            if "error" in llm_result:
                errors.append(f"{brief.get('title', '?')[:60]}: {llm_result['error']}")

        # Stats
        stats = self._compute_stats(results, checker)

        output = FactCheckerOutput(
            run_id=run_id,
            editorial_run_id=editorial_run,
            property=self.property_name,
            results=results,
            stats=stats,
            errors=errors,
        )

        self._save_output(output)
        logger.info(
            f"Fact-check complete: {stats.briefs_checked} briefs, "
            f"{stats.claims_verified} verified / {stats.claims_disputed} disputed / "
            f"{stats.claims_unverified} unverified"
        )
        return output

    def _load_editorial_output(self, run_id: str | None = None) -> dict:
        evidence_dir = self.config_dir / "agents" / "editorial" / "evidence"
        if not evidence_dir.exists():
            raise FileNotFoundError(
                f"No Editorial evidence at {evidence_dir}. Run 'autopilot brief' first."
            )

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

    def _compute_stats(
        self, results: list[FactCheckResult], checker: ClaimChecker
    ) -> FactCheckerStats:
        all_claims = [c for r in results for c in r.claims]
        return FactCheckerStats(
            briefs_checked=len(results),
            claims_total=len(all_claims),
            claims_verified=sum(1 for c in all_claims if c.status == VerificationStatus.VERIFIED),
            claims_disputed=sum(1 for c in all_claims if c.status == VerificationStatus.DISPUTED),
            claims_unverified=sum(1 for c in all_claims if c.status in (
                VerificationStatus.UNVERIFIED, VerificationStatus.UNABLE_TO_VERIFY
            )),
            verdicts_pass=sum(1 for r in results if r.verdict == BriefVerdict.PASS),
            verdicts_pass_with_edits=sum(1 for r in results if r.verdict == BriefVerdict.PASS_WITH_EDITS),
            verdicts_needs_review=sum(1 for r in results if r.verdict == BriefVerdict.NEEDS_REVIEW),
            verdicts_fail=sum(1 for r in results if r.verdict == BriefVerdict.FAIL),
            api_calls_made=checker.api_calls_made,
            api_calls_failed=checker.api_calls_failed,
            total_input_tokens=checker.total_input_tokens,
            total_output_tokens=checker.total_output_tokens,
        )

    def _save_output(self, output: FactCheckerOutput) -> Path:
        evidence_dir = (
            self.config_dir / "agents" / "fact_checker" / "evidence" / output.run_id
        )
        evidence_dir.mkdir(parents=True, exist_ok=True)

        output_path = evidence_dir / "fact_checker_output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output.model_dump_json(indent=2))

        logger.info(f"Saved output to {output_path}")
        return output_path

    def _load_agent_config(self) -> dict[str, Any]:
        config_path = self.config_dir / "agents" / "fact_checker" / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _generate_run_id(self) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return f"{ts}_{self.property_name}_factcheck"

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
