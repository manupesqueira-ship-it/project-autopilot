from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import ProjectConfig, load_project_config


DECISIONS = {
    "PROCEED_TO_SANDBOX_DESIGN",
    "NEEDS_POLICY_FIXTURE",
    "NEEDS_RESEARCH",
    "BLOCKED",
    "HUMAN_REVIEW_REQUIRED",
}

CATEGORY_RULES: list[dict[str, Any]] = [
    {
        "category": "provider_routing",
        "patterns": ["provider routing", "provider whitelist", "unvetted provider", "incorrect provider"],
        "gate": "provider_gate",
        "severity": "HIGH",
        "required_action": "Keep provider routing behind registry metadata and fixture-test unapproved provider routing.",
        "implications": ["fixture_gap", "documentation_gap"],
        "fixture": "provider_routing_mismatch_requires_human_review",
    },
    {
        "category": "policy_gate_bypass",
        "patterns": ["policy gate bypass", "circumvent policy", "skip gate", "gates execute", "gate evaluation"],
        "gate": "post_builder_policy",
        "severity": "HIGH",
        "required_action": "Policy gates must run before and after any future Claude builder context.",
        "implications": ["fixture_gap", "documentation_gap"],
        "fixture": "policy_gate_bypass_blocks_builder_execution",
    },
    {
        "category": "evidence_integrity",
        "patterns": ["evidence", "immutable", "audited sources", "doesn't exist", "false confidence"],
        "gate": "evidence_gate",
        "severity": "HIGH",
        "required_action": "Require existing evidence paths and blocker acknowledgment before any safe-commit decision.",
        "implications": ["fixture_gap"],
        "fixture": "evidence_missing_blocks_safe_commit",
    },
    {
        "category": "blocker_integrity",
        "patterns": ["blocker", "blockers", "cached", "stale"],
        "gate": "human_approval_gate",
        "severity": "HIGH",
        "required_action": "Fetch blockers fresh and fail closed when blockers are stale or contradictory.",
        "implications": ["fixture_gap"],
        "fixture": "evidence_missing_blocks_safe_commit",
    },
    {
        "category": "sandbox_escape",
        "patterns": ["sandbox escape", "host system", "breakout", "outside the intended sandbox"],
        "gate": "human_approval_gate",
        "severity": "CRITICAL",
        "required_action": "Design sandbox/worktree isolation before any Claude builder execution.",
        "implications": ["fixture_gap", "sandbox"],
        "fixture": "sandbox_tool_escape_blocked",
    },
    {
        "category": "tool_escape",
        "patterns": ["tool access", "implicit access", "file i/o", "shell", "credential api", "minimal capability"],
        "gate": "human_approval_gate",
        "severity": "CRITICAL",
        "required_action": "Require explicit tool allowlist/denylist and keep no-tools default.",
        "implications": ["fixture_gap", "sandbox"],
        "fixture": "sandbox_tool_escape_blocked",
    },
    {
        "category": "command_execution_risk",
        "patterns": ["command execution", "execute commands", "shell command"],
        "gate": "human_approval_gate",
        "severity": "CRITICAL",
        "required_action": "Block command execution unless a future allowlisted sandbox sprint is approved.",
        "implications": ["fixture_gap", "sandbox"],
        "fixture": "sandbox_tool_escape_blocked",
    },
    {
        "category": "commit_safety",
        "patterns": ["commit safety", "unsafe commits", "safe commit", "commit signing", "auto-merge"],
        "gate": "definition_of_done_gate",
        "severity": "HIGH",
        "required_action": "Keep post-builder policy as the commit authority and block auto-merge without rollback.",
        "implications": ["fixture_gap"],
        "fixture": "rollback_missing_blocks_auto_merge",
    },
    {
        "category": "rollback_readiness",
        "patterns": ["rollback", "safe abort", "rejection flow"],
        "gate": "definition_of_done_gate",
        "severity": "HIGH",
        "required_action": "Document and fixture-test rejection and rollback flow before sandboxed builder execution.",
        "implications": ["fixture_gap", "documentation_gap"],
        "fixture": "rollback_missing_blocks_auto_merge",
    },
    {
        "category": "worktree_isolation",
        "patterns": ["worktree", "parallel writes", "isolation"],
        "gate": "scope_gate",
        "severity": "HIGH",
        "required_action": "Require a dedicated worktree for any future Claude builder write mode.",
        "implications": ["fixture_gap", "sandbox"],
        "fixture": "worktree_required_for_builder_execution",
    },
]


