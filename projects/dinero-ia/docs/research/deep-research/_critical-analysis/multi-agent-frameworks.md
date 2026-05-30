# Análisis Crítico — Multi-Agent Frameworks

> Documento revisado: `2026-05-08_multi-agent-frameworks.md`
> Tema: análisis técnico comparativo de frameworks multi-agent (LangGraph, CrewAI, AutoGen, Claude Agent SDK, OpenAI Agents SDK, Mastra) para producción editorial.
> **Relevancia para AI Brief LATAM:** alta. Toca directamente la decisión de stack para CAPA 2 del MASTER_PLAN (content production agents).

## Resumen ejecutivo (3-5 líneas)

El research recomienda **LangGraph (Python) con Claude Sonnet 4.5 vía `langchain-anthropic`**, persistencia en Supabase Postgres y deployment fuera de Vercel (Fly.io / Railway / Render) para runs largos. Antes de elegir framework, plantea seriamente **single-agent + tools** como alternativa válida para 6-15 piezas/día con un operador solo. Descarta AutoGen (maintenance mode), OpenAI Swarm (deprecado), Mastra (TS-only). La conclusión más fuerte es honesta: **el caso del proyecto está en la frontera multi-agent vs single-agent**, y el research recomienda **empezar single-agent 2 semanas para validar antes de invertir en framework**.

## Calidad de fuentes

**Fuentes primarias citadas:**
- Anthropic engineering: "Building Effective Agents" (dic 2024) y "When to use multi-agent systems" (2025)
- Anthropic blog: "How we built our multi-agent research system" (cita de 15× tokens vs chatbot)
- Repos GitHub oficiales (LangGraph, CrewAI, AutoGen, Claude Agent SDK, OpenAI Agents SDK, Mastra)
- Anuncios oficiales: AutoGen → Microsoft Agent Framework (1 oct 2025)
- Documentación oficial Anthropic, LangChain, CrewAI
- Releases públicos (LangGraph v1 GA mayo 2025, Claude Agent SDK 29 sep 2025, Mastra v1.0 ene 2026)

**Fuentes secundarias citadas:**
- ZenML, Lindy (blog posts) para pricing CrewAI Enterprise
- Anuncios de empresas adoptantes (Klarna, LinkedIn, Uber, Replit, JPMorgan)
- Stars/downloads de GitHub y npm/PyPI
- Reportes financieros de funding (CrewAI $18M, Mastra $35.5M)

**Fuentes faltantes que esperarías:**
- **Benchmarks de performance** entre frameworks en una tarea editorial real (latencia, retry rate, output quality)
- **Estudios independientes** de costos a escala (ningún cost benchmark más allá de "15× tokens")
- **Datos primarios de LinkedIn/Indeed** para job market signal — el research lo confiesa
- **Postmortems concretos** de equipos que migraron de CrewAI → LangGraph (claim repetido pero sin caso documentado)
- **Documentación de Vercel runtime limits** específica que justifique "no Vercel para LangGraph engine" — es opinión técnica del autor
- **Comparativa de Microsoft Agent Framework (preview)** frente a LangGraph — ausente, lo cual es razonable porque MAF está en preview

**Score de calidad de fuentes: alto.** El research es honesto sobre sus limitaciones (caveats al final), distingue claramente hechos vs opiniones, cita la guía oficial de Anthropic. Los rangos de pricing CrewAI Enterprise están marcados como "blog posts terceros". El sesgo de framework selection está auto-confesado al final. Es uno de los research más metodológicamente sólidos del set de 6.

## Hechos verificables vs opiniones

| Afirmación | Tipo | Confiabilidad |
|---|---|---|
| LangGraph llegó a v1.0 GA en mayo 2025 | Hecho | Alta — release público |
| AutoGen está en maintenance mode desde 1 oct 2025 | Hecho | Alta — anuncio oficial Microsoft |
| Claude Agent SDK lanzado 29 sep 2025 | Hecho | Alta — anuncio Anthropic |
| OpenAI Swarm deprecado | Hecho | Alta — repo oficial |
| Mastra v1.0 enero 2026, $35.5M raised | Hecho | Alta — TechCrunch + sitio oficial |
| Klarna, LinkedIn, Uber, Replit, Elastic usan LangGraph | Hecho | Alta — case studies públicos |
| ~400 empresas usan LangGraph Platform | Hecho declarado | Media — número marketing LangChain |
| CrewAI ~48k stars, 27M PyPI downloads | Hecho | Alta — métricas públicas GitHub/PyPI |
| CrewAI Enterprise $60k–$120k/año | Hecho con fuente blanda | Media — blog terceros, no oficial |
| "15× más tokens que chatbot estándar" para multi-agent | Hecho con fuente | Alta — Anthropic post oficial |
| "LangGraph es el más adoptado en enterprise" | Opinión analítica con respaldo | Media-alta — adoptantes documentados pero "más adoptado" no medido |
| "Equipos migran de CrewAI a LangGraph cuando llegan a producción seria" | Opinión / observación | Baja-media — sin caso documentado |
| "Tu caso no es claramente multi-agent" (recomendación single-agent inicial) | Opinión analítica | Alta — derivada correctamente del framework Anthropic |
| "LangGraph: curva de 1-3 días productivo, 1-2 semanas dominio" | Estimación de autor | Media — sin data, pero plausible |
| "Vercel no es ideal para agent engine, usar Fly.io/Railway/Render" | Opinión técnica | Media — el research lo marca como opinión |

