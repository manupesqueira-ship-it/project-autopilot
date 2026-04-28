"""Quality director for Project Autopilot.

Generates structured quality instructions that prompt_builder and
openai_supervisor include in builder prompts and review calls.  Does not
call OpenAI directly — it produces text blocks from project control state.
"""
from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Checklist generators — return markdown text blocks
# ---------------------------------------------------------------------------

def world_class_summary(control_docs: dict[str, str]) -> str:
    """Extract a concise summary from WORLD_CLASS_STANDARD.md for inclusion in prompts."""
    raw = control_docs.get("WORLD_CLASS_STANDARD.md", "").strip()
    if not raw:
        return (
            "World-Class Standard: Every button must work. Every flow must complete. "
            "No silent failures. No data leaks. No regressions. No shallow approvals."
        )
    # Return the first ~1500 chars which covers all section headers and key points
    return raw[:1500]


def qa_protocol_summary(control_docs: dict[str, str]) -> str:
    """Extract QA protocol for builder prompts."""
    raw = control_docs.get("QA_PROTOCOL.md", "").strip()
    if not raw:
        return (
            "QA Protocol: Test every button, form, route, and state. "
            "Check console for errors. Verify database writes. "
            "Confirm acceptance criteria individually."
        )
    return raw[:1500]


def customer_data_summary(control_docs: dict[str, str]) -> str:
    """Extract customer data policy for builder prompts."""
    raw = control_docs.get("CUSTOMER_DATA_POLICY.md", "").strip()
    if not raw:
        return ""
    return raw[:1200]


def research_protocol_summary(control_docs: dict[str, str]) -> str:
    """Extract research protocol reminder."""
    raw = control_docs.get("RESEARCH_PROTOCOL.md", "").strip()
    if not raw:
        return (
            "Research Protocol: If you encounter uncertainty about a provider, "
            "pricing, legal requirement, or architecture decision, propose research "
            "with a scope and time estimate before proceeding."
        )
    # Return just the rules section — compact enough for prompt inclusion
    rules_idx = raw.find("## Rules")
    if rules_idx > 0:
        return raw[rules_idx:rules_idx + 600]
    return raw[:600]


# ---------------------------------------------------------------------------
# Risk scoring
# ---------------------------------------------------------------------------

def assess_task_risk(task_plan: str, evidence: dict[str, Any]) -> dict[str, Any]:
    """Heuristic risk assessment based on task content and evidence.

    Returns a dict with risk_level, flags, and recommendations.
    This is deterministic and local — no API call.
    """
    flags: list[str] = []
    plan_lower = task_plan.lower()

    # Check for high-risk keywords in the task plan
    if any(w in plan_lower for w in ["auth", "login", "session", "password", "token"]):
        flags.append("auth_related")
    if any(w in plan_lower for w in ["delete", "drop", "truncate", "remove", "destroy"]):
        flags.append("destructive_operation")
    if any(w in plan_lower for w in ["deploy", "production", "release", "publish"]):
        flags.append("deployment_related")
    if any(w in plan_lower for w in ["payment", "billing", "stripe", "charge", "subscription"]):
        flags.append("payment_related")
    if any(w in plan_lower for w in ["migration", "schema", "alter table", "add column"]):
        flags.append("schema_change")
    if any(w in plan_lower for w in ["photo", "image", "biometric", "body", "scan"]):
        flags.append("sensitive_data")
    if any(w in plan_lower for w in ["provider", "api key", "external api", "third party"]):
        flags.append("external_dependency")

    # Check evidence for build/test failures
    commands = evidence.get("commands", {})
    for name, result in commands.items():
        if result.get("exit_code", 0) != 0:
            flags.append(f"failing_{name}")

    # Determine risk level
    critical_flags = {"auth_related", "payment_related", "destructive_operation", "deployment_related"}
    high_flags = {"schema_change", "sensitive_data", "external_dependency"}

    if critical_flags & set(flags):
        risk_level = "critical"
    elif high_flags & set(flags):
        risk_level = "high"
    elif any(f.startswith("failing_") for f in flags):
        risk_level = "high"
    elif flags:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "risk_level": risk_level,
        "flags": flags,
        "recommendations": _risk_recommendations(flags),
    }


def _risk_recommendations(flags: list[str]) -> list[str]:
    recs: list[str] = []
    if "auth_related" in flags:
        recs.append("Auth changes require human approval. Document the auth boundary.")
    if "destructive_operation" in flags:
        recs.append("Destructive operations are blocked by AGENT_RULES. Escalate to human.")
    if "deployment_related" in flags:
        recs.append("Deployment requires explicit human action. Do not deploy from Autopilot.")
    if "payment_related" in flags:
        recs.append("Payment integration requires human approval and Telegram escalation.")
    if "schema_change" in flags:
        recs.append("Schema changes require human approval. Document the migration.")
    if "sensitive_data" in flags:
        recs.append("Review CUSTOMER_DATA_POLICY.md. Ensure no data leaks in logs or prompts.")
    if "external_dependency" in flags:
        recs.append("Research the provider's pricing, rate limits, and reliability before integrating.")
    for f in flags:
        if f.startswith("failing_"):
            name = f.replace("failing_", "")
            recs.append(f"Fix the failing {name} before proceeding with new work.")
    return recs


# ---------------------------------------------------------------------------
# Composite quality block for prompt injection
# ---------------------------------------------------------------------------

def quality_block_for_prompt(control_docs: dict[str, str], evidence: dict[str, Any], task_plan: str = "") -> str:
    """Build the full quality context block for inclusion in builder prompts."""
    sections: list[str] = []

    wcs = world_class_summary(control_docs)
    if wcs:
        sections.append(f"WORLD_CLASS_STANDARD.md (summary):\n{wcs}")

    qa = qa_protocol_summary(control_docs)
    if qa:
        sections.append(f"QA_PROTOCOL.md (summary):\n{qa}")

    cdp = customer_data_summary(control_docs)
    if cdp:
        sections.append(f"CUSTOMER_DATA_POLICY.md (summary):\n{cdp}")

    rp = research_protocol_summary(control_docs)
    if rp:
        sections.append(f"RESEARCH_PROTOCOL.md:\n{rp}")

    if task_plan:
        risk = assess_task_risk(task_plan, evidence)
        if risk["flags"]:
            risk_lines = [f"Risk level: {risk['risk_level']}"]
            risk_lines.extend(f"- {r}" for r in risk["recommendations"])
            sections.append("Risk assessment:\n" + "\n".join(risk_lines))

    # Browser QA evidence
    browser_qa = evidence.get("browser_qa_report")
    if browser_qa:
        sections.append(f"Browser QA report available: {browser_qa}\nReview route walk results, console errors, and screenshots.")
    elif evidence.get("route_walk_urls"):
        sections.append(
            "Browser QA: No report yet. Run --browser-qa with dev server running to collect "
            "route walk evidence, screenshots, and console error checks."
        )

    sections.append(
        "IMPORTANT: Do not mark this task as complete until all relevant QA checks "
        "from QA_PROTOCOL.md have been performed and documented in your report. "
        "Every button, form, and link on affected pages must work. "
        "Console must show zero errors. Network requests must succeed."
    )

    return "\n\n".join(sections)
