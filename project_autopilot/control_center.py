"""Project Autopilot Control Center v2.0 — Command Center Dashboard.

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

    return data


# ---------------------------------------------------------------------------
# HTML rendering — v2.0 Command Center
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
    --mono: 'SF Mono', 'Cascadia Code', 'Consolas', 'Monaco', monospace;
    --sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, sans-serif;
    --radius: 10px;
    --radius-sm: 6px;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
    --shadow: 0 2px 8px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.08);
    --green: #16a34a; --green-bg: #dcfce7; --green-border: #bbf7d0; --green-text: #166534;
    --yellow: #ca8a04; --yellow-bg: #fef9c3; --yellow-border: #fef08a; --yellow-text: #854d0e;
    --red: #dc2626; --red-bg: #fee2e2; --red-border: #fecaca; --red-text: #991b1b;
    --blue: #2563eb; --blue-bg: #dbeafe; --blue-border: #bfdbfe; --blue-text: #1e40af;
    --gray: #64748b; --gray-bg: #f1f5f9; --gray-border: #e2e8f0; --gray-text: #475569;
    --purple: #7c3aed; --purple-bg: #ede9fe; --purple-border: #ddd6fe; --purple-text: #5b21b6;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: var(--sans); background: var(--bg); color: var(--text);
    line-height: 1.55; padding: 24px 28px; max-width: 1280px; margin: 0 auto;
    -webkit-font-smoothing: antialiased;
}

/* Typography */
h1 { font-size: 1.65rem; font-weight: 700; letter-spacing: -0.02em; }
h2 {
    font-size: 0.82rem; font-weight: 600; letter-spacing: 0.06em;
    text-transform: uppercase; color: var(--text-secondary);
    margin: 32px 0 14px; padding-bottom: 8px;
    border-bottom: 2px solid var(--border);
}
h3 { font-size: 0.95rem; font-weight: 600; margin: 0 0 8px; }

/* Badges */
.badge {
    display: inline-flex; align-items: center; padding: 3px 10px;
    border-radius: 20px; font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.04em; text-transform: uppercase; white-space: nowrap;
}
.badge-ok { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }
.badge-warn { background: var(--yellow-bg); color: var(--yellow-text); border: 1px solid var(--yellow-border); }
.badge-fail, .badge-blocked { background: var(--red-bg); color: var(--red-text); border: 1px solid var(--red-border); }
.badge-info { background: var(--blue-bg); color: var(--blue-text); border: 1px solid var(--blue-border); }
.badge-na { background: var(--gray-bg); color: var(--gray-text); border: 1px solid var(--gray-border); }
.badge-purple { background: var(--purple-bg); color: var(--purple-text); border: 1px solid var(--purple-border); }

/* Status dot */
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; flex-shrink: 0; }
.dot-ok { background: var(--green); }
.dot-warn { background: var(--yellow); }
.dot-fail { background: var(--red); }
.dot-na { background: var(--gray); }

/* Cards */
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 18px 20px; margin-bottom: 14px;
    box-shadow: var(--shadow-sm);
}
.card-accent-green { border-left: 4px solid var(--green); }
.card-accent-yellow { border-left: 4px solid var(--yellow); }
.card-accent-red { border-left: 4px solid var(--red); }
.card-accent-blue { border-left: 4px solid var(--blue); }
.card-accent-purple { border-left: 4px solid var(--purple); }

/* Grid */
.grid { display: grid; gap: 14px; }
.grid-2 { grid-template-columns: 1fr 1fr; }
.grid-3 { grid-template-columns: 1fr 1fr 1fr; }
.grid-4 { grid-template-columns: repeat(4, 1fr); }
.grid-auto { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
@media (max-width: 900px) { .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; } }

/* KV pairs */
.kv { margin: 5px 0; display: flex; gap: 6px; align-items: baseline; flex-wrap: wrap; }
.kv-label { color: var(--text-muted); font-size: 0.8rem; font-weight: 500; min-width: 0; }
.kv-value { font-weight: 500; font-size: 0.88rem; }
.kv-mono { font-family: var(--mono); font-size: 0.8rem; word-break: break-all; }

/* Top summary hero */
.hero {
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 24px 28px; margin-bottom: 20px; box-shadow: var(--shadow);
}
.hero-top {
    display: flex; justify-content: space-between; align-items: flex-start;
    flex-wrap: wrap; gap: 12px; margin-bottom: 20px;
}
.hero-title { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.hero-meta { color: var(--text-muted); font-size: 0.8rem; margin-top: 4px; }
.hero-status {
    font-size: 0.85rem; font-weight: 700; padding: 6px 16px;
    border-radius: 20px; letter-spacing: 0.05em;
}
.hero-status-ok { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }
.hero-status-warn { background: var(--yellow-bg); color: var(--yellow-text); border: 1px solid var(--yellow-border); }
.hero-status-blocked { background: var(--red-bg); color: var(--red-text); border: 1px solid var(--red-border); }

/* Metrics row */
.metrics-row {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px; margin-top: 16px;
}
.metric {
    text-align: center; padding: 12px 8px;
    background: var(--surface-alt); border-radius: var(--radius-sm);
    border: 1px solid var(--border-light);
}
.metric-value { font-size: 1.3rem; font-weight: 700; line-height: 1.2; }
.metric-label { font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }

/* Next step banner */
.next-step {
    background: linear-gradient(135deg, var(--blue-bg), #f0f4ff);
    border: 1px solid var(--blue-border); border-radius: var(--radius);
    padding: 14px 20px; margin-bottom: 20px;
    display: flex; align-items: center; gap: 10px;
}
.next-step-icon { font-size: 1.1rem; flex-shrink: 0; }
.next-step-text { font-weight: 500; font-size: 0.9rem; color: var(--blue-text); }

/* Stage flow */
.stage-flow {
    display: flex; align-items: center; gap: 0; overflow-x: auto;
    padding: 8px 4px; margin: 0 -4px;
}
.stage-node {
    display: flex; flex-direction: column; align-items: center;
    padding: 10px 14px; border-radius: var(--radius-sm);
    border: 2px solid var(--border); background: var(--surface);
    min-width: 110px; text-align: center; flex-shrink: 0;
    transition: all 0.15s;
}
.stage-node-completed { border-color: var(--green); background: var(--green-bg); }
.stage-node-active { border-color: var(--blue); background: var(--blue-bg); box-shadow: 0 0 0 3px rgba(37,99,235,0.15); }
.stage-node-blocked { border-color: var(--red); background: var(--red-bg); }
.stage-node-pending { border-color: var(--border); background: var(--surface-alt); opacity: 0.7; }
.stage-name { font-size: 0.76rem; font-weight: 600; margin-top: 4px; }
.stage-icon { font-size: 1rem; }
.stage-arrow {
    color: var(--text-muted); font-size: 0.9rem; margin: 0 2px;
    flex-shrink: 0; display: flex; align-items: center;
}
.stage-arrow-done { color: var(--green); }

/* Capability map */
.cap-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.cap-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-sm); padding: 14px 16px;
    display: flex; flex-direction: column; gap: 6px;
    box-shadow: var(--shadow-sm);
}
.cap-header { display: flex; justify-content: space-between; align-items: center; }
.cap-title { font-size: 0.88rem; font-weight: 600; }
.cap-desc { font-size: 0.78rem; color: var(--text-secondary); line-height: 1.45; }
.cap-meta { font-size: 0.72rem; color: var(--text-muted); }

/* Table */
table { width: 100%; border-collapse: collapse; font-size: 0.82rem; margin: 8px 0; }
th {
    text-align: left; padding: 8px 10px; font-weight: 600;
    background: var(--surface-alt); border-bottom: 2px solid var(--border);
    font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;
    color: var(--text-secondary);
}
td { padding: 7px 10px; border-bottom: 1px solid var(--border-light); vertical-align: top; }
tr:hover { background: var(--surface-alt); }

/* Code / snippet */
.snippet {
    background: var(--surface-alt); border: 1px solid var(--border-light);
    border-radius: var(--radius-sm); padding: 10px 14px;
    font-family: var(--mono); font-size: 0.78rem;
    white-space: pre-wrap; max-height: 180px; overflow-y: auto;
    margin: 6px 0; line-height: 1.6;
}
.cmd-block {
    background: #1e293b; color: #e2e8f0; border-radius: var(--radius-sm);
    padding: 10px 14px; font-family: var(--mono); font-size: 0.8rem;
    margin: 6px 0; user-select: all; cursor: text;
}

/* Empty state */
.empty-state {
    padding: 20px; text-align: center; color: var(--text-muted);
    font-size: 0.85rem; background: var(--surface-alt);
    border-radius: var(--radius-sm); border: 1px dashed var(--border);
}

/* Footer */
.footer {
    color: var(--text-muted); font-size: 0.74rem;
    margin-top: 40px; padding-top: 16px;
    border-top: 1px solid var(--border); text-align: center;
}
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


# -- Hero / Top Summary ----------------------------------------------------

def _render_hero(d: dict[str, Any]) -> str:
    status = d["overall_status"]
    status_cls = {"OK": "hero-status-ok", "WARN": "hero-status-warn", "BLOCKED": "hero-status-blocked"}.get(status, "hero-status-warn")
    stage = d.get("current_stage", "unknown")
    stage_display = stage.replace("_", " ").title()
    task_title = d["current_task"].get("title") or "No active task"
    task_state = d["task_state"].get("state", "unknown")
    bqa_v = d["browser_qa"].get("verdict", "") or "N/A"
    qa_v = d["latest_evidence"].get("qa_verdict") or "N/A"
    blockers_open = d["blockers"]["open"]

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
    <div class="metric"><div class="metric-value">{_h(stage_display)}</div><div class="metric-label">Current Stage</div></div>
    <div class="metric"><div class="metric-value">{_h(task_state)}</div><div class="metric-label">Task State</div></div>
    <div class="metric"><div class="metric-value">{_h(str(qa_v)[:20])}</div><div class="metric-label">QA Verdict</div></div>
    <div class="metric"><div class="metric-value">{_h(str(bqa_v)[:20])}</div><div class="metric-label">Browser QA</div></div>
    <div class="metric"><div class="metric-value">{blockers_open}</div><div class="metric-label">Open Blockers</div></div>
    <div class="metric"><div class="metric-value">{_h(d['autonomy_mode'])}</div><div class="metric-label">Autonomy</div></div>
  </div>
</div>
"""


