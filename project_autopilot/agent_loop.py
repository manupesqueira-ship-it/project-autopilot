from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from env_loader import load_env

load_env()

from config import ProjectConfig, project_config_path
from config_validator import ConfigIssue, validate_project_config, worst_severity
from blocker_summary import summarize_blockers
from cost_controller import CostController
from evidence_collector import collect_evidence
from evidence_bundle import create_evidence_bundle
from local_planner import _pick_next_task, generate_local_plan
from openai_supervisor import BudgetBlocked, MissingOpenAICredentials, OpenAIRequestError, OpenAISupervisor
from project_loader import ensure_project_dirs, load_project, read_project_control
from prompt_builder import build_builder_prompt
from qa_reviewer import classify_risk, classify_verdict, generate_correction_prompt, review_with_openai
from state_manager import load_state, record_blocker, save_state, write_failure_log, write_iteration_log
from task_state import load_task_state, transition_task_state
from browser_qa import diagnose_browser_qa, report_to_evidence, run_browser_qa, write_browser_qa_diagnostics_report, write_browser_qa_report
from builder_intake import intake_builder_report, verdict_as_dict, verdict_to_state
from post_builder_policy import check_current, write_policy_report
from claude_runner import detect_claude_cli, handoff_execute, handoff_manual, resolve_prompt_path
from telegram_alerts import send_alert
from risk_classifier import classify_task, format_risk_assessment
from research_log import count_research_index, record_research_request, summarize_research
from run_history import append_event, count_research_requests, new_run_id, recent_events, record_run_finished, record_run_started, summarize_recent_runs
from run_metrics import latest_run_metrics
from run_lock import LockActiveError, acquire_lock, lock_status, release_lock
from validation_report import create_validation_report
from backend_audit import run_backend_audit
from control_center import generate_control_center
from autopilot_health import build_health, claude_sdk_dry_run_health, policy_fixture_health, write_reports as write_autopilot_health_reports
from claude_analysis_call import run_analysis as run_claude_analysis_call
from claude_analysis_review import review_latest as review_latest_claude_analysis, write_review as write_claude_analysis_review
from claude_sdk_dry_run import run as run_claude_sdk_dry_run_report
from claude_prompt_pack import build_prompt_pack, write_prompt_pack
from claude_sandbox_boundary import evaluate_preflight as evaluate_claude_sandbox_preflight, simulate_sandbox as simulate_claude_sandbox, write_preflight as write_claude_sandbox_preflight, write_simulation as write_claude_sandbox_simulation
from openai_auditor import build_dry_run as build_openai_auditor_dry_run, write_dry_run as write_openai_auditor_dry_run, _status_payload as openai_auditor_status_payload, write_status as write_openai_auditor_status
from multistep_loop import build_loop as build_multistep_loop, write_loop as write_multistep_loop
from policy_test_fixtures import run as run_policy_fixture_suite
from worktree_sandbox import build_worktree_sandbox_plan, write_worktree_sandbox_plan


# ---------------------------------------------------------------------------
# HALT_AUTOPILOT support
# ---------------------------------------------------------------------------

HALT_FILE = "HALT_AUTOPILOT.md"


def _halt_path(project: ProjectConfig) -> Path:
    return project.project_control_path / HALT_FILE


def _halt_active(project: ProjectConfig) -> bool:
    return _halt_path(project).exists()


def _halt_reason(project: ProjectConfig) -> str:
    path = _halt_path(project)
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return "(could not read HALT file)"


# ---------------------------------------------------------------------------
# Core modes
# ---------------------------------------------------------------------------


def _risk_summary_dict(risk: Any) -> dict[str, Any]:
    return {
        "risk_level": risk.risk_level,
        "categories": risk.categories,
        "recommended_action": risk.recommended_action,
        "reasons": risk.reasons,
    }


def _cost_finish_details(project: ProjectConfig, cost: CostController, evidence: dict[str, Any], **extra: Any) -> dict[str, Any]:
    snapshot = cost.snapshot()
    details: dict[str, Any] = {
        "file_change_metrics": evidence.get("file_change_metrics", {}),
        "estimated_model_cost": snapshot.get("estimated_model_usage_usd"),
        "paid_api_calls": snapshot.get("paid_api_calls"),
    }
    details.update(extra)
    return details


def _count_open_blockers(project: ProjectConfig) -> int:
    return summarize_blockers(project).open_count


def _e2e_plan_path(project: ProjectConfig) -> Path:
    project_specific = project.project_control_path / f"{project.project_id.upper()}_E2E_VALIDATION_PLAN.md"
    if project_specific.exists():
        return project_specific
    return project.project_control_path / "E2E_VALIDATION_PLAN.md"


def run_cycle(project_id: str, dry_run: bool = False, cycle: bool = False) -> int:
    """Original planning cycle: evidence -> OpenAI -> builder prompt."""
    project = load_project(project_id)

    # HALT check — cycle refuses to run
    if _halt_active(project):
        reason = _halt_reason(project)
        print(f"HALT_AUTOPILOT is active. Cycle refused to run.")
        print(f"  File: {_halt_path(project)}")
        if reason:
            print(f"  Reason: {reason[:200]}")
        send_alert(project.project_id, "HALT_AUTOPILOT", "Cycle blocked by HALT_AUTOPILOT.", enabled=project.telegram_enabled)
        return 2

    # Run lock — only for --cycle (not --dry-run)
    locked = cycle and not dry_run
    if locked:
        try:
            acquire_lock(project_id)
        except LockActiveError as exc:
            print(str(exc))
            return 2

    try:
        return _run_cycle_inner(project, project_id, dry_run, cycle)
    finally:
        if locked:
            release_lock(project_id)


def _run_cycle_inner(project: ProjectConfig, project_id: str, dry_run: bool, cycle: bool) -> int:
    """Inner cycle logic after lock and HALT checks."""
    ensure_project_dirs(project)
    mode = "dry_run" if dry_run else "cycle"
    run_id = new_run_id(project.project_id, mode)
    record_run_started(project, run_id, mode)

    cost_controller = CostController(project)
    control_docs = read_project_control(project)
    evidence = collect_evidence(project, dry_run=dry_run, run_id=run_id)
    supervisor = OpenAISupervisor(project, cost_controller, dry_run=dry_run)

    try:
        task_plan = supervisor.plan_next_task(control_docs, evidence)
        qa_review = review_with_openai(supervisor, task_plan, evidence)
        correction_prompt = generate_correction_prompt(supervisor, task_plan, qa_review, evidence)
    except (MissingOpenAICredentials, BudgetBlocked, OpenAIRequestError) as exc:
        return _handle_openai_failure(project, cost_controller, control_docs, evidence, exc, run_id)

    builder_prompt = build_builder_prompt(project, control_docs, task_plan, evidence)
    if dry_run:
        qa_verdict = "DRY_RUN_SKIPPED"
        qa_risk = "not_applicable"
    else:
        qa_verdict = classify_verdict(qa_review)
        qa_risk = classify_risk(qa_review)
        append_event(project, run_id, "qa_verdict_created", {"verdict": qa_verdict, "risk_level": qa_risk})
    bundle_path = create_evidence_bundle(
        project=project,
        evidence=evidence,
        task_plan=task_plan,
        builder_prompt=builder_prompt,
        qa_review=qa_review,
        risk_summary={"risk_level": qa_risk, "verdict": qa_verdict},
        cost_snapshot=cost_controller.snapshot(),
        task_state=load_task_state(project),
    )
    append_event(
        project,
        run_id,
        "builder_prompt_created",
        {"path": str((project.repo_path / project.logs_dir / f"{project.project_id}_latest_builder_prompt.md").relative_to(project.repo_path))},
    )
    log_path = write_iteration_log(
        project=project,
        task_plan=task_plan,
        builder_prompt=builder_prompt,
        qa_review=qa_review,
        correction_prompt=correction_prompt,
        evidence=evidence,
        dry_run=dry_run,
        cycle=cycle,
    )

    state = load_state(project)
    state["cycles"] = int(state.get("cycles", 0)) + 1
    state["last_status"] = "planned_dry_run" if dry_run else "planned"
    state["last_log"] = str(log_path.relative_to(project.repo_path))
    state["last_evidence_bundle"] = str(bundle_path.relative_to(project.repo_path))
    prompt_rel = str((project.repo_path / project.logs_dir / f"{project.project_id}_latest_builder_prompt.md").relative_to(project.repo_path))
    state["last_builder_prompt"] = prompt_rel
    save_state(project, state)
    transition_task_state(project, "planned", "Project Autopilot generated a builder prompt.", run_id=run_id)
    if not dry_run and qa_verdict == "RESEARCH_REQUIRED":
        record_research_request(
            project,
            run_id,
            topic="OpenAI QA requested research",
            reason="Supervisor QA verdict was RESEARCH_REQUIRED.",
            mode="quick_check",
        )
    record_run_finished(
        project,
        run_id,
        "planned_dry_run" if dry_run else "planned",
        _cost_finish_details(project, cost_controller, evidence, outcome="dry_run" if dry_run else qa_verdict),
    )

    print(f"Project: {project.project_name} ({project.project_id})")
    print(f"Run id: {run_id}")
    print(f"Generated builder prompt: {project.repo_path / project.logs_dir / f'{project.project_id}_latest_builder_prompt.md'}")
    print(f"Wrote iteration log: {log_path}")
    print(f"Evidence bundle: {bundle_path}")
    print("No builder work was executed.")
    return 0


