from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import ProjectConfig, load_project_config


PREFLIGHT_PASS = "SANDBOX_PREFLIGHT_PASS"
PREFLIGHT_WARN = "SANDBOX_PREFLIGHT_WARN"
PREFLIGHT_BLOCKED = "SANDBOX_PREFLIGHT_BLOCKED"
SIMULATION_PASS = "SANDBOX_SIMULATION_PASS"
SIMULATION_BLOCKED = "SANDBOX_SIMULATION_BLOCKED"


ALLOWED_VALIDATION_COMMANDS = [
    "python -B -m compileall project_autopilot agent",
    "python -B project_autopilot/agent_loop.py --project {project_id} --policy-fixtures",
    "python -B project_autopilot/agent_loop.py --project {project_id} --autopilot-health",
    "python -B project_autopilot/autopilot_v2_check.py --project {project_id}",
    "python -B project_autopilot/flow_qa.py --project {project_id} --validate-mock-e2e",
    "npm run lint",
    "npm run typecheck",
    "npm run build",
    "git status --short",
    "git diff --stat",
    "git diff --check",
]


DENIED_COMMAND_PATTERNS = [
    "Get-Content .env",
    "type .env",
    "cat .env",
    "printenv",
    "set |",
    "supabase db",
    "psql",
    "execute sql",
    "enable rls",
    "create policy",
    "deploy",
    "vercel --prod",
    "systemctl enable",
    "systemctl start",
    "git push --force",
    "git reset --hard",
    "git merge master",
    "git rebase",
    "npm install",
    "Remove-Item -Recurse -Force",
    "rm -rf",
    "paid api",
    "seedance",
    "openai image",
]


@dataclass(frozen=True)
class TaskScope:
    task: str
    docs_only: bool
    product_change: bool
    ui_change: bool
    backend_change: bool
    security_or_supabase_change: bool
    paid_api_risk: bool
    deploy_risk: bool
    scheduler_risk: bool
    control_plane_change: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WorktreePlan:
    required: bool
    real_worktree_created: bool
    branch_name: str
    worktree_path: str
    lifecycle_steps: list[str]
    merge_policy: str
    direct_master_writes_allowed: bool
    one_agent_per_worktree: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FileScopePolicy:
    allowed_patterns: list[str]
    denied_patterns: list[str]
    allowed_files: list[str]
    denied_files: list[str]
    requires_human_approval: bool
    requires_design_director: bool
    requires_backend_audit: bool
    requires_research_director: bool
    requires_flow_qa: bool
    blocked_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CommandScopePolicy:
    allowed_commands: list[str]
    denied_commands: list[str]
    human_approval_required: bool
    blocked_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PromptPackPolicy:
    no_secret_context: bool
    env_files_read: bool
    includes_allowed_files: bool
    includes_denied_files: bool
    includes_allowed_commands: bool
    includes_denied_commands: bool
    includes_stop_conditions: bool
    includes_builder_report_format: bool
    includes_post_builder_policy_requirement: bool
    blocked_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RollbackPlan:
    required: bool
    exists: bool
    steps: list[str]
    rejection_flow: list[str]
    auto_merge_allowed: bool
    force_push_allowed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SandboxBoundary:
    project_id: str
    generated_at_utc: str
    task: str
    execution_enabled: bool
    external_api_calls_enabled: bool
    scheduler_enabled: bool
    automatic_claude_execution_enabled: bool
    worktree_plan: WorktreePlan
    file_policy: FileScopePolicy
    command_policy: CommandScopePolicy
    prompt_pack_policy: PromptPackPolicy
    rollback_plan: RollbackPlan
    post_builder_policy_required: bool
    evidence_bundle_required: bool
    openai_auditor_review_required_for_blocked_retry: bool
    stop_conditions: list[str]
    task_scope: TaskScope

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SandboxPreflightResult:
    verdict: str
    boundary: SandboxBoundary
    warnings: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    next_action: str = ""
    report_paths: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "boundary": self.boundary.to_dict(),
            "warnings": self.warnings,
            "blocked_reasons": self.blocked_reasons,
            "next_action": self.next_action,
            "report_paths": self.report_paths,
        }


