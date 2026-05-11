# n8n Templates Research — AI Brief LATAM Fase 1

**Fecha:** 2026-05-11
**Autor:** research notes (Manuel Pesqueira / asistido por Claude)
**Foco:** templates/workflows públicos de n8n adaptables al pipeline editorial multi-agente (RSS → scoring LLM → brief Smart Brevity → fact-check → imágenes carousel → compliance → HITL Telegram → publishing IG/TikTok via Buffer)

---

## Resumen ejecutivo

- **Anthropic SÍ tiene node oficial nativo en n8n** (no es solo HTTP Request). Existen dos nodes: el `Anthropic Chat Model` (sub-node de cluster LangChain, conecta a AI Agent / AI Chain) y el `Anthropic` app-node (document/file/image analysis y prompt ops). Confirmado vía docs.n8n.io y n8n.io/integrations/anthropic. Soporta Claude Sonnet 4 / Opus 4. Web search nativa NO está expuesta como toggle en el Chat Model node (verificado en threads de community.n8n.io) — hay que armarla como Tool con HTTP Request al endpoint `web_search` de Anthropic o usar un workflow tipo "AI Agent + Web Search Tool".
- **OpenAI gpt-image-2 existe y está disponible vía API** desde abril 2026 (snapshot `gpt-image-2-2026-04-21`). Endpoint `v1/images/generations` y `v1/images/edits`. n8n a mayo 2026 todavía tiene templates apuntando a `gpt-image-1`/DALL-E — hay que swapear modelo manualmente.
- **n8n cloud NO tiene free tier permanente**, solo trial de 14 días con features Pro y ~1000 executions. Pricing real: Starter €20/mes (2.5k exec), Pro €50/mes (10k exec). Para correr este pipeline 1x/día + HITL callbacks + retries, Starter alcanza con margen. (Hay contradicción entre fuentes: una dice €24/mes Starter, n8n.io/pricing dice €20 con anual.)
- **Encontré 16 templates relevantes verificables.** Ninguno cubre el pipeline completo (RSS → dedup historico → scoring LLM rubric → brief estructurado → fact-check → image carousel → compliance → Telegram HITL → Buffer). El template más cercano es #12533 (Maksudur Rahman) que cubre ~50%. La combinación recomendada es **#12533 + #4399 + #4028 + #9039** parcheados.
- **Buffer GraphQL API funciona pero NO hay node oficial.** Va por HTTP Request. TikTok via Buffer es soportado pero limitado. Alternativas viables: Blotato, Upload-Post, Meta Graph API directo + n8n-nodes-instagram (community).

---

## Templates evaluados

> Convenciones: complejidad 1–10 (1=trivial, 10=monstruo), adaptability 1–10 a nuestro caso (1=tirar a la basura, 10=usar tal cual). Fechas "last updated" de n8n.io son textuales — la plataforma muestra "3 months ago" para casi todo lo del catálogo a fecha 2026-05-11 (≈ febrero 2026). Cuando dice "3 months ago" sin fecha exacta, lo marco como tal.

