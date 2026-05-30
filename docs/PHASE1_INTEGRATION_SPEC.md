# Phase 1 Integration Spec — Dinero IA

**Fecha:** 2026-05-30
**Status:** Diseño técnico para Fase 1 (post-validación Fase -1).
**Asume:** ContentStudio + Blotato + Beehiiv (ADR-017 stack SaaS-first) + n8n cloud para moat editorial.

> **Por qué este doc existe:** el workflow Fase 0 (`infra/n8n/fase0.json`) prueba el moat editorial (scorer + brief + compliance) hasta Telegram. Fase 1 agrega: HITL bidireccional + 3 publish webhooks SaaS + analytics tracking. Este spec define cómo se conectan las piezas sin handwaving.

---

## Topología Fase 1

```
                     ┌─────────────────┐
   cron 6am MX ───►  │  n8n cloud      │
                     │   (moat editor) │
                     │                 │
                     │ A2 → A3 → A4 →  │
                     │   A9 → Telegram │
                     └────────┬────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │   Telegram HITL         │
                │   (Manuel decide)       │
                │   [✅] [✏️] [❌]        │
                └────┬─────────┬──────────┘
                     │         │
                  Aprobar   Editar
                     │         │
                     ▼         ▼
              ┌──────────┐  ┌──────────┐
              │ Webhook  │  │ A11      │
              │ Trigger  │  │ Editor   │
              │ (n8n)    │  │ (Opus 4) │
              └────┬─────┘  └────┬─────┘
                   │             │  (vuelve al Telegram preview)
                   ▼
        ┌──────────────────────────────────┐
        │  PUBLISH FANOUT (3 paralelos)    │
        └──────────────────────────────────┘
           │              │              │
           ▼              ▼              ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ContentStdy │  │  Blotato   │  │  Beehiiv   │
    │            │  │            │  │            │
    │ caption +  │  │ carousel + │  │ newsletter │
    │ scheduling │  │ AI images  │  │ section    │
    │ IG/TT/LI   │  │            │  │            │
    └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
          │               │                │
          ▼               ▼                ▼
        Posted          Carousel        Email sent
        (8am MX)        ready in CS     (9am MX)
                        feed
```

---

## Sección 1 — HITL bidireccional Telegram

### Estructura del mensaje

Cuando el workflow termina A9 con `verdict === "approved" || "approved_with_warnings"`, el Telegram preview incluye **inline_keyboard** con 4 botones:

```json
{
  "chat_id": "{{ MANUEL_CHAT_ID }}",
  "text": "<preview markdown>",
  "parse_mode": "Markdown",
  "reply_markup": {
    "inline_keyboard": [
      [
        { "text": "✅ Aprobar", "callback_data": "approve:{{ brief_id }}" },
        { "text": "✏️ Editar", "callback_data": "edit:{{ brief_id }}" }
      ],
      [
        { "text": "🔁 Regenerar A3", "callback_data": "regen:{{ brief_id }}" },
        { "text": "❌ Rechazar", "callback_data": "reject:{{ brief_id }}" }
      ]
    ]
  }
}
```

### Callback handler (Telegram Trigger node n8n)

Workflow separado: `dinero-ia-fase1-hitl.json` con:

1. **Telegram Trigger node** — escucha `callback_query` events del bot
2. **Parse callback_data** — extrae `action` y `brief_id`
3. **Lookup brief en Supabase** (tabla `briefs_pending`) por `brief_id`
4. **Switch node** según `action`:
   - `approve` → publish fanout (sección 2)
   - `edit` → A11 Editor LLM (Opus 4) recibe feedback del usuario
   - `regen` → vuelve a A3 con re-roll del prompt (temperature +0.1)
   - `reject` → marca como `rejected` en Supabase, no se publica

### Estado del brief en Supabase

Schema sugerido tabla `briefs_pending`:

