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

from backend_audit import run_backend_audit
from config import ProjectConfig, load_project_config
from design_director import run_design_review, write_reports as write_design_reports
from evidence_collector import collect_evidence
from provider_registry import build_registry, _write_reports as write_provider_reports
from qa_reviewer import QAVerdict
from research_director import classify_research_need, status_payload as research_status_payload, write_status as write_research_status
from risk_classifier import RiskAssessment, classify_task


POLICY_VERDICTS = {"SAFE_TO_COMMIT", "NEEDS_FIX", "BLOCKED", "HUMAN_REVIEW_REQUIRED", "SAFE_NO_CHANGES"}
SEVERITIES = {"PASS", "WARN", "FAIL", "BLOCKED", "NOT_APPLICABLE"}

FORBIDDEN_FILE_PATTERNS = [
    r"(^|/)\.env($|[./])",
    r"(^|/)\.env\.local$",
    r"(^|/)\.env\..*",
    r"(^|/)node_modules/",
    r"(^|/)\.next/",
    r"(^|/)package-lock\.json$",
    r"(^|/)logs/",
    r"(^|/)screenshots/",
]

SECRET_WORDS = ["secret", "jwt", "cookie", "service_role", "password", "private key", "api key"]
SECRET_NEGATION_WORDS = ["no secrets", "secrets sent false", "secrets_sent false", "without secrets", "secret values remain hidden"]
SQL_WORDS = ["execute sql", "ran sql", "enable rls", "create policy", "drop table", "truncate", "alter table"]
PAID_WORDS = ["paid api", "openai image", "seedance", "byteplus", "billing", "charged", "real generation"]
SCHEDULER_WORDS = ["enabled scheduler", "systemd timer enabled", "automatic schedule"]
AUTO_CLAUDE_WORDS = ["automatic claude execution", "--claude-execute", "allow_automatic_builder_execution: true"]
AUTO_CLAUDE_NEGATION_WORDS = ["automatic claude execution remains disabled", "automatic claude execution disabled", "auto-claude disabled"]
CLAUDE_SDK_LIVE_WORDS = ["claude agent sdk live", "live claude sdk", "called claude agent sdk", "anthropic api call"]
CLAUDE_SDK_APPROVAL_WORDS = ["explicit human approval", "approval granted", "human approved live claude"]
CLAUDE_SDK_NEGATION_WORDS = ["no anthropic api call", "no live claude", "no external call", "without calling anthropic"]


@dataclass(frozen=True)
class TaskCharacteristics:
    touches_ui: bool = False
    touches_backend: bool = False
    touches_security: bool = False
    touches_supabase: bool = False
    touches_docs_only: bool = False
    touches_provider_system: bool = False
    touches_design_system: bool = False
    touches_research_system: bool = False
    touches_flow_qa: bool = False
    touches_control_center: bool = False
    touches_env_or_secrets: bool = False
    touches_deploy: bool = False
    touches_paid_api: bool = False
    requires_design_review: bool = False
    requires_research_review: bool = False
    requires_backend_audit: bool = False
    requires_flow_qa: bool = False
    requires_mock_e2e: bool = False
    requires_human_approval: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PolicyGateResult:
    gate_type: str
    severity: str
    message: str
    required_fixes: list[str] = field(default_factory=list)
    human_decisions_needed: list[str] = field(default_factory=list)
    evidence_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PolicyVerdict:
    verdict: str
    safe_commit_allowed: bool
    correction_prompt_recommended: bool
    human_review_required: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PostBuilderPolicyReport:
    project_id: str
    generated_at_utc: str
    policy_verdict: PolicyVerdict
    characteristics: TaskCharacteristics
    gate_results: list[PolicyGateResult]
    failed_gates: list[str]
    warnings: list[str]
    required_fixes: list[str]
    human_decisions_needed: list[str]
    evidence_paths: list[str]
    changed_files: list[str]
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "generated_at_utc": self.generated_at_utc,
            "policy_verdict": self.policy_verdict.to_dict(),
            "characteristics": self.characteristics.to_dict(),
            "gate_results": [gate.to_dict() for gate in self.gate_results],
            "failed_gates": self.failed_gates,
            "warnings": self.warnings,
            "required_fixes": self.required_fixes,
            "human_decisions_needed": self.human_decisions_needed,
            "evidence_paths": self.evidence_paths,
            "changed_files": self.changed_files,
            "next_action": self.next_action,
        }


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip()


