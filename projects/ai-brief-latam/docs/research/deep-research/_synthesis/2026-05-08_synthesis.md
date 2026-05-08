# Síntesis comparativa de los 4 Deep Research

**Fecha:** 2026-05-08
**Documentos analizados:** 4 deep research nuevos + 3 research previos del proyecto

## Lo que TODOS los research confirman

> Confirmaciones cruzadas (aparecen en ≥2 documentos), priorizadas por su peso para AI Brief LATAM.

1. **El activo central es la newsletter, no la cuenta de Instagram.**
   - `social-media-niches-2026`: "the winning creator is an editorial system that uses short-form for top-of-funnel and email/community for retention and monetization."
   - `creators-ia-espanol-landscape`: "newsletters dominan claridad de propuesta y monetización directa."
   - `format-and-voice-research` (previo): "Multi-channel strategy. NO all-in en Instagram. El activo central es la newsletter (Beehiiv)."
   - **Peso: alto.** 3 fuentes independientes coinciden. Decisión de MASTER_PLAN reforzada.

2. **Franchise / formato repetible > experimentación libre.**
   - `social-media-niches-2026`: "the best-performing architecture across almost all the winning niches is a franchise, not a random post."
   - `creators-ia-espanol-landscape`: cuentas con propuesta clara ("Newsletter más grande de IA", "Newsletter de referencia") superan a las que rotan formato.
   - `format-and-voice-research` (previo): "Hallazgo #1 — Smart Brevity es EL framework para news briefs."
   - **Peso: alto.** Aplicar a Fase 1: lockear 2-3 franquicias antes de publicar.

3. **Saves > follows en algoritmo 2026; watch time es la métrica madre.**
   - `social-media-niches-2026`: "I would weight metrics in this order: watch time, then shares/saves, then follows, then raw views."
   - `format-and-voice-research` (previo): "Saves y shares pesan más que likes."
   - **Peso: alto.** Confirmado y operacionalizado en brand_voice.md.

4. **AI-assisted, no AI-generated. "Made with AI" es penalizable.**
   - `social-media-niches-2026`: "creators who add real synthesis and editorial judgment" vs "low-originality content farms".
   - `production-stack-research` (previo): "Pure AI-generated content: hasta -80% reach… AI-ASSISTED text NO requiere label".
   - `multi-agente-instagram-automation` paradójicamente lo menciona pero su arquitectura recomendada lo viola.
   - **Peso: alto.** Decisión proyecto sólida; el research multi-agente queda como advertencia de qué NO hacer.

5. **Hueco de mercado: rigor analítico + gobernanza + sectorial + ROI en español/LATAM.**
   - `creators-ia-espanol-landscape`: 5 huecos identificados convergen aquí.
   - `fintech-insurtech-crypto-latam`: "no existe newsletter dominante en español que conecte funding+producto+regulación+IA+unit economics."
   - **Peso: alto.** Validación cruzada del posicionamiento de AI Brief LATAM.

6. **Vertical / sectorial > generalista.**
   - `social-media-niches-2026`: "AI for one profession instead of generic AI" como underexploited angle.
   - `creators-ia-espanol-landscape`: hueco #1 = "operación real por sector" (retail, legal, salud, etc.).
   - **Peso: media-alta.** Hipótesis razonable. Aplicar como sub-franquicia ("AI para founders LATAM") sin canibalizar la propuesta general.

7. **LATAM benchmarks realistas: 12-30K es top tier, 100K+ es excepcional.**
   - `latam-specific-research` (previo): "12-30K = top tier (Ecosistema Startup, Startupeable). 100K+ = excepcional".
   - `creators-ia-espanol-landscape`: "DotCSV no tiene par regional latam… 100K+ es excepcional".
   - **Peso: alto.** Anclaje mental para targets MASTER_PLAN, ya documentado en brand_voice.md.

## Contradicciones entre research

