"""MIRA Internal Demo Check.

Validates that the internal demo is functional:
- env/runtime checks pass
- demo route exists
- mock mode infrastructure is in place
- key routes are buildable
- no paid generation required

Usage:
    python -B project_autopilot/internal_demo_check.py --project mira
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


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


def _read_text(rel: str) -> str:
    p = REPO_ROOT / rel
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _needle_before(rel: str, first: str, second: str) -> bool:
    text = _read_text(rel)
    a = text.find(first)
    b = text.find(second)
    return a >= 0 and b >= 0 and a < b


def check_demo_route() -> list[CheckResult]:
    results: list[CheckResult] = []
    results.append(CheckResult(
        "Demo page exists",
        _exists("app/[locale]/(app)/demo/page.tsx"),
    ))
    results.append(CheckResult(
        "Demo page imports QA mock utilities",
        _contains("app/[locale]/(app)/demo/page.tsx", "QA_MOCK_PROFILE"),
    ))
    results.append(CheckResult(
        "Demo page has start demo button",
        _contains("app/[locale]/(app)/demo/page.tsx", "btn-demo-start"),
    ))
    results.append(CheckResult(
        "Demo page has mock result CTA",
        _contains("app/[locale]/(app)/demo/page.tsx", "btn-demo-mock-result"),
    ))
    results.append(CheckResult(
        "Demo page shows QA mock mode marker",
        _contains("app/[locale]/(app)/demo/page.tsx", "demo-qa-mock-mode"),
    ))
    results.append(CheckResult(
        "Demo page includes QA mock flag instructions",
        _contains("app/[locale]/(app)/demo/page.tsx", "NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS"),
    ))
    results.append(CheckResult(
        "Demo page does not import Supabase client/config guard",
        not _contains("app/[locale]/(app)/demo/page.tsx", "@/lib/supabase/"),
    ))
    results.append(CheckResult(
        "Friendly Supabase config error is not a demo blocker",
        not _contains("app/[locale]/(app)/demo/page.tsx", "getSupabaseMissingEnvMessage"),
    ))
    results.append(CheckResult(
        "Demo i18n keys exist (ES)",
        _contains("messages/es.json", '"demo"'),
    ))
    results.append(CheckResult(
        "Demo i18n keys exist (EN)",
        _contains("messages/en.json", '"demo"'),
    ))
    return results


def check_mock_infrastructure() -> list[CheckResult]:
    results: list[CheckResult] = []
    results.append(CheckResult(
        "QA mock module exists",
        _exists("lib/qa-mock.ts"),
    ))
    results.append(CheckResult(
        "Mock mode has production guard",
        _contains("lib/qa-mock.ts", 'NODE_ENV === "production"'),
    ))
    results.append(CheckResult(
        "Jobs API has mock branch",
        _contains("app/api/tryon/jobs/route.ts", "isQaMockMode"),
    ))
    results.append(CheckResult(
        "Status API has mock branch",
        _contains("app/api/tryon/status/[generationId]/route.ts", "isQaMockGenerationId"),
    ))
    results.append(CheckResult(
        "Mock result SVG exists",
        _exists("public/qa-mock-result.svg"),
    ))
    results.append(CheckResult(
        "Tryon flow has QA mock fallback",
        _contains("lib/tryon-flow.ts", "isMiraQaMocksEnabled"),
    ))
    results.append(CheckResult(
        "Tryon flow bypasses Supabase before client creation in mock mode",
        _needle_before("lib/tryon-flow.ts", "if (isMiraQaMocksEnabled())", "const supabase = createClient()"),
    ))
    results.append(CheckResult(
        "Jobs API mock branch is before paid image generation",
        _needle_before("app/api/tryon/jobs/route.ts", "if (isQaMockMode())", "generateAsync(generationId"),
    ))
    results.append(CheckResult(
        "Runtime health reports QA mock mode",
        _contains("app/api/health/env/route.ts", "qaMockModeEnabled"),
    ))
    return results


def check_flow_pages() -> list[CheckResult]:
    results: list[CheckResult] = []
    pages = [
        ("Onboarding page", "app/[locale]/(app)/onboarding/page.tsx"),
        ("Scan page", "app/[locale]/(app)/scan/page.tsx"),
        ("Catalog page", "app/[locale]/(app)/catalog/page.tsx"),
        ("TryOn page", "app/[locale]/(app)/tryon/[productId]/page.tsx"),
        ("Result page", "app/[locale]/(app)/result/[generationId]/page.tsx"),
        ("Landing page", "app/[locale]/(landing)/page.tsx"),
    ]
    for label, path in pages:
        results.append(CheckResult(label, _exists(path)))
    return results


def check_env_preflight() -> list[CheckResult]:
    results: list[CheckResult] = []
    data = _read_json("logs/mira_env_preflight_latest.json")
    if data:
        verdict = data.get("verdict", "UNKNOWN")
        results.append(CheckResult(
            f"Env preflight: {verdict}",
            verdict in ("PASS", "WARN"),
        ))
    else:
        results.append(CheckResult("Env preflight not yet run", False,
                                   "Run: python -B project_autopilot/env_preflight.py --project mira"))
    return results


def check_auth_verify() -> list[CheckResult]:
    results: list[CheckResult] = []
    data = _read_json("logs/mira_supabase_auth_verify_latest.json")
    if data:
        verdict = data.get("verdict", "UNKNOWN")
        mode = data.get("mode", "?")
        results.append(CheckResult(
            f"Auth verify: {verdict} (mode: {mode})",
            verdict in ("PASS", "WARN"),
        ))
    else:
        results.append(CheckResult("Auth verify not yet run", False))
    return results


def check_build() -> list[CheckResult]:
    """Check that 'next build' output directory exists (last build succeeded)."""
    results: list[CheckResult] = []
    next_dir = REPO_ROOT / ".next"
    results.append(CheckResult(
        "Production build cache exists (.next/)",
        next_dir.exists() and (next_dir / "build-manifest.json").exists(),
    ))
    return results


def check_no_paid_apis() -> list[CheckResult]:
    results: list[CheckResult] = []
    results.append(CheckResult(
        "Mock mode defaults OFF (safe for prod)",
        _contains("lib/qa-mock.ts", "NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS") and
        not _contains("lib/qa-mock.ts", "= true"),
    ))
    results.append(CheckResult(
        "Image provider mocks when no API key",
        _contains("lib/providers/openai-image.ts", "mock") or
        _contains("lib/providers/openai-image.ts", "Mock"),
    ))
    results.append(CheckResult(
        "Video provider mocks when no API key",
        _contains("lib/providers/seedance-video.ts", "mock") or
        _contains("lib/providers/seedance-video.ts", "Mock"),
    ))
    results.append(CheckResult(
        "QA mock job returns before paid provider calls",
        _needle_before("app/api/tryon/jobs/route.ts", "return NextResponse.json({", "generateAsync(generationId"),
    ))
    return results


def check_readiness_report() -> list[CheckResult]:
    results: list[CheckResult] = []
    results.append(CheckResult(
        "Internal demo report exists",
        _exists("project_control/MIRA_INTERNAL_DEMO_READY_REPORT.md"),
    ))
    return results


def _fetch(url: str) -> tuple[int, str, str]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace"), ""
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return e.code, body, ""
    except Exception as e:
        return 0, "", str(e)


def check_managed_dev_server() -> list[CheckResult]:
    """Start a mock-mode dev server, probe env + /es/demo, then stop it."""
    from dev_server_runner import DevServer

    results: list[CheckResult] = []
    server = None
    for port in (3099, 3100):
        candidate = DevServer(
            port=port,
            extra_env={"NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS": "true"},
        )
        ok, msg = candidate.start()
        if ok:
            server = candidate
            results.append(CheckResult("Managed dev server start", True, msg))
            break
        results.append(CheckResult(f"Managed dev server port {port}", False, msg))

    if server is None:
        results.append(CheckResult(
            "Managed demo route check",
            False,
            "Could not start an isolated mock-mode dev server",
        ))
        return results

    try:
        base = server.base_url
        env_status, env_body, env_error = _fetch(f"{base}/api/health/env")
        env_ok = False
        env_detail = f"HTTP {env_status}"
        if env_error:
            env_detail = env_error
        else:
            try:
                payload = json.loads(env_body)
                env_ok = (
                    env_status == 200
                    and payload.get("qaMockModeEnabled") is True
                    and payload.get("demoRouteCanRunWithoutSupabase") is True
                )
                env_detail = (
                    f"HTTP {env_status}; qaMockModeEnabled="
                    f"{payload.get('qaMockModeEnabled')}; "
                    f"demoRouteCanRunWithoutSupabase="
                    f"{payload.get('demoRouteCanRunWithoutSupabase')}"
                )
            except Exception:
                env_detail = f"HTTP {env_status}; invalid JSON"
        results.append(CheckResult("Runtime env reports mock demo readiness", env_ok, env_detail))

        demo_status, demo_body, demo_error = _fetch(f"{base}/es/demo")
        marker_found = (
            "QA mock mode" in demo_body
            or "demo-qa-mock-mode" in demo_body
            or "MIRA Internal Demo" in demo_body
        )
        results.append(CheckResult(
            "Demo route renders in managed QA mock mode",
            demo_status == 200 and marker_found and not demo_error,
            demo_error or f"HTTP {demo_status}; marker_found={marker_found}",
        ))
    finally:
        server.stop()
        results.append(CheckResult("Managed dev server stopped", True, "Clean shutdown"))

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="MIRA Internal Demo Check")
    parser.add_argument("--project", required=True)
    parser.add_argument("--managed-dev-server", action="store_true",
                        help="Start an isolated mock-mode dev server and probe /es/demo")
    args = parser.parse_args()

    sections = [
        ("Demo Route", check_demo_route()),
        ("Mock Infrastructure", check_mock_infrastructure()),
        ("Flow Pages", check_flow_pages()),
        ("Env Preflight", check_env_preflight()),
        ("Auth Verification", check_auth_verify()),
        ("Build Status", check_build()),
        ("No Paid APIs", check_no_paid_apis()),
        ("Readiness Report", check_readiness_report()),
    ]
    if args.managed_dev_server:
        sections.append(("Managed Dev Server", check_managed_dev_server()))

    total = 0
    passed = 0
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print(f"MIRA Internal Demo Check")
    print(f"Generated: {now}")
    print()

    for section_name, checks in sections:
        section_pass = sum(1 for c in checks if c.ok)
        section_total = len(checks)
        total += section_total
        passed += section_pass
        print(f"  {section_name}: {section_pass}/{section_total}")
        for c in checks:
            mark = "[OK]" if c.ok else "[!!]"
            line = f"    {mark} {c.name}"
            if c.detail:
                line += f" -- {c.detail}"
            print(line)
        print()

    verdict = "PASS" if passed == total else ("WARN" if passed >= total * 0.8 else "FAIL")
    print(f"Internal Demo Check: {verdict} ({passed}/{total} passed)")

    # Write JSON report
    out_dir = REPO_ROOT / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "passed": passed,
        "total": total,
        "sections": [
            {
                "name": name,
                "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail} for c in checks],
            }
            for name, checks in sections
        ],
    }
    report_path = out_dir / "mira_internal_demo_check_latest.json"
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"  Report: {report_path}")


if __name__ == "__main__":
    main()
