"""Dev Runtime Diagnostics for MIRA.

Detects the class of problem where env_preflight reports env vars as PRESENT
but the running Next.js client bundle does not see them (stale server, wrong
port, stale .next cache, etc.).

Usage:
    # File + process checks only (no running server needed)
    python -B project_autopilot/dev_runtime_diagnose.py --project mira

    # Also probe a running dev server's health endpoint
    python -B project_autopilot/dev_runtime_diagnose.py --project mira --url http://localhost:3000

    # Start a managed dev server, probe it, then stop
    python -B project_autopilot/dev_runtime_diagnose.py --project mira --managed-dev-server

    # Suggest a clean restart procedure
    python -B project_autopilot/dev_runtime_diagnose.py --project mira --suggest-clean-restart

Safety:
- Never prints env var values.
- Never modifies .env or .env.local.
- Never kills user processes unless --kill-node is passed.
- Never calls paid APIs.
- Windows-friendly.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from env_loader import load_env

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class DiagCheck:
    name: str
    status: str  # PASS, WARN, FAIL, INFO, SKIP
    detail: str = ""
    action: str = ""


@dataclass
class DiagResult:
    verdict: str = "UNKNOWN"
    checks: list[DiagCheck] = field(default_factory=list)
    runtime_probe: dict[str, Any] | None = None

    def add(self, name: str, status: str, detail: str = "", action: str = "") -> None:
        self.checks.append(DiagCheck(name=name, status=status, detail=detail, action=action))


# ---------------------------------------------------------------------------
# File / env checks
# ---------------------------------------------------------------------------

def check_env_file_exists(result: DiagResult) -> None:
    """Verify .env.local exists without reading values."""
    env_local = REPO_ROOT / ".env.local"
    if env_local.exists():
        result.add(".env.local exists", "PASS")
    else:
        result.add(".env.local exists", "FAIL",
                    ".env.local not found at repo root",
                    "Create .env.local with required Supabase vars. See .env.example.")


def check_env_vars_in_files(result: DiagResult) -> None:
    """Check that required env var names appear in .env.local (not values)."""
    env_local = REPO_ROOT / ".env.local"
    if not env_local.exists():
        result.add("Required env var names in .env.local", "SKIP",
                    ".env.local not found")
        return

    try:
        content = env_local.read_text(encoding="utf-8", errors="replace")
    except Exception:
        result.add("Required env var names in .env.local", "FAIL",
                    "Could not read .env.local")
        return

    required = ["NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_ANON_KEY"]
    missing_names: list[str] = []
    empty_names: list[str] = []

    for var in required:
        # Find lines like VAR=value (ignoring comments)
        pattern = rf'^{re.escape(var)}\s*='
        matches = [
            line for line in content.splitlines()
            if re.match(pattern, line.strip()) and not line.strip().startswith("#")
        ]
        if not matches:
            missing_names.append(var)
        else:
            # Check if value is empty (VAR= or VAR="")
            for m in matches:
                eq = m.find("=")
                val = m[eq+1:].strip().strip("'\"") if eq >= 0 else ""
                if not val:
                    empty_names.append(var)

    if missing_names:
        result.add("Required env var names in .env.local", "FAIL",
                    f"Missing: {', '.join(missing_names)}",
                    "Add missing variables to .env.local")
    elif empty_names:
        result.add("Required env var names in .env.local", "WARN",
                    f"Empty values: {', '.join(empty_names)}",
                    "Fill in actual values (from Supabase Dashboard > Settings > API)")
    else:
        result.add("Required env var names in .env.local", "PASS",
                    "NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY present with values")


def check_env_preflight_alignment(result: DiagResult) -> None:
    """Run env_preflight logic and record results."""
    load_env()
    required = [
        ("NEXT_PUBLIC_SUPABASE_URL", True),
        ("NEXT_PUBLIC_SUPABASE_ANON_KEY", True),
        ("SUPABASE_SERVICE_ROLE_KEY", True),
    ]
    for var, critical in required:
        val = os.environ.get(var)
        if val is None:
            status = "FAIL" if critical else "WARN"
            result.add(f"env_preflight: {var}", status, "MISSING")
        elif val.strip() == "":
            status = "FAIL" if critical else "WARN"
            result.add(f"env_preflight: {var}", status, "EMPTY")
        else:
            result.add(f"env_preflight: {var}", "PASS", "PRESENT")


# ---------------------------------------------------------------------------
# Process / port checks
# ---------------------------------------------------------------------------

def check_node_processes(result: DiagResult) -> None:
    """Detect running node processes (Windows + Unix)."""
    try:
        if sys.platform == "win32":
            out = subprocess.check_output(
                ["tasklist", "/FI", "IMAGENAME eq node.exe", "/FO", "CSV", "/NH"],
                text=True, timeout=10, stderr=subprocess.DEVNULL
            )
            node_lines = [l for l in out.strip().splitlines() if "node.exe" in l.lower()]
            count = len(node_lines)
        else:
            out = subprocess.check_output(
                ["pgrep", "-c", "node"], text=True, timeout=10, stderr=subprocess.DEVNULL
            ).strip()
            count = int(out) if out.isdigit() else 0
    except (subprocess.SubprocessError, FileNotFoundError, ValueError):
        result.add("Node.js processes", "INFO", "Could not detect running node processes")
        return

    if count > 0:
        result.add("Node.js processes", "INFO",
                    f"{count} node process(es) detected",
                    "If env vars changed, the dev server must be restarted for NEXT_PUBLIC_* to take effect")
    else:
        result.add("Node.js processes", "INFO", "No node processes detected")


def check_port_listening(result: DiagResult, port: int = 3000) -> bool:
    """Check if a port is listening."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        in_use = s.connect_ex(("127.0.0.1", port)) == 0

    if in_use:
        result.add(f"Port {port} listening", "PASS", f"localhost:{port} is responding")
    else:
        result.add(f"Port {port} listening", "INFO",
                    f"localhost:{port} is not responding",
                    "Start the dev server: npm run dev")
    return in_use


