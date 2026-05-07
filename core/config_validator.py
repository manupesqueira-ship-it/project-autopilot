from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from config import ModelRouting, ProjectConfig, RetryPolicy

VALID_AUTONOMY_MODES = {"autonomous_guarded", "supervised", "dry_run"}
VALID_INTENSITY_MODES = {"low_cost", "normal", "high_intensity"}
VALID_PAID_API_MODES = {"disabled_by_default", "approval_required", "enabled_with_budget"}

DANGEROUS_COMMAND_PATTERNS = {
    "DANGEROUS_GIT_RESET": r"\bgit\s+reset\b",
    "DANGEROUS_GIT_CLEAN": r"\bgit\s+clean\b",
    "DANGEROUS_GIT_PUSH": r"\bgit\s+push\b",
    "DANGEROUS_DEPLOY": r"\bdeploy\b",
    "DANGEROUS_VERCEL_PROD": r"\bvercel\s+--prod\b",
    "DANGEROUS_RM": r"(^|\s)rm(\s|$)",
    "DANGEROUS_DEL": r"(^|\s)del(\s|$)",
    "DANGEROUS_RMDIR": r"(^|\s)rmdir(\s|$)",
    "DANGEROUS_REMOVE_ITEM": r"\bRemove-Item\b",
}


@dataclass(frozen=True)
class ConfigIssue:
    severity: str
    code: str
    message: str
    recommendation: str


def issue(severity: str, code: str, message: str, recommendation: str) -> ConfigIssue:
    return ConfigIssue(severity=severity, code=code, message=message, recommendation=recommendation)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _check_required(project: ProjectConfig, field_name: str) -> ConfigIssue:
    value = getattr(project, field_name, None)
    if _present(value):
        return issue("pass", f"{field_name.upper()}_PRESENT", f"{field_name} present", "No action needed.")
    return issue("fail", f"{field_name.upper()}_MISSING", f"{field_name} is missing", "Add it to the project YAML.")


def _check_non_negative_number(project: ProjectConfig, field_name: str) -> ConfigIssue:
    value = getattr(project, field_name, None)
    if isinstance(value, (int, float)) and value >= 0:
        return issue("pass", f"{field_name.upper()}_VALID", f"{field_name} is non-negative", "No action needed.")
    return issue("fail", f"{field_name.upper()}_INVALID", f"{field_name} must be numeric and non-negative", "Set a non-negative numeric value.")


def _check_min_int(project: ProjectConfig, field_name: str, minimum: int) -> ConfigIssue:
    value = getattr(project, field_name, None)
    if isinstance(value, int) and value >= minimum:
        return issue("pass", f"{field_name.upper()}_VALID", f"{field_name} >= {minimum}", "No action needed.")
    return issue("fail", f"{field_name.upper()}_INVALID", f"{field_name} must be an integer >= {minimum}", "Update the project YAML.")


def _valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _check_command_safety(field_name: str, command: str) -> list[ConfigIssue]:
    if not command:
        return [issue("warn", f"{field_name.upper()}_MISSING", f"{field_name} is empty", "Configure the command if this project needs it.")]

    issues: list[ConfigIssue] = []
    for code, pattern in DANGEROUS_COMMAND_PATTERNS.items():
        if re.search(pattern, command, flags=re.IGNORECASE):
            issues.append(
                issue(
                    "fail",
                    code,
                    f"{field_name} contains a dangerous command: {command}",
                    "Remove destructive, deploy, or git-mutating commands from project config.",
                )
            )
    if not issues:
        issues.append(issue("pass", f"{field_name.upper()}_SAFE", f"{field_name} appears safe", "No action needed."))
    return issues


