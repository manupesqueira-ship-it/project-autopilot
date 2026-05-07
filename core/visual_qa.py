"""MIRA Visual QA Tool — Static/dry-run visual quality checker.

Checks pages, selectors, accessibility markers, loading/error states,
and visual standard compliance from local files only. No network calls,
no browser automation required.

Usage:
    python -B project_autopilot/visual_qa.py --project mira
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
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""
    severity: str = "P2"  # P0 / P1 / P2


@dataclass
class PageReport:
    page: str
    path: str
    checks: list[CheckResult] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "", severity: str = "P2") -> None:
        self.checks.append(CheckResult(name, ok, detail, severity))

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.ok)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def verdict(self) -> str:
        if not self.checks:
            return "UNKNOWN"
        fails = [c for c in self.checks if not c.ok]
        if not fails:
            return "PASS"
        if any(c.severity == "P0" for c in fails):
            return "FAIL"
        if any(c.severity == "P1" for c in fails):
            return "WARN"
        return "PASS_WITH_ISSUES"


@dataclass
class VisualQAReport:
    project: str
    generated_at: str = ""
    pages: list[PageReport] = field(default_factory=list)
    meta_checks: list[CheckResult] = field(default_factory=list)

    @property
    def overall(self) -> str:
        verdicts = [p.verdict for p in self.pages]
        if "FAIL" in verdicts:
            return "FAIL"
        if "WARN" in verdicts:
            return "WARN"
        meta_fails = [c for c in self.meta_checks if not c.ok]
        if any(c.severity == "P0" for c in meta_fails):
            return "FAIL"
        if any(c.severity == "P1" for c in meta_fails):
            return "WARN"
        return "PASS"


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def _read(rel: str) -> str:
    p = REPO_ROOT / rel
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _exists(rel: str) -> bool:
    return (REPO_ROOT / rel).exists()


def _contains(content: str, needle: str) -> bool:
    return needle in content


def _count(content: str, needle: str) -> int:
    return content.count(needle)


# ---------------------------------------------------------------------------
# Page definitions — what to check per page
# ---------------------------------------------------------------------------

MIRA_PAGES = [
    {
        "name": "Landing",
        "path": "app/[locale]/(landing)/page.tsx",
        "required_testids": [],
        "required_aria": ["aria-label"],
        "needs_loading": False,
        "needs_error": False,
        "needs_empty": False,
    },
    {
        "name": "Onboarding",
        "path": "app/[locale]/(app)/onboarding/page.tsx",
        "required_testids": [
            "input-name", "input-email", "input-height-cm", "input-weight-kg",
            "btn-onboarding-next",
        ],
        "required_aria": ["aria-required", "aria-pressed", "role=\"alert\""],
        "needs_loading": True,
        "needs_error": True,
        "needs_empty": False,
    },
    {
        "name": "Scan",
        "path": "app/[locale]/(app)/scan/page.tsx",
        "required_testids": ["btn-scan-next", "btn-skip-photos"],
        "required_aria": ["aria-label", "role=\"alert\""],
        "needs_loading": True,
        "needs_error": True,
        "needs_empty": False,
    },
    {
        "name": "Catalog",
        "path": "app/[locale]/(app)/catalog/page.tsx",
        "required_testids": ["catalog-grid"],
        "required_aria": ["aria-pressed", "role=\"status\""],
        "needs_loading": False,
        "needs_error": False,
        "needs_empty": True,
    },
    {
        "name": "TryOn",
        "path": "app/[locale]/(app)/tryon/[productId]/page.tsx",
        "required_testids": ["tryon-page", "btn-tryon-start", "tryon-status"],
        "required_aria": ["aria-pressed"],
        "needs_loading": True,
        "needs_error": True,
        "needs_empty": False,
    },
    {
        "name": "Result",
        "path": "app/[locale]/(app)/result/[generationId]/page.tsx",
        "required_testids": ["result-page", "result-status", "btn-buy", "btn-try-another"],
        "required_aria": ["aria-live", "aria-label"],
        "needs_loading": True,
        "needs_error": True,
        "needs_empty": False,
    },
]


# ---------------------------------------------------------------------------
# Page-level checks
# ---------------------------------------------------------------------------

def check_page(page_def: dict[str, Any]) -> PageReport:
    report = PageReport(page=page_def["name"], path=page_def["path"])
    content = _read(page_def["path"])

    # Page exists
    exists = bool(content)
    report.add("Page file exists", exists, page_def["path"], "P0")
    if not exists:
        return report

    # data-testid selectors
    for tid in page_def["required_testids"]:
        found = _contains(content, tid)
        report.add(f"data-testid: {tid}", found,
                   "present" if found else "MISSING", "P1")

    # Aria markers
    for aria in page_def["required_aria"]:
        found = _contains(content, aria)
        report.add(f"Accessibility: {aria}", found,
                   "present" if found else "MISSING", "P1")

    # Focus indicators
    has_focus = _contains(content, "focus-visible") or _contains(content, "focus:")
    report.add("Focus indicators", has_focus,
               "focus-visible found" if has_focus else "No focus styling detected", "P1")

    # Loading state
    if page_def["needs_loading"]:
        has_loading = (
            _contains(content, "loading") or _contains(content, "submitting")
            or _contains(content, "…") or _contains(content, "spinner")
            or _contains(content, "Generating") or _contains(content, "uploading")
        )
        report.add("Loading state", has_loading,
                   "loading indicator found" if has_loading else "No loading state detected", "P1")

    # Error state
    if page_def["needs_error"]:
        has_error = _contains(content, 'role="alert"') or _contains(content, "role='alert'")
        report.add("Error state (role=alert)", has_error,
                   "alert role found" if has_error else "No error alert detected", "P1")

    # Empty state
    if page_def["needs_empty"]:
        has_empty = (
            _contains(content, 'role="status"') or _contains(content, "No products")
            or _contains(content, "empty") or _contains(content, "no results")
        )
        report.add("Empty state", has_empty,
                   "empty state found" if has_empty else "No empty state detected", "P1")

    # Button disabled state
    has_disabled = _contains(content, "disabled") or _contains(content, "cursor-not-allowed")
    report.add("Disabled state handling", has_disabled,
               "disabled styling found" if has_disabled else "No disabled state detected", "P2")

    return report


# ---------------------------------------------------------------------------
# Meta checks — project-level standards
# ---------------------------------------------------------------------------

def check_meta() -> list[CheckResult]:
    checks: list[CheckResult] = []

    # Visual standard doc
    checks.append(CheckResult(
        "Visual Quality Standard exists",
        _exists("project_control/visual/MIRA_VISUAL_QUALITY_STANDARD.md"),
        "project_control/visual/MIRA_VISUAL_QUALITY_STANDARD.md",
        "P1"
    ))

    # External builder policy
    checks.append(CheckResult(
        "External Builder Policy exists",
        _exists("project_control/EXTERNAL_BUILDER_POLICY.md"),
        "project_control/EXTERNAL_BUILDER_POLICY.md",
        "P1"
    ))

    # Shared button component has focus ring
    btn = _read("components/ui/button.tsx")
    checks.append(CheckResult(
        "Button component: focus-visible ring",
        _contains(btn, "focus-visible"),
        "focus-visible in button.tsx" if _contains(btn, "focus-visible") else "MISSING",
        "P1"
    ))

    # Step indicator accessibility
    step = _read("components/app/step-indicator.tsx")
    checks.append(CheckResult(
        "StepIndicator: aria-current",
        _contains(step, "aria-current"),
        "aria-current on active step" if _contains(step, "aria-current") else "MISSING",
        "P1"
    ))

    # Tailwind config exists
    checks.append(CheckResult(
        "Tailwind config exists",
        _exists("tailwind.config.ts"),
        "tailwind.config.ts",
        "P0"
    ))

    # Screenshot directory
    has_screenshots = _exists("screenshots")
    checks.append(CheckResult(
        "Screenshots directory exists",
        has_screenshots,
        "screenshots/ present" if has_screenshots else "No screenshots directory",
        "P2"
    ))

    # Templates
    for tpl in [
        "project_autopilot/templates/EXTERNAL_BUILDER_VISUAL_REFERENCE.template.md",
        "project_autopilot/templates/EXTERNAL_BUILDER_IMPORT_REVIEW.template.md",
        "project_autopilot/templates/MIRA_VISUAL_QA_REVIEW.template.md",
    ]:
        checks.append(CheckResult(
            f"Template: {Path(tpl).stem}",
            _exists(tpl),
            tpl,
            "P2"
        ))

    # Nav component
    nav = _read("components/app/app-nav.tsx")
    checks.append(CheckResult(
        "AppNav: aria-label on logo",
        _contains(nav, "aria-label"),
        "logo aria-label present" if _contains(nav, "aria-label") else "MISSING",
        "P1"
    ))

    # Language toggle
    lang = _read("components/ui/language-toggle.tsx")
    checks.append(CheckResult(
        "LanguageToggle: aria-labels",
        _contains(lang, "aria-label"),
        "language labels present" if _contains(lang, "aria-label") else "MISSING",
        "P1"
    ))

    return checks


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_markdown(report: VisualQAReport) -> str:
    lines = [
        f"# MIRA Visual QA Report",
        f"",
        f"**Project:** {report.project}",
        f"**Generated:** {report.generated_at}",
        f"**Overall:** {report.overall}",
        f"",
        "---",
        "",
    ]

    # Page reports
    for page in report.pages:
        emoji = {"PASS": "[OK]", "WARN": "[!!]", "FAIL": "[XX]"}.get(page.verdict, "[??]")
        lines.append(f"## {emoji} {page.page} ({page.passed}/{page.total})")
        lines.append(f"Path: `{page.path}`\n")
        for c in page.checks:
            mark = "[OK]" if c.ok else f"[{c.severity}]"
            lines.append(f"- {mark} {c.name}: {c.detail}")
        lines.append("")

    # Meta checks
    lines.append("## Project-Level Checks")
    lines.append("")
    for c in report.meta_checks:
        mark = "[OK]" if c.ok else f"[{c.severity}]"
        lines.append(f"- {mark} {c.name}: {c.detail}")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Page | Verdict | Passed | Total |")
    lines.append("|------|---------|--------|-------|")
    for page in report.pages:
        lines.append(f"| {page.page} | {page.verdict} | {page.passed} | {page.total} |")
    meta_passed = sum(1 for c in report.meta_checks if c.ok)
    lines.append(f"| Meta | — | {meta_passed} | {len(report.meta_checks)} |")
    lines.append("")

    # Issues
    issues = []
    for page in report.pages:
        for c in page.checks:
            if not c.ok:
                issues.append((page.page, c))
    for c in report.meta_checks:
        if not c.ok:
            issues.append(("Meta", c))

    if issues:
        lines.append("## Issues Found")
        lines.append("")
        lines.append("| Page | Severity | Check | Detail |")
        lines.append("|------|----------|-------|--------|")
        for page_name, c in issues:
            lines.append(f"| {page_name} | {c.severity} | {c.name} | {c.detail} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_visual_qa(project: str) -> VisualQAReport:
    report = VisualQAReport(project=project)
    report.generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Check each page
    for page_def in MIRA_PAGES:
        report.pages.append(check_page(page_def))

    # Meta checks
    report.meta_checks = check_meta()

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="MIRA Visual QA Tool")
    parser.add_argument("--project", required=True, help="Project name (e.g., mira)")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    args = parser.parse_args()

    report = run_visual_qa(args.project)

    # Write reports
    logs_dir = REPO_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    md_path = logs_dir / f"{args.project}_visual_qa_latest.md"
    md_content = generate_markdown(report)
    md_path.write_text(md_content, encoding="utf-8")

    json_path = logs_dir / f"{args.project}_visual_qa_latest.json"
    json_data = {
        "project": report.project,
        "generated_at": report.generated_at,
        "overall": report.overall,
        "pages": [
            {
                "page": p.page,
                "path": p.path,
                "verdict": p.verdict,
                "passed": p.passed,
                "total": p.total,
                "checks": [
                    {"name": c.name, "ok": c.ok, "detail": c.detail, "severity": c.severity}
                    for c in p.checks
                ],
            }
            for p in report.pages
        ],
        "meta_checks": [
            {"name": c.name, "ok": c.ok, "detail": c.detail, "severity": c.severity}
            for c in report.meta_checks
        ],
    }
    json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

    # Console output
    if args.json:
        print(json.dumps(json_data, indent=2))
    else:
        print(md_content)

    print(f"\nMarkdown report: {md_path}")
    print(f"JSON report: {json_path}")
    print(f"\nOverall verdict: {report.overall}")

    sys.exit(0 if report.overall in ("PASS", "PASS_WITH_ISSUES") else 1)


if __name__ == "__main__":
    main()
