# Multi-Agent Frameworks para Producción Editorial: Análisis Técnico Comparativo

**Contexto:** Stack Python/Next.js/Supabase/Vercel/Anthropic API. 3 propiedades media (newsletter + IG c/u). 2–5 piezas/día/propiedad. Operador solo. Kernel compartido + agentes especializados por propiedad.

---

## TL;DR

- **Recomendación principal: LangGraph (Python) con Claude Sonnet 4.5 vía `langchain-anthropic`, persistencia en Supabase Postgres vía `PostgresSaver`, y deployment en un container/VPS pequeño (Fly.io, Railway, o Render) — *no* en Vercel para los runs largos.** Es la opción con mejor balance de madurez, control de estado, human-in-the-loop nativo y observabilidad (LangSmith) para tu caso de workflow editorial determinístico con revisión humana.
- **Antes de elegir framework, considera seriamente "single-agent con tools + subagents puntuales" usando el Claude Agent SDK.** La guía oficial de Anthropic ("Building Effective Agents", "When to use multi-agent systems") es explícita: equipos pierden meses construyendo arquitecturas multi-agent cuando un solo agente con buen prompting hubiera bastado. Para 2–5 piezas/día con un operador solo, tu caso está en la frontera; un kernel = system prompt + tools, y "propiedades" = agent definitions con instructions distintas, puede ser suficiente.
- **Descarta de entrada: AutoGen (en maintenance mode desde octubre 2025), OpenAI Swarm (deprecado, reemplazado por OpenAI Agents SDK), y Mastra (TypeScript-only, rompe tu preferencia Python-first).** CrewAI es viable como atajo si quieres un MVP en horas, pero su control de estado y observabilidad son inferiores a LangGraph para producción editorial.

---

## 1. Resumen Ejecutivo

El landscape de frameworks multi-agent maduró fuerte entre 2024 y 2026. A mayo 2026, el panorama relevante para tu caso es:

| Framework | Estado real (mayo 2026) | Lenguaje | ¿Encaja con tu stack? |
|---|---|---|---|
| **LangGraph** | v1.x GA desde mayo 2025; ~400 empresas en prod (Klarna, LinkedIn, Uber, Replit, Elastic) | Python + JS | **Sí.** Postgres checkpointer compatible con Supabase, model-agnostic (Anthropic first-class) |
| **CrewAI** | v0.x activo, ~48k stars, AMP enterprise plan; "Cognition Memory" lanzado recientemente | Python | Sí, pero menos control para HITL determinístico |
| **Microsoft AutoGen** | **Maintenance mode** desde 1 oct 2025. Sucesor: Microsoft Agent Framework (preview) | Python + .NET | **No recomendado** para greenfield |
| **Claude Agent SDK** | Lanzado 29 sep 2025 (renombre de Claude Code SDK). v0.2.x activo | Python + TS | Sí, pero Claude-only y orientado a "computer use" |
| **OpenAI Swarm / Agents SDK** | Swarm **deprecado**. Agents SDK (mar 2025) es producción-ready, locked a OpenAI por defecto | Python (TS llegando) | Forzado: tu LLM principal es Claude |
| **Mastra** | v1.0 ene 2026, $35.5M raised, ~22k stars, 300k+ npm/semana | **TypeScript only** | **No** encaja con preferencia Python-first |

**Trade-off central que vale la pena reconocer:** un sistema multi-agent consume ~15× más tokens que un chatbot estándar (dato del propio post de Anthropic "How we built our multi-agent research system"). Para 2–5 piezas/día/propiedad ≈ 6–15 piezas/día total, el costo de tokens NO es problema, pero la **complejidad de debug y la deriva (drift) de voz de marca** sí lo son. Esto inclina la decisión hacia frameworks con buena observabilidad y checkpointing.

---

## 2. Tabla Comparativa Side-by-Side

