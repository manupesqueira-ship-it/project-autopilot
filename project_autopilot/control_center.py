"""Project Autopilot Control Center v0.3 — Operational Graph + Node Details.

Generates a read-only, self-contained HTML report from local logs, evidence,
project control, and config files. No server, no auth, no external deps.

Usage:
    python -B project_autopilot/control_center.py --project mira

Output:
    logs/control_center/<project_id>_control_center.html
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from config import ProjectConfig, load_project_config
from blocker_summary import summarize_blockers
from research_log import summarize_research, read_research_entries
from run_history import read_events, recent_events, summarize_recent_runs
from run_metrics import latest_run_metrics
from run_lock import lock_status
from task_state import load_task_state


# ---------------------------------------------------------------------------
# Data collection helpers — each returns a dict, never crashes
# ---------------------------------------------------------------------------

def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _read_text(path: Path, limit: int = 0) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if limit:
            lines = text.splitlines()[:limit]
            return "\n".join(lines)
        return text
    except Exception:
        return ""


def _first_heading(text: str, level: int = 2) -> str:
    prefix = "#" * level + " "
    for line in text.splitlines():
        if line.strip().startswith(prefix):
            return line.strip()[len(prefix):].strip()
    return ""


def _extract_current_task(task_queue_text: str) -> dict[str, str]:
    """Extract current priority task from TASK_QUEUE.md."""
    result: dict[str, str] = {"title": "", "criteria": ""}
    lines = task_queue_text.splitlines()
    in_priority = False
    criteria_lines: list[str] = []
    in_criteria = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## Current Priority") or stripped.startswith("## Current"):
            in_priority = True
            continue
        if in_priority and not result["title"] and stripped.startswith("### "):
            result["title"] = stripped[4:].strip()
            continue
        if in_priority and ("acceptance criteria" in stripped.lower() or "criteria" in stripped.lower()) and stripped.startswith("#"):
            in_criteria = True
            continue
        if in_criteria:
            if stripped.startswith("## ") or stripped.startswith("# "):
                break
            if stripped:
                criteria_lines.append(stripped)
        if in_priority and stripped.startswith("## ") and not stripped.startswith("## Current"):
            break

    result["criteria"] = "\n".join(criteria_lines[:10])
    return result


def _parse_blockers_detail(text: str) -> list[dict[str, str]]:
    """Parse BLOCKERS.md into structured entries."""
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    in_code = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("### "):
            if current.get("title"):
                entries.append(current)
            current = {"title": stripped[4:].strip()}
            continue
        low = stripped.lower()
        if low.startswith("status:"):
            current["status"] = stripped.split(":", 1)[1].strip()
        elif low.startswith("severity:"):
            current["severity"] = stripped.split(":", 1)[1].strip()
        elif low.startswith("source:"):
            current["source"] = stripped.split(":", 1)[1].strip()

    if current.get("title"):
        entries.append(current)
    return entries


def _parse_human_questions(text: str) -> list[dict[str, str]]:
    """Parse HUMAN_QUESTIONS.md into structured entries."""
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    in_code = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("### "):
            if current.get("title"):
                entries.append(current)
            current = {"title": stripped[4:].strip()}
            continue
        low = stripped.lower()
        if low.startswith("status:"):
            current["status"] = stripped.split(":", 1)[1].strip()
        elif low.startswith("severity:"):
            current["severity"] = stripped.split(":", 1)[1].strip()

    if current.get("title"):
        entries.append(current)
    return entries


def _latest_evidence_bundle(project: ProjectConfig) -> dict[str, Any]:
    evidence_dir = project.repo_path / project.logs_dir / "evidence" / project.project_id
    if not evidence_dir.exists():
        return {}
    bundles = sorted(evidence_dir.iterdir(), reverse=True)
    for bundle in bundles:
        meta = bundle / "metadata.json"
        if meta.exists():
            return _read_json(meta)
    return {}


def _backend_audit_json(project: ProjectConfig) -> dict[str, Any]:
    path = project.repo_path / project.logs_dir / f"{project.project_id}_backend_audit_latest.json"
    return _read_json(path)


def _flow_qa_data(project: ProjectConfig) -> dict[str, Any]:
    """Collect latest Flow QA results if available."""
    results_path = project.repo_path / "logs" / "flow_qa" / project.project_id / "latest" / "flow_results.json"
    report_path = project.repo_path / "logs" / "flow_qa" / project.project_id / "latest" / "flow_report.md"
    data: dict[str, Any] = {
        "exists": results_path.exists(),
        "report_path": str(report_path) if report_path.exists() else "",
        "flows": [],
        "overall_verdict": "NOT_RUN",
    }
    if results_path.exists():
        try:
            raw = json.loads(results_path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                data["flows"] = raw
            else:
                data["flows"] = [raw]
            verdicts = [f.get("status", "UNKNOWN") for f in data["flows"]]
            if "FAIL" in verdicts:
                data["overall_verdict"] = "FAIL"
            elif "BLOCKED" in verdicts:
                data["overall_verdict"] = "BLOCKED"
            elif all(v in ("PASS", "SKIPPED") for v in verdicts):
                data["overall_verdict"] = "PASS" if "PASS" in verdicts else "SKIPPED"
            elif "WARN" in verdicts:
                data["overall_verdict"] = "WARN"
            else:
                data["overall_verdict"] = "MIXED"
        except Exception:
            data["overall_verdict"] = "ERROR"
    return data


def _readiness_data(project: ProjectConfig) -> dict[str, Any]:
    """Collect latest MIRA secure MVP readiness report if available."""
    path = project.repo_path / project.logs_dir / "mira_readiness_latest.json"
    return _read_json(path) if path.exists() else {"overall": "NOT_RUN", "categories": []}


def _autopilot_state(project: ProjectConfig) -> dict[str, Any]:
    path = project.repo_path / project.logs_dir / f"{project.project_id}_autopilot_state.json"
    return _read_json(path)


def _browser_qa_from_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "verdict": state.get("browser_qa_verdict", ""),
        "mode": state.get("browser_qa_mode", ""),
        "passed": state.get("browser_qa_passed"),
        "summary": state.get("browser_qa_summary", {}),
        "report_path": state.get("last_browser_qa", ""),
        "runtime_url": state.get("browser_qa_selected_runtime_url", ""),
    }


def _infer_overall_status(
    blockers_open: int,
    halt_active: bool,
    bqa_verdict: str,
    latest_evidence: dict[str, Any],
) -> str:
    if halt_active or blockers_open > 0:
        return "BLOCKED"
    commands_failed = latest_evidence.get("commands_failed", latest_evidence.get("failed_command_count", 0))
    if commands_failed and commands_failed > 0:
        return "WARN"
    if bqa_verdict and bqa_verdict not in ("PASS", ""):
        return "WARN"
    return "OK"


def _infer_next_step(
    blockers_open: int,
    halt_active: bool,
    bqa_verdict: str,
    task_state_val: str,
    correction_exists: bool,
    qa_verdict: str | None,
) -> str:
    if halt_active:
        return "Remove HALT_AUTOPILOT.md to resume cycles."
    if blockers_open > 0:
        return "Resolve open blockers in BLOCKERS.md."
    if bqa_verdict == "FAIL":
        return "Fix Browser QA failures, then re-run --browser-qa."
    if bqa_verdict == "SKIPPED_DEV_SERVER_DOWN":
        return "Start the dev server (npm run dev), then run --browser-qa."
    if correction_exists:
        return "Use the correction prompt to fix issues, then re-run --post-builder."
    if qa_verdict and "FAIL" in str(qa_verdict).upper():
        return "Address QA failures and re-run post-builder intake."
    if task_state_val == "planned":
        return "Run --local-plan or --handoff-claude to start the next task."
    if task_state_val == "passed":
        return "Commit the passing work, then update TASK_QUEUE.md."
    if task_state_val in ("implemented", "validating"):
        return "Run --post-builder to validate builder output."
    if task_state_val == "blocked":
        return "Resolve the blocker, then resume work."
    return "Review TASK_QUEUE.md and plan next work."


def _infer_stage(data: dict[str, Any]) -> str:
    """Derive current lifecycle stage from project state."""
    task_state = data.get("task_state", {}).get("state", "unknown")
    has_evidence = bool(data.get("latest_evidence"))
    bqa_verdict = data.get("browser_qa", {}).get("verdict", "")
    qa_verdict = data.get("latest_evidence", {}).get("qa_verdict")
    backend_ready = data.get("backend_readiness", "")
    halt = data.get("halt_active", False)

    if halt:
        return "blocked"
    if task_state == "unknown" and not has_evidence:
        return "setup"
    if task_state == "planned":
        return "planning"
    if task_state == "assigned":
        return "builder_handoff"
    if task_state in ("implemented",):
        return "implementation"
    if task_state == "validating":
        return "validation"
    if qa_verdict:
        qa_str = str(qa_verdict).upper()
        if "PASS" in qa_str:
            if backend_ready in ("READY", "READY_FOR_MANUAL_E2E"):
                return "scheduler_readiness"
            return "qa_verdict"
        if "FAIL" in qa_str:
            return "qa_verdict"
        return "validation"
    if task_state == "passed":
        return "scheduler_readiness"
    if has_evidence:
        return "validation"
    return "research"


def _infer_qa_branch(data: dict[str, Any]) -> str:
    """Derive which QA outcome branch is active."""
    qa = data.get("latest_evidence", {}).get("qa_verdict")
    if not qa:
        return ""
    v = str(qa).upper()
    if "PASS" in v:
        return "pass"
    if "FAIL" in v and "FIX" in v:
        return "fail_fix"
    if "HUMAN" in v or "DECISION" in v:
        return "human_decision"
    if "RESEARCH" in v:
        return "research_required"
    if "BLOCK" in v:
        return "blocked"
    if "FAIL" in v:
        return "fail_fix"
    return ""


# ---------------------------------------------------------------------------
# Evidence path helpers
# ---------------------------------------------------------------------------

def _collect_evidence_paths(project: ProjectConfig, data: dict[str, Any]) -> list[dict[str, Any]]:
    """Build a list of evidence artifacts with exists/path/description."""
    pid = project.project_id
    logs = project.repo_path / project.logs_dir
    ctrl = project.project_control_path

    def _entry(name: str, desc: str, path: Path, stage: str) -> dict[str, Any]:
        try:
            resolved = path if path.is_absolute() else (project.repo_path / path)
            exists = resolved.exists()
            rel = str(resolved.relative_to(project.repo_path))
        except (ValueError, OSError):
            exists = False
            rel = str(path)
        return {"name": name, "desc": desc, "path": rel, "exists": exists, "stage": stage}

    evidence_dir = logs / "evidence" / pid
    bundle_path = Path("--")
    if evidence_dir.exists():
        bundles = sorted(evidence_dir.iterdir(), reverse=True)
        for b in bundles:
            if (b / "metadata.json").exists():
                bundle_path = b
                break

    items = [
        _entry("Evidence bundle", "Structured run evidence (commands, diffs, QA)", bundle_path / "metadata.json" if bundle_path != Path("--") else logs / "evidence" / pid / "none", "validation"),
        _entry("Browser QA report", "Route testing, console errors, screenshots", logs / f"{pid}_browser_qa_latest.md", "validation"),
        _entry("Backend audit", "Schema, data-flow, RLS static check", logs / f"{pid}_backend_audit_latest.json", "validation"),
        _entry("Builder prompt", "Latest prompt sent to builder", Path(data.get("builder_prompt_path", "")) if data.get("builder_prompt_path") else logs / f"{pid}_builder_prompt_latest.md", "builder_handoff"),
        _entry("Correction prompt", "QA-generated fix instructions", logs / f"{pid}_correction_prompt_latest.md", "qa_verdict"),
        _entry("Post-builder report", "Builder output QA intake", logs / f"{pid}_post_builder_latest.md", "qa_verdict"),
        _entry("Run history", "JSONL event stream", logs / f"run_history/{pid}.jsonl", "observability"),
        _entry("Research index", "Research request log", logs / f"research/{pid}_index.jsonl", "research"),
        _entry("Task state", "Current task lifecycle state", logs / f"{pid}_task_state.json", "planning"),
        _entry("Autopilot state", "Full autopilot state snapshot", logs / f"{pid}_autopilot_state.json", "observability"),
        _entry("Security alignment plan", "Supabase RLS/auth security audit and migration plan", ctrl / "MIRA_SUPABASE_SECURITY_ALIGNMENT_PLAN.md", "validation"),
        _entry("Manual activation checklist", "Supabase Dashboard manual steps", ctrl / "MIRA_SUPABASE_MANUAL_ACTIVATION_CHECKLIST.md", "planning"),
        _entry("Local auth verification plan", "Post-activation verification steps", ctrl / "MIRA_LOCAL_AUTH_VERIFICATION_PLAN.md", "planning"),
        _entry("RLS decision matrix", "Ownership/storage strategy comparisons", ctrl / "MIRA_RLS_DECISION_MATRIX.md", "planning"),
        _entry("RLS migration draft", "SQL drafts for RLS enablement (DO NOT RUN)", ctrl / "MIRA_RLS_STORAGE_MIGRATION_DRAFT.md", "planning"),
        _entry("Mock generation plan", "QA mock mode design and instructions", ctrl / "MIRA_MOCK_GENERATION_PLAN.md", "validation"),
        _entry("E2E validation plan", "Manual and automated E2E testing instructions", ctrl / "MIRA_E2E_VALIDATION_PLAN.md", "validation"),
        _entry("Flow QA report", "Latest automated flow results", logs / "flow_qa" / pid / "latest" / "flow_report.md", "validation"),
        _entry("Secure MVP readiness", "Overall readiness verdict and category breakdown", logs / "mira_readiness_latest.json", "validation"),
        _entry("Secure MVP runbook", "Human-facing master runbook", ctrl / "MIRA_SECURE_MVP_RUNBOOK.md", "planning"),
        _entry("Sensitive logging audit", "Privacy/logging static scan results", logs / "mira_sensitive_logging_audit_latest.json", "validation"),
        _entry("Privacy logging guardrails", "Logging rules for sensitive data", ctrl / "MIRA_PRIVACY_LOGGING_GUARDRAILS.md", "validation"),
        _entry("Env preflight report", "Supabase env var presence check", logs / "mira_env_preflight_latest.json", "validation"),
        _entry("Auth verification", "Supabase auth foundation check", logs / "mira_supabase_auth_verify_latest.json", "validation"),
        _entry("Security staging report", "RLS/storage staging validation", logs / "mira_security_staging_latest.json", "validation"),
        _entry("RLS staging plan", "Master RLS/storage staging plan", ctrl / "security" / "MIRA_RLS_STORAGE_STAGING_PLAN.md", "planning"),
        _entry("RLS policy matrix", "Per-table RLS policy definitions", ctrl / "security" / "MIRA_RLS_POLICY_MATRIX.md", "planning"),
        _entry("Storage policy matrix", "Per-bucket storage policy definitions", ctrl / "security" / "MIRA_STORAGE_POLICY_MATRIX.md", "planning"),
        _entry("Security test plan", "A/B user test matrix", ctrl / "security" / "MIRA_SECURITY_TEST_PLAN.md", "validation"),
        _entry("Security rollback plan", "RLS/storage rollback procedures", ctrl / "security" / "MIRA_SECURITY_ROLLBACK_PLAN.md", "planning"),
        _entry("Security ownership findings", "API ownership risk review", ctrl / "security" / "MIRA_SECURITY_OWNERSHIP_FINDINGS.md", "validation"),
        _entry("RLS candidate SQL", "Draft RLS policies (DO NOT RUN)", project.repo_path / "supabase" / "drafts" / "rls_candidate_policies.sql", "planning"),
        _entry("Storage candidate SQL", "Draft storage policies (DO NOT RUN)", project.repo_path / "supabase" / "drafts" / "storage_candidate_policies.sql", "planning"),
        _entry("Visual QA report", "Page layout, accessibility, state rendering checks", logs / f"{pid}_visual_qa_latest.md", "validation"),
        _entry("Visual Quality Standard", "Visual design rules and quality bar", ctrl / "visual" / "MIRA_VISUAL_QUALITY_STANDARD.md", "planning"),
        _entry("External Builder Policy", "External tool intake governance", ctrl / "EXTERNAL_BUILDER_POLICY.md", "planning"),
    ]
    return items


# ---------------------------------------------------------------------------
# Collect all data
# ---------------------------------------------------------------------------

def collect_control_center_data(project: ProjectConfig) -> dict[str, Any]:
    """Gather all data for the control center report. Never crashes."""
    now = datetime.now(timezone.utc)
    data: dict[str, Any] = {"generated_at": now.isoformat(), "generated_at_display": now.strftime("%Y-%m-%d %H:%M UTC")}

    # Project config
    data["project_id"] = project.project_id
    data["project_name"] = project.project_name
    data["repo_path"] = str(project.repo_path)
    data["autonomy_mode"] = project.autonomy_mode
    data["intensity_mode"] = project.intensity_mode
    data["builder_primary"] = project.builder_primary
    data["builder_fallback"] = project.builder_fallback
    data["daily_budget"] = project.daily_budget_usd
    data["per_cycle_budget"] = project.per_cycle_budget_usd
    data["monthly_budget"] = project.monthly_budget_usd
    data["paid_api_mode"] = project.paid_api_mode
    data["allow_paid_image"] = project.allow_paid_image_generation
    data["allow_paid_video"] = project.allow_paid_video_generation
    data["max_parallel_agents"] = project.max_parallel_agents
    data["allow_auto_exec"] = project.allow_automatic_builder_execution
    data["telegram_enabled"] = project.telegram_enabled
    data["browser_qa_enabled"] = project.browser_qa_enabled

    # HALT
    halt_path = project.project_control_path / "HALT_AUTOPILOT.md"
    data["halt_active"] = halt_path.exists()

    # Lock
    try:
        data["lock"] = lock_status(project.project_id)
    except Exception:
        data["lock"] = {"locked": False, "stale": False}

    # Task state
    try:
        data["task_state"] = load_task_state(project)
    except Exception:
        data["task_state"] = {"state": "unknown", "history": []}

    # Blockers
    try:
        bs = summarize_blockers(project)
        data["blockers"] = {"open": bs.open_count, "resolved": bs.resolved_count, "parked": bs.parked_count, "latest_open": bs.latest_open_title}
    except Exception:
        data["blockers"] = {"open": 0, "resolved": 0, "parked": 0, "latest_open": None}

    blockers_text = _read_text(project.project_control_path / "BLOCKERS.md")
    data["blockers_detail"] = _parse_blockers_detail(blockers_text)

    # Human questions
    hq_text = _read_text(project.project_control_path / "HUMAN_QUESTIONS.md")
    data["human_questions"] = _parse_human_questions(hq_text)

    # Task queue
    tq_text = _read_text(project.project_control_path / "TASK_QUEUE.md")
    data["current_task"] = _extract_current_task(tq_text)

    # Current state snippet
    data["current_state_snippet"] = _read_text(project.project_control_path / "CURRENT_STATE.md", limit=30)

    # Autopilot state
    ap_state = _autopilot_state(project)
    data["autopilot_state"] = ap_state

    # Browser QA
    data["browser_qa"] = _browser_qa_from_state(ap_state)

    # Latest evidence
    data["latest_evidence"] = _latest_evidence_bundle(project)

    # Latest run metrics
    try:
        data["latest_metrics"] = latest_run_metrics(project)
    except Exception:
        data["latest_metrics"] = None

    # Recent runs
    try:
        data["recent_runs"] = summarize_recent_runs(project.project_id, limit=5)
    except Exception:
        data["recent_runs"] = []

    # Activity timeline
    try:
        data["recent_events"] = recent_events(project, limit=20)
    except Exception:
        data["recent_events"] = []

    # Research
    try:
        data["research"] = summarize_research(project)
    except Exception:
        data["research"] = {"count": 0, "deep_research_pending_approval": 0, "completed_count": 0, "latest": None}

    # Backend audit
    data["backend_audit"] = _backend_audit_json(project)

    # Flow QA
    data["flow_qa"] = _flow_qa_data(project)

    # Secure MVP Readiness
    data["readiness"] = _readiness_data(project)

    # Cost
    cost = data["latest_evidence"].get("cost_snapshot", {})
    data["cost"] = cost if cost else {}

    # Risk
    risk = data["latest_evidence"].get("risk_summary", {})
    data["risk"] = risk if risk else {}

    # File paths
    logs = project.repo_path / project.logs_dir
    data["builder_prompt_path"] = str(project.latest_prompt_path) if project.latest_prompt_path else ""
    correction_path = logs / f"{project.project_id}_correction_prompt_latest.md"
    data["correction_prompt_exists"] = correction_path.exists()
    data["correction_prompt_path"] = str(correction_path.relative_to(project.repo_path)) if correction_path.exists() else ""

    bqa_report = logs / f"{project.project_id}_browser_qa_latest.md"
    data["browser_qa_report_exists"] = bqa_report.exists()

    backend_report = logs / f"{project.project_id}_backend_audit_latest.md"
    data["backend_audit_exists"] = backend_report.exists()
    data["backend_readiness"] = ap_state.get("backend_readiness", data["backend_audit"].get("readiness", ""))

    # Overall status
    data["overall_status"] = _infer_overall_status(
        data["blockers"]["open"],
        data["halt_active"],
        data["browser_qa"].get("verdict", ""),
        data["latest_evidence"],
    )

    # Next step
    data["next_step"] = _infer_next_step(
        data["blockers"]["open"],
        data["halt_active"],
        data["browser_qa"].get("verdict", ""),
        data["task_state"].get("state", ""),
        data["correction_prompt_exists"],
        data["latest_evidence"].get("qa_verdict"),
    )

    # Current lifecycle stage
    data["current_stage"] = _infer_stage(data)

    # QA branch
    data["qa_branch"] = _infer_qa_branch(data)

    # Evidence paths
    data["evidence_paths"] = _collect_evidence_paths(project, data)

    return data


# ---------------------------------------------------------------------------
# HTML rendering — v0.3 Operational Graph
# ---------------------------------------------------------------------------

_CSS = """\
:root {
    --bg: #f5f6f8;
    --surface: #ffffff;
    --surface-alt: #fafbfc;
    --border: #e2e5ea;
    --border-light: #edf0f3;
    --text: #1a1d23;
    --text-secondary: #5a6170;
    --text-muted: #8c92a0;
    --mono: 'SF Mono','Cascadia Code','Consolas','Monaco',monospace;
    --sans: -apple-system,BlinkMacSystemFont,'Segoe UI','Inter',Roboto,sans-serif;
    --radius: 10px;
    --radius-sm: 6px;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.04),0 1px 2px rgba(0,0,0,0.06);
    --shadow: 0 2px 8px rgba(0,0,0,0.06),0 1px 3px rgba(0,0,0,0.08);
    --green: #16a34a; --green-bg: #dcfce7; --green-border: #bbf7d0; --green-text: #166534;
    --yellow: #ca8a04; --yellow-bg: #fef9c3; --yellow-border: #fef08a; --yellow-text: #854d0e;
    --red: #dc2626; --red-bg: #fee2e2; --red-border: #fecaca; --red-text: #991b1b;
    --blue: #2563eb; --blue-bg: #dbeafe; --blue-border: #bfdbfe; --blue-text: #1e40af;
    --gray: #64748b; --gray-bg: #f1f5f9; --gray-border: #e2e8f0; --gray-text: #475569;
    --purple: #7c3aed; --purple-bg: #ede9fe; --purple-border: #ddd6fe; --purple-text: #5b21b6;
    --amber: #d97706; --amber-bg: #fef3c7; --amber-border: #fde68a; --amber-text: #92400e;
}
*,*::before,*::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: var(--sans); background: var(--bg); color: var(--text);
    line-height: 1.55; padding: 24px 28px; max-width: 1320px; margin: 0 auto;
    -webkit-font-smoothing: antialiased;
}
h1 { font-size: 1.65rem; font-weight: 700; letter-spacing: -0.02em; }
h2 {
    font-size: 0.78rem; font-weight: 600; letter-spacing: 0.06em;
    text-transform: uppercase; color: var(--text-secondary);
    margin: 28px 0 12px; padding-bottom: 7px;
    border-bottom: 2px solid var(--border);
}
h3 { font-size: 0.92rem; font-weight: 600; margin: 0 0 8px; }
h4 { font-size: 0.82rem; font-weight: 600; margin: 0 0 4px; }

