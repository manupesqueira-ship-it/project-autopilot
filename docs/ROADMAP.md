# Roadmap — AI × Finanzas LATAM (v5, 2026-05-29)

> **Cambios v5 vs v4** (ADR-017 post-Deep-Research):
> - **Pivot de nicho:** AI How-To genérico → **AI × Finanzas Personales LATAM** (vertical único, sub-decisión B.1).
> - **Reset realista de target:** 100K en 12-18m → **10K en 12m, 30-50K en 24m, 100K en 36m+ con equipo**. North star "audiencia masiva" se mantiene pero como horizonte largo, no target 12-18m.
> - **Stack SaaS-first:** ContentStudio + Blotato + Beehiiv reemplaza n8n custom + Upload-Post. n8n queda SOLO para el moat (scorer + fact-check + Telegram). Hostinger VPS DIFERIDO.
> - **NUEVO: Inflection Lever Track** como work stream paralelo a Fase -1 (5 outreaches/semana desde Mes 1).
> - **Voice clone DIFERIDO** — decisión final cuando Fase 2 esté a 30 días.
> - **Newsletter adelantado:** ya no es Fase 3, ahora Fase 1 (es el activo más durable según Reports 02+05).
>
> **Nombre del proyecto:** carpeta sigue como `projects/dinero-ia/` hasta que haya handle/dominio decidido. El proyecto editorial se llama **AI × Finanzas LATAM** (working name).

---

## Fase -1 — Validación Manual + Inflection Lever Track (Semanas 1-2)

**Objetivo:** Validar la voz/nicho/ángulo con audiencia real **antes** de invertir en pipeline técnico. **En paralelo**, iniciar el plan de partnerships/PR/cross-promo que el dataset Report 03 marcó como factor #1 de éxito.

### Work stream A — Validación Manual

**Alcance:**
- 5-10 piezas publicadas manualmente (no automatizado)
- Cuenta personal de Manuel o cuenta de prueba (no brand definitiva todavía)
- Mix de tópicos: **IA aplicada a finanzas personales LATAM** (no genérico AI how-to)
- **Sin pipeline n8n.** Manuel usa Claude.ai directo + ChatGPT Plus para visuales o Canva.

**Tareas:**
1. **Manuel:** definir 5-10 tópicos del cruce AI×Finanzas LATAM (ej: "Cómo armar tu portfolio CEDEAR con Claude en 15 min", "Probé 3 IAs para mi presupuesto. La mejor cuesta $0", "El prompt que detectó las comisiones ocultas de mi broker")
2. **Manuel + Claude (chat):** generar cada brief con prompts directos (siguiendo `docs/MANUAL_OPERATIONS.md`)
3. **Manuel:** generar visuales en ChatGPT/DALL-E playground siguiendo `docs/POST_STANDARD.md` §7
4. **Manuel:** publicar en cuenta personal o test cada 1-2 días durante 1-2 semanas
5. **Compliance check manual:** cada pieza pasa por `a9-compliance.md` (incluye reglas financieras nuevas — no recomendar valores específicos, disclaimer "no es asesoría")
6. **Track engagement** en `manual-mvp/metrics/`: views, saves, comments, shares por pieza

**Decision criteria:**
- **Funciona:** >2% engagement promedio (saves+comments)/views, ≥1 comentario sustantivo por pieza, ≥1 mensaje directo preguntando "cómo lo hiciste" → seguir a Fase 0
- **Funciona parcialmente:** 1-2% engagement, comentarios genéricos → iterar voz o sub-nicho (ej. probar wedge "AI × Inversiones" vs "AI × Presupuesto"), retest 1 ronda
- **No funciona:** <1% engagement, sin comentarios sustantivos → pivot de nicho serio, NO construir pipeline

### Work stream B — Inflection Lever Track (paralelo a A)

**Alcance:**
- Lista inicial de 20 prospects para partnership / cross-promo / podcast guest / press
- 5 outreaches/semana desde Semana 1 de Fase -1
- Bandwidth: 2-3 hs/semana de Manuel
- Objetivo Fase -1: 1-2 conversaciones avanzadas, sin necesidad de cierre

