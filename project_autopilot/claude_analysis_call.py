from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claude_prompt_safety import sanitize_prompt_text
from config import ProjectConfig, load_project_config
from env_loader import load_env
from post_builder_policy import evaluate_post_builder_policy
from risk_classifier import classify_task
from secret_status import env_var_status

load_env()


DEFAULT_TASK = "Review Project Autopilot v2 architecture and identify top 5 risks."
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
STRONG_ANALYSIS_MODEL = "claude-sonnet-4-6"
MAX_INPUT_CHARS = 12000
MAX_OUTPUT_TOKENS = 700
ESTIMATED_MAX_COST_USD = 0.05


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _latest_dir(project: ProjectConfig) -> Path:
    path = project.repo_path / project.logs_dir / "claude" / project.project_id / "latest"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _model_for_project(project: ProjectConfig) -> str:
    configured = getattr(project, "claude_analysis_model", "")
    return configured or DEFAULT_MODEL


def _is_model_not_found_error(exc: Exception) -> bool:
    text = f"{exc.__class__.__name__}: {exc}".lower()
    return "notfounderror" in text or "not_found_error" in text or ("model:" in text and "not found" in text)


def _safe_error_message(exc: Exception) -> str:
    raw = f"{exc.__class__.__name__}: {exc}"
    return sanitize_prompt_text(raw).sanitized_text


def _build_prompt(project: ProjectConfig, task: str) -> str:
    return f"""You are performing a controlled Project Autopilot analysis-only review.

Project: {project.project_name} ({project.project_id})
Task: {task}

Context:
- Project Autopilot is a control plane for planning, provider routing, QA, evidence, blockers, policy gates, and safe commits.
- Codex is the current primary builder.
- Claude Agent SDK is being tested for a single controlled analysis call.
- This is not builder execution.
- Scheduler remains disabled.
- Automatic Claude execution remains disabled.
- No file edits, tools, command execution, deployment, SQL, or live database changes are allowed.
- Paid image/video APIs remain disabled.

Instructions:
- You are analysis-only.
- Do not request secrets.
- Do not suggest editing files directly.
- Do not generate commands that mutate live systems.
- Do not instruct the caller to enable scheduler, automatic Claude execution, deployment, SQL/RLS, or paid APIs.
- Return concise structured analysis only.

Output format:
1. Top 5 risks before sandboxed Claude builder execution.
2. For each risk: severity, why it matters, mitigation.
3. Minimum safe next step.
4. What must remain disabled.
"""


def _estimate_cost_ok(project: ProjectConfig) -> tuple[bool, str]:
    if project.per_cycle_budget_usd < ESTIMATED_MAX_COST_USD:
        return False, f"Per-cycle budget ${project.per_cycle_budget_usd:.2f} is below estimated max ${ESTIMATED_MAX_COST_USD:.2f}."
    if project.daily_budget_usd < ESTIMATED_MAX_COST_USD:
        return False, f"Daily budget ${project.daily_budget_usd:.2f} is below estimated max ${ESTIMATED_MAX_COST_USD:.2f}."
    return True, f"Estimated max cost ${ESTIMATED_MAX_COST_USD:.2f} is within configured budget."


def _call_anthropic_once(model: str, prompt: str) -> tuple[str, dict[str, Any]]:
    from anthropic import Anthropic

    client = Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=MAX_OUTPUT_TOKENS,
        temperature=0,
        system=(
            "You are an analysis-only reviewer. Do not use tools. Do not edit files. "
            "Do not execute commands. Do not request or expose secrets."
        ),
        messages=[{"role": "user", "content": prompt}],
    )
    parts: list[str] = []
    for block in getattr(response, "content", []) or []:
        text = getattr(block, "text", "")
        if text:
            parts.append(text)
    usage = getattr(response, "usage", None)
    usage_payload = {}
    if usage:
        usage_payload = {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
        }
    return "\n".join(parts).strip(), {"usage": usage_payload}