| # | Tema | Research A dice | Research B dice | Cuál es más confiable y por qué |
|---|---|---|---|---|
| 1 | **Cadencia ideal de publicación** | `social-media-niches-2026`: "TT 3/day, IG 2 Reels/day + 3 Stories/day, YT Shorts 2/day, X 6-10 posts/day, 1 newsletter/week" | `format-and-voice-research` (previo): no especifica daily volume tan alto; MASTER_PLAN F1: "3-5 piezas/semana en IG, 1 newsletter/week" | **MASTER_PLAN gana.** El primero está hecho para creators full-time con team; ignora límite operacional de un fundador solo. La cadencia masiva burnout-driven es un patrón conocido y rara vez sostenible. |
| 2 | **AI generation primaria de visuales** | `multi-agente-instagram-automation`: recomienda Stable Diffusion + DALL·E + Sora como pipeline default | `production-stack-research` (previo): rechaza explícitamente AI primary por -80% reach + label penalty | **production-stack-research gana.** Tiene fuentes específicas (Mosseri statements, label policy, ScienceDirect study). El multi-agente usa pseudo-citas no auditables. |
| 3 | **CapCut como editor** | `multi-agente-instagram-automation`: CapCutAPI como editor primario | `production-stack-research` (previo): CapCut descartado (ByteDance, watermark -72% reach) | **production-stack-research gana.** Razones operativas concretas (privacy + reach penalty). El multi-agente no contempla esos costos. |
| 4 | **Bots de auto-reply a comentarios** | `multi-agente-instagram-automation`: agente Engagement automatizado con respuestas IA | MASTER_PLAN 9.1: "Nunca usar bots de follow/unfollow ni engagement automation prohibido por Meta" | **MASTER_PLAN gana.** Política Meta vigente. Riesgo de baneo es asimétrico (pierde toda la cuenta). |
| 5 | **Difficulty score "AI workflows" 4/10** | `social-media-niches-2026`: AI workflows es "easy to produce" (rank #1) | `creators-ia-espanol-landscape`: 4 posicionamientos saturados, AI generalista es uno | **creators-ia-espanol gana en señal de mercado.** Bajo esfuerzo de producción ≠ bajo esfuerzo de diferenciación. La saturación competitiva no se captura en el "difficulty" del primero. |
| 6 | **Saturación del nicho IA** | `social-media-niches-2026`: AI risk score 4/10, saturation 8/10 — pero ranquea #1 | `creators-ia-espanol-landscape`: saturación clara, hueco está en sub-verticales (sectorial / governance / LATAM) | **creators-ia-espanol gana en specificidad regional.** El primero opera en mercado anglo donde la barrera de saturación se siente diferente. En español el sample es más chico y la diferenciación viene del ángulo, no del volumen. |
| 7 | **Quién es "el benchmark" para AI newsletter** | `format-and-voice-research` (previo): Rundown AI 436K IG / 2M+ subs como benchmark | `creators-ia-espanol-landscape`: "DotCSV no tiene par regional latam, 400K+ no existe en LATAM" | **No contradicen — son contextos distintos.** Rundown es benchmark global; no hay equivalente LATAM. Conclusión: AI Brief LATAM no compite contra Rundown sino contra DotCSV / Mafia IA / Explicable. |

## Lo que solo aparece en UN research

> Insights únicos. Cada uno evaluado: oro / útil con cuidado / ruido.

- **`fintech-insurtech-crypto-latam`: "Capital stack para fintech (venture debt, FIDCs, warehouse, securitización)" como sub-vertical editorial underserviced.**
  - **Veredicto: oro.** Es específico, verificable como hueco (no hay newsletter en español sobre esto), y tiene audiencia clara (CFOs, treasury, debt funds). Aplicable a Crypto Brief o como sección de AI Brief si llega a tocar finanzas.

- **`fintech-insurtech-crypto-latam`: "Data moat > model moat" como ángulo editorial recurrente.**
  - **Veredicto: útil con cuidado.** Es un take crítico que diferencia de discurso hype. Aplicable como ángulo en piezas sobre IA aplicada a finanzas. Riesgo: que sea generalización; verificar caso por caso.

- **`creators-ia-espanol-landscape`: Mafia IA como benchmark de monetización newsletter (premium + comunidad + paid lifetime).**
  - **Veredicto: oro.** Modelo concreto a estudiar para Fase 8 monetización. Diferente de Stratechery (suscripción flat) y de Beehiiv ads. Demanda análisis post-by-post.

- **`social-media-niches-2026`: 4 format pillars (35-75s explainer / chart-map breakdown / ranking-mythbuster / "what this means for you").**
  - **Veredicto: oro.** Set acotado, testeable, y compatible con brand_voice.md. Mejor punto de partida operacional que "experimentar todo."

- **`social-media-niches-2026`: "Concept 10 — AI Scams, Deepfakes, Defense" como nicho subexplotado.**
  - **Veredicto: ruido para AI Brief LATAM.** Es geopol/security adyacente. Distrae del posicionamiento. Si llegara a aplicarse, sería más para Crypto Brief (scams) que AI Brief.

- **`multi-agente-instagram-automation`: lista de 10 agentes con responsabilidades + reglas IF-THEN.**
  - **Veredicto: vocabulario útil, arquitectura no.** Los nombres y responsabilidades coinciden parcialmente con los 9 agentes del MASTER_PLAN. Útil como vocabulario comparativo. La arquitectura propuesta (n8n nuevo, sin reutilizar core/) es ruido.

- **`multi-agente-instagram-automation`: bandit / RL para hook optimization.**
  - **Veredicto: ruido.** Engineering theater para escala 12-18 piezas Fase 1. Posponer hasta tener data suficiente (Fase 5+).

- **`fintech-insurtech-crypto-latam`: "Stablecoins B2B en LATAM" como vertical underserviced.**
  - **Veredicto: oro para Crypto Brief LATAM.** Coincide con dirección estratégica y hay demanda CFO/treasury verificable. Importante para Property #2.

- **`creators-ia-espanol-landscape`: hueco "agentes y automatización con profundidad intermedia".**
  - **Veredicto: oro.** Es exactamente lo que AI Brief LATAM puede hacer al cubrir Project Autopilot mismo como caso. Auto-referencial pero diferenciador.

## Lo que NO está en ningún research pero esperabas que sí

> Gaps materiales para el proyecto.

1. **Caso real LATAM operando un sistema multi-agente para contenido.** Ningún research cita una operación regional con métricas. Estamos sin benchmark directo.
2. **Distribución por canal vs conversión por canal.** Research mide alcance; nadie mide funnel completo (impressions → newsletter signups → producto pagado). Sigue siendo el dato más importante y el menos disponible.
3. **Costo real de produc por pieza** (tiempo + tools). Manual MVP del proyecto va a generar este dato, pero no hay anclaje externo previo.
4. **Política de Meta Graph API actualizada 2026 sobre publishing automation.** Cuál es exactamente el límite entre "automation OK" (Buffer) y "automation prohibido" (bots). El research multi-agente lo asume pero no lo documenta.
5. **Comparativa de scheduling tools 2026** con feature matrix actualizado (Buffer vs Later vs Metricool vs Publer). MASTER_PLAN lo dejó como decisión Fase 1 — ningún research lo cubre.
6. **Datos de retention real de newsletters por nicho** en español (open rate, churn, engagement por industry). Mafia IA y Explicable son únicos puntos de referencia parciales.
7. **Cobertura de creators IA en portugués brasileño**, importante porque Brasil es 50% del fintech LATAM y mercado adyacente para Crypto Brief.
8. **Estudio de portafolios de newsletter (autor único con varias propiedades)** — Beehiiv permite multi-pub pero no hay caso documentado en español de operar 3 nichos en paralelo.

## Comparación con research previo del proyecto

> 3 research previos en `projects/ai-brief-latam/research/` (2026-05-07).

### Confirmaciones (los nuevos refuerzan los previos)

- **Smart Brevity / framework editorial**: `social-media-niches-2026` confirma con concept de "franchise" + 4 format pillars. Aplicación: lockear formats antes de publicar.
- **Newsletter como activo central, no IG**: ambos confirman. `creators-ia-espanol-landscape` muestra que newsletters dominan monetización en español.
- **Saves > follows + watch time como métrica madre**: confirmado por `social-media-niches-2026`.
- **Benchmarks LATAM 12-30K top tier**: `creators-ia-espanol-landscape` lo replica explícitamente.
- **AI-asistido > AI-generado**: `social-media-niches-2026` y la arquitectura del proyecto coinciden. El research multi-agente Instagram va en sentido contrario y debe descartarse en sus recomendaciones de pipeline visual/audio.

### Contradicciones (los nuevos cuestionan los previos)

- **Ningún contradicción material directa** entre research previos y deep research nuevos sobre AI Brief LATAM core.
- **El research multi-agente Instagram contradice production-stack-research** en CapCut, AI generation, y filosofía de automatización — pero este research no era para AI Brief, era genérico. Su valor para el proyecto es limitado y debe filtrarse.

### Ampliaciones (los nuevos abren áreas no cubiertas antes)

- **`creators-ia-espanol-landscape` introduce 5 huecos de posicionamiento concretos** que `latam-specific-research` no había mapeado (sectorial, governance/ROI, middle-market LATAM, anti-hype, agentes intermedios). Aporta señal de diferenciación más fina.
- **`fintech-insurtech-crypto-latam` aporta inputs estratégicos para Property #2 (Crypto Brief LATAM)** y Property #3 (Startup Radar LATAM) — research previo se enfocó en property #1.
- **`social-media-niches-2026` introduce el concepto de "kill criteria" (15-20 posts kill format, 50 posts kill concept)** como heurística de validación — útil aunque no validada empíricamente. Posible adopción en Fase 1 con número ajustado.
- **Nuevo benchmark Mafia IA (monetización newsletter mature)** — research previo solo mencionaba Digital Brain como newsletter alta. Mafia IA tiene modelo más comparable a lo que AI Brief LATAM puede aspirar.

### Sin movimiento (lo que ya estaba decidido y los nuevos no afectan)

- Voz Smart Brevity + Morning Brew casual ✓
- Español neutro LATAM ✓
- Reels 25-35 seg con hook brutal en 3s ✓
- Caption <150 chars ✓
- Hooks framework Rufusocial (atención + tensión + promesa) ✓
- Manuel como locutor humano default + ElevenLabs backup ✓
- Stack producción $15/mes (Inoreader + Claude Pro + Canva Pro + Beehiiv free) ✓
- Caras reales > postureo pulido en LATAM ✓

## Conclusión de la síntesis (round 1: 4 research)

Los 4 nuevos research, leídos en conjunto con los 3 previos, **convergen fuerte sobre el posicionamiento de AI Brief LATAM** y **no obligan a cambios estructurales en MASTER_PLAN**. La mayoría de los insights útiles son refuerzos o sub-tácticas.

Los 2 cambios más sustantivos son:
1. **Adoptar 4 format pillars como restricción Fase 1** (en lugar de "experimentar todo").
2. **Documentar explícitamente el rechazo de auto-replies + AI generation primary** como parte del compliance del proyecto, ahora que existe un research que sugiere lo contrario.

El research multi-agente Instagram es la fuente más débil y debe tratarse como **antiejemplo documentado** de qué dirección NO tomar.

---

# Addendum — round 2: Multi-agent frameworks + Rundown AI business model

> Agregado 2026-05-08 tras procesar 2 research adicionales:
> - `2026-05-08_multi-agent-frameworks.md`
> - `2026-05-08_rundown-ai-business-model.md`

## Convergencias adicionales (involucran los 2 nuevos)

1. **Vertical AI > general AI para newcomers — ahora con peso triple.**
   - `social-media-niches-2026`: "AI for one profession instead of generic AI"
   - `creators-ia-espanol-landscape`: 4 posicionamientos saturados, 5 huecos
   - `rundown-ai-business-model`: "El nicho está saturado. Para nuevos entrants, el play es vertical AI — no general AI. La ventana cerró"
   - **Peso: muy alto.** 3 fuentes independientes coinciden. Implicación directa para AI Brief LATAM: el ángulo LATAM + sectorial es no-negociable como diferenciador.

2. **AI tooling stack como tabla, no diferenciador.**
   - `production-stack-research` (previo): stack lockeado en $15/mes (Claude + Canva + Beehiiv + Inoreader).
   - `rundown-ai-business-model`: "AI content production es ya tabla — no diferenciador"; el stack documentado de Rundown (Claude + HeyGen + ElevenLabs + Lindy) coincide ~80% con decisiones del proyecto.
   - **Peso: alto.** Validación cruzada de las decisiones de stack del proyecto. Lo diferenciador es el ángulo editorial y el access, no el stack.

3. **Bootstrapped + small team es viable hasta múltiples millones de ARR.**
   - `rundown-ai-business-model`: $10M ARR + 12 empleados + bootstrapped, $833K revenue/empleado.
   - `creators-ia-espanol-landscape`: Mafia IA con monetización mature sin VC documentado.
   - **Peso: media-alta.** Confirma decisión implícita del MASTER_PLAN de no buscar VC en fases 1-6. Anchor financiero para Fase 8.

4. **"Empezar single-agent y validar antes de invertir en framework" coincide con principio del MASTER_PLAN.**
   - `multi-agent-frameworks`: "Tu caso no es claramente multi-agent… empieza single-agent + tools 2 semanas para validar"
   - MASTER_PLAN §6.3: "no construir el agente N+1 hasta que la operación demuestre que el N+1 hace falta"
   - **Peso: alto.** No es nueva idea, pero el research da framework analítico (Anthropic 3 criterios) para tomar la decisión, no solo intuición.

## Contradicciones nuevas (round 2 vs lo previo)

| # | Tema | Research dice | MASTER_PLAN / status quo dice | Resolución sugerida |
|---|---|---|---|---|
| 8 | **Orden de canales: Newsletter + IG paralelos vs primary platform → newsletter secondary** | `rundown-ai-business-model`: "Newsletter es monetization layer encima de audience-building engine en otra plataforma (X/LinkedIn primary)". El newsletter no debe ser el activo de adquisición primario. | MASTER_PLAN §3.1: "Cadencia inicial: 3-5 piezas/semana en Instagram, 1 newsletter weekly" — implica IG + newsletter en paralelo desde día 1. | **Tensión real.** Resolución: mantener IG en Fase 1 (validar voz/operación) pero **considerar LinkedIn español como primary audience-building** simultáneo o como pivot post-Fase 1. Discutir con Manuel. La regla "una property antes que tres" sigue, pero "una plataforma de adquisición primaria" no es la misma decisión. |
| 9 | **Modelo de monetización: solo sponsorships vs dual stream** | `rundown-ai-business-model`: 50/50 sponsorships + University ($999/yr paid product). LTV 2-4× vs solo-ads. | MASTER_PLAN §3.1: monetización mencionada genéricamente, sin especificar mix. Fase 8 abre tracks (sponsorships, premium subscription, etc.) sin priorización. | **No es contradicción dura, es subespecificación.** Resolución: marcar dual stream como modelo target en Fase 8, con paid tier ($500-$1,000/yr equivalente LATAM) como driver financiero principal, no las sponsorships. |
| 10 | **Stack del control plane: Python directo vs framework** | `multi-agent-frameworks`: LangGraph como recomendación a mediano plazo (Camino A); single-agent + tools como punto de partida (Camino C). | MASTER_PLAN §4.2: "LLM principal: Claude (Anthropic API directa) para v1. Más simple y controlable que SDKs intermedios." | **Coherencia parcial.** El "API directa" del MASTER_PLAN coincide con Camino C (single-agent + tools). LangGraph como Camino A llega cuando los 9 agentes se construyan en serio (Fase 4+). No hay contradicción, solo un orden temporal a explicitar. |

## Lo que solo aparece en UN de los 2 nuevos research

> Insights únicos de los 2 documentos round 2.

- **`multi-agent-frameworks`: el check Anthropic de 3 criterios** (context pollution / paralelismo / tool selection) como framework decisional para multi-agent justification.
  - **Veredicto: oro.** Convertir en checklist explícito al diseñar Fase 4. "¿Justifica este caso multi-agent o single-agent + más tools?"

- **`multi-agent-frameworks`: deployment recommendation Fly.io/Railway/Render para agent engine, NO Vercel.**
  - **Veredicto: útil para Fase 5+.** El proyecto está local hasta que demande cloud. Cuando llegue ese momento, hay default razonable.

- **`multi-agent-frameworks`: AutoGen en maintenance mode + Mastra TS-only descartados explícitamente.**
  - **Veredicto: oro defensivo.** Cierra 2 paths que estaban abiertos en el ecosistema y evita perder tiempo evaluándolos.

- **`multi-agent-frameworks`: Claude Agent SDK como Camino B (intermedio).**
  - **Veredicto: útil con cuidado.** Opción que el MASTER_PLAN no contemplaba. Vale documentar pero LangGraph sigue siendo Camino A para el caso del proyecto (multi-modelo opcional, control fino, Postgres saver).

- **`rundown-ai-business-model`: regla "no other AI newsletters as sponsors" en rate card.**
  - **Veredicto: oro táctico para Fase 8.** Cuando AI Brief LATAM abra advertising, copiar esta regla.

- **`rundown-ai-business-model`: ratio $833K revenue/empleado como benchmark de eficiencia.**
  - **Veredicto: anchor mental.** Si AI Brief LATAM llegara a $500K-$1M ARR, equipo de 1-2 personas full-time es realista. Útil para no over-hire.

- **`rundown-ai-business-model`: University custom-built (no Skool/Circle) en escala.**
  - **Veredicto: implicación Fase 7-8.** El paid product platform se construye in-house cuando llega a escala. No es decisión de día 1, pero es el destino. Implica diseñar el datamodel desde Fase 4-5 con esa salida en mente.

- **`rundown-ai-business-model`: The Neuron acquired by TechnologyAdvice (ene 2025) a 500K subs.**
  - **Veredicto: anchor de exit value.** 500K subs = adquisición. Para AI Brief LATAM (target 12-30K en 12-18 meses) es 1/15 a 1/40 de eso, pero da orden de magnitud para conversación M&A futura.

- **`rundown-ai-business-model`: dual revenue stream + reinvest 25-50% en paid acquisition como flywheel matemático.**
  - **Veredicto: oro.** El argumento financiero más fuerte de los 6 research. Convierte la decisión de "premium subscription tier" (Fase 8 MASTER_PLAN) de opcional a estructural.

## Gaps que se cerraron parcialmente

1. **"Caso real operando un sistema multi-agente para contenido"** — sigue sin haber caso LATAM, pero ahora hay benchmark global (Rundown) con métricas. El playbook está claro aunque no haya replicación regional.
2. **Decisión de framework multi-agent** — antes era hueco; ahora hay recomendación explícita (single-agent → LangGraph) con criterios.

## Gaps que siguen abiertos

1. **Comparativa de scheduling tools 2026** (Buffer vs Later vs Metricool vs Publer) — ningún research lo cubre.
2. **Datos de retention real de newsletters en español** (open rate, churn, engagement por nicho) — Rundown da el benchmark global pero no LATAM.
3. **Vercel Workflow DevKit** como alternativa a LangGraph — el research no lo evalúa, sigue como gap.
4. **Costos reales de produc por pieza en LATAM** (tiempo + tools) — Manual MVP del proyecto va a generarlo.

## Comparación con research previo del proyecto (round 2)

### Confirmaciones cruzadas

- **`rundown-ai-business-model` valida `production-stack-research`** en el stack tooling: Claude como editor central + ElevenLabs como voz backup ✓. HeyGen y Lindy son nuevas referencias que vale considerar como tools auxiliares.
- **`rundown-ai-business-model` extiende `format-and-voice-research`**: este último mencionaba Rundown como benchmark de formato (sin emojis, posteo masivo); ahora hay dimensión financiera + estructural completa.
- **`multi-agent-frameworks` valida la decisión del proyecto sobre Python + Anthropic API directa** (§4.2 MASTER_PLAN). Camino C del research = exactamente lo que el MASTER_PLAN ya plantea para v1.

### Contradicciones nuevas con research previo

- Ninguna contradicción dura. Las 3 tensiones identificadas (orden de canales, modelo de monetización, stack del control plane) son sub-especificaciones del MASTER_PLAN, no contradicciones con research previo.

### Ampliaciones

- **Dimensión financiera explícita** que ningún research previo había dado. `format-and-voice-research` mencionaba Rundown como modelo a seguir; ahora se sabe la matemática del flywheel.
- **Framework decisional para multi-agent** (Anthropic 3 criterios) que no existía. Pasa del campo "intuición" al campo "evaluación estructurada".

## Conclusión addendum (round 2)

Los 2 research adicionales **profundizan** sin contradecir el resto. Cierran gaps importantes de stack (multi-agent decision) y de modelo de negocio (Rundown business model deep dive). Convergen con la línea editorial-LATAM-sectorial-anti-hype del proyecto.

**El cambio más sustantivo que emerge del round 2:**
- **Considerar dual revenue stream (sponsorships + paid tier $500-$1,000/yr) como arquitectura de monetización target** desde el diseño, no como decisión Fase 8 abierta.

**Tensiones nuevas a discutir con Manuel:**
1. Orden de canales (¿LinkedIn español como primary audience-building, o IG?)
2. Cuándo introducir LangGraph vs quedarse en single-agent + tools

Ambas tensiones son **decisiones de Manuel**, no derivables de research. El roadmap las marca como "discutir antes de Fase 4-5".
