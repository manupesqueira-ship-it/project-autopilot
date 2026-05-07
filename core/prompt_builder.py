from __future__ import annotations

from typing import Any

from config import ProjectConfig
from quality_director import quality_block_for_prompt


def build_builder_prompt(
    project: ProjectConfig,
    control_docs: dict[str, str],
    task_plan: str,
    evidence: dict[str, Any],
) -> str:
    changed_files = "\n".join(f"- {item}" for item in evidence.get("changed_files", [])) or "- None"
    quality_block = quality_block_for_prompt(control_docs, evidence, task_plan)
    return f"""You are the builder agent for {project.project_name}.

Project ID: {project.project_id}
Primary builder: {project.builder_primary}
Fallback builder: {project.builder_fallback}
Autonomy mode: {project.autonomy_mode}
Intensity mode: {project.intensity_mode}
Framework: {project.framework}
Package manager: {project.package_manager}

Before doing any work, read every file in `{project.project_control_path}`.

Supervisor task plan:
{task_plan.strip()}

Repository evidence:
Git status:
{evidence.get('git_status', '').strip()}

Changed files:
{changed_files}

Hard constraints:
- Follow the project's `AGENT_RULES.md`, `AUTONOMY_PROTOCOL.md`, and `COST_POLICY.md`.
- Do not modify `.env`, `.env.local`, secrets, deployment files, or git history.
- Do not run destructive commands.
- Do not delete files.
- Do not deploy.
- Keep changes scoped to the approved task.
- Write blocking questions to `BLOCKERS.md`.
- Write non-blocking questions to `HUMAN_QUESTIONS.md`.
- Provide evidence after changes: git status, changed files, build output, typecheck output, lint/test output when available.

Quality and QA expectations:

{quality_block}

Project control excerpts:

TASK_QUEUE.md:
{control_docs.get('TASK_QUEUE.md', '').strip()[:4000]}

QUALITY_BAR.md:
{control_docs.get('QUALITY_BAR.md', '').strip()[:4000]}

AGENT_RULES.md:
{control_docs.get('AGENT_RULES.md', '').strip()[:4000]}

COST_POLICY.md:
{control_docs.get('COST_POLICY.md', '').strip()[:4000]}

Browser QA evidence:
{_browser_qa_section(evidence)}
"""


def _browser_qa_section(evidence: dict[str, Any]) -> str:
    report = evidence.get("browser_qa_report")
    if report:
        return f"Latest browser QA report: {report}"
    urls = evidence.get("route_walk_urls", [])
    if urls:
        return "No browser QA report yet. Run --browser-qa with the dev server running to collect route walk evidence."
    return "No route_walk_urls configured."
