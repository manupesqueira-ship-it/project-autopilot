"""Human Approval Agent — interactive CLI for editorial decisions.

Presents compliance-reviewed content to the human editor for
approve/reject/edit/defer decisions. Records all decisions as evidence.

Unlike other agents, this one does NOT call an LLM. It's a human-in-the-loop
step that presents information and records decisions.

Usage:
    autopilot approve --property ai-brief-latam
    autopilot approve --property ai-brief-latam --auto-approve  (approve all passing)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from agents.human_approval.schemas import (
    ApprovalOutput,
    ApprovalStats,
    ContentDecision,
    Decision,
)

logger = logging.getLogger(__name__)


class HumanApprovalAgent:
    """Presents content for human review and records decisions.

    Lifecycle:
        1. Load Compliance output + Composer output
        2. For each content piece, show compliance verdict + content preview
        3. Collect human decision (approve/reject/edit/defer)
        4. Save all decisions to evidence/
    """

    def __init__(self, property_name: str, config_dir: Path | None = None):
        self.property_name = property_name
        self.config_dir = config_dir or self._find_project_root()
        self.agent_config = self._load_agent_config()

    def run(
        self,
        compliance_run_id: str | None = None,
        auto_approve: bool = False,
    ) -> ApprovalOutput:
        """Run the approval flow.

        Args:
            compliance_run_id: Specific Compliance run. If None, uses latest.
            auto_approve: If True, auto-approve all items that passed compliance.
                          Items that were blocked are auto-rejected.
        """
        run_id = self._generate_run_id()

        compliance_data = self._load_compliance_output(compliance_run_id)
        compliance_run = compliance_data.get("run_id", "unknown")
        results = compliance_data.get("results", [])

        composer_data = self._load_composer_output_for_compliance(compliance_data)

        decisions: list[ContentDecision] = []

        for result in results:
            slug = result.get("brief_slug", "unknown")
            title = result.get("brief_title", "unknown")
            content_type = result.get("content_type", "unknown")
            verdict = result.get("verdict", "blocked")

            if auto_approve:
                if verdict == "approved" or verdict == "approved_with_warnings":
                    decision = Decision.APPROVED
                    notes = f"Auto-approved (compliance verdict: {verdict})"
                else:
                    decision = Decision.REJECTED
                    notes = f"Auto-rejected (compliance verdict: {verdict})"
                    blocks = result.get("blocks", [])
                    if blocks:
                        notes += f". Blocks: {'; '.join(blocks[:3])}"
            else:
                # Non-interactive fallback — mark as deferred for CLI review
                decision = Decision.DEFERRED
                notes = f"Pending interactive review (compliance: {verdict})"

            decisions.append(ContentDecision(
                brief_slug=slug,
                brief_title=title,
                content_type=content_type,
                decision=decision,
                notes=notes,
            ))

        stats = ApprovalStats(
            items_reviewed=len(decisions),
            items_approved=sum(1 for d in decisions if d.decision == Decision.APPROVED),
            items_rejected=sum(1 for d in decisions if d.decision == Decision.REJECTED),
            items_edit_requested=sum(1 for d in decisions if d.decision == Decision.EDIT_REQUESTED),
            items_deferred=sum(1 for d in decisions if d.decision == Decision.DEFERRED),
        )

        output = ApprovalOutput(
            run_id=run_id,
            compliance_run_id=compliance_run,
            property=self.property_name,
            decisions=decisions,
            stats=stats,
        )

        self._save_output(output)
        logger.info(
            f"Approval complete: {stats.items_approved} approved, "
            f"{stats.items_rejected} rejected, {stats.items_deferred} deferred"
        )
        return output

    def _load_compliance_output(self, run_id: str | None = None) -> dict:
        evidence_dir = self.config_dir / "agents" / "compliance" / "evidence"
        if not evidence_dir.exists():
            raise FileNotFoundError(f"No Compliance evidence at {evidence_dir}.")
        if run_id:
            run_dir = evidence_dir / run_id
        else:
            runs = sorted([r for r in evidence_dir.iterdir() if r.is_dir()], reverse=True)
            if not runs:
                raise FileNotFoundError("No Compliance runs found.")
            run_dir = runs[0]
        output_file = run_dir / "compliance_output.json"
        if not output_file.exists():
            raise FileNotFoundError(f"Compliance output not found: {output_file}")
        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_composer_output_for_compliance(self, compliance_data: dict) -> dict:
        """Try to load the original composer output referenced by compliance."""
        composer_run = compliance_data.get("composer_run_id", "")
        if not composer_run:
            return {}
        evidence_dir = self.config_dir / "agents" / "content_composer" / "evidence" / composer_run
        output_file = evidence_dir / "composer_output.json"
        if output_file.exists():
            with open(output_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_output(self, output: ApprovalOutput) -> Path:
        evidence_dir = (
            self.config_dir / "agents" / "human_approval" / "evidence" / output.run_id
        )
        evidence_dir.mkdir(parents=True, exist_ok=True)
        output_path = evidence_dir / "approval_output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output.model_dump_json(indent=2))
        logger.info(f"Saved output to {output_path}")
        return output_path

    def _load_agent_config(self) -> dict[str, Any]:
        config_path = self.config_dir / "agents" / "human_approval" / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _generate_run_id(self) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return f"{ts}_{self.property_name}_approval"

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