**Lista preliminar de 20 prospects** (Manuel + Claude refinan en próxima sesión):

| Categoría | Candidatos preliminares |
|---|---|
| **Creators finanzas LATAM** (cross-promo) | Mis Propias Finanzas (1M IG, CO), Nicolás Abril (1M IG, CO), Sofía Macías (180K IG, MX), Andrés Gutiérrez (radio sindicada) |
| **Newsletters LATAM complementarios** | Startupeable (Enzo Cavalié, 50K), Cenital (Argentina, 60K daily), Ecosistema Startup (Chile, 10K) |
| **Podcasts LATAM tech/finanzas** | The Frye Show, El Podcast del Real Estate, Bitcoin LATAM podcast equivalente |
| **Brokers con programa partner** | Cocos Capital (AR), IOL Inversiones (AR), GBM (MX), Bitso (MX/LATAM), Buenbit (AR/LATAM) |
| **Fintechs con audiencia profesional** | Ualá (AR/MX/CO), Nubank (BR/MX/CO), Mercado Pago (LATAM), Mercado Crédito |
| **Medios LATAM tech/finanzas** | Bloomberg Línea (pitch), Forbes MX/AR/CO, Wired LatAm, Infobae Tecno |
| **Founders LATAM IA + finanzas** | Pierpaolo Barbieri (Ualá), Daniel Vogel (Bitso), Patricio Fuks (Cocos), Andrés Bilbao (Rappi) |

**Tareas:**
1. **Claude (próxima sesión):** refinar lista de 20 con investigación más profunda + handles/emails verificados
2. **Manuel:** template de outreach base (corto, valor primero, NO pitch frío)
3. **Manuel:** 5 outreaches/semana × 2 semanas = 10 outreaches en Fase -1
4. **Manuel + Claude:** log de tracking en `projects/dinero-ia/inflection-lever/outreach-log.md`

### Definition of Done Fase -1

- [ ] 5-10 piezas publicadas con foco AI × Finanzas LATAM
- [ ] Engagement medible (mejor o peor que 2% saves+comments/views)
- [ ] ≥10 outreaches enviados en el lever track
- [ ] Manuel tiene **convicción informada** sobre seguir, iterar, o pivot serio
- [ ] Lista de 20 prospects refinada con investigación + handles verificados
- [ ] Si funciona: definida la sub-categoría más fuerte (inversiones vs presupuesto vs ahorro vs impuestos vs jubilación)

### Bloquea Fase 0

**Sí.** No avanzar a smoke test técnico si Fase -1 no valida la voz/nicho. **Sí avanzar** con outreach del Inflection Lever Track aunque las piezas no peguen (los outreaches no dependen de engagement — son su propio lever).

---

## Decision Point post-Fase -1

```
                    ┌─ Pivot serio de nicho (otra propuesta del Report 04, ej. Real Estate)
                    │
   Voz NO funciona ─┼─ Iterar sub-nicho + retest 1 ronda más
                    │
                    └─ Pausar proyecto, evaluar otra cosa
   ─────────────────────────────────────────────────────────
                    ┌─ Mantener stack actual SaaS-first
   Voz SÍ funciona ─┤  → Fase 0 smoke test del moat (scorer + fact-check + Telegram)
                    │  → Fase 1 pipeline completo con ContentStudio + Blotato + Beehiiv
                    │
                    └─ Si engagement >5% (excepcional) considerar acelerar a Fase 2
```

---

## Fase 0 — Smoke test del moat editorial (Semana 3, condicional)

**Objetivo:** Validar que el moat editorial custom (scorer + fact-check + Telegram approval) funciona end-to-end, antes de plug-in del stack SaaS.

### Alcance

