from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claude_sandbox_approval import APPROVED_FOR_WORKTREE_CREATION_ONLY, build_contract_preview, validate_contract, write_contract_preview
from claude_sandbox_boundary import evaluate_preflight, simulate_sandbox, write_simulation
from config import ProjectConfig, load_project_config


def _latest_dir(project: ProjectConfig) -> Path:
    out = project.repo_path / project.logs_dir / "claude_sandbox" / project.project_id / "latest"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _task_id(task: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", task.lower()).strip("-")
    return (slug[:48].strip("-") or "task")


def _worktree_task_dir(project: ProjectConfig, task_id: str) -> Path:
    out = project.repo_path / project.logs_dir / "claude_sandbox" / project.project_id / "worktrees" / task_id
    out.mkdir(parents=True, exist_ok=True)
    return out


def _sandbox_path(project: ProjectConfig, task_id: str) -> Path:
    return project.repo_path.parent / f"{project.repo_path.name}-sandbox-{task_id}"


def _sandbox_branch(task_id: str) -> str:
    return f"sandbox/claude-{task_id}"


def _run_git(project: ProjectConfig, args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd or project.repo_path),
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )


def _safe_recorded_sandbox_path(project: ProjectConfig, raw_path: str) -> Path:
    path = Path(raw_path).resolve()
    expected_parent = project.repo_path.parent.resolve()
    if path.parent != expected_parent:
        raise ValueError("Recorded sandbox path is not directly under the project parent directory.")
    if not path.name.startswith(f"{project.repo_path.name}-sandbox-"):
        raise ValueError("Recorded sandbox path does not match the expected sandbox naming pattern.")
    if project.repo_path.resolve() in [path, *path.parents]:
        raise ValueError("Recorded sandbox path points inside the main repository.")
    return path


def build_worktree_sandbox_plan(project: ProjectConfig, task: str) -> dict[str, Any]:
    preflight = evaluate_preflight(project, task)
    boundary = preflight.boundary
    return {
        "project_id": project.project_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "mode": "plan_only",
        "preflight_verdict": preflight.verdict,
        "real_worktree_created": False,
        "external_api_called": False,
        "claude_execution_enabled": False,
        "branch_name": boundary.worktree_plan.branch_name,
        "worktree_path": boundary.worktree_plan.worktree_path,
        "allowed_files": boundary.file_policy.allowed_files,
        "denied_files": boundary.file_policy.denied_files,
        "lifecycle_steps": boundary.worktree_plan.lifecycle_steps,
        "rollback_steps": boundary.rollback_plan.steps,
        "rejection_flow": boundary.rollback_plan.rejection_flow,
        "post_builder_policy_command": f"python -B project_autopilot/agent_loop.py --project {project.project_id} --post-builder <builder_report.md>",
        "merge_policy": boundary.worktree_plan.merge_policy,
        "direct_master_writes_allowed": boundary.worktree_plan.direct_master_writes_allowed,
        "auto_merge_allowed": boundary.rollback_plan.auto_merge_allowed,
        "force_push_allowed": boundary.rollback_plan.force_push_allowed,
        "evidence_plan": [
            "builder report",
            "git status",
            "changed files",
            "diff stat",
            "validation command results",
            "post-builder policy report",
            "evidence bundle",
        ],
        "next_action": "This is a plan only. A real worktree may be created only in a later human-approved execution sprint.",
    }


def build_worktree_creation_plan(project: ProjectConfig, task: str, task_id: str | None = None) -> dict[str, Any]:
    task_id = task_id or _task_id(task)
    contract = build_contract_preview(
        project,
        task,
        status=APPROVED_FOR_WORKTREE_CREATION_ONLY,
        human_approver="explicit_create_approved_cli",
        allow_worktree_creation_now=True,
    )
    validation = validate_contract(contract)
    return {
        "project_id": project.project_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "task_id": task_id,
        "mode": "create_approved",
        "approval_status": contract.approval_status,
        "approval_validation": validation.to_dict(),
        "worktree_path": str(_sandbox_path(project, task_id)),
        "branch_name": _sandbox_branch(task_id),
        "source_commit": "",
        "created": False,
        "verified": False,
        "cleanup_required": False,
        "cleanup_completed": False,
        "no_claude_execution": True,
        "no_external_api": True,
        "no_product_code_touched": True,
        "claude_builder_execution_enabled": False,
        "auto_merge_enabled": False,
        "commands_run": [],
        "errors": [],
        "next_action": "Run --cleanup-approved with this task id after the worktree is no longer needed.",
    }


