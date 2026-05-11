# Automation Architecture — AI Brief LATAM

**Fecha:** 2026-05-10
**Status:** Diseño. No implementado todavía.

---

## El problema actual

El pipeline existe como código Python (9 agents, 98 tests) pero requiere intervención manual en cada paso: correr comandos, buscar archivos, copiar captions, generar imágenes con Pillow (feas), subir a IG/TikTok manualmente. No es un sistema, es un script.

## El sistema target

Un flujo 100% automatizado donde:
1. Un trigger (cron o RSS) detecta noticias nuevas
2. El sistema evalúa, genera brief, contenido, imágenes profesionales
3. El contenido pasa compliance automáticamente
4. Se publica en IG + TikTok sin intervención
5. Manuel solo revisa resultados y ajusta estrategia

---

## Stack

| Componente | Herramienta | Rol | Costo |
|---|---|---|---|
| Orquestador | **n8n** (self-hosted en Hostinger VPS) | Conecta todo, triggers, workflows | ~$10-15/mo VPS |
| LLM - Scoring/Editorial | **Claude API** (Opus 4) | Evaluar noticias, generar briefs, fact-check, compliance | ~$1-3/day |
| LLM - Contenido | **ChatGPT API** (GPT-4o) | Generar captions, newsletter sections, reel scripts | Usage-based |
| Imágenes | **gpt-image-2** (OpenAI) | Generar slides de carousel profesionales | ~$0.02-0.08/imagen |
| Video | **Seedance 2.0** | Generar reels/videos desde imágenes | TBD |
| Templates | **Canva API** (requiere Pro) | Templates profesionales, brand consistency | $14.99/mo |
| Publishing IG | **Meta Graph API** o **Buffer API** | Publicar automáticamente a Instagram | Buffer paid ~$6/mo |
| Publishing TikTok | **TikTok Content Posting API** | Publicar automáticamente a TikTok | Gratis (requiere app review) |
| Newsletter | **Beehiiv API** | Publicar newsletter automáticamente | Free tier o $49/mo |
| Monitoring | **n8n** + webhooks | Notificaciones de errores, métricas | Incluido |

---

## Flujo completo en n8n

```
TRIGGER: Cron (cada 6h) o RSS trigger en n8n
    │
    ▼
[1] FETCH SOURCES
    n8n HTTP nodes → RSS feeds (12 fuentes)
    + n8n HTTP node → scrape Anthropic /news
    │
    ▼
[2] DEDUP + PRELIMINARY SCORE
    n8n Function node → lógica de dedup (contra storage)
    n8n Function node → scoring heurístico (keywords, recency)
    │
    ▼
[3] LLM SCORING (top 10 items)
    n8n HTTP node → Claude API (Opus 4)
    Prompt: Signal Scoring Rubric (8 categorías)
    Output: score 0-100 + clasificación + justificación
    │
    ▼
[4] LLM EDITORIAL BRIEF (top 3 items con score >70)
    n8n HTTP node → Claude API
    Prompt: Generar brief Smart Brevity + ángulo LATAM
    │
    ▼
[5] LLM CONTENT GENERATION
    n8n HTTP node → ChatGPT API (o Claude)
    Prompt: Generar caption + slides text + newsletter section
    │
    ▼
[6] IMAGE GENERATION (carousel slides)
    n8n HTTP node → gpt-image-2 API
    Input: slide text + brand guidelines
    Output: 7 imágenes 1080x1080 profesionales
    │
    ▼
[7] COMPLIANCE CHECK
    n8n HTTP node → Claude API
    Prompt: Checklist Meta + brand voice
    If blocked → notify Manuel, stop
    │
    ▼
[8] PUBLISH
    ├→ n8n HTTP node → Instagram Graph API (carousel post)
    ├→ n8n HTTP node → TikTok API (slideshow)
    └→ n8n HTTP node → Beehiiv API (newsletter draft)
    │
    ▼
[9] NOTIFY
    n8n node → Telegram/Email/Slack
    "Publicado: [título] en IG + TikTok. Review: [link]"
```

---

## Opción simplificada (si Meta/TikTok API son difíciles)

Los pasos 1-7 se automatizan en n8n. El paso 8 (publish) usa Buffer API en vez de publicar directo:

```
[8 ALT] SCHEDULE VIA BUFFER
    n8n HTTP node → Buffer API
    Sube imágenes + caption a Buffer
    Buffer publica en IG + TikTok según schedule
```

Buffer paid ($6/mo) evita el proceso de Meta App Review (semanas) y TikTok App Review.

---

## Setup requerido en Hostinger VPS

1. Instalar n8n (Docker o npm)
2. Configurar dominio/SSL para n8n UI (ej: n8n.aibrieflatam.com o IP directa)
3. Configurar credentials en n8n:
   - Anthropic API key
   - OpenAI API key
   - Buffer API key (o Meta Graph token)
   - Beehiiv API key
4. Importar workflows
5. Activar triggers

---

## Orden de implementación

### Fase A: n8n + RSS + LLM scoring (reemplaza `scan` + `score`)
- Instalar n8n en Hostinger
- Crear workflow: RSS trigger → fetch → dedup → Claude scoring
- Output: notificación con top 5 items rankeados
- **Esto solo ya reemplaza 2 comandos manuales**

### Fase B: Content generation (reemplaza `brief` + `compose`)
- Agregar nodos: Claude brief → ChatGPT content → gpt-image-2 imágenes
- Output: imágenes + caption listos

### Fase C: Auto-publish (reemplaza `publish`)
- Conectar Buffer API o Meta Graph API
- Auto-publicar en IG + TikTok
- Notificación a Manuel post-publicación

### Fase D: Newsletter + analytics
- Conectar Beehiiv API
- Weekly newsletter automático
- Dashboard de métricas

---

## Decisiones pendientes antes de arrancar

1. **Reactivar Hostinger VPS** — ¿mismo plan que tenías antes?
2. **Buffer paid vs Meta Graph API directo** — Buffer es más fácil ($6/mo), Meta es gratis pero requiere app review
3. **gpt-image-2 vs Canva API para imágenes** — gpt-image-2 es más creativo, Canva es más brand-consistent. Podemos probar gpt-image-2 primero (ya tenés API key)
4. **Seedance para video** — ¿prioridad ahora o después de que imágenes funcionen?
5. **Nivel de autonomía** — ¿publicar automáticamente sin approval, o notificar primero y publicar con un click?
