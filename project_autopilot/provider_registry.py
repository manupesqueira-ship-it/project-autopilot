from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import load_project_config
from env_loader import load_env
from providers.registry import discover_providers

load_env()


def _write_reports(project_id: str, payload: dict) -> tuple[Path, Path]:
    logs = Path("logs")
    logs.mkdir(parents=True, exist_ok=True)
    json_path = logs / f"{project_id}_provider_registry_latest.json"
    md_path = logs / f"{project_id}_provider_registry_latest.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Project Autopilot Provider Registry",
        "",
        f"Generated: {payload['generated_at_utc']}",
        f"Project: {project_id}",
        "",
        "## Providers",
        "",
    ]
    for item in payload["providers"]:
        configured = "yes" if item["configured"] else "no"
        lines.extend([
            f"### {item['display_name']} (`{item['provider_id']}`)",
            f"- Type: {item['provider_type']}",
            f"- Configured: {configured}",
            f"- Status: {item['current_status']}",
            f"- Supported modes: {', '.join(item['supported_execution_modes']) or 'none'}",
            f"- Capabilities: {', '.join(item['capabilities']) or 'none'}",
            f"- Missing env vars: {', '.join(item['missing_env_vars']) or 'none'}",
            f"- Risks: {', '.join(item['risks']) or 'none'}",
            f"- Notes: {'; '.join(item['notes']) or 'none'}",
            f"- Metadata: {json.dumps(item.get('metadata', {}), sort_keys=True)}",
            "",
        ])
    lines.extend([
        "## Recommended Next Provider Action",
        "",
        payload["recommended_next_provider_action"],
        "",
        "Safety: no provider was executed, no API was called, and no secret values were printed.",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def build_registry(project_id: str) -> dict:
    project = load_project_config(project_id)
    providers = [p.to_dict() for p in discover_providers(project)]
    configured = [p for p in providers if p["configured"]]
    missing = sorted({name for p in providers for name in p["missing_env_vars"]})
    recommendation = (
        "Use Codex as primary builder with manual handoff and post-builder QA."
        if any(p["provider_id"] == "codex" and p["configured"] for p in providers)
        else "Configure a primary builder before attempting autonomous work."
    )
    if missing:
        recommendation += f" Missing optional/future provider env vars: {', '.join(missing)}."
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        "project_name": project.project_name,
        "provider_count": len(providers),
        "configured_provider_count": len(configured),
        "providers": providers,
        "recommended_next_provider_action": recommendation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot provider registry")
    parser.add_argument("--project", default="mira")
    args = parser.parse_args()

    payload = build_registry(args.project)
    md_path, json_path = _write_reports(args.project, payload)
    print(f"Provider Registry: {payload['configured_provider_count']}/{payload['provider_count']} configured")
    for item in payload["providers"]:
        configured = "yes" if item["configured"] else "no"
        missing = ", ".join(item["missing_env_vars"]) or "none"
        modes = ", ".join(item["supported_execution_modes"]) or "none"
        print(f"  - {item['provider_id']}: configured={configured}; status={item['current_status']}; modes={modes}; missing_env={missing}")
    print(f"Recommended next action: {payload['recommended_next_provider_action']}")
    print(f"Report: {md_path}")
    print(f"JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
