# Cambios sugeridos al MASTER_PLAN basados en research nuevo

**Fecha:** 2026-05-08
**Plan revisado:** `C:/Users/manup/projects/project-autopilot/MASTER_PLAN.md` v2.0 (Mayo 2026)
**Brand voice revisado:** `projects/ai-brief-latam/brand_voice.md` (last updated 2026-05-07)

> Este documento NO modifica MASTER_PLAN.md. Solo propone deltas con su evidencia,
> fuerza, y acción recomendada. La edición final la hace Manuel después de revisar.

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
