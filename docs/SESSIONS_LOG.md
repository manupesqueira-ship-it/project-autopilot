# Sessions Log — AI Brief LATAM

> Bitácora narrativa. Una entrada por sesión de trabajo.

## 2026-05-07 — Día 1: Setup inicial

**Qué hicimos:**
- Migración del repo a arquitectura v2 multi-property (`.cursorrules` + README + .gitignore actualizados).
- `PROJECT_STATE.md` introducido como living state tracker.
- 3 research files iniciales producidos y aplicados:
  - `format-and-voice-research.md` (Smart Brevity + Morning Brew + Reels length data)
  - `latam-specific-research.md` (7 hallazgos LATAM: emojis sí, comunidad como código cultural, español neutro, multi-channel funnel)
  - `production-stack-research.md` (5 dimensiones: faceless vs talking head, voz humana vs AI, acento, Canva vs CapCut, "no AI look" constraint)
- `brand_voice.md` consolidado a partir de los 3 research, incluyendo voice/accent rules (CDMX neutralizado).
- 9 competitive analyses producidas en `research/competitive/` (Rundown AI, Superhuman, Neuron, Ecosistema Startup, Startupeable, Digital Brain, DotCSV, Nicolas Abril + consolidación de patterns).
- `PRODUCTION_STACK.md` lockeado: Inoreader + Claude Pro + Canva Pro + Beehiiv = ~$15/mo MVP.
- Audit de `core/` + `docs/` heredados de MIRA (qué sirve, qué se archiva).
- 6 pieces preliminares draft (#001 Anthropic Wall Street, #002 Corgi insurtech, #003 Google Mariner, #004 Anthropic×SpaceX, #005 Uber×OpenAI, #006 Claude Code vs Codex).
- En la noche del 7 al 8, comenzó el build de Python agents (source_monitor M1-M5, signal_scorer, editorial, fact_checker, content_composer, compliance).
- `voice-clone/recording-script.md` para setup futuro de ElevenLabs.

**Decisiones tomadas:**
- Stack producción $15/mo: Inoreader Free + Claude Pro + iPhone Voice Memos + Canva Pro + Beehiiv Free.
- Voz editorial: Smart Brevity + Morning Brew casual sobrio.
- Idioma: español neutro LATAM. Blacklist explícita peninsular + extremos regionales.
- Faceless con texto en pantalla + B-roll + voz humana de Manuel (acento CDMX neutralizado).
- Reels 25-35 seg con hook brutal en primeros 3 segundos.
- Caption <150 chars, 1-2 emojis estratégicos máximo.
- Hooks framework Rufusocial: atención + tensión + promesa.
- Saves > follows como métrica madre en algoritmo 2026.
- Beehiiv como activo central (newsletter), IG como uno de varios canales de adquisición.

**Pivots / cambios de rumbo:**
- Ninguno significativo. Día de setup según plan v2.

**Learnings:**
- Sample LATAM benchmarks anclados: 1K=base, 5K=niche, 12-30K=top tier (Ecosistema Startup, Startupeable), 100K+=excepcional (DotCSV, Nicolas Abril, individuales con años), 400K+ no existe equivalente regional. Target realista AI Brief LATAM = 12-30K en 12-18 meses.
- "Comunidad" pega más que "audiencia" o "lectores" en LATAM (código cultural).
- Tagline formula probada: VALOR + TIEMPO + IDIOMA/REGIÓN + PRECIO.
- Pure AI-generated content tiene penalty -15 a -80% reach (label "Made with AI"); AI-asistido NO requiere label.

---

## 2026-05-08 — Día 2: Construcción 9 agents Python + research deep

**Qué hicimos:**
- 9 agents Python construidos end-to-end con 98 tests passing (0 fails):
  - source_monitor (34 tests) — 12 RSS sources + Anthropic Blog scraping + dedup 30d + scoring heurístico 90 keywords
  - signal_scorer (12) — LLM scoring con rubric 8 categorías Anexo B
  - editorial (11) — briefs Smart Brevity + ángulo LATAM
  - fact_checker (9) — verifies claims con 4 severidades
  - content_composer (7) — carousel 5-7 slides + caption <150 + newsletter + reel script
  - compliance (9) — Meta rules + brand voice + forbidden patterns
  - human_approval (6) — Interactive CLI + auto-approve, no LLM
  - publisher (5) — export files + evidence chain tracing
  - analytics (5) — pipeline metrics + cost tracking
- 6 deep research procesados:
  1. social-media-niches-2026
  2. fintech-insurtech-crypto-latam
  3. multi-agente-instagram-automation (marcado como antiejemplo)
  4. creators-ia-espanol-landscape
  5. multi-agent-frameworks
  6. rundown-ai-business-model
- 6 análisis críticos individuales (con bias assessment y reliability rating).
- 3 syntheses producidas: `2026-05-08_synthesis.md`, `_master-plan-deltas.md` (16 deltas round 1 + 11 deltas round 2 = 27 total), `_application-roadmap.md`.
- Upgrade a Claude Opus 4 para todos los LLM calls.
- Voice clone recording script preparado.
- End-of-day audit: `docs/AUDIT_2026-05-08.md`.

**Decisiones tomadas:**
- Rubric 8 categorías Anexo B confirmada (relevancia LATAM, novedad, urgencia, credibilidad fuente, potencial educativo, potencial viral, fit marca, riesgo penalty).
- 12 fuentes RSS iniciales + Anthropic Blog selective scraping.
- Threshold scoring 5.0 para keyword gate (configurable).
- Dual revenue stream (sponsorships + paid tier ~$500-$1K/yr) como modelo target Fase 8 — insight más importante del round 2.
- Engagement automation (auto-replies, auto-DMs) permanentemente fuera de scope.
- Visual generation: 0% AI generation primary (mantener faceless con stock + texto + voz humana en ese momento).
- Construcción lineal de los 9 agents siguiendo Anexo del MASTER_PLAN.

**Pivots / cambios de rumbo:**
- Ninguno mayor — construcción lineal sobre Python según plan.

**Learnings:**
- De los 27 deltas propuestos, la mayoría son **refuerzos**, no pivotes — el MASTER_PLAN estaba bien anclado.
- El research multi-agente Instagram **contradice frontalmente** el MASTER_PLAN (HITL opcional, AI generation primary, n8n nuevo). Marcado como antiejemplo documentado.
- El research multi-agent frameworks dice: el caso AI Brief LATAM está **en frontera** multi/single agent. Recomienda single-agent + tools antes de framework formal.
- The Rundown AI playbook deep dive: dual revenue stream **50/50 sponsorships + paid product $999/yr** duplica LTV. $10M ARR + bootstrapped + 12 employees + $833K rev/empleado.
- Solo 2 de los 4 archivos de research del primer batch coincidían con los temas previstos — research a veces vuelve con cosas distintas a lo pedido, vale procesarlas igual.

---

## 2026-05-10 — Día 3: Pivot técnico mayor

**Qué hicimos:**
- Primer post real publicado (output mediocre — el sistema técnico funciona pero el contenido no rivaliza con benchmarks profesionales).
- **Decisión de pivot:** abandonar Python custom, migrar a n8n cloud.
- Reset del repo: 9 agents Python movidos a `legacy/python-mvp-2026-05-10/`.
- `MASTER_PLAN.md` decompuesto en 5 docs nuevos:
  - `docs/STACK.md` — herramientas y costos
  - `docs/SYSTEM_DESIGN.md` — arquitectura de 11 agents
  - `docs/AGENTS_SPEC.md` — specs técnicos por agent
  - `docs/AUTOMATION_ARCHITECTURE.md` — diseño del flow automatizado
  - `docs/ROADMAP.md` — 4 fases con DoD
- 11 agents redefinidos (no 9) como n8n nodes/sub-workflows: A1 source_monitor → A2 signal_scorer → A3 editorial → A4 fact_checker → A5 visual_director → A6 audio_director → A7 copy_composer → A8(a/b/c/d) content generators → A9 compliance → A10 publisher → A11 analytics.
- Decisiones operativas: 1 post/día (no 3), gpt-image-2 como primario, voice clone 100% ElevenLabs.

**Decisiones tomadas:** ver `docs/DECISIONS.md` (ADR-008 a ADR-013 — set AI Brief LATAM).

**Pivots / cambios de rumbo:**
- **Python custom → n8n cloud + Anthropic node nativo** (ADR-009).
- **9 agents → 11 agents** — n8n permite separar A8 en A8a/b/c/d sin overhead arquitectural.
- **3 posts/día → 1 post/día** Fase 1 — validar antes de escalar (ADR-011).
- **Pillow image generation → gpt-image-2** — output mediocre forzó el upgrade (ADR-013).
- **Voz humana primaria + ElevenLabs backup → voice clone 100% ElevenLabs** — automatización total Fase 2+ (ADR-008, contradice brand_voice.md de 2026-05-07).

**Learnings:**
- **Construir sistema antes de definir editorial = output genérico.** Los 9 agents Python eran técnicamente correctos pero producían content sin alma porque el ángulo editorial no estaba lo suficientemente afilado.
- **El primer post real es más informativo que 27 deltas teóricos.** La iteración requiere materializar antes de optimizar.
- **Stack custom no rivaliza con tools profesionales.** La industria estandarizó n8n + Claude + gpt-image-2 + Buffer/Blotato — competir con eso es esfuerzo perdido.
- **Decompose MASTER_PLAN en docs especializados** es mejor que un monolito de 800 líneas. Cada doc tiene un owner conceptual claro.
- **Deltas como propuestas, no compromisos.** De los 27 deltas previos, varios quedaron SUPERSEDED por la decisión n8n (#17, #22, contradicción #10 del addendum).

---

## 2026-05-11 — Día 4: Research n8n templates + cierre operacional

**Qué hicimos:**
- Research de 16 n8n templates verificables (`2026-05-11_n8n-templates-research.md`).
- Marcado de deltas SUPERSEDED en synthesis/deltas con banner explicativo.
- Edits a `docs/STACK.md` (Buffer → Blotato/Upload-Post/Buffer fallback) y `docs/ROADMAP.md` (tarea preliminar Fase 1: importar 5 templates).
- Stubs creados: `n8n-templates-notes.md` (bitácora de import) + `DECISIONS.md` (6 ADRs) + este `SESSIONS_LOG.md`.

**Decisiones tomadas:**
- Combinación recomendada de templates: #12533 + #6389 + #4399 + #4028 + (#9472 o #5773) ≈ 70-75% del pipeline.
- Anthropic SÍ tiene node oficial nativo en n8n (no era solo HTTP Request) — desmiente la asunción del plan original.
- Buffer es fallback, no primario, hasta que se evalúen Blotato y Upload-Post (ADR-012).

**Pivots:** ninguno — refinamiento operacional.

**Learnings:**
- n8n cloud NO tiene free tier permanente (solo trial 14 días). Starter €20-24/mes es el mínimo viable. Alternativa: self-hosted en Hostinger VPS €5-7/mes.
- Buffer GraphQL para carousel IG es **unwalked path** — único ejemplo público con 0 stars. Es riesgo técnico real.
- gpt-image-2 confirmado live desde 2026-04-21, pero todos los templates 2026 todavía apuntan a gpt-image-1 → swap manual obligatorio.
- "3 months ago" timestamp en todo el catálogo n8n.io sugiere re-indexing batch, no es signal confiable de freshness.
