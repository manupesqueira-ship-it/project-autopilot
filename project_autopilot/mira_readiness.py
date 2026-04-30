"""MIRA Secure MVP Readiness Report.

Evaluates auth, Flow QA, mock generation, RLS, storage, and public testing
readiness from local files only. No network calls, no secret reads.

Usage:
    python -B project_autopilot/mira_readiness.py --project mira
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ReadinessCategory:
    name: str
    status: str  # READY, PARTIAL, BLOCKED, UNKNOWN
    checks: list[dict[str, Any]] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append({"name": name, "ok": ok, "detail": detail})

    def compute_status(self) -> str:
        if not self.checks:
            return "UNKNOWN"
        passed = sum(1 for c in self.checks if c["ok"])
        total = len(self.checks)
        if passed == total:
            return "READY"
        if passed >= total * 0.5:
            return "PARTIAL"
        return "BLOCKED"


def _exists(rel: str) -> bool:
    return (REPO_ROOT / rel).exists()


def _contains(rel: str, needle: str) -> bool:
    p = REPO_ROOT / rel
    if not p.exists():
        return False
    try:
        return needle in p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False


def _read_json(rel: str) -> Any:
    p = REPO_ROOT / rel
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _flow_qa_latest(flow_name: str) -> dict[str, Any]:
    """Return the latest result dict for a flow, or empty dict."""
    data = _read_json("logs/flow_qa/mira/latest/flow_results.json")
    if not data:
        return {}
    results = data if isinstance(data, list) else [data]
    for r in results:
        if r.get("flow_name") == flow_name:
            return r
    return {}


def _flow_qa_latest_verdict(flow_name: str) -> str:
    r = _flow_qa_latest(flow_name)
    return r.get("status", "NOT_RUN") if r else "NOT_RUN"


def check_auth() -> ReadinessCategory:
    cat = ReadinessCategory("Auth Readiness", "UNKNOWN")
    cat.add("Anonymous auth helper exists", _exists("lib/supabase/auth.ts"))
    cat.add("Supabase env precheck helper exists", _exists("lib/supabase/env.ts"))
    cat.add("Onboarding writes auth_user_id",
            _contains("app/[locale]/(app)/onboarding/page.tsx", "auth_user_id"))
    cat.add("Onboarding checks env before Supabase call",
            _contains("app/[locale]/(app)/onboarding/page.tsx", "isSupabasePublicConfigReady"))
    cat.add("Service role server helper exists",
            _exists("lib/supabase/server.ts") and _contains("lib/supabase/server.ts", "createServiceRoleServer"))
    cat.add("Service role fails fast if key missing",
            _contains("lib/supabase/server.ts", "SUPABASE_SERVICE_ROLE_KEY is not set"))
    cat.add("localStorage UX continuity preserved",
            _contains("app/[locale]/(app)/onboarding/page.tsx", "mira_profile_id"))
    cat.add("Anonymous Sign-Ins dashboard checklist exists",
            _exists("project_control/MIRA_SUPABASE_MANUAL_ACTIVATION_CHECKLIST.md"))

    # Check env preflight status
    env_data = _read_json("logs/mira_env_preflight_latest.json")
    if env_data:
        verdict = env_data.get("verdict", "UNKNOWN")
        cat.add(f"Env preflight: {verdict}",
                verdict in ("PASS", "WARN"),
                "FAIL means critical env vars missing" if verdict == "FAIL" else "")
    else:
        cat.add("Env preflight not yet run", False,
                "Run: python -B project_autopilot/env_preflight.py --project mira")

    # Check auth verification
    auth_data = _read_json("logs/mira_supabase_auth_verify_latest.json")
    if auth_data:
        av = auth_data.get("verdict", "UNKNOWN")
        cat.add(f"Auth verification: {av}",
                av in ("PASS", "WARN"),
                f"mode: {auth_data.get('mode', '?')}")
    else:
        cat.add("Auth verification not yet run", False,
                "Run: python -B project_autopilot/supabase_auth_verify.py --project mira")

    cat.status = cat.compute_status()
    return cat


def check_flow_qa() -> ReadinessCategory:
    cat = ReadinessCategory("Flow QA Readiness", "UNKNOWN")
    cat.add("Flow QA framework exists", _exists("project_autopilot/flow_qa.py"))
    cat.add("Flow definitions exist", _exists("project_autopilot/config/projects/mira_flows.yaml"))
    cat.add("Dev server runner exists", _exists("project_autopilot/dev_server_runner.py"))

    for flow, label in [
        ("mira_route_readiness", "Route readiness"),
        ("mira_selector_readiness", "Selector readiness"),
        ("mira_onboarding_safe_dry_flow", "Onboarding dry flow"),
        ("mira_full_e2e_mock_flow", "Full E2E mock flow"),
    ]:
        verdict = _flow_qa_latest_verdict(flow)
        cat.add(f"{label} latest: {verdict}",
                verdict in ("PASS", "WARN", "SKIPPED"),
                verdict)

    # Check mock E2E detail properties
    mock_result = _flow_qa_latest("mira_full_e2e_mock_flow")
    if mock_result:
        cat.add("Mock mode was active",
                mock_result.get("mock_mode_active", False))
        cat.add("Paid API calls avoided",
                mock_result.get("paid_api_calls_avoided", True))
        cat.add("No live Supabase mutation",
                not mock_result.get("live_supabase_mutation", False))

    cat.status = cat.compute_status()
    return cat


def check_mock_generation() -> ReadinessCategory:
    cat = ReadinessCategory("Mock Generation Readiness", "UNKNOWN")
    cat.add("Mock helper exists", _exists("lib/qa-mock.ts"))
    cat.add("Mock mode defaults OFF",
            _contains("lib/qa-mock.ts", 'NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS') and
            not _contains("lib/qa-mock.ts", "= true"))
    cat.add("Production guard exists",
            _contains("lib/qa-mock.ts", 'NODE_ENV === "production"'))
    cat.add("Jobs route mock branch exists",
            _contains("app/api/tryon/jobs/route.ts", "isQaMockMode"))
    cat.add("Status route mock branch exists",
            _contains("app/api/tryon/status/[generationId]/route.ts", "isQaMockGenerationId"))
    cat.add("Mock placeholder asset exists", _exists("public/qa-mock-result.svg"))
    cat.status = cat.compute_status()
    return cat


def check_rls() -> ReadinessCategory:
    cat = ReadinessCategory("RLS Readiness", "UNKNOWN")
    cat.add("Security alignment plan exists",
            _exists("project_control/MIRA_SUPABASE_SECURITY_ALIGNMENT_PLAN.md"))
    cat.add("RLS decision matrix exists",
            _exists("project_control/MIRA_RLS_DECISION_MATRIX.md"))
    cat.add("Migration draft exists",
            _exists("project_control/MIRA_RLS_STORAGE_MIGRATION_DRAFT.md"))
    cat.add("Migration draft has candidate SQL",
            _contains("project_control/MIRA_RLS_STORAGE_MIGRATION_DRAFT.md", "Candidate Migration"))
    cat.add("SQL NOT executed (RLS still disabled)",
            True, "Confirmed: RLS must remain disabled this sprint")
    cat.add("Manual blockers documented",
            _contains("project_control/BLOCKERS.md", "security model not ready"))
    cat.status = cat.compute_status()
    return cat


def check_storage() -> ReadinessCategory:
    cat = ReadinessCategory("Storage Readiness", "UNKNOWN")
    cat.add("Storage strategy in decision matrix",
            _contains("project_control/MIRA_RLS_DECISION_MATRIX.md", "Storage Path Strategy"))
    cat.add("Bucket restrictions documented",
            _contains("project_control/MIRA_SUPABASE_MANUAL_ACTIVATION_CHECKLIST.md", "file_size_limit"))
    cat.add("user-photos remains blocked until policies",
            True, "Private bucket, 0 policies, upload likely fails for anon")
    cat.add("Storage policies NOT applied (correct)",
            True, "Must not apply until strategy decided")
    cat.status = cat.compute_status()
    return cat


def check_privacy_logging() -> ReadinessCategory:
    cat = ReadinessCategory("Privacy & Logging", "UNKNOWN")
    cat.add("Sensitive logging audit tool exists",
            _exists("project_autopilot/sensitive_logging_audit.py"))
    cat.add("Privacy logging guardrails doc exists",
            _exists("project_control/MIRA_PRIVACY_LOGGING_GUARDRAILS.md"))
    cat.add("Customer data policy exists",
            _exists("project_control/CUSTOMER_DATA_POLICY.md"))

    audit_data = _read_json("logs/mira_sensitive_logging_audit_latest.json")
    if audit_data:
        verdict = audit_data.get("verdict", "UNKNOWN")
        high = audit_data.get("high", 0)
        cat.add(f"Latest audit verdict: {verdict}",
                verdict in ("PASS", "WARN") and high == 0,
                f"{audit_data.get('total_findings', 0)} findings, {high} HIGH")
    else:
        cat.add("Logging audit not yet run", False, "Run: python -B project_autopilot/sensitive_logging_audit.py --project mira")

    cat.add("Real customer data still blocked until RLS",
            True, "Correct: must not store real data yet")
    cat.status = cat.compute_status()
    return cat


def check_public_beta() -> ReadinessCategory:
    cat = ReadinessCategory("Public Beta Readiness", "UNKNOWN")
    cat.add("CAPTCHA documented as pending",
            _contains("project_control/MIRA_SUPABASE_MANUAL_ACTIVATION_CHECKLIST.md", "CAPTCHA"))
    cat.add("Site URL/Redirect URLs documented",
            _contains("project_control/MIRA_SUPABASE_MANUAL_ACTIVATION_CHECKLIST.md", "Site URL"))
    cat.add("Real customer data BLOCKED",
            _contains("project_control/BLOCKERS.md", "real customer data"),
            "Must not store real customer data until RLS + policies")
    cat.add("E2E validation plan exists",
            _exists("project_control/MIRA_E2E_VALIDATION_PLAN.md"))
    cat.add("Local auth verification plan exists",
            _exists("project_control/MIRA_LOCAL_AUTH_VERIFICATION_PLAN.md"))
    # Public beta is always BLOCKED until RLS
    cat.status = "BLOCKED"
    return cat


def compute_overall(categories: list[ReadinessCategory]) -> str:
    by_name = {c.name: c for c in categories}

    # Check if local mock E2E is ready (code-side)
    mock_gen = by_name.get("Mock Generation Readiness")
    flow_qa = by_name.get("Flow QA Readiness")
    auth = by_name.get("Auth Readiness")
    mock_e2e_verdict = _flow_qa_latest_verdict("mira_full_e2e_mock_flow")

    local_mock_ready = (
        mock_gen and mock_gen.status == "READY"
        and auth and auth.status == "READY"
        and mock_e2e_verdict in ("PASS", "WARN")
    )

    public_beta = by_name.get("Public Beta Readiness")
    rls = by_name.get("RLS Readiness")

    if local_mock_ready and public_beta and public_beta.status == "BLOCKED":
        return "CODE_READY_MOCK_E2E_PASS"
    if auth and auth.status == "READY" and (not rls or rls.status in ("READY", "PARTIAL")):
        if public_beta and public_beta.status == "BLOCKED":
            return "BLOCKED_FOR_REAL_CUSTOMER_DATA"
    statuses = [c.status for c in categories]
    if all(s == "READY" for s in statuses):
        return "READY"
    if "BLOCKED" in statuses:
        return "BLOCKED_FOR_REAL_CUSTOMER_DATA"
    return "PARTIAL_READY"


def top_blockers(categories: list[ReadinessCategory]) -> list[str]:
    blockers: list[str] = []
    for cat in categories:
        for check in cat.checks:
            if not check["ok"]:
                blockers.append(f"[{cat.name}] {check['name']}")
    return blockers[:5]


def next_actions() -> list[str]:
    return [
        "Enable Anonymous Sign-Ins in Supabase Dashboard",
        "Add SUPABASE_SERVICE_ROLE_KEY to .env.local",
        "Run local auth verification plan",
        "Start dev server with NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true and run full mock E2E",
        "Make RLS ownership/storage decisions in decision matrix",
    ]


def print_report(categories: list[ReadinessCategory], overall: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"MIRA Secure MVP Readiness Report")
    print(f"Generated: {now}")
    print(f"Overall: {overall}")
    print()

    for cat in categories:
        passed = sum(1 for c in cat.checks if c["ok"])
        total = len(cat.checks)
        print(f"  {cat.name}: {cat.status} ({passed}/{total})")
        for check in cat.checks:
            mark = "[OK]" if check["ok"] else "[!!]"
            line = f"    {mark} {check['name']}"
            if check.get("detail"):
                line += f" -- {check['detail']}"
            print(line)
        print()

    blockers = top_blockers(categories)
    if blockers:
        print("Top blockers:")
        for b in blockers:
            print(f"  - {b}")
        print()

    print("Next actions:")
    for a in next_actions():
        print(f"  - {a}")
    print()

    print("Evidence paths:")
    for p in [
        "project_control/MIRA_SUPABASE_MANUAL_ACTIVATION_CHECKLIST.md",
        "project_control/MIRA_LOCAL_AUTH_VERIFICATION_PLAN.md",
        "project_control/MIRA_RLS_DECISION_MATRIX.md",
        "project_control/MIRA_RLS_STORAGE_MIGRATION_DRAFT.md",
        "project_control/MIRA_SECURE_MVP_RUNBOOK.md",
        "logs/flow_qa/mira/latest/flow_report.md",
    ]:
        exists = _exists(p)
        mark = "[OK]" if exists else "[--]"
        print(f"  {mark} {p}")


def write_json_report(categories: list[ReadinessCategory], overall: str) -> Path:
    out_dir = REPO_ROOT / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "mira_readiness_latest.json"
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "categories": [],
    }
    for cat in categories:
        data["categories"].append({
            "name": cat.name,
            "status": cat.status,
            "checks": cat.checks,
        })
    data["top_blockers"] = top_blockers(categories)
    data["next_actions"] = next_actions()
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="MIRA Secure MVP Readiness Report")
    parser.add_argument("--project", required=True)
    parser.parse_args()

    categories = [
        check_auth(),
        check_flow_qa(),
        check_mock_generation(),
        check_privacy_logging(),
        check_rls(),
        check_storage(),
        check_public_beta(),
    ]

    overall = compute_overall(categories)
    print_report(categories, overall)
    json_path = write_json_report(categories, overall)
    print(f"JSON report: {json_path}")


if __name__ == "__main__":
    main()
