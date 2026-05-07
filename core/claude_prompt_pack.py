from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claude_sandbox_boundary import evaluate_preflight
from config import ProjectConfig, load_project_config


def _latest_dir(project: ProjectConfig) -> Path:
    out = project.repo_path / project.logs_dir / "claude_sandbox" / project.project_id / "latest"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_prompt_pack(project: ProjectConfig, task: str) -> dict[str, Any]:
    preflight = evaluate_preflight(project, task)
    boundary = preflight.boundary
    return {
        "project_id": project.project_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "mode": "prompt_pack_preview_only",
        "external_api_called": False,
        "claude_execution_enabled": False,
        "secrets_included": False,
        "env_files_read": False,
        "preflight_verdict": preflight.verdict,
        "allowed_files": boundary.file_policy.allowed_files,
        "denied_files": boundary.file_policy.denied_files,
        "allowed_commands": boundary.command_policy.allowed_commands,
        "denied_commands": boundary.command_policy.denied_commands,
        "stop_conditions": boundary.stop_conditions,
        "builder_report_format": [
            "Task title",
            "Files created",
            "Files modified",
            "Commands run",
            "Validation results",
            "Evidence captured",
            "Blockers",
            "Risks",
            "Git status",
        ],
        "post_builder_policy_command": f"python -B project_autopilot/agent_loop.py --project {project.project_id} --post-builder <builder_report.md>",
        "worktree_required": boundary.worktree_plan.required,
        "rollback_required": boundary.rollback_plan.required,
        "next_action": "Use this prompt pack only after human approval in a dedicated worktree; do not execute from Project Autopilot yet.",
    }


def write_prompt_pack(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    out = _latest_dir(project)
    md_path = out / "claude_prompt_pack_preview.md"
    json_path = out / "claude_prompt_pack_metadata.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Claude Builder Prompt Pack Preview",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Generated: {payload['generated_at_utc']}",
        f"Task: {payload['task']}",
        f"Mode: {payload['mode']}",
        "External API called: no",
        "Claude execution enabled: no",
        "Secrets included: no",
        "Env files read: no",
        "",
        "## Builder Instructions",
        "You are a future sandboxed Claude builder. This prompt pack is a preview only.",
        "Do not read, print, or modify env/secret files. Do not execute SQL, deploy, call paid APIs, enable scheduler, or enable automatic Claude execution.",
        "Work only in the human-approved task worktree. Do not write directly to master/main. Do not auto-merge.",
        "",
        "## Objective",
        payload["task"],
        "",
        "## Allowed Files",
        *[f"- `{item}`" for item in payload["allowed_files"]],
        "",
        "## Denied Files",
        *[f"- `{item}`" for item in payload["denied_files"]],
        "",
        "## Allowed Validation Commands",
        *[f"- `{item}`" for item in payload["allowed_commands"]],
        "",
        "## Denied Commands",
        *[f"- `{item}`" for item in payload["denied_commands"]],
        "",
        "## Stop Conditions",
        *[f"- {item}" for item in payload["stop_conditions"]],
        "",
        "## Required Builder Report Format",
        *[f"- {item}" for item in payload["builder_report_format"]],
        "",
        "## Post-Builder Policy",
        f"- Run: `{payload['post_builder_policy_command']}`",
        "- Project Autopilot policy is the final judge. Builder output cannot approve itself.",
        "",
        "## Next Action",
        payload["next_action"],
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a no-secret Claude builder prompt pack preview")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--task", default="Improve Project Autopilot docs")
    args = parser.parse_args()

    project = load_project_config(args.project)
    payload = build_prompt_pack(project, args.task)
    md_path, json_path = write_prompt_pack(project, payload)
    print("Claude Prompt Pack Preview: READY")
    print("  External API called: NO")
    print("  Claude execution enabled: no")
    print("  Secrets included: no")
    print(f"  Preflight verdict: {payload['preflight_verdict']}")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