def _mentions_any(text: str, words: list[str]) -> bool:
    lower = text.lower()
    return any(word in lower for word in words)


def _extract_report_paths(report_text: str) -> list[str]:
    paths: list[str] = []
    for line in report_text.splitlines():
        if not re.search(r"file|modified|created|changed|deleted|path", line, flags=re.IGNORECASE):
            continue
        for match in re.findall(r"[\w./\\\[\]\(\)-]+\.(?:py|ts|tsx|js|jsx|md|json|yaml|yml|sql|env|local|toml|lock)", line):
            paths.append(_norm(match))
    return sorted(dict.fromkeys(paths))


def classify_task_characteristics(changed_files: list[str], report_text: str, risk: RiskAssessment | None = None) -> TaskCharacteristics:
    paths = [_norm(path) for path in changed_files] + _extract_report_paths(report_text)
    text = f"{report_text}\n" + "\n".join(paths)
    lower = text.lower()

    touches_ui = any(path.startswith(("app/", "components/")) for path in paths) or any(word in lower for word in ["ui", "design", "visual", "page"])
    touches_backend = any(path.startswith(("app/api/", "lib/supabase", "supabase/")) for path in paths) or any(word in lower for word in ["backend", "database", "api route"])
    # Treat security/database policy work as sensitive, but do not flag generic
    # Project Autopilot policy modules/docs as live Supabase/RLS policy changes.
    touches_security = any(word in lower for word in ["security", "auth", "rls", "privacy", "ownership"]) or (
        "policy" in lower and any(word in lower for word in ["supabase", "database", "storage", "live sql", "customer data"])
    )
    touches_supabase = any("supabase" in path.lower() for path in paths) or "supabase" in lower
    touches_provider = any(path.startswith("project_autopilot/providers") for path in paths) or "provider" in lower
    touches_design_system = any("design_director" in path or "design_" in path or "rubric" in path for path in paths)
    touches_research = any("research" in path or "research" in lower for path in paths)
    touches_flow_qa = any("flow_qa" in path or "browser_qa" in path for path in paths)
    touches_control_center = any("control_center" in path for path in paths)
    secret_language_risk = _mentions_any(lower, SECRET_WORDS) and not _mentions_any(lower, SECRET_NEGATION_WORDS)
    touches_env = any(re.search(pattern, path, flags=re.IGNORECASE) for path in paths for pattern in FORBIDDEN_FILE_PATTERNS[:3]) or secret_language_risk
    touches_deploy = any(word in lower for word in ["deploy", "vercel", "production deployment", "dockerfile", "systemd"])
    touches_paid = _mentions_any(lower, PAID_WORDS)
    touches_claude_sdk_live = _mentions_any(lower, CLAUDE_SDK_LIVE_WORDS)
    touches_product_api = any(path.startswith("app/api/") for path in paths)

    code_paths = [p for p in paths if not p.startswith("project_control/") and not p.endswith(".md")]
    docs_only = bool(paths) and not code_paths
    risk_categories = set(risk.categories if risk else [])
    requires_research = touches_paid or touches_security or touches_deploy or touches_claude_sdk_live or "research_required" in risk_categories
    requires_backend = touches_backend or touches_security or touches_supabase or "data_schema_change" in risk_categories

    return TaskCharacteristics(
        touches_ui=touches_ui,
        touches_backend=touches_backend,
        touches_security=touches_security,
        touches_supabase=touches_supabase,
        touches_docs_only=docs_only,
        touches_provider_system=touches_provider,
        touches_design_system=touches_design_system,
        touches_research_system=touches_research,
        touches_flow_qa=touches_flow_qa,
        touches_control_center=touches_control_center,
        touches_env_or_secrets=touches_env,
        touches_deploy=touches_deploy,
        touches_paid_api=touches_paid,
        requires_design_review=touches_ui or touches_design_system,
        requires_research_review=requires_research,
        requires_backend_audit=requires_backend,
        requires_flow_qa=touches_ui or touches_flow_qa or touches_product_api,
        requires_mock_e2e=touches_ui or touches_flow_qa or touches_product_api,
        requires_human_approval=touches_env or touches_deploy or touches_paid or touches_security,
    )


