# Architecture Decision Records

> Una entrada por decisión importante. Formato: contexto, opciones (si aplica), decisión, consecuencias.
> Numeración cronológica única independientemente del proyecto. Los ADR-001 a ADR-007 son sobre Project Autopilot (orquestador). ADR-008 en adelante son sobre AI Brief LATAM (property #1).

---

## ADR-001 — Agent Control Layer Before Product Features

**Fecha:** 2026-04-27
**Status:** Aceptada
**Scope:** Project Autopilot

**Contexto / rationale:** The project is ready for more implementation work, but autonomous or semi-autonomous coding needs durable state, guardrails, evidence collection, QA review, and escalation paths before additional product changes are safe.

**Decisión:** Pause product feature development and build an Agent Control Layer first.

---

## ADR-002 — Supervised Mode First

**Fecha:** 2026-04-27
**Status:** Aceptada
**Scope:** Project Autopilot

**Contexto / rationale:** This keeps humans in control while proving the quality gates, evidence collection, and OpenAI supervisor loop.

**Decisión:** The initial agent workflow generates builder prompts but does not execute builder work automatically.

---

## ADR-003 — Project Autopilot As Reusable Orchestrator

**Fecha:** 2026-04-27
**Status:** Aceptada
**Scope:** Project Autopilot

**Contexto / rationale:** MIRA should be the first configured project, not the hardcoded system. Future projects should provide config and a `project_control/` context pack while sharing the same orchestration code.

**Decisión:** Refactor the MIRA-only control layer into Project Autopilot, a reusable project-agnostic orchestrator.

---

## ADR-004 — Secrets Stay Outside Repo State

**Fecha:** 2026-04-27
**Status:** Aceptada
**Scope:** Project Autopilot

**Contexto / rationale:** The control layer should make missing credentials visible without exposing secret values.

**Decisión:** API keys and Telegram credentials must be supplied through the local environment or another approved secret store, never committed to project control files.

---

## ADR-005 — Project Autopilot Is the Reusable System Name

**Fecha:** 2026-04-28
**Status:** Aceptada
**Scope:** Project Autopilot

**Contexto / rationale:** Naming clarity prevents confusion as more projects are added.

**Decisión:** The orchestrator is called Project Autopilot. MIRA is project #1, not the agent itself.

---

## ADR-006 — Claude Code as Heavy Builder

**Fecha:** 2026-04-28
**Status:** Aceptada
**Scope:** Project Autopilot

**Contexto / rationale:** Claude Code has superior context handling and tool use for large implementation tasks. OpenAI models are better suited for lightweight supervisory tasks at lower cost.

**Decisión:** Claude Code is the preferred agent for heavy implementation work (code generation, refactoring, bug fixes). Codex, ChatGPT, and Project Autopilot handle planning, QA, review, prompt generation, and cost control.

---

## ADR-007 — Default to Low-Cost Mode

**Fecha:** 2026-04-28
**Status:** Aceptada
**Scope:** Project Autopilot

**Contexto / rationale:** Minimize cost during development. Paid APIs are only enabled when explicitly approved by a human and configured in the project YAML.

**Decisión:** Default intensity mode is `low_cost`. Paid generation (image, video) remains disabled by default.

---

## ADR-008 — Voice strategy: voice clone 100% (ElevenLabs)

**Fecha:** 2026-05-09
**Status:** Aceptada (pendiente grabación)
**Scope:** AI Brief LATAM

**Contexto:** 3 opciones: voz humana 100%, voice clone, híbrido. Nota: contradice `brand_voice.md` de 2026-05-07 que listaba ElevenLabs solo como backup multi-idioma.

**Decisión:** Voice clone 100% con ElevenLabs ($22/mes). Grabación de 20 min pendiente.

**Consecuencias:** Sistema 100% automatizable Fase 2+. Trade-off: 10-15% menos emoción.

---

## ADR-009 — Stack de orquestación: n8n cloud (no Python custom)

**Fecha:** 2026-05-10
**Status:** Aceptada
**Scope:** AI Brief LATAM

**Contexto:** Construimos 9 agents Python que funcionan pero producen output mediocre. El stack custom no rivaliza con herramientas profesionales que la industria ya estandarizó.

**Opciones consideradas:**
- A) Continuar con Python custom + LangGraph eventual
- B) Pivotar a n8n cloud con Anthropic node nativo
- C) Híbrido (n8n llama Python como microservicios)

**Decisión:** B

**Consecuencias:** Deltas #17 y #22 del research 2026-05-08 superseded. 9 agents Python preservados como referencia en `legacy/`. Reorganización del repo.

---

## ADR-010 — Ángulo editorial: A generalista LATAM

**Fecha:** 2026-05-10
**Status:** Aceptada (pendiente refinamiento)
**Scope:** AI Brief LATAM

**Contexto:** 4 opciones de ángulo del research (generalista / vertical sectorial / governance-ROI / middle-market).

