"""Compliance Agent — reviews content before publication.

Reads Content Composer output and checks each piece against Meta rules,
brand voice rules, and property-specific compliance requirements.

Usage:
    autopilot comply --property ai-brief-latam
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

from agents.compliance.reviewer import ComplianceReviewer
from agents.compliance.schemas import (
    ComplianceOutput,
    ComplianceStats,
    ComplianceVerdict,
    ContentComplianceResult,
)

logger = logging.getLogger(__name__)


class ComplianceAgent:
    """Reviews composed content for platform and brand compliance."""

    def __init__(self, property_name: str, config_dir: Path | None = None):
        self.property_name = property_name
        self.config_dir = config_dir or self._find_project_root()
        load_dotenv(self.config_dir / ".env")
        self.agent_config = self._load_agent_config()
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set")

    def run(self, composer_run_id: str | None = None) -> ComplianceOutput:
        """Review all content from a Content Composer run."""
        run_id = self._generate_run_id()

        composer_data = self._load_composer_output(composer_run_id)
        composer_run = composer_data.get("run_id", "unknown")
        content_list = composer_data.get("content", [])
        logger.info(f"Reviewing {len(content_list)} content sets from '{composer_run}'")

        model = self.agent_config.get("llm", {}).get("model", "claude-sonnet-4-20250514")
        max_tokens = self.agent_config.get("llm", {}).get("max_tokens", 1200)
        reviewer = ComplianceReviewer(api_key=self.api_key, model=model, max_tokens=max_tokens)

        results: list[ContentComplianceResult] = []
        errors: list[str] = []

        for content in content_list:
            brief_slug = content.get("brief_slug", "unknown")
            brief_title = content.get("brief_title", "unknown")

            # Review caption
            caption_text = content.get("carousel", {}).get("caption", {}).get("full_text", "")
            if caption_text:
                llm_result = reviewer.review_content(
                    caption_text, "carousel_caption", content
                )
                results.append(reviewer.build_compliance_result(
                    llm_result, "carousel_caption", brief_slug, brief_title
                ))

            # Review newsletter
            newsletter_text = content.get("newsletter", {}).get("full_text", "")
            if newsletter_text:
                llm_result = reviewer.review_content(
                    newsletter_text, "newsletter", content
                )
                results.append(reviewer.build_compliance_result(
                    llm_result, "newsletter", brief_slug, brief_title
                ))

            # Review reel script
            reel = content.get("reel_script")
            if reel and isinstance(reel, dict):
                reel_text = (
                    f"HOOK: {reel.get('hook', '')}\n"
                    f"BODY: {reel.get('body', '')}\n"
                    f"CLOSE: {reel.get('close', '')}\n"
                    f"CTA: {reel.get('cta', '')}"
                )
                llm_result = reviewer.review_content(
                    reel_text, "reel_script", content
                )
                results.append(reviewer.build_compliance_result(
                    llm_result, "reel_script", brief_slug, brief_title
                ))

        stats = self._compute_stats(results, reviewer)
        output = ComplianceOutput(
            run_id=run_id,
            composer_run_id=composer_run,
            property=self.property_name,
            results=results,
            stats=stats,
            errors=errors,
        )

        self._save_output(output)
        logger.info(
            f"Compliance review complete: {stats.items_approved} approved, "
            f"{stats.items_approved_with_warnings} with warnings, "
            f"{stats.items_blocked} blocked"
        )
        return output

    def _load_composer_output(self, run_id: str | None = None) -> dict:
        evidence_dir = self.config_dir / "agents" / "content_composer" / "evidence"
        if not evidence_dir.exists():
            raise FileNotFoundError(f"No Composer evidence at {evidence_dir}.")
        if run_id:
            run_dir = evidence_dir / run_id
        else:
            runs = sorted([r for r in evidence_dir.iterdir() if r.is_dir()], reverse=True)
            if not runs:
                raise FileNotFoundError("No Composer runs found.")
            run_dir = runs[0]
        output_file = run_dir / "composer_output.json"
        if not output_file.exists():
            raise FileNotFoundError(f"Composer output not found: {output_file}")
        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _compute_stats(
        self, results: list[ContentComplianceResult], reviewer: ComplianceReviewer
    ) -> ComplianceStats:
        all_checks = [c for r in results for c in r.checks]
        return ComplianceStats(
            items_checked=len(results),
            items_approved=sum(1 for r in results if r.verdict == ComplianceVerdict.APPROVED),
            items_approved_with_warnings=sum(
                1 for r in results if r.verdict == ComplianceVerdict.APPROVED_WITH_WARNINGS
            ),
            items_blocked=sum(1 for r in results if r.verdict == ComplianceVerdict.BLOCKED),
            total_checks=len(all_checks),
            checks_passed=sum(1 for c in all_checks if c.passed),
            checks_failed=sum(1 for c in all_checks if not c.passed),
            api_calls_made=reviewer.api_calls_made,
            api_calls_failed=reviewer.api_calls_failed,
            total_input_tokens=reviewer.total_input_tokens,
            total_output_tokens=reviewer.total_output_tokens,
        )

    def _save_output(self, output: ComplianceOutput) -> Path:
        evidence_dir = (
            self.config_dir / "agents" / "compliance" / "evidence" / output.run_id
        )
        evidence_dir.mkdir(parents=True, exist_ok=True)
        output_path = evidence_dir / "compliance_output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output.model_dump_json(indent=2))
        logger.info(f"Saved output to {output_path}")
        return output_path

    def _load_agent_config(self) -> dict[str, Any]:
        config_path = self.config_dir / "agents" / "compliance" / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _generate_run_id(self) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return f"{ts}_{self.property_name}_compliance"

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
