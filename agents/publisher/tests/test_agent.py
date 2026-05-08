"""Tests for Publisher agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.publisher.agent import PublisherAgent
from agents.publisher.schemas import PublishChannel, PublishStatus


MOCK_APPROVAL = {
    "run_id": "test_approval",
    "compliance_run_id": "test_compliance",
    "decisions": [
        {"brief_slug": "2026-05-08_jelou", "brief_title": "Jelou $10M",
         "content_type": "newsletter", "decision": "approved"},
        {"brief_slug": "2026-05-08_jelou", "brief_title": "Jelou $10M",
         "content_type": "carousel_caption", "decision": "rejected"},
        {"brief_slug": "2026-05-08_cyber", "brief_title": "GPT Cyber",
         "content_type": "carousel_caption", "decision": "approved"},
        {"brief_slug": "2026-05-08_cyber", "brief_title": "GPT Cyber",
         "content_type": "reel_script", "decision": "approved"},
    ],
}

MOCK_COMPLIANCE = {
    "run_id": "test_compliance",
    "composer_run_id": "test_composer",
}

MOCK_COMPOSER = {
    "run_id": "test_composer",
    "content": [
        {
            "brief_slug": "2026-05-08_jelou",
            "brief_title": "Jelou $10M",
            "carousel": {
                "slides": [
                    {"slide_number": 1, "headline": "US$10M", "body": "Jelou raises.", "visual_direction": "bold"},
                ],
                "caption": {"full_text": "Jelou levanta US$10M.\n#LATAM #Fintech"},
            },
            "newsletter": {
                "full_text": "JELOU LEVANTA US$10M\nPOR QUÉ IMPORTA: WhatsApp commerce.\nBOTTOM LINE: LATAM innova.",
            },
            "reel_script": None,
        },
        {
            "brief_slug": "2026-05-08_cyber",
            "brief_title": "GPT Cyber",
            "carousel": {
                "slides": [
                    {"slide_number": 1, "headline": "GPT-5.5-Cyber", "body": "IA para cyber.", "visual_direction": "dark"},
                ],
                "caption": {"full_text": "OpenAI lanza GPT-5.5-Cyber.\n#IA #Cyber"},
            },
            "newsletter": {"full_text": ""},
            "reel_script": {
                "hook": "OpenAI creó algo exclusivo",
                "body": "GPT-5.5-Cyber solo para defensores.",
                "por_que_importa": "Ciberseguridad con IA.",
                "close": "LATAM necesita esto.",
                "cta": "Guardá esto.",
                "estimated_duration_seconds": 30,
                "on_screen_text": ["GPT-5.5-Cyber", "Acceso exclusivo"],
            },
        },
    ],
}


def _setup_evidence(tmp_path: Path):
    """Set up the full evidence chain for publisher tests."""
    # Approval
    approval_dir = tmp_path / "agents" / "human_approval" / "evidence" / "test_approval"
    approval_dir.mkdir(parents=True)
    (approval_dir / "approval_output.json").write_text(json.dumps(MOCK_APPROVAL))

    # Compliance (referenced by approval)
    comp_dir = tmp_path / "agents" / "compliance" / "evidence" / "test_compliance"
    comp_dir.mkdir(parents=True)
    (comp_dir / "compliance_output.json").write_text(json.dumps(MOCK_COMPLIANCE))

    # Composer (referenced by compliance)
    composer_dir = tmp_path / "agents" / "content_composer" / "evidence" / "test_composer"
    composer_dir.mkdir(parents=True)
    (composer_dir / "composer_output.json").write_text(json.dumps(MOCK_COMPOSER))

    # Config
    config_dir = tmp_path / "agents" / "publisher"
    config_dir.mkdir(parents=True)
    import shutil
    shutil.copy(_project_root / "agents" / "publisher" / "config.yaml", config_dir / "config.yaml")
    (tmp_path / "MASTER_PLAN.md").touch()


class TestT1ExportFiles:

    def test_exports_approved_only(self, tmp_path):
        """Only approved items get exported. Rejected items are skipped."""
        _setup_evidence(tmp_path)
        agent = PublisherAgent("ai-brief-latam", config_dir=tmp_path)
        output = agent.run(approval_run_id="test_approval")

        # Jelou: newsletter approved, caption rejected -> only newsletter exported
        # Cyber: caption + reel approved -> both exported
        assert output.stats.items_ready == 2
        assert output.stats.files_exported >= 3  # newsletter + caption + reel at minimum

    def test_files_exist_on_disk(self, tmp_path):
        """Exported files actually exist at the reported paths."""
        _setup_evidence(tmp_path)
        agent = PublisherAgent("ai-brief-latam", config_dir=tmp_path)
        output = agent.run(approval_run_id="test_approval")

        export_dir = Path(output.export_dir)
        assert export_dir.exists()

        # Check Jelou newsletter
        jelou_nl = export_dir / "2026-05-08_jelou" / "newsletter.md"
        assert jelou_nl.exists()
        assert "JELOU" in jelou_nl.read_text(encoding="utf-8")

        # Check Cyber caption
        cyber_caption = export_dir / "2026-05-08_cyber" / "caption.txt"
        assert cyber_caption.exists()

        # Check Cyber reel
        cyber_reel = export_dir / "2026-05-08_cyber" / "reel_script.md"
        assert cyber_reel.exists()
        assert "HOOK" in cyber_reel.read_text(encoding="utf-8")

    def test_channel_detection(self, tmp_path):
        """Channel is correctly detected based on approved content types."""
        _setup_evidence(tmp_path)
        agent = PublisherAgent("ai-brief-latam", config_dir=tmp_path)
        output = agent.run(approval_run_id="test_approval")

        items_by_slug = {i.brief_slug: i for i in output.items}
        # Jelou: only newsletter approved
        assert items_by_slug["2026-05-08_jelou"].channel == PublishChannel.NEWSLETTER
        # Cyber: caption + reel (instagram)
        assert items_by_slug["2026-05-08_cyber"].channel == PublishChannel.INSTAGRAM


class TestT2NoApproved:

    def test_no_approved_produces_empty(self, tmp_path):
        """If nothing was approved, output is empty but valid."""
        all_rejected = {**MOCK_APPROVAL}
        all_rejected["decisions"] = [
            {**d, "decision": "rejected"} for d in MOCK_APPROVAL["decisions"]
        ]
        approval_dir = tmp_path / "agents" / "human_approval" / "evidence" / "test_run"
        approval_dir.mkdir(parents=True)
        (approval_dir / "approval_output.json").write_text(json.dumps(all_rejected))

        # Minimal compliance + composer stubs
        comp_dir = tmp_path / "agents" / "compliance" / "evidence" / "test_compliance"
        comp_dir.mkdir(parents=True)
        (comp_dir / "compliance_output.json").write_text(json.dumps(MOCK_COMPLIANCE))
        composer_dir = tmp_path / "agents" / "content_composer" / "evidence" / "test_composer"
        composer_dir.mkdir(parents=True)
        (composer_dir / "composer_output.json").write_text(json.dumps(MOCK_COMPOSER))

        config_dir = tmp_path / "agents" / "publisher"
        config_dir.mkdir(parents=True)
        import shutil
        shutil.copy(_project_root / "agents" / "publisher" / "config.yaml", config_dir / "config.yaml")
        (tmp_path / "MASTER_PLAN.md").touch()

        agent = PublisherAgent("ai-brief-latam", config_dir=tmp_path)
        output = agent.run(approval_run_id="test_run")

        assert output.stats.items_ready == 0
        assert output.stats.files_exported == 0


class TestT3Config:

    def test_agent_initializes(self):
        agent = PublisherAgent("ai-brief-latam", config_dir=_project_root)
        assert agent.agent_config["agent"]["name"] == "publisher"
