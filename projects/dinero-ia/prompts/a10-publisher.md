# A10 — Publisher (Node spec, no LLM prompt)

**Agent:** A10 (Publisher)
**Fuente:** ADR-014 (Upload-Post como publisher primario, 2026-05-12)
**Última actualización:** 2026-05-12
**Status:** Spec listo para Fase 1. NO requiere implementación hasta Fase 0 estable.

---

> **Diferencia con otros agents:** A10 NO usa Claude. Es un publisher mecánico: toma el bundle aprobado (carousel + caption + hashtags + videos + audios) y lo posta a las plataformas via Upload-Post API.
>
> **Por qué este archivo entonces:** documentar la config del node n8n + el handshake con Upload-Post + manejo de errores. Equivalente a los prompts pero para integración mecánica.

---

## Pre-requisitos

| Pre-requisito | Status | Cómo conseguir |
|---|---|---|
| Cuenta Upload-Post | ⏳ Pendiente | https://upload-post.com (Manuel crea cuando ADR-014 confirmado) |
| API key Upload-Post | Pendiente cuenta | Settings → API Keys después de crear cuenta |
| Connected social accounts en Upload-Post (IG + TikTok) | Pendiente cuenta | Settings → Social Accounts → OAuth con cada plataforma |
| Community node `n8n-nodes-upload-post` instalado en n8n self-hosted | Pendiente VPS | `npm install n8n-nodes-upload-post` en el VPS, o via Settings → Community Nodes |
| Upload-Post credential en n8n configurada | Pendiente node | Add Credential → Upload-Post API → paste key |

**Bloquea Fase 1.** No bloquea Fase 0 (que no publica).

---

## Node config — Upload-Post Photo (carousel IG + TikTok)

```yaml
node_type: n8n-nodes-upload-post.uploadPost
operation: uploadPhotos
parameters:
  user: "manuel-aibrieflatam"   # el "user" de Upload-Post creado para AI Brief LATAM
  platforms:
    - instagram
    - tiktok
  photos:                        # array de URLs o binarios
    - "={{ $('A8a Visual Generator').item.json.slide_1_url }}"
    - "={{ $('A8a Visual Generator').item.json.slide_2_url }}"
    - "={{ $('A8a Visual Generator').item.json.slide_3_url }}"
    - "={{ $('A8a Visual Generator').item.json.slide_4_url }}"
    - "={{ $('A8a Visual Generator').item.json.slide_5_url }}"
  title: "={{ $('A7 Copy Composer').item.json.carousel.caption.hook }}"
  description: |
    ={{ $('A7 Copy Composer').item.json.carousel.caption.body }}

    {{ $('A7 Copy Composer').item.json.carousel.caption.cta }}

    {{ $('A7 Copy Composer').item.json.carousel.caption.hashtags.join(' ') }}
  platform_overrides:
    instagram:
      description: "={{ $('A7 Copy Composer').item.json.carousel.caption.body }}\n\n{{ $('A7 Copy Composer').item.json.carousel.caption.cta }}\n\n{{ $('A7 Copy Composer').item.json.carousel.caption.hashtags.slice(0, 30).join(' ') }}"
    tiktok:
      description: "={{ $('A7 Copy Composer').item.json.tiktok.caption }}\n\n{{ $('A7 Copy Composer').item.json.tiktok.hashtags.slice(0, 5).join(' ') }}"
  schedule_time: null            # null = post inmediato; ISO string para schedule
credentials:
  uploadPostApi: "Upload-Post AI Brief LATAM"
```

### Notas de la config

