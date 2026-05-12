# N8N Workflow Skeleton — AI Brief LATAM

**Fecha:** 2026-05-12
**Status:** Diseño aprobado en sesión 4. Pendiente: implementación del JSON v2.
**Source de base:** template n8n #12533 (155 nodes) — vamos a usar ~10% del esqueleto y reemplazar el resto.

---

## Estrategia: 2 fases de implementación

| Fase | Nodes | Goal | Bloqueante para siguiente |
|---|---:|---|---|
| **Fase 0 — smoke test** | ~12 | Validar que la cadena Claude (scoring + editorial) llega a Telegram con un brief decente | Aprobación de Manuel del brief en Telegram |
| **Fase 1 — pipeline completo** | ~75-90 | 11 agents end-to-end con publish automático | Decisión publisher (ADR-004) + Supabase schema + Telegram callback HITL |

**Por qué dos fases:** ir directo a Fase 1 con un JSON de 90 nodes nuevos es alto riesgo. Fase 0 valida que el corazón del pipeline (LLM scoring + LLM editorial + delivery a Telegram) funciona en condiciones reales antes de invertir en image gen, compliance, publishing.

---

## Fase 0 — Smoke test (target inmediato)

### Objetivo

Probar end-to-end:
1. Una fuente RSS (OpenAI Blog) entrega items reales
2. Claude Sonnet scorea con la rúbrica de 8 categorías
3. Un item con score >= 50 dispara el editorial
4. Claude Opus 4 genera un brief Smart Brevity con ángulo LATAM
5. El brief llega a Manuel por Telegram en menos de 2 minutos

Si esto funciona, sabemos que:
- ✅ El node Anthropic nativo de n8n funciona con nuestras API keys
- ✅ Los prompts (a2-signal-scorer.md, a3-editorial.md) producen output usable
- ✅ Telegram bot está bien configurado
- ✅ El JSON parsing entre nodes no se rompe en producción

Si NO funciona, sabemos exactamente en qué node se rompe (no entre 90 nodes).

### Arquitectura Fase 0 (Mermaid)

```mermaid
flowchart LR
    A[Manual Trigger] --> B[RSS Read<br/>OpenAI Blog]
    B --> C[Limit<br/>3 items]
    C --> D[Set<br/>Normalize]
    D --> E[Chain LLM<br/>A2 Signal Scorer<br/>Claude Sonnet 4.5]
    E --> F[Code<br/>Compute total_score]
    F --> G{If score >= 50}
    G -->|Yes| H[Chain LLM<br/>A3 Editorial<br/>Claude Opus 4]
    G -->|No| Z[End / Log]
    H --> I[Set<br/>Format Telegram MD]
    I --> J[Telegram<br/>Send Message]
```

### Node-by-node spec

> Convenciones: cada bloque incluye el `type` exacto (para el JSON), parámetros mínimos, y el nodo del que recibe input.

#### 1. Manual Trigger
- **type:** `n8n-nodes-base.manualTrigger`
- **Parámetros:** ninguno (clic en "Execute Workflow" para correr)
- **Entrada:** ninguna
- **Salida:** trigger event
- **Razón:** evita complicar el smoke test con cron. Schedule Trigger se agrega en Fase 1.

#### 2. RSS Feed Read
- **type:** `n8n-nodes-base.rssFeedRead`
- **Parámetros:**
  - `url`: `https://openai.com/blog/rss.xml`
  - `options.ignoreSSL`: false
- **Entrada:** Manual Trigger
- **Salida:** array de items RSS con campos estándar (`title`, `link`, `pubDate`, `content`, `contentSnippet`)
- **Razón:** OpenAI Blog es una fuente confiable con feed RSS estable. Postergamos las 11 fuentes restantes a Fase 1.

#### 3. Limit
- **type:** `n8n-nodes-base.limit`
- **Parámetros:**
  - `maxItems`: 3
- **Entrada:** RSS Feed Read
- **Salida:** primeros 3 items
- **Razón:** no quemar tokens scoreando 20 items en una prueba.

