from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import ProjectConfig, load_project_config
from providers.registry import discover_providers
from research_director import classify_research_need
from risk_classifier import classify_task


@dataclass
class BuilderPlan:
    task: str
    recommended_provider: str
    fallback_provider: str
    execution_mode: str
    live_call_required: bool = False
    explicit_approval_required: bool = False
    required_approvals: list[str] = field(default_factory=list)
    research_required: bool = False
    research_status: str = "NO_RESEARCH_REQUIRED"
    design_review_required: bool = False
    backend_security_review_required: bool = False
    flow_qa_required: bool = False
    risk_level: str = "low"
    risk_categories: list[str] = field(default_factory=list)
    stop_conditions: list[str] = field(default_factory=list)
    validation_commands: list[str] = field(default_factory=list)
    auto_commit_policy: str = "allowed_if_all_gates_pass"
    allowed_files: list[str] = field(default_factory=list)
    disallowed_files: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_ALLOWED = ["project_autopilot/**", "project_control/**"]
DEFAULT_DISALLOWED = [
    ".env",
    ".env.local",
    ".env.*",
    "deployment files",
    "git history",
    "live Supabase",
    "paid APIs",
]


def plan_task(project: ProjectConfig, task: str) -> BuilderPlan:
    assessment = classify_task(task)
    research_status, research_reasons = classify_research_need(task)
    text = task.lower()

    is_ui = any(word in text for word in ["ui", "design", "visual", "page", "component", "layout", "result page"])
    is_backend = any(word in text for word in ["backend", "supabase", "schema", "rls", "database", "auth", "security"])
    is_deploy = any(word in text for word in ["deploy", "production", "vercel"])
    is_paid = any(word in text for word in ["paid", "billing", "image generation", "video generation", "seedance"])
    is_refactor = any(word in text for word in ["refactor", "complex", "architecture", "migration"])
    is_docs = any(word in text for word in ["doc", "readme", "runbook", "spec"])
    is_high_level_objective = any(word in text for word in ["objective", "strategy", "roadmap", "loop", "orchestration", "autonomous", "sandboxed"])
    is_builder_blocked = any(word in text for word in ["builder blocked", "claude blocked", "blocked output", "diagnose blocker"])
    is_builder_done = any(word in text for word in ["builder done", "review builder output", "builder report", "review output"])
    is_claude_sdk_fit = any(
        phrase in text
        for phrase in [
            "review architecture",
            "architecture review",
            "codebase analysis",
            "design review assistance",
            "refactor planning",
            "claude sdk",
            "claude agent sdk",
        ]
    )

    provider = "codex"
    fallback = "claude_code"
    execution = "manual_handoff"
    approvals: list[str] = []
    stop: list[str] = [
        "Stop if secrets/env files would be touched.",
        "Stop if SQL/RLS/live database changes are needed.",
        "Stop if paid API calls are required.",
        "Stop if scheduler or automatic Claude execution would be enabled.",
    ]
    validations = ["python -B -m compileall project_autopilot agent", project.lint_command, project.typecheck_command, project.build_command]
    auto_commit = "allowed_if_all_gates_pass"
    allowed = DEFAULT_ALLOWED.copy()
    notes: list[str] = ["Project Autopilot plans and validates; it does not execute builders in this sprint."]
    live_call_required = False
    explicit_approval_required = False

    if is_high_level_objective or is_builder_blocked or is_builder_done:
        provider = "openai_auditor"
        fallback = "codex"
        execution = "dry_run_planning"
        auto_commit = "not_applicable_planning_only"
        notes.append("OpenAI Auditor should plan/review first; it does not build or approve its own output.")
        if is_builder_blocked:
            notes.append("Blocked builder output returns to OpenAI Auditor for diagnosis and correction prompt drafting.")
        if is_builder_done:
            notes.append("Completed builder output returns to OpenAI Auditor for evidence review before Project Autopilot policy gates.")

    if is_ui:
        validations.append("python -B project_autopilot/design_director.py --project mira")
        validations.append("python -B project_autopilot/flow_qa.py --project mira --validate-mock-e2e")
        allowed.extend(["app/**", "components/**"])
        notes.append("UI/design changes require Design Director and Flow QA.")

    if is_backend:
        validations.append("python -B project_autopilot/agent_loop.py --project mira --backend-audit")
        approvals.append("human approval for live DB/RLS/storage changes")
        auto_commit = "no_auto_commit_for_live_db_or_security_changes"
        notes.append("Backend/security changes require backend audit and may require research.")

    if is_refactor:
        provider = "claude_code" if not (is_high_level_objective or is_builder_blocked or is_builder_done) else provider
        fallback = "codex"
        auto_commit = "manual_review_recommended_for_complex_refactor"
        notes.append("Complex refactors may fit Claude Code manual handoff, with Codex QA fallback.")

    if is_claude_sdk_fit and not is_docs:
        provider = "claude_agent_sdk" if not is_high_level_objective else provider
        fallback = "codex"
        execution = "dry_run_only" if provider == "claude_agent_sdk" else execution
        explicit_approval_required = True
        approvals.append("explicit human approval before any live Claude Agent SDK call")
        auto_commit = "manual_review_required_before_live_claude_sdk_use"
        notes.append("Claude Agent SDK is dry-run only; OpenAI Auditor may prepare prompts/reviews but no live builder call is made.")

    if is_claude_sdk_fit and is_backend:
        provider = "claude_agent_sdk"
        fallback = "codex"
        execution = "dry_run_only"
        explicit_approval_required = True
        approvals.append("explicit human approval for backend/security analysis scope")
        notes.append("Backend/security work routed to Claude SDK only as a future dry-run analysis candidate.")

    if is_paid:
        approvals.append("budget approval")
        approvals.append("paid API approval")
        auto_commit = "mock_or_stub_only_without_paid_api_approval"
        stop.append("Real paid provider calls are blocked.")

    if is_deploy:
        approvals.append("deployment approval")
        auto_commit = "blocked_until_deploy_mode_enabled"
        stop.append("Deployment is blocked until deploy mode is explicitly enabled.")

    if is_docs and not (is_ui or is_backend or is_paid or is_deploy):
        validations = ["python -B -m compileall project_autopilot agent", project.lint_command, project.typecheck_command, project.build_command]
        notes.append("Docs/control-plane updates can use Codex and may auto-commit if gates pass.")

    validations = [cmd for cmd in validations if cmd]

    return BuilderPlan(
        task=task,
        recommended_provider=provider,
        fallback_provider=fallback,
        execution_mode=execution,
        live_call_required=live_call_required,
        explicit_approval_required=explicit_approval_required,
        required_approvals=sorted(set(approvals)),
        research_required=research_status in {"RESEARCH_REQUIRED", "DECISION_BLOCKED_RESEARCH_REQUIRED"},
        research_status=research_status,
        design_review_required=is_ui,
        backend_security_review_required=is_backend,
        flow_qa_required=is_ui or "flow" in text,
        risk_level=assessment.risk_level,
        risk_categories=assessment.categories,
        stop_conditions=stop,
        validation_commands=validations,
        auto_commit_policy=auto_commit,
        allowed_files=sorted(set(allowed)),
        disallowed_files=DEFAULT_DISALLOWED,
        notes=notes + [f"Research triggers: {', '.join(research_reasons) if research_reasons else 'none'}"],
    )