def _handle_openai_failure(
    project: ProjectConfig,
    cost_controller: CostController,
    control_docs: dict[str, str],
    evidence: dict[str, Any],
    exc: Exception,
    run_id: str,
) -> int:
    """Handle any OpenAI failure: log it, alert, generate local fallback, exit cleanly."""
    if isinstance(exc, OpenAIRequestError):
        error_type = exc.error_type
        status_code = exc.status_code
        message = exc.message
        error_dict = exc.as_dict()
    elif isinstance(exc, BudgetBlocked):
        error_type = "BudgetBlocked"
        status_code = None
        message = str(exc)
        error_dict = {"error_type": error_type, "message": message}
    else:
        error_type = type(exc).__name__
        status_code = None
        message = str(exc)
        error_dict = {"error_type": error_type, "message": message}

    append_event(project, run_id, "error", error_dict)

    # 1. Write failure log
    recommendation = (
        "OpenAI supervisor unavailable. A local fallback plan has been generated. "
        "Resolve the underlying issue (billing, quota, credentials) when convenient."
    )
    log_path = write_failure_log(
        project=project,
        title=error_type,
        error=error_dict,
        evidence=evidence,
        recommendation=recommendation,
    )

    # 2. Record blocker
    body = (
        f"Status: open\nSeverity: blocking\nSource: Project Autopilot\n\n"
        f"Question or blocker:\n{error_type}"
        + (f" ({status_code})" if status_code else "")
        + f"\n{message}\n\n"
        f"Failure log:\n{log_path.relative_to(project.repo_path)}\n\n"
        f"Recommended action:\n{recommendation}"
    )
    record_blocker(project, f"Autopilot blocked: {error_type}", body)
    append_event(
        project,
        run_id,
        "blocker_recorded",
        {"title": f"Autopilot blocked: {error_type}", "status_code": status_code},
    )

    # 3. Send Telegram alert
    alert = send_alert(project.project_id, error_type, message, enabled=project.telegram_enabled)

    # 4. Generate local fallback plan
    fallback = generate_local_plan(project, control_docs, evidence)
    fallback_path = project.repo_path / project.logs_dir / f"{project.project_id}_latest_builder_prompt.md"
    fallback_path.parent.mkdir(parents=True, exist_ok=True)
    fallback_path.write_text(fallback, encoding="utf-8")
    append_event(
        project,
        run_id,
        "builder_prompt_created",
        {"path": str(fallback_path.relative_to(project.repo_path)), "fallback": True},
    )
    bundle_path = create_evidence_bundle(
        project=project,
        evidence=evidence,
        task_plan="LOCAL FALLBACK PLAN",
        builder_prompt=fallback,
        qa_review="Local fallback plan generated without OpenAI QA.",
        cost_snapshot=cost_controller.snapshot(),
        task_state=load_task_state(project),
    )

    # 5. Update state
    state = load_state(project)
    state["last_status"] = "blocked_with_fallback"
    state["last_error"] = error_dict
    state["last_log"] = str(log_path.relative_to(project.repo_path))
    state["last_builder_prompt"] = str(fallback_path.relative_to(project.repo_path))
    state["last_evidence_bundle"] = str(bundle_path.relative_to(project.repo_path))
    save_state(project, state)
    transition_task_state(project, "blocked", f"Project Autopilot blocked on {error_type}.", run_id=run_id)
    record_run_finished(
        project,
        run_id,
        "blocked_with_fallback",
        _cost_finish_details(project, cost_controller, evidence, outcome=error_type),
    )

    # 6. Print summary
    print(f"Blocked: {error_type}" + (f" ({status_code})" if status_code else ""))
    print(message)
    print(f"Failure log: {log_path}")
    print(f"Telegram: {alert.reason}")
    print(f"Local fallback plan written to: {fallback_path}")
    print(f"Evidence bundle: {bundle_path}")
    print("You can paste the fallback plan into Claude Code as the builder prompt.")
    return 2


def run_local_plan(project_id: str) -> int:
    """Force local fallback planner — no OpenAI call."""
    project = load_project(project_id)
    if _halt_active(project):
        print(f"WARNING: HALT_AUTOPILOT is active. Proceeding with local plan (read-only).")
        print(f"  File: {_halt_path(project)}")
    ensure_project_dirs(project)
    run_id = new_run_id(project.project_id, "local_plan")
    record_run_started(project, run_id, "local_plan")

    control_docs = read_project_control(project)
    evidence = collect_evidence(project, dry_run=False, run_id=run_id)

    fallback = generate_local_plan(project, control_docs, evidence)
    prompt_path = project.repo_path / project.logs_dir / f"{project.project_id}_latest_builder_prompt.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(fallback, encoding="utf-8")
    append_event(project, run_id, "builder_prompt_created", {"path": str(prompt_path.relative_to(project.repo_path))})

    title, body = _pick_next_task(control_docs.get("TASK_QUEUE.md", ""))
    risk = classify_task(title or "Current task queue", body or "", evidence.get("changed_files", []), control_docs)
    bundle_path = create_evidence_bundle(
        project=project,
        evidence=evidence,
        task_plan="LOCAL PLAN",
        builder_prompt=fallback,
        qa_review="Local plan mode does not call OpenAI QA.",
        risk_summary=_risk_summary_dict(risk),
        cost_snapshot=CostController(project).snapshot(),
        task_state=load_task_state(project),
    )

    state = load_state(project)
    state["cycles"] = int(state.get("cycles", 0)) + 1
    state["last_status"] = "local_plan"
    state["last_builder_prompt"] = str(prompt_path.relative_to(project.repo_path))
    state["last_evidence_bundle"] = str(bundle_path.relative_to(project.repo_path))
    save_state(project, state)
    transition_task_state(project, "planned", "Local planner generated a builder prompt.", run_id=run_id)
    if "research_required" in risk.categories:
        record_research_request(
            project,
            run_id,
            topic=title or "Current task queue",
            reason="Risk classifier marked the task as research_required.",
            mode="quick_check",
        )
    record_run_finished(
        project,
        run_id,
        "local_plan",
        _cost_finish_details(project, CostController(project), evidence, outcome=risk.recommended_action),
    )

    print(f"Project: {project.project_name} ({project.project_id})")
    print(f"Run id: {run_id}")
    print(f"Local fallback plan written to: {prompt_path}")
    print(f"Evidence bundle: {bundle_path}")
    print("Paste this into Claude Code or your preferred builder agent.")
    return 0


def run_status(project_id: str) -> int:
    """Print project status summary."""
    project = load_project(project_id)
    state = load_state(project)
    cost = CostController(project)
    task_state = load_task_state(project)
    recent_runs = summarize_recent_runs(project.project_id, limit=5)
    latest_run = recent_runs[0] if recent_runs else None

    print(f"Project:            {project.project_name} ({project.project_id})")
    print(f"Autonomy mode:      {project.autonomy_mode}")
    print(f"Intensity mode:     {project.intensity_mode}")
    print(f"Builder primary:    {project.builder_primary}")
    print(f"Builder fallback:   {project.builder_fallback}")
    if _halt_active(project):
        print()
        print(f"*** HALT_AUTOPILOT ACTIVE ***")
        reason = _halt_reason(project)
        if reason:
            print(f"  Reason: {reason[:200]}")

    # Run lock
    ls = lock_status(project.project_id)
    if ls["locked"]:
        print()
        print(f"*** RUN LOCK ACTIVE ***")
        print(f"  PID: {ls['pid']}")
        print(f"  Started: {ls['started_at']}")
        print(f"  Lock file: {ls['lock_path']}")
    elif ls["stale"]:
        print()
        print(f"Run lock: STALE (PID {ls['pid']}, started {ls['started_at']})")
    else:
        print(f"Run lock:           not held")
    print()

    # Budget
    snap = cost.snapshot()
    print("Budget:")
    print(f"  Per-cycle:        ${snap['per_cycle_budget_usd']:.2f}")
    print(f"  Daily:            ${snap['daily_budget_usd']:.2f}")
    print(f"  Monthly:          ${snap['monthly_budget_usd']:.2f}")
    print(f"  Paid API mode:    {snap['paid_api_mode']}")
    print(f"  Est. model usage: ${snap['estimated_model_usage_usd']:.4f}")
    print(f"  Paid API calls:   {snap['paid_api_calls']}")
    print()

    # State
    print("Activity:")
    print(f"Cycles run:         {state.get('cycles', 0)}")
    print(f"Last status:        {state.get('last_status', 'unknown')}")
    print(f"Task state:         {task_state.get('state', 'unknown')}")
    print(f"Total runs logged:  {len(summarize_recent_runs(project.project_id, limit=1000000))}")
    if latest_run:
        print(f"Last run id:        {latest_run.get('run_id')}")
        print(f"Last run duration:  {latest_run.get('duration_seconds')}s")
        print(f"Last run outcome:   {latest_run.get('outcome') or latest_run.get('status')}")
        print(f"Latest commands:    {latest_run.get('commands_count', 0)} ({latest_run.get('failed_commands_count', 0)} failed)")
        print(
            "Latest file delta:  "
            f"+{latest_run.get('files_created', 0)} created, "
            f"{latest_run.get('files_modified', 0)} modified, "
            f"{latest_run.get('files_deleted', 0)} deleted, "
            f"+{latest_run.get('lines_added', 0)}/-{latest_run.get('lines_removed', 0)} lines"
        )
        if latest_run.get("evidence_bundle_path"):
            print(f"Latest evidence:    {latest_run['evidence_bundle_path']}")
        if latest_run.get("qa_verdict"):
            print(f"Latest QA verdict:  {latest_run['qa_verdict']} ({latest_run.get('risk_level') or 'risk unknown'})")
    blocker_summary = summarize_blockers(project)
    print(f"Open blockers:      {blocker_summary.open_count}")
    print(f"Resolved blockers:  {blocker_summary.resolved_count}")
    if blocker_summary.latest_open_title:
        print(f"Latest open blocker:{blocker_summary.latest_open_title}")
    print(f"Blocker file:       {blocker_summary.path.relative_to(project.repo_path)}")
    print(f"Research requests:  {count_research_index(project)} indexed / {count_research_requests(project)} run events")
    last_log = state.get("last_log")
    if last_log:
        print(f"Last log:           {last_log}")
    last_prompt = state.get("last_builder_prompt")
    if last_prompt:
        print(f"Last builder prompt:{last_prompt}")
    last_bundle = state.get("last_evidence_bundle")
    if last_bundle:
        print(f"Evidence bundle:    {last_bundle}")
    last_correction = state.get("last_correction_prompt")
    if last_correction:
        print(f"Correction prompt:  {last_correction}")
    last_browser_qa = state.get("last_browser_qa")
    if last_browser_qa:
        print(f"Browser QA report:  {last_browser_qa}")
        print(f"Browser QA passed:  {state.get('browser_qa_passed')}")
    last_backend_audit = state.get("last_backend_audit")
    if last_backend_audit:
        print(f"Backend audit:      {last_backend_audit}")
        print(f"Backend readiness:  {state.get('backend_readiness', 'unknown')}")
    print()

    # Git status (quick)
    try:
        result = subprocess.run(
            ["git", "status", "--short", "--branch"],
            cwd=project.repo_path,
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10,
        )
        git_out = result.stdout.strip()
        lines = git_out.splitlines()
        print(f"Git branch:         {lines[0] if lines else '?'}")
        dirty_count = len(lines) - 1 if len(lines) > 1 else 0
        print(f"Git dirty files:    {dirty_count}")
    except Exception:
        print("Git status:         unavailable")

    if recent_runs:
        print()
        print("Recent runs:")
        for run in recent_runs:
            duration = run.get("duration_seconds")
            duration_text = f"{duration}s" if duration is not None else "unfinished"
            print(
                f"  {run['run_id']} | {run.get('status') or 'unknown'} | "
                f"{duration_text} | commands {run.get('commands_count', 0)} "
                f"({run.get('failed_commands_count', 0)} failed)"
            )

    control_docs = read_project_control(project)
    task_queue = control_docs.get("TASK_QUEUE.md", "")
    title, body = _pick_next_task(task_queue)
    risk = classify_task(title or "Current task queue", body or task_queue, [], control_docs)
    print()
    print("Risk summary:")
    print(format_risk_assessment(risk))

    return 0


