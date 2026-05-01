from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claude_sandbox_boundary import evaluate_preflight
from config import ProjectConfig, load_project_config


APPROVAL_NOT_REQUESTED = "APPROVAL_NOT_REQUESTED"
APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
APPROVED_FOR_DRY_RUN_ONLY = "APPROVED_FOR_DRY_RUN_ONLY"
APPROVED_FOR_WORKTREE_CREATION_FUTURE = "APPROVED_FOR_WORKTREE_CREATION_FUTURE"
APPROVED_FOR_BUILDER_EXECUTION_FUTURE = "APPROVED_FOR_BUILDER_EXECUTION_FUTURE"
REJECTED = "REJECTED"
EXPIRED = "EXPIRED"
INVALID = "INVALID"

VALID_APPROVAL_STATUSES = {
    APPROVAL_NOT_REQUESTED,
    APPROVAL_REQUESTED,
    APPROVED_FOR_DRY_RUN_ONLY,
    APPROVED_FOR_WORKTREE_CREATION_FUTURE,
    APPROVED_FOR_BUILDER_EXECUTION_FUTURE,
    REJECTED,
    EXPIRED,
    INVALID,
}


@dataclass(frozen=True)
class SandboxApprovalRequest:
    project_id: str
    task_id: str
    task_summary: str
    requested_provider: str
    requested_execution_mode: str
    requested_at_utc: str
    approval_scope: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SandboxApprovalDecision:
    status: str
    human_approver: str
    approval_timestamp: str
    expiration_timestamp: str
    decision_notes: str
    future_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SandboxApprovalStatus:
    status: str
    allows_dry_run: bool
    allows_worktree_creation_now: bool
    allows_builder_execution_now: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SandboxApprovalContract:
    project_id: str
    task_id: str
    task_summary: str
    requested_provider: str
    requested_execution_mode: str
    allowed_files: list[str]
    denied_files: list[str]
    allowed_commands: list[str]
    denied_commands: list[str]
    max_runtime_minutes: int
    max_command_count: int
    max_file_edits: int
    requires_no_secrets: bool
    requires_no_sql: bool
    requires_no_deploy: bool
    requires_no_paid_api: bool
    requires_post_builder_policy: bool
    requires_openai_auditor_review: bool
    requires_rollback_plan: bool
    human_approver: str
    approval_timestamp: str
    expiration_timestamp: str
    approval_scope: str
    approval_status: str
    explicit_forbidden_actions: list[str]
    future_only: bool
    worktree_creation_enabled_now: bool
    builder_execution_enabled_now: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ApprovalValidationResult:
    valid: bool
    status: str
    blocked_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _task_id(task: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in task).strip("-")
    slug = "-".join(part for part in slug.split("-") if part)
    return f"claude-sandbox-{slug[:48] or 'task'}"


def build_approval_request(project: ProjectConfig, task: str) -> SandboxApprovalRequest:
    return SandboxApprovalRequest(
        project_id=project.project_id,
        task_id=_task_id(task),
        task_summary=task,
        requested_provider="claude_agent_sdk",
        requested_execution_mode="human_approved_sandbox_future",
        requested_at_utc=_now().isoformat(),
        approval_scope="dry_run_interface_only_this_sprint",
    )


def build_contract_preview(
    project: ProjectConfig,
    task: str,
    status: str = APPROVED_FOR_DRY_RUN_ONLY,
    human_approver: str = "human_required_before_future_execution",
) -> SandboxApprovalContract:
    preflight = evaluate_preflight(project, task)
    boundary = preflight.boundary
    now = _now()
    expires = now + timedelta(hours=24)
    return SandboxApprovalContract(
        project_id=project.project_id,
        task_id=_task_id(task),
        task_summary=task,
        requested_provider="claude_agent_sdk",
        requested_execution_mode="human_approved_sandbox_future",
        allowed_files=boundary.file_policy.allowed_files,
        denied_files=boundary.file_policy.denied_files,
        allowed_commands=boundary.command_policy.allowed_commands,
        denied_commands=boundary.command_policy.denied_commands,
        max_runtime_minutes=45,
        max_command_count=20,
        max_file_edits=25,
        requires_no_secrets=True,
        requires_no_sql=True,
        requires_no_deploy=True,
        requires_no_paid_api=True,
        requires_post_builder_policy=True,
        requires_openai_auditor_review=True,
        requires_rollback_plan=True,
        human_approver=human_approver,
        approval_timestamp=now.isoformat(),
        expiration_timestamp=expires.isoformat(),
        approval_scope="dry_run_only; worktree_creation_and_builder_execution_are_future_only",
        approval_status=status,
        explicit_forbidden_actions=[
            "read_or_modify_env_files",
            "print_secret_values",
            "call_anthropic_or_openai_from_runner",
            "execute_claude_builder",
            "create_real_worktree_this_sprint",
            "write_directly_to_master",
            "auto_merge",
            "force_push",
            "execute_sql_or_enable_rls",
            "deploy",
            "call_paid_apis",
            "enable_scheduler",
            "enable_automatic_claude_execution",
        ],
        future_only=True,
        worktree_creation_enabled_now=False,
        builder_execution_enabled_now=False,
    )


