from __future__ import annotations

from dataclasses import dataclass

from config import ProjectConfig

LOW_COST_TASKS = {"summary", "log_parse", "classification", "status"}
LOW_COST_DEFAULT_TASKS = LOW_COST_TASKS | {"planning", "prompt_generation", "correction", "qa"}
STANDARD_TASKS = {"planning", "prompt_generation", "correction"}
PREMIUM_TASKS = {"architecture", "qa_critical", "visual_review", "repeated_failure"}
CRITICAL_TASKS = {"architecture", "qa_critical", "visual_review"}


@dataclass(frozen=True)
class ModelChoice:
    task_type: str
    model: str
    reason: str


def choose_model(project: ProjectConfig, task_type: str, failure_count: int = 0) -> ModelChoice:
    routing = project.model_routing
    mode = project.intensity_mode

    # Low-cost mode is intentionally conservative: normal supervision,
    # prompting, QA, and log-style work stay on the cheap model by default.
    # Premium escalation is reserved for explicitly critical repeated failures.
    if mode == "low_cost":
        if task_type == "repeated_failure":
            return ModelChoice(task_type, routing.premium_model, "low-cost repeated failure escalation")
        if failure_count >= 2 and task_type in CRITICAL_TASKS:
            return ModelChoice(task_type, routing.premium_model, "low-cost critical repeated failure escalation")
        if task_type in LOW_COST_DEFAULT_TASKS:
            return ModelChoice(task_type, routing.cheap_model, "low-cost default route")
        if task_type in PREMIUM_TASKS:
            return ModelChoice(task_type, routing.premium_model, "low-cost explicit premium task")
        return ModelChoice(task_type, routing.cheap_model, "low-cost fallback route")

    if mode == "high_intensity" and task_type in PREMIUM_TASKS:
        return ModelChoice(task_type, routing.premium_model, "high intensity premium task")
    if failure_count >= 2:
        return ModelChoice(task_type, routing.premium_model, "repeated failure escalation")
    if task_type in LOW_COST_TASKS:
        return ModelChoice(task_type, routing.cheap_model, "low-cost task")
    if task_type in PREMIUM_TASKS:
        return ModelChoice(task_type, routing.premium_model, "premium task")
    if task_type == "qa":
        return ModelChoice(task_type, routing.qa_model, "QA review")
    if task_type in STANDARD_TASKS:
        return ModelChoice(task_type, routing.standard_model, "standard planning task")

    return ModelChoice(task_type, routing.standard_model, "default standard route")