@dataclass(frozen=True)
class ReviewFinding:
    title: str
    category: str
    policy_gate: str
    severity: str
    required_action: str
    implications: list[str]
    coverage_status: str
    evidence_excerpt: str
    fixture_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ClaudeAnalysisReview:
    project_id: str
    generated_at_utc: str
    decision: str
    proceed_to_sandbox_design: bool
    source_response_path: str
    source_metadata_path: str
    findings: list[ReviewFinding] = field(default_factory=list)
    extracted_risks: list[str] = field(default_factory=list)
    gate_mappings: dict[str, list[str]] = field(default_factory=dict)
    required_actions: list[str] = field(default_factory=list)
    fixture_recommendations: list[str] = field(default_factory=list)
    research_recommendations: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    next_action: str = ""
    external_api_called: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "generated_at_utc": self.generated_at_utc,
            "decision": self.decision,
            "proceed_to_sandbox_design": self.proceed_to_sandbox_design,
            "source_response_path": self.source_response_path,
            "source_metadata_path": self.source_metadata_path,
            "findings": [finding.to_dict() for finding in self.findings],
            "extracted_risks": self.extracted_risks,
            "gate_mappings": self.gate_mappings,
            "required_actions": self.required_actions,
            "fixture_recommendations": self.fixture_recommendations,
            "research_recommendations": self.research_recommendations,
            "blockers": self.blockers,
            "next_action": self.next_action,
            "external_api_called": self.external_api_called,
        }


def _latest_dir(project: ProjectConfig) -> Path:
    return project.repo_path / project.logs_dir / "claude" / project.project_id / "latest"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _fixture_ids_available() -> set[str]:
    try:
        from policy_test_fixtures import fixtures

        return {fixture.fixture_id for fixture in fixtures()}
    except Exception:
        return set()


def _extract_risk_titles(response_text: str) -> list[str]:
    titles: list[str] = []
    for line in response_text.splitlines():
        stripped = line.strip()
        match = re.match(r"^#{2,3}\s+\d+\.\s+\**(.+?)\**\s*$", stripped)
        if match:
            titles.append(match.group(1).strip("* "))
            continue
        match = re.match(r"^\d+\.\s+\**(.+?)\**\s*$", stripped)
        if match:
            titles.append(match.group(1).strip("* "))
    return titles[:8]


def _excerpt_for(text: str, patterns: list[str], max_chars: int = 220) -> str:
    lower = text.lower()
    best = -1
    for pattern in patterns:
        idx = lower.find(pattern.lower())
        if idx >= 0 and (best == -1 or idx < best):
            best = idx
    if best == -1:
        return ""
    start = max(0, best - 80)
    end = min(len(text), best + max_chars)
    return " ".join(text[start:end].split())


def _coverage_for(fixture_id: str, available_fixtures: set[str]) -> str:
    if not fixture_id:
        return "DOCUMENTED"
    return "COVERED" if fixture_id in available_fixtures else "FIXTURE_MISSING"


def review_latest(project: ProjectConfig) -> ClaudeAnalysisReview:
    latest = _latest_dir(project)
    response_path = latest / "claude_analysis_response.md"
    metadata_path = latest / "claude_analysis_metadata.json"
    response_text = _read_text(response_path)
    metadata = _read_json(metadata_path)
    available_fixtures = _fixture_ids_available()

    if not response_text or not metadata:
        return ClaudeAnalysisReview(
            project_id=project.project_id,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            decision="HUMAN_REVIEW_REQUIRED",
            proceed_to_sandbox_design=False,
            source_response_path=str(response_path),
            source_metadata_path=str(metadata_path),
            blockers=["Latest Claude analysis evidence is missing or incomplete."],
            next_action="Run one approved controlled Claude analysis call before reviewing recommendations.",
        )

    if metadata.get("secrets_sent") or not metadata.get("no_tools", True) or not metadata.get("no_commands", True):
        return ClaudeAnalysisReview(
            project_id=project.project_id,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            decision="BLOCKED",
            proceed_to_sandbox_design=False,
            source_response_path=str(response_path),
            source_metadata_path=str(metadata_path),
            blockers=["Latest Claude analysis metadata violates no-secrets/no-tools/no-commands safety expectations."],
            next_action="Discard unsafe evidence and rerun only after prompt safety is repaired.",
        )

    findings: list[ReviewFinding] = []
    lower = response_text.lower()
    for rule in CATEGORY_RULES:
        if not any(pattern.lower() in lower for pattern in rule["patterns"]):
            continue
        fixture_id = str(rule.get("fixture", ""))
        coverage = _coverage_for(fixture_id, available_fixtures)
        findings.append(
            ReviewFinding(
                title=str(rule["category"]).replace("_", " ").title(),
                category=str(rule["category"]),
                policy_gate=str(rule["gate"]),
                severity=str(rule["severity"]),
                required_action=str(rule["required_action"]),
                implications=list(rule["implications"]),
                coverage_status=coverage,
                evidence_excerpt=_excerpt_for(response_text, list(rule["patterns"])),
                fixture_id=fixture_id,
            )
        )

    gate_mappings: dict[str, list[str]] = {}
    for finding in findings:
        gate_mappings.setdefault(finding.policy_gate, []).append(finding.category)

    fixture_recommendations = sorted(
        {
            finding.fixture_id
            for finding in findings
            if finding.fixture_id and finding.coverage_status == "FIXTURE_MISSING"
        }
    )
    required_actions = sorted({finding.required_action for finding in findings})
    research_recommendations: list[str] = []
    if any(f.category in {"sandbox_escape", "tool_escape", "command_execution_risk"} for f in findings):
        research_recommendations.append(
            "Optional before implementation: evaluate sandboxed AI coding agent isolation patterns, command allowlists, rollback, and approval gates."
        )

    if not findings:
        decision = "HUMAN_REVIEW_REQUIRED"
        proceed = False
        next_action = "Manually review the latest Claude response; no known risk categories were extracted."
    elif fixture_recommendations:
        decision = "NEEDS_POLICY_FIXTURE"
        proceed = False
        next_action = "Add deterministic policy fixtures for uncovered risks, rerun policy fixtures, then rerun this review."
    elif any(f.severity == "CRITICAL" and f.coverage_status != "COVERED" for f in findings):
        decision = "BLOCKED"
        proceed = False
        next_action = "Critical Claude-builder safety coverage is incomplete; do not proceed to sandbox design."
    else:
        decision = "PROCEED_TO_SANDBOX_DESIGN"
        proceed = True
        next_action = "Proceed to a sandboxed Claude builder design sprint only; keep builder execution, scheduler, auto-merge, deploy, and live DB changes disabled."

    return ClaudeAnalysisReview(
        project_id=project.project_id,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        decision=decision,
        proceed_to_sandbox_design=proceed,
        source_response_path=str(response_path),
        source_metadata_path=str(metadata_path),
        findings=findings,
        extracted_risks=_extract_risk_titles(response_text),
        gate_mappings=gate_mappings,
        required_actions=required_actions,
        fixture_recommendations=fixture_recommendations,
        research_recommendations=research_recommendations,
        next_action=next_action,
    )


