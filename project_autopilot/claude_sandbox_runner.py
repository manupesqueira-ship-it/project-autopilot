from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claude_prompt_pack import build_prompt_pack, write_prompt_pack
from claude_sandbox_approval import (
    APPROVED_FOR_DRY_RUN_ONLY,
    SandboxApprovalContract,
    build_approval_request,
    build_contract_preview,
    validate_contract,
    write_contract_preview,
)
from claude_sandbox_boundary import evaluate_preflight, simulate_sandbox, write_preflight, write_simulation
from config import ProjectConfig, load_project_config
from worktree_sandbox import build_worktree_sandbox_plan, write_worktree_sandbox_plan


RUNNER_DISABLED = "RUNNER_DISABLED"
APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
APPROVAL_VALIDATED_DRY_RUN_ONLY = "APPROVAL_VALIDATED_DRY_RUN_ONLY"
WORKTREE_CREATION_BLOCKED_THIS_SPRINT = "WORKTREE_CREATION_BLOCKED_THIS_SPRINT"
BUILDER_EXECUTION_BLOCKED_THIS_SPRINT = "BUILDER_EXECUTION_BLOCKED_THIS_SPRINT"
READY_FOR_FUTURE_HUMAN_APPROVED_WORKTREE = "READY_FOR_FUTURE_HUMAN_APPROVED_WORKTREE"
REJECTED = "REJECTED"
BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class RunnerState:
    state: str
    approval_status: str
    dry_run_result: str
    worktree_creation_enabled: bool
    builder_execution_enabled: bool
    external_api_called: bool
    real_worktree_created: bool
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunnerPlan:
    project_id: str
    generated_at_utc: str
    task: str
    runner_state: RunnerState
    approval_contract: dict[str, Any]
    approval_validation: dict[str, Any]
    sandbox_preflight_verdict: str
    sandbox_simulation_verdict: str
    prompt_pack_path: str
    worktree_plan_path: str
    approval_contract_path: str
    rollback_checklist: list[str]
    rejection_checklist: list[str]
    cancellation_checklist: list[str]
    evidence_preservation_checklist: list[str]
    report_paths: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _latest_dir(project: ProjectConfig) -> Path:
    out = project.repo_path / project.logs_dir / "claude_sandbox" / project.project_id / "latest"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def rollback_checklist() -> list[str]:
    return [
        "Do not merge failed or blocked work.",
        "Preserve builder report, git status, diff stat, command results, and policy report.",
        "If a future worktree exists, leave it parked until human review.",
        "If a future branch commit exists, revert within the branch; do not rewrite shared history.",
        "Record blocker or human decision before retry.",
    ]


def rejection_checklist() -> list[str]:
    return [
        "Mark approval as rejected.",
        "Do not create or reuse a worktree.",
        "Do not execute Claude.",
        "Generate a correction or scope-reduction prompt for OpenAI Auditor/Codex.",
        "Keep generated evidence ignored and unstaged.",
    ]


def cancellation_checklist() -> list[str]:
    return [
        "Cancel runner plan before any execution.",
        "Confirm no real worktree was created.",
        "Confirm no external API call occurred.",
        "Confirm scheduler and automatic Claude execution remain disabled.",
        "Preserve approval preview and runner plan for audit.",
    ]


def evidence_preservation_checklist(project: ProjectConfig) -> list[str]:
    return [
        f"logs/claude_sandbox/{project.project_id}/latest/claude_sandbox_runner_plan.md",
        f"logs/claude_sandbox/{project.project_id}/latest/claude_sandbox_runner_plan.json",
        f"logs/claude_sandbox/{project.project_id}/latest/claude_sandbox_approval_contract_preview.json",
        f"logs/claude_sandbox/{project.project_id}/latest/claude_sandbox_preflight.md",
        f"logs/claude_sandbox/{project.project_id}/latest/claude_sandbox_simulation.md",
        f"logs/claude_sandbox/{project.project_id}/latest/claude_prompt_pack_preview.md",
        f"logs/claude_sandbox/{project.project_id}/latest/worktree_sandbox_plan.md",
    ]


