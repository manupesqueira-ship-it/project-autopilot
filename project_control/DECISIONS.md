# Decisions

## 2026-04-27 - Agent Control Layer Before Product Features

Decision: Pause product feature development and build an Agent Control Layer first.

Rationale: The project is ready for more implementation work, but autonomous or semi-autonomous coding needs durable state, guardrails, evidence collection, QA review, and escalation paths before additional product changes are safe.

## 2026-04-27 - Supervised Mode First

Decision: The initial agent workflow generates builder prompts but does not execute builder work automatically.

Rationale: This keeps humans in control while proving the quality gates, evidence collection, and OpenAI supervisor loop.

## 2026-04-27 - Project Autopilot As Reusable Orchestrator

Decision: Refactor the MIRA-only control layer into Project Autopilot, a reusable project-agnostic orchestrator.

Rationale: MIRA should be the first configured project, not the hardcoded system. Future projects should provide config and a `project_control/` context pack while sharing the same orchestration code.

## 2026-04-27 - Secrets Stay Outside Repo State

Decision: API keys and Telegram credentials must be supplied through the local environment or another approved secret store, never committed to project control files.

Rationale: The control layer should make missing credentials visible without exposing secret values.

## 2026-04-28 - Project Autopilot Is the Reusable System Name

Decision: The orchestrator is called Project Autopilot. MIRA is project #1, not the agent itself.

Rationale: Naming clarity prevents confusion as more projects are added.

## 2026-04-28 - Claude Code as Heavy Builder

Decision: Claude Code is the preferred agent for heavy implementation work (code generation, refactoring, bug fixes). Codex, ChatGPT, and Project Autopilot handle planning, QA, review, prompt generation, and cost control.

Rationale: Claude Code has superior context handling and tool use for large implementation tasks. OpenAI models are better suited for lightweight supervisory tasks at lower cost.

## 2026-04-28 - Default to Low-Cost Mode

Decision: Default intensity mode is `low_cost`. Paid generation (image, video) remains disabled by default.

Rationale: Minimize cost during development. Paid APIs are only enabled when explicitly approved by a human and configured in the project YAML.
