# Roadmap de aplicación de research findings

**Fecha:** 2026-05-08
**Inputs:** los 4 deep research + 3 research previos + análisis crítico + síntesis + master-plan-deltas

> Cada finding clasificado por momento de aplicación. Lo que no aparece acá fue intencionalmente filtrado o queda en monitoreo pasivo.

## Aplicar ahora (alta evidencia + bajo costo)

> Findings que se aplican en la próxima sesión sin discusión adicional.

1. **Confirmar 4 format pillars como restricción Fase 1**
   - Pillars: (a) explainer 35-75s con hook brutal, (b) chart/map breakdown, (c) ranking/myth-buster, (d) "what this means for LATAM/your business"
   - Acción: agregar a `brand_voice.md` como sección "Format pillars (Fase 1)" con esa lista exacta. Tocar `templates/` si existen.
   - Fuente: `social-media-niches-2026` + coherencia con Smart Brevity de research previo.
   - Costo: 5 min de edición.

2. **Documentar explícitamente "Engagement automation permanently out of scope" en compliance_rules.yaml + MASTER_PLAN §9.1**
   - Acción: editar `projects/dinero-ia/compliance_rules.yaml` con regla explícita; agregar línea en §9.1.
   - Fuente: research multi-agente Instagram propone lo contrario; filtrarlo como decisión documentada.
   - Costo: 10 min.

3. **Mover Visual generation de "decisión a tomar Fase 1" a "decisión confirmada"**
   - Acción: editar §4.3 del MASTER_PLAN: "Canva Pro + AI assistant + 0% AI generation primary de visuales (faceless con stock + texto + voz humana)".
   - Fuente: production-stack-research previo + filtro de research multi-agente que sugiere lo contrario.
   - Costo: 5 min.

4. **Agregar fuentes IA-aplicada-LATAM a sources.yaml**
   - Lista mínima para incluir: Belvo blog, Simetrik blog, Mendel AI, Ualá research/blog, CloudWalk product blog.
   - Acción: editar `projects/dinero-ia/sources.yaml` con tag "ai-applied-latam".
   - Fuente: `fintech-insurtech-crypto-latam` lista nominal verificada.
   - Costo: 15 min (validar que cada blog publica regularmente antes de incluir).

5. **Refinar audiencia AI Brief LATAM en MASTER_PLAN §3.1**
   - Agregar: "managers y C-level interesados en governance / ROI / coste de IA".
   - Fuente: `creators-ia-espanol-landscape` hueco #2 (governance/ROI directivo).
   - Costo: 2 min.

6. **Anotar el patrón `_critical-analysis/` y `_synthesis/` en §5 estructura del repo**
   - Para que futuros research sigan este patrón sin reinventarlo.
   - Costo: 5 min.

## Aplicar después de validar con 2-3 piezas reales

> Findings que requieren ver el comportamiento del sistema antes de comprometerse.

1. **Sub-franquicia "AI para founders LATAM" o "AI para una función concreta"**
   - Idea: empezar Fase 1 con la franquicia generalista + una sub-franquicia vertical (ej: "AI para fundadores SaaS" o "AI para CFOs"). Medir si la sub-franquicia engancha mejor.
   - Disparador para decidir: tras 5 piezas mixtas, ver si las verticales tienen mejor save/share rate.
   - Fuente: `social-media-niches-2026` ("AI for one profession") + `creators-ia-espanol-landscape` (hueco sectorial).
   - Riesgo: dispersión de marca; vale validar antes de commit.

2. **Adoptar criterio "saves > follows + watch time como métrica madre" en dashboard manual**
   - Ya está en brand_voice.md como principio. Falta medirlo concretamente.
   - Disparador: tras 5 piezas, calcular ratio saves/views y shares/views; comparar con benchmark de Mafia IA / Explicable.
   - Fuente: convergencia 3 sources.

3. **Considerar pre-grabar batch de voz semanal vs grabar pieza por pieza**
   - El research production-stack confirma voz humana como default. Optimización operacional.
   - Disparador: tras 5 piezas, medir tiempo real de grabación + edición. Si excede 20 min/pieza, batch.

4. **Lockear o ajustar handle final de Instagram**
   - MASTER_PLAN §11 dice post-Fase 1 con research. Tras 5-10 piezas y signals iniciales, ya hay evidencia de qué tono pega.
   - Fuente: convergencia con `creators-ia-espanol-landscape` (taglines probadas, formula VALOR + TIEMPO + IDIOMA + PRECIO).

5. **Crear "ediorial calendar / franchise lock" como restricción del Composer**
   - En lugar de agente nuevo, agregar a config del Content Composer: "el output debe coincidir con uno de los 4 format pillars".
   - Disparador: tras Fase 4 cuando exista Composer Agent.