def build_runner_plan(project: ProjectConfig, task: str, mode: str = "dry_run") -> RunnerPlan:
    preflight = evaluate_preflight(project, task)
    preflight_md, preflight_json = write_preflight(project, preflight)
    simulation = simulate_sandbox(project, task)
    simulation_md, simulation_json = write_simulation(project, simulation)
    prompt_pack = build_prompt_pack(project, task)
    prompt_md, prompt_json = write_prompt_pack(project, prompt_pack)
    worktree_plan = build_worktree_sandbox_plan(project, task)
    worktree_md, worktree_json = write_worktree_sandbox_plan(project, worktree_plan)
    contract = build_contract_preview(project, task, status=APPROVED_FOR_DRY_RUN_ONLY)
    validation = validate_contract(contract)
    contract_path = write_contract_preview(project, contract)

    if not validation.valid or preflight.verdict == "SANDBOX_PREFLIGHT_BLOCKED" or simulation.verdict == "SANDBOX_SIMULATION_BLOCKED":
        state = BLOCKED
        next_action = "Resolve approval/preflight/simulation blockers before any future runner work."
    elif mode == "approval_preflight":
        state = APPROVAL_VALIDATED_DRY_RUN_ONLY
        next_action = "Approval contract preview is valid for dry-run only; worktree creation remains blocked this sprint."
    elif mode == "status":
        state = RUNNER_DISABLED
        next_action = "Run approval preflight or runner dry-run; execution remains disabled."
    else:
        state = READY_FOR_FUTURE_HUMAN_APPROVED_WORKTREE
        next_action = "Future worktree creation can be designed in a later human-approved sprint; do not create it now."

    runner_state = RunnerState(
        state=state,
        approval_status=contract.approval_status,
        dry_run_result="RUNNER_DRY_RUN_PASS" if validation.valid else "RUNNER_DRY_RUN_BLOCKED",
        worktree_creation_enabled=False,
        builder_execution_enabled=False,
        external_api_called=False,
        real_worktree_created=False,
        next_action=next_action,
    )
    return RunnerPlan(
        project_id=project.project_id,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        task=task,
        runner_state=runner_state,
        approval_contract=contract.to_dict(),
        approval_validation=validation.to_dict(),
        sandbox_preflight_verdict=preflight.verdict,
        sandbox_simulation_verdict=simulation.verdict,
        prompt_pack_path=str(prompt_md),
        worktree_plan_path=str(worktree_md),
        approval_contract_path=str(contract_path),
        rollback_checklist=rollback_checklist(),
        rejection_checklist=rejection_checklist(),
        cancellation_checklist=cancellation_checklist(),
        evidence_preservation_checklist=evidence_preservation_checklist(project),
        report_paths={
            "preflight_md": str(preflight_md),
            "preflight_json": str(preflight_json),
            "simulation_md": str(simulation_md),
            "simulation_json": str(simulation_json),
            "prompt_pack_md": str(prompt_md),
            "prompt_pack_json": str(prompt_json),
            "worktree_plan_md": str(worktree_md),
            "worktree_plan_json": str(worktree_json),
            "approval_contract_json": str(contract_path),
        },
    )


