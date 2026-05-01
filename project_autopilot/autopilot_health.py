from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from autopilot_v2_check import run_check
from blocker_summary import summarize_blockers
from builder_orchestrator import status as builder_orchestrator_status
from claude_runner import detect_claude_cli
from config import ProjectConfig, load_project_config
from provider_registry import build_registry
from run_lock import lock_status


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def policy_fixture_health(project: ProjectConfig) -> dict[str, Any]:
    json_path = project.repo_path / project.logs_dir / "policy_tests" / project.project_id / "latest" / "policy_test_results.json"
    report_path = project.repo_path / project.logs_dir / "policy_tests" / project.project_id / "latest" / "policy_test_report.md"
    payload = _read_json(json_path)
    if not payload:
        return {
            "status": "UNKNOWN",
            "severity": "warn",
            "passed": 0,
            "total": 0,
            "failed": 0,
            "failed_fixtures": [],
            "result_path": str(json_path),
            "report_path": str(report_path),
            "command": f"python -B project_autopilot/policy_test_fixtures.py --project {project.project_id} --run all",
        }
    failed_results = [item for item in payload.get("results", []) if not item.get("passed")]
    status = payload.get("status", "UNKNOWN")
    return {
        "status": status,
        "severity": "pass" if status == "PASS" else "fail",
        "passed": payload.get("passed", 0),
        "total": payload.get("total", 0),
        "failed": payload.get("failed", 0),
        "failed_fixtures": [item.get("fixture_id", "unknown") for item in failed_results],
        "result_path": str(json_path),
        "report_path": str(report_path),
        "command": f"python -B project_autopilot/policy_test_fixtures.py --project {project.project_id} --run all",
    }


def claude_sdk_dry_run_health(project: ProjectConfig) -> dict[str, Any]:
    json_path = project.repo_path / project.logs_dir / f"{project.project_id}_claude_sdk_dry_run_latest.json"
    report_path = project.repo_path / project.logs_dir / f"{project.project_id}_claude_sdk_dry_run_latest.md"
    payload = _read_json(json_path)
    if not payload:
        return {
            "verdict": "UNKNOWN",
            "severity": "warn",
            "report_path": str(report_path),
            "json_path": str(json_path),
            "command": f"python -B project_autopilot/agent_loop.py --project {project.project_id} --claude-sdk-dry-run",
        }
    verdict = payload.get("verdict", "UNKNOWN")
    return {
        "verdict": verdict,
        "severity": "pass" if verdict == "CLAUDE_SDK_DRY_RUN_READY" else ("fail" if verdict == "CLAUDE_SDK_DRY_RUN_BLOCKED" else "warn"),
        "anthropic_api_key_status": payload.get("anthropic_api_key_status", "UNKNOWN"),
        "sdk_package_detected": payload.get("sdk_package_detected", False),
        "external_calls_made": payload.get("external_calls_made", False),
        "report_path": str(report_path),
        "json_path": str(json_path),
        "command": f"python -B project_autopilot/agent_loop.py --project {project.project_id} --claude-sdk-dry-run",
    }


def _latest_flow_status(project: ProjectConfig) -> dict[str, Any]:
    results_path = project.repo_path / project.logs_dir / "flow_qa" / project.project_id / "latest" / "flow_results.json"
    report_path = project.repo_path / project.logs_dir / "flow_qa" / project.project_id / "latest" / "validation_summary.md"
    raw = _read_json(results_path)
    rows = raw if isinstance(raw, list) else ([raw] if raw else [])
    statuses = [str(row.get("status", "UNKNOWN")) for row in rows if isinstance(row, dict)]
    if not statuses:
        verdict = "UNKNOWN"
    elif "FAIL" in statuses:
        verdict = "FAIL"
    elif "BLOCKED" in statuses:
        verdict = "BLOCKED"
    elif "WARN" in statuses:
        verdict = "WARN"
    elif any(status == "PASS" for status in statuses):
        verdict = "PASS"
    else:
        verdict = "UNKNOWN"
    return {
        "status": verdict,
        "results_path": str(results_path),
        "report_path": str(report_path),
        "flows": len(statuses),
    }


def _open_blockers(project: ProjectConfig, limit: int = 5) -> list[str]:
    path = project.project_control_path / "BLOCKERS.md"
    if not path.exists():
        return []
    titles: list[str] = []
    current_title = ""
    in_code = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("## "):
            current_title = stripped.lstrip("# ").strip()
        if stripped.lower() == "status: open" and current_title:
            titles.append(current_title)
    return titles[-limit:][::-1]