## Monitorear durante 30 días

> Findings que vale tener en mente pero NO aplicar todavía. Re-evaluamos en 30 días con data del manual MVP.

1. **Cadencia masiva del research social-media-niches-2026** (TT 3/day, IG 2/day, X 6-10/day)
   - No aplicable Fase 1 con 1 fundador.
   - Re-evaluar: si Fase 1 muestra que 3-5 piezas/semana es trivial de producir, considerar subir cadencia. Improbable.

2. **Bandit / RL para hook optimization**
   - El research multi-agente lo propone, los demás no. Engineering theater para escala 12-18 piezas.
   - Re-evaluar: cuando Fase 5+ tenga 100+ piezas, evaluar si A/B simple ya está siendo limitante para entonces.

3. **WhatsApp Channels como canal alternativo**
   - Mencionado en `latam-specific-research` previo como pendiente.
   - Re-evaluar: tras Fase 1, si la newsletter Beehiiv tiene tracción, ver si WhatsApp Channel cross-poll vale.

4. **Mafia IA como modelo de monetización newsletter (premium + comunidad + lifetime)**
   - Inspiración para Fase 8.
   - Re-evaluar: cuando AI Brief LATAM tenga 1-3K subs, hacer un análisis específico de Mafia IA post-by-post.

5. **El benchmark "Anas Andaloussi (446K IG + 652K TT) escala con hustle/comercial"**
   - Útil para entender qué pasa si AI Brief LATAM no diferencia bien.
   - Re-evaluar: tras Fase 1, ver si el contenido propio se está pareciendo o diferenciando.

6. **Sub-vertical "Capital stack para fintech (FIDCs, venture debt, securitización)"**
   - Aplicable a Crypto Brief LATAM o como ángulo de AI Brief si toca finanzas.
   - Re-evaluar: cuando se diseñe Crypto Brief Fase 5.

7. **Stablecoins B2B en LATAM como vertical underserviced**
   - Aplicable a Crypto Brief LATAM.
   - Re-evaluar: Fase 5.

8. **Research adicional sobre creators IA en portugués brasileño**
   - Brasil es 50% del fintech LATAM y mercado relevante.
   - Re-evaluar: si AI Brief LATAM crece a top tier y Fase 5/6 demanda multi-idioma.

9. **Reels 25-35 seg vs 30-90 seg**
   - El research previo dice 25-35s; `social-media-niches-2026` dice 35-75s para explainers.
   - Re-evaluar: tras 10 piezas, ver curva de retención por largo. Mantener 25-35s default.

10. **Auto-citar fuentes en captions**
    - El research no lo cubre, pero el risk profile bajo de AI Brief depende de "información verificable con fuente".
    - Re-evaluar: tras 5 piezas, si las captions se sienten cargadas, ver si la fuente va al post mismo, al carrusel, o al newsletter expandido.

## Descartar (bajo valor o no aplica a nuestro caso)

> Findings que se ignoran intencionalmente. Documentar la razón.

1. **Agente Engagement automatizado para auto-replies**
   - Razón: viola política Meta + MASTER_PLAN §9.1. Riesgo asimétrico (perder cuenta).

2. **Stable Diffusion / DALL·E / Sora como pipeline visual primario**
   - Razón: viola constraint "no AI look" + label penalty -15 a -80% reach. production-stack-research previo ya lo descartó.

3. **CapCutAPI como editor primario**
   - Razón: ByteDance ownership + watermark penalty + production-stack-research ya descartó CapCut.

4. **Plan de 8 semanas del research multi-agente**
   - Razón: empieza con infraestructura, no con manual MVP. Conflicto con regla "Manual antes que automatizado".

5. **Bandit / RL desde Fase 1**
   - Razón: engineering theater para escala 12-18 piezas. Posponer a Fase 5+ si demanda real.

6. **Concept "Discipline for Smart Men" / nicho masculinity**
   - Razón: anglo-céntrico, saturado en español, problemático culturalmente. Fuera del posicionamiento sobrio anti-humo de AI Brief LATAM.

7. **Concept "Mystery / disaster casefiles" + "AI Scams / Defense" como nichos**
   - Razón: distraen del posicionamiento de AI Brief LATAM. Si llegan, son para Crypto Brief o property nueva no contemplada.

8. **Concept "Luxury decoded" + "Empires / borders"**
   - Razón: irrelevante al portfolio de 3 properties LATAM.

9. **Cadencia "TT 3/day, IG 2/day + 3 Stories/day, YT Shorts 2/day, X 6-10/day"**
   - Razón: calibrada para creator full-time con team. Imposible para Fase 1 fundador solo.

10. **Costos infraestructura $200-500/mes hobby + $1,000-5,000/mes startup**
    - Razón: production-stack-research locka MVP en $15/mes. La estructura barata es un constraint deliberado, no una limitación.