def run_history_cmd(project_id: str) -> int:
    """Print recent run history in a compact, morning-readable form."""
    project = load_project(project_id)
    events = recent_events(project, limit=10)
    runs = summarize_recent_runs(project.project_id, limit=1)
    latest = runs[0] if runs else None
    blocker_summary = summarize_blockers(project)

    print(f"Run history: {project.project_name} ({project.project_id})")
    if not events:
        print("No run history recorded yet.")
        return 0

    if latest:
        print(f"Last run id:        {latest.get('run_id')}")
        print(f"Last run duration:  {latest.get('duration_seconds')}s")
        print(f"Commands executed:  {latest.get('commands_count', 0)} ({latest.get('failed_commands_count', 0)} failed)")
        print(f"Latest QA verdict:  {latest.get('qa_verdict') or 'none'}")
    print(f"Latest blocker:     {blocker_summary.latest_open_title or 'none'}")
    print()
    print("Last 10 events:")
    for event in events:
        meta = event.get("metadata", {})
        detail = event.get("status") or meta.get("label") or meta.get("verdict") or event.get("file_path") or ""
        print(f"- {event.get('timestamp_utc')} | {event.get('run_id')} | {event.get('event_type')} | {detail}")
    return 0


def run_metrics_cmd(project_id: str) -> int:
    """Print latest run activity metrics."""
    project = load_project(project_id)
    metrics = latest_run_metrics(project)
    if not metrics:
        print(f"Metrics: {project.project_name} ({project.project_id})")
        print("No run metrics recorded yet.")
        return 0

    print(f"Metrics: {project.project_name} ({project.project_id})")
    print(f"Run id:             {metrics['run_id']}")
    print(f"Outcome:            {metrics.get('outcome') or 'unknown'}")
    print(f"Active duration:    {metrics['active_duration_seconds']}s")
    print(f"Total duration:     {metrics['total_duration_seconds']}s")
    print(f"Commands executed:  {metrics['commands_executed']} ({metrics['commands_failed']} failed)")
    print(
        "Files changed:      "
        f"+{metrics['files_created']} created, "
        f"{metrics['files_modified']} modified, "
        f"{metrics['files_deleted']} deleted"
    )
    print(f"Line delta:         +{metrics['lines_added']}/-{metrics['lines_removed']}")
    print(f"Risk level:         {metrics.get('risk_level') or 'unknown'}")
    print(f"QA verdict:         {metrics.get('qa_verdict') or 'none'}")
    print(f"Evidence bundle:    {metrics.get('evidence_bundle_path') or 'none'}")
    print(f"Task state:         {metrics.get('task_state')}")
    print(f"Open blockers:      {metrics.get('open_blockers')}")
    print(f"Research requests:  {metrics.get('research_requests')}")
    print(f"Cost estimate:      {metrics.get('cost_estimate_usd') if metrics.get('cost_estimate_usd') is not None else 'n/a'}")
    return 0


def run_research_status(project_id: str) -> int:
    """Print research index summary."""
    project = load_project(project_id)
    summary = summarize_research(project)
    print(f"Research status: {project.project_name} ({project.project_id})")
    if summary["count"] == 0:
        print("No research requests recorded yet.")
        return 0
    print(f"Requested research count:      {summary['count']}")
    print(f"Deep research pending approval:{summary['deep_research_pending_approval']}")
    print(f"Completed research count:      {summary['completed_count']}")
    latest = summary.get("latest")
    if latest:
        print("Latest research request:")
        print(f"  id:        {latest.get('research_id')}")
        print(f"  topic:     {latest.get('topic')}")
        print(f"  mode:      {latest.get('mode')}")
        print(f"  status:    {latest.get('status')}")
        print(f"  estimate:  {latest.get('estimated_minutes')} min")
        print(f"  approval:  {'required' if latest.get('requires_human_approval') else 'not required'}")
    return 0


def run_request_research(project_id: str, topic: str, mode: str) -> int:
    """Record a research request. Does not perform research."""
    project = load_project(project_id)
    run_id = new_run_id(project.project_id, "research_request")
    record_run_started(project, run_id, "research_request", task_title=topic)
    record = record_research_request(
        project,
        run_id,
        topic=topic,
        reason="Manual CLI research request.",
        mode=mode,
        requested_by="CLI",
        linked_task=topic,
    )
    if mode == "deep_research":
        send_alert(
            project.project_id,
            "Deep research approval required",
            topic,
            enabled=project.telegram_enabled,
        )
    record_run_finished(
        project,
        run_id,
        "research_requested",
        {"outcome": "research_requested", "research_id": record["research_id"]},
    )
    print("Research request recorded.")
    print(f"Research id: {record['research_id']}")
    print(f"Topic: {record['topic']}")
    print(f"Mode: {record['mode']}")
    print(f"Estimated minutes: {record['estimated_minutes']}")
    print(f"Human approval required: {'yes' if record['requires_human_approval'] else 'no'}")
    if mode == "deep_research":
        print("Deep research requires explicit human approval before any research is performed.")
    print("No research was run automatically.")
    return 0


def run_handoff_claude(project_id: str) -> int:
    """Generate or reuse latest builder prompt, then hand off to Claude (manual mode)."""
    project = load_project(project_id)
    ensure_project_dirs(project)

    prompt_path = resolve_prompt_path(project)
    if not prompt_path.exists():
        # Generate a fresh local plan first
        print("No existing builder prompt found. Generating local plan...")
        run_local_plan(project_id)

    result = handoff_manual(project)
    print(result.message)
    return 0


def run_claude_manual(project_id: str) -> int:
    """Print the prompt path for manual paste into Claude Code."""
    project = load_project(project_id)
    result = handoff_manual(project)
    print(result.message)
    return 0


def run_claude_execute(project_id: str) -> int:
    """Attempt automatic Claude execution (blocked by default)."""
    project = load_project(project_id)
    result = handoff_execute(project)
    print(result.message)
    return 0 if result.executed else 1


def run_browser_qa_cmd(project_id: str) -> int:
    """Run browser QA against configured route_walk_urls."""
    project = load_project(project_id)
    ensure_project_dirs(project)
    run_id = new_run_id(project.project_id, "browser_qa")
    record_run_started(project, run_id, "browser_qa")
    append_event(
        project,
        run_id,
        "browser_qa_started",
        {"route_count": len(project.route_walk_urls), "screenshot_enabled": project.screenshot_enabled},
    )

    report = run_browser_qa(project, run_id=run_id)
    report_path = write_browser_qa_report(project, report)
    evidence = report_to_evidence(report)
    evidence["browser_qa_report"] = str(report_path.relative_to(project.repo_path))

    state = load_state(project)
    state["last_browser_qa"] = str(report_path.relative_to(project.repo_path))
    state["browser_qa_passed"] = report.passed
    state["browser_qa_verdict"] = report.verdict
    state["browser_qa_mode"] = report.mode
    state["browser_qa_summary"] = report.summary_counts
    state["browser_qa_total_issues"] = report.total_issues
    state["browser_qa_selected_runtime_url"] = report.diagnostics.selected_runtime_url
    save_state(project, state)

    event_details = {
        "mode": report.mode,
        "passed": report.passed,
        "verdict": report.verdict,
        "outcome": report.outcome,
        "total_issues": report.total_issues,
        "report": str(report_path.relative_to(project.repo_path)),
        "configured_url": report.diagnostics.configured_url,
        "selected_runtime_url": report.diagnostics.selected_runtime_url,
        "ports_tested": report.diagnostics.ports_tested,
        **report.summary_counts,
    }
    append_event(project, run_id, "browser_qa_finished", event_details)
    if report.verdict in ("FAIL", "SKIPPED_DEV_SERVER_DOWN"):
        append_event(project, run_id, "browser_qa_failed", event_details)
    record_run_finished(project, run_id, f"browser_qa_{report.verdict.lower()}", event_details)

    print(f"Browser QA verdict: {report.verdict}")
    print(f"Run id: {run_id}")
    print(f"Mode: {report.mode}")
    print(f"Viewports: {', '.join(report.viewport_coverage.keys()) or 'http_only'}")
    print(f"Configured URL: {report.diagnostics.configured_url or 'none'}")
    print(f"Selected runtime URL: {report.diagnostics.selected_runtime_url or 'none'}")
    print(f"Ports tested: {', '.join(str(port) for port in report.diagnostics.ports_tested) or 'none'}")
    counts = report.summary_counts
    print(f"Routes: {counts['routes_checked']} checked, {counts['routes_passed']} passed, {counts['routes_failed']} failed")
    print(f"Issues: {report.total_issues} total ({counts['console_errors']} console, {counts['page_errors']} page, {counts['failed_network_requests']} net requests, {counts['failed_resource_loads']} net loads)")
    print(report.summary)
    print(f"Report: {report_path}")

    if report.verdict == "SKIPPED_DEV_SERVER_DOWN":
        print(f"\nStart the dev server first: {project.dev_server_command or 'npm run dev'}")
    elif report.verdict == "WARN":
        print("\nHTTP-only fallback cannot validate client-side behavior. Install Playwright for full QA.")
    elif report.verdict == "FAIL":
        failed = [r for r in report.routes if not r.passed]
        for r in failed:
            print(
                f"  FAIL: {r.url} [{r.viewport}] "
                f"(HTTP {r.status}, {len(r.console_errors)} console, "
                f"{len(r.page_errors)} page, "
                f"{len(r.failed_network_requests) + len(r.failed_resource_loads)} net failures)"
            )

    return 0 if report.verdict in ("PASS", "WARN") else 1