def _render_next_step(d: dict[str, Any]) -> str:
    return f"""\
<div class="next-step">
  <span class="next-step-icon">&#10148;</span>
  <span class="next-step-text">Next: {_h(d["next_step"])}</span>
</div>
"""


# -- Stage Flow -------------------------------------------------------------

_STAGES = [
    ("setup", "Setup"),
    ("research", "Research"),
    ("planning", "Planning"),
    ("builder_handoff", "Builder Handoff"),
    ("implementation", "Implementation"),
    ("validation", "Validation"),
    ("qa_verdict", "QA Verdict"),
    ("scheduler_readiness", "Scheduler Ready"),
]

_STAGE_ICONS = {
    "setup": "&#9881;",            # gear
    "research": "&#128269;",       # magnifying glass
    "planning": "&#128203;",       # clipboard
    "builder_handoff": "&#128229;", # envelope
    "implementation": "&#128296;",  # wrench
    "validation": "&#9989;",       # check
    "qa_verdict": "&#128202;",     # chart
    "scheduler_readiness": "&#128640;", # rocket
}


def _render_stage_flow(d: dict[str, Any]) -> str:
    current = d.get("current_stage", "unknown")
    stage_order = [s[0] for s in _STAGES]
    current_idx = stage_order.index(current) if current in stage_order else -1

    nodes: list[str] = []
    for i, (key, label) in enumerate(_STAGES):
        if key == current:
            cls = "stage-node stage-node-active"
        elif current == "blocked":
            cls = "stage-node stage-node-blocked" if i == 0 else "stage-node stage-node-pending"
        elif current_idx >= 0 and i < current_idx:
            cls = "stage-node stage-node-completed"
        else:
            cls = "stage-node stage-node-pending"

        icon = _STAGE_ICONS.get(key, "&#9679;")
        nodes.append(f'<div class="{cls}"><span class="stage-icon">{icon}</span><span class="stage-name">{_h(label)}</span></div>')
        if i < len(_STAGES) - 1:
            arrow_cls = "stage-arrow stage-arrow-done" if current_idx >= 0 and i < current_idx else "stage-arrow"
            nodes.append(f'<span class="{arrow_cls}">&#10148;</span>')

    return f'<div class="stage-flow">{"".join(nodes)}</div>'