/* Badges */
.badge {
    display: inline-flex; align-items: center; padding: 2px 9px;
    border-radius: 20px; font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.04em; text-transform: uppercase; white-space: nowrap;
}
.badge-ok { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }
.badge-warn { background: var(--yellow-bg); color: var(--yellow-text); border: 1px solid var(--yellow-border); }
.badge-amber { background: var(--amber-bg); color: var(--amber-text); border: 1px solid var(--amber-border); }
.badge-fail,.badge-blocked { background: var(--red-bg); color: var(--red-text); border: 1px solid var(--red-border); }
.badge-info { background: var(--blue-bg); color: var(--blue-text); border: 1px solid var(--blue-border); }
.badge-na { background: var(--gray-bg); color: var(--gray-text); border: 1px solid var(--gray-border); }
.badge-purple { background: var(--purple-bg); color: var(--purple-text); border: 1px solid var(--purple-border); }

/* Cards */
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 16px 18px; margin-bottom: 12px;
    box-shadow: var(--shadow-sm);
}
.card-accent-green { border-left: 4px solid var(--green); }
.card-accent-yellow { border-left: 4px solid var(--yellow); }
.card-accent-red { border-left: 4px solid var(--red); }
.card-accent-blue { border-left: 4px solid var(--blue); }
.card-accent-purple { border-left: 4px solid var(--purple); }
.card-accent-amber { border-left: 4px solid var(--amber); }