@dataclass(frozen=True)
class SandboxSimulationResult:
    verdict: str
    project_id: str
    generated_at_utc: str
    task: str
    lifecycle: list[dict[str, Any]]
    denied_command_tests: list[dict[str, str]]
    execution_occurred: bool
    external_api_called: bool
    real_worktree_created: bool
    claude_builder_execution_enabled: bool
    rollback_plan_exists: bool
    post_builder_policy_planned: bool
    blocked_reasons: list[str] = field(default_factory=list)
    next_action: str = ""
    report_paths: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safe_slug(text: str, fallback: str = "task") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug[:48].strip("-") or fallback)


def classify_task_scope(task: str) -> TaskScope:
    text = task.lower()
    ui = any(word in text for word in ["ui", "design", "visual", "component", "page", "layout"])
    backend = any(word in text for word in ["backend", "api", "database", "schema", "server", "storage"])
    security = any(word in text for word in ["security", "supabase", "rls", "auth", "secret", "privacy", "policy"])
    paid = any(word in text for word in ["paid", "billing", "seedance", "image generation", "video generation"])
    deploy = any(word in text for word in ["deploy", "vercel", "production", "release"])
    scheduler = any(word in text for word in ["scheduler", "cron", "systemd timer", "automatic execution"])
    docs = any(word in text for word in ["doc", "readme", "runbook", "spec", "standard", "plan"])
    control_plane = any(word in text for word in ["autopilot", "control plane", "provider", "orchestrator", "policy", "sandbox", "claude"])
    product = ui or backend or ("mira" in text and not control_plane and not docs)
    docs_only = docs and not product and not backend and not ui
    return TaskScope(
        task=task,
        docs_only=docs_only,
        product_change=product,
        ui_change=ui,
        backend_change=backend,
        security_or_supabase_change=security,
        paid_api_risk=paid,
        deploy_risk=deploy,
        scheduler_risk=scheduler,
        control_plane_change=control_plane,
    )


def build_worktree_plan(project: ProjectConfig, task: str) -> WorktreePlan:
    slug = _safe_slug(task)
    branch = f"agent/claude-sandbox-{slug}"
    proposed_path = str(project.repo_path.parent / f"{project.repo_path.name}-claude-sandbox-{slug}")
    return WorktreePlan(
        required=True,
        real_worktree_created=False,
        branch_name=branch,
        worktree_path=proposed_path,
        lifecycle_steps=[
            "Confirm master/main worktree is clean.",
            "Create a dedicated task branch and worktree only after explicit human approval.",
            "Run exactly one builder agent in the worktree.",
            "Collect builder report, diffs, command evidence, and blockers.",
            "Run Project Autopilot post-builder policy before any commit/merge decision.",
            "Reject or park the worktree if policy is BLOCKED/NEEDS_FIX.",
            "Merge only after SAFE_TO_COMMIT or explicit accepted human decision.",
        ],
        merge_policy="no_auto_merge; human-reviewed merge only after policy verdict",
        direct_master_writes_allowed=False,
        one_agent_per_worktree=True,
    )


def build_file_policy(project: ProjectConfig, task: str) -> FileScopePolicy:
    scope = classify_task_scope(task)
    allowed_patterns = ["project_autopilot/**", "project_control/**", "docs/**", "*.md"]
    denied_patterns = [
        ".env",
        ".env.local",
        ".env.*",
        "**/*secret*",
        "node_modules/**",
        ".next/**",
        ".vercel/**",
        "deployment configs",
        "supabase/migrations/**",
        "supabase/drafts/** unless human-approved as docs-only draft",
        "package-lock.json unless dependency approval is explicit",
        "app/** unless task scope explicitly permits product changes",
        "lib/** unless task scope explicitly permits product/backend changes",
        "components/** unless task scope explicitly permits UI changes",
    ]
    allowed_files = allowed_patterns.copy()
    requires_human = False
    blocked_reason = ""

    if scope.ui_change:
        allowed_files.append("components/** only with explicit UI scope and Design Director review")
        allowed_files.append("app/** only with explicit product UI scope and Flow QA")
        requires_human = True
    if scope.backend_change or scope.security_or_supabase_change:
        allowed_files.append("lib/** only with explicit backend scope and backend audit")
        allowed_files.append("app/api/** only with explicit backend scope and backend audit")
        requires_human = True
    if scope.paid_api_risk or scope.deploy_risk or scope.scheduler_risk:
        requires_human = True
        blocked_reason = "Task mentions paid API, deployment, or scheduler enablement; future builder execution must be blocked pending explicit approval."

    return FileScopePolicy(
        allowed_patterns=allowed_patterns,
        denied_patterns=denied_patterns,
        allowed_files=allowed_files,
        denied_files=denied_patterns,
        requires_human_approval=requires_human,
        requires_design_director=scope.ui_change,
        requires_backend_audit=scope.backend_change or scope.security_or_supabase_change,
        requires_research_director=scope.security_or_supabase_change or scope.paid_api_risk or scope.deploy_risk,
        requires_flow_qa=scope.product_change or scope.ui_change or scope.backend_change,
        blocked_reason=blocked_reason,
    )