# -- You Are Here -----------------------------------------------------------

def _render_you_are_here(d: dict[str, Any]) -> str:
    stage = d.get("current_stage", "unknown").replace("_", " ").title()
    task = d["current_task"]
    risk = d.get("risk", {})
    risk_level = risk.get("risk_level", "unknown")
    risk_cats = risk.get("categories") or risk.get("risk_categories") or []
    if isinstance(risk_cats, list):
        risk_cats_str = ", ".join(risk_cats) if risk_cats else "none"
    else:
        risk_cats_str = str(risk_cats)
    blockers_open = d["blockers"]["open"]
    hq_count = len(d.get("human_questions", []))
    evidence = d.get("latest_evidence", {})
    evidence_id = evidence.get("run_id") or evidence.get("bundle_id") or "none"

    lines = [f'<div class="card card-accent-purple">']
    lines.append(f'<h3>You Are Here</h3>')
    lines.append(f'<div class="grid grid-2" style="margin-top:8px">')
    lines.append(f'<div>')
    lines.append(_kv("Project phase", stage))
    lines.append(_kv("Active task", task.get("title") or "None"))
    lines.append(_kv("Task state", d["task_state"].get("state", "unknown")))
    lines.append(_kv("Risk level", risk_level))
    lines.append(_kv("Risk categories", risk_cats_str))
    lines.append(f'</div><div>')
    lines.append(_kv("Open blockers", str(blockers_open)))
    lines.append(_kv("Human questions", str(hq_count)))
    lines.append(_kv("Latest evidence", evidence_id, mono=True))
    lines.append(_kv("Builder prompt", d.get("builder_prompt_path", "") or "none", mono=True))
    if d.get("correction_prompt_exists"):
        lines.append(_kv("Correction prompt", d["correction_prompt_path"], mono=True))
    lines.append(f'</div></div>')

    next_cmd = _suggest_command(d)
    if next_cmd:
        lines.append(f'<div style="margin-top:12px"><span class="kv-label">Recommended command</span></div>')
        lines.append(f'<div class="cmd-block">{_h(next_cmd)}</div>')

    lines.append(f'</div>')
    return "\n".join(lines)