| Dimensión | LangGraph | CrewAI | AutoGen | Claude Agent SDK | OpenAI Agents SDK | Mastra |
|---|---|---|---|---|---|---|
| **Versión / GA** | v1.1+ (mayo 2025 GA) | v0.x activo | v0.7.x maintenance | v0.2.x activo | v1.x activo (mar 2025) | v1.0 (ene 2026) |
| **GitHub stars (aprox.)** | ~12k (Python) + 2k JS | ~48k | ~56k (frozen) | ~5k Py + 4k TS | ~19k+ | ~22k |
| **Backed by** | LangChain Inc | crewAI Inc ($18M raised) | Microsoft (legacy) | Anthropic | OpenAI | Kepler Software ($35.5M) |
| **API stability** | GA, semver | Cambios frecuentes pre-1.0 | Frozen | API moviéndose (V1→V2) | GA | Activa, breaking changes posibles |
| **Modelo mental** | Grafo dirigido + state tipado | Crews (roles) + Flows (event-driven) | GroupChat conversacional | Tool-loop con subagents | Handoffs entre agents | Workflows + Agents |
| **State compartido** | First-class (typed state, reducers, Store cross-thread) | Memory unificada con scopes jerárquicos | Conversation history (in-memory) | MCP servers + sessions | Context variables (ephemeral) | Memory + LibSQL/Postgres |
| **Checkpointing** | Built-in (Memory/SQLite/Postgres) | Replay desde último kickoff | Limitado | Session store con eager flush | Sessions API | Built-in workflows suspend/resume |
| **HITL nativo** | `interrupt()` + state inspection/edit | Vía Flows | Limitado | Hooks + permission_mode + can_use_tool callback | Approval API | `suspend`/`resume` workflows |
| **Tool calling Claude** | First-class vía `langchain-anthropic` (incluye text editor, memory, prompt caching middleware) | Vía LiteLLM, funciona | Vía adapter | Nativo (es su punto fuerte) | Funciona pero el SDK está optimizado para OpenAI | Vía AI SDK, soporta Anthropic |
| **Observabilidad** | LangSmith (de pago tras tier free) | CrewAI AMP / OTel | OTel parcial | Tracing built-in | Tracing dashboard built-in | Mastra Studio + tracing |
| **Curva aprendizaje** | Alta (grafo + state) | Baja (YAML/role-based) | Media (async-first) | Baja-media | Baja | Baja-media (TS-native) |
| **Modelo de precio** | OSS MIT; LangSmith ~$39/seat | OSS; Pro $99/mo, Enterprise desde $60k/año | OSS MIT | SDK gratis; consumo Anthropic API | OSS; consumo OpenAI | OSS Apache 2.0; ee/ enterprise |

---

## 3. Deep Dive por Framework

### 3.1 LangGraph

**Madurez.** Llegó a GA en mayo 2025 (v1.0), versionado semver, hoy en v1.1.x. Adopción en producción de Klarna, LinkedIn (AI recruiter, SQL Bot), Uber (code migration), Replit (agent que construye software), Elastic, AppFolio, JPMorgan, BlackRock. La cifra que circula es ~400 empresas usando LangGraph Platform. Es el más adoptado en enterprise por margen.

**Arquitectura.** El modelo mental es un **grafo dirigido**: nodes (funciones o LLM calls), edges (control flow incluido condicional), y un **state tipado** (TypedDict/Pydantic) que fluye y se mergea con reducers. Esto te da ciclos, branching condicional, paralelismo y control fino. Trae **`Checkpointer`** (Memory/SQLite/`PostgresSaver`/Redis) que persiste el estado completo en cada superstep — esto habilita time-travel debugging, durable execution (reanuda tras un crash), y `interrupt()` para human-in-the-loop sin que tú escribas la plomería.

**Anthropic / Claude.** Soporte de primera clase vía `langchain-anthropic`: `ChatAnthropic(model="claude-sonnet-4-5")`, structured outputs nativos, middleware específico para text editor tool, memory tool, **prompt caching automático** (`AnthropicPromptCachingMiddleware`), bash tool, y citations vía `search_result`. Los `create_react_agent` y los grafos custom funcionan igual con Claude.

**Use cases donde brilla.** Workflows largos con cycles (research → critique → revise), HITL, branching condicional (¿el draft pasa el fact-check? si no, vuelve), y cuando necesitas explicar exactamente qué pasó (tracing por nodo en LangSmith). Es la opción default en la industria para "production agent orchestration".

**Donde se siente forzado.** Si tu workflow es 100% lineal y simple, los TypedDict y reducers son overkill. Curva de aprendizaje alta — un dev Python experimentado sin background en grafos toma 1–3 días para ser productivo, 1–2 semanas para dominar checkpointing/interrupts.

**Pricing.** OSS MIT, gratis. **LangSmith** (observability/eval) tiene tier free de hasta 5k traces/mes, después ~$39/seat/mes. **LangGraph Platform** (deployment managed) es opcional — puedes self-hostear sin problema con un Dockerfile y Postgres.

**Comunidad.** Releases regulares (cada 1–2 semanas), Discord activo, curso gratuito en LangChain Academy, ~1.5k+ libs/templates en el ecosistema awesome-langgraph. Job market signal: explícitamente listado en muchos JD de "AI Engineer" 2025–2026.