| # | Nombre | URL | Autor | Last update | Qué resuelve | Nodes principales | LLM compat | Image gen | HITL | Publishing IG/TikTok | RSS multi-source | Dedup histórico | Complejidad | Adaptability | License | Quality signals |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Curate and generate an AI newsletter from RSS feeds with OpenAI and Slack | https://n8n.io/workflows/12533-curate-and-generate-an-ai-newsletter-from-rss-feeds-with-openai-and-slack/ | Maksudur Rahman | ~3 months ago | Monitorea 15+ fuentes (RSS + Reddit + blogs), scoring LLM, top-N stories, draft a Slack con approve/reply-feedback | RSS Read, HTTP Request, OpenAI/Anthropic Chat Model, AI Agent, If, Set, Slack | OpenAI + Anthropic | No nativa | Sí, vía Slack (no Telegram) | No | Sí (~15) | No explícito | 8 | 8 | unspecified | Listado oficial n8n.io |
| 2 | Smart RSS feed monitoring with AI filtering, Baserow storage, and Slack alerts | https://n8n.io/workflows/6389-smart-rss-feed-monitoring-with-ai-filtering-baserow-storage-and-slack-alerts/ | Daniel Shashko (tomax) | ~3 months ago | RSS multi-source con persistencia de "seen items" en Baserow + AI Agent que compara contra historial | RSS Read, HTTP Request, XML, AI Agent, OpenAI Chat Model, Baserow, Slack | OpenAI | No | No | No | Sí | **Sí (Baserow GUIDs)** | 7 | 8 | unspecified | Listado oficial; mejor ejemplo público de dedup persistente |
| 3 | Anthropic AI agent: Claude Sonnet 4 and Opus 4 with Think and Web Search tool | https://n8n.io/workflows/4399-anthropic-ai-agent-claude-sonnet-4-and-opus-4-with-think-and-web-search-tool/ | Davide Boizza (n3witalia) | ~3 months ago | AI Agent con routing Sonnet 4 / Opus 4 según complejidad + web search + think tool + JSON output parser | AI Agent, Anthropic Chat Model, Tool (web_search), Tool (think), Structured Output Parser, Sticky Note | **Anthropic nativo** | No | No | No | No | No | 6 | 9 | unspecified | Mejor ejemplo público de Claude nativo con fact-check via web search |
| 4 | Claude 3.7 Sonnet AI chatbot agent with Anthropic web search and think functions | https://n8n.io/workflows/4036-claude-37-sonnet-ai-chatbot-agent-with-anthropic-web-search-and-think-functions/ | n8n team / community | ~3 months ago | Variante "vieja" del #3 con Claude 3.7 — útil como reference si Sonnet 4 da problemas | AI Agent, Anthropic Chat Model, Tools | Anthropic nativo | No | No | No | No | No | 5 | 6 | unspecified | Listado oficial |
| 5 | Generate AI LinkedIn Posts with Human Approval via Telegram and GPT | https://n8n.io/workflows/9472-generate-ai-linkedin-posts-with-human-approval-via-telegram-and-gpt/ | Yasser Sami | ~3 months ago | Telegram bot → request → AI Agent draft → "Good to go?" → si rechazo, 2do agent reescribe con feedback → Google Sheets | Telegram Trigger, Telegram, AI Agent, Set, Google Sheets | OpenAI / Gemini | No | **Sí (texto-only, ida y vuelta con feedback)** | No (LinkedIn manual) | No | No | 6 | 8 | unspecified | Mejor patrón público de HITL conversacional |
| 6 | Generate & schedule social media posts with GPT-4 and Telegram approval workflow | https://n8n.io/workflows/5773-generate-and-schedule-social-media-posts-with-gpt-4-and-telegram-approval-workflow/ | Femi Ad (hgray) | ~3 months ago | 23 nodes. Telegram approval bidireccional + Upload-Post a IG/TikTok/X/LI/FB | Telegram Trigger, Telegram, OpenRouter, HTTP Request (Upload-Post), Set, Code | OpenRouter (GPT-4, Claude) | No | Sí (approve/reject) | **Sí (Upload-Post, no Buffer)** | No | No | 7 | 7 | unspecified | Cobertura multi-plataforma alta |
| 7 | Post AI news to Telegram with Google Gemini and human approval | https://n8n.io/workflows/13216-post-ai-news-to-telegram-with-google-gemini-and-human-approval/ | Natnail Getachew (itan) | ~3 months ago | RSS (VentureBeat + AI Blog) → Gemini summary → draft a Telegram privado → click Approve → publica en canal Telegram público | RSS Read, If, Merge, Gemini, Telegram | Gemini | No | Sí | No (solo Telegram) | Sí (2 fuentes) | "Most recent" filter, no dedup persistente | 5 | 7 | unspecified | Patrón limpio HITL+RSS pero sin Buffer |
| 8 | Generate and publish carousels for TikTok and Instagram with GPT-Image-1 | https://n8n.io/workflows/4028-generate-and-publish-carousels-for-tiktok-and-instagram-with-gpt-image-1/ | Juan Carlos Cavero Gracia | ~3 months ago | 5 imágenes carousel: gen 1 con prompt + 4 edits secuenciales (consistencia estilo). Publish vía upload-post.com | HTTP Request (OpenAI Images), Merge, Set, HTTP Request (upload-post) | OpenAI (gpt-image-1 / DALL-E) — **swapear a gpt-image-2** | **Sí (5 imgs carousel)** | No | Sí (upload-post.com, no Buffer) | No | No | 6 | 9 | unspecified | Patrón "5 imgs estilísticamente consistentes" que necesitamos casi tal cual |
| 9 | Automate RSS to Instagram with AI-generated content and Cloudinary | https://n8n.io/workflows/11791-automate-rss-to-instagram-with-ai-generated-content-and-cloudinary/ | Paolo Ronco | ~3 months ago | RSS → AI caption + AI image → Cloudinary → Meta Graph API direct a IG | RSS Read, OpenAI, Edit Image, HTTP Request (Cloudinary), HTTP Request (Meta Graph) | OpenAI | Sí (single) | No | **Sí (Meta Graph API directo a IG)** | Sí | No | 7 | 6 | $3 paid template | Único ejemplo verificado con Meta Graph API directo |
| 10 | Create secure human-in-the-loop approval flows with Postgres and Telegram | https://n8n.io/workflows/9039-create-secure-human-in-the-loop-approval-flows-with-postgres-and-telegram/ | Mohammad (mohammad-1378) | ~3 months ago | Approval con HMAC-signed links + audit trail en Postgres (tickets, ticket_audit, workflow_errors) | Telegram, Postgres, HTTP Request, Code, Crypto | N/A (gobernanza pura) | No | **Sí (link-based + audit)** | No | No | No | 7 | 7 | unspecified | Patrón de seguridad/audit serio para HITL — útil si querés trazabilidad |
| 11 | Automate RSS content with AI: summarize, notify & archive | https://n8n.io/workflows/4503-automate-rss-content-with-ai-summarize-notify-and-archive/ | Victor (victoorsaad) | ~3 months ago | RSS → summary OpenAI → archive Google Sheets. Dedup débil (filter "<24h"). | RSS Read, OpenAI, Google Sheets, Set, If | OpenAI | No | No | No | Sí | **No real** (solo "<24h" filter) | 4 | 5 | unspecified | Baseline minimal — útil como template introductorio |
| 12 | Personalized AI tech newsletter using RSS, OpenAI and Gmail | https://n8n.io/workflows/3986-personalized-ai-tech-newsletter-using-rss-openai-and-gmail/ | n8n.io creator | ~3 months ago | RSS + vector DB + LLM → email digest. Vector embeddings = pseudo-dedup | RSS Read, OpenAI Embeddings, Vector Store, OpenAI Chat, Gmail | OpenAI | No | No | No | Sí | Sí (vía vector similarity) | 7 | 6 | unspecified | Único ejemplo público con dedup semántico (no solo GUID) |
| 13 | Daily tech news curation with RSS, GPT-4o-Mini, and Gmail delivery | https://n8n.io/workflows/7874-daily-tech-news-curation-with-rss-gpt-4o-mini-and-gmail-delivery/ | Alex Huy | ~3 months ago | 14 fuentes RSS (TechCrunch, MIT Tech Review, Verge, Wired, VentureBeat, ZDNet…) → Vertex AI scoring → top 10 → Gmail | RSS Read, Vertex AI, Set, Gmail | Google Vertex AI | No | No | No | **Sí (14 fuentes)** | No | 5 | 7 | unspecified | Mejor source-list ya curada para arrancar |
| 14 | AI blog post journalist (Perplexity for research, Anthropic Claude for blog) | https://n8n.io/workflows/5202-ai-blog-post-journalist-perplexity-for-research-anthropic-claude-for-blog/ | n8n.io creator | ~3 months ago | Perplexity busca + verifica fuentes → Claude redacta blog post estructurado (intro, secciones, takeaway, meta) | HTTP Request (Perplexity), Anthropic Chat Model, AI Agent, Set | **Anthropic nativo** + Perplexity | No | No | No | No | No | 6 | 8 | unspecified | Excelente referencia para "fact-check + draft" en dos pasadas |
| 15 | Batch process prompts with Anthropic Claude API | https://n8n.io/workflows/3409-batch-process-prompts-with-anthropic-claude-api/ | n8n.io creator | ~3 months ago | Batch API de Claude (50% más barato) para procesar N prompts en paralelo | HTTP Request, Code, Anthropic credential | Anthropic (batch) | No | No | No | No | No | 4 | 6 | unspecified | Útil si querés scoring de muchos items en batch barato |
| 16 | enescingoz/awesome-n8n-templates (repo) | https://github.com/enescingoz/awesome-n8n-templates | enescingoz et al. | March 2026 | 280+ templates JSON listos para importar, 18 categorías | N/A (catálogo) | Mix | Mix | Mix | Mix | Mix | Mix | N/A | N/A | CC-BY-4.0 | **22.1k stars, 6k forks** — la fuente más grande |

