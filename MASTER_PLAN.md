# MASTER PLAN v2 — Project Autopilot

**Sistema multi-agente para construir y operar un portafolio de propiedades de medios digitales en Latinoamérica.**

- **Versión:** 2.0
- **Reemplaza:** Master Plan v1 (que asumía MIRA como caso de uso primario)
- **Fecha:** Mayo 2026
- **Owner:** Manuel Pesqueira
- **IDE principal:** Cursor (dos ventanas: una por repo)
- **Builders externos orquestados:** Claude Code, Codex, Cursor agente
- **Plataformas operadas:** Instagram (3 cuentas), Beehiiv (3 newsletters), web/app consumer (Fase 7+)

---

## 0. Resumen ejecutivo

Project Autopilot es un sistema operativo de agentes para construir, operar y escalar un portafolio de tres propiedades de medios LATAM:

1. **AI Brief LATAM** (priority #1) — IA para founders, operadores y profesionales de la región.
2. **Crypto Brief LATAM** (priority #2) — Stablecoins, regulación y adopción real, sin trading ni hype.
3. **Startup Radar LATAM** (priority #3) — Inteligencia ejecutiva sobre venture, founders, M&A regional.

El sistema **NO** es un app builder genérico ni un reemplazo de Cursor/Claude Code/Codex. Es una capa de **control + producción de contenido + análisis** donde los agentes hacen el trabajo pesado (research, draft, fact-check, copy, diseño, compliance) y vos sos el editor jefe que aprueba antes de publicar.

Tres reglas que ordenan todo el plan:

1. **Manual antes que automatizado.** Mínimo 3 semanas operando AI Brief a mano antes de que Autopilot ejecute nada por su cuenta.
2. **Una property antes que tres.** Crypto y Startup esperan a que AI Brief tenga señales claras de tracción.
3. **Human-in-the-loop sobre cada publicación.** Ningún post sale sin aprobación tuya hasta que el sistema tenga track record verificable.

Plazo total estimado a Fase 6 (las 3 properties operativas con automatización sólida): **4 a 6 meses** de trabajo enfocado.

---

## 1. Cambios desde v1

| Aspecto | v1 | v2 |
|---|---|---|
| Propósito | Control plane genérico | Sistema multi-agente para portafolio de medios LATAM |
| Caso de uso primario | MIRA (try-on app) | AI Brief LATAM (Instagram + newsletter) |
| Estado de MIRA | Project #2 / test case | Snapshot congelado, no sprints activos |
| Tipo de tareas | Bug fixes, features, refactors de código | Research, briefs, copy, diseño, compliance, publishing |
| Output esperado | Code commits | Posts, carruseles, reels, newsletters |
| Builders externos | Claude Code, Cursor, Codex | Mismos + APIs de plataformas (Beehiiv, Buffer, Meta) |
| Primera tarea de validación | Email validation en MIRA onboarding | Brief de IA producido end-to-end por el pipeline |
| Cantidad de "projects" | 1 (mira) | 3 (ai-brief-latam, crypto-brief-latam, startup-radar-latam) |

**MIRA queda como snapshot histórico congelado.** El repo `mira` (post-split) se mantiene como referencia. No recibe sprints. Se extrae código solo si es genuinamente reusable para Autopilot. Los hallazgos del audit de Supabase quedan archivados para reusar el aprendizaje cuando se diseñe la capa de datos del producto consumer en Fase 7.

---

## 2. Arquitectura — 3 capas

Esta es la idea más importante del plan. Si solo te llevás una cosa, es esta.

```
┌──────────────────────────────────────────────────────────────┐
│  CAPA 3 — PROPERTIES (los proyectos)                         │
│                                                              │
│  ai-brief-latam │ crypto-brief-latam │ startup-radar-latam   │
│  Cada una con: config propia, voz, fuentes, risk profile,    │
│  cadencia, audiencia, monetización.                          │
└──────────────────────────────────────────────────────────────┘
                              ▲ corre sobre
┌──────────────────────────────────────────────────────────────┐
│  CAPA 2 — CONTENT PRODUCTION AGENTS (apps)                   │
│                                                              │
│  Source Monitor → Signal Scorer → Editorial → Fact-Check →   │
│  Composer → Compliance → Approval → Publisher → Analytics    │
│                                                              │
│  Estos agentes son aplicaciones que orquestan el contenido.  │
│  Su comportamiento se modula por la config de cada property. │
└──────────────────────────────────────────────────────────────┘
                              ▲ corre sobre
┌──────────────────────────────────────────────────────────────┐
│  CAPA 1 — CONTROL PLANE (kernel — lo que ya tenés en core/)  │
│                                                              │
│  Intake → Planner → Composer → Builder → QA → Auditor →      │
│  Policy Engine → Evidence Recorder                           │
│                                                              │
│  Genérico, agnóstico al dominio. Maneja: scheduling,         │
│  evidencia, costos, errores, retries, secrets, audit log.    │
└──────────────────────────────────────────────────────────────┘
```

**Lo importante:** los 25 agentes que mencionaste en tu doc viven en CAPA 2. **No reemplazan al control plane (capa 1). Son aplicaciones que corren sobre él.**

Beneficios de esta separación:

- Si más adelante querés usar Autopilot para algo distinto a media (un SaaS, un bot, un asistente B2B, lo que sea), la capa 1 sirve. Solo cambiás la capa 2.
- Si querés cambiar la voz de Crypto Brief sin tocar el Editorial Agent, lo hacés en capa 3.
- Si querés un Financial Risk Agent estricto solo para Crypto, va en capa 2 con config "activo solo si property == crypto-brief-latam".
- El control plane garantiza siempre: nada se publica sin aprobación, todo cambio queda auditado, todo costo está trackeado, ningún secret se filtra.

---

## 3. Las 3 properties — definición inicial

### 3.1 ai-brief-latam (priority #1, primera en operación)

**Propósito:** Hacer accionable el ecosistema de IA para profesionales, founders y empresas de LATAM.

**Audiencia:** Founders, operadores, consultores, freelancers, profesionales de empresa que quieren usar herramientas reales antes que la masa.

**Voz de marca:** Práctica, sobria, anti-humo, técnicamente precisa, accesible. NO entusiasta ingenuo, NO "esta IA va a cambiar el mundo". SÍ "esto sirve para X, esto no, así se usa, así no se usa".

**Fuentes iniciales (target 15-25):** OpenAI/Anthropic/Google/Meta blogs oficiales, Hacker News, Andrew Ng's The Batch, AI Snake Oil, Latent Space, MLOps Community, Product Hunt (filtros AI), GitHub trending (AI repos), arXiv (selectivo), TechCrunch AI, The Information AI, Stratechery, plus LATAM-specific (Bloomberg Línea Tech, Contxto, LatamList, Forbes Latam Tech).

**Cadencia inicial (Manual MVP):** 3-5 piezas por semana en Instagram, 1 newsletter weekly.

**Risk profile:** Bajo. Riesgos principales: información imprecisa sobre lanzamientos (verificar siempre fuente oficial), confundir rumor con hecho, exagerar capacidades de herramientas.

**Compliance especial:** Cuando se reseñan herramientas, no hacer claims que no se puedan verificar. Distinguir explícitamente entre "anuncio", "lanzamiento", "rumor" y "análisis".

### 3.2 crypto-brief-latam (priority #2)

**Propósito:** Cobertura crypto seria para LATAM enfocada en stablecoins, regulación, adopción real, seguridad. Anti-trading, anti-hype, anti-shilling.

**Audiencia:** Profesionales y empresarios LATAM que necesitan entender stablecoins, remesas, regulación y oportunidades reales sin caer en scams.

**Voz de marca:** Extremadamente sobria, defensiva contra scams, educativa, conservadora. Cero entusiasmo gratuito. Cero "to the moon". Cero promesas.

**Fuentes iniciales (target 15-25):** Chainalysis, Coin Metrics, The Block, CoinDesk, Bitcoin Magazine, Messari, regulatory feeds (CNV Argentina, CNBV México, CMF Chile, etc.), exchanges con presencia LATAM (Bitso, Lemon, Ripio), Bloomberg Crypto, Reuters Crypto.

**Cadencia inicial:** 2-3 piezas por semana, 1 newsletter weekly.

**Risk profile:** ALTO. Esta property necesita un **Financial Risk Agent dedicado** con reglas estrictas:
- NUNCA recomendar comprar o vender activos
- NUNCA prometer rendimientos
- NUNCA promover monedas específicas como inversión
- SIEMPRE incluir riesgos
- SIEMPRE incluir disclaimers ("no es asesoría financiera")
- Citar siempre fuente oficial

**Compliance especial:** Revisión legal por jurisdicción si se habla de regulación. Cuidar que el contenido no califique como "asesoría financiera" en ningún país LATAM. Disclaimers visibles en cada post de naturaleza informativa-financiera.

### 3.3 startup-radar-latam (priority #3)

**Propósito:** Inteligencia ejecutiva sobre venture, founders, rondas, M&A y nuevas empresas en LATAM.

**Audiencia:** Founders, inversionistas, operadores, consultores, estudiantes top de business schools. Premium positioning.

**Voz de marca:** Analítica, founder-friendly, business-focused, premium pero no arrogante. Más data-driven que inspiracional.

**Fuentes iniciales (target 15-25):** LAVCA, Crunchbase (LATAM filter), Bloomberg Línea, Reuters LATAM, Contxto, LatamList, Forbes Latam, founder twitter/LinkedIn (curated list), VC newsletters (Kaszek, Atlántico, monashees, Kalei, ALLVP).

**Cadencia inicial:** 2-3 piezas por semana, 1 newsletter weekly premium.

**Risk profile:** Medio. Riesgos: verificar valuaciones, no confirmar rumores como hechos, cuidar reputación de founders y empresas.

**Compliance especial:** Citar siempre fuente para rondas, valuaciones, exits. Distinguir claramente "confirmado" vs "reportado" vs "rumor".

---

## 4. Stack tecnológico

### 4.1 Confirmado por vos

- **Newsletter:** Beehiiv (a re-validar después de Fase 1 con uso real). Razón: positioning de media business, deliverability robusta, analytics nativos, monetización integrada.
- **Instagram:** Manual + Buffer/Later/Metricool al inicio. Meta Graph API directa después (requiere cuenta business + app review de Meta — proceso de semanas).
- **Visuales:** Canva templates como base + AI generation (a definir cuál) + revisión humana siempre.
- **Source monitoring:** Manual + RSS via Feedly o Inoreader inicialmente. Scrapers propios solo cuando algo crítico no esté en RSS.

### 4.2 Confirmado por estructura

- **Lenguaje del control plane:** Python (lo que ya tenés en `core/` post-split). No tocar.
- **LLM principal:** Claude (Anthropic API directa) para v1. Más simple y controlable que SDKs intermedios.
- **Estructura de evidencia:** filesystem local, una carpeta por run (`evidence/{run_id}/`).
- **Storage:** local en disco para v1. Migración a algo más serio solo si la operación lo demanda.

### 4.3 Decisiones a tomar durante Fase 1 (no antes)

- **Scheduler:** Buffer vs Later vs Metricool. Probar 1-2 durante el manual MVP, decidir al final de Fase 1.
- **Visual generation:** Midjourney, Recraft, DALL-E vía API, o solo Canva sin AI. Decidir tras 5-10 piezas hechas a mano.
- **Analytics:** Meta Insights API (cuando esté business account aprobada por Meta), o métricas manuales del dashboard al inicio.
- **Fact-checking helper:** Decidir si solo Claude o agregás Perplexity/Tavily/Exa para fuentes en tiempo real.

### 4.4 Diferido (no tocar hasta que aplique)

- App/web consumer product → Fase 7
- Database para usuarios → Fase 7
- Push notifications, mobile app → Fase 7+
- Paid acquisition → Fase 8 (solo si una property pega)
- B2B / sponsorships → Fase 8
- Premium subscription tier → Fase 8
- Cloud / VPS para Autopilot → no hasta tener razón clara (mantener local)

---

## 5. Estructura de archivos del repo `project-autopilot`

Post-split, post-Fase 0, así debería verse:

```
project-autopilot/
├── README.md
├── MASTER_PLAN.md (este archivo)
├── DAILY_OPERATIONS.md
├── ARCHITECTURE.md
│
├── core/                         # CAPA 1 — control plane (heredado del split)
│   ├── intake.py
│   ├── planner.py
│   ├── composer.py
│   ├── policy_engine.py
│   ├── evidence.py
│   ├── (~60 archivos heredados; en Fase 0 se decantan)
│   └── _archive/                 # los que no aplican al nuevo enfoque
│
├── agents/                       # CAPA 2 — content production agents
│   ├── source_monitor/
│   ├── signal_scorer/
│   ├── editorial/
│   ├── fact_checker/
│   ├── content_composer/
│   ├── compliance/
│   ├── financial_risk/           # solo activado por crypto-brief
│   ├── publisher/
│   ├── analytics/
│   └── learning/
│
├── projects/                     # CAPA 3 — properties
│   ├── ai-brief-latam/
│   │   ├── config.yaml
│   │   ├── brand_voice.md
│   │   ├── sources.yaml
│   │   ├── risk_profile.yaml
│   │   ├── compliance_rules.yaml
│   │   └── manual-mvp/
│   │       ├── dashboard.md
│   │       └── pieces/
│   │           └── 2026-05-08_openai-launches-x.md
│   │
│   ├── crypto-brief-latam/
│   │   └── (misma estructura, activa en Fase 5)
│   │
│   └── startup-radar-latam/
│       └── (misma estructura, activa en Fase 6)
│
├── docs/                         # heredado del split (project_control)
│   └── (consolidado en Fase 0)
│
├── evidence/                     # gitignored — output de runs de Autopilot
│
├── .gitignore
├── .cursorrules
└── .env.example
```

---

## 6. Catálogo de agentes (capa 2)

### 6.1 MVP — 9 agentes (Fases 3-5)

| # | Agent | Función | Tipo | Fase |
|---|---|---|---|---|
| 1 | Source Monitor | Lee fuentes, extrae items nuevos, dedupea | Mix (RSS=det / scraping=LLM) | F3 |
| 2 | Signal Scorer | Califica items 0-100 según rubric de la property | LLM | F3 |
| 3 | Editorial | Convierte item alto-score en brief con ángulo | LLM | F4 |
| 4 | Fact-Checker | Verifica claims, fuentes, fechas, números | LLM + tools | F4 |
| 5 | Content Composer | Genera caption + slides de carrusel + sección de newsletter | LLM | F4 |
| 6 | Compliance | Revisa Meta rules, copyright, claims, financial risk | LLM con reglas | F4 |
| 7 | Human Approval | UI para revisar/editar/aprobar/rechazar/programar | UI (CLI o web) | F4 |
| 8 | Publisher | Publica/programa via API o asistido | Determinístico | F4 |
| 9 | Analytics & Learn | Recoge métricas, produce recomendaciones | Mix | F5 |

Estos 9 cubren el flujo end-to-end. Algunos pueden ser stubs (humano haciendo el trabajo) y se automatizan progresivamente. **No hace falta tener los 9 perfectos para empezar a operar.**

### 6.2 Intermedio — 20 agentes (post Fase 6)

Expansión cuando una property tiene tracción y vale la pena especializar:

10. Strategy Director (revisa portfolio completo)
11. Market Research (deep research por vertical)
12. Source Discovery (encuentra nuevas fuentes)
13. Trend Detection (detecta temas emergentes en redes)
14. Scriptwriting (guiones específicos para reels)
15. Design Direction (briefs visuales específicos)
16. Carousel Builder (especializado en formato carrusel)
17. Video Production (especializado en reels)
18. Newsletter Agent (especializado en formato newsletter, separado del Composer general)
19. Brand Voice (asegura consistencia por property)
20. Quality Control (extra layer antes de Approval)

### 6.3 Completo — 25+ agentes (Fase 8+)

Roles full descritos en tu doc original. Se construyen solo si una property específica los demanda. Lista referencial:

- Legal/Copyright (extra capa)
- Monetization (oportunidades de monetización)
- App/Product (features para app consumer)
- Per-vertical research agents (ai-research-agent, crypto-research-agent, etc.)
- Per-platform publisher agents (LinkedIn, X, etc.)
- Crisis/Reputation (manejo de eventos negativos)

**Principio crítico — no negociable:** **NO construir el agente N+1 hasta que la operación demuestre que el N+1 hace falta.** El error histórico de Autopilot fue construir antes de necesitar.

---

## 7. Las fases

### FASE 0 — Cleanup post-split (3-5 días)

**Objetivo:** Cerrar la operación de split, dejar los dos repos limpios y listos en Cursor, archivar MIRA.

Tareas:

1. Esperar a que termine el split actual (Phase 8 del prompt en ejecución).
2. Push a GitHub: `mira` (snapshot histórico, marcar README como "FROZEN — Reference only") + `project-autopilot` (active development).
3. Abrir ambos repos en ventanas separadas de Cursor con sus respectivos `.cursorrules`.
4. Reemplazar MASTER_PLAN.md viejo por este v2 en `project-autopilot/MASTER_PLAN.md`. Subirlo también a Project Knowledge en Claude.
5. Crear `projects/ai-brief-latam/`, `projects/crypto-brief-latam/`, `projects/startup-radar-latam/` con stubs de config (las dos últimas vacías por ahora).
6. Crear `agents/` con README explicando capa 2.
7. Pasada rápida por `core/` (los 60 archivos) y `docs/`: marcar qué sirve para el nuevo enfoque, qué se archiva (subcarpeta `_archive/`), qué se deja como está. **No reescribas nada todavía**, solo clasificá.
8. Primer commit: "Bootstrap v2 architecture: 3-layer model + multi-property structure"

**DoD:** Dos repos en GitHub, ambos abiertos en Cursor con cursorrules apropiados, estructura de carpetas para multi-property creada, MIRA congelado.

### FASE 1 — Manual MVP de AI Brief LATAM (3-4 semanas)

**Objetivo:** Operar AI Brief LATAM completamente a mano durante 3-4 semanas, publicar 12-18 piezas, mandar 3-4 newsletters. **Documentar cada paso como si fuera a automatizarse.**

Esta es **la fase más importante del plan**. Sin ella, todo lo que automatices después va a estar mal calibrado. Se justifica el tiempo aunque parezca lento — vas a aprender más en estas 3 semanas que en 3 meses de construcción anticipada.

**Setup operativo (semana 1, días 1-3):**

1. Crear cuenta Instagram Business para AI Brief LATAM (handle tentativo, no final — el final se decide post-Fase 1 con research de naming).
2. Crear cuenta Beehiiv (free tier OK al inicio).
3. Crear cuenta Buffer (free) o equivalente.
4. Crear cuenta Canva Pro (vale la pena por templates).
5. Configurar fuentes en Feedly o Inoreader (15-25 sources iniciales).
6. Branding mínimo: logo simple, paleta de 3-4 colores, 2-3 templates en Canva. **No perder días en esto.** Lo definitivo se hace después con research de mercado.

**Operación diaria (semanas 1-4):**

- 30-45 min/día revisando fuentes en Feedly
- Selección 1-2 temas por día para trabajar
- Brief escrito a mano (10-15 min)
- Fact-check (10-15 min)
- Composición de post + visual en Canva (30-60 min)
- Publicación o scheduling

**Newsletter weekly:** acumular los temas de la semana, escribir el viernes/sábado, enviar lunes 8am LATAM.

**Documentación obligatoria:** Cada pieza se loggea en `projects/ai-brief-latam/manual-mvp/pieces/{date}_{slug}.md` con la estructura del Anexo C. Esto es inegociable. Una pieza sin log = una pieza que no aporta a la fase.

**DoD:**
- 12-18 piezas publicadas en Instagram
- 3-4 newsletters enviadas
- Cada pieza con su log completo
- Dashboard manual de métricas (Google Sheet o Notion: followers, alcance, engagement, signups, etc.)
- Identificadas las 3 partes más dolorosas/repetitivas del workflow (insumo crítico para Fase 2)

**Trampas a evitar:**
- Pulir el branding antes de publicar (parálisis por análisis).
- Querer automatizar antes de tiempo (no hasta Fase 3).
- Cambiar de stack a mitad (decidí en setup y no cambies hasta Fase 1.5).
- Publicar sin documentar (mata el valor de toda la fase).
- Empezar Crypto o Startup en paralelo (foco total en AI Brief).

### FASE 2 — Documentation Harness Analysis (1 semana)

**Objetivo:** Convertir el output documentado de Fase 1 en specs concretas de automatización.

Tareas:

1. Revisar los 12-18 logs de pieza.
2. Stats agregadas: tiempo promedio por etapa, % de temas rechazados, % que requirieron fact-check externo, etc.
3. Identificar los 3 cuellos de botella más caros en tiempo.
4. Identificar las 3 decisiones más repetitivas (candidatas claras a automatizar).
5. Identificar los errores cometidos (calibración del Compliance Agent).
6. Decidir el primer agente a construir (probable: Source Monitor + Signal Scorer combinados; reduce el cuello de botella diario más obvio).
7. Escribir specs concretos: input, output, criterios de éxito, fallback humano.

**DoD:** Documento `WORKFLOW_ANALYSIS.md` con stats, cuellos de botella identificados, prioridad clara de qué automatizar primero, specs del primer agente.

### FASE 3 — Vertical Slice: Primer agente automatizado (2 semanas)

**Objetivo:** Tener UN agente (Source Monitor + Signal Scorer) corriendo end-to-end por el control plane. Reducir tu trabajo diario de 30-45 min de scanning a aprobar/rechazar una shortlist en 5 min.

Tareas:

1. Implementar `agents/source_monitor/` — lee fuentes RSS, extrae items nuevos, dedupea contra historial.
2. Implementar `agents/signal_scorer/` — califica cada item 0-100 según rubric de la property (Anexo B).
3. Conectar ambos al control plane (intake → composer → policy_engine → evidence).
4. Comando: `autopilot scan --property ai-brief-latam`.
5. Output: shortlist de 5-10 items diarios con score y razones, en formato legible.

**DoD:** Cada mañana corrés el comando, recibís shortlist, elegís en <10 min lo que vas a trabajar. Tu tiempo de scanning baja de 30-45 min a <10 min.

### FASE 4 — Pipeline completo de un brief (3 semanas)

**Objetivo:** End-to-end: desde fuente seleccionada hasta publicación programada, con humano solo en los puntos de aprobación.

Tareas:

1. Implementar `agents/editorial/` — convierte item en brief con ángulo (Anexo A).
2. Implementar `agents/fact_checker/` — verifica claims, anota fuentes, marca dudas.
3. Implementar `agents/content_composer/` — genera caption + slides de carrusel + sección de newsletter.
4. Implementar `agents/compliance/` — revisa Meta rules, copyright, claims (Anexo D).
5. Implementar `agents/human_approval/` — UI mínima (CLI con preview, o página web simple) para aprobar/editar/rechazar/programar.
6. Implementar `agents/publisher/` — usa Buffer API o publishing manual asistido.
7. Calibrar Compliance Agent con reglas específicas de AI Brief (relativamente bajas).

**DoD:** Comando `autopilot brief --property ai-brief-latam --topic <topic-id-from-shortlist>` produce un draft completo en <5 minutos. Vos editás/aprobás en <10 minutos. Se programa publicación. Tiempo total por pieza baja de 60-90 min (Fase 1) a <20 min.

### FASE 5 — Agregar Crypto Brief LATAM (2-3 semanas)

**Objetivo:** Validar la arquitectura multi-property activando la segunda.

Tareas:

1. Repetir Fase 1 en mini: Manual MVP de Crypto Brief, 1 semana, 5-7 piezas. Esto te calibra para la voz crypto.
2. Configurar `projects/crypto-brief-latam/` (config, fuentes, voz, **risk profile estricto**).
3. Implementar `agents/financial_risk/` — agente extra solo para Crypto (Anexo E).
4. Calibrar `agents/compliance/` con reglas Crypto-específicas.
5. Correr el pipeline completo.

**Criterio de validación de la arquitectura:** si una pieza de Crypto pasa el flow sin tocar el código de los agentes existentes (solo config + el nuevo Financial Risk), la arquitectura funcionó.

**DoD:** Crypto Brief operativo con su propio risk profile sin tocar AI Brief. Ambas properties producen contenido aprobado en paralelo.

### FASE 6 — Agregar Startup Radar LATAM (1-2 semanas)

**Objetivo:** Tercera property activa. Si Fase 5 validó la arquitectura, esta debería ser solo configuración + 1 semana de manual MVP.

Tareas:

1. Manual MVP de Startup Radar (1 semana, 5-7 piezas).
2. Configurar `projects/startup-radar-latam/`.
3. Activar pipeline.

**DoD:** 3 properties operativas en producción. Sistema produciendo entre 25-40 piezas por mes en total.

### FASE 7 — App/web consumer product (4-8 semanas)

**Objetivo:** Construir el producto del lado del usuario: signup de newsletter custom, feed personalizado, eventualmente app móvil.

A planear cuando llegue. **No vale la pena specear ahora** porque las decisiones dependen de qué property pega y qué audiencia se forme.

Decisiones a tomar entonces:
- Stack frontend (probablemente Next.js, dado experiencia con MIRA)
- Auth y datos (Supabase o alternativa — acá sí aplican los aprendizajes del Supabase audit de MIRA)
- Tier free vs premium
- Mobile-first o web-first

### FASE 8 — Scale + monetización (ongoing)

**Objetivo:** Crecer la(s) property/properties que pegaron. Premium, sponsorships, B2B.

A planear según señales reales. Posibles tracks:
- Newsletter sponsorships
- Premium subscription tier
- Reportes pagos / research deep-dives
- Comunidad
- Cursos / templates
- B2B intelligence subscription

---

## 8. Manual MVP playbook — la fase crítica

### 8.1 Reglas no negociables de Fase 1

1. **Toda pieza tiene log.** Sin log, no cuenta.
2. **Tiempos reales, no estimados.** Cronometrá cada etapa.
3. **Errores documentados, no escondidos.** Si publicaste algo con un error y lo tuviste que editar, eso va al log. Es la información más valiosa para el Compliance Agent futuro.
4. **No optimices el branding.** Tu obsesión con el visual es enemigo del aprendizaje. Publicás con lo "good enough", iterás.
5. **No publiques sin fuente verificable.** Si no podés citar la fuente original, la pieza no sale.

### 8.2 Workflow diario sugerido (90-120 min total)

| Hora | Actividad | Tiempo |
|---|---|---|
| 8:00 | Review Feedly + tomar notas | 30-40 min |
| 8:40 | Decidir 1-2 temas del día (criterios en Anexo B) | 5 min |
| 8:45 | Brief + fact-check del tema #1 | 25-30 min |
| 9:15 | Composición visual + caption en Canva | 30-45 min |
| 10:00 | Programar en Buffer / publicar | 5 min |
| | **Tiempo total** | **~95-125 min** |

Este tiempo es alto a propósito. La Fase 3 lo reduce a la mitad. La Fase 4 lo reduce a un cuarto.

### 8.3 Métricas a trackear desde día 1

Mantener una tabla en Google Sheets o Notion con una fila por pieza publicada:
- Fecha
- Property (siempre ai-brief-latam en F1)
- Slug del tema
- Tiempo total invertido (min)
- Tiempo de cada etapa (research / brief / fact-check / composition / publish)
- Followers ganados en 24h
- Followers ganados en 72h
- Alcance
- Likes
- Comentarios
- Saves
- Shares
- Newsletter signups en 72h
- Notas de aprendizaje

Al final de cada semana, sumarizar.

---

## 9. Riesgos especiales y compliance

### 9.1 Meta / Instagram

Reglas no negociables del sistema (enforced por Compliance Agent):

- Nunca usar bots de follow/unfollow o engagement automation prohibido por Meta.
- Nunca enviar DMs masivos.
- Nunca publicar contenido copiado sin transformación sustancial.
- Nunca usar imágenes/videos con copyright sin licencia.
- Cuentas profesionales/business obligatorias para usar API oficial.
- Publishing solo via métodos oficiales (Meta Graph API o tools aprobadas como Buffer/Later/Metricool).
- Evitar contenido financiero engañoso (especialmente Crypto).
- Evitar claims sin fuente.

### 9.2 Crypto-específico (Crypto Brief LATAM)

Reglas adicionales (enforced por Financial Risk Agent + Compliance Agent):

- Nunca dar asesoría financiera personalizada.
- Nunca recomendar comprar/vender activos específicos.
- Nunca prometer rendimientos.
- Nunca promover monedas como inversión.
- Disclaimers visibles ("Este contenido es informativo, no asesoría financiera").
- Citar siempre fuente oficial para datos.
- Evitar afiliados dudosos.
- Revisar regulación por país cuando aplique.

### 9.3 Copyright y atribución

- Citar siempre fuente original.
- Transformar sustancialmente cualquier insight tomado de terceros.
- No reproducir gráficos sin permiso/licencia.
- No usar imágenes protegidas sin derecho.
- Diseño visual original (templates propios, no plantillas robadas).

### 9.4 Demonetización / ban risk

Para minimizar riesgo de baneo en Meta:
- No automatizar acciones que parezcan bot.
- No usar la misma cuenta para acciones masivas.
- Mantener relación natural seguidores/seguidos.
- Variar formatos.
- No publicar contenido idéntico entre cuentas (cuando sumemos las 3).

---

## 10. Métricas de éxito por fase

### Fase 1 (Manual MVP)
- ✅ 12-18 piezas publicadas
- ✅ 3-4 newsletters enviadas
- ✅ 100% de piezas con log completo
- ✅ Dashboard de métricas operativo
- ✅ 3 cuellos de botella identificados
- 📈 Followers: target soft 200-500 (depende del nicho)
- 📈 Newsletter signups: target soft 30-80

### Fase 2 (Analysis)
- ✅ WORKFLOW_ANALYSIS.md completo
- ✅ Spec del primer agente

### Fase 3 (First agent)
- ✅ Tiempo de scanning diario reducido de 30-45 min a <10 min

### Fase 4 (Pipeline complete)
- ✅ Tiempo total por pieza reducido de 90-120 min a <20 min
- ✅ Pipeline produciendo briefs aprobados sin intervención manual fuera de aprobaciones

### Fase 5 (Crypto)
- ✅ Crypto Brief activo
- ✅ Cero modificaciones a agentes para soportar la nueva property (solo config + Financial Risk Agent nuevo)

### Fase 6 (Startup Radar)
- ✅ 3 properties activas
- ✅ 25-40 piezas/mes en producción

---

## 11. Decisiones abiertas (a cerrar antes de Fase 1)

1. **Handles de Instagram tentativos** para AI Brief LATAM. Pueden ser internos (`ai.brief.latam`, `aibrief.lat`, `briefai.la`, etc.) — final se define en Fase 1.5 con research.
2. **Cuenta de Instagram personal o nueva entidad?** Si es nueva entidad: ¿LLC, persona física, otra figura? Esto afecta verification, ads, etc.
3. **Idioma:** ¿Español neutro? ¿Variantes regionales? Recomendación: español neutro con guiños regionales sin abusar.
4. **Día de envío del newsletter:** lunes 8am LATAM es estándar, pero podés probar otros.
5. **Horarios de publicación Instagram:** A definir con datos. Inicialmente probar 3 ventanas: 9am / 13h / 19h LATAM.

---

## 12. Anexos

### Anexo A — Template de brief

```markdown
# Brief: {topic_slug}

**Fecha:** YYYY-MM-DD
**Property:** ai-brief-latam
**Score:** XX/100
**Fuentes:**
- [URL 1]
- [URL 2]

## ¿Qué pasó?
{1-3 oraciones, fáctico}

## ¿Por qué importa para LATAM?
{2-4 oraciones, ángulo regional}

## ¿Qué cambia?
{antes vs después, 2-4 oraciones}

## ¿Quién gana, quién pierde?
{lista corta}

## Datos clave
- Dato 1
- Dato 2
- Dato 3

## Posibles ángulos editoriales
1. {ángulo educativo}
2. {ángulo de oportunidad}
3. {ángulo de riesgo}

## Riesgos
- {legal, reputacional, financiero, plataforma}

## Recomendación de formato
{Reel | Carrusel | Post estático | Solo newsletter}

## Hook tentativo
"{frase corta para el slide 1 / primer 3 segundos del reel}"

## CTA tentativo
{newsletter signup | save | share | comment}
```

### Anexo B — Signal Scoring Rubric

Cada item de fuente se califica 0-100 sumando categorías:

| Categoría | Peso | Criterio |
|---|---|---|
| Relevancia LATAM | 0-20 | ¿Aplica a la audiencia? |
| Novedad | 0-15 | ¿Es nuevo o ya circuló? |
| Urgencia | 0-10 | ¿Tiene ventana de tiempo? |
| Credibilidad de fuente | 0-15 | ¿Fuente confiable y verificable? |
| Potencial educativo | 0-10 | ¿Enseña algo útil? |
| Potencial viral | 0-10 | ¿Tiene hook fuerte? |
| Fit con la marca | 0-10 | ¿Coincide con voz/posicionamiento? |
| Riesgo (penalty) | 0 a -10 | ¿Hay riesgo legal/reputacional? |

Score >70 = candidato fuerte. Score 50-70 = considerar. Score <50 = descartar.

### Anexo C — Manual MVP daily log template

Archivo: `projects/ai-brief-latam/manual-mvp/pieces/{YYYY-MM-DD}_{slug}.md`

```markdown
# {Topic title}

## Metadata
- **Fecha:** YYYY-MM-DD
- **Property:** ai-brief-latam
- **Slug:** {slug}
- **Tipo:** {reel | carrusel | post estático}
- **Publicado en:** {fecha-hora}
- **URL post:** {link}

## Tiempos (cronometrar)
- Research / scanning: __ min
- Selección del tema: __ min
- Brief: __ min
- Fact-check: __ min
- Composición visual + caption: __ min
- Programación / publicación: __ min
- **TOTAL: __ min**

## Decisiones tomadas
- ¿Por qué este tema y no otros?: 
- ¿Qué alternativas consideré?: 
- ¿Qué ángulo elegí y por qué?: 

## Fuentes usadas
1. {URL} — {qué tomé de acá}
2. {URL} — {qué tomé de acá}

## Brief final
{pegar el brief usado}

## Caption final publicado
{pegar caption}

## Errores y dolores del proceso
- {qué fue lo más doloroso}
- {qué error casi cometí}
- {qué tuve que rehacer}

## Métricas (llenar 24h, 72h y 7d después)
- Alcance 24h: 
- Likes 24h: 
- Comments 24h: 
- Saves 24h: 
- Shares 24h: 
- Followers ganados 24h: 
- Newsletter signups 24h: 
- (repetir para 72h y 7d)

## Aprendizajes
- {qué funcionó}
- {qué no funcionó}
- {qué cambiaría la próxima vez}
- {qué de esto se podría automatizar}
```

### Anexo D — Compliance checklist Instagram/Meta

Antes de publicar, verificar:

- [ ] Cuenta es business/professional
- [ ] Caption no contiene claims financieros sin disclaimer
- [ ] Imágenes son originales o con licencia
- [ ] No hay copia textual de otra fuente
- [ ] Hashtags son <30 y relevantes
- [ ] No se prometen resultados
- [ ] Si reseña herramienta: claim verificable
- [ ] No hay info personal de terceros sin consentimiento
- [ ] No se usa data scraped de plataformas sin permiso
- [ ] No hay enlace a contenido prohibido por Meta

### Anexo E — Compliance checklist Crypto

Antes de publicar, verificar (additional al anexo D):

- [ ] Disclaimer visible "no es asesoría financiera"
- [ ] No se recomienda comprar/vender activo específico
- [ ] No se prometen rendimientos
- [ ] Cita fuente oficial para cualquier dato
- [ ] No promueve scams ni esquemas de referidos dudosos
- [ ] Riesgos mencionados explícitamente
- [ ] Si menciona regulación: verificada por jurisdicción
- [ ] Si menciona exchange: revisar que no haya conflictos / patrocinios no declarados
- [ ] Tono no genera FOMO

---

## 13. Próximos 3 pasos concretos (post-split)

Apenas termine la operación de split en curso:

1. **Push a GitHub de los dos repos** (mira como FROZEN, project-autopilot como ACTIVE).
2. **Bootstrap de la estructura v2** en project-autopilot (carpetas `projects/`, `agents/`, configs stub, este master plan en su lugar).
3. **Setup de cuentas** para Fase 1: Instagram Business para AI Brief LATAM, Beehiiv, Buffer, Canva Pro, Feedly. **Empezar Fase 1 antes del fin de la próxima semana.**

---

**Recordatorio final:** este plan está optimizado para producir contenido real, validar mercado real, y construir solo lo que la operación demuestre que vale la pena. Si en cualquier momento un agente o feature no ha sido demandado por el uso real, **no se construye**. Lo único no negociable son las 3 reglas de la sección 0: manual primero, una property primero, humano siempre en el loop.
