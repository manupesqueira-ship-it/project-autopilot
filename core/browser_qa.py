"""Browser QA evidence collector for Project Autopilot.

Browser QA first diagnoses which configured URL is reachable, including
localhost/127.0.0.1 and common Next.js dev ports. It then runs the current QA
pass against that runtime base without rewriting project config.

P0 features:
- Network request/response interception (4xx/5xx, failed loads).
- Config-driven multiple viewport screenshots.
- PASS / WARN / FAIL verdict with clear semantics.
- Security: no auth headers, cookies, bearer tokens, JWTs, or bodies logged.
"""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from config import ProjectConfig

DEFAULT_VIEWPORTS: dict[str, dict[str, int]] = {
    "mobile": {"width": 375, "height": 812},
    "tablet": {"width": 768, "height": 1024},
    "desktop": {"width": 1280, "height": 800},
}

COMMON_NEXT_PORTS = [3000, 3001, 3002, 3003]


def _parse_config_viewports(raw: dict[str, str]) -> dict[str, dict[str, int]]:
    """Parse viewport config like ``{'mobile': '375x812'}`` into sized dicts."""
    viewports: dict[str, dict[str, int]] = {}
    for name, spec in raw.items():
        parts = str(spec).lower().split("x")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            viewports[name] = {"width": int(parts[0]), "height": int(parts[1])}
    return viewports


def resolve_viewports(project: ProjectConfig) -> dict[str, dict[str, int]]:
    """Return viewports from config, falling back to DEFAULT_VIEWPORTS."""
    if project.browser_qa_viewports:
        parsed = _parse_config_viewports(project.browser_qa_viewports)
        if parsed:
            return parsed
    return dict(DEFAULT_VIEWPORTS)


@dataclass
class NetworkFailure:
    url: str
    method: str = "GET"
    status: int | None = None
    resource_type: str = ""
    failure_text: str = ""
    route_url: str = ""
    viewport: str = ""


@dataclass
class ReachabilityCheck:
    url: str
    status: int | None = None
    passed: bool = False
    duration_seconds: float = 0.0
    error: str = ""


@dataclass
class BrowserQADiagnostics:
    configured_url: str = ""
    selected_runtime_url: str | None = None
    selected_base_url: str | None = None
    ports_tested: list[int] = field(default_factory=list)
    checks: list[ReachabilityCheck] = field(default_factory=list)

    @property
    def reachable(self) -> bool:
        return self.selected_runtime_url is not None


@dataclass
class RouteResult:
    url: str
    configured_url: str = ""
    viewport: str = "http_only"
    viewport_size: dict[str, int] | None = None
    status: int | None = None
    duration_seconds: float = 0.0
    console_errors: list[str] = field(default_factory=list)
    page_errors: list[str] = field(default_factory=list)
    failed_network_requests: list[NetworkFailure] = field(default_factory=list)
    failed_resource_loads: list[NetworkFailure] = field(default_factory=list)
    screenshot_path: str | None = None
    error: str | None = None

    @property
    def passed(self) -> bool:
        return (
            self.status is not None
            and 200 <= self.status < 400
            and not self.console_errors
            and not self.page_errors
            and not self.failed_network_requests
            and not self.failed_resource_loads
            and not self.error
        )