#### 4. Set — Normalize Item
- **type:** `n8n-nodes-base.set`
- **Parámetros (mode = "raw" JSON):**
  ```json
  {
    "title": "={{ $json.title }}",
    "url": "={{ $json.link }}",
    "snippet": "={{ $json.contentSnippet || $json.content || '' }}",
    "source_name": "OpenAI Blog",
    "published_at": "={{ $json.pubDate }}",
    "tags": []
  }
  ```
- **Entrada:** Limit
- **Salida:** items normalizados al formato que el scorer espera
- **Razón:** los nombres de campos de RSS varían por feed; normalizamos acá para que el scorer reciba siempre la misma estructura.

#### 5. Chain LLM — A2 Signal Scorer
- **type:** `@n8n/n8n-nodes-langchain.chainLlm`
- **Parámetros:**
  - `promptType`: "define"
  - `text`: contenido de `projects/ai-brief-latam/prompts/a2-signal-scorer.md` → sección "User message template"
  - `hasOutputParser`: true
- **Sub-nodes (conectados como inputs):**
  - **Anthropic Chat Model** (`@n8n/n8n-nodes-langchain.lmChatAnthropic`)
    - Model: `claude-sonnet-4-5-20250929` (último Sonnet 4.5)
    - Temperature: 0.2
    - Max Tokens: 500
    - Credenciales: Anthropic API key (Manuel pega)
    - **System Message:** el system prompt completo de `a2-signal-scorer.md`
  - **Structured Output Parser** (`@n8n/n8n-nodes-langchain.outputParserStructured`)
    - Schema (JSON): el schema definido al final de `a2-signal-scorer.md`
- **Entrada:** Set (Normalize Item)
- **Salida:** JSON con `relevancia_latam`, `novedad`, …, `justification`, `suggested_angle`, `risk_flags`
- **Razón:** Sonnet es 5× más barato que Opus para scoring batch. La rúbrica está bien definida, no requiere "creatividad" de Opus.

#### 6. Code — Compute total_score
- **type:** `n8n-nodes-base.code`
- **Lenguaje:** JavaScript
- **Código:**
  ```javascript
  const data = $input.item.json;
  const score = (data.relevancia_latam || 0) +
                (data.novedad || 0) +
                (data.urgencia || 0) +
                (data.credibilidad_fuente || 0) +
                (data.potencial_educativo || 0) +
                (data.potencial_viral || 0) +
                (data.fit_marca || 0) +
                (data.riesgo || 0);

  let classification = 'discard';
  if (score >= 70) classification = 'strong';
  else if (score >= 50) classification = 'consider';

  return {
    ...data,
    total_score: Math.round(score * 100) / 100,
    classification,
  };
  ```
- **Entrada:** Chain LLM (A2)
- **Salida:** mismo item con `total_score` y `classification` agregados
- **Razón:** sumar 8 campos en una expresión n8n inline es feo. Code node lo aísla.

#### 7. If — Score Threshold
- **type:** `n8n-nodes-base.if`
- **Condición:**
  - `{{ $json.total_score }}` `>=` `50`
- **Entrada:** Code (Compute total_score)
- **Salida true:** → Chain LLM (A3)
- **Salida false:** → ¿qué? Para Fase 0, conectar a un Set de log o dejar suelto.
- **Razón:** threshold 50 (no 70) en Fase 0 para garantizar que algo pase. En Fase 1 subimos a 65-70.

#### 8. Chain LLM — A3 Editorial
- **type:** `@n8n/n8n-nodes-langchain.chainLlm`
- **Parámetros:**
  - `promptType`: "define"
  - `text`: contenido de `projects/ai-brief-latam/prompts/a3-editorial.md` → sección "User message template"
  - `hasOutputParser`: true
- **Sub-nodes:**
  - **Anthropic Chat Model**
    - Model: `claude-opus-4-20250514` (Opus 4)
    - Temperature: 0.4
    - Max Tokens: 1500
    - **System Message:** el system prompt completo de `a3-editorial.md`
  - **Structured Output Parser** con el schema del brief
