from __future__ import annotations

import argparse
import json
import sys
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parent))

import post_builder_policy as policy
from config import ProjectConfig, load_project_config
from design_director import DesignReview
from qa_reviewer import QAVerdict
from risk_classifier import classify_task


@dataclass(frozen=True)
class FixtureExpectation:
    verdicts: set[str]
    safe_commit_allowed: bool | None = None
    blocked_gates: set[str] = field(default_factory=set)
    required_gates: dict[str, set[str]] = field(default_factory=dict)
    forbidden_verdicts: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class PolicyFixture:
    fixture_id: str
    description: str
    changed_files: list[str]
    builder_report: str
    expectation: FixtureExpectation
    commands: dict[str, dict[str, Any]] = field(default_factory=dict)
    force_design_verdict: str | None = None
    qa_verdict: QAVerdict | None = None


@dataclass
class FixtureResult:
    fixture_id: str
    description: str
    passed: bool
    expected_verdicts: list[str]
    actual_verdict: str
    safe_commit_allowed: bool
    failed_gates: list[str]
    warnings_count: int
    errors: list[str] = field(default_factory=list)
    gate_summary: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _evidence(project: ProjectConfig, fixture: PolicyFixture) -> dict[str, Any]:
    return {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "changed_files": fixture.changed_files,
        "commands": fixture.commands,
        "git_status": "Simulated policy fixture. No working-tree files were changed.",
        "git_diff_stat": "Simulated policy fixture.",
    }


@contextmanager
def _forced_design_review(verdict: str | None) -> Iterator[None]:
    if not verdict:
        yield
        return

    original = policy.run_design_review

    def fake_design_review(project: ProjectConfig) -> DesignReview:
        if verdict == "DESIGN_FAIL":
            return DesignReview(
                verdict="DESIGN_FAIL",
                overall_design_score=48,
                innovation_score=42,
                premium_score=40,
                usability_score=55,
                accessibility_score=60,
                copy_score=58,
                reasons=["Forced fixture result: UI quality gate failed."],
                required_actions=["Resolve forced fixture design failure before commit."],
                rubric_notes={"Fixture": "Forced DESIGN_FAIL for policy regression coverage."},
                inspected_paths=["fixture://design_fail_case"],
            )
        return DesignReview(
            verdict=verdict,
            overall_design_score=76,
            innovation_score=70,
            premium_score=74,
            usability_score=78,
            accessibility_score=72,
            copy_score=76,
            reasons=[f"Forced fixture result: {verdict}."],
            required_actions=[],
            rubric_notes={"Fixture": f"Forced {verdict} for policy regression coverage."},
            inspected_paths=["fixture://forced_design_review"],
        )

    policy.run_design_review = fake_design_review
    try:
        yield
    finally:
        policy.run_design_review = original


def _allowed(*values: str) -> set[str]:
    return set(values)


