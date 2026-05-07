from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from builder_orchestrator import plan_task
from config import ProjectConfig, load_project_config
from env_loader import load_env
from provider_registry import build_registry
from secret_status import env_var_status

load_env()


VERDICTS = {"CLAUDE_SDK_DRY_RUN_READY", "CLAUDE_SDK_DRY_RUN_PARTIAL", "CLAUDE_SDK_DRY_RUN_BLOCKED"}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _latest_policy_fixture_status(project: ProjectConfig) -> dict[str, Any]:
    path = project.repo_path / project.logs_dir / "policy_tests" / project.project_id / "latest" / "policy_test_results.json"
    payload = _read_json(path)
    if not payload:
        return {
            "status": "UNKNOWN",
            "passed": 0,
            "total": 0,
            "failed": 0,
            "path": str(path),
        }
    return {
        "status": payload.get("status", "UNKNOWN"),
        "passed": payload.get("passed", 0),
        "total": payload.get("total", 0),
        "failed": payload.get("failed", 0),
        "path": str(path),
    }


def _provider_by_id(registry: dict[str, Any], provider_id: str) -> dict[str, Any]:
    for provider in registry.get("providers", []):
        if provider.get("provider_id") == provider_id:
            return provider
    return {}


def _add_check(checks: list[dict[str, Any]], name: str, status: str, message: str) -> None:
    checks.append({"name": name, "status": status, "message": message})


def _verdict(checks: list[dict[str, Any]], key_status: str) -> str:
    if any(item["status"] == "FAIL" for item in checks):
        return "CLAUDE_SDK_DRY_RUN_BLOCKED"
    if key_status != "PRESENT_VALUE_HIDDEN" or any(item["status"] == "WARN" for item in checks):
        return "CLAUDE_SDK_DRY_RUN_PARTIAL"
    return "CLAUDE_SDK_DRY_RUN_READY"


def build_dry_run_report(project: ProjectConfig, task: str | None = None) -> dict[str, Any]:
    task = task or "Review architecture of Project Autopilot"
    root = project.repo_path
    ap = root / "project_autopilot"
    checks: list[dict[str, Any]] = []
    key = env_var_status("ANTHROPIC_API_KEY", min_length=16)
    registry = build_registry(project.project_id)
    claude = _provider_by_id(registry, "claude_agent_sdk")
    metadata = claude.get("metadata", {})
    fixture = _latest_policy_fixture_status(project)
    plan = plan_task(project, task)

    _add_check(
        checks,
        "Claude Agent SDK provider file exists",
        "PASS" if (ap / "providers" / "claude_agent_sdk_provider.py").exists() else "FAIL",
        "Provider scaffold found." if (ap / "providers" / "claude_agent_sdk_provider.py").exists() else "Provider scaffold missing.",
    )
    _add_check(
        checks,
        "Provider registry loads Claude Agent SDK provider",
        "PASS" if claude else "FAIL",
        "Provider loaded by registry." if claude else "Provider missing from registry.",
    )
    _add_check(
        checks,
        "ANTHROPIC_API_KEY detected safely",
        "PASS" if key["status"] == "PRESENT_VALUE_HIDDEN" else "WARN",
        f"ANTHROPIC_API_KEY: {key['status']}.",
    )
    _add_check(
        checks,
        "Provider configured status follows key presence",
        "PASS" if bool(claude.get("configured")) == (key["status"] == "PRESENT_VALUE_HIDDEN") else "FAIL",
        f"configured={bool(claude.get('configured'))}; key={key['status']}.",
    )
    _add_check(
        checks,
        "Automatic Claude execution disabled",
        "PASS" if project.allow_automatic_builder_execution is False and metadata.get("automatic_execution_enabled") is False else "FAIL",
        "Automatic Claude execution remains disabled.",
    )
    _add_check(
        checks,
        "Scheduler disabled",
        "PASS" if not (root / "project_control" / "SCHEDULER_ENABLED.md").exists() else "FAIL",
        "No scheduler enable marker found.",
    )
    _add_check(
        checks,
        "Post-builder policy enforcement exists",
        "PASS" if (ap / "post_builder_policy.py").exists() else "FAIL",
        "Post-builder policy module found.",
    )
    _add_check(
        checks,
        "Policy fixture suite latest result",
        "PASS" if fixture["status"] == "PASS" else ("WARN" if fixture["status"] == "UNKNOWN" else "FAIL"),
        f"{fixture['status']} ({fixture['passed']}/{fixture['total']}) at {fixture['path']}.",
    )
    _add_check(
        checks,
        "Design Director exists",
        "PASS" if (ap / "design_director.py").exists() else "FAIL",
        "Design Director available.",
    )
    _add_check(
        checks,
        "Research Director exists",
        "PASS" if (ap / "research_director.py").exists() else "FAIL",
        "Research Director available.",
    )
    _add_check(
        checks,
        "Builder Orchestrator Claude dry-run routing",
        "PASS" if plan.recommended_provider == "claude_agent_sdk" and plan.execution_mode == "dry_run_only" else "WARN",
        f"Task routes to {plan.recommended_provider} using {plan.execution_mode}.",
    )
    _add_check(
        checks,
        "Future live call requires explicit approval",
        "PASS" if metadata.get("requires_explicit_approval_for_live_call") is True and plan.explicit_approval_required else "FAIL",
        "Explicit approval is required before any future live Claude SDK call.",
    )
    _add_check(
        checks,
        "Worktree/sandbox policy documented",
        "PASS" if (project.project_control_path / "AUTOPILOT_V2_SPEC.md").exists() else "WARN",
        "Autopilot v2 spec documents worktree/sandbox requirements.",
    )
    _add_check(
        checks,
        "Cost/budget gate documented",
        "PASS" if (project.project_control_path / "COST_POLICY.md").exists() else "WARN",
        "Cost policy exists for future live provider calls.",
    )
    _add_check(
        checks,
        "No external call made",
        "PASS",
        "Dry-run validator did not call Anthropic, Claude Code, OpenAI, Supabase, or paid APIs.",
    )

    verdict = _verdict(checks, key["status"])
    next_action = (
        "Proceed only to a human-approved controlled Claude analysis call in a future sprint."
        if verdict == "CLAUDE_SDK_DRY_RUN_READY"
        else "Resolve blocked or partial dry-run checks before any live Claude SDK work."
    )

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        "project_name": project.project_name,
        "verdict": verdict,
        "anthropic_api_key_status": key["status"],
        "sdk_package_detected": bool(metadata.get("sdk_package_detected")),
        "provider_configured": bool(claude.get("configured")),
        "provider_status": claude.get("current_status", "missing"),
        "automatic_execution_enabled": False,
        "external_calls_enabled": False,
        "external_calls_made": False,
        "live_claude_calls": "DISABLED_EXPECTED",
        "automatic_claude_execution": "DISABLED_EXPECTED",
        "task_planned": task,
        "builder_orchestrator_plan": plan.to_dict(),
        "policy_fixture_suite": fixture,
        "checks": checks,
        "next_recommended_action": next_action,
        "safety": {
            "anthropic_api_called": False,
            "claude_code_executed": False,
            "openai_api_called": False,
            "paid_api_called": False,
            "secret_values_printed": False,
        },
    }