def write_worktree_creation(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    latest = _latest_dir(project)
    task_dir = _worktree_task_dir(project, payload["task_id"])
    md_path = latest / "worktree_creation.md"
    json_path = latest / "worktree_creation.json"
    task_json = task_dir / "worktree_creation.json"
    task_md = task_dir / "worktree_creation.md"
    for path in (json_path, task_json):
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Claude Sandbox Worktree Creation",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Task id: `{payload['task_id']}`",
        f"Task: {payload['task']}",
        f"Verdict: {payload.get('verdict', 'UNKNOWN')}",
        f"Approval status: {payload['approval_status']}",
        f"Worktree path: `{payload['worktree_path']}`",
        f"Branch: `{payload['branch_name']}`",
        f"Source commit: `{payload.get('source_commit', '')}`",
        f"Created: {'yes' if payload['created'] else 'no'}",
        f"Verified: {'yes' if payload['verified'] else 'no'}",
        f"Cleanup required: {'yes' if payload['cleanup_required'] else 'no'}",
        "Claude execution: no",
        "External API: no",
        "Product code touched: no",
        "Auto-merge: no",
        "",
        "## Commands Run",
        *[f"- `{item}`" for item in payload["commands_run"]],
        "",
        "## Errors",
        *([f"- {item}" for item in payload["errors"]] or ["- none"]),
        "",
        "## Next Action",
        payload["next_action"],
    ]
    for path in (md_path, task_md):
        path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def create_approved_worktree(project: ProjectConfig, task: str, task_id: str | None = None) -> dict[str, Any]:
    payload = build_worktree_creation_plan(project, task, task_id)
    contract = build_contract_preview(
        project,
        task,
        status=APPROVED_FOR_WORKTREE_CREATION_ONLY,
        human_approver="explicit_create_approved_cli",
        allow_worktree_creation_now=True,
    )
    contract_path = write_contract_preview(project, contract)
    validation = validate_contract(contract)
    payload["approval_contract_path"] = str(contract_path)
    if not validation.valid:
        payload["verdict"] = "WORKTREE_CREATION_BLOCKED"
        payload["errors"].extend(validation.blocked_reasons)
        payload["next_action"] = "Fix approval contract blockers; no worktree was created."
        return payload

    worktree_path = _safe_recorded_sandbox_path(project, payload["worktree_path"])
    if worktree_path.exists():
        payload["verdict"] = "WORKTREE_CREATION_BLOCKED"
        payload["errors"].append("Sandbox worktree path already exists.")
        payload["cleanup_required"] = True
        payload["next_action"] = "Run cleanup-approved for this task id or inspect the existing sandbox path."
        return payload

    source = _run_git(project, ["rev-parse", "HEAD"])
    payload["commands_run"].append("git rev-parse HEAD")
    if source.returncode != 0:
        payload["verdict"] = "WORKTREE_CREATION_BLOCKED"
        payload["errors"].append((source.stderr or source.stdout).strip() or "Could not resolve source commit.")
        return payload
    payload["source_commit"] = source.stdout.strip()

    add = _run_git(project, ["worktree", "add", "-b", payload["branch_name"], str(worktree_path), payload["source_commit"]])
    payload["commands_run"].append("git worktree add -b <sandbox-branch> <sandbox-path> <source-commit>")
    if add.returncode != 0:
        payload["verdict"] = "WORKTREE_CREATION_BLOCKED"
        payload["errors"].append((add.stderr or add.stdout).strip() or "git worktree add failed.")
        payload["cleanup_required"] = worktree_path.exists()
        payload["next_action"] = "No retry was attempted. Inspect git worktree constraints and rerun only after cleanup."
        return payload

    payload["created"] = True
    payload["cleanup_required"] = True
    status = _run_git(project, ["-C", str(worktree_path), "status", "--short"])
    branch = _run_git(project, ["-C", str(worktree_path), "branch", "--show-current"])
    payload["commands_run"].extend(["git -C <sandbox-path> status --short", "git -C <sandbox-path> branch --show-current"])
    if status.returncode == 0 and branch.returncode == 0 and branch.stdout.strip() == payload["branch_name"]:
        payload["verified"] = True
        payload["verdict"] = "WORKTREE_CREATION_PASS"
        payload["next_action"] = "Cleanup is required after inspection; Claude builder execution remains disabled."
    else:
        payload["verdict"] = "WORKTREE_CREATION_WARN"
        payload["errors"].append("Worktree was created but safe verification did not fully pass.")
        payload["next_action"] = "Run cleanup-approved or inspect the recorded sandbox path; do not execute Claude."
    return payload