def _write_policy_review(project: ProjectConfig, report_text: str, evidence_paths: list[str]) -> tuple[str, str]:
    evidence = {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "changed_files": [],
        "commands": {},
        "git_status": "Controlled Claude analysis call created ignored evidence only.",
        "git_diff_stat": "",
        "evidence_paths": evidence_paths,
    }
    risk = classify_task("Controlled Claude analysis call", report_text, [])
    policy_report = evaluate_post_builder_policy(
        project=project,
        builder_report_text=report_text,
        evidence=evidence,
        qa_verdict=None,
        risk=risk,
        run_required_gates=True,
    )
    out = _latest_dir(project)
    md_path = out / "claude_analysis_policy_review.md"
    json_path = out / "claude_analysis_policy_review.json"
    json_path.write_text(json.dumps(policy_report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Controlled Claude Analysis Policy Review",
        "",
        f"Verdict: {policy_report.policy_verdict.verdict}",
        f"Safe commit allowed: {'yes' if policy_report.policy_verdict.safe_commit_allowed else 'no'}",
        f"Human review required: {'yes' if policy_report.policy_verdict.human_review_required else 'no'}",
        "",
        "## Gate Summary",
    ]
    for gate in policy_report.gate_results:
        lines.append(f"- {gate.severity} `{gate.gate_type}`: {gate.message}")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return str(md_path), str(json_path)


def run_analysis(project_id: str, task: str = DEFAULT_TASK, approved_live_call: bool = False) -> tuple[int, dict[str, Any]]:
    project = load_project_config(project_id)
    started = time.perf_counter()
    key = env_var_status("ANTHROPIC_API_KEY", min_length=16)
    model = _model_for_project(project)
    out = _latest_dir(project)
    prompt = _build_prompt(project, task)
    safety = sanitize_prompt_text(prompt)
    budget_ok, budget_message = _estimate_cost_ok(project)
    live_call_made = False
    response_text = ""
    error_message = ""
    call_meta: dict[str, Any] = {}

    verdict = "CLAUDE_ANALYSIS_DRY_RUN_READY"
    if safety.blocked_reason:
        verdict = "CLAUDE_ANALYSIS_CALL_BLOCKED"
        error_message = safety.blocked_reason
    elif len(safety.sanitized_text) > MAX_INPUT_CHARS:
        verdict = "CLAUDE_ANALYSIS_CALL_BLOCKED"
        error_message = f"Sanitized prompt is too large ({len(safety.sanitized_text)} chars)."
    elif not budget_ok:
        verdict = "CLAUDE_ANALYSIS_CALL_BLOCKED"
        error_message = budget_message
    elif not model:
        verdict = "BLOCKED_MODEL_NOT_CONFIGURED"
        error_message = "No Claude analysis model could be determined."
    elif approved_live_call and key["status"] != "PRESENT_VALUE_HIDDEN":
        verdict = "CLAUDE_ANALYSIS_CALL_BLOCKED"
        error_message = f"ANTHROPIC_API_KEY is {key['status']}."
    elif approved_live_call:
        try:
            live_call_made = True
            response_text, call_meta = _call_anthropic_once(model, safety.sanitized_text)
            verdict = "CLAUDE_ANALYSIS_CALL_COMPLETE" if response_text else "CLAUDE_ANALYSIS_CALL_BLOCKED"
            if not response_text:
                error_message = "Anthropic returned an empty response."
        except Exception as exc:
            if _is_model_not_found_error(exc):
                verdict = "CLAUDE_ANALYSIS_MODEL_NOT_FOUND"
                error_message = (
                    f"Model not found or unavailable: {model}. "
                    f"Configure claude_analysis_model to {DEFAULT_MODEL} for low-cost analysis "
                    f"or {STRONG_ANALYSIS_MODEL} for stronger analysis if available."
                )
            else:
                verdict = "CLAUDE_ANALYSIS_CALL_BLOCKED"
                error_message = _safe_error_message(exc)
            call_meta = {}
    else:
        call_meta = {}
        response_text = "Dry-run only. No Anthropic call was made."

    duration = round(time.perf_counter() - started, 3)
    request_path = out / "claude_analysis_request_redacted.md"
    response_path = out / "claude_analysis_response.md"
    metadata_path = out / "claude_analysis_metadata.json"
    request_path.write_text(safety.sanitized_text, encoding="utf-8")
    response_path.write_text(response_text or f"{verdict}: {error_message}", encoding="utf-8")
    metadata = {
        "generated_at_utc": _now(),
        "project_id": project.project_id,
        "project_name": project.project_name,
        "task": task,
        "approved_live_call": approved_live_call,
        "live_call_made": live_call_made,
        "redaction_count": safety.redaction_count,
        "redaction_findings": safety.findings,
        "blocked_reason": safety.blocked_reason or error_message,
        "model_used": model,
        "attempted_model": model,
        "default_model": DEFAULT_MODEL,
        "recommended_models": {
            "low_cost_analysis": DEFAULT_MODEL,
            "stronger_analysis": STRONG_ANALYSIS_MODEL,
        },
        "model_error": error_message if verdict == "CLAUDE_ANALYSIS_MODEL_NOT_FOUND" else "",
        "error_type": verdict if error_message else "",
        "token_usage": call_meta.get("usage", {}),
        "estimated_max_cost_usd": ESTIMATED_MAX_COST_USD,
        "budget_message": budget_message,
        "duration_seconds": duration,
        "verdict": verdict,
        "no_file_edits": True,
        "no_tools": True,
        "no_commands": True,
        "secrets_sent": False,
        "external_api_called": "anthropic_only_if_live" if live_call_made else "none",
        "anthropic_call_count": 1 if live_call_made else 0,
        "automatic_execution_enabled": False,
        "scheduler_enabled": False,
        "request_redacted_path": str(request_path),
        "response_path": str(response_path),
    }
    policy_md, policy_json = _write_policy_review(
        project,
        (
            "Controlled Claude Agent SDK live analysis with explicit human approval. "
            if approved_live_call
            else "Claude Agent SDK analysis dry-run. "
        )
        + "Analysis-only; no tools; no commands; no file edits; no secrets sent.",
        [str(request_path), str(response_path), str(metadata_path)],
    )
    metadata["policy_review_path"] = policy_md
    metadata["policy_review_json_path"] = policy_json
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    return 0, metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Controlled Claude SDK analysis call")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--dry-run", action="store_true", help="Build sanitized prompt without calling Anthropic.")
    parser.add_argument("--approved-live-call", action="store_true", help="Make exactly one explicit analysis-only Anthropic call.")
    parser.add_argument("--task", default=DEFAULT_TASK)
    args = parser.parse_args()

    approved = bool(args.approved_live_call)
    exit_code, metadata = run_analysis(args.project, task=args.task, approved_live_call=approved)
    print(f"Claude Analysis: {metadata['verdict']}")
    print(f"  Live call made: {'yes' if metadata['live_call_made'] else 'no'}")
    print(f"  Secrets sent: {metadata['secrets_sent']}")
    print(f"  Redactions: {metadata['redaction_count']}")
    print(f"  Model: {metadata['model_used']}")
    print(f"  Request: {metadata['request_redacted_path']}")
    print(f"  Response: {metadata['response_path']}")
    print(f"  Metadata: {(_latest_dir(load_project_config(args.project)) / 'claude_analysis_metadata.json')}")
    print(f"  Policy review: {metadata['policy_review_path']}")
    if metadata.get("blocked_reason"):
        print(f"  Note: {metadata['blocked_reason']}")
    print("  Next action: Review saved evidence; keep scheduler and automatic Claude execution disabled.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