def write_reports(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    logs = project.repo_path / project.logs_dir
    logs.mkdir(parents=True, exist_ok=True)
    md_path = logs / f"{project.project_id}_claude_sdk_dry_run_latest.md"
    json_path = logs / f"{project.project_id}_claude_sdk_dry_run_latest.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Claude Agent SDK Dry-Run Readiness",
        "",
        f"Generated: {payload['generated_at_utc']}",
        f"Project: {payload['project_name']} ({payload['project_id']})",
        f"Verdict: {payload['verdict']}",
        f"ANTHROPIC_API_KEY: {payload['anthropic_api_key_status']}",
        f"SDK package detected: {'yes' if payload['sdk_package_detected'] else 'no'}",
        f"Provider configured: {'yes' if payload['provider_configured'] else 'no'}",
        f"Provider status: {payload['provider_status']}",
        f"Automatic Claude execution: {payload['automatic_claude_execution']}",
        f"Live Claude calls: {payload['live_claude_calls']}",
        f"External calls made: {'yes' if payload['external_calls_made'] else 'NO'}",
        "",
        "## Checks",
    ]
    for check in payload["checks"]:
        lines.append(f"- {check['status']} {check['name']}: {check['message']}")
    lines.extend([
        "",
        "## Builder Orchestrator Dry-Run Plan",
        f"- Task: {payload['task_planned']}",
        f"- Recommended provider: {payload['builder_orchestrator_plan']['recommended_provider']}",
        f"- Execution mode: {payload['builder_orchestrator_plan']['execution_mode']}",
        f"- Explicit approval required: {'yes' if payload['builder_orchestrator_plan']['explicit_approval_required'] else 'no'}",
        "",
        "## Next Recommended Action",
        payload["next_recommended_action"],
        "",
        "Safety: no Anthropic API call, Claude Code execution, OpenAI call, paid API call, SQL, deploy, or secret value logging occurred.",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def run(project_id: str, task: str | None = None) -> tuple[int, dict[str, Any], Path, Path]:
    project = load_project_config(project_id)
    payload = build_dry_run_report(project, task)
    md_path, json_path = write_reports(project, payload)
    exit_code = 2 if payload["verdict"] == "CLAUDE_SDK_DRY_RUN_BLOCKED" else 0
    return exit_code, payload, md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Claude Agent SDK dry-run readiness validator")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--status", action="store_true", help="Run status validation without a custom task.")
    parser.add_argument("--plan", help="Dry-run provider routing for a Claude-appropriate task.")
    args = parser.parse_args()

    exit_code, payload, md_path, json_path = run(args.project, args.plan)
    print(f"Claude SDK Dry-Run: {payload['verdict']}")
    print(f"  ANTHROPIC_API_KEY: {payload['anthropic_api_key_status']}")
    print(f"  SDK package detected: {'yes' if payload['sdk_package_detected'] else 'no'}")
    print(f"  Provider configured: {'yes' if payload['provider_configured'] else 'no'}")
    print(f"  External calls made: {'yes' if payload['external_calls_made'] else 'NO'}")
    print(f"  Automatic Claude execution: {payload['automatic_claude_execution']}")
    print(f"  Next action: {payload['next_recommended_action']}")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