def fixtures() -> list[PolicyFixture]:
    return [
        PolicyFixture(
            fixture_id="clean_tree_no_changes",
            description="No changed files should produce SAFE_NO_CHANGES.",
            changed_files=[],
            builder_report="No files changed. This is a clean-tree policy fixture.",
            expectation=FixtureExpectation(_allowed("SAFE_NO_CHANGES"), safe_commit_allowed=False),
        ),
        PolicyFixture(
            fixture_id="docs_only_safe",
            description="Project-control docs-only update should be safe.",
            changed_files=["project_control/EXAMPLE.md"],
            builder_report="Documentation-only wording update for project control notes.",
            expectation=FixtureExpectation(
                _allowed("SAFE_TO_COMMIT"),
                safe_commit_allowed=True,
                required_gates={
                    "design_gate": {"NOT_APPLICABLE"},
                    "backend_gate": {"NOT_APPLICABLE"},
                    "research_gate": {"PASS"},
                },
            ),
        ),
        PolicyFixture(
            fixture_id="autopilot_docs_safe",
            description="Autopilot v2 spec docs should not be blocked.",
            changed_files=["project_control/AUTOPILOT_V2_SPEC.md"],
            builder_report="Documentation-only update to the Autopilot v2 specification.",
            expectation=FixtureExpectation(
                _allowed("SAFE_TO_COMMIT", "HUMAN_REVIEW_REQUIRED"),
                forbidden_verdicts={"BLOCKED"},
            ),
        ),
        PolicyFixture(
            fixture_id="ui_change_requires_design",
            description="UI change must run the design gate.",
            changed_files=["app/[locale]/(app)/result/[generationId]/page.tsx"],
            builder_report="UI polish update to the result page interaction and empty state.",
            expectation=FixtureExpectation(
                _allowed("SAFE_TO_COMMIT", "HUMAN_REVIEW_REQUIRED"),
                required_gates={
                    "design_gate": {"PASS", "WARN", "FAIL"},
                    "flow_qa_gate": {"PASS", "WARN", "FAIL"},
                },
                forbidden_verdicts={"BLOCKED"},
            ),
        ),
        PolicyFixture(
            fixture_id="backend_change_requires_backend_audit",
            description="Product API route changes must require backend and Flow QA gates.",
            changed_files=["app/api/tryon/jobs/route.ts"],
            builder_report="Backend route update for try-on job handling. Validation commands passed.",
            expectation=FixtureExpectation(
                _allowed("SAFE_TO_COMMIT", "HUMAN_REVIEW_REQUIRED", "NEEDS_FIX"),
                required_gates={
                    "backend_gate": {"PASS", "WARN", "BLOCKED"},
                    "flow_qa_gate": {"PASS", "WARN", "FAIL"},
                },
            ),
        ),
        PolicyFixture(
            fixture_id="supabase_security_change_requires_human_review",
            description="Supabase/RLS security work must not be approved blindly.",
            changed_files=["lib/supabase/server.ts"],
            builder_report="Supabase RLS security policy review for server helpers. Human approval is required before live changes.",
            expectation=FixtureExpectation(
                _allowed("HUMAN_REVIEW_REQUIRED", "BLOCKED"),
                safe_commit_allowed=False,
                required_gates={
                    "backend_gate": {"PASS", "WARN", "BLOCKED"},
                    "research_gate": {"WARN"},
                    "human_approval_gate": {"WARN", "BLOCKED"},
                },
                forbidden_verdicts={"SAFE_TO_COMMIT"},
            ),
        ),
        PolicyFixture(
            fixture_id="forbidden_env_file_blocked",
            description="A simulated .env.local path must be blocked without creating it.",
            changed_files=[".env.local"],
            builder_report="Changed environment file placeholder for local configuration.",
            expectation=FixtureExpectation(
                _allowed("BLOCKED"),
                safe_commit_allowed=False,
                blocked_gates={"forbidden_files_gate", "secrets_env_gate"},
            ),
        ),
        PolicyFixture(
            fixture_id="secret_leak_text_blocked",
            description="Secret-like text in a report must be blocked.",
            changed_files=["project_autopilot/README.md"],
            builder_report="Builder report accidentally included SUPABASE_SERVICE_ROLE_KEY= and sb_secret_ and access_token placeholders.",
            expectation=FixtureExpectation(
                _allowed("BLOCKED"),
                safe_commit_allowed=False,
                blocked_gates={"secrets_env_gate"},
            ),
        ),
        PolicyFixture(
            fixture_id="paid_api_integration_blocked",
            description="Paid image/video API integration must be blocked or escalated.",
            changed_files=["project_autopilot/providers/new_paid_image_provider.py"],
            builder_report="Integrated Seedance paid API and OpenAI image generation with real generation calls.",
            expectation=FixtureExpectation(
                _allowed("BLOCKED", "HUMAN_REVIEW_REQUIRED"),
                safe_commit_allowed=False,
                forbidden_verdicts={"SAFE_TO_COMMIT"},
            ),
        ),
        PolicyFixture(
            fixture_id="scheduler_enablement_blocked",
            description="Scheduler activation must not pass policy.",
            changed_files=["project_autopilot/config/projects/mira.yaml"],
            builder_report="Enabled scheduler and cron automation for unattended runs.",
            expectation=FixtureExpectation(
                _allowed("BLOCKED", "HUMAN_REVIEW_REQUIRED"),
                safe_commit_allowed=False,
                forbidden_verdicts={"SAFE_TO_COMMIT"},
            ),
        ),
        PolicyFixture(
            fixture_id="auto_claude_execution_blocked",
            description="Automatic Claude execution must stay blocked.",
            changed_files=["project_autopilot/claude_runner.py"],
            builder_report="Enabled automatic Claude execution using --claude-execute for builder runs.",
            expectation=FixtureExpectation(
                _allowed("BLOCKED", "HUMAN_REVIEW_REQUIRED"),
                safe_commit_allowed=False,
                forbidden_verdicts={"SAFE_TO_COMMIT"},
            ),
        ),
        PolicyFixture(
            fixture_id="generated_logs_staged_blocked",
            description="Generated logs must not be staged.",
            changed_files=["logs/flow_qa/mira/latest/flow_results.json"],
            builder_report="Generated Flow QA evidence was staged for commit.",
            expectation=FixtureExpectation(
                _allowed("BLOCKED"),
                safe_commit_allowed=False,
                blocked_gates={"forbidden_files_gate"},
            ),
        ),
        PolicyFixture(
            fixture_id="research_required_case",
            description="Provider/vendor decision should require research or human review.",
            changed_files=["project_control/DECISIONS.md"],
            builder_report=(
                "Choose image-generation provider for production. Compare provider pricing, "
                "compliance, current vendor limits, and architecture strategy before implementation."
            ),
            expectation=FixtureExpectation(
                _allowed("HUMAN_REVIEW_REQUIRED"),
                safe_commit_allowed=False,
                required_gates={"research_gate": {"WARN"}},
                forbidden_verdicts={"SAFE_TO_COMMIT"},
            ),
        ),
        PolicyFixture(
            fixture_id="design_fail_case",
            description="Forced Design Director failure should require fixes.",
            changed_files=["app/[locale]/(app)/result/[generationId]/page.tsx"],
            builder_report="UI redesign changed the result page layout.",
            force_design_verdict="DESIGN_FAIL",
            expectation=FixtureExpectation(
                _allowed("NEEDS_FIX", "HUMAN_REVIEW_REQUIRED"),
                safe_commit_allowed=False,
                required_gates={"design_gate": {"FAIL"}},
                forbidden_verdicts={"SAFE_TO_COMMIT"},
            ),
        ),
        PolicyFixture(
            fixture_id="validation_failure_case",
            description="Failed validation command should produce NEEDS_FIX.",
            changed_files=["project_control/EXAMPLE.md"],
            builder_report="Documentation update where local validation failed.",
            commands={"lint": {"exit_code": 1, "stdout": "", "stderr": "simulated lint failure"}},
            expectation=FixtureExpectation(
                _allowed("NEEDS_FIX"),
                safe_commit_allowed=False,
                required_gates={"validation_gate": {"FAIL"}},
                forbidden_verdicts={"SAFE_TO_COMMIT"},
            ),
        ),
        PolicyFixture(
            fixture_id="claude_sdk_live_call_without_approval_blocked",
            description="Live Claude Agent SDK calls must be blocked without explicit approval.",
            changed_files=["project_autopilot/providers/claude_agent_sdk_provider.py"],
            builder_report="Called Claude Agent SDK live for an architecture review without prior human approval.",
            expectation=FixtureExpectation(
                _allowed("BLOCKED", "HUMAN_REVIEW_REQUIRED"),
                safe_commit_allowed=False,
                required_gates={"human_approval_gate": {"BLOCKED", "WARN"}},
                forbidden_verdicts={"SAFE_TO_COMMIT"},
            ),
        ),
        PolicyFixture(
            fixture_id="claude_sdk_dry_run_safe",
            description="Claude Agent SDK dry-run readiness checks should be safe when no live call occurs.",
            changed_files=["project_autopilot/claude_sdk_dry_run.py"],
            builder_report=(
                "Added Claude Agent SDK dry-run readiness check only. "
                "No external call was made. No live provider request was made. "
                "Builder auto-execution remains disabled."
            ),
            expectation=FixtureExpectation(
                _allowed("SAFE_TO_COMMIT"),
                safe_commit_allowed=True,
                forbidden_verdicts={"BLOCKED"},
            ),
        ),
        PolicyFixture(
            fixture_id="controlled_claude_analysis_approved_safe",
            description="Approved analysis-only Claude SDK calls should not be treated as builder execution.",
            changed_files=["project_autopilot/claude_analysis_call.py"],
            builder_report=(
                "Controlled Claude Agent SDK live analysis with explicit human approval. "
                "Analysis-only; no tools; no commands; no file edits; no secrets sent. "
                "Automatic Claude execution remains disabled."
            ),
            expectation=FixtureExpectation(
                _allowed("SAFE_TO_COMMIT", "HUMAN_REVIEW_REQUIRED"),
                safe_commit_allowed=None,
                forbidden_verdicts={"BLOCKED"},
            ),
        ),
    ]