def _suggest_command(d: dict[str, Any]) -> str:
    """Derive a concrete CLI command based on state."""
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


# -- Capability Map ---------------------------------------------------------

_CAPABILITIES = [
    {
        "key": "control",
        "title": "Control Layer",
        "desc": "HALT, run lock, config validation, autonomy gates",
        "files": ["agent_loop.py", "config_validator.py", "run_lock.py"],
        "status_fn": "_cap_control",
    },
    {
        "key": "reliability",
        "title": "Reliability Core",
        "desc": "Evidence bundles, task state, run history, metrics",
        "files": ["evidence_bundle.py", "task_state.py", "run_history.py", "run_metrics.py"],
        "status_fn": "_cap_reliability",
    },
    {
        "key": "builder",
        "title": "Builder Handoff",
        "desc": "Prompt building, Claude runner, builder intake",
        "files": ["prompt_builder.py", "claude_runner.py", "builder_intake.py"],
        "status_fn": "_cap_builder",
    },
    {
        "key": "qa",
        "title": "QA Layer",
        "desc": "Post-builder QA, correction prompts, risk classifier",
        "files": ["qa_reviewer.py", "risk_classifier.py"],
        "status_fn": "_cap_qa",
    },
    {
        "key": "browser_qa",
        "title": "Browser QA",
        "desc": "Route testing, screenshots, console/network audit",
        "files": ["browser_qa.py"],
        "status_fn": "_cap_browser_qa",
    },
    {
        "key": "research",
        "title": "Research",
        "desc": "Research requests, deep research, approval flow",
        "files": ["research_log.py"],
        "status_fn": "_cap_research",
    },
    {
        "key": "observability",
        "title": "Observability",
        "desc": "Control center, Telegram alerts, run metrics",
        "files": ["control_center.py", "telegram_alerts.py", "run_metrics.py"],
        "status_fn": "_cap_observability",
    },
    {
        "key": "scheduler",
        "title": "Scheduler Readiness",
        "desc": "Systemd templates, retry policy, VPS deployment",
        "files": [],
        "status_fn": "_cap_scheduler",
    },
    {
        "key": "safety",
        "title": "Safety / Budget / Risk",
        "desc": "Cost controller, budget gates, auto-exec controls",
        "files": ["cost_controller.py", "risk_classifier.py"],
        "status_fn": "_cap_safety",
    },
]


