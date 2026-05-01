from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import ProjectConfig, load_project_config


RUBRIC = [
    "Visual hierarchy",
    "Spacing rhythm",
    "Typography consistency",
    "Color discipline",
    "Contrast/accessibility",
    "CTA clarity",
    "Mobile responsiveness",
    "Desktop polish",
    "Interaction feedback",
    "Loading/error states",
    "Originality/innovation",
    "Premium feel",
    "Brand coherence",
    "Copywriting clarity",
    "Flow friction",
    "Emotional pull",
    "Novelty without gimmicks",
    "Information density",
    "Trust and credibility",
    "Product-market tone fit",
]

PENALTIES = {
    "generic_saas": [r"hero.*gradient", r"card.*gradient", r"template", r"lorem ipsum"],
    "cheap_gradient_cards": [r"gradient", r"from-purple", r"to-blue", r"blur-3xl"],
    "random_colors": [r"#[0-9a-fA-F]{6}"],
    "unclear_cta": [r"click here", r"submit", r"continue"],
    "too_much_text": [r"<p[\s>]"],
}

REWARDS = {
    "clear_hierarchy": [r"\bdisplay\b", r"\blabel-mono\b", r"\btracking-"],
    "interaction_feedback": [r"hover:", r"focus-visible", r"aria-", r"role=\"alert\""],
    "responsive": [r"\bmd:", r"\blg:", r"grid", r"flex"],
    "premium_identity": [r"brand", r"editorial", r"premium", r"visual"],
    "state_polish": [r"loading", r"error", r"empty", r"disabled"],
}


@dataclass
class DesignReview:
    verdict: str
    overall_design_score: int
    innovation_score: int
    premium_score: int
    usability_score: int
    accessibility_score: int
    copy_score: int
    reasons: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    required_actions: list[str] = field(default_factory=list)
    rubric_notes: dict[str, str] = field(default_factory=dict)
    inspected_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _count_matches(text: str, patterns: list[str]) -> int:
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def _sample_app_files(project: ProjectConfig) -> tuple[str, list[str]]:
    app_root = project.repo_path / "app"
    component_root = project.repo_path / "components"
    paths = list(app_root.rglob("*.tsx"))[:80] + list(component_root.rglob("*.tsx"))[:80]
    inspected: list[str] = []
    chunks: list[str] = []
    for path in paths:
        inspected.append(str(path.relative_to(project.repo_path)))
        chunks.append(_read(path)[:12000])
    return "\n".join(chunks), inspected