- 1 fuente RSS (Cenital o Bloomberg Línea Tech para finanzas LATAM) + 1 anglo (TechCrunch AI)
- **Moat editorial:**
  - A2 Signal Scorer (Sonnet 4.5) con rúbrica 9 categorías (8 originales + 1 nueva: `relevancia_finanzas_latam`)
  - A3 Editorial (Opus 4) generando brief AI × Finanzas con voz nueva
  - A9 Compliance (Opus 4) chequeando reglas financieras nuevas
- Output: brief llega a Telegram en <2 min
- Sin Fact-Check externo, sin Carousel, sin Publishing
- Trigger manual (no cron)

### Tareas

1. **Manuel:** crear Telegram bot vía @BotFather (~5 min) — si no se hizo ya
2. **Manuel:** Anthropic API key + $10-20 USD billing (~5 min) — si no se hizo ya
3. **Manuel:** n8n cloud trial (gratis) — registrar cuenta con `aibrieflatam.media@gmail.com`
4. **Claude (chat):** generar workflow JSON simplificado (3 agents: A2 + A3 + A9 + Telegram send) — NO 10 agents
5. **Manuel:** importar workflow + pegar credenciales (~10 min)
6. **Manuel:** Execute Workflow → recibir brief en Telegram (~2 min)
7. **Manuel + Claude:** evaluar brief — ¿voz finanzas, hook, compliance pasan?
8. Iterar A2/A3/A9 si la calidad baja del estándar (1-3 iteraciones)

### Definition of Done Fase 0

- [ ] ≥3 briefs decentes en Telegram en una semana
- [ ] Compliance pasa en todos sin intervención (no recomienda valores específicos, disclaimer presente)
- [ ] Voz finanzas pasa el test "podría haberlo escrito Mis Propias Finanzas con menos sesgo emprendedor"

### Bloqueante para Fase 1

Si Fase 0 no entrega briefs publicables, NO avanzar a Fase 1. El problema está en prompts o señal de fuentes, no en plumbing SaaS.

---

## Fase 1 — Pipeline buy-first + moat custom (Semanas 4-6)

**Objetivo:** Pipeline completo automatizado que produce y publica 1 pieza/día (carousel IG + caption TikTok + sección newsletter), aprobada por humano via Telegram. **Stack híbrido: SaaS para plumbing + n8n para moat editorial.**

### Stack final (ADR-017)

| Capa | Tool | Costo/mo |
|---|---|---:|
| RSS discovery + scheduling + approvals + social publishing IG/TikTok/LinkedIn | **ContentStudio Standard** | $19 |
| Carousel generation + AI images + social API | **Blotato Starter** | $29 |
| Newsletter publishing + AI editor + automations | **Beehiiv Launch** (gratis hasta 2,500 subs) | $0 |
| Moat editorial: scorer + fact-check + Telegram approval | **n8n cloud trial** (gratis) | $0 |
| LLMs editoriales | Anthropic Opus 4 + Sonnet 4.5 | ~$25-42 |
| Image generation backup (si Blotato no rinde) | OpenAI gpt-image-2 | ~$6-8 |
| Domain | varios | ~$1 |
| **Total Fase 1** | | **~$80-100/mo** |

### Agents activos en n8n (solo moat editorial — 4, no 12)

- **A2 Signal Scorer** (Sonnet 4.5) — rúbrica 9 categorías incluyendo `relevancia_finanzas_latam`
- **A3 Editorial AI × Finanzas** (Opus 4) — brief con voz nueva, hooks emocionales, body sobrio con disclaimer
- **A4 Fact-Checker** (Opus 4 + Claude web_search nativo) — verificar cifras financieras (rendimientos, comisiones, tasas) con fuentes oficiales
- **A9 Compliance Financiero** (Opus 4) — 18 reglas (15 originales + 3 nuevas para finanzas)
- **A11 Editor LLM HITL** — Telegram bidireccional (inline keyboard: approve / edit / reject)