## Afirmaciones débiles o cuestionables

1. **"~400 empresas en producción"** es métrica de LangChain, no auditada externamente. Vale como signal direccional, no como tamaño de mercado.
2. **"Equipos migran de CrewAI a LangGraph"** se afirma sin caso documentado. Es probable verbal en la comunidad, pero no en el research como evidencia.
3. **"30% menos boilerplate Claude Agent SDK vs LangGraph"** es estimación sin medición.
4. **El job market signal** se confiesa como anecdótico — útil saber pero no decisivo.
5. **"Mastra crece 300k weekly npm downloads"** sería más útil con tendencia (¿desde cuándo?). Un crecimiento explosivo reciente es distinto a base estable.
6. **"Recomendación de Fly.io/Railway/Render"** es opinión sobre deployment shape de agentes, no comparativa cuantitativa con Vercel Functions o Vercel Agents (Workflow DevKit).
7. **"Microsoft Agent Framework GA Q1 2026"** depende de comunicación corporate; ese tipo de fechas suele deslizar.
8. **No evalúa explícitamente Vercel Workflow DevKit** como alternativa, aunque Vercel está en el stack target — gap notable.

## Contradicciones internas

- **Sección 6.2 recomienda LangGraph (Camino A)** pero **§6.3 recomienda Camino C primero (single-agent sin framework)**. No es contradicción real, es secuencia (single-agent → LangGraph), pero el TL;DR pone "LangGraph" como recomendación principal sin esa cualificación temporal. Lectura rápida arrastra al lector hacia el wrong default.
- **CrewAI descrito como "atajo razonable si quieres MVP en horas"** y simultáneamente "te va a doler en producción seria". El research no resuelve si para 2-week validación CrewAI no sería superior a LangGraph (rapidez de MVP > control de estado).
- **"Trade-off central: 15× más tokens"** y luego "para 2-5 piezas/día el costo NO es problema". Si no es problema, ¿por qué se cita como trade-off central? El argumento real es complejidad de debug, no costos. Mezcla framings.

## Insights genuinamente útiles

1. **El check Anthropic de 3 criterios** (context pollution / paralelismo / tool selection) aplicado al caso del proyecto da resultado claro: NO es claramente multi-agent. Aplicación directa: revisar §6 del MASTER_PLAN ("9 agentes MVP") con esa lente.
2. **Pattern "kernel = system prompt + tools, propiedades = agent definitions con instructions distintas"** es una traducción operativa simple del MASTER_PLAN 3-capas a un single-agent SDK. Reduce complejidad sin perder separación.
3. **Camino C (single-agent + tools, validar 2 semanas)** es exactamente coherente con la regla del MASTER_PLAN "no construir N+1 hasta demostrar necesidad". Convierte la decisión de framework en una decisión post-validación, no pre-construcción.
4. **LangGraph + Postgres saver compatible con Supabase** valida la decisión de Supabase del proyecto. Útil cuando se llegue a Fase 4.
5. **Deployment recommendation: Fly.io/Railway/Render para engine, no Vercel** afecta directamente §4.2 del MASTER_PLAN ("v1 storage local; migración a algo serio solo si demanda"). Cuando se migre, hay un default razonable.
6. **Identificación de AutoGen como dead-end (maintenance mode) y Mastra como TS-only** evita 2 paths que estaban abiertos a discusión en el ecosistema.
7. **Claude Agent SDK como Camino B** es una opción intermedia que el MASTER_PLAN no contemplaba explícitamente. Vale la pena documentarla aunque la decisión final sea LangGraph.
8. **Trade-off complejidad-debug-y-drift-de-voz** como riesgo real de multi-agent — bien identificado para operador solo. Drift de voz de marca es exactamente lo que un Brand Voice Agent (§6.2 del MASTER_PLAN) intenta prevenir; el research lo refuerza.

## Ruido / contenido sin valor

- **La tabla side-by-side §2** es útil pero repite información de los deep dives §3. Doble counting.
- **Sección 3.6 sobre Mastra** es exhaustiva (~10 líneas) y la conclusión es "no, es TS-only". Para un proyecto Python-first, podría ser un párrafo corto.
- **"Costos enterprise CrewAI $60k–$120k/año"** se repite en §3.2 y en la tabla §2. Para un operador solo en OSS, es información irrelevante.
- **Sección §3.5 sobre OpenAI Agents SDK** es completa pero termina en "no tiene sentido". Mismo issue: análisis exhaustivo para un descarte rápido.
- **El comentario sobre "Branding constraints" del Claude Agent SDK** ("Anthropic no permite a third parties ofrecer login claude.ai") es irrelevante para uso interno y el research mismo lo dice.
- **El TL;DR es demasiado largo** (3 párrafos densos). Para una recomendación que en realidad es "empieza con C, después A", podría ser 4 líneas.