@dataclass
class BrowserQAReport:
    project_id: str
    run_id: str
    timestamp: str
    mode: str
    playwright_available: bool
    dev_server_reachable: bool
    dev_server_url: str = ""
    viewport_coverage: dict[str, dict[str, int]] = field(default_factory=dict)
    routes: list[RouteResult] = field(default_factory=list)
    summary: str = ""
    limitations: list[str] = field(default_factory=list)
    diagnostics: BrowserQADiagnostics = field(default_factory=BrowserQADiagnostics)

    @property
    def passed(self) -> bool:
        if not self.dev_server_reachable or not self.routes:
            return False
        return all(route.passed for route in self.routes)

    @property
    def verdict(self) -> str:
        """PASS / WARN / FAIL / SKIPPED_DEV_SERVER_DOWN.

        - PASS: all routes passed in Playwright mode.
        - WARN: HTTP-only fallback was used (cannot validate client-side).
        - FAIL: at least one route failed.
        - SKIPPED_DEV_SERVER_DOWN: dev server not reachable.
        """
        if not self.dev_server_reachable:
            return "SKIPPED_DEV_SERVER_DOWN"
        if not self.routes:
            return "SKIPPED_DEV_SERVER_DOWN"
        if not all(route.passed for route in self.routes):
            return "FAIL"
        if self.mode == "http_only":
            return "WARN"
        return "PASS"

    # Keep legacy property for backwards compat in state/events.
    @property
    def outcome(self) -> str:
        return self.verdict

    @property
    def summary_counts(self) -> dict[str, int]:
        return {
            "routes_checked": len(self.routes),
            "routes_passed": sum(1 for route in self.routes if route.passed),
            "routes_failed": sum(1 for route in self.routes if not route.passed),
            "console_errors": sum(len(route.console_errors) for route in self.routes),
            "page_errors": sum(len(route.page_errors) for route in self.routes),
            "failed_network_requests": sum(
                len(route.failed_network_requests) for route in self.routes
            ),
            "failed_resource_loads": sum(
                len(route.failed_resource_loads) for route in self.routes
            ),
            "screenshots_captured": sum(1 for route in self.routes if route.screenshot_path),
        }

    @property
    def total_issues(self) -> int:
        counts = self.summary_counts
        return (
            counts["routes_failed"]
            + counts["console_errors"]
            + counts["page_errors"]
            + counts["failed_network_requests"]
            + counts["failed_resource_loads"]
        )


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _file_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _check_playwright() -> bool:
    try:
        import playwright.sync_api  # noqa: F401
        return True
    except ImportError:
        return False


def _probe_url(url: str, timeout: int = 5) -> ReachabilityCheck:
    started = perf_counter()
    check = ReachabilityCheck(url=url)
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "ProjectAutopilotBrowserQA/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            check.status = response.status
            check.passed = 200 <= response.status < 400
    except urllib.error.HTTPError as exc:
        check.status = exc.code
        check.error = f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        check.error = str(getattr(exc, "reason", exc))
    except Exception as exc:
        check.error = str(exc)
    check.duration_seconds = round(perf_counter() - started, 3)
    return check


def _check_server(url: str) -> bool:
    return _probe_url(url).passed


def _base_url(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))


def _replace_base(url: str, base_url: str) -> str:
    original = urlsplit(url)
    base = urlsplit(base_url)
    return urlunsplit((base.scheme, base.netloc, original.path or "/", original.query, original.fragment))


def _with_host_port(url: str, host: str, port: int) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme or "http", f"{host}:{port}", parsed.path or "/", parsed.query, parsed.fragment))


def _candidate_urls(url: str) -> list[str]:
    parsed = urlsplit(url)
    host = parsed.hostname or ""
    configured_port = parsed.port or (443 if parsed.scheme == "https" else 80)
    hosts = [host]
    if host == "localhost":
        hosts.append("127.0.0.1")
    elif host == "127.0.0.1":
        hosts.append("localhost")

    ports = [configured_port]
    if (parsed.scheme in {"", "http"}) and host in {"localhost", "127.0.0.1"}:
        ports.extend(port for port in COMMON_NEXT_PORTS if port not in ports)

    candidates: list[str] = []
    for candidate_host in hosts:
        for port in ports:
            candidate = _with_host_port(url, candidate_host, port)
            if candidate not in candidates:
                candidates.append(candidate)
    if url not in candidates:
        candidates.insert(0, url)
    return candidates


def diagnose_browser_qa(project: ProjectConfig) -> BrowserQADiagnostics:
    configured_url = project.route_walk_urls[0] if project.route_walk_urls else ""
    diagnostics = BrowserQADiagnostics(configured_url=configured_url)
    ports_tested: list[int] = []
    seen: set[str] = set()

    for route_url in project.route_walk_urls:
        for candidate in _candidate_urls(route_url):
            if candidate in seen:
                continue
            seen.add(candidate)
            parsed = urlsplit(candidate)
            if parsed.port and parsed.port not in ports_tested:
                ports_tested.append(parsed.port)
            check = _probe_url(candidate)
            diagnostics.checks.append(check)
            if check.passed and diagnostics.selected_runtime_url is None:
                diagnostics.selected_runtime_url = check.url
                diagnostics.selected_base_url = _base_url(check.url)

    diagnostics.ports_tested = ports_tested
    return diagnostics


def _safe_route_name(url: str) -> str:
    raw = url.split("//", 1)[-1]
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", raw).strip("_")
    return safe[:120] or "route"


def _screenshots_base(project: ProjectConfig) -> Path:
    configured = project.repo_path / project.screenshots_dir
    if configured.name == project.project_id:
        return configured
    return project.repo_path / "screenshots" / project.project_id


