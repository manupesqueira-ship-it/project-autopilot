from __future__ import annotations

import json

from config import ProjectConfig
from providers.base import ProviderInfo
from secret_status import env_var_status


def _latest_auditor_status(project: ProjectConfig) -> dict[str, object]:
    path = project.repo_path / project.logs_dir / "openai_auditor" / project.project_id / "latest" / "openai_auditor_dry_run.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"verdict": "NOT_RUN", "live_call_made": False, "path": str(path)}
    return {
        "verdict": payload.get("verdict", "UNKNOWN"),
        "mode": payload.get("mode", "unknown"),
        "live_call_made": bool(payload.get("live_call_made", False)),
        "openai_call_count": payload.get("openai_call_count", 0),
        "path": str(path),
    }


def detect(project: ProjectConfig) -> ProviderInfo:
    required = ["OPENAI_API_KEY"]
    key_status = env_var_status("OPENAI_API_KEY", min_length=16)
    missing = [] if key_status["status"] == "PRESENT_VALUE_HIDDEN" else required
    latest = _latest_auditor_status(project)
    return ProviderInfo(
        provider_id="openai_auditor",
        display_name="OpenAI Auditor",
        provider_type="auditor_planner",
        configured=not missing,
        capabilities=[
            "task planning",
            "prompt refinement",
            "builder failure diagnosis",
            "correction prompt generation",
            "policy evidence review",
            "next-step recommendation",
        ],
        risks=[
            "Prompt injection if builder reports are trusted too broadly.",
            "Over-broad instructions that blur planner and builder roles.",
            "Hallucinated fixes without evidence.",
            "Token cost if live reviewer calls are enabled.",
            "Sensitive context leakage if redaction fails.",
        ],
        required_env_vars=required,
        missing_env_vars=missing,
        supported_execution_modes=["dry_run", "controlled_analysis_future", "reviewer_future"],
        current_status="dry_run_only_configured" if not missing else "dry_run_only_missing_credentials",
        notes=[
            f"OPENAI_API_KEY status: {key_status['status']}.",
            "Provider registry never calls OpenAI.",
            "OpenAI Auditor is a planner/reviewer, not a default builder.",
            "Live OpenAI auditor calls remain disabled until explicitly approved.",
        ],
        metadata={
            "env_status": key_status["status"],
            "current_mode": "dry_run_only",
            "live_calls_enabled": False,
            "automatic_execution_enabled": False,
            "requires_explicit_approval_for_live_call": True,
            "policy_engine_remains_final_judge": True,
            "latest_auditor_dry_run": latest,
        },
    )