def _cap_status(d: dict[str, Any], cap_key: str) -> tuple[str, str]:
    """Return (status_word, badge_kind) for each capability."""
    if cap_key == "control":
        if d.get("halt_active"):
            return ("HALTED", "fail")
        return ("Active", "ok")
    if cap_key == "reliability":
        if d.get("latest_evidence"):
            return ("Active", "ok")
        return ("No data", "na")
    if cap_key == "builder":
        if d.get("builder_prompt_path"):
            return ("Ready", "ok")
        return ("Pending", "na")
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
        if bv:
            return (bv, "warn")
        return ("Not run", "na")
    if cap_key == "research":
        rc = d.get("research", {}).get("count", 0)
        if rc > 0:
            return (f"{rc} requests", "info")
        return ("None", "na")
    if cap_key == "observability":
        return ("Active", "ok")
    if cap_key == "scheduler":
        return ("Not enabled", "na")
    if cap_key == "safety":
        if d.get("allow_auto_exec"):
            return ("Auto-exec ON", "warn")
        return ("Locked down", "ok")
    return ("Unknown", "na")


def _render_capability_map(d: dict[str, Any]) -> str:
    cards: list[str] = []
    for cap in _CAPABILITIES:
        status_word, badge_kind = _cap_status(d, cap["key"])
        file_str = f'{len(cap["files"])} modules' if cap["files"] else "templates only"
        cards.append(f"""\
<div class="cap-card">
  <div class="cap-header">
    <span class="cap-title">{_h(cap['title'])}</span>
    {_badge(status_word, badge_kind)}
  </div>
  <div class="cap-desc">{_h(cap['desc'])}</div>
  <div class="cap-meta">{_h(file_str)}</div>
</div>""")
    return f'<div class="cap-grid">{"".join(cards)}</div>'


# -- Current Task -----------------------------------------------------------

def _render_current_task(d: dict[str, Any]) -> str:
    task = d["current_task"]
    title = task.get("title")
    if not title:
        return '<div class="empty-state">No current task detected in TASK_QUEUE.md</div>'
    risk = d.get("risk", {})
    lines = [f'<div class="card card-accent-blue">']
    lines.append(f'<h3>{_h(title)}</h3>')
    lines.append(f'<div class="grid grid-2" style="margin-top:6px">')
    lines.append(f'<div>')
    lines.append(_kv("Task state", d["task_state"].get("state", "unknown")))
    if risk:
        lines.append(_kv("Risk level", risk.get("risk_level", "unknown")))
        cats = risk.get("categories") or risk.get("risk_categories") or []
        if cats:
            lines.append(_kv("Risk categories", ", ".join(cats) if isinstance(cats, list) else str(cats)))
    lines.append(f'</div><div>')
    if risk.get("recommended_action") or risk.get("action"):
        lines.append(_kv("Recommended action", risk.get("recommended_action", risk.get("action", ""))))
    lines.append(_kv("Builder prompt", d.get("builder_prompt_path", "") or "none", mono=True))
    if d.get("correction_prompt_exists"):
        lines.append(_kv("Correction prompt", d["correction_prompt_path"], mono=True))
    lines.append(f'</div></div>')
    if task.get("criteria"):
        lines.append(f'<div style="margin-top:10px"><span class="kv-label">Acceptance criteria</span></div>')
        lines.append(f'<div class="snippet">{_h(task["criteria"])}</div>')
    lines.append('</div>')
    return "\n".join(lines)


# -- Latest Run Summary -----------------------------------------------------