/* Grid */
.grid { display: grid; gap: 12px; }
.grid-2 { grid-template-columns: 1fr 1fr; }
.grid-3 { grid-template-columns: 1fr 1fr 1fr; }
.grid-4 { grid-template-columns: repeat(4, 1fr); }
.grid-auto { grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
@media (max-width: 900px) { .grid-2,.grid-3,.grid-4 { grid-template-columns: 1fr; } }

/* KV */
.kv { margin: 4px 0; display: flex; gap: 6px; align-items: baseline; flex-wrap: wrap; }
.kv-label { color: var(--text-muted); font-size: 0.78rem; font-weight: 500; }
.kv-value { font-weight: 500; font-size: 0.85rem; }
.kv-mono { font-family: var(--mono); font-size: 0.78rem; word-break: break-all; }

/* Hero */
.hero {
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 22px 26px; margin-bottom: 16px; box-shadow: var(--shadow);
}
.hero-top { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }
.hero-title { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.hero-meta { color: var(--text-muted); font-size: 0.78rem; margin-top: 3px; }
.hero-status { font-size: 0.82rem; font-weight: 700; padding: 5px 14px; border-radius: 20px; letter-spacing: 0.05em; }
.hero-status-ok { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }
.hero-status-warn { background: var(--yellow-bg); color: var(--yellow-text); border: 1px solid var(--yellow-border); }
.hero-status-blocked { background: var(--red-bg); color: var(--red-text); border: 1px solid var(--red-border); }

/* Metrics */
.metrics-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-top: 14px; }
.metric { text-align: center; padding: 10px 6px; background: var(--surface-alt); border-radius: var(--radius-sm); border: 1px solid var(--border-light); }
.metric-value { font-size: 1.2rem; font-weight: 700; line-height: 1.2; }
.metric-label { font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }

/* What-happens-next panel */
.whn-panel {
    background: linear-gradient(135deg, var(--blue-bg), #f0f4ff);
    border: 1px solid var(--blue-border); border-radius: var(--radius);
    padding: 16px 20px; margin-bottom: 16px;
}
.whn-title { font-size: 0.82rem; font-weight: 700; color: var(--blue-text); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 8px; }
.whn-action { font-weight: 600; font-size: 0.92rem; color: var(--text); margin-bottom: 6px; }
.whn-detail { font-size: 0.82rem; color: var(--text-secondary); }

/* Command block */
.cmd-block {
    background: #1e293b; color: #e2e8f0; border-radius: var(--radius-sm);
    padding: 8px 12px; font-family: var(--mono); font-size: 0.78rem;
    margin: 6px 0; user-select: all; cursor: text;
}

/* ================================================================
   OPERATIONAL GRAPH — branching flow map via CSS grid
   ================================================================ */
.op-graph {
    position: relative; padding: 12px 0;
}
/* Each lane is a row in the flow */
.op-lane {
    display: flex; align-items: flex-start; gap: 0;
    margin-bottom: 2px; position: relative;
}
.op-lane-label {
    width: 140px; flex-shrink: 0; padding: 8px 10px 8px 0;
    font-size: 0.74rem; font-weight: 600; color: var(--text-secondary);
    text-transform: uppercase; letter-spacing: 0.04em;
    text-align: right; border-right: 2px solid var(--border);
    min-height: 42px; display: flex; align-items: center; justify-content: flex-end;
}
.op-lane-label-active { color: var(--blue); border-right-color: var(--blue); }
.op-lane-label-done { color: var(--green); border-right-color: var(--green); }
.op-lane-label-blocked { color: var(--red); border-right-color: var(--red); }
.op-lane-nodes {
    display: flex; align-items: center; gap: 6px;
    padding: 4px 0 4px 14px; flex-wrap: wrap;
}

/* Node chip */
.op-node {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 5px 11px; border-radius: 16px;
    font-size: 0.73rem; font-weight: 500;
    border: 1.5px solid var(--border); background: var(--surface);
    white-space: nowrap; cursor: default;
    transition: box-shadow 0.15s;
}
.op-node-done { border-color: var(--green-border); background: var(--green-bg); color: var(--green-text); }
.op-node-active { border-color: var(--blue); background: var(--blue-bg); color: var(--blue-text); box-shadow: 0 0 0 2px rgba(37,99,235,0.18); font-weight: 600; }
.op-node-amber { border-color: var(--amber-border); background: var(--amber-bg); color: var(--amber-text); }
.op-node-fail { border-color: var(--red-border); background: var(--red-bg); color: var(--red-text); }
.op-node-disabled { border-color: var(--gray-border); background: var(--gray-bg); color: var(--gray-text); opacity: 0.6; }
.op-node-pending { border-color: var(--border); background: var(--surface-alt); color: var(--text-muted); }
.op-node-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.op-node-dot-done { background: var(--green); }
.op-node-dot-active { background: var(--blue); }
.op-node-dot-amber { background: var(--amber); }
.op-node-dot-fail { background: var(--red); }
.op-node-dot-disabled { background: var(--gray); }
.op-node-dot-pending { background: var(--text-muted); }

/* Branch connector */
.op-branch { color: var(--text-muted); font-size: 0.72rem; padding: 0 2px; display: inline-flex; align-items: center; }
.op-branch-active { color: var(--blue); font-weight: 600; }

/* Node detail panel (toggleable) */
.nd-panel {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 14px 16px;
    margin-top: 10px; box-shadow: var(--shadow-sm);
    display: none;
}
.nd-panel.nd-open { display: block; }
.nd-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }

/* Legend */
.legend { display: flex; flex-wrap: wrap; gap: 14px; padding: 10px 0; font-size: 0.74rem; color: var(--text-secondary); }
.legend-item { display: flex; align-items: center; gap: 5px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; border: 1.5px solid transparent; }
.legend-dot-done { background: var(--green-bg); border-color: var(--green); }
.legend-dot-active { background: var(--blue-bg); border-color: var(--blue); }
.legend-dot-amber { background: var(--amber-bg); border-color: var(--amber); }
.legend-dot-fail { background: var(--red-bg); border-color: var(--red); }
.legend-dot-pending { background: var(--gray-bg); border-color: var(--gray); }
.legend-dot-disabled { background: var(--gray-bg); border-color: var(--gray); opacity: 0.5; }

/* Human action panel */
.human-panel {
    background: var(--amber-bg); border: 1px solid var(--amber-border);
    border-radius: var(--radius); padding: 16px 18px; margin-bottom: 12px;
}
.human-panel-calm {
    background: var(--green-bg); border: 1px solid var(--green-border);
}

/* Evidence navigator */
.ev-row {
    display: flex; align-items: center; gap: 10px;
    padding: 7px 0; border-bottom: 1px solid var(--border-light);
    font-size: 0.82rem;
}
.ev-row:last-child { border-bottom: none; }
.ev-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.ev-dot-yes { background: var(--green); }
.ev-dot-no { background: var(--red); }
.ev-name { font-weight: 500; min-width: 140px; }
.ev-path { font-family: var(--mono); font-size: 0.74rem; color: var(--text-secondary); word-break: break-all; }
.ev-stage { font-size: 0.7rem; color: var(--text-muted); margin-left: auto; white-space: nowrap; }

/* Capability map */
.cap-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 10px; }
.cap-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-sm); padding: 12px 14px;
    display: flex; flex-direction: column; gap: 4px; box-shadow: var(--shadow-sm);
}
.cap-header { display: flex; justify-content: space-between; align-items: center; }
.cap-title { font-size: 0.85rem; font-weight: 600; }
.cap-desc { font-size: 0.76rem; color: var(--text-secondary); line-height: 1.4; }

