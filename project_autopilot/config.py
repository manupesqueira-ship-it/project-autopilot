from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

AUTOPILOT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = AUTOPILOT_ROOT.parent
PROJECTS_DIR = AUTOPILOT_ROOT / "config" / "projects"


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    backoff_seconds: int = 60
    backoff_multiplier: int = 2
    stop_on_same_error_count: int = 3


@dataclass
class ModelRouting:
    cheap_model: str = "gpt-5.4-mini"
    standard_model: str = "gpt-5.4"
    premium_model: str = "gpt-5.5"
    qa_model: str = "gpt-5.4"


@dataclass
class ProjectConfig:
    project_id: str
    project_name: str
    repo_path: Path
    project_control_path: Path
    framework: str
    package_manager: str
    build_command: str
    typecheck_command: str
    lint_command: str = ""
    test_command: str = ""
    dev_server_command: str = ""
    route_walk_urls: list[str] = field(default_factory=list)
    autonomy_mode: str = "autonomous_guarded"
    intensity_mode: str = "low_cost"
    max_retries_per_task: int = 3
    run_frequency_hours: int = 3
    max_cycles_per_day: int = 4
    max_parallel_agents: int = 1
    daily_budget_usd: float = 5.0
    per_cycle_budget_usd: float = 1.5
    monthly_budget_usd: float = 100.0
    paid_api_mode: str = "disabled_by_default"
    allow_paid_image_generation: bool = False
    allow_paid_video_generation: bool = False
    telegram_enabled: bool = False
    builder_primary: str = "codex"
    builder_fallback: str = "claude"
    allow_automatic_builder_execution: bool = False
    builder_handoff_mode: str = "manual"
    claude_command: str = "claude"
    latest_prompt_path: str = ""
    browser_qa_enabled: bool = False
    screenshot_enabled: bool = True
    browser_qa_viewports: dict[str, str] = field(default_factory=dict)
    model_routing: ModelRouting = field(default_factory=ModelRouting)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    logs_dir: str = "logs"
    screenshots_dir: str = "screenshots"


def _coerce_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    """Parse the small YAML subset used by Project Autopilot configs.

    Supported shapes are top-level scalars, top-level lists, and one-level
    dictionaries. This keeps the system dependency-free for early bootstrap.
    """
    data: dict[str, Any] = {}
    current_key: str | None = None
    current_kind: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()

        if indent > 0 and current_key:
            if stripped.startswith("-") and current_kind == "list":
                data[current_key].append(_coerce_scalar(stripped[1:].strip()))
            elif ":" in stripped and current_kind == "dict":
                key, value = stripped.split(":", 1)
                data[current_key][key.strip()] = _coerce_scalar(value.strip())
            continue

        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            data[key] = []
            current_key = key
            current_kind = "list"
        elif value == "{}":
            data[key] = {}
            current_key = None
            current_kind = None
        elif value == "[]":
            data[key] = []
            current_key = None
            current_kind = None
        else:
            data[key] = _coerce_scalar(value)
            current_key = None
            current_kind = None

        if value == "" and key in {"model_routing", "browser_qa_viewports", "retry_policy"}:
            data[key] = {}
            current_kind = "dict"

    return data


def _resolve_path(value: str | Path, base: Path = REPO_ROOT) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base / path).resolve()


def project_config_path(project_id: str) -> Path:
    return PROJECTS_DIR / f"{project_id}.yaml"


def load_project_config(project_id: str) -> ProjectConfig:
    path = project_config_path(project_id)
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in PROJECTS_DIR.glob("*.yaml"))) or "none"
        raise FileNotFoundError(f"Unknown project '{project_id}'. Available projects: {available}")

    raw = parse_simple_yaml(path)
    routing = ModelRouting(**raw.get("model_routing", {}))
    viewports = raw.get("browser_qa_viewports", {})
    retry = RetryPolicy(**raw.get("retry_policy", {}))
    raw = {key: value for key, value in raw.items() if key not in {"model_routing", "browser_qa_viewports", "retry_policy"}}
    raw["repo_path"] = _resolve_path(raw["repo_path"])
    raw["project_control_path"] = _resolve_path(raw["project_control_path"], raw["repo_path"])
    raw["model_routing"] = routing
    raw["retry_policy"] = retry
    if viewports:
        raw["browser_qa_viewports"] = viewports
    return ProjectConfig(**raw)