def _gate(gate_type: str, severity: str, message: str, fixes: list[str] | None = None, decisions: list[str] | None = None, evidence: list[str] | None = None) -> PolicyGateResult:
    return PolicyGateResult(
        gate_type=gate_type,
        severity=severity,
        message=message,
        required_fixes=fixes or [],
        human_decisions_needed=decisions or [],
        evidence_paths=evidence or [],
    )


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _flow_qa_latest(project: ProjectConfig) -> tuple[str, str]:
    report = project.repo_path / project.logs_dir / "flow_qa" / project.project_id / "latest" / "validation_summary.md"
    results = project.repo_path / project.logs_dir / "flow_qa" / project.project_id / "latest" / "flow_results.json"
    if not results.exists():
        return "NOT_RUN", str(report.relative_to(project.repo_path)) if report.exists() else ""
    try:
        raw = json.loads(results.read_text(encoding="utf-8"))
        rows = raw if isinstance(raw, list) else [raw]
        statuses = [row.get("status", "UNKNOWN") for row in rows]
    except Exception:
        return "ERROR", str(results.relative_to(project.repo_path))
    if "FAIL" in statuses:
        verdict = "FAIL"
    elif "BLOCKED" in statuses:
        verdict = "BLOCKED"
    elif "WARN" in statuses:
        verdict = "WARN"
    elif statuses and all(s in {"PASS", "SKIPPED"} for s in statuses):
        verdict = "PASS" if "PASS" in statuses else "SKIPPED"
    else:
        verdict = "UNKNOWN"
    return verdict, str(report.relative_to(project.repo_path)) if report.exists() else str(results.relative_to(project.repo_path))


def _contains_forbidden_file(files: list[str]) -> list[str]:
    bad: list[str] = []
    for path in files:
        normalized = _norm(path)
        if any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in FORBIDDEN_FILE_PATTERNS):
            bad.append(path)
    return sorted(dict.fromkeys(bad))


def _unexpected_files(files: list[str], allowed_prefixes: list[str] | None = None) -> list[str]:
    allowed_prefixes = allowed_prefixes or ["project_autopilot/", "project_control/"]
    allowed_exact = {".gitignore"}
    unexpected = []
    for path in files:
        normalized = _norm(path)
        if normalized.startswith("logs/") or normalized.startswith("screenshots/"):
            unexpected.append(path)
            continue
        if normalized in allowed_exact:
            continue
        if not any(normalized.startswith(prefix) for prefix in allowed_prefixes):
            unexpected.append(path)
    return sorted(dict.fromkeys(unexpected))


