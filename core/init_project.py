"""Bootstrap a new project for Project Autopilot.

Creates project_control/ files from templates and a project YAML config.
Reusable across any project -- not specific to MIRA.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

AUTOPILOT_ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = AUTOPILOT_ROOT / "templates"
PROJECTS_DIR = AUTOPILOT_ROOT / "config" / "projects"

# Same order used by project_loader.py
CONTROL_FILES = [
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

DEFAULT_YAML_TEMPLATE = """\
project_id: {project_id}
project_name: {project_name}
repo_path: {repo_path}
project_control_path: project_control
framework: unknown
package_manager: npm

build_command: npm run build
typecheck_command: npm run typecheck
lint_command: npm run lint
test_command: npm test
dev_server_command: npm run dev

browser_qa_enabled: false
screenshot_enabled: true
screenshots_dir: screenshots/{project_id}

route_walk_urls: []

autonomy_mode: autonomous_guarded
intensity_mode: low_cost
max_retries_per_task: 3
run_frequency_hours: 3
max_cycles_per_day: 4
max_parallel_agents: 1

daily_budget_usd: 5
per_cycle_budget_usd: 1.50
monthly_budget_usd: 100
paid_api_mode: disabled_by_default
allow_paid_image_generation: false
allow_paid_video_generation: false

telegram_enabled: false

builder_primary: codex
builder_fallback: claude
allow_automatic_builder_execution: false
builder_handoff_mode: manual
claude_command: claude
latest_prompt_path: logs/{project_id}_latest_builder_prompt.md

model_routing:
  cheap_model: gpt-5.4-mini
  standard_model: gpt-5.4
  premium_model: gpt-5.5
  qa_model: gpt-5.4
"""


def _copy_template(template_name: str, dest: Path, force: bool) -> str:
    """Copy a single template file to dest. Returns a status string."""
    src = TEMPLATES_DIR / template_name
    if not src.exists():
        return f"  SKIP (no template): {template_name}"
    if dest.exists() and not force:
        return f"  EXISTS (kept):      {dest.name}"
    shutil.copy2(src, dest)
    return f"  CREATED:            {dest.name}"


def init_project(
    project_id: str,
    project_name: str,
    repo_path: str,
    force: bool = False,
) -> bool:
    """Create project_control/ files and project YAML config.

    Returns True on success, False on fatal error.
    """
    repo = Path(repo_path).resolve()
    if not repo.is_dir():
        print(f"ERROR: repo-path does not exist: {repo}", file=sys.stderr)
        return False

    control_dir = repo / "project_control"
    control_dir.mkdir(parents=True, exist_ok=True)

    # --- project_control/ files from templates ---
    print(f"\nProject control directory: {control_dir}")
    for filename in CONTROL_FILES:
        template_name = filename.replace(".md", ".template.md")
        dest = control_dir / filename
        status = _copy_template(template_name, dest, force)
        print(status)

    # --- project YAML ---
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    yaml_path = PROJECTS_DIR / f"{project_id}.yaml"
    if yaml_path.exists() and not force:
        print(f"\n  EXISTS (kept):      {yaml_path}")
    else:
        yaml_content = DEFAULT_YAML_TEMPLATE.format(
            project_id=project_id,
            project_name=project_name,
            repo_path=repo_path.replace("\\", "/"),
        )
        yaml_path.write_text(yaml_content, encoding="utf-8")
        print(f"\n  CREATED:            {yaml_path}")

    # --- logs / screenshots dirs ---
    (repo / "logs").mkdir(parents=True, exist_ok=True)
    (repo / "screenshots" / project_id).mkdir(parents=True, exist_ok=True)

    print(f"\nProject '{project_id}' initialized at {repo}")
    print("Next steps:")
    print(f"  1. Edit {yaml_path} to set framework, package_manager, commands.")
    print(f"  2. Fill in {control_dir}/MASTER_PLAN.md with your project goals.")
    print(f"  3. Run: python -B project_autopilot/agent_loop.py --project {project_id} --doctor")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="init_project",
        description="Bootstrap a new project for Project Autopilot.",
    )
    parser.add_argument(
        "--project-id",
        required=True,
        help="Short identifier (lowercase, no spaces). Used as config filename and directory names.",
    )
    parser.add_argument(
        "--project-name",
        required=True,
        help="Human-readable project name.",
    )
    parser.add_argument(
        "--repo-path",
        required=True,
        help="Absolute path to the project repository root.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Overwrite existing files. Without this flag, existing files are kept.",
    )
    args = parser.parse_args()
    ok = init_project(
        project_id=args.project_id,
        project_name=args.project_name,
        repo_path=args.repo_path,
        force=args.force,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
