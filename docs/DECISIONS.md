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

## ADR-016 — Pivot estratégico post-Critical-Review (4 cambios mayores)

**Fecha:** 2026-05-18
**Status:** Propuesta — confirmar parcialmente con outputs de Deep Research (carril 2 lanzado 2026-05-18)
**Scope:** AI Brief LATAM / proyecto en general
**Trigger:** Critical Review interno (`docs/CRITICAL_REVIEW.md`) + carril 3 respondido por Manuel:
- North star: audiencia masiva, revenue diferido
- Strategy: convicción full en UNA idea hasta validar
- Experimento: cuánto se puede automatizar una red social con IA

**Contexto:** El Critical Review identificó 5 problemas estructurales del plan. Manuel respondió cada uno y aceptó 4 pivots. Este ADR los codifica para que todo el repo opere bajo la misma página.

### Pivot 1 — Nicho: AI News → AI How-To

**Antes:** "AI Brief LATAM" = news brief diario de IA (modelo Rundown AI). Saturado en español (Digital Brain 60K, IA al Día 20K+).
**Después:** "AI How-To LATAM" (nombre tentativo, rename pending) = contenido práctico tutorial sobre cómo USAR herramientas IA. Menos saturado, más shareable (saves > likes en algoritmo 2026), más defensible para 1 operador.

**Implicaciones:**
- Fuentes (`sources.yaml`) cambian peso: feeds de productividad/herramientas pesan más que noticias de modelos
- Scoring (`a2`) cambia: peso a `potencial_educativo` y `aplicabilidad_inmediata` sube, peso a `novedad` baja
- Editorial (`a3`) cambia: estructura output → tutorial step-by-step vs news brief
- Visual standard puede mantenerse — el dark mode editorial funciona para how-to
- **Acción inmediata:** marcar como dirección, NO renombrar carpeta `projects/dinero-ia/` aún (Manuel: "el nombre es lo de menos, luego lo cambiamos")
- **Acción tras Deep Research:** confirmar específicamente cuál tópico how-to (AI práctico genérico vs herramientas específicas vs por industria) según Prompt 4 output

### Pivot 2 — Voz: Anti-hype sobrio → Viral hype calibrado

**Antes:** Smart Brevity + Morning Brew + "anti-hype" como regla dura. Techo ~30K (research benchmarks LATAM).
**Después:** Viral hype calibrado — hooks emocionales/contrarian + body sobrio Smart Brevity. Modelo NeoCom/Filo (>1M en 2-3 años) pero con contenido educativo en lugar de pop culture.

**Implicaciones:**
- `brand_voice.md` cambia: "Hard NO hype" → "Hype con framework (atención + tensión + promesa pero EMOCIONAL no técnico)"
- `a2-signal-scorer.md` cambia: `potencial_viral` peso sube significativamente
- `a3-editorial.md` cambia: `hook_tentativo` se permite emocional/contrarian si está respaldado
- `a9-compliance.md` cambia: regla 8 ("NO hype injustificado") matizada — el hype es OK si pasa el framework de 3 condiciones
- Riesgo: contradicción con "AI ethics no irresponsable" — mitigar con regla "hook viral pero cuerpo defendible con datos"
- **Acción inmediata:** update `brand_voice.md` con calibración explícita
- **Acción tras Deep Research:** confirmar con outputs del Prompt 3 (playbook 10K-100K) qué tipo de hook usaron

### Pivot 3 — Scope: Multi-property scaffold → Single-property convicción

**Antes:** Repo asume 3 properties paralelas (AI Brief + Crypto Brief + Startup Radar). ROADMAP Fase 5 multi-property. Multiple docs anticipan expansión.
**Después:** Single-property exclusivo hasta validar AI How-To LATAM (>5K subs/followers). Multi-property scaffold se elimina/comenta.

**Implicaciones:**
- `ROADMAP.md` Fase 5 → "TBD post-validation, no comprometido"
- `COSTS_6MO.md` → eliminar sensitivity multi-property
- `a9-compliance.md` → eliminar tabla "Reglas a expandir cuando arranque cada feature" (la fila Newsletter se mantiene como platform-level)
- `sources.yaml` → eliminar comentarios "para Crypto Brief"
- **Acción inmediata:** limpieza en los 4 archivos arriba