### Templates considerados y descartados (por completitud)
- "Webpage change detection & alerts with Google Suite and hash tracking" (#3366) — patrón crypto-hash + Remove Duplicates útil pero es webpage, no RSS. Vale como referencia técnica, no como base.
- "Automate Instagram posts with GPT-4o captions, ImgBB & Buffer integration" (#6334) — Buffer **vía Zapier bridge**, no GraphQL directo. Sub-óptimo para producción.
- ScraperNode/awesome-n8n-templates (GitHub) — claim de 8.697 templates pero sin verificar individualmente; demasiado ruido para sourcing manual.
- "Multi-platform video publisher" (#3895), "Upload to Instagram, TikTok & YouTube from Google Drive" (#2894) — video-first, no aplican a carousel de imágenes.

### Por qué no llegué a 20
Encontré 16 reales. Los descartes (~4-6 templates) caían en una de tres categorías: (a) video-only sin carousel, (b) duplicados conceptuales sin valor incremental, (c) repos GitHub sin templates verificables (números inflados, "8.697 workflows" que no son auditables uno por uno). Prefiero 16 verificados que 20 con relleno.

---

## Top 5-7 recomendados para importar y adaptar

### 1. #12533 — Curate AI newsletter from RSS + OpenAI + Slack (Maksudur Rahman)
**Justificación:** El esqueleto más completo del catálogo. Cubre fetch multi-source + scoring LLM + top-N + draft + HITL básico (Slack reply).
**Adaptar:**
- Swap Slack → Telegram Bot
- Swap OpenAI Chat → Anthropic Chat Model (Sonnet)
- Swap "15 fuentes default" → tus 12 fuentes LATAM mix
- Agregar rubric scoring de 8 categorías como Structured Output Parser
**Borrar:** la pieza de Slack interactive blocks, el feedback loop iterativo (sustituir por edit-in-Telegram).
**Agregar:** dedup persistente (importar de #6389), fact-check pass (importar de #14), image carousel (importar de #8), Buffer publish (custom).

### 2. #6389 — Smart RSS + AI filtering + Baserow + Slack (Daniel Shashko)
**Justificación:** Único template público con dedup **persistente real** (Baserow guarda GUIDs procesados). Crítico para evitar repetir items entre runs.
**Adaptar:** Baserow → Supabase (ya está en tu stack confirmado). Patrón es idéntico: tabla `seen_items` con `guid + url + processed_at`, query previo al scoring, insert post-aceptación.
**Borrar:** la lógica AI-Agent-for-dedup (caro y lento — un simple `WHERE NOT IN (SELECT guid FROM seen_items WHERE processed_at > NOW() - 30 days)` es 100x más barato).
**Agregar:** índice TTL de 30 días.

### 3. #4399 — Anthropic AI Agent Sonnet 4 / Opus 4 + Web Search + Think
**Justificación:** Es el único template público que muestra Claude nativo con web_search como tool. Es exactamente el patrón que necesitás para el fact-checking step (#8 de tu pipeline).
**Adaptar:** Usar para el fact-check node. Sistema-prompt: "Recibís el brief draft. Verificá cada claim numérico/factual con web_search. Devolvé JSON con `verified_claims`, `unverified_claims`, `corrections_needed`."
**Borrar:** routing Opus/Sonnet (overkill para tu volumen — quedate con Sonnet).
**Agregar:** Structured Output Parser con tu schema de fact-check report.

### 4. #4028 — Carousel TikTok/IG con gpt-image-1 (Juan Carlos Cavero Gracia)
**Justificación:** Único template público que resuelve el "5-7 imágenes con consistencia estilística" generando 1 imagen + N edits sucesivos (cada edit toma la anterior como base). Esto es la única forma viable de tener coherencia visual sin entrenar un LoRA.
**Adaptar:** Swap modelo de `gpt-image-1` → `gpt-image-2` (cambiar el `model` param en HTTP Request). Swap upload-post.com → Buffer GraphQL API.
**Borrar:** TikTok publish via upload-post (si vas con Buffer).
**Agregar:** brand style preamble en el prompt (mismo system prompt para las 5 imágenes), guardrails de aspect ratio.

### 5. #9472 — LinkedIn HITL via Telegram con feedback iterativo (Yasser Sami)
**Justificación:** Mejor patrón público de HITL **conversacional** con Telegram. No es solo approve/reject — soporta "rechazo + texto de feedback → 2do agent rewrite". Si tu voz editorial es exigente, este loop te ahorra muchos rounds.
**Adaptar:** Cambiar LinkedIn → tu staging table en Supabase (cola "approved → publish next").
**Borrar:** Google Sheets como storage final.
**Agregar:** comando `/edit` que abre editor inline en Telegram (Markdown blob editable), comando `/reject` con razón, comando `/approve`.

### 6. #9039 — HITL approval con Postgres + HMAC links (Mohammad)
**Justificación:** Si te importa audit trail (qué se aprobó, cuándo, quién, qué se rechazó y por qué), este es el patrón. HMAC firma cada link → no puede ser tampered, expira en X minutos.
**Adaptar:** Postgres → Supabase. Telegram queda como está.
**Borrar:** la parte "tickets" (es para IT requests). Quedate con el patrón crypto.
**Agregar:** integrá audit trail con la tabla `seen_items` (#6389) para tener un único log unificado.

### 7. #14 — AI blog post journalist (Perplexity + Anthropic Claude)
**Justificación:** Mejor patrón público de "research-then-write" en dos pasadas separadas. Aplicable a tu paso 7-8 (generate brief → fact-check brief).
**Adaptar:** Reemplazar Perplexity por tu fact-check Claude+web_search (#4399), o mantener Perplexity si querés segundo opinion barato.
**Borrar:** el formato blog largo (intro/secciones/meta).
**Agregar:** Smart Brevity schema (Why It Matters / What Happened / What's Next + 3 bullets).

---

## Combinación recomendada

**El stack óptimo: #12533 (esqueleto) + #6389 (dedup persistente) + #4399 (fact-check Claude) + #4028 (carousel image gen) + #5773 o #9472 (Telegram HITL).**

Importás #12533 como workflow base — te da el shape "RSS → scoring LLM → top-N → draft → notify". Le injertás el subgrafo de #6389 entre "fetch RSS" y "scoring" (Supabase lookup → filter `NOT IN seen_items`). El step "generate brief" lo dejás como está pero swapeado a Anthropic node. El step "fact-check" lo armás copiando el sub-workflow de #4399 (Anthropic Agent + web_search tool) y lo conectás post-draft. El step "image carousel" lo copiás de #4028 con el swap a gpt-image-2 y el prompt-chain de 5 imágenes consistentes. El step "HITL" lo armás con el patrón conversacional de #9472 (approve/reject/feedback loop) opcionalmente con el audit trail de #9039 si querés rigor. **Cobertura estimada: ~70-75% del pipeline.**

Falta custom (~25-30%): (a) el rubric scoring de 8 categorías como Structured Output Parser (ningún template tiene este rubric específico LATAM-aware), (b) el compliance check contra reglas Meta + brand voice (ningún template combina ambas), (c) el push final a Buffer GraphQL API (no hay node oficial — todo via HTTP Request custom), (d) la cola de items aprobados con scheduling diferido (publicación a la hora óptima, no en el momento del approval).

---

## Patterns recurrentes detectados

1. **"RSS Read → Edit Fields (Set) → ..."**: Prácticamente el 100% de los templates RSS normalizan items con un Set node justo después del RSS Read, mapeando `title/link/pubDate/content/guid` a un schema estable. No vale la pena reinventarlo.
2. **Dedup débil es la regla**: De 16 templates, solo 2 (#6389 con Baserow GUIDs, #12 con embeddings vectoriales) tienen dedup persistente real. La mayoría usa "filter pubDate <24h" que rompe en cuanto tenés feeds con fechas mal formateadas o publicaciones tardías.
3. **AI-Agent-as-Dedup es un anti-pattern caro**: #6389 muestra el patrón pero también su costo — usar un LLM para comparar listas largas de "seen vs new" es 10-100x más caro que un `SELECT ... WHERE guid NOT IN (...)`. Útil para fuzzy/semantic dedup pero overkill para GUID matching.
4. **Telegram HITL con callback_query (inline buttons)** es estándar en templates simples; los templates "serios" (#9039) usan HMAC-signed links externos. Para vos lo correcto probablemente es inline buttons + un comando `/edit` que abre conversación.
5. **Structured Output Parser** es el patrón aceptado para forzar JSON estable del LLM. Aparece en #3, #14, y en el blog post de hackceleration. Sin esto, el scoring va a fallar el 5-10% de las veces por outputs malformed.
6. **Sticky Notes como documentación inline** — todos los templates serios incluyen Sticky Notes explicando cada sub-sección. Útil cuando volvés al workflow 3 meses después.
7. **Casi nadie usa Buffer**: La mayoría de templates 2026 prefiere Blotato o Upload-Post (servicios SaaS unified) sobre Buffer GraphQL. Hay UN solo template oficial con Buffer (#6334) y va via Zapier bridge (sub-óptimo).
8. **gpt-image-1 sigue siendo el default en templates** a mayo 2026, aun cuando gpt-image-2 ya está disponible. Hay que swap manual.
9. **"3 months ago" en todo el catálogo n8n.io** — sospecha de que n8n hizo un re-indexing batch del catálogo a ~febrero 2026. No es confiable como signal de freshness real. Mirar autor + commits si es público en GitHub.

---

## Gaps / lo que vas a tener que construir desde cero

1. **Rubric scoring de 8 categorías LATAM-aware**: No existe template público que score noticias contra rubric multi-eje (relevancia LATAM, novedad, urgencia, credibilidad fuente, potencial educativo, viral, fit con marca, riesgo penalty). Hay que diseñar el system prompt + Structured Output Parser schema + el Code node que computa el score agregado (weighted sum). **Effort estimado: 1-2 días.**
2. **Compliance check Meta + brand voice**: Hay templates de compliance para documentos legales (#11861, #7662) y de moderación de reviews (#12129) pero nada que combine reglas Meta (no claims médicos, no investment advice, no engagement-bait) + brand voice (anti-hype, sectorial, tono sobrio). Construir Claude prompt + checklist como Code node post-LLM. **Effort: 1 día.**
3. **Buffer GraphQL publish (carousel imágenes)**: No hay node oficial. Hay que armar HTTP Request POST con GraphQL mutation + auth Bearer + manejo de upload de imágenes (Buffer pide URL públicas, no binarios → necesitás Supabase Storage o Cloudinary intermedio). El template #6334 lo hace via Zapier bridge, no directo. **Effort: 2 días (incluye debugging GraphQL).**
4. **Editor inline en Telegram para preview**: El patrón "approve/reject" existe; el patrón "edit Markdown inline antes de aprobar" no aparece en ningún template. Hay que armar conversation state machine con Telegram Bot API + waitForResponse en n8n. **Effort: 1-2 días.**
5. **Scheduling diferido post-approval**: Aprobar a las 7:30am pero publicar a las 12pm (horario óptimo IG LATAM). Implica una cola con `publish_at` y un segundo workflow cron que cada 15min busca items `WHERE publish_at <= NOW() AND status = 'approved'`. **Effort: medio día.**
6. **Source health monitoring**: Si un RSS feed muere o cambia URL, el pipeline falla silencioso. Necesitás alerting por feed muerto. No hay template específico. **Effort: medio día.**
7. **Cost tracker**: Track Anthropic + OpenAI usage por run (tokens in/out, $) en Supabase para no llevarse sorpresas. **Effort: medio día.**

**Effort total custom estimado: 6-8 días de trabajo enfocado.**

---

## Recursos de aprendizaje extra

### Docs oficiales n8n (críticos)
- Anthropic Chat Model node: https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatanthropic/
- Anthropic app node: https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-langchain.anthropic/
- Anthropic credentials setup: https://docs.n8n.io/integrations/builtin/credentials/anthropic/
- Remove Duplicates node (modo "previous executions"): https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.removeduplicates/
- Structured Output Parser: https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.outputparserstructured/
- Cloud free trial detalles: https://docs.n8n.io/manage-cloud/cloud-free-trial/

### Posts blog técnicos
- "Build AI Agents with n8n + Claude API [Complete Guide]" — n8nlab.io: https://n8nlab.io/blog/build-ai-agents-n8n-claude-api
- "n8n + Anthropic Claude Integration: 5 AI Workflows" — n8nautomation.cloud: https://n8nautomation.cloud/blog/n8n-anthropic-claude-integration-ai-workflows
- "Building an AI News Curation Agent with n8n, Claude, and WordPress REST API" — dev.to/hackceleration: https://dev.to/hackceleration/building-an-ai-news-curation-agent-with-n8n-claude-and-wordpress-rest-api-1mhh
- "Building your own LLM evaluation framework" — blog.n8n.io: https://blog.n8n.io/llm-evaluation-framework/
- "n8n Cloud Execution Limits Explained: Real Cost in 2026" — n8nautomation.cloud: https://n8nautomation.cloud/blog/n8n-cloud-execution-limits-explained-cost-2026

### YouTube
- "Turn Claude into a POWERFUL AI Agent in n8n" — https://www.youtube.com/watch?v=cNSqSnTAuSA (tutorial Claude 3.7 + web_search + Think tool — patrón del template #4399)
- "n8n Tutorial for 2026: How To Build AI Agents for FREE" — https://www.youtube.com/watch?v=Pqp4qJ5sS5g (intro práctico AI Agent node)
- "Remove Duplicates in n8n — The Secret Node to Clean Your Data" — https://www.youtube.com/watch?v=1k8DoLBpeLI

### Repos GitHub
- enescingoz/awesome-n8n-templates (22.1k stars, March 2026): https://github.com/enescingoz/awesome-n8n-templates — la fuente principal de templates JSON importables
- ghwoodard/n8n-social-media-automation (MIT): https://github.com/ghwoodard/n8n-social-media-automation — único ejemplo público de Buffer GraphQL desde n8n
- MookieLian/n8n-nodes-instagram: https://github.com/MookieLian/n8n-nodes-instagram — community node Instagram Graph API (alternativa a Buffer)
- restyler/awesome-n8n: https://github.com/restyler/awesome-n8n — index curado de community nodes y tutoriales

### Threads community.n8n.io útiles
- "New to n8n - How do I enable web search in Claude Sonnet 4?": https://community.n8n.io/t/new-to-n8n-how-do-i-enable-web-search-in-claude-sonnet-4/168264 (confirma que web_search **no** está como toggle nativo, hay que pasarlo como Tool)
- "Web Search with Anthropic Models?": https://community.n8n.io/t/web-search-with-anthropic-models/252767
- "[Node Request] Instagram Graph API integration": https://community.n8n.io/t/node-request-instagram-graph-api-integration/236127 (confirmación 2026: n8n **no** tiene node oficial Instagram Graph)

---

## Caveats y consideraciones

### n8n cloud pricing (mayo 2026)
- **Contradicción detectada entre fuentes:**
  - n8n.io/pricing (fuente oficial): Starter €20/mes (anual), Pro €50/mes (anual), Business €667/mes (anual), 2.5k / 10k / 40k executions respectivamente.
  - costbench.com y connectsafely.ai: Starter "€24/mes", Pro "€60/mes", Business "€800/mes" — pricing **mensual** sin descuento anual.
- **Resolución probable**: ambos están bien — los números más bajos son con billing anual (~20% off), los altos son monthly. La fuente oficial confirma.
- **NO hay free tier permanente**. Free trial = 14 días + features Pro + ~1000 executions cap.
- **Para tu pipeline**: 1 run/día × 30 días = 30 runs/mes en el cron diario. Cada run interno dispara ~20-40 sub-executions (cada node es una execution en n8n cloud). Estimado realista: 600-1200 executions/mes solo del cron, sin contar HITL callbacks. **Starter (€20-24/mes) alcanza con holgura.**
- **Riesgo de tier-jumping**: si agregás 2do workflow (ej. analytics) o subís a 3 runs/día (mañana/mediodía/noche), te vas a 5-10k executions/mes y necesitás Pro (€50-60/mes).
- **Alternativa**: self-hosted (community edition, MIT, gratis) en un VPS de $5-7/mes (Hetzner, Contabo). Misma feature parity. Único tradeoff: vos manejás backups, updates, SSL. Vale la pena considerarlo si pensás escalar a 3+ workflows.

### Anthropic en n8n — el detalle crítico
- **Hay node oficial nativo** (`Anthropic Chat Model` + `Anthropic` app node). NO necesitás HTTP Request para casos básicos. Confirmado vía:
  - https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatanthropic/
  - https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-langchain.anthropic/
  - https://n8n.io/integrations/anthropic/
- **Soporta Claude Sonnet 4 y Opus 4** explícitamente (template #4399 lo usa).
- **Web search NO es toggle nativo**: confirmado en thread community.n8n.io/t/168264. Hay que armarlo como Tool externo apuntando al endpoint `web_search` de Anthropic. El template #4399 ya hace esto — copialo.
- **Cache control (prompt caching)**: a confirmar si el node nativo lo expone. Si no, fallback a HTTP Request para esos casos (el system prompt grande del scoring se debería cachear, ahorra 50-90% del costo).
- **Batch API**: template #3409 muestra cómo usarlo via HTTP Request (no hay toggle en node nativo). Útil para scoring de 50-100 items en una pasada con 50% descuento.

### OpenAI gpt-image-2 — confirmaciones
- **Existe, se llama oficialmente `gpt-image-2`**, snapshot `gpt-image-2-2026-04-21`. Confirmado en:
  - https://openai.com/index/introducing-chatgpt-images-2-0/
  - https://developers.openai.com/api/docs/models/gpt-image-2
- **Endpoints**: `v1/images/generations` y `v1/images/edits` (ambos confirmados — el edit endpoint es crítico para tu patrón "1 imagen + N edits con consistencia estilística" del template #4028).
- **Features nuevas relevantes**: rendering de texto mejorado (útil para imágenes con type en español), 4K resolution, soporte localizado para idiomas (japonés/koreano/chino/hindi/bengalí — español ya existía). Capability "Agentic" / O-series reasoning integration.
- **Pricing**: NO confirmé números exactos por imagen — la doc remite a la pricing calculator. Asumir similar o ligeramente más caro que gpt-image-1 hasta confirmar (estimación: $0.04-0.08 por imagen 1024x1024 — **hipótesis, verificar antes de scale**).
- **Disponibilidad API "early May 2026"**: a fecha 2026-05-11 debería estar live, pero verificar via call de prueba. Si no está, fallback a gpt-image-1 que sigue funcionando.

### Buffer API
- **Buffer migrate a GraphQL API**: legacy REST en api.bufferapp.com → nueva GraphQL en api.buffer.com. Templates viejos pueden usar legacy y romperse.
- **TikTok via Buffer es limitado**: posts simples sí, features avanzadas (sounds, effects) no.
- **NO hay node oficial Buffer en n8n**: todo via HTTP Request con GraphQL mutations. Repo de referencia: ghwoodard/n8n-social-media-automation.
- **Alternativas a Buffer (considerar)**: Blotato (template #7187 oficial), Upload-Post (template #5773 oficial, #3524, #6 de mi lista usan esto). Costos: Blotato ~$15-30/mes, Upload-Post ~$10-25/mes. Buffer ~$5-15/mes para 1 brand. Si tu volumen es 1 post/día, los tres son viables.

### Riesgos técnicos identificados
1. **Web search en Claude vía Tool**: si Anthropic cambia su Tool spec, el patrón del #4399 puede romperse silencioso. Mantener fallback a Perplexity (template #14) o HTTP Request al endpoint web_search de Anthropic directo.
2. **n8n.io template "3 months ago" timestamps**: no confiables como signal de freshness. Templates pueden estar abandonados sin que se note. Verificar autores en Twitter/X y community.n8n.io antes de invertir tiempo.
3. **Instagram Graph API requiere business account + FB page**: 2-3 horas de setup la primera vez. NO es algo que automatices fácil.
4. **TikTok publishing API tiene approval process**: TikTok Content Posting API requiere app approval. Buffer/Blotato/Upload-Post evitan esto. Si vas directo a TikTok API → 1-4 semanas de waiting.
5. **Meta rate limits IG Graph API**: 200 posts/24h por usuario, pero shadowban-risk a partir de patrones automatizados. 1 post/día es seguro; 5+/día → revisar.
6. **n8n cloud cold-start latency**: en plan Starter, workflows pueden tener ~3-10s de cold start si no se ejecutan frecuente. No es problem para cron diario, sí para HITL callbacks (Telegram bot puede sentir lag).
7. **LLM rate limits**: Anthropic tier-1 (default): 50 requests/minute, 40k input tokens/min, 8k output tokens/min. Tu pipeline puede pegarse a esos límites si scoreás 50+ items en paralelo. Solución: rate limiter en Code node o Batch API.

### Notas de verificación
- **Confirmado vía docs.n8n.io**: existencia de nodes Anthropic, Remove Duplicates, Structured Output Parser, Telegram, RSS Read.
- **Confirmado vía openai.com**: existencia y disponibilidad de gpt-image-2.
- **Confirmado vía n8n.io/pricing**: tiers actuales y ausencia de free tier permanente.
- **Confirmado vía community.n8n.io**: web search no es toggle nativo en Claude node.
- **NO confirmado / hipótesis**: pricing exacto gpt-image-2 (asunción $0.04-0.08/img), cache control disponible en node Anthropic nativo (asumir que no, fallback HTTP Request), Buffer GraphQL mutation exacta para carousel IG (hay que probarla, no hay docs públicos exhaustivos).
- **Contradicción anotada**: pricing n8n cloud (mensual vs anual) — resuelto via fuente oficial.
- **Limitación de este research**: no descargué los JSON crudos de cada template para inspeccionar nodes uno-por-uno. La info de "nodes principales" sale de las páginas descriptivas de n8n.io, que son resumidas. Para due diligence final: import cada template top-7 a tu instance n8n y abrí el JSON real antes de comprometerte a una arquitectura.

---

**Fin del documento.**