def write_worktree_cleanup(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    latest = _latest_dir(project)
    task_dir = _worktree_task_dir(project, payload["task_id"])
    md_path = latest / "worktree_cleanup.md"
    json_path = latest / "worktree_cleanup.json"
    task_json = task_dir / "worktree_cleanup.json"
    task_md = task_dir / "worktree_cleanup.md"
    for path in (json_path, task_json):
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Claude Sandbox Worktree Cleanup",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Task id: `{payload['task_id']}`",
        f"Verdict: {payload.get('verdict', 'UNKNOWN')}",
        f"Worktree path: `{payload.get('worktree_path', '')}`",
        f"Branch: `{payload.get('branch_name', '')}`",
        f"Cleanup completed: {'yes' if payload.get('cleanup_completed') else 'no'}",
        "Claude execution: no",
        "External API: no",
        "",
        "## Commands Run",
        *[f"- `{item}`" for item in payload.get("commands_run", [])],
        "",
        "## Errors",
        *([f"- {item}" for item in payload.get("errors", [])] or ["- none"]),
        "",
        "## Next Action",
        payload.get("next_action", ""),
    ]
    for path in (md_path, task_md):
        path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def cleanup_approved_worktree(project: ProjectConfig, task_id: str) -> dict[str, Any]:
    task_dir = _worktree_task_dir(project, task_id)
    creation_path = task_dir / "worktree_creation.json"
    payload = {
        "project_id": project.project_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "mode": "cleanup_approved",
        "worktree_path": "",
        "branch_name": "",
        "cleanup_completed": False,
        "no_claude_execution": True,
        "no_external_api": True,
        "commands_run": [],
        "errors": [],
        "next_action": "",
    }
    if not creation_path.exists():
        payload["verdict"] = "WORKTREE_CLEANUP_BLOCKED"
        payload["errors"].append("No recorded worktree creation evidence exists for this task id.")
        payload["next_action"] = "Refusing cleanup without recorded sandbox evidence."
        return payload

    creation = json.loads(creation_path.read_text(encoding="utf-8"))
    payload["worktree_path"] = creation.get("worktree_path", "")
    payload["branch_name"] = creation.get("branch_name", "")
    try:
        worktree_path = _safe_recorded_sandbox_path(project, payload["worktree_path"])
    except ValueError as exc:
        payload["verdict"] = "WORKTREE_CLEANUP_BLOCKED"
        payload["errors"].append(str(exc))
        payload["next_action"] = "Cleanup refused because recorded path did not pass sandbox safety checks."
        return payload

    if not worktree_path.exists():
        payload["verdict"] = "WORKTREE_CLEANUP_PASS"
        payload["cleanup_completed"] = True
        payload["next_action"] = "Recorded sandbox worktree path is already absent."
        return payload

    remove = _run_git(project, ["worktree", "remove", str(worktree_path)])
    payload["commands_run"].append("git worktree remove <recorded-sandbox-path>")
    if remove.returncode != 0:
        payload["verdict"] = "WORKTREE_CLEANUP_BLOCKED"
        payload["errors"].append((remove.stderr or remove.stdout).strip() or "git worktree remove failed.")
        payload["next_action"] = "Manual cleanup may be needed for the recorded sandbox path only; do not delete arbitrary paths."
        return payload

    payload["verdict"] = "WORKTREE_CLEANUP_PASS"
    payload["cleanup_completed"] = True
    payload["next_action"] = "Sandbox worktree was removed. Branch cleanup, if desired later, must be explicit and human-approved."
    return payload


