"""Local fallback planner — generates a builder prompt without any external API calls.

Used when OpenAI is unavailable (429, quota, missing key, budget blocked).
Reads project_control files and evidence to produce a deterministic prompt
optimized for Claude Code as the builder agent.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from config import ProjectConfig
from quality_director import quality_block_for_prompt


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _pick_next_task(task_queue_md: str) -> tuple[str, str]:
    """Extract the first actionable task from TASK_QUEUE.md.

    Returns (task_title, task_body).  If nothing actionable is found,
    returns a sentinel indicating the queue needs an update.
    """
    lines = task_queue_md.strip().splitlines()
    in_block = False
    title = ""
    body_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        # Skip top-level headings and empty lines before first task
        if stripped.startswith("# ") and not stripped.startswith("### "):
            continue
        if stripped.startswith("## Paused") or stripped.startswith("## Done") or stripped.startswith("## Completed"):
            break
        if stripped.startswith("### "):
            if in_block:
                break  # already captured one task
            title = stripped.lstrip("# ").strip()
            in_block = True
            continue
        if in_block:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()
    if not title:
        return "", ""
    return title, body


def _summarize_evidence(evidence: dict[str, Any]) -> str:
    parts: list[str] = []
    git_status = evidence.get("git_status", "").strip()
    if git_status:
        parts.append(f"Git status:\n```\n{git_status}\n```")

    changed = evidence.get("changed_files", [])
    if changed:
        parts.append("Changed files:\n" + "\n".join(f"- {f}" for f in changed))

    for name, result in evidence.get("commands", {}).items():
        ec = result.get("exit_code", "?")
        output = result.get("output", "").strip()
        status = "PASS" if ec == 0 else "FAIL"
        summary = output[:600] if output else "(no output)"
        parts.append(f"{name}: {status} (exit {ec})\n```\n{summary}\n```")

    return "\n\n".join(parts) if parts else "No evidence collected."


def _format_acceptance_criteria(task_body: str) -> str:
    """Pull acceptance criteria lines from the task body, or return a default."""
    criteria_lines: list[str] = []
    in_criteria = False
    for line in task_body.splitlines():
        stripped = line.strip()
        if re.match(r"(?i)^acceptance\s+criteria", stripped):
            in_criteria = True
            continue
        if in_criteria:
            if stripped.startswith("- "):
                criteria_lines.append(stripped)
            elif stripped == "":
                continue
            elif stripped.startswith("#"):
                break
            else:
                criteria_lines.append(f"- {stripped}")

    if criteria_lines:
        return "\n".join(criteria_lines)
    return "- Build passes: npm run build\n- Typecheck passes: npm run typecheck\n- Lint passes: npm run lint\n- No regressions in existing functionality"


def generate_local_plan(
    project: ProjectConfig,
    control_docs: dict[str, str],
    evidence: dict[str, Any],
) -> str:
    """Generate a deterministic builder prompt from local state only.

    Returns a fully-formed prompt string marked as LOCAL FALLBACK PLAN.
    """
    task_queue = control_docs.get("TASK_QUEUE.md", "")
    title, body = _pick_next_task(task_queue)

    if not title:
        return f"""# LOCAL FALLBACK PLAN — IDLE

Generated: {_utc_stamp()}
Project: {project.project_name} ({project.project_id})
Status: IDLE / NEEDS_TASK_QUEUE_UPDATE

No actionable task found in TASK_QUEUE.md.
Update project_control/TASK_QUEUE.md with the next priority task, then rerun.
"""

    acceptance = _format_acceptance_criteria(body)
    evidence_summary = _summarize_evidence(evidence)

    agent_rules = control_docs.get("AGENT_RULES.md", "").strip()[:3000]
    quality_bar = control_docs.get("QUALITY_BAR.md", "").strip()[:3000]
    cost_policy = control_docs.get("COST_POLICY.md", "").strip()[:2000]
    quality_block = quality_block_for_prompt(control_docs, evidence, f"{title}\n{body}")

    return f"""# LOCAL FALLBACK PLAN

Generated: {_utc_stamp()}
Project: {project.project_name} ({project.project_id})
Mode: local fallback (no external API was used to generate this plan)
Builder target: {project.builder_primary} (fallback: {project.builder_fallback})
Framework: {project.framework}
Package manager: {project.package_manager}

---

## Task

{title}

{body.strip()}

---

## Acceptance Criteria

{acceptance}

---

## Commands to Run After Changes

```bash
{project.typecheck_command or '# no typecheck command configured'}
{project.build_command or '# no build command configured'}
{project.lint_command or '# no lint command configured'}
{project.test_command or '# no test command configured'}
```

---

## Current Repository Evidence

{evidence_summary}

---

## Safety Constraints

- Do NOT modify .env, .env.local, secrets, deployment files, or git history.
- Do NOT run destructive commands (rm, del, git reset, git clean, git push, deploy).
- Do NOT delete files.
- Do NOT deploy.
- Do NOT add new dependencies unless required to fix an error.
- Do NOT change visual design unless the task explicitly requires it.
- Keep changes scoped to the approved task above.
- Write blocking questions to project_control/BLOCKERS.md.
- Write non-blocking questions to project_control/HUMAN_QUESTIONS.md.

---

## Quality and QA Expectations

{quality_block}

---

## Stop / Report Format

When done, report:
1. Files created (with one-line reason each).
2. Files modified (with one-line reason each).
3. Commands run and their results.
4. Whether build/typecheck/lint pass.
5. QA checks performed (per QA_PROTOCOL.md).
6. Any remaining risks or blockers.
7. Whether git is clean or dirty.

---

## Project Control Context

### AGENT_RULES.md
{agent_rules}

### QUALITY_BAR.md
{quality_bar}

### COST_POLICY.md
{cost_policy}
"""
