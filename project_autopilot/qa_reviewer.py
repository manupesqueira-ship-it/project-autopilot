from __future__ import annotations

from typing import Any

from openai_supervisor import OpenAISupervisor


def review_with_openai(supervisor: OpenAISupervisor, task_plan: str, evidence: dict[str, Any]) -> str:
    return supervisor.qa_review(task_plan, evidence)


def generate_correction_prompt(
    supervisor: OpenAISupervisor,
    task_plan: str,
    qa_review: str,
    evidence: dict[str, Any],
) -> str:
    return supervisor.correction_prompt(task_plan, qa_review, evidence)

