# n8n Templates — Notas de inspección y adaptación

> Bitácora operacional. Cuando importes un template, registralo acá ANTES de modificar nada.

## Templates a importar (Fase 1)

| ID n8n | Nombre | URL | Función esperada | Status |
|---|---|---|---|---|
| #12533 | Curate AI newsletter from RSS | https://n8n.io/workflows/12533 | A1+A2+A3 esqueleto + HITL Slack→Telegram | ✅ importado 2026-05-12 (cuenta aibrieflatam.media@gmail.com) |
| #6389 | Smart RSS + Baserow (dedup) | https://n8n.io/workflows/6389 | Dedup persistente, patrón portable | ⏳ pending |
| #4399 | Anthropic AI Agent Sonnet 4 + web_search | https://n8n.io/workflows/4399 | A4 fact-checker con Claude nativo + web | ⏳ pending |
| #4028 | Carousel gpt-image-2 | https://n8n.io/workflows/4028 | A8a visual generator (swap gpt-image-1 → gpt-image-2) | ⏳ pending |
| #9472 o #5773 | Telegram HITL | https://n8n.io/workflows/9472 (o /5773) | A9 human approval | ⏳ pending |

## Por cada template importado — completar esta plantilla:

### Template: [ID + Nombre]
- **Fecha importación:**
- **URL original:**
- **Nodos que usa:**
- **Adaptaciones aplicadas:**
- **Lo que conservé del original:**
- **Lo que descarté:**
- **Issues encontrados al ejecutar:**
- **Decisión final:** mantener / descartar / fusionar con otro
- **Tiempo invertido:**

---

## Template #12533 — Curate AI newsletter from RSS + OpenAI + Slack

> **Status:** 🔍 inspeccionado pre-import (2026-05-11). Pendiente: click "Use for free" en n8n.io para descargar JSON e importar a tu n8n cloud. Una vez importado, completar campos faltantes abajo.

### Datos de inspección (de la página pública n8n.io)

- **Fecha inspección:** 2026-05-11
- **URL original:** https://n8n.io/workflows/12533-curate-and-generate-an-ai-newsletter-from-rss-feeds-with-openai-and-slack/
- **Autor:** Maksudur Rahman
- **Last updated:** ~3 months ago (txt en página, ≈ febrero 2026)
- **Versión n8n requerida:** 1.0+ (usa LangChain nodes)
- **Total de nodos:** **155 reales** (no 30+ como decía la página pública — la página lista una muestra). Confirmado por inspección del JSON descargado vía API el 2026-05-12.
- **Licencia:** Free template ("Use for free" en n8n.io)
- **JSON archivado:** `legacy/n8n-templates/12533-original.json` (envelope completo, 192 KB) + `legacy/n8n-templates/12533-importable.json` (sin envelope, listo para paste, 186 KB)

### Nodos principales identificados (post-inspección JSON real)

Breakdown de los 155 nodes, en orden de frecuencia:

| Cantidad | Tipo de node | Para qué |
|---:|---|---|
| 19 | `n8n-nodes-base.set` | Normalización de items |
| 16 | `n8n-nodes-base.stickyNote` | Comentarios del autor (no afectan execution) |
| 15 | `n8n-nodes-base.splitOut` | Split de arrays |
| 13 | `n8n-nodes-base.scheduleTrigger` | Cron triggers (uno por source/path) |
| 12 | `n8n-nodes-base.httpRequest` | Scraping blogs no-RSS + posible Anthropic API |
| 12 | `n8n-nodes-base.code` | Custom logic |
| 11 | `n8n-nodes-base.slack` | HITL multi-paso |
| 9 | `@n8n/n8n-nodes-langchain.chainLlm` | LLM calls |
| 6 | `@n8n/n8n-nodes-langchain.outputParserStructured` | JSON enforcement |
| 6 | `n8n-nodes-base.rssFeedReadTrigger` | 6 fuentes RSS directas |
| 6 | `n8n-nodes-base.filter` | Filtering items |
| 5 | `@n8n/n8n-nodes-langchain.outputParserAutofixing` | Error correction de parsers |
| 4 | `n8n-nodes-base.aggregate` | Aggregation |
| 3 | `n8n-nodes-base.reddit` | Reddit posts |
| 3 | `n8n-nodes-base.if` | Branching condicional |
| **2** | `@n8n/n8n-nodes-langchain.lmChatOpenAi` | **OpenAI ChatModel — único LLM nativo en el template** |
| 2 | `n8n-nodes-base.googleSheets` | Storage / dedup |
| 2 | `@n8n/n8n-nodes-langchain.informationExtractor` | Extracción estructurada |
| 2 | `n8n-nodes-base.executeWorkflow` | Sub-workflows |
| 2 | `n8n-nodes-base.convertToFile` | File output |