**Fit con Supabase.** Excelente. `langgraph-checkpoint-postgres` (la lib oficial) escribe a cualquier Postgres, incluido Supabase. Atención a dos detalles: (1) usa `autocommit=True` y `row_factory=dict_row` con psycopg si manejas la conexión tú, y (2) `langgraph dev` (CLI dev mode) ignora el checkpointer en algunas versiones — usa `langgraph` programáticamente desde tu propia app. Existe también un paquete community `@skroyc/langgraph-supabase-checkpointer` para JS con RLS habilitado.

### 3.2 CrewAI

**Madurez.** ~48k stars, ~27M downloads PyPI, 150+ enterprise customers (DocuSign, Gelato, PwC, IBM watsonx). Sigue pre-1.0 con cambios frecuentes en API. La compañía levantó $18M; revenue reportado ~$2.4–3.2M (estimado, no confirmado por la empresa).

**Arquitectura.** Dos abstracciones: **Crews** (autonomous, role-based: defines `Agent(role, goal, backstory, tools)` y `Task(description, agent)`, los corres con `Process.sequential | hierarchical | consensual`) y **Flows** (event-driven, deterministic, tipo state-machine con `@start` y `@listen`). Los Flows se introdujeron precisamente porque los Crews puros no eran predecibles para producción.

**Memoria.** Lanzaron "Cognition Memory" recientemente: API unificada (`memory.remember()`, `memory.recall()`) con scopes jerárquicos, importance scoring y consolidation. Es una de las mejores capas de memoria built-in del set.

**Anthropic / Claude.** Vía LiteLLM por debajo. Funciona bien (`llm=LLM(model="anthropic/claude-sonnet-4-5")`) pero no aprovecha automáticamente prompt caching ni los middleware específicos de Anthropic.

**Donde brilla.** Pipelines de **content production** son literalmente el use case canónico de CrewAI. El abstraction "researcher → writer → editor" mapea 1:1 a tu flujo. Tiempo a primer crew funcionando: ~30 min para un dev Python.

**Donde se siente forzado.** Cuando necesitas control fino: el logging built-in es mediocre (queja recurrente: `print` no funciona dentro de tasks), HITL es indirecto, no hay checkpointing time-travel, y debug de loops cíclicos es doloroso. Equipos suelen migrar de CrewAI a LangGraph cuando llegan a producción seria.

**Pricing.** OSS MIT, **pero los planes managed son caros y poco transparentes**: Free (50 ejecuciones/mes), Pro/Basic ~$99/mes, Enterprise desde $60k/año, Ultra hasta $120k/año. Para un solo operador, te quedas en OSS self-hosted; eso está bien y es lo que recomiendan ZenML y Lindy.

**Fit con tu caso.** Atajo razonable si quieres un MVP en un día. Pero la falta de checkpointing serio y de HITL determinístico te va a doler cuando empieces a iterar sobre brand voice y aprobación humana.

### 3.3 Microsoft AutoGen

**Estado actual: en maintenance mode oficial desde el 1 de octubre de 2025.** Microsoft anunció que AutoGen y Semantic Kernel se fusionan en **Microsoft Agent Framework (MAF)**, en public preview, con GA prevista Q1 2026. El propio repo de AutoGen dice: *"AutoGen is now in maintenance mode. New users should start with Microsoft Agent Framework."*

**Implicación práctica:** no lo elijas para greenfield 2026. Si te encuentras tutoriales viejos hablando de GroupChat, AssistantAgent, AG2, son reliquias. La sucesora (MAF) es Azure-céntrica, lo cual no encaja bien con tu stack Vercel/Supabase/Anthropic.

### 3.4 Claude Agent SDK (antes Claude Code SDK)

**Madurez.** Lanzado el 29 de septiembre de 2025 junto con Claude Sonnet 4.5. Renombre del Claude Code SDK porque Anthropic descubrió que la misma harness servía para non-coding agents. Versión actual ~v0.2.111+. Disponible en Python y TypeScript.