/* Table */
table { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin: 6px 0; }
th {
    text-align: left; padding: 7px 9px; font-weight: 600;
    background: var(--surface-alt); border-bottom: 2px solid var(--border);
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em;
    color: var(--text-secondary);
}
td { padding: 6px 9px; border-bottom: 1px solid var(--border-light); vertical-align: top; }
tr:hover { background: var(--surface-alt); }

.snippet {
    background: var(--surface-alt); border: 1px solid var(--border-light);
    border-radius: var(--radius-sm); padding: 8px 12px;
    font-family: var(--mono); font-size: 0.76rem;
    white-space: pre-wrap; max-height: 160px; overflow-y: auto; margin: 6px 0; line-height: 1.5;
}
.empty-state {
    padding: 16px; text-align: center; color: var(--text-muted);
    font-size: 0.82rem; background: var(--surface-alt);
    border-radius: var(--radius-sm); border: 1px dashed var(--border);
}
.footer {
    color: var(--text-muted); font-size: 0.72rem;
    margin-top: 36px; padding-top: 14px;
    border-top: 1px solid var(--border); text-align: center;
}
"""

# Minimal JS for node detail toggle
_JS = """\
<script>
(function(){
  document.querySelectorAll('[data-nd-toggle]').forEach(function(el){
    el.addEventListener('click',function(){
      var t=document.getElementById(el.getAttribute('data-nd-toggle'));
      if(t){t.classList.toggle('nd-open');}
    });
    el.style.cursor='pointer';
  });
})();
</script>
"""


def _h(text: str) -> str:
    return escape(str(text)) if text else ""


def _badge(label: str, kind: str = "info") -> str:
    return f'<span class="badge badge-{kind}">{_h(label)}</span>'


def _status_badge(value: str) -> str:
    v = str(value).upper()
    if v in ("PASS", "OK", "READY", "READY_FOR_MANUAL_E2E", "COMPLETED", "COMMITTED"):
        return _badge(v, "ok")
    if v in ("WARN", "PARTIAL_READY", "NEEDS REVIEW", "PARTIAL"):
        return _badge(v, "warn")
    if v in ("FAIL", "BLOCKED", "FAIL_FIX_REQUIRED"):
        return _badge(v, "fail")
    if v in ("SKIPPED_DEV_SERVER_DOWN", "SKIPPED"):
        return _badge(v, "warn")
    if not v or v in ("NONE", "UNKNOWN", "N/A"):
        return _badge("N/A", "na")
    return _badge(v, "info")


def _kv(label: str, value: Any, mono: bool = False) -> str:
    cls = "kv-value kv-mono" if mono else "kv-value"
    return f'<div class="kv"><span class="kv-label">{_h(label)}</span> <span class="{cls}">{_h(str(value))}</span></div>'


def _kv_badge(label: str, value: str) -> str:
    return f'<div class="kv"><span class="kv-label">{_h(label)}</span> {_status_badge(value)}</div>'


def _section(sid: str, title: str, content: str) -> str:
    return f'<section id="{_h(sid)}"><h2>{_h(title)}</h2>\n{content}\n</section>\n'


# -- Hero -------------------------------------------------------------------

def _render_hero(d: dict[str, Any]) -> str:
    status = d["overall_status"]
    status_cls = {"OK": "hero-status-ok", "WARN": "hero-status-warn", "BLOCKED": "hero-status-blocked"}.get(status, "hero-status-warn")
    stage = d.get("current_stage", "unknown").replace("_", " ").title()
    task_state = d["task_state"].get("state", "unknown")
    bqa_v = d["browser_qa"].get("verdict", "") or "N/A"
    qa_v = d["latest_evidence"].get("qa_verdict") or "N/A"
    blockers_open = d["blockers"]["open"]
    hq_count = len(d.get("human_questions", []))

    return f"""\
<div class="hero">
  <div class="hero-top">
    <div>
      <div class="hero-title">
        <h1>{_h(d['project_name'])}</h1>
        <span class="hero-status {status_cls}">{_h(status)}</span>
      </div>
      <div class="hero-meta">{_h(d['project_id'])} &middot; {_h(d['generated_at_display'])} &middot; {_h(d['repo_path'])}</div>
    </div>
  </div>
  <div class="metrics-row">
    <div class="metric"><div class="metric-value">{_h(stage)}</div><div class="metric-label">Stage</div></div>
    <div class="metric"><div class="metric-value">{_h(task_state)}</div><div class="metric-label">Task State</div></div>
    <div class="metric"><div class="metric-value">{_h(str(qa_v)[:18])}</div><div class="metric-label">QA Verdict</div></div>
    <div class="metric"><div class="metric-value">{_h(str(bqa_v)[:18])}</div><div class="metric-label">Browser QA</div></div>
    <div class="metric"><div class="metric-value">{blockers_open}</div><div class="metric-label">Blockers</div></div>
    <div class="metric"><div class="metric-value">{hq_count}</div><div class="metric-label">Questions</div></div>
    <div class="metric"><div class="metric-value">{_h(d['autonomy_mode'])}</div><div class="metric-label">Autonomy</div></div>
  </div>
