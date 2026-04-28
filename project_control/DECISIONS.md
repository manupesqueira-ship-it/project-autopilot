# Decisions

## 2026-04-27 - Agent Control Layer Before Product Features

Decision: Pause product feature development and build an Agent Control Layer first.

Rationale: The project is ready for more implementation work, but autonomous or semi-autonomous coding needs durable state, guardrails, evidence collection, QA review, and escalation paths before additional product changes are safe.

## 2026-04-27 - Supervised Mode First

Decision: The initial agent workflow generates builder prompts but does not execute builder work automatically.

Rationale: This keeps humans in control while proving the quality gates, evidence collection, and OpenAI supervisor loop.

## 2026-04-27 - Secrets Stay Outside Repo State

Decision: API keys and Telegram credentials must be supplied through the local environment or another approved secret store, never committed to project control files.

Rationale: The control layer should make missing credentials visible without exposing secret values.
