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
from openai_auditor import build_dry_run as build_openai_auditor_dry_run, write_dry_run as write_openai_auditor_dry_run
from risk_classifier import classify_task


STATES = [
    "OBJECTIVE_RECEIVED",
    "OPENAI_PLANNING",
    "BUILDER_SELECTED",
    "ASSIGNED_TO_CLAUDE",
    "ASSIGNED_TO_CODEX",
    "BUILDER_RUNNING",
    "BUILDER_BLOCKED",
    "OPENAI_REVIEWING_BLOCKER",
    "CORRECTION_PROMPT_READY",
    "BUILDER_RETRY_READY",
    "BUILDER_DONE",
    "OPENAI_REVIEWING_OUTPUT",
    "VALIDATING",
    "POLICY_REVIEW",
    "SAFE_TO_COMMIT",
    "NEEDS_FIX",
    "BLOCKED",
    "HUMAN_REVIEW_REQUIRED",
    "DONE",
]


@dataclass(frozen=True)
class LoopStep:
    state: str
    owner: str
    action: str
    gates: list[str] = field(default_factory=list)
    stop_conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MultiStepLoopDryRun:
    project_id: str
    generated_at_utc: str
    objective: str
    verdict: str
    current_mode: str
    recommended_builder: str
    fallback_builder: str
    execution_enabled: bool
    external_api_called: bool
    scheduler_enabled: bool
    automatic_claude_execution_enabled: bool
    states: list[str]
    proposed_lifecycle: list[LoopStep]
    required_gates: list[str]
    next_action: str
    evidence_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "generated_at_utc": self.generated_at_utc,
            "objective": self.objective,
            "verdict": self.verdict,
            "current_mode": self.current_mode,
            "recommended_builder": self.recommended_builder,
            "fallback_builder": self.fallback_builder,
            "execution_enabled": self.execution_enabled,
            "external_api_called": self.external_api_called,
            "scheduler_enabled": self.scheduler_enabled,
            "automatic_claude_execution_enabled": self.automatic_claude_execution_enabled,
            "states": self.states,
            "proposed_lifecycle": [step.to_dict() for step in self.proposed_lifecycle],
            "required_gates": self.required_gates,
            "next_action": self.next_action,
            "evidence_paths": self.evidence_paths,
        }


def _latest_dir(project: ProjectConfig) -> Path:
    path = project.repo_path / project.logs_dir / "multistep_loop" / project.project_id / "latest"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def build_loop(project: ProjectConfig, objective: str) -> MultiStepLoopDryRun:
    plan = plan_task(project, objective)
    auditor = build_openai_auditor_dry_run(project, objective)
    auditor_md, auditor_json = write_openai_auditor_dry_run(project, auditor)
    risk = classify_task(objective)

    assigned_state = "ASSIGNED_TO_CLAUDE" if plan.recommended_provider in {"claude_code", "claude_agent_sdk"} else "ASSIGNED_TO_CODEX"
    builder_label = "Claude sandbox future" if assigned_state == "ASSIGNED_TO_CLAUDE" else "Codex manual builder"
    gates = sorted(
        {
            "provider_gate",
            "risk_gate",
            "evidence_gate",
            "validation_gate",
            "post_builder_policy",
            "definition_of_done_gate",
            *auditor.required_policy_gates,
        }
    )
    lifecycle = [
        LoopStep("OBJECTIVE_RECEIVED", "human", "State objective and constraints.", ["scope_gate"]),
        LoopStep("OPENAI_PLANNING", "openai_auditor", "Dry-run planner prepares builder prompt outline.", ["provider_gate", "risk_gate"]),
        LoopStep("BUILDER_SELECTED", "builder_orchestrator", f"Select {plan.recommended_provider} with fallback {plan.fallback_provider}.", ["provider_gate"]),
        LoopStep(assigned_state, "project_autopilot", f"Prepare handoff for {builder_label}; execution remains disabled.", ["human_approval_gate"]),
        LoopStep("BUILDER_BLOCKED", "builder", "If blocked, return blocker report to OpenAI Auditor.", ["evidence_gate"]),
        LoopStep("OPENAI_REVIEWING_BLOCKER", "openai_auditor", "Diagnose blocker and draft correction instructions.", ["research_gate"]),
        LoopStep("CORRECTION_PROMPT_READY", "project_autopilot", "Save correction prompt; wait for human/builder action.", ["human_approval_gate"]),
        LoopStep("BUILDER_DONE", "builder", "Builder submits report and evidence.", ["evidence_gate"]),
        LoopStep("OPENAI_REVIEWING_OUTPUT", "openai_auditor", "Review builder output; cannot approve alone.", ["validation_gate"]),
        LoopStep("VALIDATING", "project_autopilot", "Run configured local validation and QA.", gates),
        LoopStep("POLICY_REVIEW", "project_autopilot", "Run post-builder policy; final judge remains Project Autopilot.", gates),
        LoopStep("SAFE_TO_COMMIT", "project_autopilot", "Commit only if policy verdict permits and logs are not staged.", ["definition_of_done_gate"]),
    ]
    if risk.recommended_action in {"block", "require_human_decision"}:
        lifecycle.append(LoopStep("HUMAN_REVIEW_REQUIRED", "human", "Approve, reject, or narrow the objective before execution.", ["human_approval_gate"]))

    return MultiStepLoopDryRun(
        project_id=project.project_id,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        objective=objective,
        verdict="MULTISTEP_LOOP_DRY_RUN_READY",
        current_mode="dry_run_only",
        recommended_builder=plan.recommended_provider,
        fallback_builder=plan.fallback_provider,
        execution_enabled=False,
        external_api_called=False,
        scheduler_enabled=False,
        automatic_claude_execution_enabled=project.allow_automatic_builder_execution,
        states=STATES,
        proposed_lifecycle=lifecycle,
        required_gates=gates,
        next_action="Use this dry-run lifecycle to design sandbox boundaries; do not execute Claude or OpenAI live calls.",
        evidence_paths=[str(auditor_md), str(auditor_json)],
    )


