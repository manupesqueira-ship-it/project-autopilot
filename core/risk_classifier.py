from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any


@dataclass(frozen=True)
class RiskAssessment:
    risk_level: str
    categories: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    recommended_action: str = "proceed"


KEYWORD_RULES = {
    "destructive_risk": [
        r"\bdelete\b",
        r"\bremove-item\b",
        r"(^|\s)rm(\s|$)",
        r"\brmdir\b",
        r"\bgit\s+reset\b",
        r"\bgit\s+clean\b",
        r"\bdrop\s+table\b",
        r"\btruncate\b",
    ],
    "deploy_risk": [r"\bdeploy\b", r"\bdeployment\b", r"\bvercel\s+--prod\b", r"\bproduction\b", r"\brelease\b"],
    "secrets_risk": [r"\.env\b", r"\.env\.local\b", r"\bsecret\b", r"\btoken\b", r"\bapi\s+key\b", r"\bcredential\b", r"\bprivate\s+key\b"],
    "paid_api_risk": [r"\bpaid\s+api\b", r"\bbilling\b", r"\bquota\b", r"\bimage\s+generation\b", r"\bvideo\s+generation\b", r"\bopenai\s+image\b", r"\bseedance\b"],
    "data_schema_change": [r"\bschema\b", r"\bmigration\b", r"\bdatabase\b", r"\bsupabase\b", r"\btable\b", r"\brls\b", r"\bpolicy\b"],
    "product_behavior_change": [r"\bfeature\b", r"\bui\b", r"\broute\b", r"\bworkflow\b", r"\bonboarding\b", r"\bcheckout\b", r"\bauth\b"],
    "research_required": [r"\bresearch\b", r"\blatest\b", r"\bcurrent\b", r"\bpricing\b", r"\bregulation\b", r"\bcompliance\b"],
    "human_decision_required": [r"\bapprove\b", r"\bapproval\b", r"\bdecision\b", r"\bstrategy\b", r"\blegal\b", r"\bprivacy\b"],
}

PATH_RULES = {
    "secrets_risk": [".env", ".env.local", ".pem", ".key"],
    "deploy_risk": ["vercel.json", ".vercel", "netlify.toml", "Dockerfile", "docker-compose"],
    "data_schema_change": ["supabase/", "schema.sql", "migrations/"],
    "product_behavior_change": ["app/", "components/", "styles/"],
}

RISK_ORDER = ["low", "medium", "high", "critical"]


def _contains_any(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        prefix = text[max(0, match.start() - 24):match.start()].lower()
        if any(negation in prefix for negation in ["do not ", "don't ", "not ", "no "]):
            continue
        return pattern
    return None


def classify_task(
    title: str,
    body: str = "",
    changed_files: list[str] | None = None,
    project_control_context: dict[str, str] | None = None,
) -> RiskAssessment:
    text = f"{title}\n{body}".lower()
    changed_files = changed_files or []
    categories: list[str] = []
    reasons: list[str] = []

    for category, needles in KEYWORD_RULES.items():
        match = _contains_any(text, needles)
        if match:
            categories.append(category)
            reasons.append(f"Matched keyword '{match}' for {category}.")

    for path in changed_files:
        normalized = path.replace("\\", "/")
        for category, needles in PATH_RULES.items():
            match = _contains_any(normalized, needles)
            if match:
                categories.append(category)
                reasons.append(f"Changed path '{path}' matched {category}.")

    categories = sorted(dict.fromkeys(categories))
    if not categories:
        return RiskAssessment("low", ["safe_local_change"], ["No high-risk keywords or paths detected."], "proceed")

    if "destructive_risk" in categories or "secrets_risk" in categories:
        return RiskAssessment("critical", categories, reasons, "block")
    if "deploy_risk" in categories or "paid_api_risk" in categories or "human_decision_required" in categories:
        return RiskAssessment("high", categories, reasons, "require_human_decision")
    if "data_schema_change" in categories or "product_behavior_change" in categories or "research_required" in categories:
        return RiskAssessment("medium", categories, reasons, "proceed_with_qa")
    return RiskAssessment("low", categories, reasons, "proceed")


def format_risk_assessment(assessment: RiskAssessment) -> str:
    return (
        f"Risk level: {assessment.risk_level}\n"
        f"Categories: {', '.join(assessment.categories)}\n"
        f"Recommended action: {assessment.recommended_action}\n"
        "Reasons:\n"
        + "\n".join(f"- {reason}" for reason in assessment.reasons)
    )
