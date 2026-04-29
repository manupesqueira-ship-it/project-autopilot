"""Flow QA framework for Project Autopilot.

Non-destructive, Playwright-based flow validation for project routes,
selectors, and safe dry-run interactions.

CLI:
    python -B project_autopilot/flow_qa.py --project mira --list
    python -B project_autopilot/flow_qa.py --project mira --dry-run
    python -B project_autopilot/flow_qa.py --project mira --diagnose
    python -B project_autopilot/flow_qa.py --project mira --run <flow_name>

Safety:
    - All flows are non-destructive by default.
    - No form submission unless safe_mock=true.
    - No paid API calls.
    - No file uploads.
    - No database mutations.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure project_autopilot is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml  # type: ignore[import-untyped]

FLOWS_DIR = Path(__file__).resolve().parent / "config" / "projects"
LOGS_BASE = Path(__file__).resolve().parent.parent / "logs" / "flow_qa"

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class StepResult:
    verb: str
    status: str  # PASS, FAIL, SKIP, BLOCKED
    detail: str = ""
    selector: str = ""
    screenshot: str = ""


@dataclass
class FlowResult:
    schema_version: str = "1.0"
    run_id: str = ""
    project: str = ""
    flow_name: str = ""
    status: str = "PENDING"  # PASS, WARN, FAIL, BLOCKED, SKIPPED
    started_at_utc: str = ""
    ended_at_utc: str = ""
    steps_total: int = 0
    steps_passed: int = 0
    steps_failed: int = 0
    steps_blocked: int = 0
    steps_skipped: int = 0
    blockers: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    console_errors: list[str] = field(default_factory=list)
    page_errors: list[str] = field(default_factory=list)
    network_errors: list[str] = field(default_factory=list)
    step_results: list[dict[str, Any]] = field(default_factory=list)
    report_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "project": self.project,
            "flow_name": self.flow_name,
            "status": self.status,
            "started_at_utc": self.started_at_utc,
            "ended_at_utc": self.ended_at_utc,
            "steps_total": self.steps_total,
            "steps_passed": self.steps_passed,
            "steps_failed": self.steps_failed,
            "steps_blocked": self.steps_blocked,
            "steps_skipped": self.steps_skipped,
            "blockers": self.blockers,
            "screenshots": self.screenshots,
            "console_errors": self.console_errors,
            "page_errors": self.page_errors,
            "network_errors": self.network_errors,
            "step_results": self.step_results,
            "report_path": self.report_path,
        }


# ---------------------------------------------------------------------------
# Flow config loading
# ---------------------------------------------------------------------------

def load_flows_config(project: str) -> dict[str, Any]:
    """Load mira_flows.yaml (or {project}_flows.yaml)."""
    path = FLOWS_DIR / f"{project}_flows.yaml"
    if not path.exists():
        print(f"[flow_qa] ERROR: Flow config not found: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_flow_names(config: dict[str, Any]) -> list[str]:
    return list(config.get("flows", {}).keys())


# ---------------------------------------------------------------------------
# Playwright availability
# ---------------------------------------------------------------------------

def check_playwright() -> tuple[bool, str]:
    """Check if Playwright is available."""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-untyped]
        return True, "playwright available"
    except ImportError:
        return False, "playwright not installed (pip install playwright && playwright install)"


def check_dev_server(base_url: str) -> tuple[bool, str]:
    """Check if the dev server is reachable."""
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(base_url, method="HEAD")
        urllib.request.urlopen(req, timeout=5)
        return True, f"dev server reachable at {base_url}"
    except Exception as e:
        return False, f"dev server not reachable at {base_url}: {e}"


# ---------------------------------------------------------------------------
# Flow runners
# ---------------------------------------------------------------------------

def run_route_readiness(config: dict[str, Any], flow_def: dict[str, Any],
                        project: str, run_id: str, out_dir: Path) -> FlowResult:
    """Visit routes and check for errors."""
    result = _init_result(project, "mira_route_readiness", run_id, out_dir)
    base_url = config.get("base_url", "http://localhost:3000")
    locale = config.get("locale", "es")
    routes = flow_def.get("routes", [])
    result.steps_total = len(routes)

    pw_ok, pw_msg = check_playwright()
    srv_ok, srv_msg = check_dev_server(base_url)

    if not srv_ok:
        result.status = "SKIPPED"
        result.blockers.append(srv_msg)
        result.steps_skipped = result.steps_total
        for r in routes:
            result.step_results.append({"verb": "goto", "status": "SKIP",
                                        "detail": srv_msg, "path": r["path"]})
        _finalize(result, out_dir)
        return result

    if not pw_ok:
        result.status = "SKIPPED"
        result.blockers.append(pw_msg)
        result.steps_skipped = result.steps_total
        for r in routes:
            result.step_results.append({"verb": "goto", "status": "SKIP",
                                        "detail": pw_msg, "path": r["path"]})
        _finalize(result, out_dir)
        return result

    from playwright.sync_api import sync_playwright  # type: ignore[import-untyped]

    console_errors: list[str] = []
    page_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        for route_def in routes:
            path = route_def["path"].replace("{locale}", locale)
            url = f"{base_url}{path}"
            name = route_def.get("name", path)
            try:
                resp = page.goto(url, wait_until="networkidle", timeout=15000)
                status = resp.status if resp else 0
                if status >= 400:
                    result.steps_failed += 1
                    result.network_errors.append(f"{url} -> {status}")
                    result.step_results.append({"verb": "goto", "status": "FAIL",
                                                "detail": f"HTTP {status}", "path": path})
                else:
                    result.steps_passed += 1
                    result.step_results.append({"verb": "goto", "status": "PASS",
                                                "detail": f"HTTP {status}", "path": path})
                # screenshot
                ss_dir = out_dir / "screenshots"
                ss_dir.mkdir(parents=True, exist_ok=True)
                ss_name = f"route_{name.lower().replace(' ', '_').replace('(', '').replace(')', '')}.png"
                ss_path = ss_dir / ss_name
                page.screenshot(path=str(ss_path))
                result.screenshots.append(str(ss_path))
            except Exception as e:
                result.steps_failed += 1
                result.step_results.append({"verb": "goto", "status": "FAIL",
                                            "detail": str(e), "path": path})

        browser.close()

    result.console_errors = console_errors
    result.page_errors = page_errors

    if result.steps_failed > 0:
        result.status = "FAIL"
    elif console_errors or page_errors:
        result.status = "WARN"
    else:
        result.status = "PASS"

    _finalize(result, out_dir)
    return result


def run_selector_readiness(config: dict[str, Any], flow_def: dict[str, Any],
                           project: str, run_id: str, out_dir: Path) -> FlowResult:
    """Assert selectors exist on each page."""
    result = _init_result(project, "mira_selector_readiness", run_id, out_dir)
    base_url = config.get("base_url", "http://localhost:3000")
    locale = config.get("locale", "es")
    pages = flow_def.get("pages", {})

    total_selectors = 0
    for page_def in pages.values():
        if not page_def.get("skip", False):
            total_selectors += len(page_def.get("selectors", []))
    result.steps_total = total_selectors

    pw_ok, pw_msg = check_playwright()
    srv_ok, srv_msg = check_dev_server(base_url)

    if not srv_ok:
        result.status = "SKIPPED"
        result.blockers.append(srv_msg)
        result.steps_skipped = result.steps_total
        _finalize(result, out_dir)
        return result

    if not pw_ok:
        result.status = "SKIPPED"
        result.blockers.append(pw_msg)
        result.steps_skipped = result.steps_total
        _finalize(result, out_dir)
        return result

    from playwright.sync_api import sync_playwright  # type: ignore[import-untyped]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for page_name, page_def in pages.items():
            if page_def.get("skip", False):
                skip_reason = page_def.get("skip_reason", "skipped")
                for sel in page_def.get("selectors", []):
                    result.steps_skipped += 1
                    result.step_results.append({
                        "verb": "assert_selector", "status": "SKIP",
                        "detail": skip_reason, "selector": sel, "page": page_name,
                    })
                continue

            path = page_def["path"].replace("{locale}", locale)
            url = f"{base_url}{path}"
            try:
                page.goto(url, wait_until="networkidle", timeout=15000)
            except Exception as e:
                for sel in page_def.get("selectors", []):
                    result.steps_failed += 1
                    result.step_results.append({
                        "verb": "assert_selector", "status": "FAIL",
                        "detail": f"Page load failed: {e}", "selector": sel,
                        "page": page_name,
                    })
                continue

            for sel_spec in page_def.get("selectors", []):
                # sel_spec like "data-testid=input-name"
                css = f"[{sel_spec}]"
                try:
                    el = page.query_selector(css)
                    if el:
                        result.steps_passed += 1
                        result.step_results.append({
                            "verb": "assert_selector", "status": "PASS",
                            "selector": sel_spec, "page": page_name,
                        })
                    else:
                        result.steps_failed += 1
                        result.step_results.append({
                            "verb": "assert_selector", "status": "FAIL",
                            "detail": "Selector not found",
                            "selector": sel_spec, "page": page_name,
                        })
                except Exception as e:
                    result.steps_failed += 1
                    result.step_results.append({
                        "verb": "assert_selector", "status": "FAIL",
                        "detail": str(e), "selector": sel_spec, "page": page_name,
                    })

        browser.close()

    if result.steps_failed > 0:
        result.status = "FAIL"
    elif result.steps_skipped > 0:
        result.status = "WARN"
    else:
        result.status = "PASS"

    _finalize(result, out_dir)
    return result


def run_onboarding_safe_dry(config: dict[str, Any], flow_def: dict[str, Any],
                            project: str, run_id: str, out_dir: Path) -> FlowResult:
    """Fill onboarding form locally without submitting."""
    result = _init_result(project, "mira_onboarding_safe_dry_flow", run_id, out_dir)
    base_url = config.get("base_url", "http://localhost:3000")
    locale = config.get("locale", "es")
    steps = flow_def.get("steps", [])
    result.steps_total = len(steps)

    pw_ok, pw_msg = check_playwright()
    srv_ok, srv_msg = check_dev_server(base_url)

    if not srv_ok or not pw_ok:
        blocker = srv_msg if not srv_ok else pw_msg
        result.status = "SKIPPED"
        result.blockers.append(blocker)
        result.steps_skipped = result.steps_total
        _finalize(result, out_dir)
        return result

    from playwright.sync_api import sync_playwright  # type: ignore[import-untyped]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for step in steps:
            verb = step.get("verb", "")
            try:
                if verb == "goto":
                    path = step["path"].replace("{locale}", locale)
                    url = f"{base_url}{path}"
                    page.goto(url, wait_until="networkidle", timeout=15000)
                    result.steps_passed += 1
                    result.step_results.append({"verb": "goto", "status": "PASS", "path": path})

                elif verb == "assert_selector":
                    sel = step["selector"]
                    el = page.query_selector(sel)
                    if el:
                        result.steps_passed += 1
                        result.step_results.append({"verb": "assert_selector", "status": "PASS", "selector": sel})
                    else:
                        result.steps_failed += 1
                        result.step_results.append({"verb": "assert_selector", "status": "FAIL",
                                                    "selector": sel, "detail": "Not found"})

                elif verb == "fill":
                    sel = step["selector"]
                    val = step["value"]
                    page.fill(sel, val)
                    result.steps_passed += 1
                    result.step_results.append({"verb": "fill", "status": "PASS", "selector": sel})

                elif verb == "click":
                    sel = step["selector"]
                    page.click(sel)
                    result.steps_passed += 1
                    result.step_results.append({"verb": "click", "status": "PASS", "selector": sel})

                elif verb == "screenshot":
                    ss_dir = out_dir / "screenshots"
                    ss_dir.mkdir(parents=True, exist_ok=True)
                    ss_name = step.get("name", "screenshot") + ".png"
                    ss_path = ss_dir / ss_name
                    page.screenshot(path=str(ss_path))
                    result.screenshots.append(str(ss_path))
                    result.steps_passed += 1
                    result.step_results.append({"verb": "screenshot", "status": "PASS", "path": str(ss_path)})

                elif verb == "note":
                    result.steps_passed += 1
                    result.step_results.append({"verb": "note", "status": "PASS", "detail": step.get("message", "")})

                elif verb == "blocked_reason":
                    result.steps_blocked += 1
                    result.blockers.append(step.get("message", ""))
                    result.step_results.append({"verb": "blocked_reason", "status": "BLOCKED",
                                                "detail": step.get("message", "")})

                else:
                    result.steps_skipped += 1
                    result.step_results.append({"verb": verb, "status": "SKIP",
                                                "detail": f"Verb '{verb}' not implemented"})

            except Exception as e:
                result.steps_failed += 1
                result.step_results.append({"verb": verb, "status": "FAIL", "detail": str(e)})

        browser.close()

    if result.steps_failed > 0:
        result.status = "FAIL"
    elif result.steps_blocked > 0:
        result.status = "BLOCKED"
    else:
        result.status = "PASS"

    _finalize(result, out_dir)
    return result


def run_blocked_flow(config: dict[str, Any], flow_def: dict[str, Any],
                     project: str, run_id: str, out_dir: Path) -> FlowResult:
    """Report a blocked flow without attempting execution."""
    result = _init_result(project, "mira_full_flow_blocked", run_id, out_dir)
    blockers = flow_def.get("blockers", [])
    result.blockers = blockers
    result.status = "BLOCKED"
    result.steps_total = 1
    result.steps_blocked = 1
    result.step_results.append({
        "verb": "blocked_reason",
        "status": "BLOCKED",
        "detail": "; ".join(blockers),
    })
    _finalize(result, out_dir)
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FLOW_RUNNERS = {
    "mira_route_readiness": run_route_readiness,
    "mira_selector_readiness": run_selector_readiness,
    "mira_onboarding_safe_dry_flow": run_onboarding_safe_dry,
    "mira_full_flow_blocked": run_blocked_flow,
}


def _init_result(project: str, flow_name: str, run_id: str, out_dir: Path) -> FlowResult:
    return FlowResult(
        run_id=run_id,
        project=project,
        flow_name=flow_name,
        started_at_utc=datetime.now(timezone.utc).isoformat(),
    )


def _finalize(result: FlowResult, out_dir: Path) -> None:
    result.ended_at_utc = datetime.now(timezone.utc).isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON
    json_path = out_dir / "flow_results.json"
    result.report_path = str(out_dir / "flow_report.md")

    # Merge if file exists (multiple flows in one run)
    all_results: list[dict[str, Any]] = []
    if json_path.exists():
        try:
            existing = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(existing, list):
                all_results = existing
            else:
                all_results = [existing]
        except Exception:
            pass

    all_results.append(result.to_dict())
    json_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")

    # Write markdown report
    md = _generate_report(result)
    report_path = out_dir / "flow_report.md"
    # Append if multiple flows
    mode = "a" if report_path.exists() else "w"
    with open(report_path, mode, encoding="utf-8") as f:
        f.write(md)
        f.write("\n\n---\n\n")

    print(f"[flow_qa] {result.flow_name}: {result.status}")
    print(f"  Steps: {result.steps_passed}P / {result.steps_failed}F / "
          f"{result.steps_blocked}B / {result.steps_skipped}S (total {result.steps_total})")
    if result.blockers:
        print(f"  Blockers: {'; '.join(result.blockers)}")
    print(f"  Report: {result.report_path}")


def _generate_report(result: FlowResult) -> str:
    lines = [
        f"# Flow QA Report: {result.flow_name}",
        f"",
        f"**Verdict:** {result.status}",
        f"**Run ID:** {result.run_id}",
        f"**Project:** {result.project}",
        f"**Started:** {result.started_at_utc}",
        f"**Ended:** {result.ended_at_utc}",
        f"",
        f"## Summary",
        f"- Steps total: {result.steps_total}",
        f"- Passed: {result.steps_passed}",
        f"- Failed: {result.steps_failed}",
        f"- Blocked: {result.steps_blocked}",
        f"- Skipped: {result.steps_skipped}",
        f"",
    ]

    if result.blockers:
        lines.append("## Blockers")
        for b in result.blockers:
            lines.append(f"- {b}")
        lines.append("")

    if result.step_results:
        lines.append("## Step Results")
        for sr in result.step_results:
            icon = {"PASS": "[OK]", "FAIL": "[FAIL]", "SKIP": "[SKIP]", "BLOCKED": "[BLOCKED]"}.get(sr.get("status", ""), "[?]")
            detail = sr.get("detail", "")
            sel = sr.get("selector", "")
            page = sr.get("page", "")
            path = sr.get("path", "")
            desc_parts = [sr.get("verb", "")]
            if sel:
                desc_parts.append(f"`{sel}`")
            if page:
                desc_parts.append(f"on {page}")
            if path:
                desc_parts.append(f"→ {path}")
            desc = " ".join(desc_parts)
            line = f"- {icon} {sr.get('status', '')} — {desc}"
            if detail:
                line += f" ({detail})"
            lines.append(line)
        lines.append("")

    if result.console_errors:
        lines.append("## Console Errors")
        for e in result.console_errors:
            lines.append(f"- {e}")
        lines.append("")

    if result.page_errors:
        lines.append("## Page Errors")
        for e in result.page_errors:
            lines.append(f"- {e}")
        lines.append("")

    if result.network_errors:
        lines.append("## Network Errors")
        for e in result.network_errors:
            lines.append(f"- {e}")
        lines.append("")

    if result.screenshots:
        lines.append("## Screenshots")
        for s in result.screenshots:
            lines.append(f"- {s}")
        lines.append("")

    lines.append("## Recommended Next Steps")
    if result.status == "BLOCKED":
        lines.append("- Resolve all blockers listed above before re-running.")
    elif result.status == "FAIL":
        lines.append("- Fix failing selectors or route errors.")
        lines.append("- Re-run this flow after fixes.")
    elif result.status == "WARN":
        lines.append("- Investigate console/page errors.")
        lines.append("- Add missing selectors for skipped pages.")
    else:
        lines.append("- All checks passed. Proceed to next phase.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Diagnose
# ---------------------------------------------------------------------------

def diagnose(project: str, config: dict[str, Any]) -> None:
    """Check prerequisites without running flows."""
    base_url = config.get("base_url", "http://localhost:3000")

    print(f"[flow_qa] Diagnosing prerequisites for project: {project}")
    print()

    pw_ok, pw_msg = check_playwright()
    print(f"  Playwright: {'[OK]' if pw_ok else '[MISSING]'} {pw_msg}")

    srv_ok, srv_msg = check_dev_server(base_url)
    print(f"  Dev server:  {'[OK]' if srv_ok else '[DOWN]'} {srv_msg}")

    flow_names = get_flow_names(config)
    print(f"  Flows defined: {len(flow_names)}")
    for name in flow_names:
        flow_def = config["flows"][name]
        status = flow_def.get("status", "runnable")
        runner = "[OK] runner available" if name in FLOW_RUNNERS else "[WARN] no runner"
        print(f"    - {name} [{status}] {runner}")

    print()
    if pw_ok and srv_ok:
        print("  [OK] All prerequisites met. Ready to run flows.")
    else:
        print("  [WARN] Some prerequisites not met. Flows may be skipped.")


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------

def dry_run(project: str, config: dict[str, Any]) -> None:
    """Show what would be done without executing."""
    print(f"[flow_qa] Dry run for project: {project}")
    print()
    for name, flow_def in config.get("flows", {}).items():
        status = flow_def.get("status", "runnable")
        desc = flow_def.get("description", "")
        safe = flow_def.get("safe", False)
        print(f"  Flow: {name}")
        print(f"    Status: {status}")
        print(f"    Description: {desc}")
        print(f"    Safe: {safe}")

        if status == "BLOCKED":
            blockers = flow_def.get("blockers", [])
            print(f"    Blockers: {len(blockers)}")
            for b in blockers:
                print(f"      - {b}")
        elif "routes" in flow_def:
            print(f"    Routes to visit: {len(flow_def['routes'])}")
        elif "pages" in flow_def:
            total_sel = sum(len(p.get("selectors", [])) for p in flow_def["pages"].values())
            print(f"    Pages to check: {len(flow_def['pages'])}")
            print(f"    Selectors to assert: {total_sel}")
        elif "steps" in flow_def:
            print(f"    Steps: {len(flow_def['steps'])}")

        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Flow QA for Project Autopilot")
    parser.add_argument("--project", required=True, help="Project ID (e.g. mira)")
    parser.add_argument("--list", action="store_true", help="List available flows")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--diagnose", action="store_true", help="Check prerequisites")
    parser.add_argument("--run", type=str, help="Run a specific flow by name")
    args = parser.parse_args()

    config = load_flows_config(args.project)

    if args.list:
        print(f"[flow_qa] Available flows for project '{args.project}':")
        for name in get_flow_names(config):
            flow_def = config["flows"][name]
            status = flow_def.get("status", "runnable")
            desc = flow_def.get("description", "")
            print(f"  - {name} [{status}]: {desc}")
        return

    if args.dry_run:
        dry_run(args.project, config)
        return

    if args.diagnose:
        diagnose(args.project, config)
        return

    if args.run:
        flow_name = args.run
        if flow_name not in config.get("flows", {}):
            print(f"[flow_qa] ERROR: Flow '{flow_name}' not found. Available: {get_flow_names(config)}")
            sys.exit(1)

        runner = FLOW_RUNNERS.get(flow_name)
        if not runner:
            print(f"[flow_qa] ERROR: No runner for flow '{flow_name}'")
            sys.exit(1)

        flow_def = config["flows"][flow_name]
        run_id = str(uuid.uuid4())[:8]
        out_dir = LOGS_BASE / args.project / "latest"

        # Clean latest dir for fresh run
        if out_dir.exists():
            for f in out_dir.glob("flow_results.json"):
                f.unlink()
            for f in out_dir.glob("flow_report.md"):
                f.unlink()

        result = runner(config, flow_def, args.project, run_id, out_dir)
        sys.exit(0 if result.status in ("PASS", "WARN", "BLOCKED", "SKIPPED") else 1)

    parser.print_help()


if __name__ == "__main__":
    main()