```sql
CREATE TABLE briefs_pending (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_url TEXT NOT NULL,
  source_name TEXT NOT NULL,
  signal_score NUMERIC,
  sub_categoria TEXT,
  brief JSONB NOT NULL,
  compliance JSONB,
  telegram_message_id BIGINT,
  status TEXT CHECK (status IN ('pending', 'approved', 'edited', 'rejected', 'regenerated', 'published')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  decided_at TIMESTAMPTZ,
  edit_feedback TEXT,
  published_to JSONB
);
```

**Sin Supabase Fase 0/1 inicial:** se puede usar n8n's `Static Data` storage (más limitado pero suficiente para 1 pieza/día).

### Edit-loop con A11

Cuando Manuel toca "✏️ Editar":

1. Telegram bot pregunta: *"¿Qué querés ajustar? (responder con texto)"*
2. Manuel responde con texto libre (ej: "el hook está flojo, hacelo más viral pero sin perder el body sobrio")
3. n8n recibe el reply (otro Telegram Trigger)
4. A11 Editor LLM (Opus 4) toma el brief original + feedback Manuel + brand_voice.md v3 + genera versión nueva
5. Vuelve al Telegram preview con la versión nueva + mismos 4 botones

**Loop limit:** max 2 ediciones consecutivas. Después: descartar o pasar igual al publish (Manuel decide).

---

## Sección 2 — Publish Fanout (3 webhooks paralelos)

Al recibir `approve:{brief_id}`, n8n hace 3 calls en paralelo (sin esperar uno antes del otro):

### 2.1 — ContentStudio (IG carousel + caption + TikTok + LinkedIn)

**Endpoint:** `POST https://api.contentstudio.io/v1/social/posts`

**Auth:** Bearer token (API key en n8n credentials, NO en repo)

**Payload:**

```json
{
  "title": "<brief.title>",
  "content": {
    "instagram": {
      "caption": "<hook_calibrado>\n\n<por_que_importa_finanzas en 2 líneas>\n\n<cta_tentativo>\n\n<disclaimer_texto_sugerido si disclaimer_requerido>\n\n<hashtags_finanzas_latam>",
      "media_urls": ["<carousel slide 1 url>", "..."],
      "hashtags": ["#FinanzasPersonales", "#InversionesLATAM", "#IAparaTodos"]
    },
    "tiktok": {
      "caption": "<hook + cta + 3-5 hashtags>",
      "video_url": null
    },
    "linkedin": {
      "caption": "<por_que_importa_finanzas + accionable + disclaimer>",
      "media_urls": ["<carousel pdf url>"]
    }
  },
  "schedule": {
    "instagram_at": "2026-05-31T13:00:00Z",
    "tiktok_at": "2026-05-31T13:00:00Z",
    "linkedin_at": "2026-05-31T14:00:00Z"
  },
  "tags": ["dinero-ia", "{{ sub_categoria }}"]
}
```

**Retry:** 3 intentos con backoff exponencial (5s, 15s, 45s). Si falla las 3: notificar Manuel via Telegram + dejar en queue `failed_publishes` para retry manual.

**Note crítico:** ContentStudio NO genera carouseles — necesita las imágenes ya generadas. Esas vienen de Blotato (2.2). Por lo que en realidad, el flujo correcto es:

```
1. Llamar Blotato primero (genera carousel slides)
2. Esperar respuesta con URLs
3. Llamar ContentStudio con URLs ya generadas
4. Llamar Beehiiv en paralelo (no necesita imágenes)
```

Ver "Orden correcto" abajo.

### 2.2 — Blotato (carousel generation + AI images)

**Endpoint:** `POST https://api.blotato.com/v1/carousels/generate`

**Auth:** API key Blotato (n8n credentials)

**Payload:**