- **Entrada:** If (true branch)
- **Salida:** JSON con todos los campos del brief: `title`, `que_paso`, `por_que_importa`, `angulo_latam`, `hook_tentativo`, etc.
- **Razón:** Opus 4 acá vale los $20-30/mes extra por la calidad del hook.

#### 9. Set — Format Telegram MD
- **type:** `n8n-nodes-base.set`
- **Parámetros (mode = "raw"):**
  ```json
  {
    "telegram_text": "*🟢 AI Brief LATAM — preview*\n\n*{{ $json.title }}*\nScore: {{ $('Code').item.json.total_score }}/100\n\n*¿Qué pasó?*\n{{ $json.que_paso }}\n\n*¿Por qué importa?*\n{{ $json.por_que_importa }}\n\n*Ángulo LATAM:*\n{{ $json.angulo_latam }}\n\n*Hook tentativo:*\n_{{ $json.hook_tentativo }}_\n\n*Datos clave:*\n• {{ $json.datos_clave.join('\\n• ') }}\n\n*Formato recomendado:* {{ $json.formato_recomendado }}\n*CTA:* {{ $json.cta_tentativo }}\n\n*Fuente:* {{ $('Set').item.json.url }}"
  }
  ```
- **Entrada:** Chain LLM (A3)
- **Salida:** `{telegram_text: "...markdown..."}`
- **Razón:** Telegram MarkdownV2 tiene escape rules raras, usamos Markdown clásico (`parse_mode: "Markdown"`) que es más permisivo.

#### 10. Telegram — Send Message
- **type:** `n8n-nodes-base.telegram`
- **Parámetros:**
  - `operation`: "sendMessage"
  - `chatId`: `{{ $credentials.chat_id }}` o hardcoded (mejor en credentials)
  - `text`: `={{ $json.telegram_text }}`
  - `additionalFields.parseMode`: "Markdown"
- **Credenciales:** Telegram API (con bot token de `@BotFather`)
- **Entrada:** Set (Format Telegram MD)
- **Salida:** confirmación de envío
- **Razón:** node Telegram oficial de n8n maneja retries y rate limits automáticamente.

### Lo que del template #12533 NO usamos en Fase 0

- Los 13 Schedule Trigger nodes (usamos 1 Manual Trigger)
- Los 6 RSS Feed Read Trigger originales (usamos 1, nuestra fuente)
- Los 11 Slack nodes (swap a 1 Telegram)
- Los 3 Reddit nodes (postergamos Reddit a Fase 1)
- Los 12 HTTP Request nodes (Anthropic via node nativo, no HTTP)
- Los 2 Google Sheets nodes (postergamos dedup a Fase 1)
- Las 16 sticky notes del autor original (las nuestras se agregan después)
- Los 9 chainLlm con prompts genéricos (reemplazamos con nuestros 2 prompts)

**Total: borramos ~143 de 155 nodes. Conservamos esencialmente el patrón "RSS → normalize → LLM → branch → LLM → output" pero con nuestros prompts y target.**

### Credenciales requeridas en n8n cloud

| Credencial | Valor | Cómo obtenerla |
|---|---|---|
| `Anthropic API` | sk-ant-… | https://console.anthropic.com/settings/keys |
| `Telegram` | bot token | Hablar con `@BotFather` en Telegram → `/newbot` → seguir prompts |
| `chat_id` (no es credencial, va hardcoded) | tu user ID | Escribirle al bot, después `curl "https://api.telegram.org/bot<TOKEN>/getUpdates"` para ver tu `chat.id` |

---

## Fase 1 — Pipeline completo (referencia, NO implementar todavía)

Solo se construye cuando Fase 0 entregue ≥3 briefs decentes en Telegram (≥1 al día durante 3 días).

### Arquitectura Fase 1 (alto nivel)

