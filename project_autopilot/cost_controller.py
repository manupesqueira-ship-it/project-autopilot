from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import ProjectConfig


@dataclass
class CostDecision:
    allowed: bool
    reason: str


@dataclass
class CostState:
    estimated_model_usage_usd: float = 0.0
    paid_api_calls: int = 0
    cycle_spend_usd: float = 0.0
    daily_spend_usd: float = 0.0
    monthly_spend_usd: float = 0.0
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CostController:
    def __init__(self, project: ProjectConfig):
        self.project = project
        self.path = project.repo_path / project.logs_dir / f"{project.project_id}_cost_state.json"
        self.state = self._load()

    def _load(self) -> CostState:
        if not self.path.exists():
            return CostState()
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return CostState(**raw)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.state.last_updated = datetime.now(timezone.utc).isoformat()
        self.path.write_text(json.dumps(self.state.__dict__, indent=2, sort_keys=True), encoding="utf-8")

    def can_spend(self, estimated_usd: float) -> CostDecision:
        if estimated_usd <= 0:
            return CostDecision(True, "no cost requested")
        if self.state.cycle_spend_usd + estimated_usd > self.project.per_cycle_budget_usd:
            return CostDecision(False, "per-cycle budget would be exceeded")
        if self.state.daily_spend_usd + estimated_usd > self.project.daily_budget_usd:
            return CostDecision(False, "daily budget would be exceeded")
        if self.state.monthly_spend_usd + estimated_usd > self.project.monthly_budget_usd:
            return CostDecision(False, "monthly budget would be exceeded")
        return CostDecision(True, "within budget")

    def record_model_estimate(self, model: str, input_chars: int, output_chars: int = 0) -> CostDecision:
        # Conservative rough estimate for routing decisions, not billing truth.
        estimated_tokens = max(1, (input_chars + output_chars) // 4)
        estimated_usd = estimated_tokens * self._rate_per_token(model)
        decision = self.can_spend(estimated_usd)
        if decision.allowed:
            self.state.estimated_model_usage_usd += estimated_usd
            self.state.cycle_spend_usd += estimated_usd
            self.state.daily_spend_usd += estimated_usd
            self.state.monthly_spend_usd += estimated_usd
            self.save()
        return decision

    def allow_paid_api(self, api_kind: str) -> CostDecision:
        if self.project.paid_api_mode != "enabled_with_budget":
            return CostDecision(False, "paid API mode is disabled")
        if api_kind == "image_generation" and not self.project.allow_paid_image_generation:
            return CostDecision(False, "paid image generation is disabled")
        if api_kind == "video_generation" and not self.project.allow_paid_video_generation:
            return CostDecision(False, "paid video generation is disabled")
        self.state.paid_api_calls += 1
        self.save()
        return CostDecision(True, "paid API call allowed")

    @staticmethod
    def _rate_per_token(model: str) -> float:
        lowered = model.lower()
        if "mini" in lowered or "cheap" in lowered:
            return 0.0000002
        if "5.5" in lowered or "premium" in lowered:
            return 0.000003
        return 0.000001

    def snapshot(self) -> dict[str, Any]:
        return {
            "estimated_model_usage_usd": round(self.state.estimated_model_usage_usd, 6),
            "paid_api_calls": self.state.paid_api_calls,
            "cycle_spend_usd": round(self.state.cycle_spend_usd, 6),
            "daily_spend_usd": round(self.state.daily_spend_usd, 6),
            "monthly_spend_usd": round(self.state.monthly_spend_usd, 6),
            "daily_budget_usd": self.project.daily_budget_usd,
            "per_cycle_budget_usd": self.project.per_cycle_budget_usd,
            "monthly_budget_usd": self.project.monthly_budget_usd,
            "paid_api_mode": self.project.paid_api_mode,
            "paid_mode_disabled": self.project.paid_api_mode != "enabled",
            "allow_paid_image_generation": self.project.allow_paid_image_generation,
            "allow_paid_video_generation": self.project.allow_paid_video_generation,
        }

    def report(self) -> str:
        """Human-readable cost status report."""
        snap = self.snapshot()
        paid_status = "DISABLED" if snap["paid_mode_disabled"] else "ENABLED"
        return (
            f"Cost Controller Report\n"
            f"  Daily budget:       ${snap['daily_budget_usd']:.2f}  (spent: ${snap['daily_spend_usd']:.4f})\n"
            f"  Per-cycle budget:   ${snap['per_cycle_budget_usd']:.2f}  (spent: ${snap['cycle_spend_usd']:.4f})\n"
            f"  Monthly budget:     ${snap['monthly_budget_usd']:.2f}  (spent: ${snap['monthly_spend_usd']:.4f})\n"
            f"  Est. model usage:   ${snap['estimated_model_usage_usd']:.4f}\n"
            f"  Paid API calls:     {snap['paid_api_calls']}\n"
            f"  Paid API mode:      {paid_status} ({snap['paid_api_mode']})\n"
            f"  Note: Local planning (--local-plan, --dry-run) is always free."
        )