def _relative(project: ProjectConfig, path: Path) -> str:
    try:
        return str(path.relative_to(project.repo_path))
    except ValueError:
        return str(path)


def _network_failure_from_response(response: Any, route_url: str, viewport: str) -> NetworkFailure:
    """Capture failed response metadata. Never logs headers, cookies, tokens, or bodies."""
    request = response.request
    return NetworkFailure(
        url=response.url,
        method=request.method,
        status=response.status,
        resource_type=request.resource_type,
        route_url=route_url,
        viewport=viewport,
    )


def _network_failure_from_request(request: Any, route_url: str, viewport: str) -> NetworkFailure:
    """Capture failed request metadata. Never logs headers, cookies, tokens, or bodies."""
    failure = request.failure
    failure_text = ""
    if callable(failure):
        failure_value = failure()
        if isinstance(failure_value, dict):
            failure_text = str(failure_value.get("errorText", ""))
        elif failure_value:
            failure_text = str(failure_value)
    return NetworkFailure(
        url=request.url,
        method=request.method,
        resource_type=request.resource_type,
        failure_text=failure_text or "request failed",
        route_url=route_url,
        viewport=viewport,
    )


def _runtime_routes(configured_urls: list[str], runtime_base: str) -> list[tuple[str, str]]:
    return [(configured, _replace_base(configured, runtime_base)) for configured in configured_urls]


def _run_with_playwright(
    project: ProjectConfig,
    run_id: str,
    route_pairs: list[tuple[str, str]],
    viewports: dict[str, dict[str, int]],
) -> tuple[list[RouteResult], list[str]]:
    from playwright.sync_api import sync_playwright  # noqa: E402

    results: list[RouteResult] = []
    limitations: list[str] = []
    screenshots_base = _screenshots_base(project) / run_id

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for viewport_name, viewport_size in viewports.items():
                context = browser.new_context(viewport=viewport_size)
                for configured_url, runtime_url in route_pairs:
                    result = RouteResult(
                        url=runtime_url,
                        configured_url=configured_url,
                        viewport=viewport_name,
                        viewport_size=dict(viewport_size),
                    )
                    console_errors: list[str] = []
                    page_errors: list[str] = []
                    failed_responses: list[NetworkFailure] = []
                    failed_loads: list[NetworkFailure] = []
                    page = context.new_page()

                    page.on(
                        "console",
                        lambda msg, bucket=console_errors: bucket.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None,
                    )
                    page.on("pageerror", lambda exc, bucket=page_errors: bucket.append(str(exc)))
                    page.on(
                        "response",
                        lambda response, bucket=failed_responses, route=runtime_url, vp=viewport_name: bucket.append(
                            _network_failure_from_response(response, route, vp)
                        )
                        if response.status >= 400
                        else None,
                    )
                    page.on(
                        "requestfailed",
                        lambda request, bucket=failed_loads, route=runtime_url, vp=viewport_name: bucket.append(
                            _network_failure_from_request(request, route, vp)
                        ),
                    )

                    started = perf_counter()
                    try:
                        response = page.goto(runtime_url, wait_until="networkidle", timeout=20000)
                        result.status = response.status if response else None
                        if project.screenshot_enabled:
                            screenshot_dir = screenshots_base / viewport_name
                            screenshot_dir.mkdir(parents=True, exist_ok=True)
                            screenshot_path = screenshot_dir / f"{_safe_route_name(runtime_url)}.png"
                            page.screenshot(path=str(screenshot_path), full_page=True)
                            result.screenshot_path = _relative(project, screenshot_path)
                    except Exception as exc:
                        result.error = str(exc)
                    finally:
                        result.duration_seconds = round(perf_counter() - started, 3)
                        result.console_errors = console_errors
                        result.page_errors = page_errors
                        result.failed_network_requests = failed_responses
                        result.failed_resource_loads = failed_loads
                        page.close()
                        results.append(result)
                context.close()
            browser.close()
    except Exception as exc:
        limitations.append(f"Playwright mode failed: {exc}")
        return [], limitations

    return results, limitations