**Arquitectura.** El modelo mental es radicalmente distinto al resto: te da **una computadora** al agente. Tools built-in (Read, Write, Edit, Bash, WebSearch, WebFetch). Tú declaras `query(prompt, options=ClaudeAgentOptions(allowed_tools=[...], system_prompt=...))` y Claude maneja el tool loop. Soporta:
- **Subagents** (vía `AgentDefinition` programático o filesystem `.claude/agents/`): cada subagent tiene su propio context window, tools restringidos, system prompt, y opcionalmente un modelo distinto.
- **Hooks** (`PreToolUse`, `PostToolUse`) para HITL granular y modificación de tool output.
- **Permissions**: `allowed_tools`, `disallowed_tools`, `permission_mode`, `can_use_tool` callback.
- **Custom tools** vía in-process MCP server (con decorador `@tool`).
- **Sessions** persistentes con `session_store_flush="eager"` para resume cross-process.

**Anthropic / Claude.** Es la integración más profunda posible — está construido por Anthropic, alrededor de Claude. Aprovecha automáticamente extended thinking, prompt caching, computer use, memory tool, sin que tengas que configurar nada.

**Donde brilla.** Cuando quieres "darle una computadora a Claude" — leer/escribir archivos, ejecutar comandos, buscar en la web. Pattern recomendado por Anthropic: un agente principal con subagents especializados (research, citation, fact-check) compartiendo el sistema de archivos como state.

**Donde se siente forzado / limitaciones.**
- **Locked a Claude.** No portabilidad de modelo.
- **Orquestación más débil que LangGraph**: no hay grafo explícito ni checkpointing time-travel. Si el agente principal falla mid-run, no hay un mecanismo nativo equivalente a LangGraph para reanudar desde el último checkpoint con estado completo (las sessions ayudan pero no son lo mismo).
- **API moviéndose**: hay V2 emergiendo paralela a V1 generator pattern. Espera breaking changes.
- **Branding constraints**: Anthropic *no permite* a third parties ofrecer login claude.ai o rate limits del producto Claude — usa API key authentication. No es un problema para tu uso interno.

**Pricing.** El SDK es gratis; pagas la API de Anthropic. Sin overhead adicional.

**Fit con tu caso.** Es una opción **viable como camino single-agent + subagents** (ver §6). Si te quedas en Claude para siempre, integración nativa con Anthropic features puntea fuerte. Si quieres flexibilidad multi-modelo o necesitas el control de grafo de LangGraph, es un downgrade.

### 3.5 OpenAI Agents SDK (sucesor de Swarm)

**Estado.** **Swarm está deprecado** (educational only, sin actualizaciones desde marzo 2025). Su sucesor, **OpenAI Agents SDK**, salió en marzo 2025; production-ready, ~19k stars, 10M+ downloads/mes.

**Arquitectura.** Primitivos: `Agent` (instructions + tools + model), `Handoff` (transferir control a otro agent vía tool call), `Guardrails` (input/output validation paralelo), `Sessions` (memoria de turn), `Tracing` built-in. Modelo "handoff" vs "manager pattern" — el primero entrega ownership del response, el segundo usa `agent.asTool()`.

**Anthropic / Claude.** **Forzado.** El SDK está optimizado para OpenAI Responses API. Puedes usar Claude vía `OpenAIChatCompletionsModel` apuntando a un proxy compatible (LiteLLM, OpenRouter), pero pierdes prompt caching nativo, websocket transport, computer use, y la mitad de las features avanzadas.

**Veredicto para tu caso.** No tiene sentido. Tu LLM principal es Claude; usar el SDK de OpenAI con Claude por debajo es nadar contra corriente.

### 3.6 Mastra

**Estado.** Lanzado por el equipo detrás de Gatsby (Sam Bhagwat), v1.0 en enero 2026, $35.5M total raised (Y Combinator, Paul Graham, Guillermo Rauch / Vercel founder, Amjad Masad, Balaji Srinivasan), ~22k stars, ~300k weekly npm downloads. Crecimiento muy fuerte. Replit Agent 3 corre Mastra.

**Arquitectura.** TypeScript-native (Zod-first), construido sobre Vercel AI SDK. Primitivos: `Agent`, `Workflow` (suspend/resume con persistencia), `Tool`, Memory (short-term + observational long-term), Model Router (3,300+ modelos via API unificada incluyendo Anthropic), MCP, RAG, Evals, Studio (UI playground).

**Por qué NO para ti.** Es **TypeScript-only**. Tu preferencia es Python-first. Forzarte a TS rompe tu velocidad de iteración. Mastra es la mejor opción si decidieras *invertir esa preferencia* (y existe argumento — todo el resto de tu stack frontend ya es TS), pero esa es una decisión meta-arquitectónica más grande que la elección de framework.

---

## 6. Recomendación Final + Check "Single-Agent vs Multi-Agent"

### 6.1 Honest reality check antes de elegir framework