def evaluate_post_builder_policy(
    project: ProjectConfig,
    builder_report_text: str,
    evidence: dict[str, Any],
    qa_verdict: QAVerdict | None = None,
    risk: RiskAssessment | None = None,
    run_required_gates: bool = True,
) -> PostBuilderPolicyReport:
    changed_files = evidence.get("changed_files", [])
    risk = risk or classify_task("Post-builder review", body=builder_report_text, changed_files=changed_files)
    characteristics = classify_task_characteristics(changed_files, builder_report_text, risk)
    gates: list[PolicyGateResult] = []
    evidence_paths: list[str] = []

    # Provider gate
    provider_payload = build_registry(project.project_id)
    provider_md, provider_json = write_provider_reports(project.project_id, provider_payload)
    evidence_paths.extend([str(provider_md), str(provider_json)])
    providers_ok = provider_payload.get("configured_provider_count", 0) >= 1
    missing_future = sorted({name for provider in provider_payload.get("providers", []) for name in provider.get("missing_env_vars", [])})
    gates.append(_gate(
        "provider_gate",
        "PASS" if providers_ok else "FAIL",
        f"{provider_payload.get('configured_provider_count', 0)}/{provider_payload.get('provider_count', 0)} providers configured.",
        fixes=[] if providers_ok else ["Configure at least one builder provider."],
        evidence=[str(provider_md)],
    ))
    if missing_future:
        gates.append(_gate("provider_gate", "WARN", f"Future provider env vars missing: {', '.join(missing_future)}.", evidence=[str(provider_md)]))

    # Scope and forbidden files
    bad_files = _contains_forbidden_file(changed_files + _extract_report_paths(builder_report_text))
    gates.append(_gate(
        "forbidden_files_gate",
        "BLOCKED" if bad_files else "PASS",
        f"Forbidden files touched or reported: {', '.join(bad_files)}" if bad_files else "No forbidden files detected.",
        fixes=["Remove forbidden file changes from the worktree and redo safely."] if bad_files else [],
    ))
    unexpected = _unexpected_files(changed_files)
    gates.append(_gate(
        "scope_gate",
        "WARN" if unexpected else "PASS",
        f"Unexpected changed files for control-plane sprint: {', '.join(unexpected)}" if unexpected else "Changed files are within expected Project Autopilot/control scope.",
        fixes=["Review unexpected changed files and confirm they belong to the task."] if unexpected else [],
    ))

    # Hard safety gates based on report text and paths.
    lower = builder_report_text.lower()
    safety_blocks: list[str] = []
    if characteristics.touches_env_or_secrets:
        safety_blocks.append("Secrets/env risk detected.")
    if _mentions_any(lower, SQL_WORDS):
        safety_blocks.append("SQL/RLS/storage mutation language detected.")
    if characteristics.touches_paid_api:
        safety_blocks.append("Paid API risk detected.")
    if _mentions_any(lower, SCHEDULER_WORDS):
        safety_blocks.append("Scheduler enablement language detected.")
    if _mentions_any(lower, AUTO_CLAUDE_WORDS) and not _mentions_any(lower, AUTO_CLAUDE_NEGATION_WORDS):
        safety_blocks.append("Automatic Claude execution language detected.")
    claude_live_without_approval = (
        _mentions_any(lower, CLAUDE_SDK_LIVE_WORDS)
        and not _mentions_any(lower, CLAUDE_SDK_APPROVAL_WORDS)
        and not _mentions_any(lower, CLAUDE_SDK_NEGATION_WORDS)
    )
    if claude_live_without_approval:
        safety_blocks.append("Claude Agent SDK live call without explicit approval detected.")
    gates.append(_gate(
        "secrets_env_gate",
        "BLOCKED" if any("Secrets/env" in item for item in safety_blocks) else "PASS",
        "Secrets/env risk blocked." if any("Secrets/env" in item for item in safety_blocks) else "No secrets/env risk detected.",
        decisions=["Human approval required for any env/secret handling."] if any("Secrets/env" in item for item in safety_blocks) else [],
    ))
    gates.append(_gate(
        "human_approval_gate",
        "BLOCKED" if safety_blocks else ("WARN" if characteristics.requires_human_approval else "PASS"),
        "; ".join(safety_blocks) if safety_blocks else ("Human approval likely required for this risk profile." if characteristics.requires_human_approval else "No human approval gate triggered."),
        decisions=safety_blocks if safety_blocks else (["Human approval required before proceeding."] if characteristics.requires_human_approval else []),
    ))

    # Validation gate.
    failed_commands = [
        f"{name} exit {result.get('exit_code')}"
        for name, result in evidence.get("commands", {}).items()
        if result.get("exit_code") not in (0, None)
    ]
    gates.append(_gate(
        "validation_gate",
        "FAIL" if failed_commands else "PASS",
        f"Validation command failures: {', '.join(failed_commands)}" if failed_commands else "Configured validation commands passed or were skipped safely.",
        fixes=[f"Fix failing validation: {item}" for item in failed_commands],
    ))

    # Risk gate.
    gates.append(_gate(
        "risk_gate",
        "BLOCKED" if risk.recommended_action == "block" else ("WARN" if risk.risk_level in {"medium", "high"} else "PASS"),
        f"Risk level: {risk.risk_level}; categories: {', '.join(risk.categories)}; action: {risk.recommended_action}",
        decisions=risk.reasons if risk.recommended_action == "require_human_decision" else [],
    ))

    # QA gate.
    if qa_verdict:
        qa_sev = "PASS"
        fixes = []
        decisions = []
        if qa_verdict.verdict == "FAIL_FIX_REQUIRED":
            qa_sev = "FAIL"
            fixes = qa_verdict.required_fixes
        elif qa_verdict.verdict == "BLOCKED":
            qa_sev = "BLOCKED"
            decisions = qa_verdict.human_decisions_needed or qa_verdict.reasons
        elif qa_verdict.verdict in {"HUMAN_DECISION_REQUIRED", "RESEARCH_REQUIRED"}:
            qa_sev = "WARN"
            decisions = qa_verdict.human_decisions_needed or qa_verdict.research_needed or qa_verdict.reasons
        gates.append(_gate("evidence_gate", qa_sev, f"Local QA verdict: {qa_verdict.verdict}", fixes=fixes, decisions=decisions))
    else:
        gates.append(_gate("evidence_gate", "WARN", "No QA verdict object was provided; policy check used working-tree evidence only."))

    # Design gate.
    if characteristics.requires_design_review:
        design = run_design_review(project) if run_required_gates else None
        design_paths: list[str] = []
        if design:
            md_path, json_path = write_design_reports(project, design)
            design_paths = [str(md_path), str(json_path)]
            evidence_paths.extend(design_paths)
            if design.verdict == "DESIGN_FAIL":
                sev = "FAIL"
            elif design.verdict == "DESIGN_REQUIRES_HUMAN_VISUAL_REVIEW":
                sev = "WARN"
            else:
                sev = "PASS" if design.verdict == "DESIGN_PASS" else "WARN"
            gates.append(_gate(
                "design_gate",
                sev,
                f"Design Director verdict: {design.verdict}",
                fixes=design.required_actions if sev == "FAIL" else [],
                decisions=["Human visual review required before UI/design approval."] if design.verdict == "DESIGN_REQUIRES_HUMAN_VISUAL_REVIEW" else [],
                evidence=design_paths,
            ))
        else:
            gates.append(_gate("design_gate", "WARN", "Design review required but not run in lightweight mode."))
    else:
        gates.append(_gate("design_gate", "NOT_APPLICABLE", "No UI/design-heavy change detected."))

    # Research gate.
    research_status, research_reasons = classify_research_need(builder_report_text + "\n" + "\n".join(changed_files))
    research_payload = research_status_payload(project)
    research_md, research_json = write_research_status(project, research_payload)
    evidence_paths.extend([str(research_md), str(research_json)])
    if characteristics.requires_research_review and research_status in {"RESEARCH_REQUIRED", "DECISION_BLOCKED_RESEARCH_REQUIRED"}:
        gates.append(_gate(
            "research_gate",
            "WARN",
            f"{research_status}: {', '.join(research_reasons)}",
            decisions=["Complete or approve scoped research before committing this decision."],
            evidence=[str(research_md)],
        ))
    else:
        gates.append(_gate("research_gate", "PASS" if research_status == "NO_RESEARCH_REQUIRED" else "WARN", research_status, evidence=[str(research_md)]))

    # Backend gate.
    if characteristics.requires_backend_audit:
        summary, report_path = run_backend_audit(project) if run_required_gates else (None, None)
        if summary:
            evidence_paths.append(str(report_path))
            if summary.readiness == "BLOCKED":
                sev = "BLOCKED"
            elif summary.readiness == "PARTIAL_READY":
                sev = "WARN"
            elif summary.readiness == "UNKNOWN":
                sev = "WARN"
            else:
                sev = "PASS"
            gates.append(_gate(
                "backend_gate",
                sev,
                f"Backend audit readiness: {summary.readiness}",
                fixes=["Fix backend/schema/security blockers before commit."] if sev == "BLOCKED" else [],
                evidence=[str(report_path)],
            ))
        else:
            gates.append(_gate("backend_gate", "WARN", "Backend audit required but not run in lightweight mode."))
    else:
        gates.append(_gate("backend_gate", "NOT_APPLICABLE", "No backend/security-heavy change detected."))

    # Flow QA gate.
    if characteristics.requires_mock_e2e or characteristics.requires_flow_qa:
        flow_verdict, flow_path = _flow_qa_latest(project)
        sev = "PASS" if flow_verdict in {"PASS", "WARN"} else "FAIL"
        gates.append(_gate(
            "flow_qa_gate",
            sev,
            f"Latest Flow QA/mock E2E verdict: {flow_verdict}",
            fixes=["Run and fix `python -B project_autopilot/flow_qa.py --project mira --validate-mock-e2e`."] if sev == "FAIL" else [],
            evidence=[flow_path] if flow_path else [],
        ))
        if flow_path:
            evidence_paths.append(flow_path)
    else:
        gates.append(_gate("flow_qa_gate", "NOT_APPLICABLE", "No product flow change detected."))

    # Definition of Done gate.
    dod_path = project.project_control_path / "AUTOPILOT_DEFINITION_OF_DONE.md"
    dod_ok = dod_path.exists()
    gates.append(_gate(
        "definition_of_done_gate",
        "PASS" if dod_ok else "FAIL",
        "Definition of Done exists." if dod_ok else "Definition of Done missing.",
        fixes=["Restore project_control/AUTOPILOT_DEFINITION_OF_DONE.md."] if not dod_ok else [],
        evidence=[str(dod_path.relative_to(project.repo_path))] if dod_ok else [],
    ))

    return _finalize_policy_report(project, characteristics, gates, changed_files, evidence_paths)