def run_browser_qa_diagnose(project_id: str) -> int:
    """Diagnose Browser QA URL reachability. No Playwright, screenshots, or product data mutation."""
    project = load_project(project_id)
    ensure_project_dirs(project)
    diagnostics = diagnose_browser_qa(project)
    path = write_browser_qa_diagnostics_report(project, diagnostics)
    print(f"Browser QA diagnostics: {'PASS' if diagnostics.reachable else 'FAIL'}")
    print(f"Configured URL: {diagnostics.configured_url or 'none'}")
    print("Reachability:")
    for check in diagnostics.checks:
        status = check.status if check.status is not None else ""
        detail = f" {status}" if status != "" else f" {check.error}" if check.error else ""
        print(f"- {check.url} {'PASS' if check.passed else 'FAIL'}{detail}")
    print(f"Selected runtime URL: {diagnostics.selected_runtime_url or 'none'}")
    print(f"Diagnostics report: {path}")
    return 0 if diagnostics.reachable else 1


def run_e2e_plan(project_id: str) -> int:
    """Print the project-specific manual E2E validation plan. No automation or data access."""
    project = load_project(project_id)
    path = _e2e_plan_path(project)
    print(f"Project: {project.project_name} ({project.project_id})")
    print(f"E2E validation plan: {path}")
    print()

    if not path.exists():
        print("No E2E validation plan found.")
        print(f"Expected: {path.relative_to(project.repo_path)}")
        return 1

    print("Preconditions:")
    print("- Local app can be started with the intended environment.")
    print("- Supabase project access is available for table and storage inspection.")
    print("- Use only fake QA data; do not use real customer photos or personal data.")
    print("- Do not commit logs, screenshots, exported data, or env files.")
    print()
    print("Exact next manual steps:")
    print("1. Run `npm run dev`.")
    print("2. Open `http://localhost:3000/es/onboarding`.")
    print("3. Submit onboarding with `qa-test+manual-001@example.com` and fake profile data.")
    print("4. Verify `users_profile` in Supabase.")
    print("5. Upload a safe test image at `/es/scan`.")
    print("6. Verify `user-photos` storage and `user_assets`.")
    print("7. Select a product from `/es/catalog` and trigger try-on.")
    print("8. Verify `generations` and result polling at `/es/result/[generationId]`.")
    print("9. Capture screenshots/evidence and record failures in `project_control/BLOCKERS.md`.")
    print()
    print("This command does not run browser automation, call Supabase, or modify data.")
    return 0


def run_new_validation_report(project_id: str) -> int:
    """Create a blank product validation report draft under logs."""
    project = load_project(project_id)
    ensure_project_dirs(project)
    latest_path, run_path = create_validation_report(project)
    print(f"Validation report draft: {run_path}")
    print(f"Latest validation report: {latest_path}")
    print("No product data was modified.")
    return 0


def run_backend_audit_cmd(project_id: str) -> int:
    """Run static backend/data-flow audit. No Supabase or OpenAI calls."""
    project = load_project(project_id)
    ensure_project_dirs(project)
    run_id = new_run_id(project.project_id, "backend_audit")
    record_run_started(project, run_id, "backend_audit")
    append_event(project, run_id, "backend_audit_started", {})

    try:
        summary, report_path = run_backend_audit(project)
    except Exception as exc:
        append_event(project, run_id, "backend_audit_failed", {"error": str(exc)})
        record_run_finished(project, run_id, "backend_audit_failed", {"outcome": "error"})
        print(f"Backend audit failed: {exc}")
        return 1

    rel_report = str(report_path.relative_to(project.repo_path))
    state = load_state(project)
    state["last_backend_audit"] = rel_report
    state["backend_readiness"] = summary.readiness
    state["backend_manual_verification_required"] = summary.manual_verification_required
    save_state(project, state)

    append_event(
        project,
        run_id,
        "backend_audit_finished",
        {
            "report": rel_report,
            "readiness": summary.readiness,
            "tables_referenced": summary.tables_referenced,
            "buckets_referenced": summary.buckets_referenced,
            "manual_verification_required": len(summary.manual_verification_required),
        },
    )
    record_run_finished(
        project,
        run_id,
        f"backend_audit_{summary.readiness.lower()}",
        {
            "outcome": summary.readiness,
            "backend_audit_report": rel_report,
        },
    )

    print(f"Backend audit: {summary.readiness}")
    print(f"Run id: {run_id}")
    print(f"Report: {report_path}")
    print(f"Tables referenced: {', '.join(summary.tables_referenced) or 'none'}")
    print(f"Buckets referenced: {', '.join(summary.buckets_referenced) or 'none'}")
    if summary.manual_verification_required:
        print("Manual verification required:")
        for item in summary.manual_verification_required:
            print(f"- {item}")
    print("No Supabase calls were made. No product data was modified.")
    return 0


def run_control_center(project_id: str) -> int:
    """Generate Control Center HTML report. Read-only, no secrets, no state changes."""
    project = load_project(project_id)
    path = generate_control_center(project)
    print(f"Control Center: {path}")
    return 0


def run_builder_intake(project_id: str, report_path: str) -> int:
    """Ingest a builder report, collect fresh evidence, and produce a QA verdict."""
    project = load_project(project_id)
    ensure_project_dirs(project)
    run_id = new_run_id(project.project_id, "post_builder")
    record_run_started(project, run_id, "post_builder")

    transition_task_state(project, "validating", "Post-builder intake started.", run_id=run_id)
    result = intake_builder_report(project, report_path, run_validation=True, run_id=run_id)
    verdict = result["verdict"]
    policy_report = result.get("policy_report")
    append_event(
        project,
        run_id,
        "qa_verdict_created",
        {"verdict": verdict.verdict, "risk_level": verdict.risk_level, "recommended_next_action": verdict.recommended_next_action},
    )
    if policy_report:
        append_event(
            project,
            run_id,
            "post_builder_policy_created",
            {
                "verdict": policy_report.policy_verdict.verdict,
                "safe_commit_allowed": policy_report.policy_verdict.safe_commit_allowed,
                "failed_gates": policy_report.failed_gates,
            },
        )
        if policy_report.policy_verdict.verdict in {"SAFE_TO_COMMIT", "SAFE_NO_CHANGES"}:
            target_state = "passed"
        elif policy_report.policy_verdict.verdict == "NEEDS_FIX":
            target_state = "needs_fix"
        elif policy_report.policy_verdict.verdict in {"BLOCKED", "HUMAN_REVIEW_REQUIRED"}:
            target_state = "blocked"
        else:
            target_state = verdict_to_state(verdict)
        transition_task_state(project, target_state, f"Post-builder policy verdict: {policy_report.policy_verdict.verdict}.", run_id=run_id)
    else:
        target_state = verdict_to_state(verdict)
        transition_task_state(project, target_state, f"Post-builder verdict: {verdict.verdict}.", run_id=run_id)

    state = load_state(project)
    status_suffix = policy_report.policy_verdict.verdict.lower() if policy_report else verdict.verdict.lower()
    state["last_status"] = f"post_builder_{status_suffix}"
    state["last_qa_verdict"] = verdict_as_dict(verdict)
    state["last_log"] = str(result["intake_log_path"].relative_to(project.repo_path))
    state["last_evidence_bundle"] = str(result["bundle_path"].relative_to(project.repo_path))
    if result.get("policy_report_path"):
        state["last_post_builder_policy"] = str(result["policy_report_path"].relative_to(project.repo_path))
    correction_prompt_path = result.get("correction_prompt_path")
    if correction_prompt_path:
        state["last_correction_prompt"] = str(correction_prompt_path.relative_to(project.repo_path))
        append_event(
            project,
            run_id,
            "correction_prompt_created",
            {"path": str(correction_prompt_path.relative_to(project.repo_path))},
        )
    save_state(project, state)

    policy_blocked = policy_report and policy_report.policy_verdict.verdict in {"BLOCKED", "HUMAN_REVIEW_REQUIRED"}
    if verdict.verdict in {"BLOCKED", "HUMAN_DECISION_REQUIRED"} or policy_blocked:
        policy_text = ""
        if policy_report:
            policy_text = (
                f"\n\nUnified policy verdict:\n{policy_report.policy_verdict.verdict}\n\n"
                f"Failed gates:\n{', '.join(policy_report.failed_gates) or 'none'}\n\n"
                "Human decisions needed:\n"
                + "\n".join(f"- {item}" for item in policy_report.human_decisions_needed or ["None"])
            )
        body = (
            "Status: open\nSeverity: blocking\nSource: Project Autopilot post-builder QA\n\n"
            f"Question or blocker:\n{policy_report.policy_verdict.verdict if policy_report else verdict.verdict}\n\n"
            f"Post-builder log:\n{state['last_log']}\n\n"
            f"Recommended action:\n{policy_report.next_action if policy_report else verdict.recommended_next_action}"
            f"{policy_text}"
        )
        blocker_title = f"Post-builder QA: {policy_report.policy_verdict.verdict if policy_report else verdict.verdict}"
        record_blocker(project, blocker_title, body)
        append_event(
            project,
            run_id,
            "blocker_recorded",
            {"title": blocker_title, "log": state["last_log"]},
        )

    if verdict.verdict == "RESEARCH_REQUIRED" or (policy_report and policy_report.policy_verdict.verdict == "HUMAN_REVIEW_REQUIRED" and policy_report.characteristics.requires_research_review):
        record_research_request(
            project,
            run_id,
            topic="Post-builder QA research request",
            reason="Post-builder QA verdict was RESEARCH_REQUIRED.",
            mode="quick_check",
        )

    record_run_finished(
        project,
        run_id,
        f"post_builder_{status_suffix}",
        _cost_finish_details(
            project,
            CostController(project),
            result["evidence"],
            outcome=policy_report.policy_verdict.verdict if policy_report else verdict.verdict,
            qa_verdict=verdict.verdict,
            risk_level=verdict.risk_level,
        ),
    )

    print(f"Post-builder intake: {project.project_name} ({project.project_id})")
    print(f"Run id: {run_id}")
    print(f"Verdict: {verdict.verdict}")
    print(f"Risk level: {verdict.risk_level}")
    if policy_report:
        print(f"Unified policy verdict: {policy_report.policy_verdict.verdict}")
        print(f"Safe commit allowed: {policy_report.policy_verdict.safe_commit_allowed}")
        print(f"Failed gates: {', '.join(policy_report.failed_gates) if policy_report.failed_gates else 'none'}")
        print(f"Policy report: {result['policy_report_path']}")
    print(f"Post-builder log: {result['intake_log_path']}")
    print(f"Evidence bundle: {result['bundle_path']}")
    if correction_prompt_path:
        print(f"Correction prompt: {correction_prompt_path}")
    print(f"Recommended next action: {policy_report.next_action if policy_report else verdict.recommended_next_action}")

    if policy_report:
        return 0 if policy_report.policy_verdict.verdict in {"SAFE_TO_COMMIT", "SAFE_NO_CHANGES"} else 1
    return 0 if verdict.verdict == "PASS" else 1


