from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import ProjectConfig
from evidence_bundle import create_evidence_bundle
from evidence_collector import collect_evidence
from qa_reviewer import QAVerdict, generate_local_correction_prompt, local_structured_review
from risk_classifier import RiskAssessment, classify_task, format_risk_assessment


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def read_builder_report(path: str | Path) -> tuple[Path, str]:
    report_path = Path(path)
    if not report_path.exists():
        raise FileNotFoundError(f"Builder report not found: {report_path}")
    return report_path, report_path.read_text(encoding="utf-8")


def intake_builder_report(
    project: ProjectConfig,
    report_path: str | Path,
    run_validation: bool = True,
) -> dict[str, Any]:
    path, report_text = read_builder_report(report_path)
    evidence = collect_evidence(project, dry_run=not run_validation)
    risk = classify_task(
        title="Builder result intake",
        body=report_text,
        changed_files=evidence.get("changed_files", []),
        project_control_context={},
    )
    verdict = local_structured_review(
        task_plan=report_text,
        evidence=evidence,
        risk_assessment=risk,
        builder_report=report_text,
    )

    bundle_path = create_evidence_bundle(
        project=project,
        evidence=evidence,
        task_plan="Builder result intake",
        builder_prompt=report_text,
        qa_review=verdict.to_markdown(),
    )
    (bundle_path / "builder_report.md").write_text(report_text, encoding="utf-8")
    (bundle_path / "risk_assessment.txt").write_text(format_risk_assessment(risk), encoding="utf-8")

    intake_log_path = write_intake_summary(
        project=project,
        report_path=path,
        evidence=evidence,
        risk=risk,
        verdict=verdict,
        bundle_path=bundle_path,
    )

    correction_prompt_path: Path | None = None
    if verdict.verdict == "FAIL_FIX_REQUIRED":
        correction_prompt = generate_local_correction_prompt(project, verdict, evidence)
        correction_prompt_path = project.repo_path / project.logs_dir / f"{project.project_id}_correction_prompt_latest.md"
        correction_prompt_path.write_text(correction_prompt, encoding="utf-8")

    return {
        "report_path": path,
        "evidence": evidence,
        "risk": risk,
        "verdict": verdict,
        "bundle_path": bundle_path,
        "intake_log_path": intake_log_path,
        "correction_prompt_path": correction_prompt_path,
    }


def write_intake_summary(
    project: ProjectConfig,
    report_path: Path,
    evidence: dict[str, Any],
    risk: RiskAssessment,
    verdict: QAVerdict,
    bundle_path: Path,
) -> Path:
    logs_dir = project.repo_path / project.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    path = logs_dir / f"{project.project_id}_post_builder_{_stamp()}.md"
    changed_files = "\n".join(f"- {item}" for item in evidence.get("changed_files", [])) or "- None"
    command_lines = []
    for name, result in evidence.get("commands", {}).items():
        command_lines.append(f"- {name}: exit {result.get('exit_code')}")
    content = f"""# Post-Builder Intake

Project: {project.project_name} ({project.project_id})
Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
Builder report: {report_path}
Evidence bundle: {bundle_path}

## QA Verdict

{verdict.to_markdown()}

## Risk Assessment

{format_risk_assessment(risk)}

## Changed Files

{changed_files}

## Command Results

{chr(10).join(command_lines) if command_lines else '- None'}
"""
    path.write_text(content, encoding="utf-8")
    return path


def verdict_to_state(verdict: QAVerdict) -> str:
    if verdict.verdict == "PASS":
        return "passed"
    if verdict.verdict == "FAIL_FIX_REQUIRED":
        return "needs_fix"
    if verdict.verdict in {"BLOCKED", "HUMAN_DECISION_REQUIRED"}:
        return "blocked"
    if verdict.verdict == "RESEARCH_REQUIRED":
        return "parked"
    return "blocked"


def verdict_as_dict(verdict: QAVerdict) -> dict[str, Any]:
    return asdict(verdict)