def _finalize_policy_report(
    project: ProjectConfig,
    characteristics: TaskCharacteristics,
    gates: list[PolicyGateResult],
    changed_files: list[str],
    evidence_paths: list[str],
) -> PostBuilderPolicyReport:
    blocked = [gate for gate in gates if gate.severity == "BLOCKED"]
    failed = [gate for gate in gates if gate.severity == "FAIL"]
    warned = [gate for gate in gates if gate.severity == "WARN"]
    fixes = sorted({fix for gate in gates for fix in gate.required_fixes})
    decisions = sorted({decision for gate in gates for decision in gate.human_decisions_needed})
    failed_gates = [gate.gate_type for gate in blocked + failed]
    warnings = [f"{gate.gate_type}: {gate.message}" for gate in warned]

    if blocked:
        verdict = "BLOCKED"
        reason = "One or more hard safety gates are blocked."
        safe = False
        correction = False
        human = True
        next_action = "Resolve blocked gates or get explicit human approval before more builder work."
    elif failed:
        verdict = "NEEDS_FIX"
        reason = "One or more required quality/validation gates failed."
        safe = False
        correction = True
        human = False
        next_action = "Use the correction prompt, fix failed gates, and rerun --post-builder."
    elif decisions or (characteristics.requires_design_review and any(g.gate_type == "design_gate" and "HUMAN" in g.message.upper() for g in gates)):
        verdict = "HUMAN_REVIEW_REQUIRED"
        reason = "No hard failure, but human decision/review is required."
        safe = False
        correction = False
        human = True
        next_action = "Record the human decision or visual/research approval, then rerun policy check."
    elif not changed_files:
        verdict = "SAFE_NO_CHANGES"
        reason = "No working-tree changes detected."
        safe = False
        correction = False
        human = False
        next_action = "No commit needed."
    else:
        verdict = "SAFE_TO_COMMIT"
        reason = "All applicable hard gates passed; warnings, if any, do not block this scope."
        safe = True
        correction = False
        human = False
        next_action = "Commit is allowed if generated logs are not staged and human agrees with scope."

    policy = PolicyVerdict(
        verdict=verdict,
        safe_commit_allowed=safe,
        correction_prompt_recommended=correction,
        human_review_required=human,
        reason=reason,
    )
    all_evidence = sorted({item for item in evidence_paths if item})
    return PostBuilderPolicyReport(
        project_id=project.project_id,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        policy_verdict=policy,
        characteristics=characteristics,
        gate_results=gates,
        failed_gates=failed_gates,
        warnings=warnings,
        required_fixes=fixes,
        human_decisions_needed=decisions,
        evidence_paths=all_evidence,
        changed_files=changed_files,
        next_action=next_action,
    )