```json
{
  "template_id": "dinero-ia-dark-editorial",
  "slides": [
    {
      "slide_type": "hook",
      "text": "<hook_tentativo>",
      "background_color": "#0F0F10",
      "primary_font": "Inter Bold",
      "accent_color": "#00D9A0"
    },
    {
      "slide_type": "data_point",
      "text": "<datos_clave[0]>",
      "source_attribution": "<fuente + fecha + moneda>"
    },
    {
      "slide_type": "step",
      "text": "<paso 1 del prompt_o_template_sugerido>"
    },
    "...",
    {
      "slide_type": "disclaimer",
      "text": "<disclaimer_texto_sugerido>",
      "footer": "Educativo, no asesoría — Dinero IA"
    }
  ],
  "output_format": "carousel_5_to_7_slides",
  "aspect_ratio": "1080x1080",
  "brand_kit_id": "dinero-ia-dark"
}
```

**Pre-requisito Fase 1:** Manuel crea **template `dinero-ia-dark-editorial`** en Blotato la primera vez (UI manual). Cumple POST_STANDARD §7: dark mode #0F0F10, Inter Bold para hooks, JetBrains Mono para captions, accent mint #00D9A0.

**Response esperada:**

```json
{
  "carousel_id": "blt_abc123",
  "status": "ready",
  "slide_urls": [
    "https://cdn.blotato.com/dinero-ia/abc123_slide1.jpg",
    "..."
  ],
  "carousel_pdf_url": "https://cdn.blotato.com/dinero-ia/abc123.pdf"
}
```

**Retry:** 2 intentos. Si falla: fallback a generación manual con OpenAI gpt-image-2 directo (workflow alternativo `dinero-ia-fallback-images.json`).

### 2.3 — Beehiiv (newsletter section)

**Endpoint:** `POST https://api.beehiiv.com/v2/publications/{publication_id}/posts`

**Auth:** Bearer API key Beehiiv

**Payload:**

```json
{
  "publication_id": "{{ DINERO_IA_PUB_ID }}",
  "title": "<brief.title>",
  "subtitle": "<por_que_importa_finanzas en 1 línea>",
  "body": "<full markdown content>",
  "status": "draft",
  "schedule_at": "2026-05-31T13:00:00Z",
  "subject_line": "<hook_tentativo (subject A/B test variants generadas por A3)>",
  "preview_text": "<datos_clave[0]>"
}
```

**Body markdown structure (estandarizada):**

```markdown
## ¿Qué pasó?

<que_paso>

## ¿Por qué importa para tus finanzas?

<por_que_importa_finanzas>

## Datos clave

- <datos_clave[0]>
- <datos_clave[1]>
- <datos_clave[2]>

## El prompt/template que probé

`<prompt_o_template_sugerido>`

## Cómo aplicarlo a tu caso LATAM

<angulo_finanzas_latam>

---

*<disclaimer_texto_sugerido>*

*Productos mencionados: <productos_mencionados>*
*Fuente original: <source_url>*
```

**Retry:** 2 intentos. Si falla: dejar en draft + notificar Telegram (Manuel publica manual).

### Orden correcto del fanout

Para evitar publicar IG sin las imágenes generadas:

```
Step 1 (parallel):
  ├─ Blotato.generate_carousel    (espera response con URLs)
  └─ Beehiiv.create_post          (no depende de imágenes)

Step 2 (después de Blotato OK):
  └─ ContentStudio.schedule_posts (necesita URLs del step 1 Blotato)
```

En n8n: usar nodo **Merge** para esperar Blotato response antes de llamar ContentStudio.

---

## Sección 3 — Analytics & dashboards

### Lo que ya tenés "gratis" (sin diseño nuestro)

| Plataforma | Métricas disponibles | Cómo accedés |
|---|---|---|
| ContentStudio | Posts publicados, IG views/likes/saves/comments, TikTok views/shares, LinkedIn impressions/reactions | UI ContentStudio + API GET `/v1/analytics/posts` |
| Blotato | Carousels generated, downloads | UI Blotato dashboard |
| Beehiiv | Subs total, open rate, click rate, growth chart, top posts | UI Beehiiv |
| n8n cloud | Workflow executions, errors, latency | UI n8n + email alerts |
| Telegram | Mensajes recibidos/enviados (log local) | Bot log |