def run_policy_check(project_id: str) -> int:
    project = load_project(project_id)
    ensure_project_dirs(project)
    report = check_current(project)
    md_path, json_path = write_policy_report(project, report)
    state = load_state(project)
    state["last_post_builder_policy"] = str(md_path.relative_to(project.repo_path))
    state["last_status"] = f"policy_check_{report.policy_verdict.verdict.lower()}"
    save_state(project, state)
    print(f"Policy check: {project.project_name} ({project.project_id})")
    print(f"Verdict: {report.policy_verdict.verdict}")
    print(f"Safe commit allowed: {report.policy_verdict.safe_commit_allowed}")
    print(f"Failed gates: {', '.join(report.failed_gates) if report.failed_gates else 'none'}")
    print(f"Warnings: {len(report.warnings)}")
    print(f"Report: {md_path}")
    print(f"JSON: {json_path}")
    print(f"Next action: {report.next_action}")
    return 0


def run_policy_fixtures(project_id: str) -> int:
    project = load_project(project_id)
    exit_code, results, json_path, md_path = run_policy_fixture_suite(project, ["all"])
    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    failed_names = [result.fixture_id for result in results if not result.passed]
    print(f"Policy fixtures: {'PASS' if failed == 0 else 'FAIL'} ({passed}/{len(results)})")
    print(f"Failed fixtures: {', '.join(failed_names) if failed_names else 'none'}")
    print(f"Report: {md_path}")
    print(f"JSON: {json_path}")
    return exit_code


def run_autopilot_health(project_id: str) -> int:
    project = load_project(project_id)
    payload = build_health(project)
    md_path, json_path = write_autopilot_health_reports(project, payload)
    print(f"Autopilot Health: {payload['overall_verdict']}")
    print(f"Policy fixtures: {payload['policy_fixture_suite']['status']} ({payload['policy_fixture_suite']['passed']}/{payload['policy_fixture_suite']['total']})")
    print(f"Providers configured: {payload['provider_registry']['configured_provider_count']}/{payload['provider_registry']['provider_count']}")
    print("Claude Integration Readiness:")
    claude = payload["claude_integration_readiness"]
    print(f"  Claude Code CLI detected: {'yes' if claude['claude_code_cli_detected'] else 'no'}")
    print(f"  Claude Code manual handoff ready: {'yes' if claude['claude_code_manual_handoff_ready'] else 'no'}")
    print(f"  Claude Code automatic execution enabled: {'yes' if claude['claude_code_automatic_execution_enabled'] else 'no'}")
    print(f"  Claude Agent SDK scaffold exists: {'yes' if claude['claude_agent_sdk_provider_scaffold_exists'] else 'no'}")
    print(f"  ANTHROPIC_API_KEY: {claude['anthropic_api_key_status']}")
    print(f"  SDK package detected: {'yes' if claude['sdk_package_detected'] else 'no'}")
    print(f"  Claude SDK dry-run: {claude['claude_sdk_dry_run_verdict']}")
    print(f"  Controlled Claude analysis: {claude.get('controlled_analysis_verdict', 'UNKNOWN')}")
    print(f"  Claude Agent SDK external call tested: {'yes' if claude['claude_agent_sdk_external_call_tested'] else 'no'}")
    sandbox = payload.get("claude_sandbox", {})
    print("Claude Sandbox Boundary:")
    print(f"  Preflight: {sandbox.get('preflight_verdict', 'UNKNOWN')}")
    print(f"  Simulation: {sandbox.get('simulation_verdict', 'UNKNOWN')}")
    print(f"  Builder execution enabled: {'yes' if sandbox.get('builder_execution_enabled') else 'no'}")
    print(f"  Real worktree created: {'yes' if sandbox.get('real_worktree_created') else 'no'}")
    print("Top blockers:")
    for blocker in payload["blockers"] or ["none"]:
        print(f"  - {blocker}")
    print("Next actions:")
    for action in payload["next_actions"]:
        print(f"  - {action}")
    print(f"Safe next sprint: {payload['safe_next_sprint_recommendation']}")
    print(f"Report: {md_path}")
    print(f"JSON: {json_path}")
    return 2 if payload["overall_verdict"] == "AUTOPILOT_BLOCKED" else 0


def run_claude_sdk_dry_run_cmd(project_id: str) -> int:
    exit_code, payload, md_path, json_path = run_claude_sdk_dry_run_report(project_id)
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


def run_claude_analysis_cmd(project_id: str, task: str, approved_live_call: bool) -> int:
    exit_code, metadata = run_claude_analysis_call(project_id, task=task, approved_live_call=approved_live_call)
    print(f"Claude Analysis: {metadata['verdict']}")
    print(f"  Live call made: {'yes' if metadata['live_call_made'] else 'no'}")
    print(f"  Secrets sent: {metadata['secrets_sent']}")
    print(f"  Redactions: {metadata['redaction_count']}")
    print(f"  Request: {metadata['request_redacted_path']}")
    print(f"  Response: {metadata['response_path']}")
    print(f"  Metadata: {Path(metadata['request_redacted_path']).parent / 'claude_analysis_metadata.json'}")
    print(f"  Policy review: {metadata['policy_review_path']}")
    if metadata.get("blocked_reason"):
        print(f"  Note: {metadata['blocked_reason']}")
    print("  Next action: Review saved evidence; keep scheduler and automatic Claude execution disabled.")
    return exit_code


def run_claude_analysis_review_cmd(project_id: str) -> int:
    project = load_project(project_id)
    review = review_latest_claude_analysis(project)
    md_path, json_path = write_claude_analysis_review(project, review)
    print(f"Claude Analysis Review: {review.decision}")
    print(f"  Proceed to sandbox design: {'yes' if review.proceed_to_sandbox_design else 'no'}")
    print(f"  Extracted risks: {len(review.extracted_risks)}")
    print(f"  Findings: {len(review.findings)}")
    print(f"  Fixture recommendations: {', '.join(review.fixture_recommendations) if review.fixture_recommendations else 'none'}")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    print(f"  Next action: {review.next_action}")
    return 2 if review.decision == "BLOCKED" else 0


def run_openai_auditor_status_cmd(project_id: str) -> int:
    project = load_project(project_id)
    payload = openai_auditor_status_payload(project)
    md_path, json_path = write_openai_auditor_status(project, payload)
    provider = payload["provider"]
    print(f"OpenAI Auditor: {provider['current_status']}")
    print(f"  Configured: {'yes' if provider['configured'] else 'no'}")
    print(f"  OPENAI_API_KEY: {provider.get('metadata', {}).get('env_status', 'UNKNOWN')}")
    print("  Live calls enabled: no")
    print("  OpenAI API called: NO")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    return 0


