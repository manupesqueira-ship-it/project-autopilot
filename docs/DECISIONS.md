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

---

# AI Brief LATAM — ADRs

> Decisiones arquitectónicas específicas de la propiedad AI Brief LATAM. Formato ADR: contexto, opciones, decisión, consecuencias.

## ADR-001 — Stack de orquestación: n8n cloud (no Python custom)

**Fecha:** 2026-05-10
**Status:** Aceptada
**Contexto:** Construimos 9 agents Python que funcionan pero producen output mediocre. El stack custom no rivaliza con herramientas profesionales que la industria ya estandarizó.
**Opciones consideradas:**
- A) Continuar con Python custom + LangGraph eventual
- B) Pivotar a n8n cloud con Anthropic node nativo
- C) Híbrido (n8n llama Python como microservicios)
**Decisión:** B
**Consecuencias:** Deltas #17 y #22 superseded. 9 agents Python preservados como referencia en legacy/. Reorganización del repo.

---

## ADR-002 — Ángulo editorial: A generalista LATAM

**Fecha:** 2026-05-10
**Status:** Aceptada (pendiente refinamiento)
**Contexto:** 4 opciones de ángulo del research (generalista / vertical sectorial / governance-ROI / middle-market).
**Decisión:** A) Generalista. Verticalizar en mes 2 con data real.
**Consecuencias:** Sistema produce contenido amplio Fase 1, riesgo de saturación si no diferencia voz claramente.

---

## ADR-003 — Volumen Fase 1: 1 post/día

**Fecha:** 2026-05-10
**Status:** Aceptada
**Contexto:** Originalmente 3/día. Manuel ajustó a 1/día para validar antes de escalar.
**Decisión:** 1/día Fase 1, escalar según tracción.
**Consecuencias:** Costos bajan a ~$60-80/mes, margen de iteración mayor.

---

## ADR-004 — Publisher: Blotato/Upload-Post antes que Buffer

**Fecha:** 2026-05-10
**Status:** Pendiente evaluación
**Contexto:** Research de templates n8n indicó Buffer GraphQL para IG carousel es "unwalked path".
**Decisión:** Evaluar Blotato y Upload-Post antes de comprometer a Buffer.
**Consecuencias:** STACK.md actualizado con alternativas.

---

## ADR-005 — Voice strategy: voice clone 100% (ElevenLabs)

**Fecha:** 2026-05-09
**Status:** Aceptada (pendiente grabación)
**Contexto:** 3 opciones: voz humana 100%, voice clone, híbrido.
**Decisión:** Voice clone 100% con ElevenLabs ($22/mes). Grabación de 20 min pendiente.
**Consecuencias:** Sistema 100% automatizable Fase 2+. Trade-off: 10-15% menos emoción.

---

## ADR-006 — Image generation: gpt-image-2 (no Pillow ni Canva primario)

**Fecha:** 2026-05-10
**Status:** Aceptada
**Contexto:** Pillow generator producía visuales mediocres. Canva Pro requiere API plan caro.
**Decisión:** gpt-image-2 como primario, Canva como backup manual.
**Consecuencias:** Quality alta sin intervención humana. Swap manual obligatorio en templates que usan gpt-image-1.
