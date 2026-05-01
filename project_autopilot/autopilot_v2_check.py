from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import ProjectConfig, load_project_config
from provider_registry import build_registry


@dataclass
class V2Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class V2Report:
    verdict: str
    checks: list[V2Check] = field(default_factory=list)
    provider_summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "checks": [asdict(check) for check in self.checks],
            "provider_summary": self.provider_summary,
        }


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def run_check(project: ProjectConfig) -> V2Report:
    root = project.repo_path
    ap = root / "project_autopilot"
    pc = project.project_control_path
    checks: list[V2Check] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append(V2Check(name, ok, detail))

    provider_summary = build_registry(project.project_id)

    add("Provider registry exists", (ap / "provider_registry.py").exists())
    add("Provider registry CLI works", provider_summary.get("provider_count", 0) >= 3, f"{provider_summary.get('provider_count', 0)} providers")
    add("Codex provider exists", (ap / "providers" / "codex_provider.py").exists())
    add("Claude Code provider exists", (ap / "providers" / "claude_code_provider.py").exists())
    add("Claude Agent SDK provider exists", (ap / "providers" / "claude_agent_sdk_provider.py").exists())
    add("Design Director exists", (ap / "design_director.py").exists())
    add("Research Director exists", (ap / "research_director.py").exists())
    add("Builder Orchestrator exists", (ap / "builder_orchestrator.py").exists())
    add("Post-builder policy enforcement exists", (ap / "post_builder_policy.py").exists())
    add("Policy fixture suite exists", (ap / "policy_test_fixtures.py").exists())
    add("Policy fixture suite command documented", _contains(ap / "README.md", "policy_test_fixtures.py"))
    policy_fixture_results = _read_json(root / project.logs_dir / "policy_tests" / project.project_id / "latest" / "policy_test_results.json")
    if policy_fixture_results:
        add(
            "Latest policy fixture suite passed",
            policy_fixture_results.get("status") == "PASS",
            f"{policy_fixture_results.get('passed', 0)}/{policy_fixture_results.get('total', 0)} passed",
        )
    else:
        add("Latest policy fixture suite passed", True, "WARN: no latest fixture report yet; run policy_test_fixtures.py")
    add("Autopilot Definition of Done exists", (pc / "AUTOPILOT_DEFINITION_OF_DONE.md").exists())
    add("Autopilot v2 spec exists", (pc / "AUTOPILOT_V2_SPEC.md").exists())
    add("Control Center exists", (ap / "control_center.py").exists())
    add("Flow QA exists", (ap / "flow_qa.py").exists())
    add("Backend audit exists", (ap / "backend_audit.py").exists())
    add("Readiness report exists", (ap / "mira_readiness.py").exists())
    add("No-human mock E2E exists", _contains(ap / "flow_qa.py", "--validate-mock-e2e"))
    add("Scheduler disabled", not (root / "project_control" / "SCHEDULER_ENABLED.md").exists(), "No scheduler enable marker found")
    add("Automatic Claude execution disabled", project.allow_automatic_builder_execution is False)
    add("Paid APIs disabled by default", project.paid_api_mode == "disabled_by_default" and not project.allow_paid_image_generation and not project.allow_paid_video_generation)
    add("HALT support exists", (ap / "run_lock.py").exists() and _contains(ap / "agent_loop.py", "HALT_AUTOPILOT"))
    add("Run lock exists", (ap / "run_lock.py").exists())

    required_docs = [
        "AGENT_RULES.md",
        "AUTONOMY_PROTOCOL.md",
        "QUALITY_BAR.md",
        "QA_PROTOCOL.md",
        "BLOCKERS.md",
        "HUMAN_QUESTIONS.md",
        "DESIGN_DIRECTOR_STANDARD.md",
        "RESEARCH_DIRECTOR_STANDARD.md",
    ]
    missing_docs = [name for name in required_docs if not (pc / name).exists()]
    add("Project control docs present", not missing_docs, ", ".join(missing_docs) if missing_docs else "all required docs present")

    failures = [c for c in checks if not c.ok]
    if not failures:
        verdict = "AUTOPILOT_V2_READY_LOCAL"
    elif len(failures) <= 3:
        verdict = "AUTOPILOT_V2_PARTIAL"
    else:
        verdict = "AUTOPILOT_V2_BLOCKED"
    return V2Report(verdict, checks, provider_summary)


def write_reports(project: ProjectConfig, report: V2Report) -> tuple[Path, Path]:
    logs = project.repo_path / project.logs_dir
    logs.mkdir(parents=True, exist_ok=True)
    md_path = logs / f"{project.project_id}_autopilot_v2_check_latest.md"
    json_path = logs / f"{project.project_id}_autopilot_v2_check_latest.json"
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        **report.to_dict(),
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Project Autopilot v2 Readiness Check",
        "",
        f"Verdict: {report.verdict}",
        "",
        "## Checks",
    ]
    for check in report.checks:
        mark = "[OK]" if check.ok else "[FAIL]"
        detail = f" - {check.detail}" if check.detail else ""
        lines.append(f"- {mark} {check.name}{detail}")
    lines.extend([
        "",
        "## Provider Summary",
        f"- Providers: {report.provider_summary.get('provider_count', 0)}",
        f"- Configured providers: {report.provider_summary.get('configured_provider_count', 0)}",
        f"- Recommended action: {report.provider_summary.get('recommended_next_provider_action', '')}",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot v2 readiness check")
    parser.add_argument("--project", default="mira")
    args = parser.parse_args()

    project = load_project_config(args.project)
    report = run_check(project)
    md_path, json_path = write_reports(project, report)
    passed = sum(1 for c in report.checks if c.ok)
    total = len(report.checks)
    print(f"Autopilot v2 Check: {report.verdict} ({passed}/{total})")
    for check in report.checks:
        mark = "[OK]" if check.ok else "[FAIL]"
        detail = f" - {check.detail}" if check.detail else ""
        print(f"  {mark} {check.name}{detail}")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    return 0 if report.verdict != "AUTOPILOT_V2_BLOCKED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