def run_openai_auditor_plan_cmd(project_id: str, task: str) -> int:
    project = load_project(project_id)
    payload = build_openai_auditor_dry_run(project, task)
    md_path, json_path = write_openai_auditor_dry_run(project, payload)
    print(f"OpenAI Auditor Dry-Run: {payload.verdict}")
    print(f"  Recommended builder: {payload.recommended_builder}")
    print("  OpenAI API called: NO")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    print(f"  Next action: {payload.next_action}")
    return 0


def run_multistep_dry_run_cmd(project_id: str, objective: str) -> int:
    project = load_project(project_id)
    payload = build_multistep_loop(project, objective)
    md_path, json_path = write_multistep_loop(project, payload)
    print(f"Multi-Step Loop Dry-Run: {payload.verdict}")
    print(f"  Objective: {payload.objective}")
    print(f"  Recommended builder: {payload.recommended_builder}")
    print("  Execution enabled: no")
    print("  External API called: NO")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    print(f"  Next action: {payload.next_action}")
    return 0


def run_claude_sandbox_preflight_cmd(project_id: str, task: str) -> int:
    project = load_project(project_id)
    preflight = evaluate_claude_sandbox_preflight(project, task)
    preflight_md, preflight_json = write_claude_sandbox_preflight(project, preflight)
    prompt_pack = build_prompt_pack(project, task)
    prompt_md, prompt_json = write_prompt_pack(project, prompt_pack)
    worktree_plan = build_worktree_sandbox_plan(project, task)
    worktree_md, worktree_json = write_worktree_sandbox_plan(project, worktree_plan)
    print(f"Claude Sandbox Preflight: {preflight.verdict}")
    print("  Claude builder execution enabled: no")
    print("  External API called: NO")
    print("  Real worktree created: no")
    print(f"  Allowed file entries: {len(preflight.boundary.file_policy.allowed_files)}")
    print(f"  Denied file entries: {len(preflight.boundary.file_policy.denied_files)}")
    print(f"  Allowed commands: {len(preflight.boundary.command_policy.allowed_commands)}")
    print(f"  Denied commands: {len(preflight.boundary.command_policy.denied_commands)}")
    print(f"  Human approval needed: {'yes' if preflight.boundary.file_policy.requires_human_approval else 'no'}")
    print(f"  Preflight report: {preflight_md}")
    print(f"  Preflight JSON: {preflight_json}")
    print(f"  Prompt pack: {prompt_md}")
    print(f"  Prompt pack JSON: {prompt_json}")
    print(f"  Worktree plan: {worktree_md}")
    print(f"  Worktree plan JSON: {worktree_json}")
    print(f"  Next action: {preflight.next_action}")
    return 0 if preflight.verdict != "SANDBOX_PREFLIGHT_BLOCKED" else 2


def run_claude_sandbox_simulate_cmd(project_id: str, task: str) -> int:
    project = load_project(project_id)
    preflight = evaluate_claude_sandbox_preflight(project, task)
    preflight_md, preflight_json = write_claude_sandbox_preflight(project, preflight)
    prompt_pack = build_prompt_pack(project, task)
    prompt_md, prompt_json = write_prompt_pack(project, prompt_pack)
    worktree_plan = build_worktree_sandbox_plan(project, task)
    worktree_md, worktree_json = write_worktree_sandbox_plan(project, worktree_plan)
    simulation = simulate_claude_sandbox(project, task)
    simulation_md, simulation_json = write_claude_sandbox_simulation(project, simulation)
    print(f"Claude Sandbox Simulation: {simulation.verdict}")
    print("  Lifecycle simulated: task -> OpenAI Auditor -> future Claude sandbox -> validation -> policy")
    print("  Claude builder execution enabled: no")
    print("  External API called: NO")
    print("  Real worktree created: no")
    print(f"  Denied command tests: {len(simulation.denied_command_tests)}")
    print(f"  Preflight report: {preflight_md}")
    print(f"  Preflight JSON: {preflight_json}")
    print(f"  Prompt pack: {prompt_md}")
    print(f"  Prompt pack JSON: {prompt_json}")
    print(f"  Worktree plan: {worktree_md}")
    print(f"  Worktree plan JSON: {worktree_json}")
    print(f"  Simulation report: {simulation_md}")
    print(f"  Simulation JSON: {simulation_json}")
    print(f"  Next action: {simulation.next_action}")
    return 0 if simulation.verdict == "SANDBOX_SIMULATION_PASS" else 2