def validate_contract(contract: SandboxApprovalContract) -> ApprovalValidationResult:
    blocked: list[str] = []
    warnings: list[str] = []
    if contract.approval_status not in VALID_APPROVAL_STATUSES:
        blocked.append("Approval status is invalid.")
    if not contract.requires_no_secrets:
        blocked.append("Approval contract does not require no-secret execution.")
    if not contract.requires_no_sql:
        blocked.append("Approval contract does not block SQL/RLS.")
    if not contract.requires_no_deploy:
        blocked.append("Approval contract does not block deployment.")
    if not contract.requires_no_paid_api:
        blocked.append("Approval contract does not block paid APIs.")
    if not contract.requires_post_builder_policy:
        blocked.append("Approval contract does not require post-builder policy.")
    if not contract.requires_openai_auditor_review:
        blocked.append("Approval contract does not require OpenAI Auditor review.")
    if not contract.requires_rollback_plan:
        blocked.append("Approval contract does not require rollback plan.")
    if not contract.allowed_files:
        blocked.append("Approval contract missing file allowlist.")
    if not contract.denied_files:
        blocked.append("Approval contract missing file denylist.")
    if not contract.allowed_commands:
        blocked.append("Approval contract missing command allowlist.")
    if not contract.denied_commands:
        blocked.append("Approval contract missing command denylist.")
    if contract.worktree_creation_enabled_now:
        blocked.append("Worktree creation is enabled now; this sprint must keep it disabled.")
    if contract.builder_execution_enabled_now:
        blocked.append("Builder execution is enabled now; this sprint must keep it disabled.")
    if not contract.future_only:
        blocked.append("Approval contract is not marked future-only.")

    if contract.approval_status == APPROVAL_NOT_REQUESTED:
        warnings.append("Approval has not been requested; dry-run only.")
    elif contract.approval_status in {APPROVED_FOR_WORKTREE_CREATION_FUTURE, APPROVED_FOR_BUILDER_EXECUTION_FUTURE}:
        warnings.append("Approval status is future-only and cannot execute in this sprint.")
    elif contract.approval_status in {REJECTED, EXPIRED, INVALID}:
        blocked.append(f"Approval status is {contract.approval_status}.")

    try:
        expires = datetime.fromisoformat(contract.expiration_timestamp)
        if expires < _now():
            blocked.append("Approval contract has expired.")
    except ValueError:
        blocked.append("Approval expiration timestamp is invalid.")

    valid = not blocked
    return ApprovalValidationResult(
        valid=valid,
        status="APPROVAL_VALIDATED_DRY_RUN_ONLY" if valid else "APPROVAL_INVALID",
        blocked_reasons=blocked,
        warnings=warnings,
        next_action="Use this contract as a preview only; future worktree creation requires a separate human-approved sprint."
        if valid
        else "Fix approval contract blockers before any future sandbox execution planning.",
    )


def approval_status_from_contract(contract: SandboxApprovalContract) -> SandboxApprovalStatus:
    validation = validate_contract(contract)
    if not validation.valid:
        return SandboxApprovalStatus(
            status=INVALID,
            allows_dry_run=False,
            allows_worktree_creation_now=False,
            allows_builder_execution_now=False,
            reason="Approval contract failed validation.",
        )
    return SandboxApprovalStatus(
        status=contract.approval_status,
        allows_dry_run=contract.approval_status in {
            APPROVED_FOR_DRY_RUN_ONLY,
            APPROVED_FOR_WORKTREE_CREATION_FUTURE,
            APPROVED_FOR_BUILDER_EXECUTION_FUTURE,
        },
        allows_worktree_creation_now=False,
        allows_builder_execution_now=False,
        reason="All approvals are dry-run/future-only in this sprint.",
    )


def write_contract_preview(project: ProjectConfig, contract: SandboxApprovalContract) -> Path:
    out = project.repo_path / project.logs_dir / "claude_sandbox" / project.project_id / "latest"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "claude_sandbox_approval_contract_preview.json"
    path.write_text(json.dumps(contract.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Claude sandbox approval contract preview")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--task", default="Improve Project Autopilot docs")
    args = parser.parse_args()

    project = load_project_config(args.project)
    contract = build_contract_preview(project, args.task)
    validation = validate_contract(contract)
    path = write_contract_preview(project, contract)
    print(f"Claude Sandbox Approval Contract: {validation.status}")
    print(f"  Approval status: {contract.approval_status}")
    print("  Worktree creation enabled now: no")
    print("  Builder execution enabled now: no")
    print(f"  Contract: {path}")
    print(f"  Next action: {validation.next_action}")
    return 0 if validation.valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