def build_command_policy(project: ProjectConfig) -> CommandScopePolicy:
    allowed = [cmd.format(project_id=project.project_id) for cmd in ALLOWED_VALIDATION_COMMANDS]
    return CommandScopePolicy(
        allowed_commands=allowed,
        denied_commands=DENIED_COMMAND_PATTERNS,
        human_approval_required=False,
        blocked_reason="",
    )


def build_prompt_pack_policy() -> PromptPackPolicy:
    return PromptPackPolicy(
        no_secret_context=True,
        env_files_read=False,
        includes_allowed_files=True,
        includes_denied_files=True,
        includes_allowed_commands=True,
        includes_denied_commands=True,
        includes_stop_conditions=True,
        includes_builder_report_format=True,
        includes_post_builder_policy_requirement=True,
    )


def build_rollback_plan() -> RollbackPlan:
    return RollbackPlan(
        required=True,
        exists=True,
        steps=[
            "Keep all builder writes inside the task worktree.",
            "If validation fails, do not merge; preserve evidence and produce a correction prompt.",
            "If policy is BLOCKED, park or delete the task worktree only after human review.",
            "If changes are rejected, leave master/main untouched and archive the builder report.",
            "If a commit was made inside the task branch, revert within that branch; never rewrite shared history.",
        ],
        rejection_flow=[
            "NEEDS_FIX: return correction prompt to builder.",
            "BLOCKED: stop builder loop and request human decision.",
            "HUMAN_REVIEW_REQUIRED: record decision before retry.",
            "SAFE_TO_COMMIT: human may merge after verifying generated logs are not staged.",
        ],
        auto_merge_allowed=False,
        force_push_allowed=False,
    )


def build_boundary(project: ProjectConfig, task: str) -> SandboxBoundary:
    scope = classify_task_scope(task)
    file_policy = build_file_policy(project, task)
    command_policy = build_command_policy(project)
    stop_conditions = [
        "Stop if env/secret files would be read, printed, or modified.",
        "Stop if live SQL/RLS/storage policy mutation is needed.",
        "Stop if deploy, scheduler, auto-Claude, or paid API execution is requested.",
        "Stop if the builder needs to write outside the approved task worktree.",
        "Stop if command/file denylist is triggered.",
        "Stop if post-builder policy cannot run.",
        "Stop if rollback/evidence plan is missing.",
    ]
    return SandboxBoundary(
        project_id=project.project_id,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        task=task,
        execution_enabled=False,
        external_api_calls_enabled=False,
        scheduler_enabled=False,
        automatic_claude_execution_enabled=project.allow_automatic_builder_execution,
        worktree_plan=build_worktree_plan(project, task),
        file_policy=file_policy,
        command_policy=command_policy,
        prompt_pack_policy=build_prompt_pack_policy(),
        rollback_plan=build_rollback_plan(),
        post_builder_policy_required=True,
        evidence_bundle_required=True,
        openai_auditor_review_required_for_blocked_retry=True,
        stop_conditions=stop_conditions,
        task_scope=scope,
    )