def _render_latest_run(d: dict[str, Any]) -> str:
    m = d.get("latest_metrics")
    if not m:
        return '<div class="empty-state">No run metrics recorded yet.</div>'
    qa = m.get("qa_verdict") or "N/A"
    outcome = m.get("outcome", "")
    accent = "card-accent-green" if outcome == "success" else ("card-accent-red" if outcome == "failure" else "")
    lines = [f'<div class="card {accent}">']
    lines.append(f'<div class="grid grid-3" style="margin-bottom:8px">')
    lines.append(f'<div>{_kv("Run ID", m.get("run_id", ""), mono=True)}</div>')
    lines.append(f'<div>{_kv_badge("Outcome", outcome or "N/A")}</div>')
    lines.append(f'<div>{_kv_badge("QA Verdict", str(qa))}</div>')
    lines.append(f'</div>')
    dur = m.get("total_duration_seconds", 0)
    cmds_exec = m.get("commands_executed", 0)
    cmds_fail = m.get("commands_failed", 0)
    f_created = m.get("files_created", 0)
    f_modified = m.get("files_modified", 0)
    f_deleted = m.get("files_deleted", 0)
    l_added = m.get("lines_added", 0)
    l_removed = m.get("lines_removed", 0)
    lines.append('<div class="grid grid-4">')
    lines.append(f'<div>{_kv("Duration", f"{dur}s")}</div>')
    lines.append(f'<div>{_kv("Commands", f"{cmds_exec} ({cmds_fail} failed)")}</div>')
    lines.append(f'<div>{_kv("Files", f"+{f_created} ~{f_modified} -{f_deleted}")}</div>')
    lines.append(f'<div>{_kv("Lines", f"+{l_added} / -{l_removed}")}</div>')
    lines.append('</div>')
    if m.get("evidence_bundle_path"):
        lines.append(f'<div style="margin-top:6px">{_kv("Evidence", m["evidence_bundle_path"], mono=True)}</div>')
    lines.append('</div>')
    return "\n".join(lines)


# -- Activity Timeline ------------------------------------------------------

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
    return f'<div class="card" style="overflow-x:auto;padding:12px"><table>{header}{"".join(rows)}</table></div>'


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
        st = _cmd_status(key)
        lines.append(f'<div>{_kv_badge(label, st)}</div>')
    qa = ev.get("qa_verdict") or "N/A"
    lines.append(f'<div>{_kv_badge("QA Verdict", str(qa))}</div>')
    bqa_verdict = d.get("browser_qa", {}).get("verdict", "") or "N/A"
    lines.append(f'<div>{_kv_badge("Browser QA", bqa_verdict)}</div>')
    lines.append(f'<div>{_kv_badge("Backend Audit", d.get("backend_readiness", "N/A"))}</div>')
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
        return '<div class="empty-state">No Browser QA results available. Run --browser-qa to generate.</div>'

    accent = "card-accent-green" if verdict == "PASS" else ("card-accent-red" if verdict == "FAIL" else "card-accent-yellow")
    lines = [f'<div class="card {accent}">']
    lines.append(f'<h3>Browser QA {_status_badge(verdict)}</h3>')
    lines.append(f'<div class="grid grid-3" style="margin-top:8px">')

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

    lines.append(f'<div>')
    lines.append(_kv("Mode", mode))
    lines.append(_kv("Routes", f"{routes_checked} checked"))
    lines.append(_kv("Passed", str(routes_passed)))
    lines.append(_kv("Failed", str(routes_failed)))
    lines.append(f'</div><div>')
    lines.append(_kv("Console errors", str(console_errs)))
    lines.append(_kv("Page errors", str(page_errs)))
    lines.append(_kv("Network failures", str(net_reqs + net_loads)))
    lines.append(f'</div><div>')
    lines.append(_kv("Total issues", str(total_issues)))
    lines.append(_kv("Screenshots", str(screenshots)))
    lines.append(_kv("Report", bqa.get("report_path", ""), mono=True))
    lines.append(f'</div></div></div>')
    return "\n".join(lines)


# -- Backend / Data ---------------------------------------------------------

def _render_backend(d: dict[str, Any]) -> str:
    audit = d.get("backend_audit", {})
    lines = [f'<div class="card">']
    lines.append(f'<h3>Backend / Data {_status_badge(d.get("backend_readiness", "N/A"))}</h3>')
    if not audit:
        lines.append('<div class="empty-state" style="margin-top:8px">No backend audit data. Run --backend-audit to generate.</div>')
    else:
        tables = audit.get("tables_referenced", [])
        buckets = audit.get("buckets_referenced", [])
        manual = audit.get("manual_verification_required", [])
        lines.append(f'<div class="grid grid-3" style="margin-top:8px">')
        lines.append(f'<div>{_kv("Tables", ", ".join(tables) if tables else "none")}</div>')
        lines.append(f'<div>{_kv("Buckets", ", ".join(buckets) if buckets else "none")}</div>')
        lines.append(f'<div>{_kv("Manual items", str(len(manual)))}</div>')
        lines.append(f'</div>')
        if manual:
            lines.append('<ul style="margin:8px 0 0 18px;font-size:0.82rem;color:var(--text-secondary)">')
            for item in manual[:6]:
                lines.append(f"<li>{_h(item)}</li>")
            if len(manual) > 6:
                lines.append(f"<li>... and {len(manual) - 6} more</li>")
            lines.append("</ul>")
    risk_cats = d.get("risk", {}).get("categories", d.get("risk", {}).get("risk_categories", []))
    has_data_risk = "data_schema_change" in (risk_cats if isinstance(risk_cats, list) else [])
    if has_data_risk:
        lines.append(f'<div style="margin-top:8px">{_badge("data_schema_change risk", "warn")}</div>')
    lines.append("</div>")
    return "\n".join(lines)