def write_runner_plan(project: ProjectConfig, plan: RunnerPlan) -> tuple[Path, Path]:
    out = _latest_dir(project)
    md_path = out / "claude_sandbox_runner_plan.md"
    json_path = out / "claude_sandbox_runner_plan.json"
    payload = plan.to_dict()
    payload["report_paths"]["runner_md"] = str(md_path)
    payload["report_paths"]["runner_json"] = str(json_path)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Claude Sandbox Runner Plan",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Generated: {plan.generated_at_utc}",
        f"Task: {plan.task}",
        f"Runner state: {plan.runner_state.state}",
        f"Approval status: {plan.runner_state.approval_status}",
        f"Dry-run result: {plan.runner_state.dry_run_result}",
        "Worktree creation enabled: no",
        "Builder execution enabled: no",
        "External API called: no",
        "Real worktree created: no",
        "",
        "## Gate Results",
        f"- Sandbox preflight: {plan.sandbox_preflight_verdict}",
        f"- Sandbox simulation: {plan.sandbox_simulation_verdict}",
        f"- Approval validation: {plan.approval_validation.get('status', 'UNKNOWN')}",
        "",
        "## Approval Contract",
        f"- Contract: `{plan.approval_contract_path}`",
        f"- Scope: {plan.approval_contract.get('approval_scope')}",
        f"- Future-only: {'yes' if plan.approval_contract.get('future_only') else 'no'}",
        "",
        "## Rollback Checklist",
        *[f"- {item}" for item in plan.rollback_checklist],
        "",
        "## Rejection Checklist",
        *[f"- {item}" for item in plan.rejection_checklist],
        "",
        "## Cancellation Checklist",
        *[f"- {item}" for item in plan.cancellation_checklist],
        "",
        "## Evidence Preservation",
        *[f"- `{item}`" for item in plan.evidence_preservation_checklist],
        "",
        "## Next Action",
        plan.runner_state.next_action,
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def status_payload(project: ProjectConfig) -> dict[str, Any]:
    base = _latest_dir(project)
    latest = _read_json(base / "claude_sandbox_runner_plan.json")
    contract = _read_json(base / "claude_sandbox_approval_contract_preview.json")
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        "runner_interface": "AVAILABLE",
        "runner_state": latest.get("runner_state", {}).get("state", RUNNER_DISABLED),
        "approval_status": contract.get("approval_status", "APPROVAL_NOT_REQUESTED"),
        "worktree_creation_enabled": False,
        "builder_execution_enabled": False,
        "external_api_called": False,
        "real_worktree_created": False,
        "latest_runner_plan": str(base / "claude_sandbox_runner_plan.md"),
        "latest_runner_plan_json": str(base / "claude_sandbox_runner_plan.json"),
        "approval_contract_preview": str(base / "claude_sandbox_approval_contract_preview.json"),
        "next_action": "Run --approval-preflight or --dry-run. Future execution remains disabled.",
    }


def write_status(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    out = _latest_dir(project)
    md_path = out / "claude_sandbox_runner_status.md"
    json_path = out / "claude_sandbox_runner_status.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Claude Sandbox Runner Status",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Runner interface: {payload['runner_interface']}",
        f"Runner state: {payload['runner_state']}",
        f"Approval status: {payload['approval_status']}",
        "Worktree creation enabled: no",
        "Builder execution enabled: no",
        "External API called: no",
        "Real worktree created: no",
        "",
        "## Evidence",
        f"- Runner plan: `{payload['latest_runner_plan']}`",
        f"- Approval contract preview: `{payload['approval_contract_preview']}`",
        "",
        "## Next Action",
        payload["next_action"],
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Human-approved Claude sandbox runner interface")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--task", default="Improve Project Autopilot docs")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--status", action="store_true")
    group.add_argument("--approval-preflight", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--rollback-plan", action="store_true")
    args = parser.parse_args()

    project = load_project_config(args.project)
    if args.status:
        payload = status_payload(project)
        md_path, json_path = write_status(project, payload)
        print(f"Claude Sandbox Runner: {payload['runner_state']}")
        print(f"  Approval status: {payload['approval_status']}")
        print("  Worktree creation enabled: no")
        print("  Builder execution enabled: no")
        print("  External API called: NO")
        print(f"  Report: {md_path}")
        print(f"  JSON: {json_path}")
        return 0

    mode = "approval_preflight" if args.approval_preflight else "dry_run"
    plan = build_runner_plan(project, args.task, mode=mode)
    md_path, json_path = write_runner_plan(project, plan)
    label = "Approval Preflight" if args.approval_preflight else ("Rollback Plan" if args.rollback_plan else "Runner Dry-Run")
    print(f"Claude Sandbox {label}: {plan.runner_state.state}")
    print(f"  Approval status: {plan.runner_state.approval_status}")
    print(f"  Dry-run result: {plan.runner_state.dry_run_result}")
    print("  Worktree creation enabled: no")
    print("  Builder execution enabled: no")
    print("  External API called: NO")
    print("  Real worktree created: no")
    print(f"  Runner plan: {md_path}")
    print(f"  Runner JSON: {json_path}")
    print(f"  Approval contract: {plan.approval_contract_path}")
    print(f"  Next action: {plan.runner_state.next_action}")
    return 0 if plan.runner_state.state != BLOCKED else 2


if __name__ == "__main__":
    raise SystemExit(main())