def write_policy_report(project: ProjectConfig, report: PostBuilderPolicyReport) -> tuple[Path, Path]:
    logs = project.repo_path / project.logs_dir
    logs.mkdir(parents=True, exist_ok=True)
    md_path = logs / f"{project.project_id}_post_builder_policy_latest.md"
    json_path = logs / f"{project.project_id}_post_builder_policy_latest.json"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Post-Builder Policy Report",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Generated: {report.generated_at_utc}",
        f"Unified verdict: {report.policy_verdict.verdict}",
        f"Safe commit allowed: {'yes' if report.policy_verdict.safe_commit_allowed else 'no'}",
        f"Correction prompt recommended: {'yes' if report.policy_verdict.correction_prompt_recommended else 'no'}",
        f"Human review required: {'yes' if report.policy_verdict.human_review_required else 'no'}",
        f"Reason: {report.policy_verdict.reason}",
        "",
        "## Gate Summary",
    ]
    for gate in report.gate_results:
        lines.append(f"- {gate.severity} `{gate.gate_type}`: {gate.message}")
    lines.extend(["", "## Failed Gates"])
    lines.extend(f"- {item}" for item in report.failed_gates or ["None"])
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in report.warnings or ["None"])
    lines.extend(["", "## Required Fixes"])
    lines.extend(f"- {item}" for item in report.required_fixes or ["None"])
    lines.extend(["", "## Human Decisions Needed"])
    lines.extend(f"- {item}" for item in report.human_decisions_needed or ["None"])
    lines.extend(["", "## Evidence Paths"])
    lines.extend(f"- {item}" for item in report.evidence_paths or ["None"])
    lines.extend(["", "## Next Action", report.next_action])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def build_policy_correction_prompt(project: ProjectConfig, report: PostBuilderPolicyReport, evidence: dict[str, Any]) -> str:
    failed = "\n".join(f"- {gate}" for gate in report.failed_gates) or "- None"
    fixes = "\n".join(f"- {fix}" for fix in report.required_fixes) or "- None"
    decisions = "\n".join(f"- {item}" for item in report.human_decisions_needed) or "- None"
    commands = "\n".join(f"- `{cmd}`" for cmd in [project.lint_command, project.typecheck_command, project.build_command] if cmd) or "- No configured commands"
    evidence_paths = "\n".join(f"- {path}" for path in report.evidence_paths) or "- None"
    changed = "\n".join(f"- {path}" for path in evidence.get("changed_files", [])) or "- None"
    return f"""# v2 Post-Builder Policy Correction Prompt

Project Autopilot produced a unified post-builder policy verdict.

## Unified Verdict

{report.policy_verdict.verdict}

Reason: {report.policy_verdict.reason}

## Failed Gates

{failed}

## Required Fixes

{fixes}

## Human Decisions / Review Needed

{decisions}

## Files Involved

{changed}

## Validation Commands

{commands}

## Forbidden Actions

- Do not modify `.env`, `.env.local`, `.env.*`, secrets, deployment files, or git history.
- Do not execute SQL, enable RLS, create policies, or modify live Supabase.
- Do not call Anthropic, OpenAI, image/video generation, or paid APIs.
- Do not enable scheduler or automatic Claude execution.
- Do not deploy.
- Do not stage generated logs or screenshots.

## Expected Evidence

{evidence_paths}

## Stop Conditions

- Stop if a fix requires secrets, live database changes, paid APIs, deployment, scheduler activation, or automatic builder execution.
- Stop if human approval is needed.
- Stop if the safe alternative is unclear.

## Report Back

1. Files changed.
2. Gates fixed.
3. Commands run and results.
4. Remaining warnings.
5. Current git status.
"""


