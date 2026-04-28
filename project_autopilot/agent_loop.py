from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from env_loader import load_env

load_env()

from config import ProjectConfig
from cost_controller import CostController
from evidence_collector import collect_evidence
from local_planner import generate_local_plan
from openai_supervisor import BudgetBlocked, MissingOpenAICredentials, OpenAIRequestError, OpenAISupervisor
from project_loader import ensure_project_dirs, load_project, read_project_control
from prompt_builder import build_builder_prompt
from qa_reviewer import generate_correction_prompt, review_with_openai
from state_manager import load_state, record_blocker, save_state, write_failure_log, write_iteration_log
from browser_qa import run_browser_qa, write_browser_qa_report
from claude_runner import detect_claude_cli, handoff_execute, handoff_manual, resolve_prompt_path
from telegram_alerts import send_alert


# ---------------------------------------------------------------------------
# Core modes
# ---------------------------------------------------------------------------


def run_cycle(project_id: str, dry_run: bool = False, cycle: bool = False) -> int:
    """Original planning cycle: evidence -> OpenAI -> builder prompt."""
    project = load_project(project_id)
    ensure_project_dirs(project)

    cost_controller = CostController(project)
    control_docs = read_project_control(project)
    evidence = collect_evidence(project, dry_run=dry_run)
    supervisor = OpenAISupervisor(project, cost_controller, dry_run=dry_run)

    try:
        task_plan = supervisor.plan_next_task(control_docs, evidence)
        qa_review = review_with_openai(supervisor, task_plan, evidence)
        correction_prompt = generate_correction_prompt(supervisor, task_plan, qa_review, evidence)
    except (MissingOpenAICredentials, BudgetBlocked, OpenAIRequestError) as exc:
        return _handle_openai_failure(project, cost_controller, control_docs, evidence, exc)

    builder_prompt = build_builder_prompt(project, control_docs, task_plan, evidence)
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
    prompt_rel = str((project.repo_path / project.logs_dir / f"{project.project_id}_latest_builder_prompt.md").relative_to(project.repo_path))
    state["last_builder_prompt"] = prompt_rel
    save_state(project, state)

    print(f"Project: {project.project_name} ({project.project_id})")
    print(f"Generated builder prompt: {project.repo_path / project.logs_dir / f'{project.project_id}_latest_builder_prompt.md'}")
    print(f"Wrote iteration log: {log_path}")
    print("No builder work was executed.")
    return 0