def _run_with_http(route_pairs: list[tuple[str, str]]) -> list[RouteResult]:
    results: list[RouteResult] = []
    for configured_url, runtime_url in route_pairs:
        result = RouteResult(url=runtime_url, configured_url=configured_url, viewport="http_only")
        started = perf_counter()
        try:
            req = urllib.request.Request(runtime_url, method="GET", headers={"User-Agent": "ProjectAutopilotBrowserQA/1.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                result.status = response.status
        except urllib.error.HTTPError as exc:
            result.status = exc.code
            result.error = f"HTTP {exc.code}"
            result.failed_network_requests.append(
                NetworkFailure(url=runtime_url, method="GET", status=exc.code, route_url=runtime_url, viewport="http_only")
            )
        except Exception as exc:
            result.error = str(exc)
            result.failed_resource_loads.append(
                NetworkFailure(url=runtime_url, method="GET", failure_text=str(exc), route_url=runtime_url, viewport="http_only")
            )
        result.duration_seconds = round(perf_counter() - started, 3)
        results.append(result)
    return results


def run_browser_qa(project: ProjectConfig, run_id: str | None = None) -> BrowserQAReport:
    """Run browser QA against configured route_walk_urls."""
    run_id = run_id or f"{project.project_id}_browser_qa_{_file_stamp()}"
    playwright_available = _check_playwright()
    mode = "playwright" if playwright_available else "http_only"
    viewports = resolve_viewports(project)
    report = BrowserQAReport(
        project_id=project.project_id,
        run_id=run_id,
        timestamp=_utc_stamp(),
        mode=mode,
        playwright_available=playwright_available,
        dev_server_reachable=False,
        viewport_coverage=viewports if playwright_available else {},
    )

    if not project.route_walk_urls:
        report.summary = "No route_walk_urls configured. Skipping browser QA."
        report.limitations.append("No routes were configured for Browser QA.")
        return report

    diagnostics = diagnose_browser_qa(project)
    report.diagnostics = diagnostics
    report.dev_server_url = diagnostics.selected_runtime_url or diagnostics.configured_url

    if not playwright_available:
        report.limitations.extend(
            [
                "LIMITED_HTTP_ONLY_MODE: Playwright not installed.",
                "HTTP-only fallback cannot validate client-side behavior.",
                "No screenshots, console errors, page errors, or subresource network requests were captured.",
                "Install with: pip install playwright && python -m playwright install chromium",
            ]
        )

    report.dev_server_reachable = diagnostics.reachable
    if not diagnostics.reachable:
        start_cmd = project.dev_server_command or "npm run dev"
        report.summary = (
            f"SKIPPED_DEV_SERVER_DOWN: Dev server not reachable. "
            f"Start the dev server first: {start_cmd}"
        )
        report.limitations.append(
            f"Dev server not reachable at any tested URL. Start with: {start_cmd}"
        )
        return report

    route_pairs = _runtime_routes(project.route_walk_urls, diagnostics.selected_base_url or _base_url(diagnostics.selected_runtime_url or ""))

    if playwright_available:
        routes, limitations = _run_with_playwright(project, run_id, route_pairs, viewports)
        report.limitations.extend(limitations)
        if routes:
            report.routes = routes
            report.mode = "playwright"
            report.summary = f"Playwright Browser QA checked {len(routes)} route/viewport combinations."
        else:
            report.mode = "http_only"
            report.playwright_available = False
            report.viewport_coverage = {}
            report.routes = _run_with_http(route_pairs)
            report.limitations.append("Fell back to HTTP-only checks after Playwright failed.")
            report.limitations.append("HTTP-only fallback cannot validate client-side behavior.")
            report.summary = f"HTTP-only Browser QA checked {len(report.routes)} routes after Playwright fallback."
    else:
        report.routes = _run_with_http(route_pairs)
        report.summary = f"LIMITED_HTTP_ONLY_MODE: HTTP-only Browser QA checked {len(report.routes)} routes."

    return report


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


def _network_rows(routes: list[RouteResult]) -> list[str]:
    rows = ["| Route | Viewport | Type | Method | Status | Resource | URL | Failure |", "|---|---|---|---|---:|---|---|---|"]
    count = 0
    for route in routes:
        for failure in route.failed_network_requests:
            rows.append(
                f"| {route.url} | {route.viewport} | response | {failure.method} | {failure.status or ''} | "
                f"{failure.resource_type or ''} | {failure.url} | {failure.failure_text or ''} |"
            )
            count += 1
        for failure in route.failed_resource_loads:
            rows.append(
                f"| {route.url} | {route.viewport} | requestfailed | {failure.method} | {failure.status or ''} | "
                f"{failure.resource_type or ''} | {failure.url} | {failure.failure_text or ''} |"
            )
            count += 1
    if count == 0:
        rows.append("| None |  |  |  |  |  |  |  |")
    return rows


def _error_rows(routes: list[RouteResult]) -> list[str]:
    rows = ["| Route | Viewport | Source | Message |", "|---|---|---|---|"]
    count = 0
    for route in routes:
        for error in route.console_errors:
            rows.append(f"| {route.url} | {route.viewport} | console | {error} |")
            count += 1
        for error in route.page_errors:
            rows.append(f"| {route.url} | {route.viewport} | pageerror | {error} |")
            count += 1
        if route.error:
            rows.append(f"| {route.url} | {route.viewport} | route | {route.error} |")
            count += 1
    if count == 0:
        rows.append("| None |  |  |  |")
    return rows


def _diagnostic_rows(diagnostics: BrowserQADiagnostics) -> list[str]:
    rows = ["| URL | Result | Status | Duration | Error |", "|---|---|---:|---:|---|"]
    for check in diagnostics.checks:
        rows.append(
            f"| {check.url} | {'PASS' if check.passed else 'FAIL'} | "
            f"{check.status if check.status is not None else ''} | {check.duration_seconds:.3f}s | {check.error} |"
        )
    if not diagnostics.checks:
        rows.append("| None |  |  |  |  |")
    return rows


def write_browser_qa_report(project: ProjectConfig, report: BrowserQAReport) -> Path:
    """Write latest and run-specific Browser QA markdown reports under logs/."""
    logs_dir = project.repo_path / project.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    latest_path = logs_dir / f"{project.project_id}_browser_qa_latest.md"
    run_path = logs_dir / f"{project.project_id}_browser_qa_{_file_stamp()}.md"
    counts = report.summary_counts

    route_rows = [
        "| Configured Route | Runtime Route | Viewport | Status | Duration | Result | Screenshot |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for route in report.routes:
        route_rows.append(
            f"| {route.configured_url or route.url} | {route.url} | {route.viewport} | "
            f"{route.status if route.status is not None else ''} | {route.duration_seconds:.3f}s | "
            f"{'PASS' if route.passed else 'FAIL'} | {route.screenshot_path or ''} |"
        )
    if not report.routes:
        route_rows.append("| None |  |  |  |  | SKIPPED |  |")

    screenshot_lines = [f"- {route.screenshot_path}" for route in report.routes if route.screenshot_path] or ["- None"]
    viewport_lines = [
        f"- {name}: {size['width']}x{size['height']}" for name, size in report.viewport_coverage.items()
    ] or ["- HTTP-only mode: no viewport rendering"]

    # Build limitations with clear pass/fail semantics.
    limitations = list(report.limitations) or ["No Browser QA limitations recorded."]
    limitations.append("Browser QA does not fill forms, click buttons, or test multi-step flows.")
    limitations.append("Browser QA does not verify database writes or business logic.")
    limitations.append("Browser QA does not perform visual regression testing.")
    limitations.append("Browser QA does not run accessibility audits.")

    # Verdict explanation.
    verdict = report.verdict
    verdict_explanation = {
        "PASS": "All routes returned 2xx/3xx, zero console errors, zero page errors, zero failed network requests in Playwright mode.",
        "WARN": "All routes returned 2xx/3xx in HTTP-only mode. HTTP-only fallback cannot validate client-side behavior (console errors, page errors, subresource failures, responsive layout).",
        "FAIL": "One or more routes failed: non-2xx/3xx status, console errors, page errors, or failed network requests detected.",
        "SKIPPED_DEV_SERVER_DOWN": f"Dev server not reachable. Start with: {project.dev_server_command or 'npm run dev'}",
    }.get(verdict, "Unknown verdict.")

    content = "\n".join(
        [
            "# Browser QA Report",
            "",
            f"**Project:** {project.project_name} ({project.project_id})",
            f"**Run id:** {report.run_id}",
            f"**Timestamp:** {report.timestamp}",
            f"**Mode:** {report.mode}",
            f"**Playwright:** {'available' if report.playwright_available else 'not installed/unavailable'}",
            f"**Dev server:** {'reachable' if report.dev_server_reachable else 'NOT reachable'}",
            f"**Dev server URL:** {report.dev_server_url or 'none'}",
            f"**Verdict:** {verdict}",
            "",
            f"> {verdict_explanation}",
            "",
            "## Summary",
            "",
            f"| Metric | Count |",
            f"|---|---:|",
            f"| Routes tested | {counts['routes_checked']} |",
            f"| Routes passed | {counts['routes_passed']} |",
            f"| Routes failed | {counts['routes_failed']} |",
            f"| Console errors | {counts['console_errors']} |",
            f"| Page errors | {counts['page_errors']} |",
            f"| Failed network requests | {counts['failed_network_requests']} |",
            f"| Failed resource loads | {counts['failed_resource_loads']} |",
            f"| Screenshots captured | {counts['screenshots_captured']} |",
            f"| Total issues | {report.total_issues} |",
            "",
            report.summary,
            "",
            "## Reachability Diagnostics",
            "",
            f"Configured URL: {report.diagnostics.configured_url or 'none'}",
            f"Selected runtime URL: {report.diagnostics.selected_runtime_url or 'none'}",
            f"Selected runtime base: {report.diagnostics.selected_base_url or 'none'}",
            f"Ports tested: {', '.join(str(port) for port in report.diagnostics.ports_tested) or 'none'}",
            "",
            "\n".join(_diagnostic_rows(report.diagnostics)),
            "",
            "## Viewport Coverage",
            "",
            f"Viewports configured: {len(report.viewport_coverage)}",
            "",
            "\n".join(viewport_lines),
            "",
            "## Route Table",
            "",
            "\n".join(route_rows),
            "",
            "## Failed Network Requests",
            "",
            "\n".join(_network_rows(report.routes)),
            "",
            "## Console And Page Errors",
            "",
            "\n".join(_error_rows(report.routes)),
            "",
            "## Screenshots",
            "",
            "\n".join(screenshot_lines),
            "",
            "## Limitations",
            "",
            "\n".join(f"- {item}" for item in limitations),
            "",
            "## Security",
            "",
            "- No auth headers, cookies, bearer tokens, JWTs, or request bodies are logged.",
            "- Only URL, method, status code, and resource type are captured from network events.",
            "",
        ]
    )
    latest_path.write_text(content, encoding="utf-8")
    run_path.write_text(content, encoding="utf-8")
    return latest_path


def write_browser_qa_diagnostics_report(project: ProjectConfig, diagnostics: BrowserQADiagnostics) -> Path:
    logs_dir = project.repo_path / project.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    path = logs_dir / f"{project.project_id}_browser_qa_diagnostics_latest.md"
    content = "\n".join(
        [
            "# Browser QA Diagnostics",
            "",
            f"Timestamp: {_utc_stamp()}",
            f"Project: {project.project_name} ({project.project_id})",
            f"Configured URL: {diagnostics.configured_url or 'none'}",
            f"Selected runtime URL: {diagnostics.selected_runtime_url or 'none'}",
            f"Selected runtime base: {diagnostics.selected_base_url or 'none'}",
            f"Ports tested: {', '.join(str(port) for port in diagnostics.ports_tested) or 'none'}",
            "",
            "## Reachability",
            "",
            "\n".join(_diagnostic_rows(diagnostics)),
            "",
            "## Notes",
            "",
            "- Diagnostics do not require Playwright.",
            "- Diagnostics do not capture screenshots.",
            "- Diagnostics do not submit forms or modify product data.",
            "- Config is not rewritten; any detected runtime URL is used only for the current run.",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")
    return path


def report_to_evidence(report: BrowserQAReport) -> dict[str, Any]:
    """Convert a BrowserQAReport into a dict suitable for evidence collection."""
    counts = report.summary_counts
    return {
        "browser_qa_passed": report.passed,
        "run_id": report.run_id,
        "mode": report.mode,
        "verdict": report.verdict,
        "outcome": report.outcome,
        "playwright_available": report.playwright_available,
        "dev_server_reachable": report.dev_server_reachable,
        "dev_server_url": report.dev_server_url,
        "viewport_coverage": report.viewport_coverage,
        "routes_checked": counts["routes_checked"],
        "routes_passed": counts["routes_passed"],
        "routes_failed": counts["routes_failed"],
        "console_errors_total": counts["console_errors"],
        "page_errors_total": counts["page_errors"],
        "failed_network_requests_total": counts["failed_network_requests"],
        "failed_resource_loads_total": counts["failed_resource_loads"],
        "screenshots_captured": counts["screenshots_captured"],
        "total_issues": report.total_issues,
        "summary": report.summary,
        "limitations": report.limitations,
        "configured_url": report.diagnostics.configured_url,
        "selected_runtime_url": report.diagnostics.selected_runtime_url,
        "selected_runtime_base_url": report.diagnostics.selected_base_url,
        "ports_tested": report.diagnostics.ports_tested,
    }