# ---------------------------------------------------------------------------
# .next cache check
# ---------------------------------------------------------------------------

def check_next_cache(result: DiagResult) -> None:
    """Check .next/ directory existence and age."""
    next_dir = REPO_ROOT / ".next"
    if not next_dir.exists():
        result.add(".next cache", "INFO", "No .next directory (clean state)")
        return

    try:
        mtime = next_dir.stat().st_mtime
        age_min = (time.time() - mtime) / 60
        if age_min > 60:
            result.add(".next cache", "WARN",
                        f".next last modified {age_min:.0f} min ago — may be stale",
                        "Delete .next/ and restart dev server if env vars were changed")
        else:
            result.add(".next cache", "PASS",
                        f".next last modified {age_min:.0f} min ago")
    except OSError:
        result.add(".next cache", "INFO", "Could not stat .next directory")


# ---------------------------------------------------------------------------
# Runtime probe
# ---------------------------------------------------------------------------

def probe_runtime_env(result: DiagResult, url: str) -> dict[str, Any] | None:
    """Hit the /api/health/env endpoint and compare with file-based checks."""
    import urllib.request
    import urllib.error

    endpoint = url.rstrip("/") + "/api/health/env"
    try:
        req = urllib.request.Request(endpoint, method="GET")
        resp = urllib.request.urlopen(req, timeout=10)
        body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        result.add("Runtime env probe", "FAIL",
                    f"Could not reach {endpoint}: {e.reason}",
                    "Start the dev server and try again")
        return None
    except Exception as e:
        result.add("Runtime env probe", "FAIL",
                    f"Error probing {endpoint}: {e}")
        return None

    result.runtime_probe = body

    # Check public config readiness
    pub_ready = body.get("publicConfigReady", False)
    srv_ready = body.get("serverConfigReady", False)

    if pub_ready:
        result.add("Runtime: public config ready", "PASS")
    else:
        result.add("Runtime: public config ready", "FAIL",
                    "NEXT_PUBLIC_* vars not available in running Next.js process",
                    "Stop dev server, delete .next/, restart with: npm run dev")

    if srv_ready:
        result.add("Runtime: server config ready", "PASS")
    else:
        result.add("Runtime: server config ready", "WARN",
                    "Server config (service_role) not fully ready in runtime")

    mock_enabled = bool(body.get("qaMockModeEnabled", body.get("mockModeEnabled", False)))
    if mock_enabled:
        result.add("Runtime: QA mock mode", "PASS",
                    "NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS is active in this dev server")
    else:
        result.add("Runtime: QA mock mode", "INFO",
                    "QA mock mode is not active in this dev server",
                    "For the internal demo, restart with NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true")

    if body.get("demoRouteCanRunWithoutSupabase"):
        result.add("Runtime: demo can bypass Supabase", "PASS",
                    "/demo can run in mock mode without Supabase public config")
    elif not pub_ready:
        result.add("Runtime: demo can bypass Supabase", "WARN",
                    "Supabase public config is missing and QA mock mode is off",
                    "Start the demo server with NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true")

    # Cross-check: env_preflight says PRESENT but runtime says missing
    load_env()
    file_url_present = bool(os.environ.get("NEXT_PUBLIC_SUPABASE_URL", "").strip())
    file_anon_present = bool(os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY", "").strip())
    runtime_url_present = body.get("supabasePublicUrlPresent", False)
    runtime_anon_present = body.get("supabaseAnonKeyPresent", False)

    if file_url_present and not runtime_url_present:
        result.add("MISMATCH: NEXT_PUBLIC_SUPABASE_URL", "FAIL",
                    "env_preflight sees value but runtime does NOT",
                    "This is the known stale-server bug. Delete .next/ and restart dev server.")

    if file_anon_present and not runtime_anon_present:
        result.add("MISMATCH: NEXT_PUBLIC_SUPABASE_ANON_KEY", "FAIL",
                    "env_preflight sees value but runtime does NOT",
                    "This is the known stale-server bug. Delete .next/ and restart dev server.")

    if file_url_present and runtime_url_present:
        result.add("Alignment: NEXT_PUBLIC_SUPABASE_URL", "PASS",
                    "File and runtime agree: PRESENT")
    if file_anon_present and runtime_anon_present:
        result.add("Alignment: NEXT_PUBLIC_SUPABASE_ANON_KEY", "PASS",
                    "File and runtime agree: PRESENT")

    return body


# ---------------------------------------------------------------------------
# Managed dev server probe
# ---------------------------------------------------------------------------

def run_managed_server_check(result: DiagResult) -> dict[str, Any] | None:
    """Start a managed dev server, probe it, then stop."""
    from dev_server_runner import DevServer

    port = 3099
    server = DevServer(port=port)
    started, msg = server.start()
    if not started:
        result.add("Managed dev server start", "FAIL", msg)
        return None

    result.add("Managed dev server start", "PASS", msg)

    try:
        probe_data = probe_runtime_env(result, f"http://localhost:{port}")
        return probe_data
    finally:
        server.stop()
        result.add("Managed dev server stop", "PASS", "Clean shutdown")


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(result: DiagResult) -> str:
    has_fail = any(c.status == "FAIL" for c in result.checks)
    has_warn = any(c.status == "WARN" for c in result.checks)
    has_mismatch = any("MISMATCH" in c.name for c in result.checks)

    if has_mismatch:
        return "FAIL_ENV_MISMATCH"
    if has_fail:
        return "FAIL"
    if has_warn:
        return "WARN"
    return "PASS"


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def write_report(result: DiagResult) -> Path:
    logs_dir = REPO_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)

    md_path = logs_dir / "mira_dev_runtime_diagnose_latest.md"
    lines = [
        "# Dev Runtime Diagnostics Report",
        "",
        f"**Verdict:** {result.verdict}",
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Platform:** {platform.system()} {platform.release()}",
        "",
        "## Checks",
        "",
    ]
    for c in result.checks:
        icon = {"PASS": "[OK]", "WARN": "[??]", "FAIL": "[!!]",
                "INFO": "[--]", "SKIP": "[--]"}.get(c.status, "[??]")
        line = f"- {icon} **{c.status}** {c.name}"
        if c.detail:
            line += f" — {c.detail}"
        lines.append(line)
        if c.action:
            lines.append(f"  - Action: {c.action}")

    if result.runtime_probe:
        lines.append("")
        lines.append("## Runtime Probe Response")
        lines.append("```json")
        lines.append(json.dumps(result.runtime_probe, indent=2))
        lines.append("```")

    lines.append("")
    lines.append("## Root Cause Guidance")
    lines.append("")
    lines.append("If env_preflight says PRESENT but browser shows missing:")
    lines.append("1. NEXT_PUBLIC_* vars are compiled into the client JS bundle at server start")
    lines.append("2. Editing .env.local does NOT take effect until the dev server restarts")
    lines.append("3. A stale .next/ cache can also cause the old (missing) values to persist")
    lines.append("4. Fix: stop dev server → delete .next/ → run `npm run dev`")
    lines.append("5. Verify: visit /api/health/env in the browser")
    lines.append("")
    lines.append("For the internal demo, QA mock mode is a separate safe path:")
    lines.append("- Start with `NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true`")
    lines.append("- `/es/demo` should render without Supabase public config in mock mode")
    lines.append("- Real onboarding and scan still require Supabase public config")
    lines.append("")
    lines.append("## Safety")
    lines.append("- No secret values printed or logged")
    lines.append("- No .env files modified")
    lines.append("- No user processes killed")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    json_path = logs_dir / "mira_dev_runtime_diagnose_latest.json"
    json_data = {
        "verdict": result.verdict,
        "generated_at": now.isoformat(),
        "platform": f"{platform.system()} {platform.release()}",
        "checks": [
            {"name": c.name, "status": c.status, "detail": c.detail, "action": c.action}
            for c in result.checks
        ],
        "runtime_probe": result.runtime_probe,
    }
    json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

    return md_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="MIRA Dev Runtime Diagnostics")
    parser.add_argument("--project", required=True)
    parser.add_argument("--url", help="URL of running dev server to probe")
    parser.add_argument("--managed-dev-server", action="store_true",
                        help="Start a managed dev server, probe it, then stop")
    parser.add_argument("--suggest-clean-restart", action="store_true",
                        help="Print clean restart instructions")
    parser.add_argument("--port", type=int, default=3000,
                        help="Port to check for running dev server")
    args = parser.parse_args()

    result = DiagResult()

    # File / env checks
    check_env_file_exists(result)
    check_env_vars_in_files(result)
    check_env_preflight_alignment(result)
    check_node_processes(result)
    check_port_listening(result, args.port)
    check_next_cache(result)

    # Runtime probe
    if args.managed_dev_server:
        run_managed_server_check(result)
    elif args.url:
        probe_runtime_env(result, args.url)

    # Compute verdict
    result.verdict = compute_verdict(result)

    # Write report
    report_path = write_report(result)

    # Print summary
    print(f"Dev Runtime Diagnostics: {result.verdict}")
    for c in result.checks:
        icon = {"PASS": "[OK]", "WARN": "[??]", "FAIL": "[!!]",
                "INFO": "[--]", "SKIP": "[--]"}.get(c.status, "[??]")
        line = f"  {icon} {c.status} {c.name}"
        if c.detail:
            line += f" — {c.detail}"
        print(line)
        if c.action:
            print(f"       Action: {c.action}")

    print(f"  Report: {report_path}")

    if args.suggest_clean_restart:
        print()
        print("=== Clean Restart Procedure ===")
        print("1. Stop the running Next.js dev server (Ctrl+C)")
        print("2. Delete the .next cache:  rm -rf .next")
        if sys.platform == "win32":
            print("   (Windows: rd /s /q .next)")
        print("3. Start fresh:  npm run dev")
        print("4. Verify:  open http://localhost:3000/api/health/env in browser")
        print("5. Run:  python -B project_autopilot/dev_runtime_diagnose.py --project mira --url http://localhost:3000")

    sys.exit(1 if result.verdict.startswith("FAIL") else 0)


if __name__ == "__main__":
    main()
