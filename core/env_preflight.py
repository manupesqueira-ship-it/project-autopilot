"""Supabase / MIRA Environment Preflight Check.

Checks that required environment variables are present (not their values).
Never prints secret values. Writes reports to logs/.

Usage:
    python -B project_autopilot/env_preflight.py --project mira
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from env_loader import load_env

REPO_ROOT = Path(__file__).resolve().parent.parent

# (env_var_name, required_for, critical)
ENV_CHECKS = [
    ("NEXT_PUBLIC_SUPABASE_URL", "Supabase browser client, all pages", True),
    ("NEXT_PUBLIC_SUPABASE_ANON_KEY", "Supabase browser client, all pages", True),
    ("SUPABASE_SERVICE_ROLE_KEY", "Server-side generation writes", True),
    ("OPENAI_API_KEY", "Paid image generation (not needed for mock QA)", False),
    ("ALLOW_SUPABASE_ANON_SERVER_FALLBACK", "Dev-only: bypass service_role requirement", False),
]


@dataclass
class EnvCheckResult:
    name: str
    status: str  # PRESENT, EMPTY, MISSING
    required_for: str
    critical: bool
    fix: str = ""


def check_env_var(name: str) -> str:
    val = os.environ.get(name)
    if val is None:
        return "MISSING"
    if val.strip() == "":
        return "EMPTY"
    return "PRESENT"


def run_preflight() -> tuple[str, list[EnvCheckResult]]:
    load_env()
    results: list[EnvCheckResult] = []

    for name, required_for, critical in ENV_CHECKS:
        status = check_env_var(name)
        fix = ""
        if status != "PRESENT":
            if name == "NEXT_PUBLIC_SUPABASE_URL":
                fix = "Add to .env.local: NEXT_PUBLIC_SUPABASE_URL=https://YOUR_REF.supabase.co"
            elif name == "NEXT_PUBLIC_SUPABASE_ANON_KEY":
                fix = "Add to .env.local: NEXT_PUBLIC_SUPABASE_ANON_KEY=your_publishable_key (from Supabase Dashboard > Settings > API)"
            elif name == "SUPABASE_SERVICE_ROLE_KEY":
                fix = "Add to .env.local: SUPABASE_SERVICE_ROLE_KEY=your_secret_key (from Supabase Dashboard > Settings > API)"
            elif name == "OPENAI_API_KEY":
                fix = "Optional. Not needed for mock QA. Add when ready for paid generation."

        results.append(EnvCheckResult(
            name=name, status=status, required_for=required_for,
            critical=critical, fix=fix,
        ))

    critical_missing = [r for r in results if r.critical and r.status != "PRESENT"]
    if critical_missing:
        verdict = "FAIL"
    elif any(r.status != "PRESENT" for r in results):
        verdict = "WARN"
    else:
        verdict = "PASS"

    return verdict, results


def write_reports(verdict: str, results: list[EnvCheckResult]) -> tuple[Path, Path]:
    logs_dir = REPO_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)

    md_path = logs_dir / "mira_env_preflight_latest.md"
    lines = [
        "# MIRA Env Preflight Report",
        "",
        f"**Verdict:** {verdict}",
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Environment Variables",
        "",
        "| Variable | Status | Critical | Required For |",
        "|---|---|---|---|",
    ]
    for r in results:
        lines.append(f"| {r.name} | {r.status} | {'Yes' if r.critical else 'No'} | {r.required_for} |")

    lines.append("")
    missing = [r for r in results if r.status != "PRESENT" and r.fix]
    if missing:
        lines.append("## Fixes Needed")
        lines.append("")
        for r in missing:
            lines.append(f"- **{r.name}** ({r.status}): {r.fix}")
        lines.append("")

    lines.append("## Notes")
    lines.append("- Values are never printed or logged.")
    lines.append("- .env and .env.local are never modified by this tool.")
    lines.append("- Restart dev server after adding env vars.")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    json_path = logs_dir / "mira_env_preflight_latest.json"
    data = {
        "verdict": verdict,
        "generated_at": now.isoformat(),
        "checks": [
            {"name": r.name, "status": r.status, "critical": r.critical,
             "required_for": r.required_for, "fix": r.fix}
            for r in results
        ],
    }
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return md_path, json_path


def main() -> None:
    parser = argparse.ArgumentParser(description="MIRA Env Preflight")
    parser.add_argument("--project", required=True)
    parser.parse_args()

    verdict, results = run_preflight()
    md_path, json_path = write_reports(verdict, results)

    print(f"Env Preflight: {verdict}")
    for r in results:
        icon = "[OK]" if r.status == "PRESENT" else ("[!!]" if r.critical else "[--]")
        crit = " (critical)" if r.critical and r.status != "PRESENT" else ""
        print(f"  {icon} {r.name}: {r.status}{crit}")
        if r.fix:
            print(f"      Fix: {r.fix}")
    print(f"  Report: {md_path}")

    sys.exit(1 if verdict == "FAIL" else 0)


if __name__ == "__main__":
    main()