def _gate_map(report: policy.PostBuilderPolicyReport) -> dict[str, list[str]]:
    gates: dict[str, list[str]] = {}
    for gate in report.gate_results:
        gates.setdefault(gate.gate_type, []).append(gate.severity)
    return gates


def _evaluate_fixture(project: ProjectConfig, fixture: PolicyFixture) -> FixtureResult:
    evidence = _evidence(project, fixture)
    risk = classify_task(
        title=f"Fixture case: {fixture.fixture_id}",
        body=fixture.builder_report,
        changed_files=fixture.changed_files,
    )
    with _forced_design_review(fixture.force_design_verdict):
        report = policy.evaluate_post_builder_policy(
            project=project,
            builder_report_text=fixture.builder_report,
            evidence=evidence,
            qa_verdict=fixture.qa_verdict,
            risk=risk,
            run_required_gates=True,
        )

    actual = report.policy_verdict.verdict
    expected = fixture.expectation
    gates = _gate_map(report)
    errors: list[str] = []
    if actual not in expected.verdicts:
        errors.append(f"Expected verdict in {sorted(expected.verdicts)}, got {actual}.")
    if actual in expected.forbidden_verdicts:
        errors.append(f"Forbidden verdict produced: {actual}.")
    if expected.safe_commit_allowed is not None and report.policy_verdict.safe_commit_allowed != expected.safe_commit_allowed:
        errors.append(
            f"Expected safe_commit_allowed={expected.safe_commit_allowed}, got {report.policy_verdict.safe_commit_allowed}."
        )
    for gate in expected.blocked_gates:
        if gate not in report.failed_gates:
            errors.append(f"Expected failed/blocked gate '{gate}', got failed gates {report.failed_gates}.")
    for gate, severities in expected.required_gates.items():
        actual_severities = gates.get(gate, [])
        if not actual_severities:
            errors.append(f"Expected gate '{gate}' to be present.")
            continue
        if not any(severity in severities for severity in actual_severities):
            errors.append(f"Expected gate '{gate}' severity in {sorted(severities)}, got {actual_severities}.")

    return FixtureResult(
        fixture_id=fixture.fixture_id,
        description=fixture.description,
        passed=not errors,
        expected_verdicts=sorted(expected.verdicts),
        actual_verdict=actual,
        safe_commit_allowed=report.policy_verdict.safe_commit_allowed,
        failed_gates=report.failed_gates,
        warnings_count=len(report.warnings),
        errors=errors,
        gate_summary=[{"gate": gate.gate_type, "severity": gate.severity, "message": gate.message} for gate in report.gate_results],
    )