def run_design_review(project: ProjectConfig) -> DesignReview:
    text, inspected = _sample_app_files(project)
    control = project.project_control_path
    logs = project.repo_path / project.logs_dir
    screenshots = list((project.repo_path / project.screenshots_dir).rglob("*.png")) if (project.repo_path / project.screenshots_dir).exists() else []
    visual_reports = [
        logs / f"{project.project_id}_visual_qa_latest.md",
        logs / "flow_qa" / project.project_id / "latest" / "flow_report.md",
    ]

    docs = {
        "DESIGN_DIRECTOR_STANDARD.md": (control / "DESIGN_DIRECTOR_STANDARD.md").exists(),
        "DESIGN_RUBRIC.md": (control / "DESIGN_RUBRIC.md").exists(),
        "INNOVATION_STANDARD.md": (control / "INNOVATION_STANDARD.md").exists(),
        "COPYWRITING_STANDARD.md": (control / "COPYWRITING_STANDARD.md").exists(),
        "WORLD_CLASS_STANDARD.md": (control / "WORLD_CLASS_STANDARD.md").exists(),
    }

    score = 72
    reasons: list[str] = []
    missing: list[str] = []
    required: list[str] = []

    for name, exists in docs.items():
        if exists:
            score += 2
        else:
            missing.append(name)
            score -= 4

    if screenshots:
        score += 4
        reasons.append(f"Screenshot evidence found: {len(screenshots)} image(s).")
    else:
        missing.append("fresh screenshots for current UI state")
        required.append("Run Browser QA/visual QA screenshots or request human visual review before approving UI work.")
        score -= 10

    if any(path.exists() for path in visual_reports):
        score += 4
        reasons.append("Existing Flow QA or visual QA artifacts are available.")
    else:
        missing.append("visual/flow QA artifacts")
        score -= 6

    for label, patterns in REWARDS.items():
        count = _count_matches(text, patterns)
        if count:
            reasons.append(f"Reward signal: {label} ({count} match(es)).")
            score += min(5, count // 12 + 1)

    penalty_hits = 0
    for label, patterns in PENALTIES.items():
        count = _count_matches(text, patterns)
        if count:
            penalty_hits += count
            reasons.append(f"Penalty signal: {label} ({count} match(es)); requires review, not automatic failure.")
            score -= min(8, count // 20 + 2)

    score = max(0, min(100, score))
    innovation = max(0, min(100, score - (10 if not screenshots else 4)))
    premium = max(0, min(100, score - min(8, penalty_hits // 20)))
    usability = max(0, min(100, score + 4 if "role=\"alert\"" in text else score))
    accessibility = max(0, min(100, 70 + min(18, _count_matches(text, [r"aria-", r"focus-visible", r"role="]))))
    copy_score = max(0, min(100, score - 2))

    if not screenshots:
        verdict = "DESIGN_REQUIRES_HUMAN_VISUAL_REVIEW"
    elif score >= 82 and premium >= 78 and usability >= 78:
        verdict = "DESIGN_PASS"
    elif score >= 68:
        verdict = "DESIGN_WARN"
    else:
        verdict = "DESIGN_FAIL"
        required.append("Raise visual quality before accepting this UI/design work.")

    rubric_notes = {item: "Static heuristic reviewed; screenshot/human review still required for final judgment." for item in RUBRIC}
    if not text:
        verdict = "DESIGN_REQUIRES_HUMAN_VISUAL_REVIEW"
        missing.append("app/components source text")
        required.append("Run in a real project with UI source files or provide screenshots.")

    return DesignReview(
        verdict=verdict,
        overall_design_score=score,
        innovation_score=innovation,
        premium_score=premium,
        usability_score=usability,
        accessibility_score=accessibility,
        copy_score=copy_score,
        reasons=reasons[:30],
        missing_evidence=sorted(set(missing)),
        required_actions=sorted(set(required)),
        rubric_notes=rubric_notes,
        inspected_paths=inspected[:120],
    )


def write_reports(project: ProjectConfig, review: DesignReview) -> tuple[Path, Path]:
    logs = project.repo_path / project.logs_dir
    logs.mkdir(parents=True, exist_ok=True)
    md_path = logs / f"{project.project_id}_design_director_latest.md"
    json_path = logs / f"{project.project_id}_design_director_latest.json"
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": project.project_id,
        **review.to_dict(),
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Design Director Review",
        "",
        f"Project: {project.project_name}",
        f"Verdict: {review.verdict}",
        "",
        "## Scores",
        f"- Overall design: {review.overall_design_score}/100",
        f"- Innovation: {review.innovation_score}/100",
        f"- Premium: {review.premium_score}/100",
        f"- Usability: {review.usability_score}/100",
        f"- Accessibility: {review.accessibility_score}/100",
        f"- Copy: {review.copy_score}/100",
        "",
        "## Strict Review Notes",
    ]
    lines.extend(f"- {reason}" for reason in review.reasons or ["No strong heuristic signals found."])
    lines.extend(["", "## Missing Evidence"])
    lines.extend(f"- {item}" for item in review.missing_evidence or ["None"])
    lines.extend(["", "## Required Actions"])
    lines.extend(f"- {item}" for item in review.required_actions or ["No immediate action for non-UI work."])
    lines.extend([
        "",
        "## Honesty Note",
        "Static heuristics cannot fully judge taste, emotional pull, or premium feel. Fresh screenshots and human visual review remain required for major UI/design approval.",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot Design Director")
    parser.add_argument("--project", default="mira")
    args = parser.parse_args()

    project = load_project_config(args.project)
    review = run_design_review(project)
    md_path, json_path = write_reports(project, review)
    print(f"Design Director: {review.verdict}")
    print(f"  Overall: {review.overall_design_score}/100")
    print(f"  Innovation: {review.innovation_score}/100")
    print(f"  Premium: {review.premium_score}/100")
    print(f"  Usability: {review.usability_score}/100")
    print(f"  Accessibility: {review.accessibility_score}/100")
    print(f"  Copy: {review.copy_score}/100")
    print(f"  Report: {md_path}")
    print(f"  JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