**Hallazgo importante (corrige WebFetch summary anterior):** el template NO usa el node Anthropic nativo. Tiene solo `lmChatOpenAi` × 2 como LLM nativo. Si la página decía "Anthropic integrado" probablemente sea vía uno de los 12 HTTP Request nodes (Claude API directa). Esto significa que **swap a Anthropic implica reemplazar nodes OpenAI Chat Model con nodes Anthropic Chat Model nativos** — pero también revisar los HTTP Request para ver si ya hay llamadas a Anthropic que se pueden consolidar.

### Funcionalidad declarada

- Monitorea 15+ fuentes (TechCrunch, r/OpenAI, Anthropic blog, Google blog + 11 más no enumeradas en la página pública)
- Usa GPT-4o para "filter out noise to identify only high-impact stories"
- Selecciona top 4 stories basado en relevancia para "tech-savvy audience"
- Genera draft de newsletter → envía a Slack
- HITL: humano aprueba en Slack o pide rewrite con feedback → loop de revisión IA

### Mapping al pipeline AI Brief LATAM

| Step pipeline | ¿Lo cubre este template? | Notas |
|---|---|---|
| 1. Trigger diario cron 7 AM CDMX | ✅ (cron-based polling) | Re-configurar el cron a tu timezone |
| 2. Fetch 12 RSS LATAM mix | 🟡 parcial | Tiene 15+ sources, **pero anglo-céntricas**. Hay que reemplazar lista entera por las 12 LATAM-mix |
| 3. Deduplicación 30d historial | 🟡 parcial | Usa Google Sheets — patrón portable, pero ver template #6389 (Baserow GUIDs) para versión más limpia |
| 4. Scoring heurístico (rules) | ❌ no | Salta directo al LLM scoring. Hay que insertar un Function/Code node antes del scorer |
| 5. Scoring LLM rubric 8 categorías LATAM-aware | ❌ no — gap custom | Tiene scoring genérico "tech-savvy audience". Hay que **reescribir el prompt entero** con tu rubric Anexo B |
| 6. Selección top 1-3 items | 🟡 parcial | Selecciona top 4 — ajustar a top 1-3 (ADR-011: 1 post/día Fase 1) |
| 7. Brief estructurado Smart Brevity | 🟡 parcial | Genera draft de newsletter genérico. Hay que reemplazar prompt por Smart Brevity + ángulo LATAM (brand_voice.md) |
| 8. Fact-check Claude + web_search | ❌ no | Hay que añadir un step nuevo usando patrón del template #4399 |
| 9. Copy post (caption + hashtags) | ❌ no | El template apunta a newsletter, no a post de IG. Hay que añadir un node nuevo |
| 10. Carousel 5-7 imágenes gpt-image-2 | ❌ no | No tiene generación de imágenes. Importar template #4028 para esto |
| 11. Compliance check | ❌ no | No tiene. Hay que añadir Claude Opus 4 node con prompt de compliance (Meta rules + brand voice) |
| 12. Telegram HITL preview | 🔁 swap | Tiene Slack HITL — **swap a Telegram Bot node** (existe nativo en n8n) |
| 13. Approve/edit/reject | ✅ patrón replicable | Lógica de "reply triggers revision" es replicable; cambiar de Slack a Telegram |
| 14. Publish IG + TikTok | ❌ no | No tiene publishing. Importar templates #4028 (upload-post) o agregar Blotato/Buffer custom |