def validate_model_routing(routing: ModelRouting) -> list[ConfigIssue]:
    checks = []
    for field_name in ["cheap_model", "standard_model", "premium_model", "qa_model"]:
        value = getattr(routing, field_name, "")
        checks.append(
            issue(
                "pass" if _present(value) else "fail",
                f"MODEL_ROUTING_{field_name.upper()}",
                f"model_routing.{field_name} {'present' if _present(value) else 'missing'}",
                "No action needed." if _present(value) else "Add the model route to project YAML.",
            )
        )
    return checks


def validate_project_config(project: ProjectConfig, config_path: Path | None = None) -> list[ConfigIssue]:
    issues: list[ConfigIssue] = []

    if config_path:
        issues.append(
            issue(
                "pass" if config_path.exists() else "fail",
                "PROJECT_YAML_EXISTS",
                f"Project YAML {'exists' if config_path.exists() else 'is missing'}: {config_path}",
                "No action needed." if config_path.exists() else "Create the project YAML file.",
            )
        )

    for field_name in [
        "project_id",
        "project_name",
        "repo_path",
        "project_control_path",
        "framework",
        "package_manager",
        "build_command",
        "typecheck_command",
        "lint_command",
    ]:
        issues.append(_check_required(project, field_name))

    issues.append(
        issue(
            "pass" if project.repo_path.exists() else "fail",
            "REPO_PATH_EXISTS",
            f"repo_path {'exists' if project.repo_path.exists() else 'does not exist'}: {project.repo_path}",
            "No action needed." if project.repo_path.exists() else "Fix repo_path in project YAML.",
        )
    )
    issues.append(
        issue(
            "pass" if project.project_control_path.exists() else "fail",
            "PROJECT_CONTROL_PATH_EXISTS",
            f"project_control_path {'exists' if project.project_control_path.exists() else 'does not exist'}: {project.project_control_path}",
            "No action needed." if project.project_control_path.exists() else "Create the project_control directory or fix config.",
        )
    )

    issues.append(
        issue(
            "pass" if project.autonomy_mode in VALID_AUTONOMY_MODES else "fail",
            "AUTONOMY_MODE_VALID",
            f"autonomy_mode={project.autonomy_mode}",
            f"Use one of: {', '.join(sorted(VALID_AUTONOMY_MODES))}.",
        )
    )
    issues.append(
        issue(
            "pass" if project.intensity_mode in VALID_INTENSITY_MODES else "fail",
            "INTENSITY_MODE_VALID",
            f"intensity_mode={project.intensity_mode}",
            f"Use one of: {', '.join(sorted(VALID_INTENSITY_MODES))}.",
        )
    )
    issues.append(
        issue(
            "pass" if project.paid_api_mode in VALID_PAID_API_MODES else "fail",
            "PAID_API_MODE_VALID",
            f"paid_api_mode={project.paid_api_mode}",
            f"Use one of: {', '.join(sorted(VALID_PAID_API_MODES))}.",
        )
    )

    for field_name in ["daily_budget_usd", "per_cycle_budget_usd", "monthly_budget_usd"]:
        issues.append(_check_non_negative_number(project, field_name))
    issues.append(_check_min_int(project, "max_cycles_per_day", 1))
    issues.append(_check_min_int(project, "max_parallel_agents", 1))
    issues.append(_check_min_int(project, "run_frequency_hours", 1))

    issues.extend(validate_model_routing(project.model_routing))
    issues.extend(validate_retry_policy(project.retry_policy))

    for url in project.route_walk_urls:
        issues.append(
            issue(
                "pass" if _valid_url(url) else "fail",
                "ROUTE_WALK_URL_VALID",
                f"route_walk_url={url}",
                "No action needed." if _valid_url(url) else "Use a valid http(s) URL.",
            )
        )

    issues.append(
        issue(
            "pass" if project.builder_handoff_mode in {"manual", "disabled", "automatic"} else "fail",
            "BUILDER_HANDOFF_MODE_VALID",
            f"builder_handoff_mode={project.builder_handoff_mode}",
            "Use manual, disabled, or automatic.",
        )
    )
    if project.allow_automatic_builder_execution:
        issues.append(
            issue(
                "warn",
                "AUTOMATIC_BUILDER_EXECUTION_ENABLED",
                "Automatic builder execution is enabled",
                "Keep disabled until scheduler and execution guardrails are complete.",
            )
        )
    else:
        issues.append(issue("pass", "AUTOMATIC_BUILDER_EXECUTION_DISABLED", "Automatic builder execution disabled", "No action needed."))

    for field_name in ["build_command", "typecheck_command", "lint_command", "test_command", "dev_server_command"]:
        issues.extend(_check_command_safety(field_name, getattr(project, field_name, "")))

    issues.extend(validate_browser_qa_viewports(project.browser_qa_viewports))

    return issues


