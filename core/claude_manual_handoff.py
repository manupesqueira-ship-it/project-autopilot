from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claude_prompt_pack import build_prompt_pack, write_prompt_pack
from claude_sandbox_boundary import evaluate_preflight, write_preflight
from config import ProjectConfig, load_project_config
from worktree_sandbox import build_worktree_creation_plan, create_approved_worktree, write_worktree_creation


def _latest_dir(project: ProjectConfig) -> Path:
    out = project.repo_path / project.logs_dir / "claude_sandbox" / project.project_id / "latest"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _builder_report_template(project: ProjectConfig) -> list[str]:
    return [
        "# Manual Claude Builder Report",
        "",
        "## Task",
        "- Title:",
        "- Sandbox worktree path:",
        "- Sandbox branch:",
        "",
        "## Files Created",
        "- None, or list paths.",
        "",
        "## Files Modified",
        "- None, or list paths.",
        "",
        "## Commands Run",
        "- Command, exit code, concise result.",
        "",
        "## Validation Results",
        "- lint/typecheck/build/QA results, or explain not run.",
        "",
        "## Evidence Captured",
        "- Screenshots/logs/reports, sanitized only.",
        "",
        "## Blockers",
        "- None, or list blockers.",
        "",
        "## Risks",
        "- None, or list risks.",
        "",
        "## Git Status",
        "- Paste `git status --short` from the sandbox worktree.",
        "",
        "## Return Command",
        f"- `python -B project_autopilot/agent_loop.py --project {project.project_id} --post-builder <path_to_this_report>`",
    ]


def build_handoff_packet(project: ProjectConfig, task: str, create_worktree: bool = False) -> dict[str, Any]:
    preflight = evaluate_preflight(project, task)
    preflight_md, preflight_json = write_preflight(project, preflight)
    prompt_pack = build_prompt_pack(project, task)
    prompt_md, prompt_json = write_prompt_pack(project, prompt_pack)

    if create_worktree:
        creation = create_approved_worktree(project, task)
        creation_md, creation_json = write_worktree_creation(project, creation)
    else:
        creation = build_worktree_creation_plan(project, task)
        creation["verdict"] = "HANDOFF_DRY_RUN_NO_WORKTREE"
        creation_md = _latest_dir(project) / "worktree_creation.md"
        creation_json = _latest_dir(project) / "worktree_creation.json"

    worktree_path = creation.get("worktree_path", "")
    branch_name = creation.get("branch_name", "")
    task_id = creation.get("task_id", "")
    cleanup_command = f"python -B project_autopilot/agent_loop.py --project {project.project_id} --claude-worktree-cleanup-approved --task-id {task_id}"
    post_builder_command = f"python -B project_autopilot/agent_loop.py --project {project.project_id} --post-builder <path_to_claude_builder_report>"

    verdict = "MANUAL_HANDOFF_READY"
    if create_worktree and creation.get("verdict") not in {"WORKTREE_CREATION_PASS", "WORKTREE_CREATION_WARN"}:
        verdict = "MANUAL_HANDOFF_BLOCKED"
    elif not create_worktree:
        verdict = "MANUAL_HANDOFF_DRY_RUN_READY"

    return {
        "project_id": project.project_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "task_id": task_id,
        "verdict": verdict,
        "mode": "create_worktree_approved" if create_worktree else "dry_run",
        "worktree_created": bool(create_worktree and creation.get("created")),
        "worktree_path": worktree_path,
        "branch_name": branch_name,
        "cleanup_required": bool(create_worktree and creation.get("cleanup_required")),
        "waiting_for_manual_claude_report": bool(create_worktree and creation.get("created")),
        "claude_executed_by_project_autopilot": False,
        "external_api_called": False,
        "anthropic_called": False,
        "openai_called": False,
        "product_code_touched": False,
        "automatic_claude_execution_enabled": False,
        "preflight_verdict": preflight.verdict,
        "worktree_creation_verdict": creation.get("verdict"),
        "allowed_files": prompt_pack["allowed_files"],
        "denied_files": prompt_pack["denied_files"],
        "allowed_commands": prompt_pack["allowed_commands"],
        "denied_commands": prompt_pack["denied_commands"],
        "stop_conditions": prompt_pack["stop_conditions"],
        "builder_report_format": _builder_report_template(project),
        "required_validation_commands": prompt_pack["allowed_commands"],
        "post_builder_policy_command": post_builder_command,
        "cleanup_command": cleanup_command,
        "evidence_paths": {
            "manual_handoff_packet": str(_latest_dir(project) / "manual_handoff_packet.md"),
            "manual_handoff_metadata": str(_latest_dir(project) / "manual_handoff_metadata.json"),
            "preflight": str(preflight_md),
            "preflight_json": str(preflight_json),
            "prompt_pack": str(prompt_md),
            "prompt_pack_json": str(prompt_json),
            "worktree_creation": str(creation_md),
            "worktree_creation_json": str(creation_json),
        },
        "next_human_action": (
            f"Open Claude Code in {worktree_path} and paste the manual handoff packet."
            if create_worktree and creation.get("created")
            else "Review the dry-run handoff packet; create an approved worktree only when ready."
        ),
        "creation_errors": creation.get("errors", []),
    }