def smoke_test_worktree(project: ProjectConfig) -> dict[str, Any]:
    unique = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    task = "Sandbox worktree creation smoke test"
    task_id = f"smoke-{unique}"
    creation = create_approved_worktree(project, task, task_id=task_id)
    creation_md, creation_json = write_worktree_creation(project, creation)
    cleanup = cleanup_approved_worktree(project, task_id)
    cleanup_md, cleanup_json = write_worktree_cleanup(project, cleanup)
    verdict = "WORKTREE_SMOKE_PASS" if creation.get("created") and cleanup.get("cleanup_completed") else "WORKTREE_SMOKE_FAIL"
    payload = {
        "project_id": project.project_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "task_id": task_id,
        "verdict": verdict,
        "creation_verdict": creation.get("verdict"),
        "cleanup_verdict": cleanup.get("verdict"),
        "worktree_path": creation.get("worktree_path"),
        "branch_name": creation.get("branch_name"),
        "no_claude_execution": True,
        "no_external_api": True,
        "no_product_code_touched": True,
        "cleanup_completed": bool(cleanup.get("cleanup_completed")),
        "creation_report": str(creation_md),
        "creation_json": str(creation_json),
        "cleanup_report": str(cleanup_md),
        "cleanup_json": str(cleanup_json),
        "errors": creation.get("errors", []) + cleanup.get("errors", []),
    }
    out = _latest_dir(project)
    (out / "worktree_smoke_test.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (out / "worktree_smoke_test.md").write_text(
        "\n".join([
            "# Claude Sandbox Worktree Smoke Test",
            "",
            f"Verdict: {verdict}",
            f"Task id: `{task_id}`",
            f"Worktree path: `{payload['worktree_path']}`",
            f"Branch: `{payload['branch_name']}`",
            f"Cleanup completed: {'yes' if payload['cleanup_completed'] else 'no'}",
            "Claude execution: no",
            "External API: no",
            "Product code touched: no",
            "",
            "## Evidence",
            f"- Creation: `{creation_md}`",
            f"- Cleanup: `{cleanup_md}`",
        ]),
        encoding="utf-8",
    )
    return payload