def validate_browser_qa_viewports(viewports: dict[str, str]) -> list[ConfigIssue]:
    """Validate browser_qa_viewports config entries (if any)."""
    if not viewports:
        return []
    checks: list[ConfigIssue] = []
    for name, spec in viewports.items():
        parts = str(spec).lower().split("x")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            w, h = int(parts[0]), int(parts[1])
            if w > 0 and h > 0:
                checks.append(issue("pass", "BROWSER_QA_VIEWPORT_VALID", f"viewport {name}={spec}", "No action needed."))
            else:
                checks.append(issue("fail", "BROWSER_QA_VIEWPORT_INVALID", f"viewport {name}={spec} has zero dimension", "Use WIDTHxHEIGHT with positive values."))
        else:
            checks.append(issue("fail", "BROWSER_QA_VIEWPORT_INVALID", f"viewport {name}={spec} invalid format", "Use WIDTHxHEIGHT (e.g. 375x812)."))
    return checks


def validate_retry_policy(policy: RetryPolicy) -> list[ConfigIssue]:
    checks: list[ConfigIssue] = []
    if isinstance(policy.max_attempts, int) and policy.max_attempts >= 1:
        checks.append(issue("pass", "RETRY_MAX_ATTEMPTS_VALID", f"retry_policy.max_attempts={policy.max_attempts}", "No action needed."))
    else:
        checks.append(issue("fail", "RETRY_MAX_ATTEMPTS_INVALID", "retry_policy.max_attempts must be an integer >= 1", "Fix in project YAML."))
    if isinstance(policy.backoff_seconds, int) and policy.backoff_seconds >= 1:
        checks.append(issue("pass", "RETRY_BACKOFF_SECONDS_VALID", f"retry_policy.backoff_seconds={policy.backoff_seconds}", "No action needed."))
    else:
        checks.append(issue("fail", "RETRY_BACKOFF_SECONDS_INVALID", "retry_policy.backoff_seconds must be an integer >= 1", "Fix in project YAML."))
    if isinstance(policy.backoff_multiplier, int) and policy.backoff_multiplier >= 1:
        checks.append(issue("pass", "RETRY_BACKOFF_MULTIPLIER_VALID", f"retry_policy.backoff_multiplier={policy.backoff_multiplier}", "No action needed."))
    else:
        checks.append(issue("fail", "RETRY_BACKOFF_MULTIPLIER_INVALID", "retry_policy.backoff_multiplier must be an integer >= 1", "Fix in project YAML."))
    if isinstance(policy.stop_on_same_error_count, int) and policy.stop_on_same_error_count >= 1:
        checks.append(issue("pass", "RETRY_STOP_ON_SAME_ERROR_VALID", f"retry_policy.stop_on_same_error_count={policy.stop_on_same_error_count}", "No action needed."))
    else:
        checks.append(issue("fail", "RETRY_STOP_ON_SAME_ERROR_INVALID", "retry_policy.stop_on_same_error_count must be an integer >= 1", "Fix in project YAML."))
    return checks


def worst_severity(issues: list[ConfigIssue]) -> str:
    severities = {item.severity for item in issues}
    if "fail" in severities:
        return "fail"
    if "warn" in severities:
        return "warn"
    return "pass"