def write_review(project: ProjectConfig, review: ClaudeAnalysisReview) -> tuple[Path, Path]:
    out_dir = _latest_dir(project)
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "claude_analysis_review.md"
    json_path = out_dir / "claude_analysis_review.json"
    json_path.write_text(json.dumps(review.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Claude Analysis Review",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Generated: {review.generated_at_utc}",
        f"Decision: {review.decision}",
        f"Proceed to sandbox design: {'yes' if review.proceed_to_sandbox_design else 'no'}",
        "External API called by review: no",
        "",
        "## Input Evidence",
        f"- Response: {review.source_response_path}",
        f"- Metadata: {review.source_metadata_path}",
        "",
        "## Extracted Risks",
    ]
    lines.extend(f"- {risk}" for risk in review.extracted_risks or ["None extracted"])
    lines.extend(["", "## Gate Mappings"])
    if review.findings:
        for finding in review.findings:
            lines.append(
                f"- {finding.severity} `{finding.category}` -> `{finding.policy_gate}` "
                f"({finding.coverage_status})"
            )
            lines.append(f"  - Action: {finding.required_action}")
            if finding.fixture_id:
                lines.append(f"  - Fixture: `{finding.fixture_id}`")
    else:
        lines.append("- None")
    lines.extend(["", "## Fixture Recommendations"])
    lines.extend(f"- {item}" for item in review.fixture_recommendations or ["None"])
    lines.extend(["", "## Research Recommendations"])
    lines.extend(f"- {item}" for item in review.research_recommendations or ["None"])
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {item}" for item in review.blockers or ["None"])
    lines.extend(["", "## Next Action", review.next_action])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def latest_review_payload(project: ProjectConfig) -> dict[str, Any]:
    return _read_json(_latest_dir(project) / "claude_analysis_review.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Review saved Claude analysis and map it to Project Autopilot policy decisions")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--latest", action="store_true", help="Review latest saved Claude analysis evidence.")
    parser.add_argument("--status", action="store_true", help="Print latest saved review status.")
    args = parser.parse_args()

    project = load_project_config(args.project)
    if args.status:
        payload = latest_review_payload(project)
        if not payload:
            print("Claude Analysis Review: NOT_RUN")
            print(f"  Command: python -B project_autopilot/claude_analysis_review.py --project {project.project_id} --latest")
            return 0
        print(f"Claude Analysis Review: {payload.get('decision', 'UNKNOWN')}")
        print(f"  Proceed to sandbox design: {'yes' if payload.get('proceed_to_sandbox_design') else 'no'}")
        print(f"  Findings: {len(payload.get('findings', []))}")
        print(f"  Next action: {payload.get('next_action', '')}")
        return 0

    review = review_latest(project)
    md_path, json_path = write_review(project, review)
    print(f"Claude Analysis Review: {review.decision}")
    print(f"  Proceed to sandbox design: {'yes' if review.proceed_to_sandbox_design else 'no'}")
    print(f"  Extracted risks: {len(review.extracted_risks)}")
    print(f"  Findings: {len(review.findings)}")
    print(f"  Fixture recommendations: {', '.join(review.fixture_recommendations) if review.fixture_recommendations else 'none'}")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    print(f"  Next action: {review.next_action}")
    return 2 if review.decision == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