def run_doctor(project_id: str) -> int:
    """Validate environment and project health. No API calls, no Telegram sends."""
    project = load_project(project_id)
    issues: list[ConfigIssue] = []

    def add(severity: str, code: str, message: str, recommendation: str) -> None:
        issues.append(ConfigIssue(severity, code, message, recommendation))

    def check_ignore(path: str) -> bool:
        result = subprocess.run(
            ["git", "check-ignore", "-q", path],
            cwd=project.repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0

    def npm_script_from_command(command: str) -> str | None:
        parts = command.strip().split()
        if len(parts) >= 3 and parts[0] == "npm" and parts[1] == "run":
            return parts[2]
        if command.strip() == "npm test":
            return "test"
        return None

    print(f"Doctor: {project.project_name} ({project.project_id})")
    print()

    # Environment
    add("pass", "REPO_ROOT_DETECTED", f"repo root detected: {project.repo_path}", "No action needed.")
    env_path = project.repo_path / ".env"
    env_local = project.repo_path / ".env.local"
    add("pass" if env_path.exists() else "warn", "ENV_FOUND", f".env found: {'yes' if env_path.exists() else 'no'}", "No action needed." if env_path.exists() else "Create locally only if required.")
    add("pass" if env_local.exists() else "warn", "ENV_LOCAL_FOUND", f".env.local found: {'yes' if env_local.exists() else 'no'}", "No action needed." if env_local.exists() else "Create locally only if required.")
    openai_key = os.environ.get("OPENAI_API_KEY")
    add("pass" if openai_key else "warn", "OPENAI_API_KEY_PRESENT", f"OPENAI_API_KEY present: {'yes' if openai_key else 'no'}", "Set locally for --cycle; local-plan works without it.")
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get(f"{project.project_id.upper()}_TELEGRAM_BOT_TOKEN")
    telegram_chat = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get(f"{project.project_id.upper()}_TELEGRAM_CHAT_ID")
    add("pass" if telegram_token else "warn", "TELEGRAM_BOT_TOKEN_PRESENT", f"TELEGRAM_BOT_TOKEN present: {'yes' if telegram_token else 'no'}", "Set locally to enable alerts.")
    add("pass" if telegram_chat else "warn", "TELEGRAM_CHAT_ID_PRESENT", f"TELEGRAM_CHAT_ID present: {'yes' if telegram_chat else 'no'}", "Set locally to enable alerts.")
    claude_ok, claude_path = detect_claude_cli(project)
    add("pass" if claude_ok else "warn", "CLAUDE_CLI_DETECTED", f"Claude CLI detected: {'yes' if claude_ok else 'no'}", claude_path if claude_ok else "Install/configure Claude CLI for handoff execution; manual paste still works.")
    try:
        import playwright.sync_api  # noqa: F401
        pw_ok = True
    except ImportError:
        pw_ok = False
    add("pass" if pw_ok else "warn", "PLAYWRIGHT_DETECTED", f"Playwright detected: {'yes' if pw_ok else 'no'}", "Install later for richer browser QA; HTTP checks can still run.")
    if not pw_ok:
        add("warn", "PLAYWRIGHT_LIMITATION", "Without Playwright: no screenshots, no console/page errors, no network interception, no responsive testing.", "pip install playwright && python -m playwright install chromium")
    add("pass", "BROWSER_QA_ENABLED", f"browser_qa_enabled: {project.browser_qa_enabled}", "Enable in project config when Browser QA should be required by workflow.")
    add("pass", "SCREENSHOT_ENABLED", f"screenshot_enabled: {project.screenshot_enabled}", "No action needed.")
    from browser_qa import resolve_viewports
    viewports = resolve_viewports(project)
    add(
        "pass",
        "BROWSER_QA_VIEWPORTS",
        f"configured viewports: {len(viewports)} ({', '.join(viewports.keys())})",
        "Add browser_qa_viewports to project config to customize. Defaults: mobile, tablet, desktop.",
    )
    add(
        "pass" if project.route_walk_urls else "warn",
        "ROUTE_WALK_URL_COUNT",
        f"configured route_walk_urls: {len(project.route_walk_urls)}",
        "Add route_walk_urls to project config for Browser QA coverage." if not project.route_walk_urls else "No action needed.",
    )

    # Config
    cfg_path = project_config_path(project_id)
    issues.extend(validate_project_config(project, cfg_path))

    # Project control
    required_control = [
        "MASTER_PLAN.md",
        "CURRENT_STATE.md",
        "TASK_QUEUE.md",
        "QUALITY_BAR.md",
        "WORLD_CLASS_STANDARD.md",
        "QA_PROTOCOL.md",
        "CUSTOMER_DATA_POLICY.md",
        "RESEARCH_PROTOCOL.md",
        "DESIGN_REFERENCES.md",
        "TECHNICAL_ARCHITECTURE.md",
        "COST_POLICY.md",
        "DECISIONS.md",
        "BLOCKERS.md",
        "HUMAN_QUESTIONS.md",
        "AGENT_RULES.md",
        "AUTONOMY_PROTOCOL.md",
    ]
    for name in required_control:
        exists = (project.project_control_path / name).exists()
        add("pass" if exists else "fail", f"CONTROL_{name.replace('.', '_').upper()}", f"project_control/{name} exists: {'yes' if exists else 'no'}", "No action needed." if exists else "Create from template.")

    # Repo health
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project.repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    dirty = len([line for line in result.stdout.splitlines() if line.strip()])
    add("pass" if dirty == 0 else "warn", "GIT_STATUS", f"git status: {'clean' if dirty == 0 else f'dirty ({dirty} files)'}", "Commit or stash unrelated changes before autonomous work.")
    for path in ["logs/autopilot-test.md", "logs/evidence/test/metadata.json", ".env", ".env.local", "node_modules/example", ".next/example", "__pycache__/example.pyc"]:
        ignored = check_ignore(path)
        add("pass" if ignored else "fail", f"IGNORED_{path.upper().replace('/', '_').replace('.', '_').replace('-', '_')}", f"{path} ignored: {'yes' if ignored else 'no'}", "Update .gitignore.")
    screenshot_probe = f"screenshots/{project.project_id}/autopilot-test.png"
    screenshot_ignored = check_ignore(screenshot_probe)
    add(
        "pass" if screenshot_ignored else "warn",
        "SCREENSHOT_DIRECTORY_IGNORED",
        f"{screenshot_probe} ignored: {'yes' if screenshot_ignored else 'no'}",
        "Keep Browser QA screenshots out of commits unless intentionally curating evidence.",
    )

    # package.json and configured scripts
    pkg_path = project.repo_path / "package.json"
    if pkg_path.exists():
        add("pass", "PACKAGE_JSON_EXISTS", "package.json exists", "No action needed.")
        package = json.loads(pkg_path.read_text(encoding="utf-8"))
        scripts = package.get("scripts", {})
        for label, command in [
            ("build", project.build_command),
            ("typecheck", project.typecheck_command),
            ("lint", project.lint_command),
            ("test", project.test_command),
        ]:
            script = npm_script_from_command(command)
            if script:
                exists = script in scripts
                severity = "pass" if exists else ("warn" if label == "test" else "fail")
                add(severity, f"NPM_SCRIPT_{script.upper()}_EXISTS", f"npm script '{script}' exists: {'yes' if exists else 'no'}", "No action needed." if exists else "Add the script or update project config.")
            else:
                add("warn", f"COMMAND_{label.upper()}_SCRIPT_UNKNOWN", f"Could not infer npm script from {label}_command: {command}", "Verify command manually.")
    else:
        add("fail", "PACKAGE_JSON_MISSING", "package.json missing", "Add package.json or update package manager config.")

    # Browser QA and Claude handoff config summary checks.
    add("pass" if isinstance(project.browser_qa_enabled, bool) else "fail", "BROWSER_QA_CONFIG_VALID", f"browser_qa_enabled={project.browser_qa_enabled}", "Use true or false.")
    add("pass" if project.builder_handoff_mode in {"manual", "disabled", "automatic"} else "fail", "CLAUDE_HANDOFF_CONFIG_VALID", f"builder_handoff_mode={project.builder_handoff_mode}", "Use manual, disabled, or automatic.")

    # HALT_AUTOPILOT
    halt = _halt_active(project)
    add("warn" if halt else "pass", "HALT_AUTOPILOT", f"HALT_AUTOPILOT active: {'YES' if halt else 'no'}", "Remove project_control/HALT_AUTOPILOT.md to resume cycles." if halt else "No action needed.")

    fixture_health = policy_fixture_health(project)
    fixture_severity = fixture_health["severity"]
    add(
        "pass" if fixture_severity == "pass" else ("fail" if fixture_severity == "fail" else "warn"),
        "POLICY_FIXTURE_SUITE",
        f"policy fixtures: {fixture_health['status']} ({fixture_health['passed']}/{fixture_health['total']} passed)",
        fixture_health["command"],
    )
    claude_dry = claude_sdk_dry_run_health(project)
    add(
        "pass" if claude_dry["severity"] == "pass" else ("fail" if claude_dry["severity"] == "fail" else "warn"),
        "CLAUDE_SDK_DRY_RUN",
        f"Claude SDK dry-run: {claude_dry['verdict']}; ANTHROPIC_API_KEY={claude_dry.get('anthropic_api_key_status', 'UNKNOWN')}",
        claude_dry["command"],
    )

    severity_rank = {"pass": 0, "warn": 1, "fail": 2}
    for item in sorted(issues, key=lambda issue: (severity_rank[issue.severity], issue.code)):
        print(f"{item.severity.upper():4} {item.code}: {item.message}")
        if item.severity != "pass":
            print(f"     Recommendation: {item.recommendation}")

    result_severity = worst_severity(issues)
    result_label = result_severity.upper()
    print()
    print(f"DOCTOR_RESULT: {result_label}")

    # Scheduler readiness report
    print()
    _print_scheduler_readiness(project)
    print()
    _print_product_validation_readiness(project)
    print()
    _print_policy_fixture_readiness(project)

    return 2 if result_severity == "fail" else 0


def _print_policy_fixture_readiness(project: ProjectConfig) -> None:
    info = policy_fixture_health(project)
    status = info["status"]
    if status == "PASS":
        result = "PASS"
    elif status == "FAIL":
        result = "FAIL"
    else:
        result = "WARN"
    print("POLICY_FIXTURE_SUITE:")
    print(f"  status: {result}")
    print(f"  latest result: {info['result_path']}")
    print(f"  latest report: {info['report_path']}")
    print(f"  passed/total: {info['passed']}/{info['total']}")
    print(f"  failed count: {info['failed']}")
    print(f"  failed fixtures: {', '.join(info['failed_fixtures']) if info['failed_fixtures'] else 'none'}")
    print(f"  command: {info['command']}")


def _print_product_validation_readiness(project: ProjectConfig) -> None:
    """Print product-validation readiness. Does not access Supabase or run app flows."""
    e2e_path = _e2e_plan_path(project)
    supabase_url_present = bool(os.environ.get("NEXT_PUBLIC_SUPABASE_URL"))
    supabase_anon_present = bool(os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY"))
    checks: list[tuple[str, bool, str]] = [
        ("MIRA_E2E_VALIDATION_PLAN exists", e2e_path.exists(), str(e2e_path.relative_to(project.repo_path))),
        ("Browser QA available", True, "project_autopilot/browser_qa.py"),
        ("Browser QA mode available", True, "playwright when installed, otherwise http_only"),
        ("NEXT_PUBLIC_SUPABASE_URL present", supabase_url_present, "value hidden"),
        ("NEXT_PUBLIC_SUPABASE_ANON_KEY present", supabase_anon_present, "value hidden"),
        ("route_walk_urls configured", bool(project.route_walk_urls), f"{len(project.route_walk_urls)} routes"),
        ("customer data policy exists", (project.project_control_path / "CUSTOMER_DATA_POLICY.md").exists(), "project_control/CUSTOMER_DATA_POLICY.md"),
        ("QA protocol exists", (project.project_control_path / "QA_PROTOCOL.md").exists(), "project_control/QA_PROTOCOL.md"),
        ("world-class standard exists", (project.project_control_path / "WORLD_CLASS_STANDARD.md").exists(), "project_control/WORLD_CLASS_STANDARD.md"),
    ]
    required = {
        "MIRA_E2E_VALIDATION_PLAN exists",
        "NEXT_PUBLIC_SUPABASE_URL present",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY present",
        "route_walk_urls configured",
        "customer data policy exists",
        "QA protocol exists",
        "world-class standard exists",
    }
    missing_required = [name for name, ok, _ in checks if name in required and not ok]
    if not missing_required:
        result = "READY"
    elif any(name.startswith("NEXT_PUBLIC_SUPABASE") for name in missing_required):
        result = "WARN"
    else:
        result = "NOT_READY"

    print("PRODUCT_VALIDATION_READINESS:")
    for name, ok, detail in checks:
        print(f"  {'[x]' if ok else '[ ]'} {name}: {detail}")
    print()
    print(f"PRODUCT_VALIDATION_READINESS_RESULT: {result}")
    if missing_required:
        print(f"  Missing/needs attention: {', '.join(missing_required)}")


def _print_scheduler_readiness(project: ProjectConfig) -> None:
    """Print scheduler readiness checklist. Does not implement a scheduler."""
    checks: list[tuple[str, bool]] = []

    # git clean
    try:
        git_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project.repo_path,
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10,
        )
        git_clean = not any(line.strip() for line in git_result.stdout.splitlines())
    except Exception:
        git_clean = False
    checks.append(("git clean", git_clean))

    # config valid
    from config_validator import validate_project_config as _vp, worst_severity as _ws
    cfg_issues = _vp(project, project_config_path(project.project_id))
    checks.append(("config valid", _ws(cfg_issues) != "fail"))

    # logs ignored
    try:
        log_ignored = subprocess.run(
            ["git", "check-ignore", "-q", "logs/autopilot-test.md"],
            cwd=project.repo_path, capture_output=True, text=True, timeout=10,
        ).returncode == 0
    except Exception:
        log_ignored = False
    checks.append(("logs ignored", log_ignored))

    # run_lock available
    try:
        from run_lock import acquire_lock as _al  # noqa: F401
        checks.append(("run_lock available", True))
    except ImportError:
        checks.append(("run_lock available", False))

    # HALT_AUTOPILOT absent
    checks.append(("HALT_AUTOPILOT absent", not _halt_active(project)))

    # evidence bundle available
    bundle_dir = project.repo_path / "logs" / "evidence" / project.project_id
    checks.append(("evidence bundle available", bundle_dir.exists()))

    # risk classifier available
    try:
        from risk_classifier import classify_task as _ct  # noqa: F401
        checks.append(("risk classifier available", True))
    except ImportError:
        checks.append(("risk classifier available", False))

    # Telegram configured
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get(f"{project.project_id.upper()}_TELEGRAM_BOT_TOKEN")
    telegram_chat = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get(f"{project.project_id.upper()}_TELEGRAM_CHAT_ID")
    checks.append(("Telegram configured", bool(telegram_token and telegram_chat)))

    # budget limits valid
    budgets_ok = (
        project.daily_budget_usd > 0
        and project.per_cycle_budget_usd > 0
        and project.monthly_budget_usd > 0
    )
    checks.append(("budget limits valid", budgets_ok))

    # max_cycles_per_day configured
    checks.append(("max_cycles_per_day configured", project.max_cycles_per_day > 0))

    # run_frequency_hours configured
    checks.append(("run_frequency_hours configured", project.run_frequency_hours > 0))

    # automatic builder execution disabled or explicitly safe
    checks.append(("automatic builder execution disabled", not project.allow_automatic_builder_execution))

    # paid APIs disabled or budgeted
    checks.append(("paid APIs disabled or budgeted", project.paid_api_mode in ("disabled_by_default", "enabled_with_budget")))

    # deploy automation disabled (always true — no deploy automation exists)
    checks.append(("deploy automation disabled", True))

    # retry policy configured
    rp = project.retry_policy
    retry_ok = rp.max_attempts >= 1 and rp.backoff_seconds >= 1 and rp.backoff_multiplier >= 1 and rp.stop_on_same_error_count >= 1
    checks.append(("retry policy configured", retry_ok))

    # no open critical blockers
    blocker_info = summarize_blockers(project)
    checks.append(("no open critical blockers", blocker_info.open_count == 0))

    # post-builder intake available
    try:
        from builder_intake import intake_builder_report as _ibr  # noqa: F401
        checks.append(("post-builder intake available", True))
    except ImportError:
        checks.append(("post-builder intake available", False))

    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    failed = [name for name, ok in checks if not ok]

    hard_requirements = {
        "run_lock available", "HALT_AUTOPILOT absent", "config valid",
        "max_cycles_per_day configured", "run_frequency_hours configured",
        "budget limits valid",
    }
    if passed == total:
        result = "READY"
    elif any(f in hard_requirements for f in failed):
        result = "NOT_READY"
    else:
        result = "WARN"

    print("SCHEDULER_READINESS:")
    for name, ok in checks:
        status = "ok" if ok else "MISSING"
        print(f"  {'[x]' if ok else '[ ]'} {name}: {status}")
    print()
    print(f"SCHEDULER_READINESS_RESULT: {result}")
    if failed:
        print(f"  Missing: {', '.join(failed)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Project Autopilot — reusable autonomous builder orchestrator.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -B project_autopilot/agent_loop.py --project mira --doctor\n"
            "  python -B project_autopilot/agent_loop.py --project mira --dry-run\n"
            "  python -B project_autopilot/agent_loop.py --project mira --local-plan\n"
            "  python -B project_autopilot/agent_loop.py --project mira --cycle\n"
            "  python -B project_autopilot/agent_loop.py --project mira --status\n"
            "  python -B project_autopilot/agent_loop.py --project mira --history\n"
            "  python -B project_autopilot/agent_loop.py --project mira --metrics\n"
            "  python -B project_autopilot/agent_loop.py --project mira --e2e-plan\n"
            "  python -B project_autopilot/agent_loop.py --project mira --handoff-claude\n"
            "  python -B project_autopilot/agent_loop.py --project mira --policy-fixtures\n"
            "  python -B project_autopilot/agent_loop.py --project mira --autopilot-health\n"
            "  python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run\n"
            "  python -B project_autopilot/agent_loop.py --project mira --claude-analysis-dry-run\n"
            "  python -B project_autopilot/agent_loop.py --project mira --claude-analysis-review\n"
            "  python -B project_autopilot/agent_loop.py --project mira --openai-auditor-status\n"
            "  python -B project_autopilot/agent_loop.py --project mira --multistep-dry-run --objective \"Improve MIRA result page design\"\n"
        ),
    )
    parser.add_argument("--project", default="mira", help="Project id from project_autopilot/config/projects/.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="Skip OpenAI calls and validation commands.")
    group.add_argument("--cycle", action="store_true", help="Run one bounded planning/QA cycle. Falls back to local plan on OpenAI failure.")
    group.add_argument("--local-plan", action="store_true", help="Force local fallback planner. No OpenAI call.")
    group.add_argument("--status", action="store_true", help="Print project status summary.")
    group.add_argument("--history", action="store_true", help="Print recent run history summary.")
    group.add_argument("--metrics", action="store_true", help="Print latest run activity metrics.")
    group.add_argument("--research-status", action="store_true", help="Print research request summary.")
    group.add_argument("--request-research", metavar="TOPIC", help="Record a research request. Does not run research.")
    group.add_argument("--doctor", action="store_true", help="Validate environment and project health.")
    group.add_argument("--handoff-claude", action="store_true", help="Generate prompt then hand off to Claude Code (manual mode).")
    group.add_argument("--claude-manual", action="store_true", help="Print latest prompt path for manual paste into Claude Code.")
    group.add_argument("--claude-execute", action="store_true", help="Invoke Claude CLI automatically (blocked unless config allows).")
    group.add_argument("--browser-qa", action="store_true", help="Run browser QA against configured route_walk_urls.")
    group.add_argument("--browser-qa-diagnose", action="store_true", help="Diagnose Browser QA dev-server reachability.")
    group.add_argument("--backend-audit", action="store_true", help="Run static backend and data-flow audit.")
    group.add_argument("--control-center", action="store_true", help="Generate Control Center HTML report.")
    group.add_argument("--e2e-plan", action="store_true", help="Print the project-specific manual E2E validation plan.")
    group.add_argument("--new-validation-report", action="store_true", help="Create a blank product validation report draft.")
    group.add_argument("--intake-builder-report", metavar="PATH", help="Ingest a builder report and produce a QA verdict.")
    group.add_argument("--post-builder", metavar="PATH", help="Alias for --intake-builder-report.")
    group.add_argument("--policy-check", action="store_true", help="Evaluate current working tree with v2 post-builder policy gates.")
    group.add_argument("--policy-fixtures", action="store_true", help="Run deterministic v2 policy fixture regression tests.")
    group.add_argument("--autopilot-health", action="store_true", help="Print consolidated Project Autopilot operational health.")
    group.add_argument("--claude-sdk-dry-run", action="store_true", help="Validate Claude Agent SDK dry-run readiness without external calls.")
    group.add_argument("--claude-analysis-dry-run", action="store_true", help="Build a sanitized Claude analysis prompt without calling Anthropic.")
    group.add_argument("--claude-analysis-approved", action="store_true", help="Make one explicit analysis-only Anthropic call.")
    group.add_argument("--claude-analysis-review", action="store_true", help="Review saved Claude analysis evidence and map it to policy decisions.")
    group.add_argument("--openai-auditor-status", action="store_true", help="Show OpenAI Auditor dry-run provider status without API calls.")
    group.add_argument("--openai-auditor-plan", action="store_true", help="Create an OpenAI Auditor dry-run plan for --task without API calls.")
    group.add_argument("--multistep-dry-run", action="store_true", help="Preview the future planner-builder-review-policy loop without execution.")
    group.add_argument("--claude-sandbox-preflight", action="store_true", help="Evaluate future Claude sandbox boundary without executing Claude.")
    group.add_argument("--claude-sandbox-simulate", action="store_true", help="Simulate future Claude sandbox lifecycle without creating a worktree.")
    parser.add_argument("--research-mode", default="quick_check", choices=["quick_check", "standard_research", "deep_research"], help="Research mode for --request-research.")
    parser.add_argument("--task", default="Review Project Autopilot v2 architecture and identify top 5 risks.", help="Task text for Claude analysis or planning commands.")
    parser.add_argument("--objective", default="Improve MIRA result page design", help="Objective text for --multistep-dry-run.")

    args = parser.parse_args()

    if args.doctor:
        return run_doctor(args.project)
    if args.status:
        return run_status(args.project)
    if args.history:
        return run_history_cmd(args.project)
    if args.metrics:
        return run_metrics_cmd(args.project)
    if args.research_status:
        return run_research_status(args.project)
    if args.request_research:
        return run_request_research(args.project, args.request_research, args.research_mode)
    if args.local_plan:
        return run_local_plan(args.project)
    if args.handoff_claude:
        return run_handoff_claude(args.project)
    if args.claude_manual:
        return run_claude_manual(args.project)
    if args.claude_execute:
        return run_claude_execute(args.project)
    if args.browser_qa:
        return run_browser_qa_cmd(args.project)
    if args.browser_qa_diagnose:
        return run_browser_qa_diagnose(args.project)
    if args.backend_audit:
        return run_backend_audit_cmd(args.project)
    if args.control_center:
        return run_control_center(args.project)
    if args.e2e_plan:
        return run_e2e_plan(args.project)
    if args.new_validation_report:
        return run_new_validation_report(args.project)
    if args.intake_builder_report:
        return run_builder_intake(args.project, args.intake_builder_report)
    if args.post_builder:
        return run_builder_intake(args.project, args.post_builder)
    if args.policy_check:
        return run_policy_check(args.project)
    if args.policy_fixtures:
        return run_policy_fixtures(args.project)
    if args.autopilot_health:
        return run_autopilot_health(args.project)
    if args.claude_sdk_dry_run:
        return run_claude_sdk_dry_run_cmd(args.project)
    if args.claude_analysis_dry_run:
        return run_claude_analysis_cmd(args.project, args.task, approved_live_call=False)
    if args.claude_analysis_approved:
        return run_claude_analysis_cmd(args.project, args.task, approved_live_call=True)
    if args.claude_analysis_review:
        return run_claude_analysis_review_cmd(args.project)
    if args.openai_auditor_status:
        return run_openai_auditor_status_cmd(args.project)
    if args.openai_auditor_plan:
        return run_openai_auditor_plan_cmd(args.project, args.task)
    if args.multistep_dry_run:
        return run_multistep_dry_run_cmd(args.project, args.objective)
    if args.claude_sandbox_preflight:
        return run_claude_sandbox_preflight_cmd(args.project, args.task)
    if args.claude_sandbox_simulate:
        return run_claude_sandbox_simulate_cmd(args.project, args.task)
    return run_cycle(project_id=args.project, dry_run=args.dry_run, cycle=args.cycle)


if __name__ == "__main__":
    raise SystemExit(main())
