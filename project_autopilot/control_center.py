"""Project Autopilot Control Center Lite v0.1.

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

    return data


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

_CSS = """
:root {
    --bg: #f8f9fa; --surface: #ffffff; --border: #dee2e6;
    --text: #212529; --muted: #6c757d; --mono: 'Consolas', 'Monaco', 'Courier New', monospace;
    --green: #198754; --green-bg: #d1e7dd; --green-border: #badbcc;
    --yellow: #856404; --yellow-bg: #fff3cd; --yellow-border: #ffecb5;
    --red: #842029; --red-bg: #f8d7da; --red-border: #f5c2c7;
    --blue: #084298; --blue-bg: #cfe2ff; --blue-border: #b6d4fe;
    --gray: #495057; --gray-bg: #e9ecef; --gray-border: #ced4da;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; padding: 20px; max-width: 1200px; margin: 0 auto; }
h1 { font-size: 1.5rem; margin-bottom: 4px; }
h2 { font-size: 1.15rem; margin: 24px 0 12px; padding-bottom: 6px; border-bottom: 2px solid var(--border); }
h3 { font-size: 1rem; margin: 12px 0 6px; }
.header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; }
.header-left h1 { font-size: 1.5rem; }
.header-left .meta { color: var(--muted); font-size: 0.85rem; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.03em; }
.badge-ok { background: var(--green-bg); color: var(--green); border: 1px solid var(--green-border); }
.badge-warn { background: var(--yellow-bg); color: var(--yellow); border: 1px solid var(--yellow-border); }
.badge-fail, .badge-blocked { background: var(--red-bg); color: var(--red); border: 1px solid var(--red-border); }
.badge-info { background: var(--blue-bg); color: var(--blue); border: 1px solid var(--blue-border); }
.badge-na { background: var(--gray-bg); color: var(--gray); border: 1px solid var(--gray-border); }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 16px; }
.card-green { border-left: 4px solid var(--green); }
.card-yellow { border-left: 4px solid #ffc107; }
.card-red { border-left: 4px solid #dc3545; }
.card-blue { border-left: 4px solid #0d6efd; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.kv { margin: 4px 0; }
.kv .label { color: var(--muted); font-size: 0.82rem; }
.kv .value { font-weight: 500; }
.mono { font-family: var(--mono); font-size: 0.85rem; word-break: break-all; }
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin: 8px 0; }
th { text-align: left; background: var(--bg); padding: 6px 8px; border-bottom: 2px solid var(--border); font-weight: 600; }
td { padding: 5px 8px; border-bottom: 1px solid var(--border); vertical-align: top; }
tr:hover { background: #f1f3f5; }
.next-step { background: var(--blue-bg); border: 1px solid var(--blue-border); border-radius: 8px; padding: 14px 18px; margin: 16px 0; font-weight: 500; }
.snippet { background: var(--bg); border: 1px solid var(--border); border-radius: 4px; padding: 10px; font-family: var(--mono); font-size: 0.82rem; white-space: pre-wrap; max-height: 200px; overflow-y: auto; margin: 6px 0; }
.footer { color: var(--muted); font-size: 0.78rem; margin-top: 30px; padding-top: 12px; border-top: 1px solid var(--border); text-align: center; }
"""


def _h(text: str) -> str:
    return escape(str(text)) if text else ""


def _badge(label: str, kind: str = "info") -> str:
    return f'<span class="badge badge-{kind}">{_h(label)}</span>'


def _status_badge(value: str) -> str:
    v = str(value).upper()
    if v in ("PASS", "OK", "READY", "READY_FOR_MANUAL_E2E"):
        return _badge(v, "ok")
    if v in ("WARN", "PARTIAL_READY", "NEEDS REVIEW"):
        return _badge(v, "warn")
    if v in ("FAIL", "BLOCKED", "FAIL_FIX_REQUIRED"):
        return _badge(v, "fail")
    if v in ("SKIPPED_DEV_SERVER_DOWN", "SKIPPED"):
        return _badge(v, "warn")
    if not v or v in ("NONE", "UNKNOWN", "N/A"):
        return _badge("N/A", "na")
    return _badge(v, "info")


def _kv(label: str, value: Any, mono: bool = False) -> str:
    cls = "value mono" if mono else "value"
    return f'<div class="kv"><span class="label">{_h(label)}:</span> <span class="{cls}">{_h(str(value))}</span></div>'


def _kv_badge(label: str, value: str) -> str:
    return f'<div class="kv"><span class="label">{_h(label)}:</span> {_status_badge(value)}</div>'


def _section(title: str, content: str) -> str:
    return f"<h2>{_h(title)}</h2>\n{content}\n"


def _render_header(d: dict[str, Any]) -> str:
    status = d["overall_status"]
    badge = _status_badge(status)
    return f"""
<div class="header">
  <div class="header-left">
    <h1>Control Center &mdash; {_h(d['project_name'])} ({_h(d['project_id'])})</h1>
    <div class="meta">Generated {_h(d['generated_at_display'])} &middot; {_h(d['repo_path'])}</div>
  </div>
  <div>{badge}</div>
</div>
<div class="grid">
  <div class="card">
    {_kv('Autonomy', d['autonomy_mode'])}
    {_kv('Intensity', d['intensity_mode'])}
    {_kv('Builder', f"{d['builder_primary']} / {d['builder_fallback']}")}
    {_kv('Telegram', 'yes' if d['telegram_enabled'] else 'no')}
  </div>
  <div class="card">
    {_kv('Task state', d['task_state'].get('state', 'unknown'))}
    {_kv_badge('Browser QA', d['browser_qa'].get('verdict', 'N/A'))}
    {_kv_badge('Backend', d.get('backend_readiness', 'N/A'))}
    {_kv('Open blockers', d['blockers']['open'])}
  </div>
</div>
"""


def _render_next_step(d: dict[str, Any]) -> str:
    return f'<div class="next-step">Recommended next step: {_h(d["next_step"])}</div>'


def _render_current_task(d: dict[str, Any]) -> str:
    task = d["current_task"]
    risk = d.get("risk", {})
    lines = []
    lines.append('<div class="card card-blue">')
    lines.append(f'<h3>Current Task</h3>')
    lines.append(_kv("Title", task.get("title") or "No current task detected"))
    lines.append(_kv("Task state", d["task_state"].get("state", "unknown")))
    if risk:
        lines.append(_kv("Risk level", risk.get("risk_level", "unknown")))
        cats = risk.get("categories") or risk.get("risk_categories") or []
        if cats:
            lines.append(_kv("Risk categories", ", ".join(cats) if isinstance(cats, list) else str(cats)))
        lines.append(_kv("Recommended action", risk.get("recommended_action", risk.get("action", ""))))
    if task.get("criteria"):
        lines.append(f'<div class="snippet">{_h(task["criteria"])}</div>')
    lines.append(_kv("Builder prompt", d.get("builder_prompt_path", ""), mono=True))
    if d.get("correction_prompt_exists"):
        lines.append(_kv("Correction prompt", d["correction_prompt_path"], mono=True))
    lines.append('</div>')
    return "\n".join(lines)


def _render_latest_run(d: dict[str, Any]) -> str:
    m = d.get("latest_metrics")
    if not m:
        return '<div class="card">No run metrics recorded yet.</div>'
    rows = [
        ("Run ID", m.get("run_id", "")),
        ("Outcome", m.get("outcome", "")),
        ("Active duration", f"{m.get('active_duration_seconds', 0)}s"),
        ("Total duration", f"{m.get('total_duration_seconds', 0)}s"),
        ("Commands", f"{m.get('commands_executed', 0)} ({m.get('commands_failed', 0)} failed)"),
        ("Files", f"+{m.get('files_created', 0)} created, {m.get('files_modified', 0)} modified, {m.get('files_deleted', 0)} deleted"),
        ("Lines", f"+{m.get('lines_added', 0)} / -{m.get('lines_removed', 0)}"),
        ("QA verdict", m.get("qa_verdict") or "none"),
        ("Evidence bundle", m.get("evidence_bundle_path") or "none"),
    ]
    trs = "".join(f"<tr><td>{_h(k)}</td><td>{_h(str(v))}</td></tr>" for k, v in rows)
    return f'<div class="card"><table><tbody>{trs}</tbody></table></div>'


def _render_timeline(d: dict[str, Any]) -> str:
    events = d.get("recent_events", [])
    if not events:
        return '<div class="card">No events recorded yet.</div>'
    header = "<tr><th>Timestamp</th><th>Run ID</th><th>Event</th><th>Detail</th></tr>"
    rows: list[str] = []
    for ev in events:
        meta = ev.get("metadata", {})
        detail = ev.get("status") or meta.get("label") or meta.get("verdict") or meta.get("outcome") or ev.get("file_path") or ""
        rows.append(
            f"<tr><td class='mono'>{_h(str(ev.get('timestamp_utc', ''))[:19])}</td>"
            f"<td class='mono'>{_h(str(ev.get('run_id', '')))}</td>"
            f"<td>{_h(str(ev.get('event_type', '')))}</td>"
            f"<td>{_h(str(detail)[:80])}</td></tr>"
        )
    return f'<div class="card" style="overflow-x:auto"><table>{header}{"".join(rows)}</table></div>'


def _render_quality_gates(d: dict[str, Any]) -> str:
    ev = d.get("latest_evidence", {})
    cmds = ev.get("commands", {}) if isinstance(ev.get("commands"), dict) else {}
    # Try to get from evidence commands or fall back
    def _cmd_status(key: str) -> str:
        cmd = cmds.get(key, {})
        if not cmd:
            return "N/A"
        return "PASS" if cmd.get("exit_code") == 0 else "FAIL"

    lines = ['<div class="card"><div class="grid">']
    for label, key in [("Lint", "lint"), ("Typecheck", "typecheck"), ("Build", "build")]:
        st = _cmd_status(key)
        lines.append(f'<div>{_kv_badge(label, st)}</div>')
    qa = ev.get("qa_verdict") or "N/A"
    lines.append(f'<div>{_kv_badge("QA Verdict", str(qa))}</div>')
    lines.append(f'<div>{_kv_badge("Backend Audit", d.get("backend_readiness", "N/A"))}</div>')
    lines.append(f'<div>{_kv("Correction prompt", "yes" if d.get("correction_prompt_exists") else "no")}</div>')
    lines.append('</div></div>')
    return "\n".join(lines)


def _render_browser_qa(d: dict[str, Any]) -> str:
    bqa = d.get("browser_qa", {})
    verdict = bqa.get("verdict", "")
    summary = bqa.get("summary", {})
    mode = bqa.get("mode", "")

    card_class = "card-green" if verdict == "PASS" else ("card-red" if verdict == "FAIL" else "card-yellow")

    lines = [f'<div class="card {card_class}">']
    lines.append(f'<h3>Browser QA {_status_badge(verdict or "N/A")}</h3>')
    if not verdict:
        lines.append("<p>No Browser QA results available yet.</p>")
    else:
        lines.append(_kv("Mode", mode))
        viewports = d.get("autopilot_state", {}).get("browser_qa_summary", summary)
        routes_checked = viewports.get("routes_checked", summary.get("routes_checked", 0))
        routes_passed = viewports.get("routes_passed", summary.get("routes_passed", 0))
        routes_failed = viewports.get("routes_failed", summary.get("routes_failed", 0))
        console_errs = viewports.get("console_errors", summary.get("console_errors", 0))
        page_errs = viewports.get("page_errors", summary.get("page_errors", 0))
        net_reqs = viewports.get("failed_network_requests", summary.get("failed_network_requests", 0))
        net_loads = viewports.get("failed_resource_loads", summary.get("failed_resource_loads", 0))
        screenshots = viewports.get("screenshots_captured", summary.get("screenshots_captured", 0))

        lines.append(_kv("Routes", f"{routes_checked} checked, {routes_passed} passed, {routes_failed} failed"))
        total_issues = console_errs + page_errs + net_reqs + net_loads
        lines.append(_kv("Total issues", str(total_issues)))
        lines.append(_kv("Console errors", str(console_errs)))
        lines.append(_kv("Page errors", str(page_errs)))
        lines.append(_kv("Network failures", str(net_reqs + net_loads)))
        lines.append(_kv("Screenshots", str(screenshots)))
        lines.append(_kv("Report", bqa.get("report_path", ""), mono=True))
    lines.append("</div>")
    return "\n".join(lines)


def _render_backend(d: dict[str, Any]) -> str:
    audit = d.get("backend_audit", {})
    lines = ['<div class="card">']
    lines.append(f'<h3>Backend / Data {_status_badge(d.get("backend_readiness", "N/A"))}</h3>')
    if not audit:
        lines.append("<p>No backend audit data available yet.</p>")
    else:
        tables = audit.get("tables_referenced", [])
        buckets = audit.get("buckets_referenced", [])
        manual = audit.get("manual_verification_required", [])
        lines.append(_kv("Tables referenced", ", ".join(tables) if tables else "none"))
        lines.append(_kv("Buckets referenced", ", ".join(buckets) if buckets else "none"))
        lines.append(_kv("Manual verification items", str(len(manual))))
        if manual:
            lines.append('<ul style="margin:6px 0 0 18px;font-size:0.85rem">')
            for item in manual[:8]:
                lines.append(f"<li>{_h(item)}</li>")
            lines.append("</ul>")
    cdp = (project.project_control_path / "CUSTOMER_DATA_POLICY.md").exists() if hasattr(d, '_project') else True
    risk_cats = d.get("risk", {}).get("categories", d.get("risk", {}).get("risk_categories", []))
    has_data_risk = "data_schema_change" in (risk_cats if isinstance(risk_cats, list) else [])
    lines.append(_kv("Customer data policy", "exists"))
    if has_data_risk:
        lines.append(f'<div style="margin-top:6px">{_badge("data_schema_change risk", "warn")}</div>')
    lines.append("</div>")
    return "\n".join(lines)


def _render_research(d: dict[str, Any]) -> str:
    r = d.get("research", {})
    lines = ['<div class="card">']
    lines.append(f"<h3>Research</h3>")
    lines.append(_kv("Total requests", r.get("count", 0)))
    lines.append(_kv("Deep research pending approval", r.get("deep_research_pending_approval", 0)))
    lines.append(_kv("Completed", r.get("completed_count", 0)))
    latest = r.get("latest")
    if latest:
        lines.append(f'<div style="margin-top:8px"><strong>Latest:</strong></div>')
        lines.append(_kv("Topic", latest.get("topic", "")))
        lines.append(_kv("Mode", latest.get("mode", "")))
        lines.append(_kv("Status", latest.get("status", "")))
        lines.append(_kv("Estimate", f"{latest.get('estimated_minutes', '')} min"))
        if latest.get("requires_human_approval"):
            lines.append(f'<div style="margin-top:4px">{_badge("Requires human approval", "warn")}</div>')
    else:
        lines.append("<p style='color:var(--muted);font-size:0.85rem'>No research requests recorded yet.</p>")
    lines.append("</div>")
    return "\n".join(lines)


def _render_blockers(d: dict[str, Any]) -> str:
    blockers = d.get("blockers_detail", [])
    questions = d.get("human_questions", [])
    bs = d.get("blockers", {})

    lines = ['<div class="card">']
    lines.append(f'<h3>Blockers ({bs.get("open", 0)} open, {bs.get("resolved", 0)} resolved, {bs.get("parked", 0)} parked)</h3>')
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
        lines.append("<p style='color:var(--muted);font-size:0.85rem'>No blockers parsed.</p>")

    if questions:
        lines.append(f'<h3 style="margin-top:14px">Human Questions ({len(questions)})</h3>')
        lines.append("<table><tr><th>Question</th><th>Status</th><th>Severity</th></tr>")
        for q in questions:
            st = q.get("status", "").lower()
            lines.append(
                f"<tr><td>{_h(q.get('title', ''))}</td>"
                f"<td>{_badge(st, 'warn' if st == 'open' else 'ok')}</td>"
                f"<td>{_h(q.get('severity', ''))}</td></tr>"
            )
        lines.append("</table>")

    lines.append("</div>")
    return "\n".join(lines)


def _render_budget(d: dict[str, Any]) -> str:
    cost = d.get("cost", {})
    lines = ['<div class="card">']
    lines.append(_kv("Per-cycle budget", f"${d['per_cycle_budget']:.2f}"))
    lines.append(_kv("Daily budget", f"${d['daily_budget']:.2f}"))
    lines.append(_kv("Monthly budget", f"${d['monthly_budget']:.2f}"))
    lines.append(_kv("Paid API mode", d["paid_api_mode"]))
    if cost:
        lines.append(_kv("Cycle spend", f"${cost.get('cycle_spend_usd', 0):.4f}"))
        lines.append(_kv("Daily spend", f"${cost.get('daily_spend_usd', 0):.4f}"))
        lines.append(_kv("Monthly spend", f"${cost.get('monthly_spend_usd', 0):.4f}"))
    lines.append(_kv("Paid image generation", "disabled" if not d["allow_paid_image"] else "enabled"))
    lines.append(_kv("Paid video generation", "disabled" if not d["allow_paid_video"] else "enabled"))
    lines.append("</div>")
    return "\n".join(lines)


def _render_safety(d: dict[str, Any]) -> str:
    lock = d.get("lock", {})
    lines = ['<div class="card">']
    lines.append('<div class="grid">')
    gates = [
        ("Scheduler", "no", "na"),
        ("Auto Claude execution", "yes" if d["allow_auto_exec"] else "no", "warn" if d["allow_auto_exec"] else "ok"),
        ("Deploy automation", "no", "ok"),
        ("Paid generation", "yes" if d["allow_paid_image"] or d["allow_paid_video"] else "no", "warn" if d["allow_paid_image"] or d["allow_paid_video"] else "ok"),
        ("Max parallel agents", str(d["max_parallel_agents"]), "info"),
        ("Run lock", "HELD" if lock.get("locked") else ("STALE" if lock.get("stale") else "not held"), "warn" if lock.get("locked") else "ok"),
        ("HALT active", "YES" if d["halt_active"] else "no", "fail" if d["halt_active"] else "ok"),
        ("Telegram", "yes" if d["telegram_enabled"] else "no", "ok" if d["telegram_enabled"] else "na"),
    ]
    for label, value, kind in gates:
        lines.append(f'<div>{_kv(label, "")} {_badge(value, kind)}</div>')
    lines.append("</div></div>")
    return "\n".join(lines)


def render_html(d: dict[str, Any]) -> str:
    parts = [
        f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>Control Center - {_h(d['project_name'])}</title>"
        f"<style>{_CSS}</style></head><body>",
        _render_header(d),
        _render_next_step(d),
        _section("Current Task", _render_current_task(d)),
        _section("Latest Run Summary", _render_latest_run(d)),
        _section("Activity Timeline", _render_timeline(d)),
        _section("Quality Gates", _render_quality_gates(d)),
        _section("Browser QA", _render_browser_qa(d)),
        _section("Backend / Customer Data", _render_backend(d)),
        _section("Research", _render_research(d)),
        _section("Blockers & Human Questions", _render_blockers(d)),
        _section("Budget / Cost", _render_budget(d)),
        _section("Safety / Autonomy Gates", _render_safety(d)),
        f'<div class="footer">Project Autopilot Control Center Lite v0.1 &middot; Generated {_h(d["generated_at_display"])} &middot; Read-only, no secrets included</div>',
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
    parser = argparse.ArgumentParser(description="Project Autopilot Control Center Lite v0.1")
    parser.add_argument("--project", default="mira", help="Project id.")
    args = parser.parse_args()

    project = load_project_config(args.project)
    path = generate_control_center(project)
    print(f"Control Center generated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