def check_current(project: ProjectConfig) -> PostBuilderPolicyReport:
    evidence = collect_evidence(project, dry_run=True)
    report_text = "Current working tree review."
    risk = classify_task("Current working tree review", report_text, evidence.get("changed_files", []))
    return evaluate_post_builder_policy(
        project=project,
        builder_report_text=report_text,
        evidence=evidence,
        qa_verdict=None,
        risk=risk,
        run_required_gates=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot v2 post-builder policy")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--check-current", action="store_true")
    parser.add_argument("--report", help="Evaluate a builder report without running full post-builder intake")
    parser.add_argument("--simulate-file", action="append", default=[], help="Add a simulated changed file path for policy testing")
    args = parser.parse_args()

    project = load_project_config(args.project)
    if args.report:
        report_path = Path(args.report)
        report_text = report_path.read_text(encoding="utf-8")
        changed_files = sorted(dict.fromkeys([_norm(path) for path in args.simulate_file] + _extract_report_paths(report_text)))
        evidence = {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "changed_files": changed_files,
            "commands": {},
            "git_status": "Simulated policy report check.",
            "git_diff_stat": "",
        }
        risk = classify_task("Simulated post-builder policy report", report_text, changed_files)
        report = evaluate_post_builder_policy(
            project=project,
            builder_report_text=report_text,
            evidence=evidence,
            qa_verdict=None,
            risk=risk,
            run_required_gates=True,
        )
        md_path, json_path = write_policy_report(project, report)
        print(f"Post-builder policy: {report.policy_verdict.verdict}")
        print(f"  Safe commit allowed: {report.policy_verdict.safe_commit_allowed}")
        print(f"  Failed gates: {', '.join(report.failed_gates) if report.failed_gates else 'none'}")
        print(f"  Warnings: {len(report.warnings)}")
        print(f"  Report: {md_path}")
        print(f"  JSON: {json_path}")
        return 0

    if args.check_current:
        report = check_current(project)
        md_path, json_path = write_policy_report(project, report)
        print(f"Post-builder policy: {report.policy_verdict.verdict}")
        print(f"  Safe commit allowed: {report.policy_verdict.safe_commit_allowed}")
        print(f"  Failed gates: {', '.join(report.failed_gates) if report.failed_gates else 'none'}")
        print(f"  Warnings: {len(report.warnings)}")
        print(f"  Report: {md_path}")
        print(f"  JSON: {json_path}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