def status(project: ProjectConfig) -> dict[str, Any]:
    providers = [p.to_dict() for p in discover_providers(project)]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        "primary_builder": project.builder_primary,
        "fallback_builder": project.builder_fallback,
        "automatic_builder_execution": project.allow_automatic_builder_execution,
        "scheduler_enabled": False,
        "paid_api_mode": project.paid_api_mode,
        "providers": providers,
        "status": "READY_FOR_MANUAL_ORCHESTRATION",
    }


def write_status(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    logs = project.repo_path / project.logs_dir
    logs.mkdir(parents=True, exist_ok=True)
    json_path = logs / f"{project.project_id}_builder_orchestrator_latest.json"
    md_path = logs / f"{project.project_id}_builder_orchestrator_latest.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Builder Orchestrator Status",
        "",
        f"Status: {payload['status']}",
        f"Primary builder: {payload['primary_builder']}",
        f"Fallback builder: {payload['fallback_builder']}",
        f"Automatic builder execution: {payload['automatic_builder_execution']}",
        f"Scheduler enabled: {payload['scheduler_enabled']}",
        f"Paid API mode: {payload['paid_api_mode']}",
        "",
        "No builders are executed by this module.",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def write_plan(project: ProjectConfig, plan: BuilderPlan) -> tuple[Path, Path]:
    logs = project.repo_path / project.logs_dir
    logs.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(ch if ch.isalnum() else "_" for ch in plan.task.lower())[:60].strip("_") or "task"
    json_path = logs / f"{project.project_id}_builder_orchestrator_plan_{safe_name}.json"
    md_path = logs / f"{project.project_id}_builder_orchestrator_plan_latest.md"
    payload = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "project_id": project.project_id, **plan.to_dict()}
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Builder Orchestrator Plan",
        "",
        f"Task: {plan.task}",
        f"Recommended provider: {plan.recommended_provider}",
        f"Fallback provider: {plan.fallback_provider}",
        f"Execution mode: {plan.execution_mode}",
        f"Live call required: {plan.live_call_required}",
        f"Explicit approval required: {plan.explicit_approval_required}",
        f"Risk: {plan.risk_level} ({', '.join(plan.risk_categories)})",
        f"Research: {plan.research_status}",
        f"Design review required: {plan.design_review_required}",
        f"Backend/security review required: {plan.backend_security_review_required}",
        f"Flow QA required: {plan.flow_qa_required}",
        f"Auto-commit policy: {plan.auto_commit_policy}",
        "",
        "## Required Approvals",
        *[f"- {item}" for item in plan.required_approvals or ["None"]],
        "",
        "## Stop Conditions",
        *[f"- {item}" for item in plan.stop_conditions],
        "",
        "## Validation Commands",
        *[f"- `{cmd}`" for cmd in plan.validation_commands],
        "",
        "## Notes",
        *[f"- {item}" for item in plan.notes],
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot Builder Orchestrator")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--plan", help="Plan routing for a task without executing it")
    args = parser.parse_args()

    project = load_project_config(args.project)
    if args.plan:
        plan = plan_task(project, args.plan)
        md_path, json_path = write_plan(project, plan)
        print(f"Builder Orchestrator Plan: {plan.task}")
        print(f"  Provider: {plan.recommended_provider} (fallback: {plan.fallback_provider})")
        print(f"  Mode: {plan.execution_mode}")
        print(f"  Live call required: {plan.live_call_required}")
        print(f"  Explicit approval required: {plan.explicit_approval_required}")
        print(f"  Risk: {plan.risk_level}")
        print(f"  Research: {plan.research_status}")
        print(f"  Design review: {'yes' if plan.design_review_required else 'no'}")
        print(f"  Backend/security review: {'yes' if plan.backend_security_review_required else 'no'}")
        print(f"  Flow QA: {'yes' if plan.flow_qa_required else 'no'}")
        print(f"  Auto-commit: {plan.auto_commit_policy}")
        print(f"  Report: {md_path}")
        print(f"  JSON: {json_path}")
        return 0

    payload = status(project)
    md_path, json_path = write_status(project, payload)
    print(f"Builder Orchestrator: {payload['status']}")
    print(f"  Primary: {payload['primary_builder']}")
    print(f"  Fallback: {payload['fallback_builder']}")
    print(f"  Automatic execution: {payload['automatic_builder_execution']}")
    print(f"  Scheduler enabled: {payload['scheduler_enabled']}")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
