"""Sensitive Logging Audit for MIRA.

Static scan of source files for risky logging patterns that could expose
sensitive user data, tokens, sessions, or credentials.

Usage:
    python -B project_autopilot/sensitive_logging_audit.py --project mira

Safety:
- Static scan only. Does not execute app code.
- Does not call Supabase or read .env values.
- Does not modify any files.
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

SCAN_DIRS = ["app/api", "lib", "app/[locale]", "components"]
SCAN_EXTENSIONS = {".ts", ".tsx"}

# Patterns that are risky when they appear in console.log/error/warn or are
# returned in API responses without sanitisation.
RISKY_PATTERNS: list[tuple[str, str, str]] = [
    # (regex, severity, reason)
    (r'console\.(log|error|warn)\s*\([^)]*\berr\b', "WARN",
     "Logging raw error object may expose stack traces or internal details"),
    (r'console\.(log|error)\s*\(.*JSON\.stringify', "WARN",
     "Logging JSON.stringify of object may include sensitive fields"),
    (r'console\.(log|error|warn)\s*\(.*\b(session|access_token|refresh_token|token)\b', "HIGH",
     "Logging auth tokens or sessions"),
    (r'console\.(log|error|warn)\s*\(.*\b(service_role|SERVICE_ROLE|sb_secret)\b', "HIGH",
     "Logging service role key or secret"),
    (r'console\.log\s*\(.*\b(profile|profileRow|form)\b', "WARN",
     "Logging user profile payload may include PII"),
    (r'console\.log\s*\(.*\b(storage_path|storagePath|image_output_path|video_output_path)\b', "WARN",
     "Logging storage paths may expose user file locations"),
    (r'setError\s*\(\s*`[^`]*\$\{[^}]*(Error|error|message)\b', "WARN",
     "Displaying raw Supabase/system error to user may expose internals"),
    (r'setError\s*\([^)]*\?\.\s*message\b', "WARN",
     "Displaying raw error.message to user may expose Supabase internals"),
    (r'NextResponse\.json\s*\(\s*\{\s*error\s*:\s*err', "HIGH",
     "Returning raw error object in API response"),
    (r'NextResponse\.json\s*\(.*stack', "HIGH",
     "Returning stack trace in API response"),
]

# Patterns that are safe and should not be flagged
SAFE_SUPPRESSIONS = [
    r'console\.warn\s*\(\s*"?\[mira/auth\]',  # Auth helper generic warning
    r'console\.error\s*\(\s*"?\[MIRA\]',  # QA mock production guard
    r'//.*console',  # Commented out
]


@dataclass
class Finding:
    file: str
    line: int
    severity: str  # HIGH, WARN, INFO
    pattern: str
    snippet: str
    reason: str
    suggested_fix: str = ""


def scan_file(path: Path, rel: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return findings

    for line_num, line_text in enumerate(lines, 1):
        stripped = line_text.strip()
        # Skip comments
        if stripped.startswith("//") or stripped.startswith("*"):
            continue

        # Check safe suppressions
        suppressed = False
        for safe_re in SAFE_SUPPRESSIONS:
            if re.search(safe_re, line_text):
                suppressed = True
                break
        if suppressed:
            continue

        for pattern_re, severity, reason in RISKY_PATTERNS:
            if re.search(pattern_re, line_text):
                suggested = ""
                if "console.error" in line_text and "err" in line_text:
                    suggested = 'Replace with: console.error("operation failed") without the raw error object'
                elif "setError" in line_text and "message" in line_text:
                    suggested = "Replace with a generic user-facing message instead of raw error.message"
                elif "service_role" in line_text.lower():
                    suggested = "Never log service role key values"

                findings.append(Finding(
                    file=rel,
                    line=line_num,
                    severity=severity,
                    pattern=pattern_re[:60],
                    snippet=stripped[:120],
                    reason=reason,
                    suggested_fix=suggested,
                ))
                break  # One finding per line

    return findings


def run_audit() -> tuple[str, list[Finding]]:
    all_findings: list[Finding] = []

    for scan_dir in SCAN_DIRS:
        base = REPO_ROOT / scan_dir
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.suffix not in SCAN_EXTENSIONS:
                continue
            if "node_modules" in str(path) or ".next" in str(path):
                continue
            try:
                rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            except ValueError:
                continue
            all_findings.extend(scan_file(path, rel))

    high = sum(1 for f in all_findings if f.severity == "HIGH")
    warn = sum(1 for f in all_findings if f.severity == "WARN")

    if high > 0:
        verdict = "FAIL"
    elif warn > 0:
        verdict = "WARN"
    else:
        verdict = "PASS"

    return verdict, all_findings


def write_reports(verdict: str, findings: list[Finding]) -> tuple[Path, Path]:
    logs_dir = REPO_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)

    # Markdown report
    md_path = logs_dir / "mira_sensitive_logging_audit_latest.md"
    lines = [
        "# Sensitive Logging Audit Report",
        "",
        f"**Verdict:** {verdict}",
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Findings:** {len(findings)} ({sum(1 for f in findings if f.severity == 'HIGH')} HIGH, "
        f"{sum(1 for f in findings if f.severity == 'WARN')} WARN)",
        "",
    ]

    if findings:
        lines.append("## Findings")
        lines.append("")
        for f in findings:
            icon = "[!!]" if f.severity == "HIGH" else "[??]"
            lines.append(f"### {icon} {f.severity} — {f.file}:{f.line}")
            lines.append(f"- **Pattern:** `{f.pattern}`")
            lines.append(f"- **Snippet:** `{f.snippet}`")
            lines.append(f"- **Reason:** {f.reason}")
            if f.suggested_fix:
                lines.append(f"- **Suggested fix:** {f.suggested_fix}")
            lines.append("")
    else:
        lines.append("No concerning patterns found.")
        lines.append("")

    lines.append("## Categories Scanned")
    lines.append("- Auth tokens/sessions")
    lines.append("- Service role / secret keys")
    lines.append("- User profile PII (name, email, body measurements)")
    lines.append("- Storage paths (user photos, generated outputs)")
    lines.append("- Raw error objects in console/API responses")
    lines.append("- Supabase error messages exposed to users")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    # JSON report
    json_path = logs_dir / "mira_sensitive_logging_audit_latest.json"
    data = {
        "verdict": verdict,
        "generated_at": now.isoformat(),
        "total_findings": len(findings),
        "high": sum(1 for f in findings if f.severity == "HIGH"),
        "warn": sum(1 for f in findings if f.severity == "WARN"),
        "findings": [
            {
                "file": f.file,
                "line": f.line,
                "severity": f.severity,
                "reason": f.reason,
                "snippet": f.snippet,
                "suggested_fix": f.suggested_fix,
            }
            for f in findings
        ],
    }
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return md_path, json_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Sensitive Logging Audit")
    parser.add_argument("--project", required=True)
    parser.parse_args()

    verdict, findings = run_audit()
    md_path, json_path = write_reports(verdict, findings)

    print(f"Sensitive Logging Audit: {verdict}")
    print(f"  Findings: {len(findings)} ({sum(1 for f in findings if f.severity == 'HIGH')} HIGH, "
          f"{sum(1 for f in findings if f.severity == 'WARN')} WARN)")
    if findings:
        for f in findings:
            icon = "[!!]" if f.severity == "HIGH" else "[??]"
            print(f"  {icon} {f.severity} {f.file}:{f.line} — {f.reason}")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")

    sys.exit(1 if verdict == "FAIL" else 0)


if __name__ == "__main__":
    main()