### Pivot 4 — Order: Design-first → Validate-first

**Antes:** 35+ commits de diseño, 0 piezas publicadas, smoke test pospuesto al día 11.
**Después:** **Validación manual ANTES de cualquier ejecución técnica**. Manuel publica 5-10 piezas con prompts directos en Claude.ai en cuenta personal/test. Si funciona → smoke test técnico. Si no → iterar voz, NO construir pipeline.

**Implicaciones:**
- `ROADMAP.md` reordenado: agregar **Fase -1 "Validación Manual"** antes de Fase 0.
- `MANUAL_OPERATIONS.md` se promueve a operación primaria, no fallback.
- Decisiones futuras: priorizar "test rápido en mundo real" sobre "documentación completa".
- **Acción inmediata:** update ROADMAP. Manuel ejecuta Validación Manual cuando tenga 1-2 horas de calma.

### Implicaciones cross-pivot — orden de operaciones revisado

Antes del Critical Review:
```
Diseño completo → Fase 0 smoke test → Fase 1 build → Fase 2 reels → Fase 3 newsletter scale → Fase 4 podcast
```

Después de ADR-016:
```
Validación Manual (5-10 piezas, 7-14 días) → Decision Point
    ├─ Si voz funciona (>2% engagement) → Build vs Buy decision (Blotato vs custom)
    │   ├─ Build → Fase 0 smoke test → Fase 1 pipeline
    │   └─ Buy → Blotato 30 días → iteración → reconsiderar
    └─ Si voz NO funciona → iterar voz manual → re-evaluar nicho
```

### Status de los 15 ADRs previos tras este pivot

| ADR | Status | Razón |
|---|---|---|
| ADR-001 a ADR-007 | Sin cambio | Sobre Project Autopilot, no AI Brief |
| ADR-008 (voice clone ElevenLabs) | Sigue vigente | Pero **rebaja prioridad** — solo cuando reels arranquen post-validación |
| ADR-009 (n8n stack) | Sigue vigente | Pero contingent en build-decision post Validación Manual |
| ADR-010 (ángulo generalista LATAM) | **MODIFICADO** | Ya no generalista IA news, ahora how-to específico |
| ADR-011 (1 post/día Fase 1) | Sigue vigente | Pero aplica a Fase 1 post-validación, no Fase -1 |
| ADR-012 (publisher) | Sigue vigente | Pero contingent en build-decision |
| ADR-013 (gpt-image-2) | Sigue vigente | Visual generation se mantiene |
| ADR-014 (Upload-Post) | Sigue vigente | Mismo caveat |
| ADR-015 (Hostinger VPS) | Sigue vigente | Mismo caveat |

### Riesgos de este pivot

1. **Re-trabajo:** algunos prompts (a2, a3, a7) van a requerir ajustes — ~2-4 horas total.
2. **Identidad del proyecto:** "AI Brief LATAM" como nombre puede confundir hasta que se rename.
3. **Sobreajuste:** si los Deep Research dicen "AI news SÍ es buen nicho", reversamos parcialmente.
4. **Pérdida de momentum:** parar para validar manual puede sentirse como "regresión", pero es necesario.

### Acciones de este ADR (concretas)

- [x] Documentar este ADR-016
- [ ] Update `ROADMAP.md` con Fase -1 + remover Fase 5 multi-property
- [ ] Update `brand_voice.md` con calibración hype + how-to focus
- [ ] Update `config.yaml` con description + name pending rename + phase
- [ ] Update `a9-compliance.md` removiendo tabla multi-property
- [ ] Update `COSTS_6MO.md` removiendo sensitivity multi-property
- [ ] Update `sources.yaml` removiendo refs a Crypto Brief
- [ ] Update `OPEN_QUESTIONS.md` cerrando P (voz) + agregando Q, R, S, T, U

### Acciones deferred (esperando Deep Research)

