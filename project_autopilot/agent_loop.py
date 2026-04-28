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
from cost_controller import CostController
from evidence_collector import collect_evidence
from evidence_bundle import create_evidence_bundle
from local_planner import _pick_next_task, generate_local_plan
from openai_supervisor import BudgetBlocked, MissingOpenAICredentials, OpenAIRequestError, OpenAISupervisor
from project_loader import ensure_project_dirs, load_project, read_project_control
from prompt_builder import build_builder_prompt
from qa_reviewer import generate_correction_prompt, review_with_openai
from state_manager import load_state, record_blocker, save_state, write_failure_log, write_iteration_log
from task_state import load_task_state, transition_task_state
from browser_qa import run_browser_qa, write_browser_qa_report
from claude_runner import detect_claude_cli, handoff_execute, handoff_manual, resolve_prompt_path
from telegram_alerts import send_alert
from risk_classifier import classify_task, format_risk_assessment


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
    bundle_path = create_evidence_bundle(
        project=project,
        evidence=evidence,
        task_plan=task_plan,
        builder_prompt=builder_prompt,
        qa_review=qa_review,
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
    transition_task_state(project, "planned", "Project Autopilot generated a builder prompt.")

    print(f"Project: {project.project_name} ({project.project_id})")
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
    bundle_path = create_evidence_bundle(
        project=project,
        evidence=evidence,
        task_plan="LOCAL FALLBACK PLAN",
        builder_prompt=fallback,
        qa_review="Local fallback plan generated without OpenAI QA.",
    )

    # 5. Update state
    state = load_state(project)
    state["last_status"] = "blocked_with_fallback"
    state["last_error"] = error_dict
    state["last_log"] = str(log_path.relative_to(project.repo_path))
    state["last_builder_prompt"] = str(fallback_path.relative_to(project.repo_path))
    state["last_evidence_bundle"] = str(bundle_path.relative_to(project.repo_path))
    save_state(project, state)
    transition_task_state(project, "blocked", f"Project Autopilot blocked on {error_type}.")

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
    ensure_project_dirs(project)

    control_docs = read_project_control(project)
    evidence = collect_evidence(project, dry_run=False)

    fallback = generate_local_plan(project, control_docs, evidence)
    prompt_path = project.repo_path / project.logs_dir / f"{project.project_id}_latest_builder_prompt.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(fallback, encoding="utf-8")
    bundle_path = create_evidence_bundle(
        project=project,
        evidence=evidence,
        task_plan="LOCAL PLAN",
        builder_prompt=fallback,
        qa_review="Local plan mode does not call OpenAI QA.",
    )

    state = load_state(project)
    state["cycles"] = int(state.get("cycles", 0)) + 1
    state["last_status"] = "local_plan"
    state["last_builder_prompt"] = str(prompt_path.relative_to(project.repo_path))
    state["last_evidence_bundle"] = str(bundle_path.relative_to(project.repo_path))
    save_state(project, state)
    transition_task_state(project, "planned", "Local planner generated a builder prompt.")

    print(f"Project: {project.project_name} ({project.project_id})")
    print(f"Local fallback plan written to: {prompt_path}")
    print(f"Evidence bundle: {bundle_path}")
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
    task_state = load_task_state(project)
    print(f"Task state:         {task_state.get('state', 'unknown')}")
    last_log = state.get("last_log")
    if last_log:
        print(f"Last log:           {last_log}")
    last_prompt = state.get("last_builder_prompt")
    if last_prompt:
        print(f"Last builder prompt:{last_prompt}")
    last_bundle = state.get("last_evidence_bundle")
    if last_bundle:
        print(f"Evidence bundle:    {last_bundle}")
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

    control_docs = read_project_control(project)
    task_queue = control_docs.get("TASK_QUEUE.md", "")
    title, body = _pick_next_task(task_queue)
    risk = classify_task(title or "Current task queue", body or task_queue, [], control_docs)
    print()
    print("Risk summary:")
    print(format_risk_assessment(risk))

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

    severity_rank = {"pass": 0, "warn": 1, "fail": 2}
    for item in sorted(issues, key=lambda issue: (severity_rank[issue.severity], issue.code)):
        print(f"{item.severity.upper():4} {item.code}: {item.message}")
        if item.severity != "pass":
            print(f"     Recommendation: {item.recommendation}")

    result_severity = worst_severity(issues)
    result_label = result_severity.upper()
    print()
    print(f"DOCTOR_RESULT: {result_label}")
    return 2 if result_severity == "fail" else 0


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