**Lo que SE MUEVE de n8n a SaaS:**
- A1 (Source Monitor) → ContentStudio RSS discovery
- A1.5 (Binary filter) → no necesario en ContentStudio flow
- A5 (Visual Director) + A8a (Visual Generator) → Blotato AI Agent Carousel Maker
- A7 (Copy Composer) → ContentStudio AI captions/hashtags + Blotato carousel text
- A8d (Newsletter Composer) → Beehiiv AI blocks dentro del editor
- A10 (Publisher) → ContentStudio + Blotato APIs

### Fuentes (nicho AI × Finanzas LATAM)

**Activas confirmadas Fase 1 — Anglo IA + Finanzas:**
- OpenAI Blog, Anthropic, Google AI (anuncios herramientas IA)
- TechCrunch AI, Wired AI (cobertura industria)
- Latent Space (IA práctica builder)

**Nuevas — Finanzas LATAM (alto peso):**
- **Cocos Capital blog** (AR, broker LATAM)
- **IOL Inversor Online** (AR)
- **Bloomberg Línea Tech + Markets** (LATAM, vía Inoreader si no hay RSS)
- **Cenital** (AR, newsletter financiero)
- **Mis Propias Finanzas blog/podcast** (CO)
- **Pequeño Cerdo Capitalista** (MX, blog Sofía Macías)
- **Sin Permiso de los Padres** (MX, finanzas jóvenes)
- **Buenbit blog** (AR/LATAM)
- **Bitso blog** (MX/LATAM, fintech)
- **Mercado Pago newsroom** (LATAM)

**Reguladores (referencia cuando aplique):**
- CNV Argentina, CNBV México, SFC Colombia, CMF Chile, SBS Perú — solo activan si una pieza específica toca regulación

### Tareas

#### Semana 4 — Setup SaaS

1. **Manuel:** crear cuenta ContentStudio Standard ($19/mo) — conectar IG + TikTok + LinkedIn via OAuth
2. **Manuel:** crear cuenta Blotato Starter ($29/mo) — conectar mismas cuentas
3. **Manuel:** crear cuenta Beehiiv Launch (gratis) — registrar dominio o usar subdomain Beehiiv inicial
4. **Manuel:** activar fuentes RSS finanzas en ContentStudio + configurar approval workflow
5. **Manuel:** template de carousel en Blotato siguiendo POST_STANDARD §7 (dark mode + Inter + JetBrains Mono)

#### Semana 5 — Pipeline moat en n8n cloud

6. **Claude:** generar workflow n8n simplificado (4 agents + Telegram HITL)
7. **Manuel:** importar workflow + pegar credenciales
8. **Manuel + Claude:** few-shot examples para A3 (usar 5-10 piezas validadas en Fase -1)
9. **Configurar webhook n8n → ContentStudio** (cuando Manuel aprueba en Telegram, n8n empuja brief a ContentStudio queue)
10. **Configurar webhook n8n → Blotato** (carousel generation request con brief + visual brief)
11. **Configurar webhook n8n → Beehiiv** (newsletter section append a draft del día)

#### Semana 6 — Test end-to-end + estabilización

12. Test end-to-end: primera pieza completa publicada (carousel IG + TikTok crosspost + newsletter section)
13. Compliance audit manual de las primeras 5 piezas
14. Correr 7 días con 1 pieza/día + HITL aprobando
15. Tracking de costos reales vs proyección en `infra/costs-actual.md`

### Definition of Done Fase 1

- [ ] 7 piezas publicadas en 7 días (1/día consistente)
- [ ] 0 errores fact-check post-publicación (cifras financieras verificadas)
- [ ] 0 violaciones compliance (disclaimer presente, no recomendaciones específicas)
- [ ] Workflow estable >95% (max 1 failure por semana)
- [ ] Costo total dentro de $80-100/mo
- [ ] Newsletter Beehiiv enviada cada día con open rate >25%
- [ ] Inflection Lever Track: ≥1 partnership cerrada o 2-3 conversaciones avanzadas

---

## Fase 2 — Reels con decisión voice clone (Semanas 7-9)

**Objetivo:** Sumar reels al mix. **Pre-requisito:** decidir voice clone (ADR-008 deferred resuelto).

### Pre-requisitos Fase 2

