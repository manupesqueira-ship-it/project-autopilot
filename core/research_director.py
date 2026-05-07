from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import ProjectConfig, load_project_config


VALID_MODES = {
    "quick_check": "5-15 min",
    "standard": "30-60 min",
    "deep_research": "90+ min",
}

TRIGGERS = {
    "new API/provider choice": [r"\bapi\b", r"\bprovider\b", r"\bvendor\b"],
    "security-sensitive decision": [r"\bsecurity\b", r"\brls\b", r"\bpolicy\b", r"\bauth\b"],
    "paid API choice": [r"\bpaid\b", r"\bbudget\b", r"\bpricing\b", r"\bquota\b"],
    "legal/privacy issue": [r"\blegal\b", r"\bprivacy\b", r"\bretention\b", r"\bcompliance\b"],
    "UX benchmark needed": [r"\bux\b", r"\bbenchmark\b", r"\bconversion\b"],
    "unknown technical architecture": [r"\barchitecture\b", r"\bunknown\b", r"\bstrategy\b"],
    "cloud/VPS/deployment architecture": [r"\bcloud\b", r"\bvps\b", r"\bdeploy\b", r"\bgithub\b"],
    "AI model/vendor comparison": [r"\bmodel\b", r"\bclaude\b", r"\bopenai\b", r"\banthropic\b"],
    "image/video generation provider selection": [r"\bimage generation\b", r"\bvideo generation\b", r"\bseedance\b"],
}


@dataclass
class ResearchRequest:
    research_id: str
    timestamp_utc: str
    project_id: str
    research_question: str
    mode: str
    why_research_is_needed: list[str] = field(default_factory=list)
    decision_blocked: str = ""
    suggested_source_types: list[str] = field(default_factory=list)
    exact_research_prompt: str = ""
    expected_output_format: str = ""
    acceptance_criteria: list[str] = field(default_factory=list)
    urgency: str = "normal"
    cost_sensitivity: str = "low_cost_preferred"
    related_project_files: list[str] = field(default_factory=list)
    follow_up_decision_owner: str = "human"
    status: str = "requested"
    requires_human_approval: bool = False

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def _requests_dir(project: ProjectConfig) -> Path:
    return project.repo_path / project.logs_dir / "research" / project.project_id / "requests"


def _index_path(project: ProjectConfig) -> Path:
    return project.repo_path / project.logs_dir / "research" / f"{project.project_id}_research_director_index.jsonl"


def classify_research_need(text: str) -> tuple[str, list[str]]:
    hits: list[str] = []
    for label, patterns in TRIGGERS.items():
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns):
            hits.append(label)
    if any("security" in h or "privacy" in h or "paid" in h for h in hits):
        return "DECISION_BLOCKED_RESEARCH_REQUIRED", hits
    if hits:
        return "RESEARCH_REQUIRED" if len(hits) >= 2 else "RESEARCH_RECOMMENDED", hits
    return "NO_RESEARCH_REQUIRED", []


def create_request(project: ProjectConfig, question: str, mode: str) -> ResearchRequest:
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid research mode '{mode}'. Valid: {', '.join(VALID_MODES)}")
    status, reasons = classify_research_need(question)
    now = datetime.now(timezone.utc)
    rid = f"{project.project_id}_{now.strftime('%Y%m%d_%H%M%S')}"
    requires_approval = mode == "deep_research"
    return ResearchRequest(
        research_id=rid,
        timestamp_utc=now.isoformat(),
        project_id=project.project_id,
        research_question=question,
        mode=mode,
        why_research_is_needed=reasons or ["Human requested research planning."],
        decision_blocked=status if status != "NO_RESEARCH_REQUIRED" else "",
        suggested_source_types=[
            "official documentation",
            "primary vendor pricing/docs",
            "security/compliance references",
            "credible implementation case studies",
        ],
        exact_research_prompt=(
            "Research this decision for Project Autopilot. Use current primary sources, "
            "cite links, compare options, identify risks/costs, and recommend a safe next step: "
            f"{question}"
        ),
        expected_output_format=(
            "Decision summary, options compared, citations, risks, cost impact, "
            "recommended path, and unresolved questions."
        ),
        acceptance_criteria=[
            "Uses primary/current sources.",
            "Separates facts from recommendations.",
            "Calls out cost, security, privacy, and implementation risks.",
            "Ends with a concrete decision or blocker.",
        ],
        urgency="high" if status.startswith("DECISION_BLOCKED") else "normal",
        related_project_files=[
            "project_control/AUTOPILOT_V2_SPEC.md",
            "project_control/AUTONOMY_PROTOCOL.md",
            "project_control/AGENT_RULES.md",
        ],
        status="requested",
        requires_human_approval=requires_approval,
    )


