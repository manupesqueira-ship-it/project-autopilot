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

## Gaps custom identificados durante adaptación

(lista que crece cada vez que descubrimos algo que ningún template resuelve)

### Conocidos de antemano (del research 2026-05-11)
- **Rubric scoring de 8 categorías LATAM-aware** — ningún template lo tiene. Hay que construirlo desde cero como custom Function/AI Agent node con prompt detallado.
- **Buffer GraphQL publish para carousel IG** — no hay node oficial. Único ejemplo público (ghwoodard/n8n-social-media-automation) tiene 0 stars. Alternativas: Blotato, Upload-Post, Meta Graph API directo.
- **gpt-image-2 swap** — todos los templates 2026 apuntan a gpt-image-1/DALL-E. Swap manual obligatorio.
- **Claude prompt caching** — el node nativo Anthropic NO expone cache_control. Para system prompts grandes (scoring rubric), fallback a HTTP Request con headers cache_control.

### Descubiertos durante import (a llenar)
- _(vacío)_