def write_worktree_sandbox_plan(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    out = _latest_dir(project)
    md_path = out / "worktree_sandbox_plan.md"
    json_path = out / "worktree_sandbox_plan.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Claude Worktree Sandbox Plan",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Generated: {payload['generated_at_utc']}",
        f"Task: {payload['task']}",
        f"Mode: {payload['mode']}",
        f"Preflight verdict: {payload['preflight_verdict']}",
        "Real worktree created: no",
        "External API called: no",
        "Claude execution enabled: no",
        "",
        "## Proposed Worktree",
        f"- Branch: `{payload['branch_name']}`",
        f"- Path: `{payload['worktree_path']}`",
        f"- Direct master writes allowed: {'yes' if payload['direct_master_writes_allowed'] else 'no'}",
        f"- Auto-merge allowed: {'yes' if payload['auto_merge_allowed'] else 'no'}",
        f"- Force-push allowed: {'yes' if payload['force_push_allowed'] else 'no'}",
        "",
        "## Allowed Files",
        *[f"- `{item}`" for item in payload["allowed_files"]],
        "",
        "## Denied Files",
        *[f"- `{item}`" for item in payload["denied_files"]],
        "",
        "## Lifecycle Steps",
        *[f"- {item}" for item in payload["lifecycle_steps"]],
        "",
        "## Rollback Plan",
        *[f"- {item}" for item in payload["rollback_steps"]],
        "",
        "## Rejection Flow",
        *[f"- {item}" for item in payload["rejection_flow"]],
        "",
        "## Evidence Plan",
        *[f"- {item}" for item in payload["evidence_plan"]],
        "",
        "## Post-Builder Policy",
        f"- `{payload['post_builder_policy_command']}`",
        "",
        "## Next Action",
        payload["next_action"],
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan future Claude sandbox worktree lifecycle without creating it")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--task", default="Improve Project Autopilot docs")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--create-approved", action="store_true")
    parser.add_argument("--cleanup-approved", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()

    project = load_project_config(args.project)
    if args.create_approved:
        payload = create_approved_worktree(project, args.task, task_id=args.task_id or None)
        md_path, json_path = write_worktree_creation(project, payload)
        print(f"Worktree Creation: {payload.get('verdict')}")
        print(f"  Task id: {payload['task_id']}")
        print(f"  Worktree path: {payload['worktree_path']}")
        print(f"  Branch: {payload['branch_name']}")
        print(f"  Cleanup required: {'yes' if payload['cleanup_required'] else 'no'}")
        print("  Claude execution: no")
        print("  External API called: NO")
        print(f"  Report: {md_path}")
        print(f"  JSON: {json_path}")
        return 0 if payload.get("verdict") in {"WORKTREE_CREATION_PASS", "WORKTREE_CREATION_WARN"} else 2

    if args.cleanup_approved:
        if not args.task_id:
            print("ERROR: --cleanup-approved requires --task-id")
            return 2
        payload = cleanup_approved_worktree(project, args.task_id)
        md_path, json_path = write_worktree_cleanup(project, payload)
        print(f"Worktree Cleanup: {payload.get('verdict')}")
        print(f"  Task id: {payload['task_id']}")
        print(f"  Worktree path: {payload.get('worktree_path', '')}")
        print(f"  Cleanup completed: {'yes' if payload.get('cleanup_completed') else 'no'}")
        print("  Claude execution: no")
        print("  External API called: NO")
        print(f"  Report: {md_path}")
        print(f"  JSON: {json_path}")
        return 0 if payload.get("verdict") == "WORKTREE_CLEANUP_PASS" else 2

    if args.smoke_test:
        payload = smoke_test_worktree(project)
        print(f"Worktree Smoke Test: {payload['verdict']}")
        print(f"  Task id: {payload['task_id']}")
        print(f"  Worktree path: {payload['worktree_path']}")
        print(f"  Branch: {payload['branch_name']}")
        print(f"  Cleanup completed: {'yes' if payload['cleanup_completed'] else 'no'}")
        print("  Claude execution: no")
        print("  External API called: NO")
        print(f"  Creation report: {payload['creation_report']}")
        print(f"  Cleanup report: {payload['cleanup_report']}")
        return 0 if payload["verdict"] == "WORKTREE_SMOKE_PASS" else 2

    if args.simulate:
        payload = build_worktree_sandbox_plan(project, args.task)
        md_path, json_path = write_worktree_sandbox_plan(project, payload)
        simulation = simulate_sandbox(project, args.task)
        sim_md, sim_json = write_simulation(project, simulation)
        print(f"Worktree Sandbox Simulation: {simulation.verdict}")
        print("  Real worktree created: no")
        print("  External API called: NO")
        print("  Claude execution enabled: no")
        print(f"  Plan: {md_path}")
        print(f"  Plan JSON: {json_path}")
        print(f"  Simulation: {sim_md}")
        print(f"  Simulation JSON: {sim_json}")
        return 0 if simulation.verdict == "SANDBOX_SIMULATION_PASS" else 2

    payload = build_worktree_sandbox_plan(project, args.task)
    md_path, json_path = write_worktree_sandbox_plan(project, payload)
    print("Worktree Sandbox Plan: READY")
    print("  Real worktree created: no")
    print("  External API called: NO")
    print("  Claude execution enabled: no")
    print(f"  Branch proposal: {payload['branch_name']}")
    print(f"  Worktree path proposal: {payload['worktree_path']}")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