def write_handoff_packet(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    out = _latest_dir(project)
    md_path = out / "manual_handoff_packet.md"
    json_path = out / "manual_handoff_metadata.json"
    payload["evidence_paths"]["manual_handoff_packet"] = str(md_path)
    payload["evidence_paths"]["manual_handoff_metadata"] = str(json_path)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Manual Claude Code Handoff Packet",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Generated: {payload['generated_at_utc']}",
        f"Verdict: {payload['verdict']}",
        f"Mode: {payload['mode']}",
        "Project Autopilot executed Claude: no",
        "Project Autopilot called Anthropic/OpenAI: no",
        "Automatic Claude execution enabled: no",
        "",
        "## Human Setup",
        f"1. Open Claude Code with working directory: `{payload['worktree_path']}`",
        f"2. Confirm branch: `{payload['branch_name']}`",
        "3. Paste this packet into Claude Code manually.",
        "4. Do not allow Claude to read env files, print secrets, deploy, run SQL/RLS, call paid APIs, auto-merge, or enable scheduler/automatic execution.",
        "",
        "## Task Objective",
        payload["task"],
        "",
        "## Allowed Files",
        *[f"- `{item}`" for item in payload["allowed_files"]],
        "",
        "## Denied Files",
        *[f"- `{item}`" for item in payload["denied_files"]],
        "",
        "## Allowed Commands",
        *[f"- `{item}`" for item in payload["allowed_commands"]],
        "",
        "## Denied Commands",
        *[f"- `{item}`" for item in payload["denied_commands"]],
        "",
        "## Non-Negotiable Rules",
        "- Do not read, print, copy, summarize, or modify `.env`, `.env.local`, `.env.*`, keys, tokens, cookies, JWTs, or credentials.",
        "- Do not execute SQL, enable RLS, alter policies, modify Supabase live resources, or deploy.",
        "- Do not call OpenAI, Anthropic, paid image/video APIs, or external paid APIs.",
        "- Do not auto-merge, force-push, rebase shared branches, or touch git history.",
        "- Work only in the sandbox worktree path listed above.",
        "",
        "## Stop Conditions",
        *[f"- {item}" for item in payload["stop_conditions"]],
        "- Stop and report if the requested change requires files outside the allowlist.",
        "- Stop and report if validation requires secrets, live data, SQL/RLS, deploy, or paid APIs.",
        "",
        "## Required Validation Commands",
        *[f"- `{item}`" for item in payload["required_validation_commands"]],
        "",
        "## Required Builder Report Format",
        "Create a markdown report with exactly this structure:",
        "```markdown",
        *payload["builder_report_format"],
        "```",
        "",
        "## Return To Project Autopilot",
        f"After Claude finishes, save the builder report and run from the main repo: `{payload['post_builder_policy_command']}`",
        "Project Autopilot policy is the final judge. Claude cannot approve its own work.",
        "",
        "## Cleanup",
        f"When the sandbox is no longer needed, run from the main repo: `{payload['cleanup_command']}`",
        "",
        "## Evidence Paths",
        *[f"- {name}: `{path}`" for name, path in payload["evidence_paths"].items()],
        "",
        "## Next Human Action",
        payload["next_human_action"],
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate manual Claude Code handoff packet for an approved sandbox worktree")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--task", default="Improve Project Autopilot docs")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--create-worktree-approved", action="store_true")
    args = parser.parse_args()

    project = load_project_config(args.project)
    payload = build_handoff_packet(project, args.task, create_worktree=args.create_worktree_approved)
    md_path, json_path = write_handoff_packet(project, payload)
    print(f"Manual Claude Handoff: {payload['verdict']}")
    print(f"  Worktree created: {'yes' if payload['worktree_created'] else 'no'}")
    print(f"  Worktree path: {payload['worktree_path']}")
    print(f"  Branch: {payload['branch_name']}")
    print("  Claude executed by Project Autopilot: no")
    print("  External API called: NO")
    print(f"  Packet: {md_path}")
    print(f"  Metadata: {json_path}")
    print(f"  Cleanup command: {payload['cleanup_command']}")
    print(f"  Next human action: {payload['next_human_action']}")
    return 0 if payload["verdict"] != "MANUAL_HANDOFF_BLOCKED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