- [ ] Fase 1 estable 14 días con 1 pieza/día sin intervención extraordinaria
- [ ] **Decisión voice clone:** Manuel graba o decide narrar manual / TTS neutro
- [ ] Si voice clone: cuenta ElevenLabs Creator ($11 primer mes con deal, después $22/mo) + grabación 20 min
- [ ] Cuenta Seedance 2.0 (estimado $15/mo)

### Decisión voice clone (resuelve ADR-008 deferred)

Manuel decide entre 3 opciones al inicio de Fase 2:
- **A) Voice clone 100% ElevenLabs:** label automático en TikTok/IG, autoridad cuestionable en finanzas
- **B) Narración manual Manuel:** label "human", autoridad alta, escala limitada
- **C) Híbrido:** voice clone para narración informativa, manual para opiniones/recomendaciones

Default si Fase 1 funcionó muy bien con autoridad de Manuel: **B (narración manual)**. Default si necesitamos escalar: **A o C**.

### Alcance

- 1 carousel + 1 reel por día (alternancia o decisión por pieza)
- Seedance anima keyframes generados por Blotato/gpt-image-2
- Voice según decisión

### Tareas

1. Configurar voice (clone o manual workflow)
2. Configurar Seedance 2.0 API
3. Workflow reel: A3 brief → A7 script (en Blotato) → keyframes Blotato → Seedance video → audio merge → publish via ContentStudio
4. Test: primer reel publicado
5. Calibrar settings primeras 5 piezas
6. Decidir mix carousel/reel según engagement primeras 2 semanas

### Definition of Done Fase 2

- [ ] 14 reels publicados en 2 semanas
- [ ] Voice (clone o manual) con calidad aceptable
- [ ] Engagement reel ≥ carousel (medible por save_rate + watch_through_rate)

---

## Fase 3 — Newsletter scale + landing + monetización inicial (Semanas 10-12)

**Objetivo:** Pasar newsletter de "activo desde día 1" a "activo principal monetizado". Crear landing para captura orgánica. Primer revenue test.

> **Cambio vs ROADMAP v4:** newsletter ya corre desde Fase 1 (Beehiiv Launch). Fase 3 es **scale + landing + monetización**, no "lanzamiento".

### Alcance

- Landing page con captura email (Lovable.dev o alternativa más simple)
- CTA newsletter en captions IG + TikTok + LinkedIn (cada pieza)
- Welcome sequence Beehiiv (3 emails): intro + top 5 piezas históricas + encuesta sub-nicho favorito
- Migrar Beehiiv Free → Scale ($43/mo) cuando llegue a 2,500 subs
- **Primer test monetización:** affiliate Cocos Capital / IOL / GBM / Bitso si tienen programa partner, o sponsored section para fintech LATAM

### Tareas

1. Diseñar landing con value prop específico (3 min/día, LATAM, finanzas con IA, sin asesoría, gratis)
2. Crear landing en Lovable.dev o template simple (~1 día)
3. Conectar landing → Beehiiv API
4. Welcome sequence configurada
5. Agregar CTA newsletter en SaaS (ContentStudio caption templates)
6. **Investigar programas partner:** Cocos Capital, IOL, GBM, Bitso, Buenbit — listar comisiones, requisitos, compliance disclosures
7. Primer sponsored section o affiliate placement (post-disclosure)
8. Tracking analytics: cross-canal (IG, TikTok, LinkedIn, newsletter open/click)

### Definition of Done Fase 3

- [ ] 800 suscriptores newsletter en 30 días post-landing launch (acumulado: ~1,500-2,000 si Fase 1+2 fueron buenas)
- [ ] Landing con conversion rate ≥3%
- [ ] Welcome sequence open rate ≥50%
- [ ] Newsletter daily open rate sostenido >30%
- [ ] **Primer revenue probado** (incluso $0 si solo es affiliate sin comisiones todavía — el test es del setup, no de la magnitud)

---

## Fase 4 — Podcast + community (Meses 4+)