</div>
"""


# -- What Happens Next ------------------------------------------------------

def _render_what_happens_next(d: dict[str, Any]) -> str:
    needs_human = d["blockers"]["open"] > 0 or len(d.get("human_questions", [])) > 0
    cmd = _suggest_command(d)
    evidence_hint = _suggest_evidence_check(d)

    lines = ['<div class="whn-panel">']
    lines.append('<div class="whn-title">What happens next?</div>')
    lines.append(f'<div class="whn-action">{_h(d["next_step"])}</div>')
    if needs_human:
        lines.append(f'<div class="whn-detail">{_badge("Human input required", "amber")}</div>')
    if cmd:
        lines.append(f'<div class="cmd-block">{_h(cmd)}</div>')
    if evidence_hint:
        lines.append(f'<div class="whn-detail" style="margin-top:4px">Inspect: {_h(evidence_hint)}</div>')
    lines.append('</div>')
    return "\n".join(lines)


def _suggest_command(d: dict[str, Any]) -> str:
    pid = d["project_id"]
    base = f"python -B project_autopilot/agent_loop.py --project {pid}"
    if d.get("halt_active"):
        return ""
    if d["blockers"]["open"] > 0:
        return ""
    bqa = d["browser_qa"].get("verdict", "")
    if bqa == "FAIL":
        return f"{base} --browser-qa"
    if bqa == "SKIPPED_DEV_SERVER_DOWN":
        return f"npm run dev  # then: {base} --browser-qa"
    if d.get("correction_prompt_exists"):
        return f"{base} --post-builder"
    ts = d["task_state"].get("state", "")
    if ts == "planned":
        return f"{base} --local-plan"
    if ts in ("implemented", "validating"):
        return f"{base} --post-builder"
    if ts == "passed":
        return ""
    return f"{base} --status"


def _suggest_evidence_check(d: dict[str, Any]) -> str:
    bqa = d["browser_qa"].get("verdict", "")
    if bqa == "FAIL":
        rp = d["browser_qa"].get("report_path", "")
        return rp if rp else "Browser QA report"
    if d.get("correction_prompt_exists"):
        return d.get("correction_prompt_path", "correction prompt")
    qa = d.get("latest_evidence", {}).get("qa_verdict")
    if qa and "FAIL" in str(qa).upper():
        return "latest evidence bundle"
    return ""


# -- Operational Graph ------------------------------------------------------

def _node(label: str, status: str, toggle_id: str = "") -> str:
    """Render a single node chip. status: done|active|amber|fail|disabled|pending"""
    cls = f"op-node op-node-{status}"
    dot = f'<span class="op-node-dot op-node-dot-{status}"></span>'
    extra = f' data-nd-toggle="{_h(toggle_id)}"' if toggle_id else ""
    return f'<span class="{cls}"{extra}>{dot}{_h(label)}</span>'


def _branch_arrow(active: bool = False) -> str:
    cls = "op-branch op-branch-active" if active else "op-branch"
    return f'<span class="{cls}">&#8594;</span>'


def _render_op_graph(d: dict[str, Any]) -> str:
    stage = d.get("current_stage", "unknown")
    qa_branch = d.get("qa_branch", "")
    task_state = d["task_state"].get("state", "unknown")
    bqa_v = d["browser_qa"].get("verdict", "")
    has_evidence = bool(d.get("latest_evidence"))
    correction = d.get("correction_prompt_exists", False)
    research_count = d.get("research", {}).get("count", 0)
    halt = d.get("halt_active", False)
    lock = d.get("lock", {})

    # Stage ordering for "done" inference
    stage_order = ["setup", "research", "planning", "builder_handoff", "implementation", "validation", "qa_verdict", "scheduler_readiness"]
    current_idx = stage_order.index(stage) if stage in stage_order else -1

    def _lane_cls(lane_stage: str) -> str:
        if lane_stage == stage:
            return "op-lane-label-active"
        idx = stage_order.index(lane_stage) if lane_stage in stage_order else 99
        if current_idx >= 0 and idx < current_idx:
            return "op-lane-label-done"
        if stage == "blocked":
            return "op-lane-label-blocked"
        return ""

    def _node_for(lane_stage: str, label: str, override_status: str = "", toggle: str = "") -> str:
        if override_status:
            return _node(label, override_status, toggle)
        if lane_stage == stage:
            return _node(label, "active", toggle)
        idx = stage_order.index(lane_stage) if lane_stage in stage_order else 99
        if current_idx >= 0 and idx < current_idx:
            return _node(label, "done", toggle)
        return _node(label, "pending", toggle)

    lines = ['<div class="op-graph">']

    # INTAKE / SETUP
    lines.append(f'<div class="op-lane"><div class="op-lane-label {_lane_cls("setup")}">Intake</div><div class="op-lane-nodes">')
    lines.append(_node_for("setup", "Config + TASK_QUEUE", toggle="nd-setup"))
    lines.append('</div></div>')

    # RESEARCH
    lines.append(f'<div class="op-lane"><div class="op-lane-label {_lane_cls("research")}">Research</div><div class="op-lane-nodes">')
    lines.append(_node_for("research", "quick_check"))
    lines.append(_branch_arrow())
    lines.append(_node_for("research", "standard_research"))
    lines.append(_branch_arrow())
    deep_status = "amber" if research_count > 0 and d.get("research", {}).get("deep_research_pending_approval", 0) > 0 else ("done" if research_count > 0 else "pending")
    if stage == "research":
        deep_status = "active"
    lines.append(_node("deep_research", deep_status, toggle_id="nd-research"))
    lines.append(f'<span class="op-branch" style="font-size:0.66rem;margin-left:2px">human approval</span>')
    lines.append('</div></div>')

    # PLANNING
    lines.append(f'<div class="op-lane"><div class="op-lane-label {_lane_cls("planning")}">Planning</div><div class="op-lane-nodes">')
    lines.append(_node_for("planning", "local-plan", toggle="nd-planning"))
    lines.append(_branch_arrow(stage == "planning"))
    lines.append(_node_for("planning", "OpenAI cycle"))
    lines.append(_branch_arrow())
    lines.append(_node_for("planning", "handoff prompt"))
    lines.append('</div></div>')

    # BUILDER HANDOFF
    lines.append(f'<div class="op-lane"><div class="op-lane-label {_lane_cls("builder_handoff")}">Builder</div><div class="op-lane-nodes">')
    lines.append(_node_for("builder_handoff", "Claude manual", toggle="nd-builder"))
    lines.append(_branch_arrow())
    lines.append(_node_for("builder_handoff", "Codex manual"))
    lines.append(_branch_arrow())
    auto_st = "disabled"
    lines.append(_node("auto-exec", auto_st))
    lines.append(f'<span class="op-branch" style="font-size:0.66rem;margin-left:2px">disabled</span>')
    lines.append('</div></div>')

    # IMPLEMENTATION
    lines.append(f'<div class="op-lane"><div class="op-lane-label {_lane_cls("implementation")}">Implement</div><div class="op-lane-nodes">')
    lines.append(_node_for("implementation", "builder report", toggle="nd-impl"))
    lines.append(_branch_arrow())
    lines.append(_node_for("implementation", "changed files"))
    lines.append('</div></div>')

    # VALIDATION
    lines.append(f'<div class="op-lane"><div class="op-lane-label {_lane_cls("validation")}">Validation</div><div class="op-lane-nodes">')
    # Infer individual gate statuses
    ev = d.get("latest_evidence", {})
    cmds = ev.get("commands", {}) if isinstance(ev.get("commands"), dict) else {}
    for gate_label, gate_key in [("lint", "lint"), ("typecheck", "typecheck"), ("build", "build")]:
        cmd = cmds.get(gate_key, {})
        if not cmd:
            gs = "pending" if current_idx < stage_order.index("validation") else "pending"
        elif cmd.get("exit_code") == 0:
            gs = "done"
        else:
            gs = "fail"
        if stage == "validation":
            gs = gs if gs in ("done", "fail") else "active"
        lines.append(_node(gate_label, gs))
    # Browser QA
    if bqa_v == "PASS":
        bqa_s = "done"
    elif bqa_v == "FAIL":
        bqa_s = "fail"
    elif bqa_v:
        bqa_s = "amber"
    else:
        bqa_s = "pending" if stage != "validation" else "active"
    lines.append(_node("browser QA", bqa_s, toggle_id="nd-bqa"))
    # Backend audit
    br = d.get("backend_readiness", "")
    if br in ("READY", "READY_FOR_MANUAL_E2E"):
        ba_s = "done"
    elif br == "PARTIAL_READY":
        ba_s = "amber"
    elif br:
        ba_s = "amber"
    else:
        ba_s = "pending"
    lines.append(_node("backend audit", ba_s))
    lines.append('</div></div>')

    # QA VERDICT — branching
    lines.append(f'<div class="op-lane"><div class="op-lane-label {_lane_cls("qa_verdict")}">QA Verdict</div><div class="op-lane-nodes" style="flex-direction:column;align-items:flex-start;gap:4px">')
    # Show the 5 branches
    qa_branches = [
        ("pass", "PASS", "commit / review", "done" if qa_branch == "pass" else "pending"),
        ("fail_fix", "FAIL_FIX_REQUIRED", "correction prompt", "fail" if qa_branch == "fail_fix" else "pending"),
        ("human_decision", "HUMAN_DECISION", "human question", "amber" if qa_branch == "human_decision" else "pending"),
        ("research_required", "RESEARCH_REQUIRED", "research request", "amber" if qa_branch == "research_required" else "pending"),
        ("blocked", "BLOCKED", "blocker filed", "fail" if qa_branch == "blocked" else "pending"),
    ]
    for branch_key, branch_label, branch_target, branch_status in qa_branches:
        is_this = qa_branch == branch_key
        if stage == "qa_verdict" and is_this:
            branch_status = "active"
        elif stage == "qa_verdict" and not qa_branch:
            branch_status = "active" if branch_key == "pass" else "pending"
        arrow = _branch_arrow(is_this)
        lines.append(f'<div style="display:flex;align-items:center;gap:4px">{_node(branch_label, branch_status)}{arrow}<span style="font-size:0.72rem;color:var(--text-muted)">{_h(branch_target)}</span></div>')
    lines.append('</div></div>')

    # SCHEDULER READINESS
    lines.append(f'<div class="op-lane"><div class="op-lane-label {_lane_cls("scheduler_readiness")}">Scheduler</div><div class="op-lane-nodes">')
    lock_st = "amber" if lock.get("locked") else "done" if not lock.get("stale") else "amber"
    halt_st = "fail" if halt else "done"
    lines.append(_node("run lock", lock_st if stage == "scheduler_readiness" or current_idx >= stage_order.index("scheduler_readiness") else "pending"))
    lines.append(_node("HALT", halt_st if halt else ("done" if not halt else "pending")))
    lines.append(_node("budget caps", "done" if stage == "scheduler_readiness" else "pending"))
    lines.append(_node("scheduler", "disabled"))
    lines.append(f'<span class="op-branch" style="font-size:0.66rem;margin-left:2px">not enabled</span>')
    lines.append('</div></div>')

    lines.append('</div>')  # end op-graph

    # Legend
    lines.append('<div class="legend">')
    for label, dot_cls in [("Completed", "done"), ("Active", "active"), ("Human decision", "amber"), ("Failed / blocked", "fail"), ("Pending", "pending"), ("Disabled", "disabled")]:
        lines.append(f'<span class="legend-item"><span class="legend-dot legend-dot-{dot_cls}"></span>{label}</span>')
    lines.append('</div>')

    return "\n".join(lines)


# -- Node Detail Panels -----------------------------------------------------

def _render_node_details(d: dict[str, Any]) -> str:
    """Render expandable detail panels for clickable graph nodes."""
    pid = d["project_id"]
    base = f"python -B project_autopilot/agent_loop.py --project {pid}"

    panels = []

    # Setup
    panels.append(f'<div id="nd-setup" class="nd-panel">')
    setup_ok = d.get("current_task", {}).get("title")
    panels.append(f'<div class="nd-header"><h4>Intake / Setup</h4>{_status_badge("OK" if setup_ok else "PENDING")}</div>')
    panels.append(_kv("What", "Load config, validate environment, read TASK_QUEUE"))
    panels.append(_kv("Inputs", "config.yaml, TASK_QUEUE.md, CURRENT_STATE.md"))
    panels.append(_kv("Outputs", "Task selection, risk classification"))
    panels.append(_kv("Next", "Research or Planning depending on task"))
    task_title = d["current_task"].get("title") or "none"
    panels.append(_kv("Current task", task_title))
    panels.append(f'<div class="cmd-block">{_h(base)} --doctor</div>')
    panels.append('</div>')

    # Research
    rc = d.get("research", {})
    panels.append(f'<div id="nd-research" class="nd-panel">')
    panels.append(f'<div class="nd-header"><h4>Deep Research</h4>{_badge("requires human approval", "amber")}</div>')
    panels.append(_kv("What", "External research with cost; needs human sign-off"))
    panels.append(_kv("Pending approval", rc.get("deep_research_pending_approval", 0)))
    panels.append(_kv("Total requests", rc.get("count", 0)))
    panels.append(_kv("Completed", rc.get("completed_count", 0)))
    panels.append(_kv("Inspect", "logs/research/ index"))
    panels.append(f'<div class="cmd-block">{_h(base)} --research-status</div>')
    panels.append('</div>')

    # Planning
    panels.append(f'<div id="nd-planning" class="nd-panel">')
    panels.append(f'<div class="nd-header"><h4>Planning / Local Plan</h4>{_status_badge(d["task_state"].get("state", "N/A"))}</div>')
    panels.append(_kv("What", "Deterministic risk classification + plan generation (free)"))
    panels.append(_kv("Inputs", "TASK_QUEUE.md, CURRENT_STATE.md, config"))
    panels.append(_kv("Outputs", "Builder prompt, risk summary"))
    panels.append(_kv("Next paths", "Builder handoff (Claude manual / Codex)"))
    panels.append(f'<div class="cmd-block">{_h(base)} --local-plan</div>')
    panels.append('</div>')

    # Builder
    panels.append(f'<div id="nd-builder" class="nd-panel">')
    bp = d.get("builder_prompt_path", "") or "none"
    panels.append(f'<div class="nd-header"><h4>Builder Handoff</h4></div>')
    panels.append(_kv("What", "Send prompt to Claude Code or Codex for implementation"))
    panels.append(_kv("Builder prompt", bp, mono=True))
    panels.append(_kv("Primary builder", d.get("builder_primary", "")))
    panels.append(_kv("Fallback", d.get("builder_fallback", "")))
    panels.append(_kv("Auto-exec", "disabled" if not d.get("allow_auto_exec") else "enabled"))
    panels.append(_kv("Next", "Implementation artifacts, then --post-builder"))
    panels.append(f'<div class="cmd-block">{_h(base)} --handoff-claude</div>')
    panels.append('</div>')

    # Implementation
    panels.append(f'<div id="nd-impl" class="nd-panel">')
    panels.append(f'<div class="nd-header"><h4>Implementation</h4></div>')
    panels.append(_kv("What", "Builder writes code, generates report of changes"))
    panels.append(_kv("Inputs", "Builder prompt"))
    panels.append(_kv("Outputs", "Changed files, builder report, git diff"))
    panels.append(_kv("Next", "Run --post-builder to validate"))
    panels.append(f'<div class="cmd-block">{_h(base)} --post-builder</div>')
    panels.append('</div>')

    # Browser QA
    bqa = d.get("browser_qa", {})
    bqa_v = bqa.get("verdict", "") or "N/A"
    panels.append(f'<div id="nd-bqa" class="nd-panel">')
    panels.append(f'<div class="nd-header"><h4>Browser QA</h4>{_status_badge(bqa_v)}</div>')
    panels.append(_kv("What", "Route testing with Playwright or HTTP fallback"))
    panels.append(_kv("Mode", bqa.get("mode", "N/A")))
    summary = bqa.get("summary", {})
    checked = summary.get("routes_checked", 0)
    failed = summary.get("routes_failed", 0)
    panels.append(_kv("Routes checked", checked))
    panels.append(_kv("Routes failed", failed))
    rp = bqa.get("report_path", "")
    if rp:
        panels.append(_kv("Report", rp, mono=True))
    if bqa_v == "FAIL":
        panels.append(_kv("Blocker", "Fix failures before proceeding"))
    panels.append(f'<div class="cmd-block">{_h(base)} --browser-qa</div>')
    panels.append('</div>')

    return "\n".join(panels)


# -- Human Action Panel -----------------------------------------------------

def _render_human_action_panel(d: dict[str, Any]) -> str:
    blockers_open = d["blockers"]["open"]
    questions = d.get("human_questions", [])
    open_questions = [q for q in questions if q.get("status", "").lower() == "open"]
    hq_count = len(open_questions)
    latest_blocker = d["blockers"].get("latest_open")
    needs_action = blockers_open > 0 or hq_count > 0

    panel_cls = "human-panel" if needs_action else "human-panel human-panel-calm"
    lines = [f'<div class="{panel_cls}">']

    if not needs_action:
        lines.append(f'<h3>No human input required</h3>')
        lines.append(f'<div style="font-size:0.82rem;color:var(--text-secondary)">All blockers resolved. No open questions. Autopilot can proceed.</div>')
    else:
        lines.append(f'<h3>Human Input Required {_badge(f"{blockers_open + hq_count} pending", "amber")}</h3>')
        lines.append(f'<div class="grid grid-2" style="margin-top:8px">')
        lines.append(f'<div>')
        lines.append(_kv("Open blockers", str(blockers_open)))
        if latest_blocker:
            lines.append(_kv("Latest blocker", latest_blocker))
        lines.append(_kv("Edit", "project_control/BLOCKERS.md", mono=True))
        lines.append(f'</div><div>')
        lines.append(_kv("Open questions", str(hq_count)))
        if open_questions:
            lines.append(_kv("Latest question", open_questions[0].get("title", "")))
        lines.append(_kv("Edit", "project_control/HUMAN_QUESTIONS.md", mono=True))
        lines.append(f'</div></div>')

        lines.append(f'<div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--amber-border)">')
        lines.append(f'<div class="kv-label" style="font-weight:600;margin-bottom:4px">Suggested answer format</div>')
        lines.append(f'<div class="snippet">Decision: [your decision]\nReason: [why]\nApproved next action: [what autopilot should do]\nConstraints: [any limits]</div>')
        lines.append(f'</div>')

    lines.append('</div>')
    return "\n".join(lines)


# -- Evidence Navigator -----------------------------------------------------

def _render_evidence_navigator(d: dict[str, Any]) -> str:
    items = d.get("evidence_paths", [])
    if not items:
        return '<div class="empty-state">No evidence paths available.</div>'

    lines = ['<div class="card" style="padding:12px 16px">']
    for item in items:
        dot_cls = "ev-dot-yes" if item["exists"] else "ev-dot-no"
        status_word = "exists" if item["exists"] else "missing"
        lines.append(f'<div class="ev-row">')
        lines.append(f'<span class="ev-dot {dot_cls}" title="{status_word}"></span>')
        lines.append(f'<span class="ev-name">{_h(item["name"])}</span>')
        lines.append(f'<span class="ev-path">{_h(item["path"])}</span>')
        lines.append(f'<span class="ev-stage">{_h(item["stage"])}</span>')
        lines.append(f'</div>')
    lines.append('</div>')
    return "\n".join(lines)


# -- Current Task -----------------------------------------------------------

def _render_current_task(d: dict[str, Any]) -> str:
    task = d["current_task"]
    title = task.get("title")
    if not title:
        return '<div class="empty-state">No current task detected in TASK_QUEUE.md</div>'
    risk = d.get("risk", {})
    lines = ['<div class="card card-accent-blue">']
    lines.append(f'<h3>{_h(title)}</h3>')
    lines.append('<div class="grid grid-2" style="margin-top:6px">')
    lines.append('<div>')
    lines.append(_kv("Task state", d["task_state"].get("state", "unknown")))
    if risk:
        lines.append(_kv("Risk level", risk.get("risk_level", "unknown")))
        cats = risk.get("categories") or risk.get("risk_categories") or []
        if cats:
            lines.append(_kv("Risk categories", ", ".join(cats) if isinstance(cats, list) else str(cats)))
    lines.append('</div><div>')
    if risk.get("recommended_action") or risk.get("action"):
        lines.append(_kv("Recommended action", risk.get("recommended_action", risk.get("action", ""))))
    lines.append(_kv("Builder prompt", d.get("builder_prompt_path", "") or "none", mono=True))
    if d.get("correction_prompt_exists"):
        lines.append(_kv("Correction prompt", d["correction_prompt_path"], mono=True))
    lines.append('</div></div>')
    if task.get("criteria"):
        lines.append('<div style="margin-top:10px"><span class="kv-label">Acceptance criteria</span></div>')
        lines.append(f'<div class="snippet">{_h(task["criteria"])}</div>')
    lines.append('</div>')
    return "\n".join(lines)


# -- Capability Map ---------------------------------------------------------

_CAPABILITIES = [
    {"key": "control", "title": "Control Layer", "desc": "HALT, run lock, config validation, autonomy gates", "files": ["agent_loop.py", "config_validator.py", "run_lock.py"]},
    {"key": "reliability", "title": "Reliability Core", "desc": "Evidence bundles, task state, run history, metrics", "files": ["evidence_bundle.py", "task_state.py", "run_history.py", "run_metrics.py"]},
    {"key": "builder", "title": "Builder Handoff", "desc": "Prompt building, Claude runner, builder intake", "files": ["prompt_builder.py", "claude_runner.py", "builder_intake.py"]},
    {"key": "qa", "title": "QA Layer", "desc": "Post-builder QA, correction prompts, risk classifier", "files": ["qa_reviewer.py", "risk_classifier.py"]},
    {"key": "browser_qa", "title": "Browser QA", "desc": "Route testing, screenshots, console/network audit", "files": ["browser_qa.py"]},
    {"key": "research", "title": "Research", "desc": "Research requests, deep research, approval flow", "files": ["research_log.py"]},
    {"key": "observability", "title": "Observability", "desc": "Control center, Telegram alerts, run metrics", "files": ["control_center.py", "telegram_alerts.py", "run_metrics.py"]},
    {"key": "scheduler", "title": "Scheduler Readiness", "desc": "Systemd templates, retry policy, VPS deployment", "files": []},
    {"key": "safety", "title": "Safety / Budget / Risk", "desc": "Cost controller, budget gates, auto-exec controls", "files": ["cost_controller.py", "risk_classifier.py"]},
]


def _cap_status(d: dict[str, Any], cap_key: str) -> tuple[str, str]:
    if cap_key == "control":
        return ("HALTED", "fail") if d.get("halt_active") else ("Active", "ok")
    if cap_key == "reliability":
        return ("Active", "ok") if d.get("latest_evidence") else ("No data", "na")
    if cap_key == "builder":
        return ("Ready", "ok") if d.get("builder_prompt_path") else ("Pending", "na")
    if cap_key == "qa":
        qv = d.get("latest_evidence", {}).get("qa_verdict")
        if qv:
            v = str(qv).upper()
            if "PASS" in v:
                return ("PASS", "ok")
            if "FAIL" in v:
                return ("FAIL", "fail")
            return (str(qv), "warn")
        return ("No verdict", "na")
    if cap_key == "browser_qa":
        bv = d.get("browser_qa", {}).get("verdict", "")
        if bv == "PASS":
            return ("PASS", "ok")
        if bv == "FAIL":
            return ("FAIL", "fail")
        return (bv, "warn") if bv else ("Not run", "na")
    if cap_key == "research":
        rc = d.get("research", {}).get("count", 0)
        return (f"{rc} requests", "info") if rc > 0 else ("None", "na")
    if cap_key == "observability":
        return ("Active", "ok")
    if cap_key == "scheduler":
        return ("Not enabled", "na")
    if cap_key == "safety":
        return ("Auto-exec ON", "warn") if d.get("allow_auto_exec") else ("Locked down", "ok")
    return ("Unknown", "na")


def _render_capability_map(d: dict[str, Any]) -> str:
    cards: list[str] = []
    for cap in _CAPABILITIES:
        status_word, badge_kind = _cap_status(d, cap["key"])
        file_str = f'{len(cap["files"])} modules' if cap["files"] else "templates only"
        cards.append(
            f'<div class="cap-card">'
            f'<div class="cap-header"><span class="cap-title">{_h(cap["title"])}</span>{_badge(status_word, badge_kind)}</div>'
            f'<div class="cap-desc">{_h(cap["desc"])}</div>'
            f'<div style="font-size:0.7rem;color:var(--text-muted)">{_h(file_str)}</div>'
            f'</div>'
        )
    return f'<div class="cap-grid">{"".join(cards)}</div>'


# -- Latest Run -------------------------------------------------------------

def _render_latest_run(d: dict[str, Any]) -> str:
    m = d.get("latest_metrics")
    if not m:
        return '<div class="empty-state">No run metrics recorded yet.</div>'
    qa = m.get("qa_verdict") or "N/A"
    outcome = m.get("outcome", "")
    accent = "card-accent-green" if outcome == "success" else ("card-accent-red" if outcome == "failure" else "")
    dur = m.get("total_duration_seconds", 0)
    cmds_exec = m.get("commands_executed", 0)
    cmds_fail = m.get("commands_failed", 0)
    f_created = m.get("files_created", 0)
    f_modified = m.get("files_modified", 0)
    f_deleted = m.get("files_deleted", 0)
    l_added = m.get("lines_added", 0)
    l_removed = m.get("lines_removed", 0)
    lines = [f'<div class="card {accent}">']
    lines.append('<div class="grid grid-3" style="margin-bottom:6px">')
    lines.append(f'<div>{_kv("Run ID", m.get("run_id", ""), mono=True)}</div>')
    lines.append(f'<div>{_kv_badge("Outcome", outcome or "N/A")}</div>')
    lines.append(f'<div>{_kv_badge("QA Verdict", str(qa))}</div>')
    lines.append('</div>')
    lines.append('<div class="grid grid-4">')
    lines.append(f'<div>{_kv("Duration", f"{dur}s")}</div>')
    lines.append(f'<div>{_kv("Commands", f"{cmds_exec} ({cmds_fail} failed)")}</div>')
    lines.append(f'<div>{_kv("Files", f"+{f_created} ~{f_modified} -{f_deleted}")}</div>')
    lines.append(f'<div>{_kv("Lines", f"+{l_added} / -{l_removed}")}</div>')
    lines.append('</div>')
    if m.get("evidence_bundle_path"):
        lines.append(f'<div style="margin-top:4px">{_kv("Evidence", m["evidence_bundle_path"], mono=True)}</div>')
    lines.append('</div>')
    return "\n".join(lines)


# -- Quality Gates ----------------------------------------------------------

def _render_quality_gates(d: dict[str, Any]) -> str:
    ev = d.get("latest_evidence", {})
    cmds = ev.get("commands", {}) if isinstance(ev.get("commands"), dict) else {}

    def _cmd_status(key: str) -> str:
        cmd = cmds.get(key, {})
        if not cmd:
            return "N/A"
        return "PASS" if cmd.get("exit_code") == 0 else "FAIL"

    lines = ['<div class="card"><div class="grid grid-auto">']
    for label, key in [("Lint", "lint"), ("Typecheck", "typecheck"), ("Build", "build")]:
        lines.append(f'<div>{_kv_badge(label, _cmd_status(key))}</div>')
    qa = ev.get("qa_verdict") or "N/A"
    lines.append(f'<div>{_kv_badge("QA Verdict", str(qa))}</div>')
    bqa_verdict = d.get("browser_qa", {}).get("verdict", "") or "N/A"
    lines.append(f'<div>{_kv_badge("Browser QA", bqa_verdict)}</div>')
    lines.append(f'<div>{_kv_badge("Backend", d.get("backend_readiness", "N/A"))}</div>')
    if d.get("correction_prompt_exists"):
        lines.append(f'<div>{_badge("Correction prompt available", "warn")}</div>')
    lines.append('</div></div>')
    return "\n".join(lines)


# -- Browser QA -------------------------------------------------------------

def _render_browser_qa(d: dict[str, Any]) -> str:
    bqa = d.get("browser_qa", {})
    verdict = bqa.get("verdict", "")
    summary = bqa.get("summary", {})
    mode = bqa.get("mode", "")

    if not verdict:
        return '<div class="empty-state">No Browser QA results. Run --browser-qa to generate.</div>'

    accent = "card-accent-green" if verdict == "PASS" else ("card-accent-red" if verdict == "FAIL" else "card-accent-yellow")
    lines = [f'<div class="card {accent}">']
    lines.append(f'<h3>Browser QA {_status_badge(verdict)}</h3>')
    viewports = d.get("autopilot_state", {}).get("browser_qa_summary", summary)
    routes_checked = viewports.get("routes_checked", summary.get("routes_checked", 0))
    routes_passed = viewports.get("routes_passed", summary.get("routes_passed", 0))
    routes_failed = viewports.get("routes_failed", summary.get("routes_failed", 0))
    console_errs = viewports.get("console_errors", summary.get("console_errors", 0))
    page_errs = viewports.get("page_errors", summary.get("page_errors", 0))
    net_reqs = viewports.get("failed_network_requests", summary.get("failed_network_requests", 0))
    net_loads = viewports.get("failed_resource_loads", summary.get("failed_resource_loads", 0))
    screenshots = viewports.get("screenshots_captured", summary.get("screenshots_captured", 0))
    total_issues = console_errs + page_errs + net_reqs + net_loads
    lines.append('<div class="grid grid-3" style="margin-top:6px">')
    lines.append(f'<div>{_kv("Mode", mode)}{_kv("Routes", f"{routes_checked} checked")}{_kv("Passed", str(routes_passed))}</div>')
    lines.append(f'<div>{_kv("Console errors", str(console_errs))}{_kv("Page errors", str(page_errs))}{_kv("Network failures", str(net_reqs + net_loads))}</div>')
    lines.append(f'<div>{_kv("Total issues", str(total_issues))}{_kv("Screenshots", str(screenshots))}{_kv("Report", bqa.get("report_path", ""), mono=True)}</div>')
    lines.append('</div></div>')
    return "\n".join(lines)


# -- Backend ----------------------------------------------------------------

def _render_backend(d: dict[str, Any]) -> str:
    audit = d.get("backend_audit", {})
    lines = ['<div class="card">']
    lines.append(f'<h3>Backend / Data {_status_badge(d.get("backend_readiness", "N/A"))}</h3>')
    if not audit:
        lines.append('<div class="empty-state" style="margin-top:6px">No backend audit data. Run --backend-audit.</div>')
    else:
        tables = audit.get("tables_referenced", [])
        buckets = audit.get("buckets_referenced", [])
        manual = audit.get("manual_verification_required", [])
        lines.append('<div class="grid grid-3" style="margin-top:6px">')
        lines.append(f'<div>{_kv("Tables", ", ".join(tables) if tables else "none")}</div>')
        lines.append(f'<div>{_kv("Buckets", ", ".join(buckets) if buckets else "none")}</div>')
        lines.append(f'<div>{_kv("Manual items", str(len(manual)))}</div>')
        lines.append('</div>')
        if manual:
            lines.append('<ul style="margin:6px 0 0 16px;font-size:0.8rem;color:var(--text-secondary)">')
            for item in manual[:6]:
                lines.append(f"<li>{_h(item)}</li>")
            if len(manual) > 6:
                lines.append(f"<li>... and {len(manual) - 6} more</li>")
            lines.append("</ul>")
    risk_cats = d.get("risk", {}).get("categories", d.get("risk", {}).get("risk_categories", []))
    if "data_schema_change" in (risk_cats if isinstance(risk_cats, list) else []):
        lines.append(f'<div style="margin-top:6px">{_badge("data_schema_change risk", "warn")}</div>')
    lines.append("</div>")
    return "\n".join(lines)


# -- Blockers ---------------------------------------------------------------

def _render_blockers(d: dict[str, Any]) -> str:
    blockers = d.get("blockers_detail", [])
    questions = d.get("human_questions", [])
    bs = d.get("blockers", {})
    open_count = bs.get("open", 0)
    lines = []
    accent = "card-accent-red" if open_count > 0 else ""
    lines.append(f'<div class="card {accent}">')
    lines.append(f'<h3>Blockers <span style="font-weight:400;font-size:0.8rem;color:var(--text-muted)">{open_count} open, {bs.get("resolved", 0)} resolved, {bs.get("parked", 0)} parked</span></h3>')
    if blockers:
        lines.append("<table><tr><th>Title</th><th>Status</th><th>Severity</th></tr>")
        for b in blockers:
            st = b.get("status", "").lower()
            badge_kind = "fail" if st == "open" else ("ok" if st == "resolved" else "na")
            lines.append(f"<tr><td>{_h(b.get('title', ''))}</td><td>{_badge(st, badge_kind)}</td><td>{_h(b.get('severity', ''))}</td></tr>")
        lines.append("</table>")
    else:
        lines.append('<div class="empty-state" style="margin-top:6px">No blockers. All clear.</div>')
    lines.append("</div>")
    if questions:
        lines.append('<div class="card card-accent-yellow">')
        lines.append(f'<h3>Human Questions <span style="font-weight:400;font-size:0.8rem;color:var(--text-muted)">{len(questions)} pending</span></h3>')
        lines.append("<table><tr><th>Question</th><th>Status</th><th>Severity</th></tr>")
        for q in questions:
            st = q.get("status", "").lower()
            lines.append(f"<tr><td>{_h(q.get('title', ''))}</td><td>{_badge(st, 'warn' if st == 'open' else 'ok')}</td><td>{_h(q.get('severity', ''))}</td></tr>")
        lines.append("</table></div>")
    return "\n".join(lines)


# -- Research ---------------------------------------------------------------

def _render_research(d: dict[str, Any]) -> str:
    r = d.get("research", {})
    count = r.get("count", 0)
    lines = ['<div class="card"><h3>Research</h3>']
    if count == 0:
        lines.append('<div class="empty-state" style="margin-top:6px">No research requests recorded.</div>')
    else:
        lines.append('<div class="grid grid-3" style="margin-top:4px">')
        lines.append(f'<div>{_kv("Total", count)}</div>')
        lines.append(f'<div>{_kv("Pending approval", r.get("deep_research_pending_approval", 0))}</div>')
        lines.append(f'<div>{_kv("Completed", r.get("completed_count", 0))}</div>')
        lines.append('</div>')
        latest = r.get("latest")
        if latest:
            lines.append('<div style="margin-top:8px;padding-top:8px;border-top:1px solid var(--border-light)">')
            lines.append(_kv("Latest topic", latest.get("topic", "")))
            lines.append(_kv_badge("Status", latest.get("status", "")))
            if latest.get("requires_human_approval"):
                lines.append(f'{_badge("Requires human approval", "warn")}')
            lines.append('</div>')
    lines.append("</div>")
    return "\n".join(lines)


# -- Timeline ---------------------------------------------------------------

def _render_timeline(d: dict[str, Any]) -> str:
    events = d.get("recent_events", [])
    if not events:
        return '<div class="empty-state">No events recorded yet.</div>'
    header = "<tr><th>Timestamp</th><th>Run</th><th>Event</th><th>Detail</th></tr>"
    rows: list[str] = []
    for ev in events:
        meta = ev.get("metadata", {})
        detail = ev.get("status") or meta.get("label") or meta.get("verdict") or meta.get("outcome") or ev.get("file_path") or ""
        rows.append(
            f"<tr><td class='kv-mono'>{_h(str(ev.get('timestamp_utc', ''))[:19])}</td>"
            f"<td class='kv-mono'>{_h(str(ev.get('run_id', '')))}</td>"
            f"<td>{_h(str(ev.get('event_type', '')))}</td>"
            f"<td>{_h(str(detail)[:100])}</td></tr>"
        )
    return f'<div class="card" style="overflow-x:auto;padding:10px 14px"><table>{header}{"".join(rows)}</table></div>'


# -- Budget -----------------------------------------------------------------

def _render_budget(d: dict[str, Any]) -> str:
    cost = d.get("cost", {})
    lines = ['<div class="card"><div class="grid grid-3">']
    lines.append('<div>')
    lines.append('<span class="kv-label" style="font-weight:600">Budget Limits</span>')
    lines.append(_kv("Per-cycle", f"${d['per_cycle_budget']:.2f}"))
    lines.append(_kv("Daily", f"${d['daily_budget']:.2f}"))
    lines.append(_kv("Monthly", f"${d['monthly_budget']:.2f}"))
    lines.append('</div><div>')
    lines.append('<span class="kv-label" style="font-weight:600">Current Spend</span>')
    if cost:
        lines.append(_kv("Cycle", f"${cost.get('cycle_spend_usd', 0):.4f}"))
        lines.append(_kv("Daily", f"${cost.get('daily_spend_usd', 0):.4f}"))
        lines.append(_kv("Monthly", f"${cost.get('monthly_spend_usd', 0):.4f}"))
    else:
        lines.append('<div class="kv"><span class="kv-label">No cost data</span></div>')
    lines.append('</div><div>')
    lines.append('<span class="kv-label" style="font-weight:600">Controls</span>')
    lines.append(_kv("API mode", d["paid_api_mode"]))
    lines.append(_kv("Paid images", "enabled" if d["allow_paid_image"] else "disabled"))
    lines.append(_kv("Paid video", "enabled" if d["allow_paid_video"] else "disabled"))
    lines.append('</div></div></div>')
    return "\n".join(lines)


# -- Safety -----------------------------------------------------------------

def _render_safety(d: dict[str, Any]) -> str:
    lock = d.get("lock", {})
    gates = [
        ("HALT file", "ACTIVE" if d["halt_active"] else "not active", "fail" if d["halt_active"] else "ok"),
        ("Auto Claude exec", "enabled" if d["allow_auto_exec"] else "disabled", "warn" if d["allow_auto_exec"] else "ok"),
        ("Run lock", "HELD" if lock.get("locked") else ("STALE" if lock.get("stale") else "free"), "warn" if lock.get("locked") else "ok"),
        ("Max parallel agents", str(d["max_parallel_agents"]), "info"),
        ("Telegram alerts", "on" if d["telegram_enabled"] else "off", "ok" if d["telegram_enabled"] else "na"),
        ("Deploy automation", "disabled", "ok"),
        ("Scheduler", "not enabled", "na"),
    ]
    lines = ['<div class="card"><div class="grid grid-auto">']
    for label, value, kind in gates:
        lines.append(f'<div class="kv"><span class="kv-label">{_h(label)}</span> {_badge(value, kind)}</div>')
    lines.append("</div></div>")
    return "\n".join(lines)


# -- Full page assembly -----------------------------------------------------

def render_html(d: dict[str, Any]) -> str:
    parts = [
        f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>Control Center &mdash; {_h(d['project_name'])}</title>"
        f"<style>{_CSS}</style></head><body>",

        # 1. Hero
        _render_hero(d),

        # 2. What happens next
        _render_what_happens_next(d),

        # 3. Operational graph (replaces linear stage flow)
        _section("op-graph", "Autopilot Flow Map", _render_op_graph(d) + _render_node_details(d)),

        # 4. Human action panel
        _section("human-action", "Human Input Required", _render_human_action_panel(d)),

        # 5. Current task
        _section("task", "Current Task", _render_current_task(d)),

        # 6. Evidence navigator
        _section("evidence", "Evidence Navigator", _render_evidence_navigator(d)),

        # 7. Capability map
        _section("capabilities", "Capability Map", _render_capability_map(d)),

        # 8. Latest run
        _section("latest-run", "Latest Run", _render_latest_run(d)),

        # 9. Quality gates
        _section("quality", "Quality Gates", _render_quality_gates(d)),

        # 10. Browser QA
        _section("browser-qa", "Browser QA", _render_browser_qa(d)),

        # 11. Backend
        _section("backend", "Backend / Customer Data", _render_backend(d)),

        # 12. Blockers & questions
        _section("blockers", "Blockers & Human Questions", _render_blockers(d)),

        # 13. Research
        _section("research", "Research", _render_research(d)),

        # 14. Activity timeline
        _section("timeline", "Activity Timeline", _render_timeline(d)),

        # 15. Budget
        _section("budget", "Budget / Cost", _render_budget(d)),

        # 16. Safety gates
        _section("safety", "Safety / Autonomy Gates", _render_safety(d)),

        # Footer
        f'<div class="footer">Project Autopilot Control Center v0.3 &middot; Generated {_h(d["generated_at_display"])} &middot; Read-only &middot; No secrets &middot; No command execution</div>',
        _JS,
        "</body></html>",
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def generate_control_center(project: ProjectConfig) -> Path:
    """Generate the control center HTML and return the output path."""
    data = collect_control_center_data(project)
    html = render_html(data)
    out_dir = project.repo_path / project.logs_dir / "control_center"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{project.project_id}_control_center.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot Control Center v0.3")
    parser.add_argument("--project", default="mira", help="Project id.")
    args = parser.parse_args()

    project = load_project_config(args.project)
    path = generate_control_center(project)
    print(f"Control Center generated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
