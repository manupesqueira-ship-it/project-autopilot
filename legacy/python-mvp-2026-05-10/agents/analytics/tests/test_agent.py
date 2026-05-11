"""Tests for Analytics agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.analytics.agent import AnalyticsAgent
from agents.analytics.schemas import AnalyticsOutput, PipelineRunSummary


def _setup_evidence(tmp_path: Path):
    """Create minimal evidence for analytics to scan."""
    # Source monitor evidence
    sm_dir = tmp_path / "agents" / "source_monitor" / "evidence" / "20260508T080000_ai-brief-latam"
    sm_dir.mkdir(parents=True)
    (sm_dir / "source_monitor_stats.json").write_text(json.dumps({
        "sources_checked": 12, "sources_failed": 1,
        "items_found": 251, "items_after_dedup": 65, "dedup_removed": 186,
    }))

    # Signal scorer evidence
    ss_dir = tmp_path / "agents" / "signal_scorer" / "evidence" / "20260508T081000_ai-brief-latam_score"
    ss_dir.mkdir(parents=True)
    (ss_dir / "signal_scorer_output.json").write_text(json.dumps({
        "run_id": "test", "stats": {
            "total_input_tokens": 5000, "total_output_tokens": 5000,
        }
    }))

    # Config
    config_dir = tmp_path / "agents" / "analytics"
    config_dir.mkdir(parents=True)
    import shutil
    shutil.copy(_project_root / "agents" / "analytics" / "config.yaml", config_dir / "config.yaml")
    (tmp_path / "MASTER_PLAN.md").touch()


class TestT1CollectRuns:

    def test_collects_pipeline_runs(self, tmp_path):
        _setup_evidence(tmp_path)
        agent = AnalyticsAgent("ai-brief-latam", config_dir=tmp_path)
        output = agent.run()

        assert len(output.pipeline_runs) == 1
        assert output.pipeline_runs[0].source_items_found == 251
        assert output.pipeline_runs[0].date == "2026-05-08"

    def test_calculates_token_costs(self, tmp_path):
        _setup_evidence(tmp_path)
        agent = AnalyticsAgent("ai-brief-latam", config_dir=tmp_path)
        output = agent.run()

        run = output.pipeline_runs[0]
        assert run.total_api_tokens == 10000  # 5000 in + 5000 out from scorer
        assert run.total_api_cost_estimate > 0


class TestT2WeeklyReport:

    def test_weekly_report_generated(self, tmp_path):
        _setup_evidence(tmp_path)
        agent = AnalyticsAgent("ai-brief-latam", config_dir=tmp_path)
        output = agent.run()

        assert output.weekly_report is not None
        assert output.weekly_report.total_scans == 1
        assert output.weekly_report.total_items_discovered == 251
        assert len(output.weekly_report.recommendations) > 0

    def test_empty_evidence_produces_valid_output(self, tmp_path):
        config_dir = tmp_path / "agents" / "analytics"
        config_dir.mkdir(parents=True)
        import shutil
        shutil.copy(_project_root / "agents" / "analytics" / "config.yaml", config_dir / "config.yaml")
        (tmp_path / "MASTER_PLAN.md").touch()

        agent = AnalyticsAgent("ai-brief-latam", config_dir=tmp_path)
        output = agent.run()

        assert len(output.pipeline_runs) == 0
        assert output.weekly_report is not None


class TestT3Config:

    def test_agent_initializes(self):
        agent = AnalyticsAgent("ai-brief-latam", config_dir=_project_root)
        assert agent.agent_config["agent"]["name"] == "analytics"