def _output_paths(project: ProjectConfig) -> tuple[Path, Path]:
    out_dir = project.repo_path / project.logs_dir / "policy_tests" / project.project_id / "latest"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "policy_test_results.json", out_dir / "policy_test_report.md"


def _write_results(project: ProjectConfig, selected: list[str], results: list[FixtureResult]) -> tuple[Path, Path]:
    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    json_path, md_path = _output_paths(project)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        "status": "PASS" if failed == 0 else "FAIL",
        "selected": selected,
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "results": [result.to_dict() for result in results],
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Project Autopilot Policy Fixture Test Report",
        "",
        f"Project: {project.project_name} ({project.project_id})",
        f"Generated: {payload['generated_at_utc']}",
        f"Status: {payload['status']}",
        f"Passed: {passed}/{len(results)}",
        "",
        "## Fixtures",
    ]
    for result in results:
        mark = "PASS" if result.passed else "FAIL"
        lines.append(f"- {mark} `{result.fixture_id}`: expected {', '.join(result.expected_verdicts)}, got {result.actual_verdict}")
        if result.failed_gates:
            lines.append(f"  - Failed gates: {', '.join(result.failed_gates)}")
        if result.errors:
            for error in result.errors:
                lines.append(f"  - Error: {error}")
    lines.extend([
        "",
        "## Safety",
        "- Fixtures use simulated changed files and in-memory builder reports.",
        "- No real `.env` files are created, modified, or printed; secret values remain hidden.",
        "- No SQL, Supabase mutation, external API, paid API, scheduler, or automatic builder execution is performed.",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def run(project: ProjectConfig, selected: list[str]) -> tuple[int, list[FixtureResult], Path, Path]:
    all_fixtures = fixtures()
    if selected == ["all"]:
        chosen = all_fixtures
    else:
        lookup = {fixture.fixture_id: fixture for fixture in all_fixtures}
        unknown = [item for item in selected if item not in lookup]
        if unknown:
            raise ValueError(f"Unknown fixture(s): {', '.join(unknown)}")
        chosen = [lookup[item] for item in selected]

    results = [_evaluate_fixture(project, fixture) for fixture in chosen]
    json_path, md_path = _write_results(project, selected, results)
    failed = [result for result in results if not result.passed]
    return (1 if failed else 0), results, json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot v2 policy fixture tests")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--list", action="store_true", help="List available fixtures.")
    parser.add_argument("--run", default="all", help="Fixture id to run, or 'all'.")
    args = parser.parse_args()

    project = load_project_config(args.project)
    all_fixtures = fixtures()
    if args.list:
        print("Policy fixtures:")
        for fixture in all_fixtures:
            print(f"  - {fixture.fixture_id}: {fixture.description}")
        return 0

    selected = ["all"] if args.run == "all" else [args.run]
    exit_code, results, json_path, md_path = run(project, selected)
    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    print(f"Policy fixtures: {'PASS' if failed == 0 else 'FAIL'} ({passed}/{len(results)})")
    for result in results:
        mark = "PASS" if result.passed else "FAIL"
        print(f"  - {mark} {result.fixture_id}: expected {', '.join(result.expected_verdicts)}, got {result.actual_verdict}")
        for error in result.errors:
            print(f"      {error}")
    print(f"Report: {md_path}")
    print(f"JSON: {json_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
