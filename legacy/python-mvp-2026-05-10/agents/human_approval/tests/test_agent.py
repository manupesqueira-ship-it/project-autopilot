"""Tests for Human Approval agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.human_approval.agent import HumanApprovalAgent
from agents.human_approval.schemas import (
    ApprovalOutput,
    ContentDecision,
    Decision,
)


MOCK_COMPLIANCE_OUTPUT = {
    "run_id": "test_compliance_run",
    "composer_run_id": "test_composer_run",
    "results": [
        {
            "brief_slug": "2026-05-08_chatgpt-ads",
            "brief_title": "ChatGPT ads",
            "content_type": "carousel_caption",
            "verdict": "approved_with_warnings",
            "summary": "Minor warnings, OK to publish.",
            "blocks": [],
            "warnings": ["Cifra sin fuente"],
        },
        {
            "brief_slug": "2026-05-08_chatgpt-ads",
            "brief_title": "ChatGPT ads",
            "content_type": "newsletter",
            "verdict": "approved",
            "summary": "All checks passed.",
            "blocks": [],
            "warnings": [],
        },
        {
            "brief_slug": "2026-05-08_cyber",
            "brief_title": "GPT-5.5-Cyber",
            "content_type": "carousel_caption",
            "verdict": "blocked",
            "summary": "Blocked due to unverified claims.",
            "blocks": ["Unverified product claims"],
            "warnings": [],
        },
    ],
}


class TestSchemas:

    def test_decision_enum(self):
        assert Decision.APPROVED.value == "approved"
        assert Decision.REJECTED.value == "rejected"
        assert Decision.DEFERRED.value == "deferred"

    def test_content_decision_creates(self):
        cd = ContentDecision(
            brief_slug="test",
            brief_title="Test",
            content_type="caption",
            decision=Decision.APPROVED,
        )
        assert cd.decided_by == "manuel"


class TestT1AutoApprove:

    def test_auto_approve_passes_and_blocks(self, tmp_path):
        """Auto-approve: approved/warnings -> approved, blocked -> rejected."""
        comp_evidence = tmp_path / "agents" / "compliance" / "evidence" / "test_run"
        comp_evidence.mkdir(parents=True)
        with open(comp_evidence / "compliance_output.json", "w") as f:
            json.dump(MOCK_COMPLIANCE_OUTPUT, f)

        config_dir = tmp_path / "agents" / "human_approval"
        config_dir.mkdir(parents=True)
        import shutil
        shutil.copy(_project_root / "agents" / "human_approval" / "config.yaml",
                     config_dir / "config.yaml")
        (tmp_path / "MASTER_PLAN.md").touch()

        agent = HumanApprovalAgent("ai-brief-latam", config_dir=tmp_path)
        output = agent.run(compliance_run_id="test_run", auto_approve=True)

        assert len(output.decisions) == 3
        assert output.stats.items_approved == 2  # approved + approved_with_warnings
        assert output.stats.items_rejected == 1  # blocked

        # Check specific decisions
        approved = [d for d in output.decisions if d.decision == Decision.APPROVED]
        rejected = [d for d in output.decisions if d.decision == Decision.REJECTED]
        assert len(approved) == 2
        assert len(rejected) == 1
        assert "blocked" in rejected[0].notes.lower()

    def test_auto_approve_saves_evidence(self, tmp_path):
        comp_evidence = tmp_path / "agents" / "compliance" / "evidence" / "test_run"
        comp_evidence.mkdir(parents=True)
        with open(comp_evidence / "compliance_output.json", "w") as f:
            json.dump(MOCK_COMPLIANCE_OUTPUT, f)

        config_dir = tmp_path / "agents" / "human_approval"
        config_dir.mkdir(parents=True)
        import shutil
        shutil.copy(_project_root / "agents" / "human_approval" / "config.yaml",
                     config_dir / "config.yaml")
        (tmp_path / "MASTER_PLAN.md").touch()

        agent = HumanApprovalAgent("ai-brief-latam", config_dir=tmp_path)
        output = agent.run(compliance_run_id="test_run", auto_approve=True)

        evidence_dirs = list((tmp_path / "agents" / "human_approval" / "evidence").iterdir())
        assert len(evidence_dirs) == 1
        output_file = evidence_dirs[0] / "approval_output.json"
        assert output_file.exists()

        loaded = ApprovalOutput.model_validate_json(output_file.read_text())
        assert len(loaded.decisions) == 3


class TestT2NonInteractive:

    def test_non_auto_defers_all(self, tmp_path):
        """Without auto-approve and without TTY, all items are deferred."""
        comp_evidence = tmp_path / "agents" / "compliance" / "evidence" / "test_run"
        comp_evidence.mkdir(parents=True)
        with open(comp_evidence / "compliance_output.json", "w") as f:
            json.dump(MOCK_COMPLIANCE_OUTPUT, f)

        config_dir = tmp_path / "agents" / "human_approval"
        config_dir.mkdir(parents=True)
        import shutil
        shutil.copy(_project_root / "agents" / "human_approval" / "config.yaml",
                     config_dir / "config.yaml")
        (tmp_path / "MASTER_PLAN.md").touch()

        agent = HumanApprovalAgent("ai-brief-latam", config_dir=tmp_path)
        output = agent.run(compliance_run_id="test_run", auto_approve=False)

        assert output.stats.items_deferred == 3


class TestT3Config:

    def test_agent_initializes(self):
        agent = HumanApprovalAgent("ai-brief-latam", config_dir=_project_root)
        assert agent.agent_config["agent"]["name"] == "human_approval"