**Cobertura estimada del pipeline:** ~40-50% de los 14 steps (cubre 1, 6, 12 ✅; 2, 3, 7 parcial; 4, 5, 8, 9, 10, 11, 14 hay que añadir).

### Adaptaciones obligatorias (a aplicar tras importar)

1. **Swap Slack → Telegram Bot** en los nodes de HITL (canales, mensaje, callbacks)
2. **Swap OpenAI Chat Model → Anthropic Chat Model** (Claude Opus 4 para scoring/editorial, Claude Sonnet 4 para tareas cheap) — el research n8n confirmó que el node Anthropic nativo soporta esto
3. **Reemplazar las 15+ fuentes anglo** por tus 12 sources LATAM-mix de `projects/ai-brief-latam/sources.yaml`
4. **Reescribir scoring prompt** con la rubric de 8 categorías Anexo B (LATAM-aware)
5. **Reescribir editorial prompt** con Smart Brevity + ángulo LATAM (referenciar `brand_voice.md`)
6. **Ajustar top-N de 4 a 1** (ADR-011)
7. **Migrar storage Google Sheets → Supabase** (o mantener Sheets como temp y migrar después)
8. **Borrar el output newsletter genérico** — vas a usar un agente de Composer separado que produzca brief estructurado + caption + slides

### Lo que vale la pena conservar del original

- **Patrón cron + RSS poll multi-source** (estructura limpia, no reinventarlo)
- **Patrón "draft → HITL → revision loop"** (lógica replicable cambiando Slack por Telegram)
- **Estructura de Set nodes para normalizar items RSS** (estándar n8n, sirve casi tal cual)

### Lo que vas a descartar

- El node de Google Sheets como storage permanente (mover a Supabase eventualmente)
- El prompt de scoring "tech-savvy audience" genérico (no LATAM, no rubric 8 categorías)
- El output "draft de newsletter completo" (vamos a generar por separado caption + slides + newsletter)
- Cualquier hardcoded URL de fuente anglo (TechCrunch sigue, otras 11 hay que reemplazar)

### Pasos concretos para vos (Manuel)

1. **Abrir** https://n8n.io/workflows/12533-curate-and-generate-an-ai-newsletter-from-rss-feeds-with-openai-and-slack/
2. Click **"Use for free"** (botón principal de la página)
3. **Pegar el JSON** en tu n8n cloud (botón "+" → "Import from clipboard" o "Import from file")
4. **Renombrar** el workflow a algo como `ai-brief-latam-pipeline-v1` para no confundir con el template original
5. **Antes de modificar nada**, exportar el JSON original a `legacy/n8n-templates/12533-original.json` (gitignored si pesa mucho, sino commit) para referencia
6. **Completar abajo** los campos "Fecha importación", "Tiempo invertido", "Issues encontrados al ejecutar" cuando lo hagas
7. Aplicar las 8 adaptaciones obligatorias listadas arriba en este orden:
   - Primero swap LLM (OpenAI → Anthropic) — porque tocás más de la mitad de los nodes
   - Segundo swap output (Slack → Telegram) — cambia el final
   - Tercero reemplazar fuentes y prompts — lo más laborioso
