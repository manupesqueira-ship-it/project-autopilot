"""QA reviewer for Project Autopilot.

Wraps the OpenAI supervisor's QA review with structured verdict parsing
and risk classification.  When OpenAI is unavailable, provides a local
deterministic review based on evidence (build/typecheck/lint results).
"""
from __future__ import annotations

from typing import Any

from openai_supervisor import OpenAISupervisor
from quality_director import assess_task_risk


# ---------------------------------------------------------------------------
# QA verdicts and risk levels
# ---------------------------------------------------------------------------

VERDICTS = {"PASS", "FAIL_FIX_REQUIRED", "RESEARCH_REQUIRED", "HUMAN_DECISION_REQUIRED", "BLOCKED"}
RISK_LEVELS = {"low", "medium", "high", "critical"}


def classify_verdict(qa_text: str) -> str:
    """Extract the verdict from QA review text.  Returns one of the VERDICTS constants."""
    upper = qa_text.upper()
    for v in ("FAIL_FIX_REQUIRED", "RESEARCH_REQUIRED", "HUMAN_DECISION_REQUIRED", "BLOCKED", "PASS"):
        if v in upper:
            return v
    # If no explicit verdict found, treat as needing human review
    return "HUMAN_DECISION_REQUIRED"


def classify_risk(qa_text: str) -> str:
    """Extract risk level from QA review text."""
    lower = qa_text.lower()
    for level in ("critical", "high", "medium", "low"):
        if f"risk level: {level}" in lower or f"risk: {level}" in lower:
            return level
    if "critical" in lower:
        return "critical"
    if "high risk" in lower or "high-risk" in lower:
        return "high"
    return "medium"


# ---------------------------------------------------------------------------
# OpenAI-backed review
# ---------------------------------------------------------------------------

def review_with_openai(supervisor: OpenAISupervisor, task_plan: str, evidence: dict[str, Any]) -> str:
    """Call the OpenAI supervisor for QA review."""
    return supervisor.qa_review(task_plan, evidence)


def generate_correction_prompt(
    supervisor: OpenAISupervisor,
    task_plan: str,
    qa_review: str,
    evidence: dict[str, Any],
) -> str:
    """Call the OpenAI supervisor for a correction prompt."""
    return supervisor.correction_prompt(task_plan, qa_review, evidence)


# ---------------------------------------------------------------------------
# Local deterministic review (when OpenAI is unavailable)
# ---------------------------------------------------------------------------

def local_review(task_plan: str, evidence: dict[str, Any]) -> str:
    """Produce a local QA review from evidence without calling OpenAI.

    Checks build/typecheck/lint results and risk flags.  This is a safety
    net, not a replacement for thorough OpenAI-driven review.
    """
    lines: list[str] = ["# Local QA Review (no OpenAI)", ""]
    commands = evidence.get("commands", {})
    all_pass = True

    for name in ("build", "typecheck", "lint", "test"):
        result = commands.get(name)
        if not result:
            lines.append(f"- {name}: not executed")
            continue
        ec = result.get("exit_code", -1)
        if ec == 0:
            lines.append(f"- {name}: PASS (exit 0)")
        else:
            lines.append(f"- {name}: FAIL (exit {ec})")
            all_pass = False

    risk = assess_task_risk(task_plan, evidence)
    lines.append("")
    lines.append(f"Risk level: {risk['risk_level']}")
    if risk["flags"]:
        lines.append("Flags: " + ", ".join(risk["flags"]))
    for rec in risk["recommendations"]:
        lines.append(f"- {rec}")

    lines.append("")
    if not all_pass:
        lines.append("Verdict: FAIL_FIX_REQUIRED")
        lines.append("Fix failing commands before proceeding.")
    elif risk["risk_level"] in ("critical", "high"):
        lines.append("Verdict: HUMAN_DECISION_REQUIRED")
        lines.append("High-risk task detected. Human review recommended before execution.")
    else:
        lines.append("Verdict: PASS (local checks only — full QA requires manual testing)")
        lines.append("IMPORTANT: Local review only verifies command exit codes and risk flags.")
        lines.append("It does not verify buttons, flows, database writes, or UI correctness.")

    return "\n".join(lines)
