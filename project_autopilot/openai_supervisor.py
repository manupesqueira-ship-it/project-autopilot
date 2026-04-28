from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

from config import ProjectConfig
from cost_controller import CostController
from model_router import choose_model


class MissingOpenAICredentials(RuntimeError):
    pass


class BudgetBlocked(RuntimeError):
    pass


class OpenAISupervisor:
    def __init__(self, project: ProjectConfig, cost_controller: CostController, dry_run: bool = False):
        self.project = project
        self.cost_controller = cost_controller
        self.dry_run = dry_run

    def _call(self, task_type: str, instructions: str, user_content: str, failure_count: int = 0) -> str:
        choice = choose_model(self.project, task_type, failure_count=failure_count)
        if self.dry_run:
            return f"DRY RUN: OpenAI call skipped. Would use {choice.model} for {task_type} ({choice.reason})."

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise MissingOpenAICredentials("OPENAI_API_KEY is missing")

        budget = self.cost_controller.record_model_estimate(choice.model, len(instructions) + len(user_content))
        if not budget.allowed:
            raise BudgetBlocked(budget.reason)

        payload = {
            "model": choice.model,
            "input": [
                {"role": "system", "content": instructions},
                {"role": "user", "content": user_content},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=90) as response:  # pragma: no cover - network dependent
            raw = json.loads(response.read().decode("utf-8"))
        if "output_text" in raw:
            return raw["output_text"]
        parts: list[str] = []
        for item in raw.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"}:
                    parts.append(content.get("text", ""))
        return "\n".join(parts).strip()

    def plan_next_task(self, control_docs: dict[str, str], evidence: dict[str, Any]) -> str:
        instructions = (
            "You are Project Autopilot's supervisor. Use only the loaded project config and "
            "project_control context. Choose a safe next task, avoid hardcoded assumptions, "
            "honor cost policy and autonomy mode, and return concise acceptance criteria."
        )
        user_content = json.dumps(
            {
                "project": self.project.project_name,
                "control_docs": control_docs,
                "evidence": evidence,
                "cost": self.cost_controller.snapshot(),
            },
            indent=2,
        )[:60000]
        return self._call("planning", instructions, user_content)

    def qa_review(self, task_plan: str, evidence: dict[str, Any]) -> str:
        instructions = (
            "You are Project Autopilot's QA reviewer. Review the evidence against the project's "
            "QUALITY_BAR, AGENT_RULES, AUTONOMY_PROTOCOL, and COST_POLICY. Return pass/fail, "
            "findings, risk level, and required corrections."
        )
        user_content = json.dumps({"task_plan": task_plan, "evidence": evidence}, indent=2)[:60000]
        return self._call("qa", instructions, user_content)

    def correction_prompt(self, task_plan: str, qa_review: str, evidence: dict[str, Any]) -> str:
        instructions = (
            "Generate a precise correction prompt for the configured builder. Keep it scoped, "
            "avoid destructive commands, avoid secrets, avoid deploys, and respect project control files."
        )
        user_content = json.dumps(
            {"task_plan": task_plan, "qa_review": qa_review, "evidence": evidence}, indent=2
        )[:60000]
        return self._call("correction", instructions, user_content)