8. **No agregar todavía** los gaps de los steps 4, 5, 8, 9, 10, 11, 14 — eso va con los otros 4 templates (#6389 dedup, #4399 fact-check, #4028 carousel, #9472/#5773 Telegram HITL avanzado)

### Bloques de info pendientes (a llenar post-import)

- **Fecha importación real:** **2026-05-12** (cuenta nueva de n8n cloud con aibrieflatam.media@gmail.com — la cuenta de manupesqueira tenía el trial vencido)
- **Tiempo total de adaptación:** _(pendiente)_
- **Issues encontrados al ejecutar:** _(pendiente — primero validación de conteo de nodes + sticky notes + errores no-credenciales)_
- **Decisión final:** mantener / descartar / fusionar — _(pendiente, esperá a probarlo)_
- **JSON original archivado en `legacy/n8n-templates/`:** ✅ commit `6eb35fa` (2026-05-12) — tanto el `-original.json` con envelope como el `-importable.json` desenvelopado

---

## Revisión profunda del template #12533 (2026-05-12)

> Manuel pidió "una buena revisada al workflow que importamos hace rato, porque es posible que tenga cosas bastante valiosas que a nosotros se nos esté yendo". Esta sección documenta el análisis exhaustivo del JSON (no la página pública).

### Macro estructura (según las sticky notes del autor)

El autor Maksudur Rahman documentó el workflow en 16 sticky notes que revelan la arquitectura lógica:

1. **RSS feeds** — blog sites + social media (Reddit, X) + newsletters + AI Event Calendars
2. **Scraping Content** — fuentes no-RSS via sub-workflow externo
3. **Limiting Content** — limit node por fuente RSS para no procesar todo el feed
4. **Pick Top Stories** — selección de top con **HITL para que humano pida feedback sobre las stories elegidas**
5. **Retrieve Blog Content** — fetching del contenido completo desde los links
6. **Iterate Over & Write Each Selected Story** — loop principal
7. **Write Intro Section** — intro del newsletter
8. **Write Segment Content** (Important Segment) — body de cada story en Smart Brevity
9. **Write "The Shortlist" Section** — quick hits (stories que NO entran en deep dive)
10. **Write Title** — subject line del email
11. **Format Full Blog Post & Generate Video Ideas** — formatting final + **3 conceptos de video viral**
12. **Final Part** — merge de todas las secciones

> **Hallazgo crítico:** el template no es solo "RSS → LLM → publish". Es una **fábrica de newsletter completa** con estructura tipo The Rundown AI / Morning Brew (Intro + Top Stories + Quick Hits + Subject + Pre-header + Viral Video Concepts). Es mucho más que lo que vimos en la página pública.

### Los 9 prompts LLM (con valor real)

#### 1. `evaluate_content` (filtro binario pre-scoring)
Determina si un contenido es relevante para AI Newsletter (job postings → out, contenido de industrias no relacionadas → out, AI y adjacent → in). **Output: binario** (no scored).

**Valor para nosotros:** podemos agregar este filtro binario ANTES del A2 Signal Scorer. Ahorra tokens en items obviamente irrelevantes. Es decisión cheap (Sonnet 4.5, max_tokens=50). En nuestra rúbrica, hoy todo va al scorer y se descarta solo si score < 50 — agregar filtro binario reduce ~30-50% de items procesados por LLM.

#### 2. `pick_top_stories` (selección con chain-of-thought + shortlist)
Pide al LLM que:
- Razone por qué elige cada story (`top_selected_stories_chain_of_thought`)
- Devuelva `top_selected_stories` (los seleccionados, deep dive)
- Devuelva `shortlist_stories` (mención corta, no deep dive)

**Valor para nosotros enorme:** introducir el concepto de **shortlist**. Nuestro pipeline actual selecciona top 1-3 y descarta el resto. Pero los items que quedaron justo abajo del threshold son perfectos para "Quick Hits" en la newsletter. Esto cambia la arquitectura: A2 sigue scoreando individual, pero **A3 Editorial debe recibir top-N + shortlist** y decidir qué va en deep dive vs quick hits.

#### 3. `write_segment_content` (Smart Brevity por story)
**Importante:** este prompt usa LITERALMENTE el framework "Smart Brevity" — el mismo que adoptamos en `brand_voice.md`. Estructura:
- **The Lead** (intro, 2-3 sentences, NO label, incluye link a source)
- **Key Details** ("the meat" — specs, features, context)
- **Forbidden:** explícitamente prohibe meta-labels como "The Recap:" o "Bottom Line:" — interesante contraste con la versión Axios pura.

**Valor:** validación cruzada de que Smart Brevity es la elección correcta. Su variante "no usar labels obvios" es un refinamiento que vale considerar en nuestro a3-editorial: en lugar de marcar literalmente "¿Por qué importa?", podríamos hacer ese párrafo fluir sin label.

#### 4. `write_intro` (format mimicry con ejemplos)
El prompt **provee ejemplos** y pide al LLM que mimique la estructura exacta (paragraph 1 = hook directo a la story principal, no "Good morning" salutation, max 2-3 sentences, no repetir la primera oración del primer story segment).

**Valor:** patrón "few-shot con ejemplos" que producimos resultados más consistentes que prompts open-ended. Para nuestro a3-editorial podríamos pasar 2-3 briefs aprobados previamente como referencia.

#### 5. `write_other_top_stories` (Quick Hits)
Toma los stories que NO entraron en deep dive y los compone como "Quick Hits" — 1-2 frases por story, link, sin contexto extenso.

**Valor:** la sección "Quick Hits" es estándar en TODOS los benchmarks (The Rundown, Superhuman, Mafia IA, Explicable). Nuestro plan actual NO la incluye. Vale agregarla a Fase 1 newsletter.

#### 6. `edit_top_stories` (feedback-loop pattern)
Este es **el patrón HITL más valioso del template**. Cuando humano da feedback ("cambiá la story 2 por otra", "el ángulo está muy hype"), un editor LLM aplica esos cambios **sin alterar ningún otro contenido**. Incluye `<core_directive>` con reglas explícitas: "must not introduce changes outside the feedback".

**Valor para nosotros gigante:** este es exactamente el patrón que necesitamos para nuestro Telegram HITL. Cuando Manuel rechace con razón ("el copy es genérico" o "la imagen 3 está pixelada"), un editor LLM aplica solo eso sin regenerar el brief entero.

#### 7. `write_subject_line` (1 principal + 5-8 alternates)
Genera 1 subject line + 5-8 alternativas + pre-header text + razonamiento para cada. **Razonamiento como numbered list** (no bullets) — detalle de UX que probablemente proviene de testing.

**Valor:** podemos pedir 3-5 caption alternates para Instagram. Útil para A/B testing manual o para que Manuel elija el que más le gusta en lugar de regenerar.

#### 8. `edit_subject_line` (feedback-loop para títulos)
Same pattern as `edit_top_stories` pero solo para subject + teaser text.

**Valor:** mismo patrón #6 aplicado a copy.

#### 9. `Generate Viral Video Ideas` (3 frameworks)
El prompt produce **3 conceptos de video** distintos siguiendo frameworks específicos:
1. **"Contrarian/Pattern Interrupt"** — challenge a common belief, stop the scroll
2. **"Actionable Listicle/Hack"** — fast-paced, value-dense, highly saveable
3. **"Story/Visual Metaphor"** — skit, analogy, narrative

Cada concepto tiene: Concept Title, Visual Style, structure.

**Valor MASIVO:** esto es exactamente lo que necesita nuestro **A6 Audio Director / A8b Video Generator** cuando entremos Fase 2. Los 3 frameworks son perfectos para diversificar reels — uno por día de cada framework alterna y previene fatiga de audiencia.

### Newsletter output structure (a copiar)

El template genera una newsletter con esta estructura completa:

```
[Subject Line] (con 5-8 alternates)
[Pre-header text]

[INTRO] — paragraph 1: hook directo, sin saludo
[INTRO] — paragraph 2: context del día

[STORY 1] — The Lead + Key Details (Smart Brevity)
[STORY 2] — The Lead + Key Details
[STORY 3] — The Lead + Key Details
(top deep-dive stories)

[OTHER TOP STORIES / QUICK HITS]
- Story 4: 1-2 sentences + link
- Story 5: 1-2 sentences + link
- Story 6: 1-2 sentences + link

[VIRAL VIDEO IDEAS] — 3 conceptos (Contrarian / Listicle / Story)
```

**Para nuestro caso:** newsletter daily debería usar esta estructura. Diferencias propuestas:
- Adaptar a español neutro LATAM
- Top stories 1-3 (no 1-5, somos más selectos)
- Quick Hits 3-5 (las que quedaron abajo del threshold)
- Viral Video Ideas → 3 conceptos por pieza (entrega ammo para que tú elijas el reel del día siguiente)

### HITL pattern — incompleto en este JSON

El template TIENE Slack nodes que envían drafts pero **NO TIENE webhook nodes que escuchen respuestas**. Esto significa que:

1. El template asume que existe un **workflow separado** (no incluido en el JSON) que listenea Slack threads, parsea respuestas, y dispara `edit_top_stories` / `edit_subject_line` cuando hay feedback.
2. La página de n8n.io vendió el template como "HITL completo" pero solo está la mitad: envío de drafts. Recepción de feedback está implícita.

**Implicación para nosotros:** cuando construyamos Telegram HITL, necesitamos:
- Telegram node "Send Message" (esto ya está en nuestro skeleton Fase 0)
- **Telegram Trigger** o **Webhook node** que escuche respuestas inline (botones de aprobar/rechazar) o replies con texto de feedback
- Workflow secundario que parsea la respuesta y dispara edit-loop o publish, según corresponda

El template #9472 ("Generate AI LinkedIn Posts with Human Approval via Telegram") tiene **este patrón completo** — vale revisarlo cuando lleguemos a esa parte.

### Dedup pattern — Google Sheets `appendOrUpdate`

El template usa **una sola Google Sheet** llamada "AI News Tracker" con columnas: URL, Title, Source, Authors, Content, Published, External Sources. La operación es `appendOrUpdate` usando URL como clave única.

**Patrón aplicable a Supabase:** crear tabla `dedup_history` con `url` como PRIMARY KEY (o UNIQUE constraint). El node "Supabase: Upsert" hace exactamente lo mismo que `appendOrUpdate` de Sheets.

### Sub-workflow pattern — Scrape URL externo

Hay 2 `executeWorkflow` nodes que llaman a **un workflow externo llamado "AI News Aggregator - Scrape Url"** (workflow ID `XnONeyNXcW98MVce`). Ese sub-workflow toma una URL y devuelve content scraped.

**Implicación crítica:** el template #12533 NO funciona standalone. Asume que tenés ALSO importado el sub-workflow del scraper. Ese workflow NO está en el JSON que tenemos. **Cuando ejecutes el workflow, los 2 nodes Scrape URL van a fallar** porque apuntan a un workflow ID que no existe en tu cuenta.

**Solución:** o (a) descargamos también ese sub-workflow del marketplace de n8n, o (b) reemplazamos los `executeWorkflow` nodes por nuestro propio scraper inline (HTTP Request + parse). Para Fase 0 no importa porque no scrapeamos nada, solo RSS.

### Polling pattern — 13 schedule triggers, 1 por fuente, 3h interval

Cada fuente RSS / Reddit / blog tiene **su propio Schedule Trigger corriendo cada 3 horas**. Patrón "fan-in" — cada source corre independiente, todo converge en el evaluator.

**Implicación:** esto significa que el flow se dispara hasta 13 veces por ciclo (8 veces al día × 13 sources = 104 ejecuciones al día solo para ingestion). Muy costoso en plan Starter de n8n cloud que tiene 2,500 ejecuciones/mes (≈ 80/día). **Se queda corto rápido.**

**Para nuestro caso:** **1 sólo cron diario a las 6 AM CDMX** que dispare la consulta paralela a las 12 fuentes via Split In Batches o Merge. Mucho más eficiente. Costo aprox: 30 ejecuciones/mes para ingestion del cron + ~150 ejecuciones por pipeline run × 30 days = 4,500/mes. **Esto excede Starter (2,500/mes) ya.** Hay que ir a Pro (10,000/mes, ~$60/mes).

> **🚨 Cost alert:** revisar `docs/STACK.md` que tiene n8n Cloud en $24/mes. Eso es Starter y NO alcanza para el volumen real del pipeline Fase 1. Habría que subir a Pro (€60/mes) o ir self-hosted en Hostinger VPS (€5-7/mes con community edition).

### Resumen — qué adoptamos / adaptamos / descartamos

#### Adoptamos (8 patterns valiosos):

1. **Filtro binario pre-scoring** (`evaluate_content`) — agregar entre A1 y A2 para ahorrar tokens
2. **Top + Shortlist** (`pick_top_stories` con shortlist) — A2 output incluye shortlist para Quick Hits
3. **"Smart Brevity sin meta-labels"** (`write_segment_content`) — refinamiento del a3-editorial
4. **Format mimicry con ejemplos** (`write_intro`) — agregar 2-3 ejemplos a a3-editorial
5. **Quick Hits section** (`write_other_top_stories`) — agregar al a8d newsletter (cuando arranque Fase 3)
6. **Feedback-loop edit pattern** (`edit_top_stories`, `edit_subject_line`) — base del HITL en Telegram
7. **N alternates pattern** (`write_subject_line` con 5-8 alternates) — caption alternates para IG
8. **Viral video frameworks** (`Generate Viral Video Ideas` con 3 conceptos) — a6/a8b en Fase 2

#### Adaptamos (4 patterns con cambios):

9. **Slack → Telegram** con webhook bidireccional (template tiene solo half, completar)
10. **Google Sheets dedup → Supabase upsert** (mismo concepto, mejor tooling)
11. **13 schedule triggers → 1 cron + fan-out** (eficiencia de ejecuciones)
12. **Subagent externo Scrape URL → inline HTTP Request en nuestro workflow** (autocontenido)

#### NO adoptamos (3 cosas):

13. **English-only** (somos español neutro LATAM)
14. **Blog/newsletter focus puro** (somos IG + TikTok + newsletter)
15. **OpenAI GPT-4o como LLM principal** (somos Claude Opus 4 + Sonnet 4.5)

### Implicaciones para nuestro skeleton

El N8N_WORKFLOW_SKELETON.md actual va a necesitar revisión cuando consolidemos las decisiones C, D, E + estos patrones. Cambios principales:

- **A1 Source Monitor:** agregar filtro binario antes de A2 (1 LLM call cheap por item antes del scoring)
- **A2 Signal Scorer:** output enriquecido con shortlist (no solo top), justificación con chain-of-thought
- **A3 Editorial:** few-shot con ejemplos de briefs aprobados anteriores
- **A8d Newsletter:** estructura completa (Intro + Top Stories + Quick Hits + Subject + Pre-header + Viral Video Ideas)
- **A9 Compliance + HITL:** patrón edit-loop para cuando Manuel da feedback parcial
- **Capa nueva A6/A8b Fase 2:** ya tenemos el framework de los 3 viral video concepts
- **Stack alert:** revisar plan n8n cloud — probable salto a Pro o self-hosted

---

## Gaps custom identificados durante adaptación

(lista que crece cada vez que descubrimos algo que ningún template resuelve)

### Conocidos de antemano (del research 2026-05-11)
- **Rubric scoring de 8 categorías LATAM-aware** — ningún template lo tiene. Hay que construirlo desde cero como custom Function/AI Agent node con prompt detallado.
- **Buffer GraphQL publish para carousel IG** — no hay node oficial. Único ejemplo público (ghwoodard/n8n-social-media-automation) tiene 0 stars. Alternativas: Blotato, Upload-Post, Meta Graph API directo.
- **gpt-image-2 swap** — todos los templates 2026 apuntan a gpt-image-1/DALL-E. Swap manual obligatorio.
- **Claude prompt caching** — el node nativo Anthropic NO expone cache_control. Para system prompts grandes (scoring rubric), fallback a HTTP Request con headers cache_control.

### Descubiertos durante import (a llenar)
- _(vacío)_