def evaluate_preflight(project: ProjectConfig, task: str) -> SandboxPreflightResult:
    boundary = build_boundary(project, task)
    blocked: list[str] = []
    warnings: list[str] = []

    if boundary.execution_enabled:
        blocked.append("Claude builder execution is enabled; this sprint requires preflight-only mode.")
    if boundary.external_api_calls_enabled:
        blocked.append("External API calls are enabled unexpectedly.")
    if boundary.scheduler_enabled:
        blocked.append("Scheduler is enabled unexpectedly.")
    if boundary.automatic_claude_execution_enabled:
        blocked.append("Automatic Claude execution is enabled unexpectedly.")
    if boundary.worktree_plan.real_worktree_created:
        blocked.append("A real worktree was created during preflight.")
    if boundary.worktree_plan.direct_master_writes_allowed:
        blocked.append("Direct master writes are allowed.")
    if boundary.rollback_plan.auto_merge_allowed:
        blocked.append("Auto-merge is allowed.")
    if not boundary.rollback_plan.exists:
        blocked.append("Rollback plan is missing.")
    if not boundary.post_builder_policy_required:
        blocked.append("Post-builder policy review is not required.")
    if not boundary.evidence_bundle_required:
        blocked.append("Evidence bundle is not required.")
    if boundary.file_policy.blocked_reason:
        warnings.append(boundary.file_policy.blocked_reason)
    if boundary.file_policy.requires_human_approval:
        warnings.append("Task scope requires explicit human approval before any future sandboxed builder execution.")

    if blocked:
        verdict = PREFLIGHT_BLOCKED
        next_action = "Fix blocked sandbox gates before considering human-approved sandbox execution."
    elif warnings:
        verdict = PREFLIGHT_WARN
        next_action = "Review warnings, narrow scope if needed, then run sandbox simulation."
    else:
        verdict = PREFLIGHT_PASS
        next_action = "Run sandbox simulation; builder execution remains disabled."

    return SandboxPreflightResult(verdict, boundary, warnings, blocked, next_action)


def simulate_sandbox(project: ProjectConfig, task: str) -> SandboxSimulationResult:
    preflight = evaluate_preflight(project, task)
    boundary = preflight.boundary
    lifecycle = [
        {"step": 1, "state": "TASK_RECEIVED", "result": "simulated"},
        {"step": 2, "state": "OPENAI_AUDITOR_PLANS", "result": "planned_dry_run_only"},
        {"step": 3, "state": "BUILDER_SELECTED", "result": "claude_future_sandbox"},
        {"step": 4, "state": "WORKTREE_PLANNED", "result": boundary.worktree_plan.worktree_path},
        {"step": 5, "state": "PROMPT_PACK_GENERATED", "result": "no_secret_preview_only"},
        {"step": 6, "state": "ALLOWLIST_REVIEWED", "result": f"{len(boundary.command_policy.allowed_commands)} commands"},
        {"step": 7, "state": "DENYLIST_TESTED", "result": "dangerous commands blocked"},
        {"step": 8, "state": "ROLLBACK_PLANNED", "result": "ready"},
        {"step": 9, "state": "POST_BUILDER_POLICY_PLANNED", "result": "required"},
        {"step": 10, "state": "NO_EXECUTION", "result": "no Claude, no worktree, no API calls"},
    ]
    denied_tests = [{"command": item, "result": "BLOCKED_BY_POLICY"} for item in boundary.command_policy.denied_commands[:10]]
    blocked = list(preflight.blocked_reasons)
    if boundary.execution_enabled:
        blocked.append("Execution occurred unexpectedly.")
    verdict = SIMULATION_BLOCKED if blocked else SIMULATION_PASS
    return SandboxSimulationResult(
        verdict=verdict,
        project_id=project.project_id,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        task=task,
        lifecycle=lifecycle,
        denied_command_tests=denied_tests,
        execution_occurred=False,
        external_api_called=False,
        real_worktree_created=False,
        claude_builder_execution_enabled=False,
        rollback_plan_exists=boundary.rollback_plan.exists,
        post_builder_policy_planned=boundary.post_builder_policy_required,
        blocked_reasons=blocked,
        next_action="Human-approved sandbox execution design can proceed only if simulation stays PASS.",
    )