**Decisión:** A) Generalista. Verticalizar en mes 2 con data real.

**Consecuencias:** Sistema produce contenido amplio Fase 1, riesgo de saturación si no diferencia voz claramente.

---

## ADR-011 — Volumen Fase 1: 1 post/día

**Fecha:** 2026-05-10
**Status:** Aceptada
**Scope:** AI Brief LATAM

**Contexto:** Originalmente 3/día. Manuel ajustó a 1/día para validar antes de escalar.

**Decisión:** 1/día Fase 1, escalar según tracción.

**Consecuencias:** Costos bajan a ~$60-80/mes, margen de iteración mayor.

---

## ADR-012 — Publisher: Blotato/Upload-Post antes que Buffer

**Fecha:** 2026-05-10
**Status:** Pendiente evaluación
**Scope:** AI Brief LATAM

**Contexto:** Research de templates n8n indicó Buffer GraphQL para IG carousel es "unwalked path".

**Decisión:** Evaluar Blotato y Upload-Post antes de comprometer a Buffer.

**Consecuencias:** `docs/STACK.md` actualizado con alternativas.

---

## ADR-013 — Image generation: gpt-image-2 (no Pillow ni Canva primario)

**Fecha:** 2026-05-10
**Status:** Aceptada
**Scope:** AI Brief LATAM

**Contexto:** Pillow generator producía visuales mediocres. Canva Pro requiere API plan caro.

**Decisión:** gpt-image-2 como primario, Canva como backup manual.

**Consecuencias:** Quality alta sin intervención humana. Swap manual obligatorio en templates que usan gpt-image-1.

---

## ADR-014 — Publisher: Upload-Post (resolución de ADR-012)

**Fecha:** 2026-05-12
**Status:** Propuesta — pendiente confirmación Manuel
**Scope:** AI Brief LATAM
**Supersedes:** ADR-012 (que dejaba abierta la elección)

**Contexto:** ADR-012 cerró el "no a Buffer primario" pero dejó pendiente la elección entre Blotato, Upload-Post, y Meta Graph API directo. Necesario decidir antes de spec'ear el node A10 de Fase 1.

**Investigación (2026-05-12):**