def save_request(project: ProjectConfig, req: ResearchRequest) -> Path:
    out_dir = _requests_dir(project)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{req.research_id}.json"
    payload = req.to_dict()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    index = _index_path(project)
    index.parent.mkdir(parents=True, exist_ok=True)
    with index.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")
    md_path = out_dir / f"{req.research_id}.md"
    lines = [
        "# Research Request",
        "",
        f"Research ID: {req.research_id}",
        f"Question: {req.research_question}",
        f"Mode: {req.mode} ({VALID_MODES[req.mode]})",
        f"Status: {req.status}",
        f"Requires human approval: {'yes' if req.requires_human_approval else 'no'}",
        "",
        "## Why Research Is Needed",
        *[f"- {item}" for item in req.why_research_is_needed],
        "",
        "## Exact Research Prompt",
        req.exact_research_prompt,
        "",
        "## Expected Output",
        req.expected_output_format,
        "",
        "## Acceptance Criteria",
        *[f"- {item}" for item in req.acceptance_criteria],
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def read_requests(project: ProjectConfig) -> list[dict[str, Any]]:
    index = _index_path(project)
    if not index.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in index.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def status_payload(project: ProjectConfig) -> dict[str, Any]:
    rows = read_requests(project)
    latest = rows[-1] if rows else None
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        "status": "NO_RESEARCH_REQUIRED" if not rows else "RESEARCH_RECOMMENDED",
        "total_requests": len(rows),
        "pending_deep_research_approval": sum(1 for r in rows if r.get("mode") == "deep_research" and r.get("status") == "requested"),
        "completed_requests": sum(1 for r in rows if r.get("status") == "completed"),
        "latest_request": latest,
    }


def write_status(project: ProjectConfig, payload: dict[str, Any]) -> tuple[Path, Path]:
    logs = project.repo_path / project.logs_dir
    logs.mkdir(parents=True, exist_ok=True)
    json_path = logs / f"{project.project_id}_research_director_latest.json"
    md_path = logs / f"{project.project_id}_research_director_latest.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    latest = payload.get("latest_request") or {}
    lines = [
        "# Research Director Status",
        "",
        f"Status: {payload['status']}",
        f"Total requests: {payload['total_requests']}",
        f"Deep research pending approval: {payload['pending_deep_research_approval']}",
        f"Completed: {payload['completed_requests']}",
        "",
        "## Latest Request",
        f"- ID: {latest.get('research_id', 'none')}",
        f"- Question: {latest.get('research_question', 'none')}",
        f"- Mode: {latest.get('mode', 'none')}",
        f"- Requires approval: {latest.get('requires_human_approval', False)}",
        "",
        "No research is executed automatically by this module.",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot Research Director")
    parser.add_argument("--project", default="mira")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--request", help="Create a research request")
    parser.add_argument("--mode", default="quick_check", choices=sorted(VALID_MODES))
    args = parser.parse_args()

    project = load_project_config(args.project)
    if args.request:
        req = create_request(project, args.request, args.mode)
        path = save_request(project, req)
        payload = status_payload(project)
        write_status(project, payload)
        print(f"Research request created: {req.research_id}")
        print(f"  Mode: {req.mode} ({VALID_MODES[req.mode]})")
        print(f"  Requires human approval: {'yes' if req.requires_human_approval else 'no'}")
        print(f"  Decision status: {req.decision_blocked or 'NO_RESEARCH_REQUIRED'}")
        print(f"  Request: {path}")
        if req.requires_human_approval:
            print("  Human approval is required before deep research runs.")
        return 0

    payload = status_payload(project)
    md_path, json_path = write_status(project, payload)
    if args.list:
        print(f"Research requests: {payload['total_requests']}")
        for row in read_requests(project)[-20:]:
            print(f"  - {row.get('research_id')}: {row.get('mode')} {row.get('status')} - {row.get('research_question')}")
    else:
        print(f"Research Director: {payload['status']}")
        print(f"  Total requests: {payload['total_requests']}")
        print(f"  Deep research pending approval: {payload['pending_deep_research_approval']}")
        print(f"  Completed: {payload['completed_requests']}")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
