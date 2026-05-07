"""Flow specification scaffolding for Project Autopilot.

This module intentionally does not execute browser automation yet. It defines
small, project-agnostic data structures that later Playwright-backed flow
automation can consume.

Intended first MIRA flow:

    onboarding -> scan -> catalog -> tryon -> result

That flow should eventually validate form completion, photo upload, product
selection, try-on generation creation, result polling, and Supabase persistence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FlowStep:
    step_id: str
    description: str
    action: str = "manual"
    target: str = ""
    data_key: str = ""


@dataclass(frozen=True)
class FlowAssertion:
    assertion_id: str
    description: str
    target: str = ""
    expected: str = ""


@dataclass(frozen=True)
class FlowSpec:
    flow_id: str
    name: str
    start_url: str
    steps: list[FlowStep] = field(default_factory=list)
    assertions: list[FlowAssertion] = field(default_factory=list)
    required_data: dict[str, Any] = field(default_factory=dict)
    risk_level: str = "medium"


def mira_manual_e2e_flow() -> FlowSpec:
    """Return the planned MIRA manual E2E flow definition.

    The structure is useful for prompt generation and future automation, but it
    does not click, submit, upload, query Supabase, or mutate data.
    """
    return FlowSpec(
        flow_id="mira_manual_supabase_persistence_e2e",
        name="MIRA Supabase Persistence Manual E2E",
        start_url="/es/onboarding",
        risk_level="high",
        required_data={
            "test_user_email": "qa-test+manual-001@example.com",
            "required_tables": ["users_profile", "user_assets", "generations"],
            "required_bucket": "user-photos",
        },
        steps=[
            FlowStep("onboarding", "Submit onboarding form with fake QA test profile data.", "manual_submit", "/es/onboarding"),
            FlowStep("scan", "Upload safe test front scan photo.", "manual_upload", "/es/scan", "test_photo"),
            FlowStep("catalog", "Open catalog and choose one product.", "manual_click", "/es/catalog"),
            FlowStep("tryon", "Click the try-on CTA for the selected product.", "manual_click", "/es/tryon/[productId]"),
            FlowStep("result", "Observe result polling until mock output is visible.", "manual_observe", "/es/result/[generationId]"),
        ],
        assertions=[
            FlowAssertion("users_profile_row", "A users_profile row exists for the test user.", "Supabase users_profile"),
            FlowAssertion("storage_object", "A user-photos storage object exists for the uploaded test image.", "Supabase Storage user-photos"),
            FlowAssertion("user_assets_row", "A user_assets row references the uploaded storage path.", "Supabase user_assets"),
            FlowAssertion("generation_row", "A generations row exists for the try-on request.", "Supabase generations"),
            FlowAssertion("result_visible", "The result page displays mock output after polling.", "browser result page"),
        ],
    )


def available_flow_specs(project_id: str) -> list[FlowSpec]:
    """Return known flow specs for a project.

    Future versions can load these from project-specific YAML/JSON files.
    """
    if project_id == "mira":
        return [mira_manual_e2e_flow()]
    return []
