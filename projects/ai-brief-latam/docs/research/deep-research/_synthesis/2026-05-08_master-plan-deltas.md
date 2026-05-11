# Cambios sugeridos al MASTER_PLAN basados en research nuevo

**Fecha:** 2026-05-08
**Plan revisado:** `C:/Users/manup/projects/project-autopilot/MASTER_PLAN.md` v2.0 (Mayo 2026)
**Brand voice revisado:** `projects/ai-brief-latam/brand_voice.md` (last updated 2026-05-07)

> Este documento NO modifica MASTER_PLAN.md. Solo propone deltas con su evidencia,
> fuerza, y acción recomendada. La edición final la hace Manuel después de revisar.

---

> **STATUS UPDATE — 2026-05-11**
>
> **MASTER_PLAN.md fue decompuesto el 2026-05-10** en una serie de docs especializados:
> - `docs/STACK.md` — herramientas confirmadas + costos
> - `docs/SYSTEM_DESIGN.md` — arquitectura del sistema multi-agente
> - `docs/AUTOMATION_ARCHITECTURE.md` — diseño del flow automatizado
> - `docs/AGENTS_SPEC.md` — 11 agents (no 9) descriptos como n8n nodes/sub-workflows
> - `docs/ROADMAP.md` — fases con DoD
>
> **La migración a n8n cloud + 11 agents como nodes/sub-workflows ya está implementada en esos docs.**
> El research n8n templates (2026-05-11) confirmó la viabilidad de la dirección.
>
> Por consecuencia, **los deltas siguientes quedan SUPERSEDED**:
> - **Delta #17** (round 2): "single-agent + tools Fase 1-3 → LangGraph Fase 4" — SUPERSEDED. La dirección elegida es n8n cloud directo desde Fase 1, sin la pasada por single-agent puro.
> - **Delta #22** (round 2): "validar 2 semanas con single-agent + tools antes de construir set de 9 agentes" — SUPERSEDED. n8n cloud reemplaza el path "framework vs no-framework"; la validación va a ser sobre templates importados, no sobre código puro.
> - **Contradicción #10** (round 2, en addendum de `2026-05-08_synthesis.md`): "Stack del control plane: Python directo vs framework" — SUPERSEDED. Resuelto: n8n cloud + Anthropic node nativo + HTTP Request para casos avanzados (prompt caching, Batch API).
>
> **Deltas que quedan PARCIALMENTE aplicables** (revisar caso por caso):
> - **Delta #18** (round 2): "Fly.io/Railway/Render NO Vercel para agent engine" — aplica solo si se elige self-hosted n8n. Si n8n cloud, n/a. Si self-hosted en Hostinger VPS (mencionado en STACK.md como alternativa), Hostinger reemplaza el default Fly.io/Railway.
>
> **Deltas que SIGUEN VIGENTES** (la decisión n8n no los afecta):
> - Deltas #1-#16 (round 1, todos sobre brand voice / editorial / monetización / posicionamiento LATAM)
> - Delta #19 (round 2, dual revenue stream) — orquestador no afecta modelo de negocio
> - Delta #20 (round 2, priorización Fase 8) — idem
> - Delta #21 (round 2, canales primary IG vs LinkedIn) — pendiente de discutir
> - Delta #23 (round 2, Brand Voice Agent priority) — aún más relevante en arquitectura n8n
> - Delta #24 (round 2, Rundown rate card como input) — idem
> - Delta #25 (round 2, drift de voz como riesgo §9) — aplica igual a sistema n8n
> - Delta #26 (round 2, revenue/employee como métrica) — idem
> - Delta #27 (round 2, Claude como default fact-check) — confirmado por research n8n templates
>
> **Documentos a editar para reflejar SUPERSEDED**: este archivo + `2026-05-08_synthesis.md` (la contradicción #10).

## Tabla de deltas propuestos

| # | Sección del MASTER_PLAN | Estado actual | Cambio propuesto | Source del cambio | Fuerza de la evidencia | Acción recomendada |
|---|---|---|---|---|---|---|
| 1 | §3.1 ai-brief-latam — voz | "Práctica, sobria, anti-humo, técnicamente precisa, accesible" | **Sin cambios.** Reforzar con marker explícito "anti-hype" en hard NO's de brand_voice | `creators-ia-espanol-landscape` (hueco "benchmarking serio anti-hype") + `social-media-niches-2026` ("creators who add real synthesis vs hype repeaters") | Alta (2 fuentes independientes) | Sin cambio al MASTER_PLAN. Pequeño ajuste en `brand_voice.md` para explicitar "anti-hype" como ángulo de diferenciación, no solo como prohibición |
| 2 | §3.1 ai-brief-latam — fuentes target 15-25 | OpenAI/Anthropic/Google/Meta blogs + AI Snake Oil + Latent Space + LATAM | Agregar **fuentes de IA aplicada a finanzas LATAM** (Belvo blog, Simetrik, Mendel AI, Ualá research) y **fuentes de gobernanza/ROI** (gartner LATAM, MIT Sloan Review en español, Finnovista reports) | `fintech-insurtech-crypto-latam` (10+ fintechs LATAM con IA aplicada) + `creators-ia-espanol-landscape` (hueco governance/ROI) | Media-alta | Discutir con Manuel. Riesgo: dispersión temática. Beneficio: ángulos diferenciados |
| 3 | §6.1 catálogo de 9 agentes MVP | Source Monitor + Signal Scorer + Editorial + Fact-Checker + Composer + Compliance + Approval + Publisher + Analytics | **Sin cambios estructurales.** Confirmar que el set de 9 cubre los 10 del research multi-agente (TrendScout = SourceMonitor + SignalScorer; Edición + Composer = ContentComposer; Engagement queda fuera intencionalmente) | `multi-agente-instagram-automation` (vocabulario coincide), MASTER_PLAN principio "no construir N+1 hasta demostrar necesidad" | Alta | Sin cambio. Notar formalmente en `agents/README.md` la equivalencia de taxonomías |
| 4 | §3.1 cadencia inicial Manual MVP | "3-5 piezas/semana en Instagram, 1 newsletter weekly" | **Sin cambios.** Rechazar explícitamente la cadencia "TT 3/day, IG 2/day, X 6-10/day" del research social-media-niches-2026 | `social-media-niches-2026` (alta cadencia recomendada) vs realidad operativa fundador solo + MASTER_PLAN regla manual primero | Alta (a favor del status quo) | Sin cambio. Documentar el razonamiento en notas para evitar revisitar |
| 5 | §6 catálogo agentes — Engagement Agent | No incluido en MVP ni en intermedio (10-20) | **Mantener fuera.** Documentar explícitamente que auto-replies y DM automation están permanentemente fuera de scope | MASTER_PLAN §9.1 + research multi-agente que lo incluye | Alta | Editar §9.1 para agregar línea: "Engagement automation (auto-replies, auto-DMs) queda permanentemente fuera de scope, incluso post-Fase 8" |
| 6 | §4.3 decisiones diferidas Fase 1 — Visual generation | "Midjourney, Recraft, DALL-E vía API, o solo Canva sin AI. Decidir tras 5-10 piezas hechas a mano" | **Pre-comprometer**: Canva Pro + AI assistant para edición + 0% AI generation primary de visuales (faceless con stock + texto + voz humana) | `production-stack-research` previo (decisión ya tomada) + `multi-agente-instagram-automation` que sugiere lo contrario | Alta | Editar §4.3 para mover Visual generation de "decisión a tomar" a "decisión confirmada por research". Reduce procrastinación |
| 7 | §6.2 catálogo intermedio — orden de construcción | Lista plana de 11 agentes (10-20) sin priorización | Priorizar **Brand Voice Agent (#19)** y **Quality Control (#20)** por encima de Carousel Builder / Video Production | `social-media-niches-2026` (franchise/voice consistency) + `creators-ia-espanol-landscape` (mercado saturado, voz como diferenciador) | Media-alta | Discutir con Manuel. Reordena §6.2 sin cambiar el set |
| 8 | §3.1 fuentes — incluir LATAM-fintech-AI | Bloomberg Línea Tech, Contxto, LatamList, Forbes Latam Tech | Agregar Belvo blog, Simetrik, Mendel AI, Ualá research/blog, CloudWalk product blog como fuentes de "IA aplicada" cuando aplica | `fintech-insurtech-crypto-latam` (lista nominal de 10+ fintechs con IA en producto) | Media-alta | Editar §3.1 fuentes (subset opcional) o cargar a `sources.yaml` directamente |
| 9 | §11 decisiones abiertas — naming AI Brief LATAM | "Handles tentativos, final post-Fase 1 con research" | **Sin cambios.** Pero agregar como criterio extra: el nombre debe **no posicionar como "noticias IA"** (saturado) sino como "implantación / governance / casos LATAM" | `creators-ia-espanol-landscape` (4 posicionamientos saturados, 5 huecos) | Media | Anotar en §11 como criterio adicional. La decisión sigue siendo Fase 1.5 |
| 10 | §3.1 ai-brief-latam — risk profile | "Bajo. Información imprecisa sobre lanzamientos, confundir rumor con hecho" | Agregar: "Riesgo de saturación competitiva si el ángulo deriva a generalista. Diferenciación viene de sectorial/governance/middle-market LATAM" | `creators-ia-espanol-landscape` (saturación + 5 huecos) | Media-alta | Editar §3.1 risk profile |
| 11 | §10 métricas Fase 1 — kill criteria | No definido. Solo "12-18 piezas publicadas" como DoD | Agregar criterio explícito: si tras 12-18 piezas el target soft de 200-500 followers no se alcanza, **revisar ángulo y voz antes de Fase 2** (no solo "identificar 3 cuellos de botella") | `social-media-niches-2026` (kill format 15-20 posts, kill concept 50 posts) — adaptado a escala manual | Media (heurística sin data dura) | Discutir con Manuel. Riesgo: trigger feliz a pivotar antes de tiempo |
| 12 | §8.2 workflow diario sugerido | "30-45 min Feedly + 25-30 min brief + ..." | **Sin cambios.** El research social-media-niches-2026 propone cadencias mucho más altas, irrelevantes para fundador solo Fase 1 | `social-media-niches-2026` vs MASTER_PLAN | Alta (a favor del status quo) | Sin cambio |
| 13 | §3.2 crypto-brief-latam — risk profile y voz | Definido bien | **Sin cambios estructurales.** Considerar agregar sub-vertical "Capital stack / FIDCs / venture debt" como ángulo diferenciador | `fintech-insurtech-crypto-latam` (hueco editorial específico) | Media | Discutir con Manuel cuando se acerque Fase 5 |
| 14 | §5 estructura del repo — nuevas carpetas | `docs/`, `projects/`, `agents/`, `core/` | Validar que la nueva carpeta `projects/ai-brief-latam/docs/research/deep-research/` y sub-carpetas `_critical-analysis/`, `_synthesis/` están alineadas con la convención | Esta operación misma | Alta | Sin cambio (ya creadas). Posible: agregar nota en §5 sobre patrón `_critical-analysis` para futuros research |
| 15 | §3.1 audiencia AI Brief LATAM | "Founders, operadores, consultores, freelancers, profesionales de empresa" | Refinar: agregar **"managers y C-level interesados en governance / ROI / coste de IA"** explícitamente | `creators-ia-espanol-landscape` (hueco governance/ROI directivos) | Media | Editar §3.1 audiencia |
| 16 | §6.2 catálogo intermedio — agente faltante | Sin agente "Editorial Calendar / Franchise Lock" | Considerar agregar agente o sub-función que enforce las 4 format pillars (35-75s explainer / chart-map breakdown / ranking-mythbuster / "what this means for you") como restricciones de output del Composer | `social-media-niches-2026` (4 format pillars) | Media | Discutir con Manuel. Posible incorporar como restricción en `agents/content_composer/config.yaml` sin agente nuevo |

## Resumen por fuerza de evidencia

- **Alta (8 deltas):** confirmaciones del status quo + 2 ajustes pequeños (§4.3 visual generation, §9.1 engagement automation explícito)
- **Media-alta (4 deltas):** ajustes de fuentes, audiencia, voz que valen discusión pero no son urgentes
- **Media (3 deltas):** decisiones que dependen del juicio de Manuel y pueden esperar
- **Baja (0 deltas):** ningún delta tiene evidencia débil que justifique cambio

## Resumen por acción recomendada

- **Editar ya** (alta evidencia + bajo costo): #5 (engagement automation explícito), #6 (visual generation confirmado)
- **Discutir con Manuel:** #2, #7, #11, #13, #15, #16
- **Sin cambio (con razonamiento documentado):** #1, #3, #4, #12, #14
- **Cargar a sources.yaml u otros configs sin tocar MASTER_PLAN:** #8

## Notas de honestidad

- Ningún research nuevo justifica un **cambio estructural** al MASTER_PLAN. La arquitectura 3-capas, las 8 fases y las 3 reglas no negociables siguen sólidas.
- El research multi-agente Instagram, si se hubiera tomado en serio sin filtro crítico, habría sugerido un MASTER_PLAN diferente y peor (HITL opcional, AI generation primary, n8n nuevo). El filtro funcionó.
- La mayoría de los deltas son **refuerzos** y **especificaciones**, no pivotes.
- Si Manuel siente la tentación de adoptar la cadencia masiva del research social-media-niches-2026, recordar que ese research está calibrado para un creator full-time con team. No aplica a Fase 1 manual con un fundador.

---

# Addendum — round 2: Deltas de multi-agent frameworks + Rundown AI

> Agregado 2026-05-08. Deltas que emergen específicamente de los 2 research adicionales,
> mantenidos separados para trazabilidad.

## Tabla de deltas adicionales (round 2)

| # | Sección del MASTER_PLAN | Estado actual | Cambio propuesto | Source del cambio | Fuerza de la evidencia | Acción recomendada |
|---|---|---|---|---|---|---|
| ~~17~~ | ~~§4.2 stack tecnológico — orquestación de agentes~~ | ~~"LLM principal: Claude (Anthropic API directa) para v1. Más simple y controlable que SDKs intermedios."~~ | ~~Agregar nota: **"Para Fase 1-3: single-agent + tools (Camino C). Para Fase 4 cuando se construyan los 9 agentes: evaluar LangGraph (Camino A) si la operación demuestra que el control plane simple no alcanza."**~~ | ~~`multi-agent-frameworks` (camino C → A explícito) + MASTER_PLAN principio "no construir N+1 hasta demostrar necesidad"~~ | ~~**Alta**~~ | **SUPERSEDED 2026-05-11** — dirección elegida: n8n cloud + Anthropic node nativo desde Fase 1. Ver banner top del archivo. |
| 18 | §4.4 diferido — Cloud/VPS para Autopilot | "no hasta tener razón clara (mantener local)" | Cuando se migre, agregar default: **"Fly.io / Railway / Render para agent engine; NO Vercel para los runs largos."** | `multi-agent-frameworks` recomendación deployment | Media-alta | **Editar ya** (es nota informativa, no compromiso) |
| 19 | §3.1 ai-brief-latam — monetización (mencionada solo en §11 abierto y Fase 8) | "Decisiones abiertas: tier free vs premium" en §7.7. Fase 8 lista tracks sin priorización | **Lockear modelo target: dual revenue stream (sponsorships + paid tier ~$500-$1,000/yr equivalente LATAM, conversion target 0.5-1% de free list)** como arquitectura desde el diseño, no decisión abierta. Sponsorships sole es modelo inferior matemáticamente. | `rundown-ai-business-model` (50/50 mix, LTV 2-4× vs solo-ads) | **Alta** | **Editar ya.** Cambio más sustantivo del round 2 |
| 20 | §Fase 8 scale + monetización | "Posibles tracks: newsletter sponsorships, premium subscription tier, etc." (sin orden) | Reordenar tracks priorizando **paid product/community** como driver financiero principal, sponsorships como secundario. Anchor benchmarks: $999/yr Rundown University, ~$833K revenue/empleado, 25-50% margen. | `rundown-ai-business-model` | Alta | Editar Fase 8 con prioridades claras |
| 21 | §3.1 ai-brief-latam — cadencia inicial / canales | "3-5 piezas/semana en Instagram, 1 newsletter weekly" — implica IG + newsletter en paralelo desde día 1 | **Discutir:** ¿agregar LinkedIn español como canal primary de audience-building paralelo a IG en Fase 1, basado en insight Rundown ("newsletter es monetization layer encima de audience-building en otra plataforma")? Alternativas: (a) mantener IG-first como ya está; (b) IG + LinkedIn paralelo; (c) LinkedIn-first + IG secundario | `rundown-ai-business-model` | Media-alta | **Discutir con Manuel** (decisión meta-arquitectónica) |
| ~~22~~ | ~~§6.1 catálogo 9 agentes MVP — orden de construcción~~ | ~~Lista de 9 agentes para Fase 3-5 sin pre-validación de necesidad de framework~~ | ~~Agregar línea: **"Antes de construir el set de 9 agentes, validar 2 semanas con single-agent + tools (sin framework). Solo migrar a LangGraph cuando: (a) consistency entre 3 properties falla, (b) HITL formal es necesario, (c) critique loop demanda checkpointing/iteraciones explícitas."**~~ | ~~`multi-agent-frameworks` Camino C → A criterios~~ | ~~**Alta**~~ | **SUPERSEDED 2026-05-11** — 11 agents (no 9) ya descriptos como n8n nodes/sub-workflows en `docs/AGENTS_SPEC.md`. La validación va a ser sobre templates importados, no sobre código Python puro. Ver banner top del archivo. |
| 23 | §6.2 catálogo intermedio — Brand Voice Agent (#19) | Listado en intermedio, sin priorización dentro del set | Subir prioridad de Brand Voice Agent dentro del intermedio. Razón nueva: el research multi-agent identifica **drift de voz de marca** como riesgo principal de multi-agent. Si llegamos a multi-agent en Fase 4+, drift es el riesgo material #1. | `multi-agent-frameworks` (drift identificado) + delta #7 anterior | Media-alta | Reordenar §6.2 cuando se llegue a Fase 4 |
| 24 | §3.1 ai-brief-latam — fuentes / inputs operativos | Lista de fuentes target | Agregar **Rundown rate card** (rundown.ai/advertise-with-us) como **input de patrón táctico** (regla "no other AI newsletters as sponsors", demographics breakdown, CPM benchmarks). No fuente de contenido editorial; fuente de tactics. | `rundown-ai-business-model` (regla exclusión sponsors) | Baja | Cargar a `sources.yaml` con tag `business-pattern` |
| 25 | §9 riesgos — agregar drift/quality | §9.1 cubre Meta rules, copyright, financial. No cubre drift de voz de marca | Agregar §9.5 "Drift de voz / quality": "Drift de voz de marca por uso de multi-agent es riesgo identificado. Mitigation: prompt caching + Brand Voice Agent + style guide en system prompt + revisión humana periódica + evaluations automáticas (LangSmith o equivalente)." | `multi-agent-frameworks` (drift como riesgo central) | Media-alta | **Editar ya** §9 con nueva subsección |
| 26 | §10 métricas de éxito — agregar benchmark de eficiencia | DoD por fase no incluye métricas de eficiencia operativa | Agregar (en Fase 6+): **revenue per employee como métrica de eficiencia.** Anchor: Rundown $833K/empleado. Para AI Brief LATAM, target conservador: $200K-$400K/empleado en Fase 6 cuando 3 properties operen. | `rundown-ai-business-model` benchmark | Media | Editar §10 con métrica adicional Fase 6+ |
| 27 | §4.3 decisiones diferidas Fase 1 — fact-checking helper | "Decidir si solo Claude o agregás Perplexity/Tavily/Exa" | Reforzar Claude como default basado en `rundown-ai-business-model` que confirma Claude como editor-in-chief de un newsletter de $10M ARR. Añadir Perplexity/Tavily solo si Claude search/research falla específicamente. | `rundown-ai-business-model` validation | Media | Editar §4.3 cerrando un grado de la decisión |

## Resumen de deltas adicionales por fuerza de evidencia

- **Alta (4 deltas):** #17 (single-agent → LangGraph orden), #19 (dual revenue stream), #20 (Fase 8 priorización), #22 (validación pre-framework)
- **Media-alta (4 deltas):** #18 (deployment defaults), #21 (canales primary, **a discutir**), #23 (Brand Voice priorización), #25 (drift como riesgo §9)
- **Media (2 deltas):** #26 (revenue/empleado métrica), #27 (Claude como default fact-check)
- **Baja (1 delta):** #24 (Rundown rate card como input táctico)

## Resumen de deltas adicionales por acción recomendada

- **Editar ya** (alta evidencia + bajo costo): #17, #18, #19, #22, #25
- **Editar Fase 8 cuando se acerque:** #20, #23
- **Editar otros con bajo costo:** #26, #27
- **Discutir con Manuel:** #21 (canal primary, decisión meta-arquitectónica)
- **Cargar a configs sin tocar MASTER_PLAN:** #24

## Notas de honestidad (round 2)

- El delta más sustantivo (#19, dual revenue stream) **convierte una decisión Fase 8 abierta en una decisión arquitectónica desde el diseño**. Es el cambio más material que emerge de los 6 research procesados.
- El delta #21 (canal primary IG vs LinkedIn) es la única tensión real con el MASTER_PLAN actual. No la resuelvo unilateralmente — es decisión meta-arquitectónica que vale la pena discutir.
- El research multi-agent es **honesto sobre límites** (auto-confiesa biases, falta de benchmarks, opiniones marcadas). Lo trato con más confianza que el research multi-agente Instagram (que era opaco).
- El research Rundown se basa fuertemente en envelope math derivada (RPS, mix 50/50, $200K Meta Ads). Los números absolutos son aproximados, pero las **direcciones** (dual stream > solo ads, paid product es la mitad del business) están bien soportadas. Las direcciones es lo que se traslada a deltas, no los números absolutos.
- Si Manuel decide ir más conservador en monetización (solo sponsorships), el modelo igual funciona — pero llegar a $1M+ ARR requeriría 5-10× más subs que con dual stream. La math de Rundown es difícil de ignorar.