### Cross-platform aggregator (custom Fase 3+)

Si Manuel quiere ver TODO en un solo lugar, Fase 3 contempla:

1. **Workflow n8n cron diario 11pm:** GET analytics de cada plataforma → INSERT en Supabase tabla `metrics_daily`
2. **Dashboard view:** Supabase view o Metabase free → tabla diaria con: piezas publicadas, engagement promedio por plataforma, subs nuevos newsletter, costo del día Anthropic+OpenAI
3. **Telegram daily report 9am:** bot manda resumen del día anterior en 1 mensaje

**No urgente para arranque Fase 1.** Implementar después de que Fase 1 esté estable 14 días.

---

## Sección 4 — Costos esperados (validar con uso real)

| Tier | Costo/mes | Concepto |
|---|---:|---|
| ContentStudio Standard | $19 | 10 social accounts, 5 workspaces, AI captions |
| Blotato Starter | $29 | 1000 credits/mes (~50-100 carousels) |
| Beehiiv Launch | $0 | Hasta 2,500 subs |
| n8n cloud (trial → Starter) | $0 → $30 | 5,000 ejec/mo |
| Anthropic API (moat 4 agents) | $25-42 | 1 pieza/día |
| OpenAI gpt-image-2 (backup) | $6-8 | Si Blotato no rinde para algunos slides |
| Domain | $1 | dineroia.com $12/año |
| **Total estimado Fase 1** | **$80-130/mo** | |

---

## Sección 5 — Pre-requisitos antes de importar este workflow a n8n

Antes de ejecutar el workflow `dinero-ia-fase1-publish.json` (próxima entrega), Manuel debe:

1. ✅ **Fase -1 ejecutada + voz validada** (>2% engagement promedio)
2. ✅ **Workflow Fase 0 corrido + 3 briefs decentes en Telegram**
3. ⚠️ **Cuenta ContentStudio Standard** ($19/mo) — crear con `aibrieflatam.media@gmail.com`. Conectar IG + TikTok + LinkedIn via OAuth.
4. ⚠️ **Cuenta Blotato Starter** ($29/mo) — crear template `dinero-ia-dark-editorial` siguiendo POST_STANDARD §7.
5. ⚠️ **Cuenta Beehiiv Launch** ($0) — registrar publicación, configurar from address, footer compliance.
6. ⚠️ **Cuenta Supabase Free** (opcional Fase 1, recomendado para tabla `briefs_pending`) — aplicar migration `infra/supabase/migrations/001_dinero_ia_briefs.sql` (próxima entrega).
7. ⚠️ **API keys cargadas en n8n credentials** (NO en repo):
   - `anthropicApi`
   - `openaiApi`
   - `telegramApi` (bot token + chat ID)
   - `contentStudioApi`
   - `blotatoApi`
   - `beehiivApi`
   - `supabaseApi` (opcional)

---

## Sección 6 — Lo que falta diseñar después de este spec

1. **Workflow JSON Fase 1 publish** (`dinero-ia-fase1-publish.json`) — el siguiente que armamos
2. **Workflow JSON Fase 1 HITL** (`dinero-ia-fase1-hitl.json`) — callback handler Telegram
3. **Workflow JSON Fase 1 A11 editor** (`dinero-ia-fase1-editor.json`) — edit-loop LLM
4. **Migration SQL Supabase** — tabla `briefs_pending` + `metrics_daily`
5. **Brand kit Blotato config** — UI manual de Manuel
6. **Webhook signatures + auth doc** — cómo validamos que un callback Telegram es legítimo (anti-spoofing)

Todo esto se entrega después de que Fase 0 corra estable. **NO antes**, porque Fase 0 valida que el moat editorial funciona — si A2/A3/A9 dan mala señal, todo Fase 1 fallaría igual.