- [ ] Confirmar nicho específico how-to (output Prompt 4)
- [ ] Decisión build vs buy (output Prompt 1)
- [ ] Update prompts A2/A3/A7 con calibración final (después de Validación Manual)
- [ ] Rename físico de carpeta `projects/dinero-ia/` → confirmed name

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

1. **Costo 10× menor que cloud Pro.** $6.49 vs $60 = $54/mo de ahorro × 12 meses = **$648/año ahorrado** para AI How-To LATAM (single property post-ADR-016).

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

---

## ADR-017 — Pivot post-Deep-Research: nicho AI×Finanzas, stack SaaS-first, target realista, inflection lever

**Fecha:** 2026-05-29
**Status:** Aceptada (Manuel respondió 5 decisiones + 3 sub-decisiones)
**Scope:** AI Brief LATAM (carpeta sigue como está hasta que haya handle/dominio decidido)
**Supersedes parcial:** ADR-010 (ángulo), ADR-014 (publisher), ADR-015 (deployment), ADR-016 (pivot #1, 4 cambios)
**Defers:** ADR-008 (voice clone)
**Trigger:** 5 Deep Research outputs procesados 2026-05-20 (`docs/DEEP_RESEARCH_SYNTHESIS.md`)

### Contexto

ADR-016 ejecutó 4 pivots el 2026-05-18 basado en el Critical Review interno. Los 5 Deep Research outputs (carril 2) confirmaron 3 de los 4 pivots y agregaron 3 capas nuevas que no estaban en el plan:

- **Layer 5:** target audiencia >100K en 12-18m no soportado por dataset de 11 creators reales.
- **Layer 6:** existe shortcut SaaS a $48/mo que cubre 75-80% del pipeline.
- **Layer 7:** 9 de 11 creators escalaron por canal EXTERNO (partnership, press, podcast guest), no viralidad orgánica.

Manuel respondió las 5 decisiones (1a, 2e, 3b, 4b, 5c) y las 3 sub-decisiones operativas (carpeta default, vertical único finanzas, compliance educativo).

### Cambio 1 — Reset realista del target de audiencia (decisión 1a)

**Antes (ADR-016 implícito + brand_voice v2):** north star = "audiencia masiva >100K" en 12-18 meses, modelo NeoCom/Filo.

**Ahora:**
- **Base case 10K en 12 meses** (Report 03: 45-65% prob con 4 factores ejecutados; sin lever externo baja a 25-30%).
- **30-50K en 24 meses** con stack maduro + lever ejecutado.
- **100K reservado para 36+ meses con equipo** (NO founder solo).
- North star de Manuel ("audiencia masiva") se mantiene como **horizonte de largo plazo**, NO como target de 12-18m.

**Justificación:** dataset Report 03 (Pictoline, MPF, Filo, Cenital, DotCSV, Mafia IA, Startupeable, etc.). 0 de 11 creators alcanzó 100K solo en 12-18m. Ajustar metas a base rates evita declarar fracaso a los 12 meses cuando 10K-30K es realmente un buen resultado.

### Cambio 2 — Pivot nicho: AI How-To genérico → AI × Finanzas Personales LATAM (decisión 2e)

**Antes (ADR-016 pivot 1):** AI How-To LATAM generalista para profesionales 25-45.

**Ahora:** **AI × Finanzas Personales LATAM** como vertical único. Sub-decisión B = B.1 (vertical único, NO wedge + expansión).

**Por qué:**
- Report 04 score: 23+ (AI puro 21; Real Estate 17; AI noticias 15).
- Combina dos verticales con mayor demanda actual: IA (+387% YoY views TikTok español) + finanzas personales LATAM (boom post-pandemia + educación financiera obligatoria 2025 en MX/AR/CO/CL).
- Sale del lane "gurú financiero" (saturadísimo) y "AI brief generalista" (saturado) entrando como "el que te enseña la herramienta".
- Monetización doble: SaaS AI affiliate + cursos finanzas/inversión.
- Defensible: requiere conocer ambos verticales, barrera para imitadores.

**Pregunta tipo que cada pieza responde:** "¿Cómo uso IA para [decisión financiera concreta LATAM]?"

Ejemplos del tipo de pieza:
- "El prompt que usé para analizar 5 ETFs en 10 min (con datos LATAM)"
- "Probé Claude para mi presupuesto mensual. Esto encontró que mi planilla no veía."
- "Cómo armar tu plan de retiro con IA, en español, en 20 min"
- "El error que cometen los argentinos con CEDEARs (y cómo IA lo detecta antes)"

**Riesgo aceptado:** compliance financiero LATAM (CNV ARG, CNBV MX, SFC COL endurecieron 2024-2025). Mitigado por sub-decisión C = C.1 (educativo, no asesoría — modelo Sofía Macías / Mis Propias Finanzas).

### Cambio 3 — Stack: SaaS-first, n8n minimalista (decisión 3b)

**Antes (ADR-014 + ADR-015):** Hostinger VPS self-hosted ($6.49/mo) + n8n + Upload-Post community node como núcleo del pipeline.

**Ahora — stack híbrido buy-first:**

| Capa | Antes | Ahora | Por qué |
|---|---|---|---|
| Publishing IG/TikTok/LinkedIn | Upload-Post community node | **ContentStudio Standard** ($19/mo) | Hub social maduro, RSS discovery + approvals + scheduling nativos. Report 01: G2 4.6/372 reviews. |
| Carousel generation + AI visuals | gpt-image-2 directo + custom | **Blotato Starter** ($29/mo) | AI Agent Carousel Maker + 58 idiomas + community nodes oficiales n8n/Make. Report 01: cubre el caso. Es el "plan B" que ya teníamos. |
| Newsletter | Beehiiv (Fase 3) | **Beehiiv Launch** ($0 hasta 2,500 subs) → **Scale** ($43/mo) | Sin cambio en herramienta, pero adelantado a Fase 1 (no Fase 3) porque es el activo más durable según Reports 02+05. |
| Orquestación + moat editorial | n8n self-hosted en Hostinger VPS | **n8n cloud trial** (gratis) primero; **migrar a Hostinger VPS solo si el trial se acaba**. n8n queda SOLO para el moat: scorer LATAM + fact-check + Telegram approval. | Reduce setup time + supply chain risk (Report 05: n8n CVEs reales 2025-2026). |

**Costo nuevo:** ~$48/mo Fase 1 (ContentStudio $19 + Blotato $29 + Beehiiv $0 + n8n cloud $0 + dominio $1 + Anthropic ~$25-42 + OpenAI ~$6-8). Total realista **~$80-100/mo Fase 1**, vs ~$80-100/mo del stack anterior. **Mismo precio, menos overhead, menos supply chain risk.**

**ADR-014 (Upload-Post) → SUPERSEDED.** Upload-Post no aparece en el análisis competitivo Report 01; Blotato cubre el caso con community node oficial maduro. Si Blotato falla, plan B = ContentStudio nativo o Upload-Post como tercera opción.

**ADR-015 (Hostinger VPS) → MODIFICADO.** No se ejecuta el setup desde día 1. Arrancamos en n8n cloud trial gratis. VPS se reabre si: (a) trial se acaba (b) necesitamos community nodes que cloud bloquea (c) volumen supera trial limits. Runbook `hostinger-vps-n8n-setup.md` se mantiene en repo como referencia, pero no es Fase 0/1 obligatorio.

### Cambio 4 — Inflection Lever Track en paralelo con Fase -1 (decisión 4b)

**Antes:** plan asumía growth por viralidad orgánica + Telegram HITL. Sin work stream explícito de partnerships/PR/cross-promo.

**Ahora:** **Inflection Lever Track** como work stream paralelo a Fase -1 (NO antes, NO después — en paralelo).

**Justificación (Report 03):** 9 de 11 creators del dataset escalaron por canal externo (ChatGPT moment para DotCSV, reseña aerolínea para Sofía Macías, inversor con red para MPF, fichaje Ramsey para Andrés Gutiérrez, partners con red para EES, Top Voice LinkedIn para Startupeable, pandemia para MPF). Sin lever externo, prob de 10K en 12m baja a 25-30%; con lever, sube a 45-65%.

**Estructura del track:**
- Lista inicial de 20 prospects (creators finanzas LATAM, podcasts finanzas, newsletters Cenital/Mis Propias Finanzas/Startupeable, medios LATAM tech, brokers Cocos/IOL/GBM con programa partner, fintechs Ualá/Nubank/Mercado Pago).
- 5 outreaches/semana desde Mes 1 de Fase -1 (no esperar a Fase 1).
- Primer hit cerrado objetivo Mes 2.
- Bandwidth asignado: 2-3 hs/semana Manuel.

### Cambio 5 — Voice clone diferido (decisión 5c)

**Antes (ADR-008):** voice clone 100% ElevenLabs ($22/mo), grabación 20 min pendiente, activación Fase 2.

**Ahora:** decisión final voice clone **diferida hasta que Fase 2 esté inmediata** (Manuel a 30 días de arrancar reels).

**Por qué:**
- Report 05: TikTok ya auto-etiqueta AIGC con voice clone realista. Voice clone obligará disclosure por plataforma.
- Pivot nicho a finanzas refuerza la importancia de "autoridad personal" — Manuel narrando directo puede sumar credibilidad vs voz AI.
- ElevenLabs deal 50% off primer mes ($11) sigue disponible cuando se active.

**ADR-008 → DEFERRED.** No se invalida, se pausa. Decisión final cuando estemos a 30 días de Fase 2 con data de qué necesita el pipeline.

### Cambios cross-cutting derivados

| Documento | Cambio | Razón |
|---|---|---|
| `docs/ROADMAP.md` | v5 — Inflection Lever Track + métricas reset 10K/30-50K/100K + stack SaaS | Cambios 1+3+4 |
| `docs/STACK.md` | v4 — reemplazar Upload-Post por ContentStudio+Blotato, deferir Hostinger VPS | Cambio 3 |
| `docs/COSTS_6MO.md` | recalcular Fase 1 con SaaS stack | Cambio 3 |
| `projects/dinero-ia/brand_voice.md` | v3 — nicho finanzas + voz adaptada + benchmarks reset | Cambios 1+2 |
| `projects/dinero-ia/sources.yaml` | sumar fuentes finanzas LATAM | Cambio 2 |
| `projects/dinero-ia/risk_profile.yaml` | agregar compliance financiero LATAM | Cambio 2 |
| `projects/dinero-ia/prompts/a9-compliance.md` | reglas asesor financiero (15 → 18 reglas) | Cambio 2 |

### Sub-decisiones de Manuel (2026-05-29)

| # | Sub-decisión | Respuesta | Implicación |
|---|---|---|---|
| A | Renombrar carpeta proyecto | Default: dejar `projects/dinero-ia/` | Cambia contenido nomás; rename físico cuando haya handle/dominio decidido |
| B | Alcance pivot finanzas | B.1 — vertical único | Foco fuerte; expansión (marketing/ops) se reabre si llegás a 10K |
| C | Posicionamiento compliance | C.1 — educativo, no asesoría | Disclaimer claro; permite mencionar Cocos/IOL/GBM con contexto. Modelo Sofía Macías. |

### Status de ADRs previos tras ADR-017

| ADR | Status post-ADR-017 |
|---|---|
| ADR-001 a ADR-007 | Sin cambio (Project Autopilot) |
| ADR-008 (voice clone) | **DEFERRED** — decisión final cuando Fase 2 esté a 30 días |
| ADR-009 (n8n stack) | **MODIFICADO** — n8n rol reducido a solo moat editorial (scorer + fact-check + Telegram) |
| ADR-010 (ángulo generalista) | **SUPERSEDED** por ADR-016 + ADR-017 (ahora AI × Finanzas) |
| ADR-011 (1 post/día Fase 1) | Sigue vigente |
| ADR-012 (publisher) | **SUPERSEDED** por ADR-017 (publisher = ContentStudio + Blotato) |
| ADR-013 (gpt-image-2) | Sigue vigente — Blotato usa gpt-image-2 internamente, mismo modelo |
| ADR-014 (Upload-Post) | **SUPERSEDED** por ADR-017 |
| ADR-015 (Hostinger VPS) | **DEFERRED** — runbook se mantiene, no se ejecuta hasta que aplique |
| ADR-016 (pivot estratégico) | **EXTENDIDO** por ADR-017 (3 layers nuevas: target, stack, lever) |

### Riesgos de ADR-017

1. **Re-trabajo conceptual:** brand_voice + sources + risk_profile + a9 requieren reescritura significativa. Estimado: 1-2 sesiones de Claude + revisión de Manuel.
2. **Pérdida de momentum:** segundo pivot grande en 11 días. Riesgo de "parálisis por análisis". Mitigado por la claridad de Fase -1 con métricas Go/No-Go.
3. **Compliance financiero LATAM:** nuevo eje de riesgo. Mitigado por C.1 (educativo) + disclaimer en cada pieza + no recomendar valores específicos.
4. **Stack SaaS bloquea customization:** ContentStudio + Blotato son cajas más cerradas que n8n custom. Si el moat editorial necesita feature que el SaaS no expone, bloqueante. Mitigado por mantener n8n para el moat.
5. **Carpeta `dinero-ia/` confunde:** el nicho ya no es "AI Brief" ni "AI How-To" sino "AI × Finanzas". Mitigado por nota explícita en docs + decisión de rename cuando haya nombre nuevo.

### Acciones de este ADR (concretas)

- [x] Documentar ADR-017
- [x] Update `docs/ROADMAP.md` → v5 con Inflection Lever Track + métricas reset + stack SaaS
- [x] Update `docs/STACK.md` → v4 con nuevo stack SaaS
- [x] Update `docs/COSTS_6MO.md` con nuevo stack
- [x] Update `projects/dinero-ia/brand_voice.md` → v3 nicho finanzas
- [x] Update `projects/dinero-ia/sources.yaml` con fuentes finanzas LATAM
- [x] Update `projects/dinero-ia/risk_profile.yaml` con compliance financiero
- [x] Update `projects/dinero-ia/prompts/a9-compliance.md` con reglas asesor financiero

### Acciones deferred

- [ ] Decidir nombre/handle/dominio del proyecto (Manuel cuando tenga claridad)
- [ ] Rename físico de carpeta `projects/dinero-ia/` cuando se decida nombre
- [ ] Lista concreta de 20 prospects para Inflection Lever Track (Manuel + Claude próxima sesión)
- [x] Decisión final voice clone → ADR-018 (activa Fase 1 con voice library, swap a clone Manuel post-grabación)

---

## ADR-018 — Pivot a video-first pipeline + voice clone activa desde día 1

**Fecha:** 2026-06-01
**Status:** Aceptada (Manuel decisión 2026-06-01)
**Scope:** Dinero IA — pipeline producción
**Supersedes parcial:** ADR-008 (voice clone deferred → ACTIVA), ADR-013 (gpt-image-2 sigue pero ahora como input a Seedance, no carouseles)
**Trigger:** Manuel pidió rediseño tras smoke test exitoso del moat editorial. Reels son el formato dominante LATAM 2026 (algoritmo IG/TT prioriza video 2-3x sobre carousel).

### Contexto

ADR-017 estableció Fase 1 = texto + carouseles + newsletter, con voice clone DIFERIDO a Fase 2. Smoke test del moat editorial (A2 + A3 + A9 + Telegram) corrió con éxito 2026-06-01. Manuel evaluó el avance y pidió rediseño:

> "Estos posts tienen que ser videos. Necesito una generación de videos. Seedance 2.0 más generación de imágenes de ChatGPT al mismo tiempo. Van a necesitar algo de música de fondo y mi voz. Como dice el master plan, habíamos quedado que para mi voz íbamos a usar ElevenLabs."

Esto cambia el pipeline desde la base: ya no es "carousel-first con reels en Fase 2" sino "reels-first con carousel opcional".

### Decisión

**Pipeline Fase 1 v2 = video-first** con los siguientes componentes nuevos:

| Agent | Función | Tool | Output |
|---|---|---|---|
| **A5 Visual Director** | Genera prompts de imagen + storyboard de 5-8 keyframes | Claude Opus 4.6 | JSON con prompts gpt-image-2 + timing |
| **A6 Audio Director** | Genera SSML del script + pacing + mood música + voice settings ElevenLabs | Claude Opus 4.6 | JSON con script SSML + voice_settings + music_brief |
| **A7 Script Composer** | Brief A3 → script reel 25-35s + caption IG/TT/LI + sección newsletter | Claude Opus 4.6 | JSON con todos los formatos |
| **A8a Image Gen** | Genera 5-8 keyframes editoriales `#0F0F10` + Inter + JetBrains Mono | OpenAI gpt-image-2 | PNG 1080×1920 (formato reel vertical) |
| **A8b Video Gen** | Anima keyframes → video continuo con transiciones | Seedance 2.0 | MP4 sin audio, 25-35s |
| **A8c Voice Gen** | Genera audio narrado con voice clone Manuel (o voice library en arranque) | ElevenLabs Creator | MP3 con SSML pacing |
| **A8d Music Selection** | Selecciona track stock según mood A6 | Epidemic Sound / Artlist API (o biblioteca curada local) | MP3 track |
| **A8e Compositor** | Mezcla video + voz + música + subs → MP4 final 9:16 | FFmpeg en n8n Code node | MP4 1080×1920 listo |

**Stack actualizado:**

| Componente | Estado pre-ADR-018 | Estado post-ADR-018 |
|---|---|---|
| Anthropic API | ✅ | ✅ + más volumen (A5, A6, A7 nuevos) |
| OpenAI gpt-image-2 | Backup visual | **Core:** genera keyframes para Seedance |
| Seedance 2.0 | DIFERIDO Fase 2 | **ACTIVA Fase 1** |
| ElevenLabs Creator | DIFERIDO Fase 2 | **ACTIVA Fase 1** (voice library al inicio, clone Manuel post-grabación) |
| Música stock | NO en plan | **NUEVA** (Epidemic Sound / Artlist) |
| Blotato (carouseles) | Core publishing | **Opcional secundario** (carousel solo si format_recomendado=carousel) |
| ContentStudio | Publish a IG/TT/LI/X | ✅ ahora publish video reels |
| Beehiiv | Newsletter | ✅ sin cambios |
| Supabase Storage | NO en plan | **NUEVA:** bucket para keyframes/audio/video |

### Voice clone — strategy híbrida (resuelve ADR-008)

**ADR-008 status:** SUPERSEDED por ADR-018.

Implementación 2 fases:
- **Fase 1.0 (arranque):** ElevenLabs voice library — voz español neutro LATAM masculina pre-existente. Calidad alta sin requerir grabación. Permite arrancar HOY sin bloqueo.
- **Fase 1.1 (Manuel graba):** swap a voice clone Manuel (20-30 min grabación). Un solo cambio en A8c voice_id parameter.

Razón: evita que la grabación sea blocker.

### Consecuencias — costos

- ElevenLabs Creator: +$22/mo
- Seedance 2.0 (60-90 videos/mo × $1.50): +$90-135/mo
- Música stock: +$13-22/mo
- gpt-image-2 más volumen: +$10-17/mo
- Anthropic con A5+A6+A7: +$30-50/mo
- **Total delta vs ADR-017:** +$165-246/mo
- **Total Fase 1 con video:** ~$270-440/mo (vs $130-180 ADR-017)

### Riesgos aceptados

1. **Compliance:** TikTok auto-etiqueta AIGC con voice. Disclosure en A9.
2. **Calidad Seedance:** animación de keyframes ≠ grabación real. Mitigación: keyframes con composición simple, no escenas complejas.
3. **Costo:** sube significativamente. Manuel aceptó el rango.
4. **Voice clone diferida 2 semanas:** primeros videos con voz library. Mitigación: calidad ElevenLabs library indistinguible para audiencia general.

### Acciones de este ADR

- [x] Documentar ADR-018
- [ ] Deep Research Top 12-15 performers US+LATAM (Agent en curso 2026-06-01)
- [ ] Standards docs: VISUAL, VOICE, MUSIC, POSTING (post-research)
- [ ] Workflow JSON `infra/n8n/dinero-ia-fase1-publish-v2.json` con A5-A8e
- [ ] Migration SQL `002_video_assets.sql` con tabla `assets_storage`
- [ ] Runbook ElevenLabs + Seedance setup
- [ ] Script de grabación de voz Manuel (`docs/voice-clone/recording-script.md`)
- [ ] Update ROADMAP a v6

---

## ADR-019 — Cadencia 2-3 posts/día + horarios LATAM diversificados + anti-canibalización

**Fecha:** 2026-06-01
**Status:** Aceptada (Manuel decisión 2026-06-01)
**Scope:** Dinero IA — operación
**Supersedes parcial:** ADR-011 (1 post/día → 2-3 posts/día)
**Trigger:** Manuel pidió "2 o 3 posts al día con información bien validada" como cadencia objetivo Fase 1.

### Contexto

ADR-011 estableció 1 pieza/día Fase 1 para validar antes de escalar. Con el rediseño video-first (ADR-018) y la prioridad "máximo nivel + automatizado", Manuel define cadencia 2-3 posts/día desde el inicio Fase 1.

### Decisión

**Cadencia objetivo:** 2-3 posts/día con diversidad obligatoria.

**Slots horarios por país** (basados en cuándo audiencia LATAM scrollea):

| Slot | Hora MX (CST) | Hora AR (ART) | Hora CO (COT) | Sub-categorías sugeridas |
|---|---|---|---|---|
| **Slot 1 — mañana** | 7:00 AM | 9:00 AM | 7:00 AM | Educativo + analítico: inversiones, comparativas |
| **Slot 2 — mediodía** | 12:30 PM | 2:30 PM | 12:30 PM | Práctico accionable: presupuesto, prompts, herramientas |
| **Slot 3 — tarde-noche (solo si 3/día)** | 7:00 PM | 9:00 PM | 7:00 PM | Tendencia + viral: noticias IA, inflación AR/MX, polémicas |

**Reglas anti-canibalización:**

1. **Diversidad de sub-categoría obligatoria:** los posts del mismo día NO pueden ser de la misma sub_categoria. Si dos items top tienen sub_categoria='inversiones', el segundo se desplaza al día siguiente.
2. **Diversidad de fuente:** los posts del mismo día NO pueden ser de la misma `source_name`. Bloomberg Línea + Cenital en distintos slots, OK. Dos de Bloomberg no.
3. **Diversidad de formato:** preferir alternar reel + reel + carousel en 3-post days, no 3 reels seguidos.

**Dedup robusto:**
- `dedup_history` ya implementada (URL-level)
- **Nuevo:** `topical_dedup` — keyword extraction sobre `que_paso` evita 2 piezas sobre el mismo evento

**Cron schedule en n8n:**
- 3 cron triggers separados (Slot 1, 2, 3) en vez de un único cron
- Cada trigger ejecuta workflow Fase 1 publish con `slot_id` parameter
- A2 Scorer filtra items según `slot_preference` matcheado con sub_categoria

### Consecuencias

**Volumen producción:** 60-90 posts/mes (vs 30 en ADR-011). 2-3x impact en costos LLM + Seedance.

**Calidad vs velocidad:** Manuel explicitó "no importa si no publico esta semana, lo que me interesa es que logre un producto final muy bueno". Por lo tanto:
- NO publicar si no hay 2-3 items que pasen score≥65 + compliance
- Mejor 1 día con 0 posts que 1 día con 3 posts mediocres
- A2 Scorer umbral sube de 60 a **65** para asegurar calidad mínima superior

**HITL bandwidth:** 2-3 previews/día en Telegram. Manuel debe estar disponible para aprobar/editar. Mitigación: timeout HITL = 4h sin respuesta, auto-postpone al día siguiente (no auto-reject).

### Acciones de este ADR

- [x] Documentar ADR-019
- [ ] Update workflow Fase 1 v2: 3 cron triggers + slot_id parameter
- [ ] Implementar `topical_dedup` en code node (keyword extraction sobre que_paso)
- [ ] Update A2 Scorer prompt: umbral 65 + slot_preference matching
- [ ] Update SQL: agregar `slot` column a `briefs_pending` (parte de migration 002)
- [ ] Actualizar Compliance prompt para considerar anti-canibalización
- [ ] Update ROADMAP a v6 con cadencia 2-3/día