def _claude_readiness(project: ProjectConfig, provider_payload: dict[str, Any]) -> dict[str, Any]:
    claude_cli_detected, _ = detect_claude_cli(project)
    providers = {item.get("provider_id"): item for item in provider_payload.get("providers", [])}
    claude_code = providers.get("claude_code", {})
    claude_sdk = providers.get("claude_agent_sdk", {})
    sdk_meta = claude_sdk.get("metadata", {})
    key_status = sdk_meta.get("env_status", "MISSING")
    sdk_dry = claude_sdk_dry_run_health(project)
    return {
        "claude_code_cli_detected": claude_cli_detected,
        "claude_code_manual_handoff_ready": bool(claude_code.get("configured")),
        "claude_code_automatic_execution_enabled": project.allow_automatic_builder_execution,
        "claude_agent_sdk_provider_scaffold_exists": bool(claude_sdk),
        "anthropic_api_key_status": key_status,
        "anthropic_api_key_present": key_status == "PRESENT_VALUE_HIDDEN",
        "sdk_package_detected": bool(sdk_meta.get("sdk_package_detected", False)),
        "claude_sdk_dry_run_verdict": sdk_dry["verdict"],
        "claude_agent_sdk_external_call_tested": False,
        "live_claude_calls": "DISABLED_EXPECTED",
        "automatic_claude_execution": "DISABLED_EXPECTED" if not project.allow_automatic_builder_execution else "ENABLED",
        "status": "DRY_RUN_READY" if sdk_dry["verdict"] == "CLAUDE_SDK_DRY_RUN_READY" else ("READY_FOR_MANUAL_HANDOFF" if claude_code.get("configured") else "PARTIAL"),
        "required_before_sdk_integration": [
            "ANTHROPIC_API_KEY added locally.",
            "Provider dry-run mode.",
            "Sandbox/worktree policy.",
            "Allowlist/denylist.",
            "Cost/budget gates.",
            "Post-builder policy fixtures passing.",
            "Human approval for first live Claude SDK call.",
        ],
    }