def _handle_openai_failure(
    project: ProjectConfig,
    cost_controller: CostController,
    control_docs: dict[str, str],
    evidence: dict[str, Any],
    exc: Exception,
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

    # 3. Send Telegram alert
    alert = send_alert(project.project_id, error_type, message, enabled=project.telegram_enabled)

    # 4. Generate local fallback plan
    fallback = generate_local_plan(project, control_docs, evidence)
    fallback_path = project.repo_path / project.logs_dir / f"{project.project_id}_latest_builder_prompt.md"
    fallback_path.parent.mkdir(parents=True, exist_ok=True)
    fallback_path.write_text(fallback, encoding="utf-8")

    # 5. Update state
    state = load_state(project)
    state["last_status"] = "blocked_with_fallback"
    state["last_error"] = error_dict
    state["last_log"] = str(log_path.relative_to(project.repo_path))
    state["last_builder_prompt"] = str(fallback_path.relative_to(project.repo_path))
    save_state(project, state)

    # 6. Print summary
    print(f"Blocked: {error_type}" + (f" ({status_code})" if status_code else ""))
    print(message)
    print(f"Failure log: {log_path}")
    print(f"Telegram: {alert.reason}")
    print(f"Local fallback plan written to: {fallback_path}")
    print("You can paste the fallback plan into Claude Code as the builder prompt.")
    return 2


def run_local_plan(project_id: str) -> int:
    """Force local fallback planner — no OpenAI call."""
    project = load_project(project_id)
    ensure_project_dirs(project)

    control_docs = read_project_control(project)
    evidence = collect_evidence(project, dry_run=False)

    fallback = generate_local_plan(project, control_docs, evidence)
    prompt_path = project.repo_path / project.logs_dir / f"{project.project_id}_latest_builder_prompt.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(fallback, encoding="utf-8")

    state = load_state(project)
    state["cycles"] = int(state.get("cycles", 0)) + 1
    state["last_status"] = "local_plan"
    state["last_builder_prompt"] = str(prompt_path.relative_to(project.repo_path))
    save_state(project, state)

    print(f"Project: {project.project_name} ({project.project_id})")
    print(f"Local fallback plan written to: {prompt_path}")
    print("Paste this into Claude Code or your preferred builder agent.")
    return 0


def run_status(project_id: str) -> int:
    """Print project status summary."""
    project = load_project(project_id)
    state = load_state(project)
    cost = CostController(project)

    print(f"Project:            {project.project_name} ({project.project_id})")
    print(f"Autonomy mode:      {project.autonomy_mode}")
    print(f"Intensity mode:     {project.intensity_mode}")
    print(f"Builder primary:    {project.builder_primary}")
    print(f"Builder fallback:   {project.builder_fallback}")
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
    print(f"Cycles run:         {state.get('cycles', 0)}")
    print(f"Last status:        {state.get('last_status', 'unknown')}")
    last_log = state.get("last_log")
    if last_log:
        print(f"Last log:           {last_log}")
    last_prompt = state.get("last_builder_prompt")
    if last_prompt:
        print(f"Last builder prompt:{last_prompt}")
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

    # Latest logs
    logs_dir = project.repo_path / project.logs_dir
    if logs_dir.exists():
        logs = sorted(logs_dir.glob(f"{project.project_id}_autopilot_*.md"), reverse=True)[:3]
        if logs:
            print()
            print("Recent logs:")
            for log in logs:
                print(f"  {log.relative_to(project.repo_path)}")

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

    report = run_browser_qa(project)

    if not report.dev_server_reachable:
        print(report.summary)
        return 1

    report_path = write_browser_qa_report(project, report)

    state = load_state(project)
    state["last_browser_qa"] = str(report_path.relative_to(project.repo_path))
    state["browser_qa_passed"] = report.passed
    save_state(project, state)

    print(f"Browser QA: {'PASS' if report.passed else 'FAIL'}")
    print(report.summary)
    print(f"Report: {report_path}")

    if not report.passed:
        failed = [r for r in report.routes if r.console_errors or r.page_errors or (r.status and r.status >= 400)]
        for r in failed:
            print(f"  FAIL: {r.url} (HTTP {r.status}, {len(r.console_errors)} console errors, {len(r.page_errors)} page errors)")

    return 0 if report.passed else 1


def run_doctor(project_id: str) -> int:
    """Validate environment and project health. No API calls, no Telegram sends."""
    project = load_project(project_id)
    checks: list[tuple[str, bool, str]] = []

    # --- Environment files ---
    env_path = project.repo_path / ".env"
    env_local = project.repo_path / ".env.local"
    checks.append((".env found", env_path.exists(), "yes" if env_path.exists() else "no"))
    checks.append((".env.local found", env_local.exists(), "yes" if env_local.exists() else "no"))

    # --- Credentials ---
    openai_key = os.environ.get("OPENAI_API_KEY")
    checks.append(("OPENAI_API_KEY present", bool(openai_key), "yes" if openai_key else "MISSING (local-plan still works)"))

    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get(f"{project.project_id.upper()}_TELEGRAM_BOT_TOKEN")
    telegram_chat = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get(f"{project.project_id.upper()}_TELEGRAM_CHAT_ID")
    checks.append(("TELEGRAM_BOT_TOKEN present", bool(telegram_token), "yes" if telegram_token else "MISSING"))
    checks.append(("TELEGRAM_CHAT_ID present", bool(telegram_chat), "yes" if telegram_chat else "MISSING"))

    # --- Project config ---
    from config import project_config_path
    cfg_path = project_config_path(project_id)
    checks.append(("Project config readable", cfg_path.exists(), str(cfg_path)))

    # --- project_control ---
    checks.append(("project_control dir", project.project_control_path.exists(), str(project.project_control_path)))
    for name in ["TASK_QUEUE.md", "CURRENT_STATE.md", "QUALITY_BAR.md", "AGENT_RULES.md", "AUTONOMY_PROTOCOL.md", "COST_POLICY.md", "WORLD_CLASS_STANDARD.md", "QA_PROTOCOL.md", "CUSTOMER_DATA_POLICY.md", "RESEARCH_PROTOCOL.md"]:
        p = project.project_control_path / name
        checks.append((f"  {name}", p.exists(), ""))

    # --- package.json scripts ---
    pkg_path = project.repo_path / "package.json"
    if pkg_path.exists():
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        scripts = pkg.get("scripts", {})
        for cmd_name in ["build", "typecheck", "lint", "test"]:
            checks.append((f"npm script: {cmd_name}", cmd_name in scripts, ""))
    else:
        checks.append(("package.json", False, "not found"))

    # --- Git ---
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project.repo_path,
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10,
        )
        dirty = len([line for line in result.stdout.strip().splitlines() if line.strip()])
        checks.append(("Git clean", dirty == 0, f"{dirty} dirty files" if dirty else "clean"))
    except Exception:
        checks.append(("Git status", False, "unavailable"))

    # --- Commands ---
    for label, cmd in [("Build cmd", project.build_command), ("Typecheck cmd", project.typecheck_command), ("Lint cmd", project.lint_command)]:
        checks.append((label, bool(cmd), cmd or "not configured"))

    # --- Claude CLI ---
    claude_ok, claude_path = detect_claude_cli(project)
    checks.append(("Claude CLI", claude_ok, claude_path if claude_ok else f"'{project.claude_command}' not on PATH"))

    # --- Playwright ---
    try:
        import playwright.sync_api  # noqa: F401
        pw_ok = True
    except ImportError:
        pw_ok = False
    checks.append(("Playwright", pw_ok, "available" if pw_ok else "not installed (browser QA limited to HTTP checks)"))

    # --- Print check results ---
    print(f"Doctor: {project.project_name} ({project.project_id})")
    print()
    all_ok = True
    for label, ok, detail in checks:
        icon = "OK" if ok else "!!"
        if not ok:
            all_ok = False
        line = f"  [{icon}] {label}"
        if detail:
            line += f"  ({detail})"
        print(line)

    # --- Config summary (always printed, not pass/fail) ---
    print()
    print("Configuration:")
    print(f"  Intensity mode:   {project.intensity_mode}")
    r = project.model_routing
    print(f"  Model routing:    cheap={r.cheap_model}  standard={r.standard_model}  premium={r.premium_model}  qa={r.qa_model}")
    print(f"  Budget:           cycle=${project.per_cycle_budget_usd:.2f}  daily=${project.daily_budget_usd:.2f}  monthly=${project.monthly_budget_usd:.2f}")
    print(f"  Paid API mode:    {project.paid_api_mode}")
    print(f"  Handoff mode:     {project.builder_handoff_mode}")
    print(f"  Auto execution:   {'ENABLED' if project.allow_automatic_builder_execution else 'disabled'}")
    print(f"  Browser QA:       {'enabled' if project.browser_qa_enabled else 'disabled (use --browser-qa to run manually)'}")
    print(f"  Route walk URLs:  {len(project.route_walk_urls)}")

    print()
    if all_ok:
        print("All checks passed.")
    else:
        fail_count = sum(1 for _, ok, _ in checks if not ok)
        print(f"{fail_count} issue(s) found. Review above.")
    return 0 if all_ok else 1


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
            "  python -B project_autopilot/agent_loop.py --project mira --handoff-claude\n"
        ),
    )
    parser.add_argument("--project", default="mira", help="Project id from project_autopilot/config/projects/.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="Skip OpenAI calls and validation commands.")
    group.add_argument("--cycle", action="store_true", help="Run one bounded planning/QA cycle. Falls back to local plan on OpenAI failure.")
    group.add_argument("--local-plan", action="store_true", help="Force local fallback planner. No OpenAI call.")
    group.add_argument("--status", action="store_true", help="Print project status summary.")
    group.add_argument("--doctor", action="store_true", help="Validate environment and project health.")
    group.add_argument("--handoff-claude", action="store_true", help="Generate prompt then hand off to Claude Code (manual mode).")
    group.add_argument("--claude-manual", action="store_true", help="Print latest prompt path for manual paste into Claude Code.")
    group.add_argument("--claude-execute", action="store_true", help="Invoke Claude CLI automatically (blocked unless config allows).")
    group.add_argument("--browser-qa", action="store_true", help="Run browser QA against configured route_walk_urls.")

    args = parser.parse_args()

    if args.doctor:
        return run_doctor(args.project)
    if args.status:
        return run_status(args.project)
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
    return run_cycle(project_id=args.project, dry_run=args.dry_run, cycle=args.cycle)


if __name__ == "__main__":
    raise SystemExit(main())
