"""QA reviewer for Project Autopilot.

Wraps the OpenAI supervisor's QA review with structured verdict parsing
and risk classification.  When OpenAI is unavailable, provides a local
deterministic review based on evidence (build/typecheck/lint results).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from config import ProjectConfig
from openai_supervisor import OpenAISupervisor
from quality_director import assess_task_risk
from risk_classifier import RiskAssessment


# ---------------------------------------------------------------------------
# QA verdicts and risk levels
# ---------------------------------------------------------------------------

VERDICTS = {"PASS", "FAIL_FIX_REQUIRED", "RESEARCH_REQUIRED", "HUMAN_DECISION_REQUIRED", "BLOCKED"}
RISK_LEVELS = {"low", "medium", "high", "critical"}


@dataclass(frozen=True)
class QAVerdict:
    verdict: str
    risk_level: str
    reasons: list[str] = field(default_factory=list)
    required_fixes: list[str] = field(default_factory=list)
    research_needed: list[str] = field(default_factory=list)
    human_decisions_needed: list[str] = field(default_factory=list)
    evidence_reviewed: list[str] = field(default_factory=list)
    recommended_next_action: str = "proceed"

    def to_markdown(self) -> str:
        def section(title: str, items: list[str]) -> str:
            body = "\n".join(f"- {item}" for item in items) if items else "- None"
            return f"### {title}\n\n{body}"

        return "\n\n".join(
            [
                f"Verdict: {self.verdict}",
                f"Risk level: {self.risk_level}",
                section("Reasons", self.reasons),
                section("Required fixes", self.required_fixes),
                section("Research needed", self.research_needed),
                section("Human decisions needed", self.human_decisions_needed),
                section("Evidence reviewed", self.evidence_reviewed),
                f"Recommended next action: {self.recommended_next_action}",
            ]
        )


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


def local_structured_review(
    task_plan: str,
    evidence: dict[str, Any],
    risk_assessment: RiskAssessment,
    builder_report: str = "",
) -> QAVerdict:
    commands = evidence.get("commands", {})
    reasons: list[str] = []
    required_fixes: list[str] = []
    research_needed: list[str] = []
    human_decisions_needed: list[str] = []
    evidence_reviewed: list[str] = [
        "builder report",
        "git status",
        "changed files",
        "git diff stat",
        "configured command outputs",
    ]

    for name, result in commands.items():
        exit_code = result.get("exit_code")
        if exit_code == 0:
            reasons.append(f"{name} passed.")
        else:
            reasons.append(f"{name} failed with exit code {exit_code}.")
            required_fixes.append(f"Fix failing `{name}` command.")

    lowered = builder_report.lower()
    if "blocker" in lowered and "none" not in lowered:
        reasons.append("Builder report mentions blockers.")
    if "not verified" in lowered:
        reasons.append("Builder report includes unverified items.")

    if risk_assessment.recommended_action == "block":
        return QAVerdict(
            verdict="BLOCKED",
            risk_level="critical",
            reasons=reasons + risk_assessment.reasons,
            required_fixes=required_fixes,
            evidence_reviewed=evidence_reviewed,
            recommended_next_action="Stop and resolve blocker before continuing.",
        )

    if risk_assessment.recommended_action == "require_human_decision":
        human_decisions_needed.extend(risk_assessment.reasons)
        return QAVerdict(
            verdict="HUMAN_DECISION_REQUIRED",
            risk_level=risk_assessment.risk_level,
            reasons=reasons + risk_assessment.reasons,
            required_fixes=required_fixes,
            human_decisions_needed=human_decisions_needed,
            evidence_reviewed=evidence_reviewed,
            recommended_next_action="Get human decision before more builder work.",
        )

    if risk_assessment.recommended_action == "proceed_with_qa" and "research_required" in risk_assessment.categories:
        research_needed.extend(risk_assessment.reasons)
        return QAVerdict(
            verdict="RESEARCH_REQUIRED",
            risk_level=risk_assessment.risk_level,
            reasons=reasons + risk_assessment.reasons,
            required_fixes=required_fixes,
            research_needed=research_needed,
            evidence_reviewed=evidence_reviewed,
            recommended_next_action="Complete scoped research before implementation continues.",
        )

    if required_fixes:
        return QAVerdict(
            verdict="FAIL_FIX_REQUIRED",
            risk_level=max(risk_assessment.risk_level, "medium", key=["low", "medium", "high", "critical"].index),
            reasons=reasons + risk_assessment.reasons,
            required_fixes=required_fixes,
            evidence_reviewed=evidence_reviewed,
            recommended_next_action="Use generated correction prompt, then rerun validation.",
        )

    return QAVerdict(
        verdict="PASS",
        risk_level=risk_assessment.risk_level,
        reasons=reasons + risk_assessment.reasons,
        evidence_reviewed=evidence_reviewed,
        recommended_next_action="Ready for human review and commit. Project Autopilot does not auto-commit.",
    )


def generate_local_correction_prompt(project: ProjectConfig, verdict: QAVerdict, evidence: dict[str, Any]) -> str:
    changed_files = evidence.get("changed_files", [])
    likely_files = "\n".join(f"- {path}" for path in changed_files) if changed_files else "- Inspect the files changed by the previous builder."
    fixes = "\n".join(f"- {fix}" for fix in verdict.required_fixes) if verdict.required_fixes else "- Address QA findings."
    reasons = "\n".join(f"- {reason}" for reason in verdict.reasons) if verdict.reasons else "- QA found issues."
    return f"""# Correction Prompt for {project.project_name}

You are the builder agent receiving a correction task from Project Autopilot.

## Failure Summary

Verdict: {verdict.verdict}
Risk level: {verdict.risk_level}

Reasons:
{reasons}

## Required Fixes

{fixes}

## Files Likely Involved

{likely_files}

## Safety Constraints

- Do not modify `.env`, `.env.local`, secrets, deployment files, or git history.
- Do not run destructive commands.
- Do not deploy.
- Do not add dependencies unless explicitly required and approved.
- Keep the fix scoped to the QA findings.
- Do not auto-commit.

## Validation Commands

```bash
{project.lint_command or '# no lint command configured'}
{project.typecheck_command or '# no typecheck command configured'}
{project.build_command or '# no build command configured'}
{project.test_command or '# no test command configured'}
```

## Stop / Report Format

When done, report:
1. Files modified.
2. Exact fixes made.
3. Commands run and results.
4. Remaining risks.
5. Current git status.
"""