def build_health(project: ProjectConfig) -> dict[str, Any]:
    provider_payload = build_registry(project.project_id)
    fixture = policy_fixture_health(project)
    flow = _latest_flow_status(project)
    v2_report = run_check(project)
    v2_payload = v2_report.to_dict()
    blockers_summary = summarize_blockers(project)
    lock = lock_status(project.project_id)
    logs = project.repo_path / project.logs_dir
    backend = _read_json(logs / f"{project.project_id}_backend_audit_latest.json")
    readiness = _read_json(logs / f"{project.project_id}_readiness_latest.json")
    design = _read_json(logs / f"{project.project_id}_design_director_latest.json")
    research = _read_json(logs / f"{project.project_id}_research_director_latest.json")
    orchestrator = builder_orchestrator_status(project)
    post_builder_policy_available = (project.repo_path / "project_autopilot" / "post_builder_policy.py").exists()
    control_center_path = logs / "control_center" / f"{project.project_id}_control_center.html"
    halt_path = project.project_control_path / "HALT_AUTOPILOT.md"
    halt_active = halt_path.exists()
    claude = _claude_readiness(project, provider_payload)
    claude_dry = claude_sdk_dry_run_health(project)

    subsystem_statuses = {
        "provider_registry": "PASS" if provider_payload.get("configured_provider_count", 0) >= 1 else "FAIL",
        "design_director": design.get("verdict", "UNKNOWN"),
        "research_director": research.get("status", "UNKNOWN"),
        "builder_orchestrator": "PASS" if orchestrator.get("status") == "READY_FOR_MANUAL_ORCHESTRATION" else "WARN",
        "autopilot_v2_check": v2_payload.get("verdict", "UNKNOWN"),
        "post_builder_policy": "PASS" if post_builder_policy_available else "FAIL",
        "policy_fixture_suite": fixture["status"],
        "flow_qa": "AVAILABLE" if (project.repo_path / "project_autopilot" / "flow_qa.py").exists() else "MISSING",
        "latest_mock_e2e": flow["status"],
        "backend_audit": backend.get("readiness", "UNKNOWN"),
        "mira_readiness": readiness.get("overall", "UNKNOWN"),
        "control_center": "AVAILABLE" if control_center_path.exists() else "MISSING",
        "halt": "ACTIVE" if halt_active else "PASS",
        "run_lock": "LOCKED" if lock.get("locked") else ("STALE" if lock.get("stale") else "PASS"),
        "scheduler": "DISABLED_EXPECTED",
        "automatic_claude_execution": "DISABLED_EXPECTED" if not project.allow_automatic_builder_execution else "ENABLED",
        "claude_agent_sdk_provider": "DRY_RUN_CONFIGURED" if claude["anthropic_api_key_present"] else "NOT_CONFIGURED",
        "claude_sdk_dry_run": claude_dry["verdict"],
    }

    blockers: list[str] = []
    if halt_active:
        blockers.append("HALT_AUTOPILOT is active.")
    if fixture["status"] == "FAIL":
        blockers.append("Policy fixture suite has failing fixtures.")
    if provider_payload.get("configured_provider_count", 0) < 1:
        blockers.append("No configured builder provider.")
    if v2_payload.get("verdict") == "AUTOPILOT_V2_BLOCKED":
        blockers.append("Autopilot v2 readiness is blocked.")
    if project.allow_automatic_builder_execution:
        blockers.append("Automatic builder execution is enabled unexpectedly.")
    if claude_dry["verdict"] == "CLAUDE_SDK_DRY_RUN_BLOCKED":
        blockers.append("Claude SDK dry-run validator is blocked.")

    warnings: list[str] = []
    if fixture["status"] == "UNKNOWN":
        warnings.append("Policy fixture suite has no latest result.")
    if claude["anthropic_api_key_present"] is False:
        warnings.append("Claude Agent SDK is not configured; this is expected before SDK integration.")
    if claude_dry["verdict"] == "UNKNOWN":
        warnings.append("Claude SDK dry-run validator has no latest result.")
    elif claude_dry["verdict"] == "CLAUDE_SDK_DRY_RUN_PARTIAL":
        warnings.append("Claude SDK dry-run validator is partial; live Claude calls remain disabled.")
    if backend.get("readiness") == "PARTIAL_READY":
        warnings.append("Backend audit is partial due to product/Supabase manual verification blockers.")
    if readiness.get("overall") and "BLOCKED" in str(readiness.get("overall")):
        warnings.append("MIRA product readiness has blockers; this does not block Autopilot control-plane operation.")

    if blockers:
        overall = "AUTOPILOT_BLOCKED"
    elif warnings:
        overall = "AUTOPILOT_PARTIAL"
    else:
        overall = "AUTOPILOT_OPERATIONAL"

    next_actions = [
        f"Run policy fixtures: {fixture['command']}",
        f"Run doctor: python -B project_autopilot/agent_loop.py --project {project.project_id} --doctor",
        f"Generate Control Center: python -B project_autopilot/agent_loop.py --project {project.project_id} --control-center",
    ]
    if not claude["anthropic_api_key_present"]:
        next_actions.append("For Claude SDK later: add ANTHROPIC_API_KEY locally, then implement dry-run mode before any live call.")
    else:
        next_actions.append("For Claude SDK later: request explicit approval before the first controlled analysis call.")
    next_actions.append("Keep scheduler and automatic Claude execution disabled until explicit approval.")

    evidence_paths = {
        "autopilot_health_md": str(logs / f"{project.project_id}_autopilot_health_latest.md"),
        "autopilot_health_json": str(logs / f"{project.project_id}_autopilot_health_latest.json"),
        "policy_fixture_report": fixture["report_path"],
        "provider_registry_report": str(logs / f"{project.project_id}_provider_registry_latest.md"),
        "autopilot_v2_check_report": str(logs / f"{project.project_id}_autopilot_v2_check_latest.md"),
        "claude_sdk_dry_run_report": str(logs / f"{project.project_id}_claude_sdk_dry_run_latest.md"),
        "claude_sdk_dry_run_json": str(logs / f"{project.project_id}_claude_sdk_dry_run_latest.json"),
        "backend_audit_report": str(logs / f"{project.project_id}_backend_audit_latest.md"),
        "mira_readiness_report": str(logs / f"{project.project_id}_readiness_latest.json"),
        "control_center": str(control_center_path),
    }

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        "project_name": project.project_name,
        "overall_verdict": overall,
        "subsystem_statuses": subsystem_statuses,
        "blockers": blockers[:5],
        "external_manual_blockers": _open_blockers(project, limit=5),
        "warnings": warnings[:10],
        "next_actions": next_actions[:5],
        "safe_next_sprint_recommendation": "Prepare a human-approved controlled Claude SDK analysis call; do not enable builder execution yet.",
        "commands_to_run": [
            f"python -B project_autopilot/agent_loop.py --project {project.project_id} --doctor",
            f"python -B project_autopilot/agent_loop.py --project {project.project_id} --autopilot-health",
            f"python -B project_autopilot/agent_loop.py --project {project.project_id} --policy-fixtures",
            f"python -B project_autopilot/agent_loop.py --project {project.project_id} --local-plan",
            f"python -B project_autopilot/agent_loop.py --project {project.project_id} --control-center",
        ],
        "evidence_paths": evidence_paths,
        "safety_flags": {
            "scheduler_enabled": False,
            "automatic_claude_execution_enabled": project.allow_automatic_builder_execution,
            "paid_api_mode": project.paid_api_mode,
            "allow_paid_image_generation": project.allow_paid_image_generation,
            "allow_paid_video_generation": project.allow_paid_video_generation,
            "external_api_calls_made": False,
            "anthropic_api_called": False,
            "openai_api_called": False,
            "supabase_sql_executed": False,
        },
        "claude_integration_readiness": claude,
        "claude_sdk_dry_run": claude_dry,
        "policy_fixture_suite": fixture,
        "provider_registry": {
            "provider_count": provider_payload.get("provider_count", 0),
            "configured_provider_count": provider_payload.get("configured_provider_count", 0),
            "recommended_next_provider_action": provider_payload.get("recommended_next_provider_action", ""),
        },
        "blocker_counts": {
            "open": blockers_summary.open_count,
            "resolved": blockers_summary.resolved_count,
            "parked": blockers_summary.parked_count,
        },
    }


