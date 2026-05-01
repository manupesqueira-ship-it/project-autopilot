from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from builder_orchestrator import plan_task
from config import ProjectConfig, load_project_config
from env_loader import load_env
from providers.openai_auditor_provider import detect as detect_openai_auditor
from research_director import classify_research_need
from risk_classifier import classify_task

load_env()


DEFAULT_TASK = "Build a sandboxed Claude builder loop"


@dataclass(frozen=True)
class OpenAIAuditorDryRun:
    project_id: str
    generated_at_utc: str
    mode: str
    verdict: str
    task: str
    provider_status: dict[str, Any]
    task_understanding: str
    recommended_builder: str
    builder_prompt_outline: list[str] = field(default_factory=list)
    required_research: list[str] = field(default_factory=list)
    required_design_review: bool = False
    required_backend_review: bool = False
    required_flow_qa: bool = False
    required_policy_gates: list[str] = field(default_factory=list)
    stop_conditions: list[str] = field(default_factory=list)
    correction_strategy: list[str] = field(default_factory=list)
    final_review_criteria: list[str] = field(default_factory=list)
    source_report_path: str = ""
    live_call_made: bool = False
    openai_call_count: int = 0
    next_action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _latest_dir(project: ProjectConfig) -> Path:
    path = project.repo_path / project.logs_dir / "openai_auditor" / project.project_id / "latest"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _status_payload(project: ProjectConfig) -> dict[str, Any]:
    provider = detect_openai_auditor(project).to_dict()
    latest_json = _latest_dir(project) / "openai_auditor_dry_run.json"
    latest = {}
    try:
        latest = json.loads(latest_json.read_text(encoding="utf-8"))
    except Exception:
        latest = {"verdict": "NOT_RUN", "path": str(latest_json)}
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        "provider": provider,
        "latest_dry_run": latest,
        "live_calls_enabled": False,
        "automatic_execution_enabled": False,
        "openai_api_called": False,
        "next_action": "Use --plan for a dry-run auditor plan; live OpenAI calls remain disabled.",
    }


def _build_prompt_outline(task: str, recommended_builder: str) -> list[str]:
    return [
        f"Objective: {task}",
        "Read project_control before proposing work.",
        f"Builder role: {recommended_builder}; OpenAI Auditor remains planner/reviewer.",
        "Allowed scope and disallowed files must be stated explicitly.",
        "Include validation commands, evidence expectations, and stop conditions.",
        "Do not request secrets, deploy, mutate live databases, enable scheduler, or enable automatic Claude execution.",
    ]


def build_dry_run(project: ProjectConfig, task: str, source_report_path: str = "") -> OpenAIAuditorDryRun:
    source_text = _read_text(Path(source_report_path)) if source_report_path else ""
    review_mode = bool(source_report_path)
    body = f"{task}\n\n{source_text}"
    risk = classify_task(task, body=body, changed_files=[])
    research_status, research_reasons = classify_research_need(body)
    orchestrator_plan = plan_task(project, task)
    provider = detect_openai_auditor(project).to_dict()

    required_policy_gates = [
        "provider_gate",
        "risk_gate",
        "scope_gate",
        "forbidden_files_gate",
        "secrets_env_gate",
        "validation_gate",
        "evidence_gate",
        "human_approval_gate",
        "definition_of_done_gate",
    ]
    if orchestrator_plan.design_review_required:
        required_policy_gates.append("design_gate")
    if orchestrator_plan.backend_security_review_required:
        required_policy_gates.append("backend_gate")
    if orchestrator_plan.flow_qa_required:
        required_policy_gates.append("flow_qa_gate")
    if research_status != "NO_RESEARCH_REQUIRED":
        required_policy_gates.append("research_gate")
    if any(phrase in task.lower() for phrase in ["claude sandbox", "sandboxed claude", "sandboxed builder", "claude builder"]):
        required_policy_gates.extend(["sandbox_preflight_gate", "sandbox_runner_approval_gate", "manual_handoff_gate", "rollback_gate"])

    if review_mode:
        task_understanding = "Dry-run review of a builder report. The auditor should diagnose blockers, extract required fixes, and prepare correction instructions."
        next_action = "Run post-builder policy after saving real builder evidence; do not let the auditor approve its own output."
    else:
        task_understanding = "Dry-run planning for a future multi-step agent loop. The auditor prepares prompts and review criteria while Project Autopilot stays final judge."
        next_action = "Use the generated outline to design the sandboxed loop; keep live OpenAI calls and builder execution disabled."

    required_research = research_reasons if research_status in {"RESEARCH_REQUIRED", "DECISION_BLOCKED_RESEARCH_REQUIRED"} else []
    return OpenAIAuditorDryRun(
        project_id=project.project_id,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        mode="review_builder_report_dry_run" if review_mode else "plan_dry_run",
        verdict="OPENAI_AUDITOR_DRY_RUN_READY",
        task=task,
        provider_status=provider,
        task_understanding=task_understanding,
        recommended_builder=orchestrator_plan.recommended_provider,
        builder_prompt_outline=_build_prompt_outline(task, orchestrator_plan.recommended_provider),
        required_research=required_research,
        required_design_review=orchestrator_plan.design_review_required,
        required_backend_review=orchestrator_plan.backend_security_review_required,
        required_flow_qa=orchestrator_plan.flow_qa_required,
        required_policy_gates=sorted(set(required_policy_gates)),
        stop_conditions=orchestrator_plan.stop_conditions + [
            "Stop if the auditor output conflicts with policy gates.",
            "Stop if a builder report lacks evidence.",
            "Stop if a live OpenAI call would be required without explicit approval.",
            "Stop if Claude sandbox approval, rollback, worktree isolation, or post-builder policy is missing.",
            "Stop if manual Claude handoff would execute Claude from Project Autopilot instead of requiring human paste into Claude Code.",
        ],
        correction_strategy=[
            "Summarize the blocker or failure from evidence only.",
            "Map failure to policy/QA gates.",
            "Generate minimal correction instructions for the builder.",
            "Require the builder to rerun validation and produce a new report.",
            "Return to Project Autopilot policy review; the auditor does not self-approve.",
        ],
        final_review_criteria=[
            "Evidence exists and paths are ignored or intended.",
            "Validation commands passed or failures are explained.",
            "Policy verdict is SAFE_TO_COMMIT before commit.",
            "No env/secrets/deploy/live DB/paid API/scheduler/automatic execution changes occurred.",
            f"Risk remains acceptable: {risk.risk_level}; categories: {', '.join(risk.categories) or 'none'}.",
        ],
        source_report_path=source_report_path,
        next_action=next_action,
    )