- **`user`:** Upload-Post tiene concepto de "user" para multi-tenant. Usamos un solo user "manuel-aibrieflatam" para AI How-To LATAM (multi-property diferido por ADR-016).
- **`platforms`:** lista de plataformas target. IG + TikTok en Fase 1. LinkedIn agregable después.
- **`platform_overrides`:** TikTok permite captions más largos (2200 chars vs 2200 IG pero TikTok ignora hashtags después de #30). Override hace que TikTok use sus propios captions y hashtags optimizados (output de A7 ya genera ambos en `carousel.caption` y `tiktok.caption`).
- **`schedule_time: null`:** post inmediato. En Fase 1 Manuel aprueba en Telegram → publish inmediato. En Fase 1.5 podemos schedule a la hora óptima del día (8 AM CDMX según research).

## Node config — Upload-Post Video (reel, Fase 2)

```yaml
node_type: n8n-nodes-upload-post.uploadPost
operation: uploadVideo
parameters:
  user: "manuel-aibrieflatam"
  platforms:
    - instagram
    - tiktok
  video_url: "={{ $('A8b Seedance Video').item.json.video_url }}"
  thumbnail_url: "={{ $('A8a Visual Generator').item.json.cover_url }}"
  audio_url: "={{ $('A8c ElevenLabs Audio').item.json.audio_url }}"   # si separado del video
  title: "={{ $('A7 Copy Composer').item.json.reel_script.hook }}"
  description: |
    ={{ $('A7 Copy Composer').item.json.reel_script.por_que_importa }}

    {{ $('A7 Copy Composer').item.json.reel_script.cta }}

    {{ $('A7 Copy Composer').item.json.carousel.caption.hashtags.slice(0, 8).join(' ') }}
```

## Manejo de errores

Errores comunes y su solución:

| Error | Causa | Solución |
|---|---|---|
| `401 Unauthorized` | API key vencida o mal copiada | Regenerar en Upload-Post dashboard, actualizar credential en n8n |
| `429 Rate Limit` | Demasiados requests/min | Upload-Post default: 60 req/min. n8n retry automático con 5s wait |
| `Platform-specific OAuth error` | Token de IG o TikTok venció | Re-link en Upload-Post Settings → Social Accounts |
| `Image format unsupported` | gpt-image-2 entregó PNG con transparencia (IG rechaza) | A8a debe forzar JPG sin alpha; conversión automática en Code node antes de A10 |
| `Carousel slot count exceeded` | Más de 20 imágenes (IG max) o 35 (TikTok max) | A7/A8a generan max 7 — error no debería ocurrir |
| `Caption too long` | IG max 2,200 chars; A7 raramente excede pero posible | Truncar en Code node antes de A10, agregar "..." al final |

## Retry strategy

```yaml
retryOnFail: true
maxTries: 3
waitBetweenTries: 30000   # 30 segundos entre retries
continueOnFail: false      # si todos los retries fallan, frenar workflow y alertar a Telegram
```

## Post-publish: log a Supabase

Después de un publish exitoso, log a la tabla `posts_published`:

```javascript
// Code node post-A10
const a10Result = $input.item.json;

return {
  brief_id: $('Get Brief ID').item.json.brief_id,
  platform: 'instagram',  // bucle para cada platform
  post_url: a10Result.instagram_post_url,
  external_id: a10Result.instagram_media_id,
  content_type: 'carousel',
  publisher_used: 'upload-post',
  publisher_response: a10Result,  // raw response para debug
  published_at: new Date().toISOString()
};
```

(Insert via Supabase node con la tabla `posts_published`.)

## Métricas — fetched async (no en este workflow)

Las métricas (likes, comments, shares, reach) NO se fetcheaan en A10. Eso lo hace un cron separado **24h después** del post, llamando a Upload-Post API endpoint de métricas. Esto se documenta en un workflow aparte: `analytics-collector.json` (Fase 1.5).

## Plataformas adicionales (Fase 1.5+)

Upload-Post soporta de forma nativa:

| Plataforma | Status AI Brief | Activar cuándo? |
|---|---|---|
| Instagram | ✅ Fase 1 | Día 1 |
| TikTok | ✅ Fase 1 | Día 1 |
| LinkedIn | ⏳ Fase 1.5 | Cuando el contenido valga para LinkedIn (Startupeable pattern) |
| YouTube Shorts | ⏳ Fase 2 | Cuando haya reels (~Semana 4) |
| Threads | ⏳ Fase 1.5 | Si decidimos cross-postear |
| Twitter/X | ❓ Evaluación | Threads gratis vs API X de pago |
| Facebook | ❌ No | Audiencia no coincide |
| Pinterest | ❌ No | Audiencia no coincide |
| Reddit | ⚠️ Manual | Subreddits tienen reglas anti-self-promo, manejar manual |
| Bluesky | ⏳ TBD | Si la audiencia migra |

## Backup path: Buffer manual

Si Upload-Post tiene un outage o problema:

1. Manuel recibe alerta en Telegram (error del retry)
2. Manuel exporta el bundle desde Supabase: caption + slides URLs
3. Manuel publica manual via Buffer (cuenta backup activa con $15/mo, $0 si no se usa)

Esta degradación es **automática** — el workflow detecta el fallo y manda Manuel un mensaje con el bundle ready para copy-paste. Tiempo de recovery: ~5 min vs publish automático ~30s.

## Plan B: Blotato

Si Upload-Post resulta inestable después de 2 semanas de Fase 1:

1. Swap el node a `n8n-nodes-blotato` (también community node).
2. La estructura de parámetros es similar — re-mapping de fields ~30 min de trabajo.
3. Costo cambia: $14/mo a $29/mo.

Decisión de swap: si Upload-Post tiene >2 fallos críticos en 14 días, switch a Blotato.