La guía de Anthropic ("**Building Effective Agents**", dic 2024) y "**When to use multi-agent systems**" (2025) dicen, literalmente:

> *"Hemos visto equipos invertir meses en arquitecturas multi-agent solo para descubrir que mejor prompting en un solo agente lograba resultados equivalentes."*

> Multi-agent justificado solo cuando: **(1)** context pollution degrada performance, **(2)** las tareas pueden correr en paralelo, **(3)** la especialización mejora tool selection.

**Tu caso evaluado contra esos 3 criterios:**

1. **¿Context pollution?** Marginal. El system prompt con style guide + brand voice + tools cabe cómodamente en context window de Claude (200k). 3 propiedades distintas no contaminan si separas por thread.
2. **¿Paralelismo?** Sí, ligero — research puede paralelizarse, pero no es crítico para 6–15 piezas/día.
3. **¿Especialización mejora tool selection?** Solo si tienes muchas tools. Con ~6–8 tools por agente, un solo agent las maneja bien.

**Conclusión honesta:** tu caso **no es claramente multi-agent**. Es un **workflow con varias pasadas del mismo modelo en distintos roles** (researcher, writer, critic), que es diferente.

### 6.2 Recomendación

**Camino A (recomendado): LangGraph como "workflow engine de agentes especializados".**
- Modelo único: Claude Sonnet 4.5 (Haiku para nodes de evaluación/dedup).
- El "kernel compartido" = módulo Python con tools + base prompts + middleware.
- "Agentes por propiedad" = 3 instancias del mismo `StateGraph` con distinto `PropertyConfig` inyectado.
- HITL nativo via `interrupt()` antes de schedule.
- State persistente en Supabase Postgres.

**Camino B (válido si valoras simplicidad y velocidad inicial): Claude Agent SDK con subagents.**
- Un agent principal por propiedad con system prompt = brand voice + style guide.
- Subagents: `researcher`, `fact_checker`, `image_director`. Definidos vía `AgentDefinition`.
- Tools: filesystem (drafts en `.md`), MCP server custom para Supabase, scheduler tool.
- HITL via `can_use_tool` callback para `publish_*` tools.
- **Trade-off:** menos control sobre flow, locked a Claude, pero menos código (~30% menos boilerplate que LangGraph).

**Camino C (no recomendado pero anotado): empezar single-agent con tools, sin framework.**
- Un loop simple: `anthropic.messages.create()` con tools, todo en un solo llamado, en un script Python.
- Subagents = nada, solo más tools.
- **Cuándo elegir esto:** si quieres validar el producto en 2 semanas antes de invertir en framework.

### 6.3 Mi llamada concreta

> **Empieza con Camino C (single-agent + tools) durante 2 semanas para validar el output editorial. Luego migra a Camino A (LangGraph) cuando: (a) tengas evidencia de que un solo loop falla en consistency entre propiedades, (b) quieras checkpointing/HITL formal, (c) el critique loop necesite controlar iteraciones explícitamente.**

---

## Caveats y Limitaciones del Análisis

- **Velocidad del landscape.** Estos frameworks cambian semana a semana. Cifras de stars, downloads y empresas en producción son al mejor conocimiento a mayo 2026.
- **Predicciones sobre Microsoft Agent Framework.** Su GA Q1 2026 viene de comunicaciones oficiales, pero "GA" en preview-to-GA frecuentemente desliza.
- **Claude Agent SDK V2.** El cambio V1→V2 está en progreso; código que escribas hoy contra V1 puede requerir refactor.
- **Job market signal.** Mi afirmación de que LangGraph es el más demandado en JD es basada en menciones agregadas en 2025–2026 articles; no tengo datos primarios de LinkedIn/Indeed.
- **Costos enterprise.** Los precios de CrewAI Enterprise ($60k–$120k/año) provienen de blog posts terceros (ZenML, Lindy); CrewAI no publica pricing en su sitio oficial.
- **Vercel deployment para LangGraph.** Mi recomendación de no usar Vercel para el engine es opinión técnica basada en el shape típico de agent workloads vs serverless functions.
- **Supabase + LangGraph.** El `PostgresSaver` oficial funciona contra cualquier Postgres incluyendo Supabase, pero hay reports de fricción con `langgraph dev` ignorando checkpointers en algunas versiones. Test antes de comprometer.
- **El sesgo de framework selection.** Hay un sesgo en la industria a sobreingenierizar agents. Mi recomendación de "empieza single-agent" no es popular en marketing de frameworks porque ningún framework gana si tú concluyes que no necesitas framework.
