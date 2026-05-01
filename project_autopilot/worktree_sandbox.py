from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claude_sandbox_boundary import evaluate_preflight, simulate_sandbox, write_simulation
from config import ProjectConfig, load_project_config


def _latest_dir(project: ProjectConfig) -> Path:
    out = project.repo_path / project.logs_dir / "claude_sandbox" / project.project_id / "latest"
    out.mkdir(parents=True, exist_ok=True)
    return out


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
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--simulate", action="store_true")
    args = parser.parse_args()

    project = load_project_config(args.project)
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