def write_dry_run(project: ProjectConfig, payload: OpenAIAuditorDryRun) -> tuple[Path, Path]:
    out = _latest_dir(project)
    md_path = out / "openai_auditor_dry_run.md"
    json_path = out / "openai_auditor_dry_run.json"
    json_path.write_text(json.dumps(payload.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# OpenAI Auditor Dry-Run",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Generated: {payload.generated_at_utc}",
        f"Mode: {payload.mode}",
        f"Verdict: {payload.verdict}",
        f"Task: {payload.task}",
        f"Recommended builder: {payload.recommended_builder}",
        "Live OpenAI call made: no",
        "",
        "## Task Understanding",
        payload.task_understanding,
        "",
        "## Builder Prompt Outline",
        *[f"- {item}" for item in payload.builder_prompt_outline],
        "",
        "## Required Gates",
        *[f"- `{item}`" for item in payload.required_policy_gates],
        "",
        "## Review Requirements",
        f"- Research required: {', '.join(payload.required_research) if payload.required_research else 'none'}",
        f"- Design review: {'yes' if payload.required_design_review else 'no'}",
        f"- Backend review: {'yes' if payload.required_backend_review else 'no'}",
        f"- Flow QA: {'yes' if payload.required_flow_qa else 'no'}",
        "",
        "## Stop Conditions",
        *[f"- {item}" for item in payload.stop_conditions],
        "",
        "## Correction Strategy",
        *[f"- {item}" for item in payload.correction_strategy],
        "",
        "## Final Review Criteria",
        *[f"- {item}" for item in payload.final_review_criteria],
        "",
        "## Next Action",
        payload.next_action,
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def write_status(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    out = _latest_dir(project)
    md_path = out / "openai_auditor_status.md"
    json_path = out / "openai_auditor_status.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    provider = payload["provider"]
    lines = [
        "# OpenAI Auditor Status",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Configured: {'yes' if provider['configured'] else 'no'}",
        f"Status: {provider['current_status']}",
        f"OPENAI_API_KEY: {provider.get('metadata', {}).get('env_status', 'UNKNOWN')}",
        f"Live calls enabled: {payload['live_calls_enabled']}",
        f"Automatic execution enabled: {payload['automatic_execution_enabled']}",
        "OpenAI API called by status: no",
        "",
        "## Latest Dry-Run",
        f"- Verdict: {payload['latest_dry_run'].get('verdict', 'UNKNOWN')}",
        f"- Path: {payload['latest_dry_run'].get('path', '')}",
        "",
        "## Next Action",
        payload["next_action"],
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="OpenAI Auditor dry-run planner/reviewer")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--plan", help="Create a dry-run auditor plan for a task")
    parser.add_argument("--review-builder-report", help="Dry-run review of a builder report path")
    parser.add_argument("--dry-run", action="store_true", help="Compatibility flag; live calls are always disabled in this sprint.")
    args = parser.parse_args()

    project = load_project_config(args.project)
    if args.status:
        payload = _status_payload(project)
        md_path, json_path = write_status(project, payload)
        provider = payload["provider"]
        print(f"OpenAI Auditor: {provider['current_status']}")
        print(f"  Configured: {'yes' if provider['configured'] else 'no'}")
        print(f"  OPENAI_API_KEY: {provider.get('metadata', {}).get('env_status', 'UNKNOWN')}")
        print("  Live calls enabled: no")
        print("  OpenAI API called: NO")
        print(f"  Report: {md_path}")
        print(f"  JSON: {json_path}")
        return 0

    if args.review_builder_report:
        task = f"Review builder report: {args.review_builder_report}"
        payload = build_dry_run(project, task=task, source_report_path=args.review_builder_report)
    else:
        payload = build_dry_run(project, task=args.plan or DEFAULT_TASK)
    md_path, json_path = write_dry_run(project, payload)
    print(f"OpenAI Auditor Dry-Run: {payload.verdict}")
    print(f"  Mode: {payload.mode}")
    print(f"  Recommended builder: {payload.recommended_builder}")
    print(f"  OpenAI API called: NO")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    print(f"  Next action: {payload.next_action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