11. **Bots para inflar comentarios o engagement**
    - Razón: política Meta + ética. No aplicable nunca.

12. **Listicles del tipo "10 prompts para ganar dinero con IA"**
    - Razón: hard NO en brand_voice.md.

13. **Memes baratos + marca de agua de otras plataformas**
    - Razón: hard NO en brand_voice.md.

14. **"AI workflow per profession" sin angle LATAM**
    - Razón: el angle LATAM diferencia. Sin él, AI Brief LATAM se parece a Matt Wolfe en español. Aplicar SOLO si tiene componente regional.

15. **Sumar followers cross-platform como métrica de comparación**
    - Razón: el research creators-ia-espanol-landscape lo hace; es manzanas con peras. Usar funnel real (impressions → newsletter signups → conversion).

## Síntesis del roadmap (round 1: 4 research)

- **6 acciones inmediatas** (1-2 horas de trabajo total, todas reversibles).
- **5 acciones tras 2-3 piezas reales** (esperan data del manual MVP).
- **10 elementos en monitoreo 30 días** (no se tocan ahora pero quedan en mente).
- **15 elementos descartados** con razón documentada para no revisitar.

El roadmap está alineado con la regla central del MASTER_PLAN: **no construir el N+1 hasta que la operación demuestre que hace falta.** La mayoría de los findings de los 4 research se traducen en validaciones del status quo o ajustes menores; los que apuntan a build-más se posponen hasta tener data real del manual MVP.

---

# Addendum — round 2: Multi-agent frameworks + Rundown AI

> Agregado 2026-05-08. Findings de los 2 research adicionales clasificados por momento de aplicación, separados de los de round 1.

## Aplicar ahora (round 2)

> Acciones inmediatas (1-3 horas total) con alta evidencia.