def write_reports(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    logs = project.repo_path / project.logs_dir
    logs.mkdir(parents=True, exist_ok=True)
    md_path = logs / f"{project.project_id}_autopilot_health_latest.md"
    json_path = logs / f"{project.project_id}_autopilot_health_latest.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Project Autopilot Operational Health",
        "",
        f"Generated: {payload['generated_at_utc']}",
        f"Project: {payload['project_name']} ({payload['project_id']})",
        f"Overall verdict: {payload['overall_verdict']}",
        "",
        "## Subsystems",
    ]
    for name, status in payload["subsystem_statuses"].items():
        lines.append(f"- {name}: {status}")
    lines.extend(["", "## Claude Integration Readiness"])
    claude = payload["claude_integration_readiness"]
    lines.extend([
        f"- Claude Code CLI detected: {'yes' if claude['claude_code_cli_detected'] else 'no'}",
        f"- Claude Code manual handoff ready: {'yes' if claude['claude_code_manual_handoff_ready'] else 'no'}",
        f"- Claude Code automatic execution enabled: {'yes' if claude['claude_code_automatic_execution_enabled'] else 'no'}",
        f"- Claude Agent SDK scaffold exists: {'yes' if claude['claude_agent_sdk_provider_scaffold_exists'] else 'no'}",
        f"- ANTHROPIC_API_KEY status: {claude['anthropic_api_key_status']}",
        f"- SDK package detected: {'yes' if claude['sdk_package_detected'] else 'no'}",
        f"- Claude SDK dry-run verdict: {claude['claude_sdk_dry_run_verdict']}",
        f"- Live Claude calls: {claude['live_claude_calls']}",
        f"- Claude Agent SDK external call tested: {'yes' if claude['claude_agent_sdk_external_call_tested'] else 'no'}",
        "",
        "Required before SDK integration:",
    ])
    lines.extend(f"- {item}" for item in claude["required_before_sdk_integration"])
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {item}" for item in payload["blockers"] or ["None"])
    lines.extend(["", "## External / Manual Blockers"])
    lines.extend(f"- {item}" for item in payload["external_manual_blockers"] or ["None"])
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in payload["warnings"] or ["None"])
    lines.extend(["", "## Next Actions"])
    lines.extend(f"- {item}" for item in payload["next_actions"])
    lines.extend(["", "## Evidence Paths"])
    lines.extend(f"- {name}: {path}" for name, path in payload["evidence_paths"].items())
    lines.extend(["", "Safety: no external APIs were called, no secrets were printed, no SQL was executed, and no builders were executed."])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot operational health")
    parser.add_argument("--project", default="mira")
    args = parser.parse_args()

    project = load_project_config(args.project)
    payload = build_health(project)
    md_path, json_path = write_reports(project, payload)
    print(f"Autopilot Health: {payload['overall_verdict']}")
    print(f"  Policy fixtures: {payload['policy_fixture_suite']['status']} ({payload['policy_fixture_suite']['passed']}/{payload['policy_fixture_suite']['total']})")
    print(f"  Providers configured: {payload['provider_registry']['configured_provider_count']}/{payload['provider_registry']['provider_count']}")
    print(f"  Claude SDK key status: {payload['claude_integration_readiness']['anthropic_api_key_status']}")
    print(f"  Claude SDK dry-run: {payload['claude_integration_readiness']['claude_sdk_dry_run_verdict']}")
    print(f"  Scheduler: {payload['subsystem_statuses']['scheduler']}")
    print(f"  Automatic Claude execution: {payload['subsystem_statuses']['automatic_claude_execution']}")
    print(f"  Blockers: {', '.join(payload['blockers']) if payload['blockers'] else 'none'}")
    print(f"  Next action: {payload['next_actions'][0] if payload['next_actions'] else 'none'}")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    return 2 if payload["overall_verdict"] == "AUTOPILOT_BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