```mermaid
flowchart TD
    A[Schedule Trigger<br/>7 AM CDMX] --> B[A1 Source Monitor<br/>12 fuentes RSS + scrape]
    B --> C[Dedup contra Supabase<br/>historial 30d]
    C --> D[Heuristic pre-score<br/>Code node]
    D --> E[A2 Signal Scorer<br/>Sonnet 4.5 batch]
    E --> F[Top 1-3 items<br/>Sort + Limit]
    F --> G[A3 Editorial<br/>Opus 4]
    G --> H[A4 Fact-Checker<br/>Opus 4 + web_search Tool]
    H --> I{Fact-check verdict}
    I -->|PASS| J[A7 Copy Composer<br/>Opus 4]
    I -->|FLAG| K[Auto-correct + retry]
    I -->|REJECT| Z1[Discard + log]
    K --> J
    J --> L[A8a Visual Generator<br/>gpt-image-2 x 5-7]
    L --> M[A9 Compliance<br/>Opus 4]
    M --> N{Compliance verdict}
    N -->|PASS| O[Telegram preview<br/>texto + imágenes]
    N -->|FLAG| O
    N -->|REJECT| Z2[Discard + log]
    O --> P{Manuel approves<br/>en Telegram}
    P -->|Approve| Q[A10 Publisher<br/>Blotato/Upload-Post/Buffer TBD]
    P -->|Edit| R[Manual edit loop]
    P -->|Reject| Z3[Discard]
    Q --> S[Log to Supabase<br/>analytics + cost]
```

### Nodes nuevos respecto a Fase 0

| Bloque | Nodes nuevos | Razón |
|---|---:|---|
| Schedule Trigger + 12 RSS + dedup | ~25 | Reemplaza Manual Trigger + 1 RSS |
| Heuristic pre-score | 1 (Code) | Filtro barato antes de LLM |
| Top-N selector | 2 (Sort + Limit) | Reemplaza el If simple |
| A4 Fact-Checker | ~5 (Chain LLM + web_search Tool + parser + retry) | Patrón del template #4399 |
| A7 Copy Composer | ~3 (Chain LLM + parser) | Caption + hashtags |
| A8a Visual Generator | ~7-10 (HTTP Request × 5-7 imágenes + merge) | gpt-image-2 API loop |
| A9 Compliance | ~3 | Chain LLM + parser |
| Telegram HITL callback | ~5 | Wait for callback + parse approval |
| A10 Publisher | ~3-5 | Depende de Blotato vs Upload-Post vs Buffer |
| Logging Supabase | ~3 | Persistencia para analytics |

**Total estimado Fase 1: 75-90 nodes.**

### Open items para Fase 1 (no bloqueantes para Fase 0)

1. **ADR-004 — publisher**: Blotato vs Upload-Post vs Buffer. Decidir antes de A10.
2. **Schema Supabase**: tablas `dedup_history`, `briefs`, `costs`. A diseñar.
3. **Telegram callback HITL**: el patrón "approve / edit / reject" desde Telegram requiere webhook listener. Inspirado en template #9472 o #5773.
4. **Threshold de scoring**: en Fase 0 usamos 50. Subir a 65-70 una vez que tengamos data real de scores.
5. **Cost monitoring**: Opus 4 a $15/$75 per M tokens. A 3 piezas/día con ~5K input + 2K output → ~$3/día → $90/mes. Trackeable.

---

## Próximos pasos concretos

1. **Manuel:** crear Telegram bot vía `@BotFather`, mandar el token + tu chat_id por mensaje al chat.
2. **Yo (post recibir credenciales):** generar `12533-v2-fase0.json` con los 10 nodes de Fase 0. Commit + raw URL.
3. **Manuel:** importar v2 a n8n cloud (Import from URL como hicimos con v1), pegar credenciales Anthropic + Telegram.
4. **Manuel:** click "Execute Workflow" → esperar 30-60s → recibir brief en Telegram.
5. **Juntos:** evaluar calidad del brief. Si gusta, agendar Fase 1. Si no, iterar prompts.
