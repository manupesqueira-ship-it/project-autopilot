from __future__ import annotations

import argparse

from cost_controller import CostController
from evidence_collector import collect_evidence
from openai_supervisor import BudgetBlocked, MissingOpenAICredentials, OpenAIRequestError, OpenAISupervisor
from project_loader import ensure_project_dirs, load_project, read_project_control
from prompt_builder import build_builder_prompt
from qa_reviewer import generate_correction_prompt, review_with_openai
from state_manager import load_state, record_blocker, save_state, write_failure_log, write_iteration_log
from telegram_alerts import send_alert


def run(project_id: str, dry_run: bool = False, cycle: bool = False) -> int:
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
    except (MissingOpenAICredentials, BudgetBlocked) as exc:
        body = (
            "Status: open\nSeverity: blocking\nSource: Project Autopilot\n\n"
            f"Question or blocker:\n{exc}\n\n"
            "Recommended action:\nResolve the credential or budget issue, then rerun the supervised cycle."
        )
        record_blocker(project, f"Autopilot blocked: {type(exc).__name__}", body)
        alert = send_alert(project.project_id, type(exc).__name__, str(exc), enabled=project.telegram_enabled)
        print(f"Blocked: {exc}. Telegram: {alert.reason}")
        return 2
    except OpenAIRequestError as exc:
        recommendation = (
            "Check OpenAI API billing, quota, and rate limits. Try again later, "
            "or switch Project Autopilot to dry-run/low-cost mode until quota is available."
        )
        error = exc.as_dict()
        log_path = write_failure_log(
            project=project,
            title=exc.error_type,
            error=error,
            evidence=evidence,
            recommendation=recommendation,
        )
        body = (
            "Status: open\nSeverity: blocking\nSource: Project Autopilot\n\n"
            f"Question or blocker:\n{exc.error_type} ({exc.status_code})\n{exc.message}\n\n"
            f"Failure log:\n{log_path.relative_to(project.repo_path)}\n\n"
            f"Recommended action:\n{recommendation}"
        )
        record_blocker(project, f"Autopilot blocked: {exc.error_type}", body)
        alert = send_alert(project.project_id, exc.error_type, exc.message, enabled=project.telegram_enabled)
        state = load_state(project)
        state["last_status"] = "blocked"
        state["last_error"] = error
        state["last_log"] = str(log_path.relative_to(project.repo_path))
        save_state(project, state)
        print(f"Blocked: {exc.error_type} ({exc.status_code})")
        print(exc.message)
        print(f"Failure log: {log_path}")
        print(f"Telegram: {alert.reason}")
        print(f"Recommendation: {recommendation}")
        return 2

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
    state["last_builder_prompt"] = str((project.repo_path / project.logs_dir / f"{project.project_id}_latest_builder_prompt.md").relative_to(project.repo_path))
    save_state(project, state)

    print(f"Project: {project.project_name} ({project.project_id})")
    print(f"Generated builder prompt: {project.repo_path / project.logs_dir / f'{project.project_id}_latest_builder_prompt.md'}")
    print(f"Wrote iteration log: {log_path}")
    print("No builder work was executed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot agent loop.")
    parser.add_argument("--project", default="mira", help="Project id from project_autopilot/config/projects.")
    parser.add_argument("--dry-run", action="store_true", help="Skip OpenAI calls and validation commands.")
    parser.add_argument("--cycle", action="store_true", help="Run one bounded planning/QA cycle.")
    args = parser.parse_args()
    return run(project_id=args.project, dry_run=args.dry_run, cycle=args.cycle)


if __name__ == "__main__":
    raise SystemExit(main())