# -- Blockers & Questions ---------------------------------------------------

def _render_blockers(d: dict[str, Any]) -> str:
    blockers = d.get("blockers_detail", [])
    questions = d.get("human_questions", [])
    bs = d.get("blockers", {})
    open_count = bs.get("open", 0)

    lines = []

    # Blockers
    accent = "card-accent-red" if open_count > 0 else ""
    lines.append(f'<div class="card {accent}">')
    lines.append(f'<h3>Blockers <span style="font-weight:400;font-size:0.82rem;color:var(--text-muted)">{open_count} open, {bs.get("resolved", 0)} resolved, {bs.get("parked", 0)} parked</span></h3>')
    if blockers:
        lines.append("<table><tr><th>Title</th><th>Status</th><th>Severity</th></tr>")
        for b in blockers:
            st = b.get("status", "").lower()
            badge_kind = "fail" if st == "open" else ("ok" if st == "resolved" else "na")
            lines.append(
                f"<tr><td>{_h(b.get('title', ''))}</td>"
                f"<td>{_badge(st, badge_kind)}</td>"
                f"<td>{_h(b.get('severity', ''))}</td></tr>"
            )
        lines.append("</table>")
    else:
        lines.append('<div class="empty-state" style="margin-top:8px">No blockers. All clear.</div>')
    lines.append("</div>")

    # Human questions
    if questions:
        lines.append(f'<div class="card card-accent-yellow">')
        lines.append(f'<h3>Human Questions <span style="font-weight:400;font-size:0.82rem;color:var(--text-muted)">{len(questions)} pending</span></h3>')
        lines.append("<table><tr><th>Question</th><th>Status</th><th>Severity</th></tr>")
        for q in questions:
            st = q.get("status", "").lower()
            lines.append(
                f"<tr><td>{_h(q.get('title', ''))}</td>"
                f"<td>{_badge(st, 'warn' if st == 'open' else 'ok')}</td>"
                f"<td>{_h(q.get('severity', ''))}</td></tr>"
            )
        lines.append("</table></div>")

    return "\n".join(lines)


# -- Research ---------------------------------------------------------------

def _render_research(d: dict[str, Any]) -> str:
    r = d.get("research", {})
    count = r.get("count", 0)
    lines = ['<div class="card">']
    lines.append(f'<h3>Research</h3>')
    if count == 0:
        lines.append('<div class="empty-state" style="margin-top:8px">No research requests recorded.</div>')
    else:
        lines.append(f'<div class="grid grid-3" style="margin-top:6px">')
        lines.append(f'<div>{_kv("Total requests", count)}</div>')
        lines.append(f'<div>{_kv("Pending approval", r.get("deep_research_pending_approval", 0))}</div>')
        lines.append(f'<div>{_kv("Completed", r.get("completed_count", 0))}</div>')
        lines.append(f'</div>')
        latest = r.get("latest")
        if latest:
            lines.append(f'<div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--border-light)">')
            lines.append(f'<span class="kv-label" style="font-weight:600">Latest request</span>')
            lines.append(_kv("Topic", latest.get("topic", "")))
            lines.append(_kv("Mode", latest.get("mode", "")))
            lines.append(_kv_badge("Status", latest.get("status", "")))
            if latest.get("requires_human_approval"):
                lines.append(f'<div style="margin-top:4px">{_badge("Requires human approval", "warn")}</div>')
            lines.append(f'</div>')
    lines.append("</div>")
    return "\n".join(lines)


# -- Budget -----------------------------------------------------------------

