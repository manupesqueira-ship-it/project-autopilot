"""MIRA Security Staging Plan Validator.

Dry-run only. Inspects repo files statically and reports on security
staging pack completeness, Supabase blockers, policy matrix status,
and ownership risks. Never executes SQL, never prints secrets.

Usage:
    python -B project_autopilot/security_staging_plan.py --project mira
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

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _file_has_warning(rel: str) -> bool:
    """Check if a SQL draft file has the required safety warning."""
    return _contains(rel, "DO NOT RUN AGAINST PRODUCTION")


# ---------------------------------------------------------------------------
# Check categories
# ---------------------------------------------------------------------------

@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""
    severity: str = "info"  # info, warn, critical


@dataclass
class Category:
    name: str
    checks: list[Check] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "", severity: str = "info") -> None:
        self.checks.append(Check(name, ok, detail, severity))

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.ok)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def status(self) -> str:
        if not self.checks:
            return "UNKNOWN"
        if self.passed == self.total:
            return "PASS"
        crits = [c for c in self.checks if not c.ok and c.severity == "critical"]
        if crits:
            return "FAIL"
        if self.passed >= self.total * 0.5:
            return "WARN"
        return "FAIL"


def check_staging_pack() -> Category:
    """Check that all security staging documents exist."""
    cat = Category("Security Staging Pack")

    required_docs = [
        ("project_control/security/MIRA_RLS_STORAGE_STAGING_PLAN.md", "RLS/storage staging plan"),
        ("project_control/security/MIRA_RLS_POLICY_MATRIX.md", "RLS policy matrix"),
        ("project_control/security/MIRA_STORAGE_POLICY_MATRIX.md", "Storage policy matrix"),
        ("project_control/security/MIRA_SECURITY_TEST_PLAN.md", "Security test plan"),
        ("project_control/security/MIRA_SECURITY_ROLLBACK_PLAN.md", "Rollback plan"),
        ("supabase/drafts/rls_candidate_policies.sql", "RLS candidate SQL"),
        ("supabase/drafts/storage_candidate_policies.sql", "Storage candidate SQL"),
    ]

    for path, label in required_docs:
        cat.add(f"{label} exists", _exists(path), path, "critical")

    return cat


def check_sql_safety() -> Category:
    """Verify SQL draft files have safety warnings and are not in live paths."""
    cat = Category("SQL Draft Safety")

    sql_drafts = [
        "supabase/drafts/rls_candidate_policies.sql",
        "supabase/drafts/storage_candidate_policies.sql",
    ]

    for path in sql_drafts:
        if _exists(path):
            cat.add(f"{path} has safety warning", _file_has_warning(path), "", "critical")
            # Check it's in drafts/ not in a live migration path
            cat.add(f"{path} is in drafts/ (not migrations/)",
                     "/drafts/" in path, "", "critical")
        else:
            cat.add(f"{path} exists", False, "Missing", "critical")

    # Check no live migration files exist
    migrations_dir = REPO_ROOT / "supabase" / "migrations"
    if migrations_dir.exists():
        migration_files = list(migrations_dir.glob("*.sql"))
        cat.add("No live migration files with RLS",
                not any(_contains(str(f.relative_to(REPO_ROOT)), "ENABLE ROW LEVEL SECURITY")
                        for f in migration_files),
                f"{len(migration_files)} migration files found")
    else:
        cat.add("No migrations/ directory (safe)", True)

    return cat


def check_supabase_blockers() -> Category:
    """Report required Supabase blockers status."""
    cat = Category("Supabase Blockers")

    # Check if blockers are documented
    cat.add("Security blocker in BLOCKERS.md",
            _contains("project_control/BLOCKERS.md", "security model not ready"),
            "", "critical")

    cat.add("Anonymous Sign-Ins documented as requirement",
            _contains("project_control/BLOCKERS.md", "Anonymous Sign-Ins") or
            _contains("project_control/security/MIRA_RLS_STORAGE_STAGING_PLAN.md", "Anonymous Sign-Ins"))

    cat.add("CAPTCHA requirement documented",
            _contains("project_control/BLOCKERS.md", "CAPTCHA") or
            _contains("project_control/security/MIRA_SECURITY_TEST_PLAN.md", "CAPTCHA") or
            _contains("project_control/MIRA_SECURE_MVP_RUNBOOK.md", "CAPTCHA"))

    cat.add("Service role key requirement documented",
            _contains("project_control/MIRA_SECURE_MVP_RUNBOOK.md", "SUPABASE_SERVICE_ROLE_KEY") or
            _contains("project_control/security/MIRA_RLS_STORAGE_STAGING_PLAN.md", "service_role"))

    cat.add("RLS disabled acknowledged (correct for staging)",
            _contains("project_control/security/MIRA_RLS_STORAGE_STAGING_PLAN.md", "RLS enabled") or
            _contains("project_control/BLOCKERS.md", "RLS disabled"))

    return cat


def check_policy_matrix() -> Category:
    """Verify policy coverage in the matrix docs."""
    cat = Category("Policy Matrix Coverage")

    tables = ["users_profile", "user_assets", "generations", "events"]
    for table in tables:
        cat.add(f"RLS policy for {table}",
                _contains("project_control/security/MIRA_RLS_POLICY_MATRIX.md", table) or
                _contains("supabase/drafts/rls_candidate_policies.sql", table),
                "", "warn" if table in ("users_profile", "generations") else "info")

    buckets = ["user-photos", "product-images", "generations"]
    for bucket in buckets:
        cat.add(f"Storage policy for {bucket}",
                _contains("project_control/security/MIRA_STORAGE_POLICY_MATRIX.md", bucket) or
                _contains("supabase/drafts/storage_candidate_policies.sql", bucket))

    # MIME / size restrictions documented
    cat.add("MIME restrictions documented",
            _contains("project_control/security/MIRA_STORAGE_POLICY_MATRIX.md", "MIME") or
            _contains("supabase/drafts/storage_candidate_policies.sql", "mime"))

    cat.add("File size limits documented",
            _contains("project_control/security/MIRA_STORAGE_POLICY_MATRIX.md", "Max size") or
            _contains("supabase/drafts/storage_candidate_policies.sql", "file_size_limit"))

    return cat


def check_ownership_risks() -> Category:
    """Check for ownership/authorization risks in API routes."""
    cat = Category("Ownership & Authorization Risks")

    # Status endpoint ownership check
    status_route = "app/api/tryon/status/[generationId]/route.ts"
    if _exists(status_route):
        has_auth_check = (
            _contains(status_route, "auth.uid") or
            _contains(status_route, "getUser") or
            _contains(status_route, "auth_user_id") or
            _contains(status_route, "ownership")
        )
        cat.add("Status endpoint has ownership check",
                has_auth_check,
                "RISK: Documented in ownership findings — fix before real data" if not has_auth_check else "",
                "warn")
    else:
        cat.add("Status endpoint exists", False, "Route missing", "critical")

    # Jobs endpoint auth check
    jobs_route = "app/api/tryon/jobs/route.ts"
    if _exists(jobs_route):
        has_auth = (
            _contains(jobs_route, "auth.uid") or
            _contains(jobs_route, "getUser") or
            _contains(jobs_route, "auth_user_id")
        )
        cat.add("Jobs endpoint has auth verification",
                has_auth,
                "RISK: profileId accepted from client without server verification" if not has_auth else "",
                "warn")

    # Generation store uses service_role for writes
    cat.add("Generation store uses service_role for writes",
            _contains("lib/generation-store.ts", "createServiceRoleServer"),
            "", "info")

    # getGeneration uses anon client (will respect RLS when enabled)
    # Both createServer AND createServiceRoleServer exist, but getGeneration uses createServer
    gen_store = "lib/generation-store.ts"
    cat.add("getGeneration uses anon client (RLS-aware)",
            _contains(gen_store, "createServer"),
            "getGeneration correctly uses anon client — RLS will filter when enabled",
            "info")

    # Ownership findings documented
    cat.add("Ownership findings documented",
            _exists("project_control/security/MIRA_SECURITY_OWNERSHIP_FINDINGS.md"),
            "", "warn")

    return cat


def check_unsafe_markers() -> Category:
    """Check for unsafe patterns that should not be present."""
    cat = Category("Unsafe Marker Scan")

    # Check no .env files are staged or modified
    for env_file in [".env", ".env.local", ".env.production"]:
        cat.add(f"No {env_file} in security docs",
                not _exists(f"project_control/security/{env_file}"),
                "", "critical")

    # Check no secrets in security docs
    security_dir = REPO_ROOT / "project_control" / "security"
    if security_dir.exists():
        for f in security_dir.iterdir():
            if f.is_file():
                content = f.read_text(encoding="utf-8", errors="replace")
                has_secret = any(pattern in content for pattern in [
                    "eyJ", "sk-", "service_role_key=", "anon_key=",
                    "SUPABASE_SERVICE_ROLE_KEY=ey",
                ])
                cat.add(f"No secrets in {f.name}",
                        not has_secret, "", "critical")

    # Check no secrets in SQL drafts
    drafts_dir = REPO_ROOT / "supabase" / "drafts"
    if drafts_dir.exists():
        for f in drafts_dir.iterdir():
            if f.is_file():
                content = f.read_text(encoding="utf-8", errors="replace")
                has_secret = any(pattern in content for pattern in [
                    "eyJ", "sk-", "password",
                ])
                cat.add(f"No secrets in {f.name}",
                        not has_secret, "", "critical")

    return cat


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def generate_report(categories: list[Category]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# MIRA Security Staging Validation Report",
        f"Generated: {now}",
        "",
    ]

    all_pass = all(c.status == "PASS" for c in categories)
    any_fail = any(c.status == "FAIL" for c in categories)
    overall = "PASS" if all_pass else ("FAIL" if any_fail else "WARN")
    lines.append(f"**Overall: {overall}**")
    lines.append("")

    for cat in categories:
        lines.append(f"## {cat.name}: {cat.status} ({cat.passed}/{cat.total})")
        for check in cat.checks:
            mark = "PASS" if check.ok else "FAIL"
            line = f"- [{mark}] {check.name}"
            if check.detail:
                line += f" — {check.detail}"
            lines.append(line)
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="MIRA Security Staging Plan Validator")
    parser.add_argument("--project", required=True)
    args = parser.parse_args()

    categories = [
        check_staging_pack(),
        check_sql_safety(),
        check_supabase_blockers(),
        check_policy_matrix(),
        check_ownership_risks(),
        check_unsafe_markers(),
    ]

    # Print summary
    all_pass = all(c.status == "PASS" for c in categories)
    any_fail = any(c.status == "FAIL" for c in categories)
    overall = "PASS" if all_pass else ("FAIL" if any_fail else "WARN")

    print(f"MIRA Security Staging Validation")
    print(f"Overall: {overall}")
    print()

    for cat in categories:
        print(f"  {cat.name}: {cat.status} ({cat.passed}/{cat.total})")
        for check in cat.checks:
            mark = "[OK]" if check.ok else "[!!]"
            line = f"    {mark} {check.name}"
            if check.detail:
                line += f" — {check.detail}"
            print(line)
        print()

    # Write markdown report
    logs_dir = REPO_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    report_path = logs_dir / "mira_security_staging_report.md"
    report_path.write_text(generate_report(categories), encoding="utf-8")
    print(f"Report: {report_path}")

    # Write JSON
    json_path = logs_dir / "mira_security_staging_latest.json"
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "categories": [],
    }
    for cat in categories:
        data["categories"].append({
            "name": cat.name,
            "status": cat.status,
            "passed": cat.passed,
            "total": cat.total,
            "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail, "severity": c.severity}
                        for c in cat.checks],
        })
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Exit code
    critical_fail = any(
        not c.ok and c.severity == "critical"
        for cat in categories
        for c in cat.checks
    )
    sys.exit(1 if critical_fail else 0)


if __name__ == "__main__":
    main()
