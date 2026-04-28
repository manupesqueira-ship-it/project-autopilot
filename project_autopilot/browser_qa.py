"""Browser-based QA evidence collector for Project Autopilot.

Uses Playwright when available to walk configured routes, capture HTTP status,
detect console/page errors, and take screenshots.  Skips gracefully when
Playwright is not installed or the dev server is not running.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import ProjectConfig


@dataclass
class RouteResult:
    url: str
    status: int | None = None
    console_errors: list[str] = field(default_factory=list)
    page_errors: list[str] = field(default_factory=list)
    screenshot_path: str | None = None
    error: str | None = None


@dataclass
class BrowserQAReport:
    project_id: str
    timestamp: str
    playwright_available: bool
    dev_server_reachable: bool
    routes: list[RouteResult] = field(default_factory=list)
    summary: str = ""

    @property
    def passed(self) -> bool:
        if not self.dev_server_reachable:
            return False
        return all(
            r.status is not None and 200 <= r.status < 400
            and not r.console_errors and not r.page_errors
            for r in self.routes
        )


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _check_playwright() -> bool:
    try:
        import playwright.sync_api  # noqa: F401
        return True
    except ImportError:
        return False


def _check_server(url: str) -> bool:
    """Quick HTTP HEAD to see if the dev server is reachable."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=5):
            return True
    except Exception:
        return False


def _screenshot_dir(project: ProjectConfig) -> Path:
    base = project.repo_path / project.screenshots_dir / project.project_id
    base.mkdir(parents=True, exist_ok=True)
    return base


def _run_with_playwright(project: ProjectConfig) -> list[RouteResult]:
    """Walk routes using Playwright.  Only called when Playwright is confirmed available."""
    from playwright.sync_api import sync_playwright  # noqa: E402

    results: list[RouteResult] = []
    ss_dir = _screenshot_dir(project)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        for url in project.route_walk_urls:
            rr = RouteResult(url=url)
            console_errors: list[str] = []
            page_errors: list[str] = []

            page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))

            try:
                response = page.goto(url, wait_until="networkidle", timeout=15000)
                rr.status = response.status if response else None

                # Screenshot
                slug = url.split("//", 1)[-1].replace("/", "_").replace(":", "")
                ss_path = ss_dir / f"{slug}.png"
                page.screenshot(path=str(ss_path), full_page=True)
                rr.screenshot_path = str(ss_path.relative_to(project.repo_path))
            except Exception as exc:
                rr.error = str(exc)

            rr.console_errors = list(console_errors)
            rr.page_errors = list(page_errors)
            console_errors.clear()
            page_errors.clear()
            results.append(rr)

        browser.close()

    return results


def _run_with_http(project: ProjectConfig) -> list[RouteResult]:
    """Fallback: check routes with plain HTTP GET (no screenshots, no console errors)."""
    results: list[RouteResult] = []
    for url in project.route_walk_urls:
        rr = RouteResult(url=url)
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                rr.status = resp.status
        except urllib.error.HTTPError as exc:
            rr.status = exc.code
            rr.error = f"HTTP {exc.code}"
        except Exception as exc:
            rr.error = str(exc)
        results.append(rr)
    return results


def run_browser_qa(project: ProjectConfig) -> BrowserQAReport:
    """Run browser QA against configured route_walk_urls."""
    report = BrowserQAReport(
        project_id=project.project_id,
        timestamp=_utc_stamp(),
        playwright_available=_check_playwright(),
        dev_server_reachable=False,
    )

    if not project.route_walk_urls:
        report.summary = "No route_walk_urls configured. Skipping browser QA."
        return report

    # Check if server is reachable using the first URL
    first_url = project.route_walk_urls[0]
    report.dev_server_reachable = _check_server(first_url)

    if not report.dev_server_reachable:
        report.summary = (
            f"Dev server not reachable at {first_url}.\n"
            f"Start the dev server first: {project.dev_server_command or 'npm run dev'}"
        )
        return report

    if report.playwright_available:
        report.routes = _run_with_playwright(project)
        report.summary = f"Playwright walk: {len(report.routes)} routes checked."
    else:
        report.routes = _run_with_http(project)
        report.summary = (
            f"HTTP-only walk: {len(report.routes)} routes checked (no screenshots, no console checks).\n"
            "Install Playwright for full browser QA:\n"
            "  pip install playwright\n"
            "  python -m playwright install chromium"
        )

    return report


def write_browser_qa_report(project: ProjectConfig, report: BrowserQAReport) -> Path:
    """Write the browser QA report as markdown under logs/."""
    logs_dir = project.repo_path / project.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    path = logs_dir / f"{project.project_id}_browser_qa_latest.md"

    lines = [
        "# Browser QA Report",
        "",
        f"Timestamp: {report.timestamp}",
        f"Project: {project.project_name} ({project.project_id})",
        f"Playwright: {'available' if report.playwright_available else 'not installed'}",
        f"Dev server: {'reachable' if report.dev_server_reachable else 'NOT reachable'}",
        f"Overall: {'PASS' if report.passed else 'FAIL' if report.dev_server_reachable else 'SKIPPED'}",
        "",
        f"{report.summary}",
        "",
    ]

    for rr in report.routes:
        status_str = str(rr.status) if rr.status is not None else "N/A"
        icon = "PASS" if (rr.status and 200 <= rr.status < 400 and not rr.console_errors and not rr.page_errors) else "FAIL"
        lines.append(f"## [{icon}] {rr.url}")
        lines.append(f"- HTTP status: {status_str}")
        if rr.console_errors:
            lines.append(f"- Console errors ({len(rr.console_errors)}):")
            for e in rr.console_errors[:10]:
                lines.append(f"  - {e}")
        if rr.page_errors:
            lines.append(f"- Page errors ({len(rr.page_errors)}):")
            for e in rr.page_errors[:10]:
                lines.append(f"  - {e}")
        if rr.screenshot_path:
            lines.append(f"- Screenshot: {rr.screenshot_path}")
        if rr.error:
            lines.append(f"- Error: {rr.error}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def report_to_evidence(report: BrowserQAReport) -> dict[str, Any]:
    """Convert a BrowserQAReport into a dict suitable for evidence collection."""
    return {
        "browser_qa_passed": report.passed,
        "playwright_available": report.playwright_available,
        "dev_server_reachable": report.dev_server_reachable,
        "routes_checked": len(report.routes),
        "routes_passed": sum(
            1 for r in report.routes
            if r.status and 200 <= r.status < 400 and not r.console_errors and not r.page_errors
        ),
        "console_errors_total": sum(len(r.console_errors) for r in report.routes),
        "page_errors_total": sum(len(r.page_errors) for r in report.routes),
        "summary": report.summary,
    }