def write_loop(project: ProjectConfig, payload: MultiStepLoopDryRun) -> tuple[Path, Path]:
    out = _latest_dir(project)
    md_path = out / "multistep_loop_dry_run.md"
    json_path = out / "multistep_loop_dry_run.json"
    json_path.write_text(json.dumps(payload.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Multi-Step Agent Loop Dry-Run",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Generated: {payload.generated_at_utc}",
        f"Objective: {payload.objective}",
        f"Verdict: {payload.verdict}",
        f"Mode: {payload.current_mode}",
        f"Recommended builder: {payload.recommended_builder}",
        f"Fallback builder: {payload.fallback_builder}",
        "External API called: no",
        "Builder execution enabled: no",
        "Scheduler enabled: no",
        f"Automatic Claude execution enabled: {'yes' if payload.automatic_claude_execution_enabled else 'no'}",
        "",
        "## States",
        *[f"- `{state}`" for state in payload.states],
        "",
        "## Proposed Lifecycle",
    ]
    for step in payload.proposed_lifecycle:
        lines.append(f"- `{step.state}` ({step.owner}): {step.action}")
        if step.gates:
            lines.append(f"  - Gates: {', '.join(step.gates)}")
    lines.extend([
        "",
        "## Required Gates",
        *[f"- `{gate}`" for gate in payload.required_gates],
        "",
        "## Evidence Paths",
        *[f"- {path}" for path in payload.evidence_paths],
        "",
        "## Next Action",
        payload.next_action,
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def status(project: ProjectConfig) -> dict[str, Any]:
    latest = _read_json(_latest_dir(project) / "multistep_loop_dry_run.json")
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        "states": STATES,
        "scaffold_status": "AVAILABLE",
        "execution_enabled": False,
        "external_api_called": False,
        "latest_dry_run": latest or {"verdict": "NOT_RUN"},
        "next_action": "Run --dry-run-objective to preview a full planner-builder-review-policy lifecycle.",
    }


def write_status(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    out = _latest_dir(project)
    md_path = out / "multistep_loop_status.md"
    json_path = out / "multistep_loop_status.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Multi-Step Agent Loop Status",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Scaffold status: {payload['scaffold_status']}",
        f"States: {len(payload['states'])}",
        f"Execution enabled: {payload['execution_enabled']}",
        "External API called by status: no",
        "",
        "## Latest Dry-Run",
        f"- Verdict: {payload['latest_dry_run'].get('verdict', 'NOT_RUN')}",
        f"- Objective: {payload['latest_dry_run'].get('objective', 'none')}",
        "",
        "## Next Action",
        payload["next_action"],
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot multi-step agent loop scaffold")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--dry-run-objective", help="Preview a full multi-step loop without executing providers")
    args = parser.parse_args()

    project = load_project_config(args.project)
    if args.status:
        payload = status(project)
        md_path, json_path = write_status(project, payload)
        print(f"Multi-Step Loop: {payload['scaffold_status']}")
        print(f"  States: {len(payload['states'])}")
        print("  Execution enabled: no")
        print("  External API called: NO")
        print(f"  Latest: {payload['latest_dry_run'].get('verdict', 'NOT_RUN')}")
        print(f"  Report: {md_path}")
        print(f"  JSON: {json_path}")
        return 0

    payload = build_loop(project, args.dry_run_objective or "Improve MIRA result page design")
    md_path, json_path = write_loop(project, payload)
    print(f"Multi-Step Loop Dry-Run: {payload.verdict}")
    print(f"  Objective: {payload.objective}")
    print(f"  Recommended builder: {payload.recommended_builder}")
    print("  Execution enabled: no")
    print("  External API called: NO")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    print(f"  Next action: {payload.next_action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
