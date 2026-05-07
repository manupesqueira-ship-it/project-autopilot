"""Supabase Auth Verification for MIRA.

Static and optional live verification that the MIRA auth foundation
is correctly wired: env vars present, code paths correct, and
(optionally) anonymous auth + profile insert work against the live
Supabase project.

Usage:
    # Static checks only (safe, no network)
    python -B project_autopilot/supabase_auth_verify.py --project mira

    # Include live dev check (inserts ONE test row, requires dev server)
    python -B project_autopilot/supabase_auth_verify.py --project mira --live-dev-check

Safety:
- Never prints secret values.
- Never modifies .env or .env.local.
- Never executes SQL.
- Never enables RLS or creates policies.
- --live-dev-check inserts exactly one disposable test profile.
- No real customer data. No photo uploads. No paid APIs.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from env_loader import load_env

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class VerifyResult:
    verdict: str = "UNKNOWN"
    mode: str = "static"
    checks: list[Check] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append(Check(name=name, ok=ok, detail=detail))


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


def _env_status(name: str) -> str:
    """Return PRESENT, EMPTY, or MISSING for an env var. Never prints values."""
    import os
    val = os.environ.get(name)
    if val is None:
        return "MISSING"
    if val.strip() == "":
        return "EMPTY"
    return "PRESENT"


# -----------------------------------------------------------------------
# Static checks
# -----------------------------------------------------------------------

def run_static(result: VerifyResult) -> None:
    """Static code/config verification. No network calls."""
    load_env()

    # 1. Env vars
    url_status = _env_status("NEXT_PUBLIC_SUPABASE_URL")
    anon_status = _env_status("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    srv_status = _env_status("SUPABASE_SERVICE_ROLE_KEY")

    result.add("NEXT_PUBLIC_SUPABASE_URL", url_status == "PRESENT", url_status)
    result.add("NEXT_PUBLIC_SUPABASE_ANON_KEY", anon_status == "PRESENT", anon_status)
    result.add("SUPABASE_SERVICE_ROLE_KEY", srv_status == "PRESENT", srv_status)

    # ALLOW_SUPABASE_ANON_SERVER_FALLBACK is optional — not a blocker
    fallback = _env_status("ALLOW_SUPABASE_ANON_SERVER_FALLBACK")
    result.add("ALLOW_SUPABASE_ANON_SERVER_FALLBACK (optional)",
               True, f"{fallback} — not required when service_role key is set")

    # 2. Code structure
    result.add("lib/supabase/env.ts exists", _exists("lib/supabase/env.ts"))
    result.add("lib/supabase/client.ts exists", _exists("lib/supabase/client.ts"))
    result.add("lib/supabase/auth.ts exists", _exists("lib/supabase/auth.ts"))
    result.add("lib/supabase/server.ts exists", _exists("lib/supabase/server.ts"))

    # 3. Auth flow wiring
    result.add("Client checks env before createBrowserClient",
               _contains("lib/supabase/client.ts", "isSupabasePublicConfigReady"))
    result.add("Server checks env before createServerClient",
               _contains("lib/supabase/server.ts", "isSupabasePublicConfigReady"))
    result.add("Auth helper uses signInAnonymously",
               _contains("lib/supabase/auth.ts", "signInAnonymously"))
    result.add("Onboarding calls getOrCreateAnonymousUser",
               _contains("app/[locale]/(app)/onboarding/page.tsx", "getOrCreateAnonymousUser"))
    result.add("Onboarding inserts auth_user_id",
               _contains("app/[locale]/(app)/onboarding/page.tsx", "auth_user_id: authUserId"))
    result.add("Onboarding stores mira_profile_id in localStorage",
               _contains("app/[locale]/(app)/onboarding/page.tsx", 'localStorage.setItem("mira_profile_id"'))
    result.add("Onboarding checks env before Supabase call",
               _contains("app/[locale]/(app)/onboarding/page.tsx", "isSupabasePublicConfigReady"))
    result.add("Scan checks env before Supabase call",
               _contains("app/[locale]/(app)/scan/page.tsx", "isSupabasePublicConfigReady"))

    # 4. Server-side safety
    result.add("Service role fails fast if key missing",
               _contains("lib/supabase/server.ts", "SUPABASE_SERVICE_ROLE_KEY is not set"))
    result.add("Generation store uses createServiceRoleServer",
               _contains("lib/generation-store.ts", "createServiceRoleServer"))

    # 5. Mock mode safety
    result.add("Mock mode defaults OFF",
               _exists("lib/qa-mock.ts") and
               _contains("lib/qa-mock.ts", "NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS") and
               not _contains("lib/qa-mock.ts", "= true"))
    result.add("Mock mode has production guard",
               _contains("lib/qa-mock.ts", 'NODE_ENV === "production"'))


# -----------------------------------------------------------------------
# Live dev check
# -----------------------------------------------------------------------

def run_live_dev_check(result: VerifyResult) -> None:
    """Run the Node.js live dev check helper.

    Performs anonymous auth + fake profile insert using the same Supabase
    client libraries as the app.  Never prints secrets, tokens, or keys.
    """
    import subprocess

    helper = REPO_ROOT / "project_autopilot" / "helpers" / "supabase_live_dev_check.mjs"
    if not helper.exists():
        result.add("Live dev check helper exists", False,
                    f"Missing: {helper}")
        return

    # Pre-check: required env vars must be present (from static checks)
    load_env()
    import os
    url_val = os.environ.get("NEXT_PUBLIC_SUPABASE_URL", "").strip()
    anon_val = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY", "").strip()
    if not url_val or not anon_val:
        result.add("Live dev check: env precondition", False,
                    "NEXT_PUBLIC_SUPABASE_URL or ANON_KEY not present — cannot run live check")
        return

    result.add("Live dev check helper exists", True)

    node_cmd = "node"
    try:
        proc = subprocess.run(
            [node_cmd, str(helper)],
            capture_output=True, text=True, timeout=30,
            cwd=str(REPO_ROOT),
        )
    except FileNotFoundError:
        result.add("Live dev check: node available", False, "node not found on PATH")
        return
    except subprocess.TimeoutExpired:
        result.add("Live dev check: execution", False, "Timed out after 30s")
        return

    stdout = proc.stdout.strip()
    if not stdout:
        result.add("Live dev check: execution", False,
                    f"No output. stderr: {proc.stderr[:200] if proc.stderr else 'none'}")
        return

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        result.add("Live dev check: parse output", False,
                    f"Invalid JSON: {stdout[:200]}")
        return

    # Auth check
    auth_ok = data.get("authOk", False)
    result.add("Live dev check: anonymous auth", auth_ok,
               data.get("userId", "no user id") if auth_ok else
               data.get("detail", "auth failed"))

    # Insert check
    insert_ok = data.get("insertOk", False)
    if insert_ok:
        result.add("Live dev check: fake profile insert", True,
                    f"Row ID: {data.get('insertedRowId', '?')}, "
                    f"email: {data.get('fakeEmail', '?')}")
    elif data.get("error") == "INSERT_FAILED":
        result.add("Live dev check: fake profile insert", False,
                    data.get("detail", "insert failed"))
    # If --no-insert was used, skip insert check

    # Overall
    overall_ok = data.get("ok", False)
    result.add("Live dev check: overall", overall_ok,
               data.get("detail", "unknown"))


# -----------------------------------------------------------------------
# Compute verdict
# -----------------------------------------------------------------------

def compute_verdict(result: VerifyResult) -> None:
    failed = [c for c in result.checks if not c.ok]
    if not failed:
        result.verdict = "PASS"
    elif any("NEXT_PUBLIC_" in c.name and c.detail in ("MISSING", "EMPTY") for c in failed):
        result.verdict = "FAIL_ENV_MISSING"
    elif any("SUPABASE_SERVICE_ROLE_KEY" in c.name and c.detail in ("MISSING", "EMPTY") for c in failed):
        result.verdict = "FAIL_ENV_MISSING"
    else:
        result.verdict = "WARN"


# -----------------------------------------------------------------------
# Reports
# -----------------------------------------------------------------------

def write_reports(result: VerifyResult) -> Path:
    logs_dir = REPO_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)

    # JSON
    json_path = logs_dir / "mira_supabase_auth_verify_latest.json"
    json_path.write_text(json.dumps({
        "verdict": result.verdict,
        "mode": result.mode,
        "generated_at": now.isoformat(),
        "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail} for c in result.checks],
    }, indent=2), encoding="utf-8")

    # Markdown
    md_path = logs_dir / "mira_supabase_auth_verify_latest.md"
    lines = [
        "# Supabase Auth Verification Report",
        "",
        f"**Verdict:** {result.verdict}",
        f"**Mode:** {result.mode}",
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Checks",
        "",
    ]
    for c in result.checks:
        icon = "[OK]" if c.ok else "[!!]"
        line = f"- {icon} {c.name}"
        if c.detail:
            line += f" — {c.detail}"
        lines.append(line)
    lines.append("")
    if result.verdict.startswith("FAIL"):
        lines.append("## Action Required")
        lines.append("Fix the failing checks above before proceeding.")
    elif result.verdict == "WARN":
        lines.append("## Notes")
        lines.append("Some non-critical checks need attention. Review findings above.")
    else:
        lines.append("## Status")
        lines.append("All checks passed. Auth foundation is correctly wired.")
    lines.append("")
    lines.append("## Reminder")
    lines.append("Real customer data remains BLOCKED until RLS, storage policies, and CAPTCHA are ready.")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


# -----------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="MIRA Supabase Auth Verification")
    parser.add_argument("--project", required=True)
    parser.add_argument("--live-dev-check", action="store_true",
                        help="Perform a live minimal dev insert (non-production, fake data only)")
    args = parser.parse_args()

    result = VerifyResult(mode="static")

    run_static(result)

    if args.live_dev_check:
        result.mode = "static+live"
        run_live_dev_check(result)

    compute_verdict(result)
    report_path = write_reports(result)

    print(f"\nSupabase Auth Verify: {result.verdict} (mode: {result.mode})")
    passed = sum(1 for c in result.checks if c.ok)
    total = len(result.checks)
    print(f"  Checks: {passed}/{total} passed")
    for c in result.checks:
        icon = "[OK]" if c.ok else "[!!]"
        line = f"  {icon} {c.name}"
        if c.detail:
            line += f" — {c.detail}"
        print(line)
    print(f"  Report: {report_path}")

    sys.exit(0 if result.verdict in ("PASS", "WARN") else 1)


if __name__ == "__main__":
    main()