| Opción | Costo | Carousel IG | TikTok | Integración n8n | Madurez | Riesgo |
|---|---:|---|---|---|---|---|
| **Buffer Essentials** | $15/mo | ⚠️ max 10 imgs (vs IG 20 nativo) | ✅ Sí | API REST, no node oficial | Alta — 10+ años | Bajo |
| **Blotato Starter** | $29/mo | ✅ Sí, AI Agent Carousel Maker | ✅ Sí | **Node oficial n8n** | Media — 2 años | **Medio-alto — Trustpilot 2.0/5 con 84% one-star sobre billing/support** |
| **Upload-Post** | Variable (TBD según volumen) | ✅ Sí (template n8n #3524 demuestra) | ✅ Sí | **Node oficial community por Upload-Post** | Media — open source | Bajo |
| **Meta Graph API directo** | $0 | ✅ Sí (con OAuth complejo) | ❌ Separate TikTok API | Custom HTTP Request | N/A | Alto — mantenimiento OAuth tokens |

**Decisión:** **Upload-Post** como publisher primario.

**Razones (en orden de peso):**
1. **Node oficial n8n mantenido por Upload-Post mismo** (https://github.com/Upload-Post/n8n-nodes-upload-post) — soporta TikTok, Instagram, YouTube, LinkedIn, X, Facebook, Pinterest, Threads, Reddit, Bluesky. Carousel confirmado vía template #3524.
2. **Multi-platform desde día 1** — no necesitamos separate integration para TikTok (gap de Buffer + Meta directo).
3. **Trade-off vs Blotato:** Blotato tiene la peor reputación de billing/support en reviews 2026 (Trustpilot 2.0/5). Upload-Post no tiene esa mancha y es open-source-friendly. Riesgo más bajo si tenemos problemas.
4. **Costo:** TBD según volumen, pero el modelo es transparente vs Blotato $29/mo credits-based.

**Consecuencias:**
- A10 Publisher se especifica con node `n8n-nodes-upload-post` (community node — instalación requiere n8n self-hosted o aprobación n8n cloud para community nodes).
- **Implicación crítica:** community nodes en n8n cloud Starter/Pro requieren approval o limitan funcionalidad. Esto **inclina la balanza hacia self-hosted** para evitar el limbo de community nodes en cloud. Ver ADR-015.
- Manuel debe crear cuenta en Upload-Post antes de Fase 1 (no urgente para Fase 0 que no publica).
- Buffer queda como backup manual (si Upload-Post falla un día, Manuel publica via Buffer en modo MANUAL_OPERATIONS).

**Fallback path:** si Upload-Post tiene un problema o no se adapta, **Blotato es el plan B** (a pesar de los reviews, su node oficial es maduro y la AI Agent Carousel Maker es justo lo que necesitamos). Buffer es plan C solo si todo el resto falla.

---

## ADR-015 — n8n deployment: Hostinger VPS self-hosted (no n8n cloud Pro)

**Fecha:** 2026-05-12
**Status:** Propuesta — pendiente confirmación Manuel
**Scope:** AI Brief LATAM

**Contexto:** La inspección del template #12533 reveló que el polling architecture supera el plan n8n cloud Starter (2,500 ejec/mes vs ~4,500 estimadas en Fase 1). ADR-009 había lockeado n8n cloud sin especificar plan. Hay que decidir antes de Fase 1.

**Investigación (2026-05-12):**

| Opción | Costo/mes | Ejecuciones | Setup | Mantenimiento | Community nodes |
|---|---:|---|---|---|---|
| **n8n cloud Starter** | €24 | 2,500 | 0 min — paga y usa | 0 (managed) | ⚠️ restringidos |
| **n8n cloud Pro** | €60 | 10,000 | 0 min | 0 (managed) | ⚠️ restringidos |
| **Hostinger VPS KVM2** | **~€6 ($6.49)** | **Ilimitadas** | ~30 min vía template "one-click" | Tuyo (updates + SSL + backups) | ✅ libres |

**Decisión:** **Hostinger VPS KVM2 self-hosted** ($6.49/mo) con template oficial n8n.

**Razones (en orden de peso):**

1. **Costo 10× menor que cloud Pro.** $6.49 vs $60 = $54/mo de ahorro × 12 meses = **$648/año ahorrado**. A escala de 1 property es significativo; a 3 properties (AI Brief + Crypto Brief + Startup Radar compartiendo el VPS) el ahorro es 30× contra alternativas paid.

2. **Ejecuciones ilimitadas.** Cloud Pro tope = 10,000 ejec/mes. Self-hosted = sin límite — soporta crecimiento de 12 fuentes a 30+ sin upgrade de plan.

3. **Community nodes sin restricciones.** El node oficial de Upload-Post (ADR-014) es community node. En cloud Starter/Pro, community nodes requieren approval especial o están limitados. Self-hosted los corre sin friction.

4. **Template "one-click" de Hostinger reduce el setup a ~30 min** (vs Docker manual + nginx + SSL + cert renewal que serían 4-6 horas). Hostinger maneja:
   - Docker install + n8n image
   - SSL via Let's Encrypt automático
   - n8n template con queue mode (necesario para Fase 1 polling concurrente)
   - 100+ pre-made workflows opcionales

5. **Specs cómodas.** KVM2 = 2 vCPU + 8GB RAM + 100GB NVMe. n8n recomienda mínimo 2 vCPU + 4 GB; tenemos doble RAM, holgura para cuando suba el volumen.

**Trade-offs aceptados:**

- **Mantenimiento es tuyo.** Updates de n8n (~mensual), upgrade de OS (~trimestral), backups (configurar 1× con script en cron), monitoring del VPS (Hostinger tiene dashboard básico). Estimado: **~30 min/mes de Manuel**.
- **Si el VPS cae, pipeline cae.** Cloud tiene SLA 99.5%. Hostinger sin SLA explícito para self-hosted. Mitigación: backup diario del workflow JSON + Supabase + assets bucket (todo replicable en otro VPS en ~1h si pasa lo peor).
- **Sin "soporte" de n8n.** Si rompemos algo, depende de community forum / docs. Cloud tiene soporte managed. Para nuestro caso, los workflows son simples y el riesgo es bajo.

**Plan de transición:**
1. **Fase 0 corre en n8n cloud trial** (la cuenta de aibrieflatam.media@gmail.com que ya importó el template #12533). Smoke test no necesita migración.
2. **Antes de Fase 1**, crear Hostinger VPS + aplicar template n8n. Tiempo estimado: 1 hora total.
3. **Migrar el workflow** via Export JSON → Import JSON al VPS. n8n.cloud y self-hosted usan el mismo schema JSON.
4. **Migrar credenciales** manual (re-pegado de API keys en el self-hosted).
5. **Apagar trial cloud** una vez verificado el self-hosted estable por 7 días.

**Consecuencias:**
- `docs/STACK.md` debe actualizarse: línea "n8n Cloud $24/mo" → "Hostinger VPS KVM2 ~$6.49/mo (self-hosted)".
- ROADMAP semana 2 incluye 1 hora de "VPS setup + n8n install" entre Fase 0 y Fase 1.
- Reduce el costo total Fase 1 de ~$85/mo a ~$30/mo (subimos LLM costs + image gen pero bajamos el orquestador).
- **Backup pattern obligatorio:** cron diario que `git commit -am` el workflow export en un repo privado. Si el VPS muere, el workflow vive en GitHub.

**Plan B si Hostinger no funciona:** Railway.app ($5/mo) o DigitalOcean Droplet ($6/mo). Mismo concepto self-hosted, otro proveedor.