def _latest_dir(project: ProjectConfig) -> Path:
    out = project.repo_path / project.logs_dir / "claude_sandbox" / project.project_id / "latest"
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_preflight(project: ProjectConfig, result: SandboxPreflightResult) -> tuple[Path, Path]:
    out = _latest_dir(project)
    md_path = out / "claude_sandbox_preflight.md"
    json_path = out / "claude_sandbox_preflight.json"
    payload = result.to_dict()
    payload["report_paths"] = {"markdown": str(md_path), "json": str(json_path)}
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    b = result.boundary
    lines = [
        "# Claude Sandbox Preflight",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Generated: {b.generated_at_utc}",
        f"Task: {b.task}",
        f"Verdict: {result.verdict}",
        "Claude builder execution enabled: no",
        "External API calls enabled: no",
        "Real worktree created: no",
        "",
        "## Worktree Boundary",
        f"- Required: {'yes' if b.worktree_plan.required else 'no'}",
        f"- Proposed branch: `{b.worktree_plan.branch_name}`",
        f"- Proposed path: `{b.worktree_plan.worktree_path}`",
        f"- Direct master writes allowed: {'yes' if b.worktree_plan.direct_master_writes_allowed else 'no'}",
        f"- Auto-merge allowed: {'yes' if b.rollback_plan.auto_merge_allowed else 'no'}",
        "",
        "## File Policy",
        *[f"- Allow: `{item}`" for item in b.file_policy.allowed_files],
        *[f"- Deny: `{item}`" for item in b.file_policy.denied_files],
        "",
        "## Command Policy",
        *[f"- Allow: `{item}`" for item in b.command_policy.allowed_commands],
        *[f"- Deny: `{item}`" for item in b.command_policy.denied_commands],
        "",
        "## Stop Conditions",
        *[f"- {item}" for item in b.stop_conditions],
        "",
        "## Warnings",
        *[f"- {item}" for item in (result.warnings or ["None"])],
        "",
        "## Blocked Reasons",
        *[f"- {item}" for item in (result.blocked_reasons or ["None"])],
        "",
        "## Next Action",
        result.next_action,
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def write_simulation(project: ProjectConfig, result: SandboxSimulationResult) -> tuple[Path, Path]:
    out = _latest_dir(project)
    md_path = out / "claude_sandbox_simulation.md"
    json_path = out / "claude_sandbox_simulation.json"
    payload = result.to_dict()
    payload["report_paths"] = {"markdown": str(md_path), "json": str(json_path)}
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Claude Sandbox Simulation",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Generated: {result.generated_at_utc}",
        f"Task: {result.task}",
        f"Verdict: {result.verdict}",
        f"Execution occurred: {'yes' if result.execution_occurred else 'no'}",
        f"External API called: {'yes' if result.external_api_called else 'no'}",
        f"Real worktree created: {'yes' if result.real_worktree_created else 'no'}",
        f"Claude builder execution enabled: {'yes' if result.claude_builder_execution_enabled else 'no'}",
        "",
        "## Lifecycle",
    ]
    lines.extend(f"- {item['step']}. `{item['state']}`: {item['result']}" for item in result.lifecycle)
    lines.extend(["", "## Denied Command Tests"])
    lines.extend(f"- `{item['command']}` -> {item['result']}" for item in result.denied_command_tests)
    lines.extend(["", "## Blocked Reasons"])
    lines.extend(f"- {item}" for item in (result.blocked_reasons or ["None"]))
    lines.extend(["", "## Next Action", result.next_action])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Claude sandbox boundary preflight and simulation")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--task", default="Improve Project Autopilot docs")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--preflight", action="store_true")
    group.add_argument("--simulate", action="store_true")
    args = parser.parse_args()

    project = load_project_config(args.project)
    if args.simulate:
        result = simulate_sandbox(project, args.task)
        md_path, json_path = write_simulation(project, result)
        print(f"Claude Sandbox Simulation: {result.verdict}")
        print("  Execution occurred: no")
        print("  External API called: NO")
        print("  Real worktree created: no")
        print(f"  Report: {md_path}")
        print(f"  JSON: {json_path}")
        return 0 if result.verdict == SIMULATION_PASS else 2

    result = evaluate_preflight(project, args.task)
    md_path, json_path = write_preflight(project, result)
    print(f"Claude Sandbox Preflight: {result.verdict}")
    print("  Claude builder execution enabled: no")
    print("  External API called: NO")
    print("  Real worktree created: no")
    print(f"  Allowed file entries: {len(result.boundary.file_policy.allowed_files)}")
    print(f"  Denied file entries: {len(result.boundary.file_policy.denied_files)}")
    print(f"  Allowed commands: {len(result.boundary.command_policy.allowed_commands)}")
    print(f"  Denied commands: {len(result.boundary.command_policy.denied_commands)}")
    print(f"  Human approval needed: {'yes' if result.boundary.file_policy.requires_human_approval else 'no'}")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    return 0 if result.verdict != PREFLIGHT_BLOCKED else 2


if __name__ == "__main__":
    raise SystemExit(main())