**Objetivo:** Agregar formato podcast + lanzar comunidad pagada/gratis para suscriptores top.

### Alcance

- Episodio semanal de 5-10 min (Smart Brevity audio = top story finanzas + IA semana)
- Voz según decisión Fase 2
- Distribución Spotify + Apple Podcasts (free)
- **Comunidad:** Telegram channel privado o Skool / Whop para top 100-500 suscriptores newsletter (free o ~$5/mo)

### Tareas

1. Definir formato episodio (duración, estructura)
2. Configurar Spotify for Podcasters
3. Workflow publicación semanal
4. Decidir plataforma comunidad (Telegram free vs Skool $59/mo vs Whop)
5. Cross-promotion en otros canales

### Definition of Done Fase 4

- [ ] 10 episodios publicados consecutivos
- [ ] 50+ plays acumulados
- [ ] Comunidad con 100+ miembros activos

---

## Fases futuras (no committed)

### Fase 5 — Monetización seria (Mes 5+)

Solo se evalúa después de >10K subs newsletter + revenue probado.

- Sponsored sections regulares con fintechs LATAM
- Cursos / workshops "AI para tus finanzas" ($50-300/curso, modelo Mis Propias Finanzas)
- Pro tier newsletter ($X/mo) con contenido extra
- Affiliate program brokers

### Fase 6 — Expansión sub-nicho (post-validación de Layer 5)

Si llegamos a 10K subs en 12 meses, evaluar expansión: **AI × Finanzas → AI × otros verticales** (marketing, ventas, ops) — esto es el "wedge + expansión" que descartamos en sub-decisión B (B.2 reabre).

### Multi-property (DIFERIDO sin compromiso)

**No considerar hasta validar Fase 4.** Multi-property prematuro contradice convicción en una idea. Si se considera eventualmente: AI × Inmobiliaria LATAM (sleeper pick Report 04, score 17), o expansión geográfica España.

---

## Timeline visual

```
Semana          1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
Fase -1 (val)   ▓▓▓▓                                          ← Validación Manual
Inflect Lever   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (siempre)  ← paralelo desde Sem 1
Fase 0 (smoke)        ▓▓                                       ← condicional
Fase 1 (build)           ▓▓▓▓▓▓                                ← condicional
Fase 2 (reels)                  ▓▓▓▓▓▓                         ← condicional
Fase 3 (scale)                         ▓▓▓▓▓▓                  ← scale + revenue test
Fase 4 (pod)                                  ▓▓▓▓▓▓▓▓▓▓...   ← podcast + community
```

---

## Métricas de éxito acumuladas (reset realista — ADR-017)

| Métrica | 30 días | 90 días | 180 días | 365 días |
|---------|---------|---------|---------|---------|
| Followers IG | 200-500 | 1,500-3,500 | 4,000-8,000 | **8K-15K** |
| Newsletter subs | 100-300 | 800-2,000 | 2,500-5,000 | **5K-10K** |
| Engagement IG >3% | Goal | 5+ piezas/mes | Consistente | Consistente |
| Newsletter open rate | >35% | >32% | >30% | >30% |
| Fact-check errors públicos | 0 | 0 | 0 | 0 |
| Compliance violations (incluye financiero) | 0 | 0 | 0 | 0 |
| Costo total mensual | $10-15 (Fase 0) | $80-100 (Fase 1) | $115-140 (Fase 2) | $130-180 (Fase 3) |
| Inflection levers cerrados | 1 en conversación | 1 cerrado | 2-3 activos | 5+ |
| Revenue test | - | - | Primer test | $200-1000/mo |

> **Reset crítico vs ROADMAP v4:** target 12m baja de "100K en 12-18m" a **8K-15K IG / 5K-10K newsletter en 12m**. Esto NO es rebajar la ambición — es alinear con base rates documentados en el dataset Report 03. **10K newsletter en 12m es realmente un buen resultado.** El north star "audiencia masiva" se persigue en horizonte 24-36m+, con equipo o automatización pesada cuando aplique.