1. **Editar §4.2 del MASTER_PLAN** con la nota: "Para Fase 1-3: single-agent + tools (Camino C). Para Fase 4: evaluar LangGraph (Camino A) cuando la operación demuestre que el control plane simple no alcanza." (delta #17)
   - Costo: 5 min. Reversible. Alta evidencia.

2. **Lockear modelo de monetización dual revenue stream** en §3.1 (no solo "Decisiones abiertas en §11"). Texto sugerido: "Modelo target Fase 8: dual revenue stream — sponsorships + paid tier ($500-$1,000/yr equivalente LATAM, conversion target 0.5-1% de free list). Sponsorships solo es modelo inferior matemáticamente (LTV 2-4× menor)." (delta #19)
   - Costo: 10 min. Reversible. **Cambio más sustantivo del round 2.**

3. **Editar Fase 8 con priorización**: "Posibles tracks (en orden de prioridad: 1) Premium subscription tier / paid community, 2) Sponsorships, 3) Reportes pagos, 4) Cursos/templates, 5) B2B intelligence subscription." Anchor benchmarks Rundown ($999/yr, 5K-7.5K members, $833K rev/empleado, 25-50% margen). (delta #20)
   - Costo: 15 min. Reversible.

4. **Agregar guard a §6.1**: "Antes de construir el set de 9 agentes Fase 4, validar 2 semanas con single-agent + tools (sin framework). Migrar a LangGraph solo cuando: consistency entre 3 properties falla, HITL formal es necesario, o critique loop demanda checkpointing." (delta #22)
   - Costo: 5 min. Reversible. Alta evidencia.

5. **Agregar §9.5 "Drift de voz / quality"**: "Drift de voz de marca por uso de multi-agent es riesgo identificado. Mitigation: prompt caching + Brand Voice Agent + style guide en system prompt + revisión humana periódica + evaluations automáticas (LangSmith o equivalente)." (delta #25)
   - Costo: 10 min. Reversible.

6. **Agregar §4.4 nota de deployment**: "Cuando se migre desde local: Fly.io / Railway / Render como defaults para agent engine. NO Vercel para los runs largos del control plane (sí Vercel para frontend de admin/dashboard)." (delta #18)
   - Costo: 5 min. Reversible.

7. **Cargar Rundown rate card a sources.yaml** con tag `business-pattern`: rundown.ai/advertise-with-us como referencia táctica (regla exclusión sponsors, demographics breakdown, CPMs). No fuente editorial. (delta #24)
   - Costo: 5 min. Reversible.

**Total round 2 acciones inmediatas: ~55 min de edición.**

## Aplicar después de validar con 2-3 piezas reales (round 2)

1. **Decidir orden de canales primary** (delta #21). Disparador: tras 5 piezas en IG, evaluar si LinkedIn español como primary audience-building da mejor conversion → newsletter que IG. Discutir con Manuel antes de Fase 1.5.

2. **Empezar Camino C (single-agent + tools sin framework)** como implementation real cuando se llegue a Fase 4. Disparador: tras Fase 1 manual MVP completo (12-18 piezas) y workflow analysis Fase 2, evaluar si single-agent es viable para Fase 3+.

3. **Evaluar uso de Claude search/research vs adopción de Perplexity/Tavily** (delta #27). Disparador: tras 5 piezas, medir cuántas veces el fact-check con Claude solo fue insuficiente. Si <20%, Claude solo. Si >20%, considerar Perplexity.

4. **Evaluar HeyGen + Lindy como tools auxiliares** del stack Rundown documentado. HeyGen para video avatar (cuidado: viola "no AI look" del production-stack-research). Lindy para scheduling sponsor outreach (Fase 8 monetización). Disparador: cuando se diseñe outreach de sponsors.

## Monitorear durante 30 días (round 2)

1. **Microsoft Agent Framework** GA Q1 2026 — si llega y es viable con stack non-Azure, evaluar como alternativa a LangGraph. Improbable que cambie el default.

2. **Claude Agent SDK V2** — el research nota que V2 emerge paralelo a V1. Esperar estabilidad antes de adoptar Camino B (Claude Agent SDK con subagents).

3. **Vercel Workflow DevKit** — el research multi-agent NO lo evalúa, gap notable. Si Vercel publica caso real de WDK como agent orchestrator, evaluar como alternativa a LangGraph (mismo deployment como el resto del stack).

4. **CrewAI Cognition Memory** — la API unificada de memoria (recently launched) podría madurar y volver CrewAI más viable. Improbable que cambie default LangGraph pero vale notar.

5. **Mafia IA + Rundown como benchmarks comparativos** — re-evaluar trimestralmente. Mafia IA en español/LATAM, Rundown global. Mafia IA podría dar mejor calibración LATAM.

6. **Transformación del paid product platform** — Rundown construyó University custom-built. Cuando AI Brief LATAM llegue a 1-3K subs y considere paid tier, decidir: Beehiiv premium vs Skool vs Circle vs custom. Default conservador: Beehiiv premium primero.

## Descartar (round 2)

> Findings de los 2 research que se ignoran intencionalmente.

1. **AutoGen como framework** — maintenance mode desde 1 oct 2025. Cero pa'lante.

2. **Mastra (TypeScript-only)** — rompe Python preference. Rechazado a menos que se invierta la decisión meta-arquitectónica del stack.

3. **OpenAI Agents SDK con Claude por debajo** — forzado, pierde features Anthropic. Sin sentido.

4. **CrewAI Enterprise pricing path ($60k-$120k/yr)** — irrelevante para operador solo. OSS self-hosted si se eligiera CrewAI, lo cual es improbable.

5. **CrewAI como framework target para producción seria** — research dice "equipos migran a LangGraph cuando llegan a producción". Si se quiere atajo MVP de 1 día, CrewAI sirve, pero no para Fase 4+ formal.

6. **Replicar founder access tier 1 (Zuckerberg, Altman, etc.)** — la ventana cerró. Para AI Brief LATAM, el equivalente realista sería founders LATAM (Bitso, Stori, Kavak, etc.) — distinto playbook.

7. **First-mover en general AI newsletter** — saturado. Solo vertical AI tiene espacio.

8. **Estrategia "100% sponsorships sin paid tier" (modelo Superhuman AI)** — matemática inferior. LTV 2-4× menor con misma base de subs. Descartar como modelo target.

9. **Spend 25-50% del revenue en Meta Ads agresivamente desde día 1** — el modelo Rundown asume RPS competitivo *ya validado*. Para AI Brief LATAM, paid acquisition tiene sentido solo después de validar conversión orgánica y RPS. Posponer a Fase 8.

10. **Adoptar Microsoft Agent Framework prematuramente** — está en preview, Azure-céntrico. Stack del proyecto es Vercel/Supabase/Anthropic. Wait & see.

## Síntesis del roadmap (round 2)

- **7 acciones inmediatas** adicionales (~55 min total).
- **4 acciones tras 2-3 piezas reales** o triggers específicos.
- **6 elementos en monitoreo 30 días.**
- **10 elementos descartados** con razón documentada.

El round 2 trae **un cambio sustantivo** que no estaba en round 1: lockear dual revenue stream como modelo target de monetización en lugar de dejarlo como "decisión Fase 8 abierta". Es el delta de mayor impacto financiero a largo plazo.

El resto son refinamientos de stack (single-agent → LangGraph como secuencia explícita) y guardrails (drift como riesgo §9, deployment defaults).

**Total acumulado (round 1 + round 2):**
- 13 acciones inmediatas (~75 min de edición total)
- 9 acciones tras 2-3 piezas reales
- 16 elementos en monitoreo
- 25 elementos descartados con razón documentada