def _render_budget(d: dict[str, Any]) -> str:
    cost = d.get("cost", {})
    lines = ['<div class="card">']
    lines.append(f'<div class="grid grid-3">')
    lines.append(f'<div>')
    lines.append(f'<span class="kv-label" style="font-weight:600">Budget Limits</span>')
    lines.append(_kv("Per-cycle", f"${d['per_cycle_budget']:.2f}"))
    lines.append(_kv("Daily", f"${d['daily_budget']:.2f}"))
    lines.append(_kv("Monthly", f"${d['monthly_budget']:.2f}"))
    lines.append(f'</div><div>')
    lines.append(f'<span class="kv-label" style="font-weight:600">Current Spend</span>')
    if cost:
        lines.append(_kv("Cycle", f"${cost.get('cycle_spend_usd', 0):.4f}"))
        lines.append(_kv("Daily", f"${cost.get('daily_spend_usd', 0):.4f}"))
        lines.append(_kv("Monthly", f"${cost.get('monthly_spend_usd', 0):.4f}"))
    else:
        lines.append('<div class="kv"><span class="kv-label">No cost data</span></div>')
    lines.append(f'</div><div>')
    lines.append(f'<span class="kv-label" style="font-weight:600">Controls</span>')
    lines.append(_kv("API mode", d["paid_api_mode"]))
    lines.append(_kv("Paid images", "enabled" if d["allow_paid_image"] else "disabled"))
    lines.append(_kv("Paid video", "enabled" if d["allow_paid_video"] else "disabled"))
    lines.append(f'</div></div></div>')
    return "\n".join(lines)


# -- Safety Gates -----------------------------------------------------------

def _render_safety(d: dict[str, Any]) -> str:
    lock = d.get("lock", {})
    lines = ['<div class="card">']
    lines.append(f'<div class="grid grid-auto">')

    gates = [
        ("HALT file", "ACTIVE" if d["halt_active"] else "not active", "fail" if d["halt_active"] else "ok"),
        ("Auto Claude exec", "enabled" if d["allow_auto_exec"] else "disabled", "warn" if d["allow_auto_exec"] else "ok"),
        ("Run lock", "HELD" if lock.get("locked") else ("STALE" if lock.get("stale") else "free"), "warn" if lock.get("locked") else "ok"),
        ("Max parallel agents", str(d["max_parallel_agents"]), "info"),
        ("Telegram alerts", "on" if d["telegram_enabled"] else "off", "ok" if d["telegram_enabled"] else "na"),
        ("Deploy automation", "disabled", "ok"),
        ("Scheduler", "not enabled", "na"),
    ]
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

        # 1. Hero — above the fold
        _render_hero(d),
        _render_next_step(d),

        # 2. Stage flow with arrows
        _section("stage-flow", "Lifecycle Stage", _render_stage_flow(d)),

        # 3. You Are Here
        _section("you-are-here", "Current State", _render_you_are_here(d)),

        # 4. Current Task
        _section("task", "Current Task", _render_current_task(d)),

        # 5. Capability Map
        _section("capabilities", "Capability Map", _render_capability_map(d)),

        # 6. Latest Run
        _section("latest-run", "Latest Run", _render_latest_run(d)),

        # 7. Quality Gates
        _section("quality", "Quality Gates", _render_quality_gates(d)),

        # 8. Browser QA
        _section("browser-qa", "Browser QA", _render_browser_qa(d)),

        # 9. Backend
        _section("backend", "Backend / Customer Data", _render_backend(d)),

        # 10. Blockers & Questions
        _section("blockers", "Blockers & Human Questions", _render_blockers(d)),

        # 11. Research
        _section("research", "Research", _render_research(d)),

        # 12. Activity Timeline
        _section("timeline", "Activity Timeline", _render_timeline(d)),

        # 13. Budget
        _section("budget", "Budget / Cost", _render_budget(d)),

        # 14. Safety Gates
        _section("safety", "Safety / Autonomy Gates", _render_safety(d)),

        # Footer
        f'<div class="footer">Project Autopilot Control Center v2.0 &middot; Generated {_h(d["generated_at_display"])} &middot; Read-only &middot; No secrets included</div>',
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
    parser = argparse.ArgumentParser(description="Project Autopilot Control Center v2.0")
    parser.add_argument("--project", default="mira", help="Project id.")
    args = parser.parse_args()

    project = load_project_config(args.project)
    path = generate_control_center(project)
    print(f"Control Center generated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
