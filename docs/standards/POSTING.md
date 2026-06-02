# Posting Standard — Dinero IA

**Versión:** 1.0
**Fecha:** 2026-06-01
**Base:** ADR-019 (cadencia 2-3 posts/día + slots LATAM) + research benchmark
**Aplica a:** A10 Publisher (ContentStudio + Beehiiv + TikTok), cron triggers n8n

> Filosofía locked: "mejor 0 posts que 3 mediocres". A2 Scorer umbral 65 minimum. Anti-canibalización obligatoria.

---

## 1. Cadencia objetivo

| Cadencia | Cuándo | Aplica |
|---|---|---|
| **2 posts/día** | Default Pre-Fase 1.0 + Fase 1.0 | Slot mañana + slot mediodía |
| **3 posts/día** | Fase 1.1+ cuando voice clone Manuel activa + producción estable 14 días | Slot mañana + slot mediodía + slot tarde |
| **1 post/día** | Días con compliance bloqueo de 1+ items | Mejor que publicar mediocre |
| **0 posts/día** | Si A2 Scorer no entrega items >65 en los 3 slots | Mejor que mediocre |

**Filosofía:** la cadencia objetivo NO es producción obligatoria — es techo. Si el sistema no tiene material de calidad >65 score + compliance pass para los 3 slots, se publica menos. Sin excepciones.

---

## 2. Slots horarios LATAM (locked)

### Slot 1 — Mañana (commute / pre-trabajo)

| País | Hora local | UTC | Por qué este horario |
|---|---|---|---|
| México (CDMX) | 7:00 AM CST | 13:00 UTC | Commute matutino, café, scroll antes del trabajo |
| Argentina (Buenos Aires) | 9:00 AM ART | 12:00 UTC | Inicio jornada profesional |
| Colombia (Bogotá) | 7:00 AM COT | 12:00 UTC | Commute matutino |
| Chile (Santiago) | 9:00 AM CLT | 12:00 UTC | Inicio jornada |
| Perú (Lima) | 7:00 AM PET | 12:00 UTC | Commute matutino |

**Trigger n8n cron:** `0 12 * * *` (12:00 UTC = 7:00 AM CDMX)
**Sub_categorías sugeridas:** inversiones, comparativas, retiro (lo analítico/educativo de la jornada)

### Slot 2 — Mediodía (almuerzo / break)

| País | Hora local | UTC |
|---|---|---|
| México | 12:30 PM CST | 18:30 UTC |
| Argentina | 2:30 PM ART | 17:30 UTC |
| Colombia | 12:30 PM COT | 17:30 UTC |
| Chile | 2:30 PM CLT | 17:30 UTC |
| Perú | 12:30 PM PET | 17:30 UTC |

**Trigger n8n cron:** `30 17 * * *` (17:30 UTC) — toma audiencia mediodía AR/CL primero, propaga.

⚠️ **Compromise importante:** los husos horarios LATAM no se alinean. Vamos a sacrificar 1.5h en MX/CO/PE para optimizar AR/CL (mediodía es más estable). Si el sistema crece, podemos crear slot 2-MX dedicado (`30 18 * * *` = 18:30 UTC = 12:30 MX).

**Sub_categorías sugeridas:** presupuesto, prompts accionables, herramientas IA (lo práctico)

### Slot 3 — Tarde-noche (solo si 3/día)

| País | Hora local | UTC |
|---|---|---|
| México | 7:00 PM CST | 01:00 UTC (next day) |
| Argentina | 9:00 PM ART | 00:00 UTC (next day) |
| Colombia | 7:00 PM COT | 00:00 UTC (next day) |
| Chile | 9:00 PM CLT | 00:00 UTC (next day) |
| Perú | 7:00 PM PET | 00:00 UTC (next day) |

**Trigger n8n cron:** `0 0 * * *` (00:00 UTC del día siguiente).

**Sub_categorías sugeridas:** tendencia + viral: noticias IA, inflación AR/MX, polémicas, comparativas controversiales (cuando audiencia tiene tiempo de comments)

### Excepciones por día de semana

| Día | Variación |
|---|---|
| Lunes | Sumar 30 min a todos los slots (gente arranca semana más tarde) |
| Viernes | Slot 3 se mueve a 6:00 PM CDMX / 8:00 PM AR (gente sale antes) |
| Sábado | Solo Slot 1 + Slot 2. NO Slot 3 (audiencia desconectada noche sábado). |
| Domingo | Solo 1 post (Slot 2 - mediodía). Reflexivo/educativo retrospectivo. |

---

## 3. Anti-canibalización — reglas duras

A10 Publisher valida ANTES de publicar:

### Regla 1 — Diversidad de sub_categoria

```sql
-- Los posts del mismo día NO pueden ser de la misma sub_categoria
SELECT COUNT(*) FROM posts_published
WHERE DATE(published_at) = TODAY
  AND sub_categoria = '{new_post.sub_categoria}';
-- Si > 0, postergar el nuevo post al día siguiente
```

### Regla 2 — Diversidad de source_name

```sql
-- Los posts del mismo día NO pueden ser de la misma source
SELECT COUNT(*) FROM posts_published
WHERE DATE(published_at) = TODAY
  AND source_name = '{new_post.source_name}';
-- Si > 0, postergar
```

### Regla 3 — Diversidad de format

| Día con 2 posts | Format mix recomendado |
|---|---|
| Mañana + Mediodía | 1 reel + 1 reel (preferido) o 1 reel + 1 carousel |
| Mañana + Tarde | 2 reels OK si sub_categorias son muy distintas |

| Día con 3 posts | Format mix recomendado |
|---|---|
| Default | 2 reels + 1 carousel intercalado (carousel en mediodía típicamente) |
| Si todas reels | OK pero diversificar mood música + paleta dentro de tolerancia §VISUAL.md |

### Regla 4 — Topical dedup

A1.5 Binary Filter del workflow incluye check de keyword extraction:

```javascript
// Pseudo-code keyword extraction
const recent_topics = await db.query(`
  SELECT topic_keywords FROM briefs_pending
  WHERE published_at > NOW() - INTERVAL '7 days'
    AND approval_status IN ('approved', 'published')
`);

const new_keywords = extractKeywords(new_brief.que_paso);  // e.g. ["openai", "gpt-5", "lanzamiento"]

const overlap = new_keywords.filter(k => recent_topics.flatMap(t => t).includes(k));
if (overlap.length >= 2) {
  return { keep: false, reason: 'topical_overlap', overlap };
}
```

**Tolerancia:** max 2 keywords compartidos con últimos 7 días. Si comparte 3+, descartar (es el mismo evento desde otro ángulo).

---

## 4. Format selection — A10 Publisher decision tree

```
Input: brief approved + format_recomendado del A3 (reel | carrusel | post estatico | newsletter)

DECISION TREE:

1. ¿format_recomendado == "reel"?
   YES → publish: IG Reel + TikTok + LinkedIn (carousel adaptado a video) + Newsletter section
   NO  → continúa

2. ¿format_recomendado == "carrusel"?
   YES → publish: IG carousel + LinkedIn (PDF) + Newsletter section
   NO TikTok (TikTok no acepta carrusel bien)

3. ¿format_recomendado == "post estatico"?
   YES → publish: IG single image + LinkedIn + Newsletter section
   NO TikTok (no es video)

4. ¿format_recomendado == "newsletter"?
   YES → solo Beehiiv newsletter, no social

DEFAULT en pre-Fase 1.0: forzar reel siempre (queremos volumen video)
```

**Excepción Pre-Fase 1.0:** sub_categoria == "comparativas" con muchas variables → permitir carousel ocasional (mejor para multiple options shown)

---

## 5. Plataformas — orden de prioridad

| Plataforma | Prioridad | Por qué |
|---|---|---|
| **Instagram Reels** | 1 | Mejor algoritmo LATAM 2026 para video corto, audiencia más diversa |
| **TikTok** | 2 | Crecimiento orgánico más rápido pero audiencia más volátil |
| **LinkedIn** | 3 | Audiencia B2B finanzas, mejor para piezas analíticas con cifras |
| **Beehiiv newsletter** | obligatorio diario | Activo más durable, 1 envío consolidado por día con 1-3 piezas |
| **YouTube Shorts** | 4 (Fase 1.5) | Activar cuando Fase 1.0 tenga >100 reels producidos |
| **X / Threads** | Fase 2+ | Bajo ROI para este nicho |

### Configuración por plataforma

**Instagram:**
- Caption: max 2,200 chars (sweet spot 150-300 chars + hashtags)
- Hashtags: 5-10 nicho-específicos (no 30 broad)
- Cover frame: K1 hook del reel
- Audio: original sound (no Instagram music library — restringe alcance comercial)
- Music attribution si aplica: en caption última línea

**TikTok:**
- Caption: max 150 chars (más corto que IG, hook + 3-5 hashtags)
- Audio: original sound siempre (más reach que TikTok library)
- Cover: K1 hook
- AIGC label: SIEMPRE marcado (voice clone obligatorio)

**LinkedIn:**
- Caption: 1300-1500 chars optimal (longer-form sirve)
- PDF carousel: hasta 20 slides
- Audio: si reel, suelen verse mute → subs OBLIGATORIOS

**Beehiiv:**
- Subject line: emocional + cifra (A3 genera 5 alternates, A7 elige top 1)
- Pre-header: complementario
- Body: consolida los 2-3 posts del día en 1 email
- Footer: disclaimer financiero estandarizado fijo

---

## 6. Hashtags — estrategia

### Categorías de hashtags

| Tipo | Función | Volumen sugerido por post |
|---|---|---|
| **Brand** | Identificación marca | 1 (`#DineroIA`) |
| **Nicho amplio** | Discovery por interés | 2-3 (`#FinanzasPersonales`, `#IAparaTodos`, `#FinanzasLATAM`) |
| **Sub_categoria** | Discovery específico | 2-3 (`#Inversiones`, `#CEDEARs`, `#PresupuestoFamiliar`, etc.) |
| **País específico** | Discovery regional | 1-2 (`#FinanzasArgentina`, `#FinanzasMexico` — alternar) |
| **Trending IA** | Discovery tech moment | 1-2 (`#ChatGPT`, `#ClaudeAI`, `#PromptEngineering`) |

**Total por post:** 7-10 hashtags. **NUNCA 30+ broad** (penaliza alcance LATAM 2026).

### Anti-hashtags

NO usar:
- ❌ `#FYP`, `#viral`, `#trending` (penalizan en IG 2026)
- ❌ `#money`, `#rich`, `#wealth` (cae a finfluencer hype)
- ❌ `#investment`, `#stocks` (saturadísimos US)
- ❌ Más de 1 brand-hashtag por post
- ❌ Hashtags peninsular si target es LATAM (`#bolsa` ok, `#chollo` no)

---

## 7. Timing operativo — flujo n8n

```
T-0 (cron Slot 1 trigger): 12:00 UTC
  ↓
T+0 a T+8min:
  - Workflow Fase 1 publish-v2 corre
  - RSS read + dedup + scoring + brief + fact-check + compliance
  - Si pasa todo → Save brief Supabase + Telegram preview con HITL

T+8min a T+1h:
  - Manuel revisa Telegram (HITL)
  - Aprueba / edita / regenera / rechaza
  - Si aprueba → trigger fanout

T+1h a T+1.5h (post-aprobación):
  - A5/A6/A7 corren (script + visual + audio direction)
  - A8a Image gen (gpt-image-2, 5-8 keyframes × 5s = 25-40s)
  - A8b Video gen Seedance (anima keyframes, 60-120s)
  - A8c Voice ElevenLabs (genera audio, 5-10s)
  - A8d Music selection (instant, lookup local library)
  - A8e Compositor FFmpeg (mix final, 30-60s)
  - Upload final MP4 + caption a ContentStudio queue
  - Beehiiv post draft

T+1.5h a T+2h:
  - ContentStudio publica al horario programado (si dentro del slot horario actual o siguiente disponible)
  - Beehiiv envía newsletter a las 9 AM CDMX (cron beehiiv aparte)
  - Posts_published actualizado en Supabase
  - Notify Telegram fanout success

Si Manuel no responde en 4h:
  - Telegram reminder
Si Manuel no responde en 8h:
  - Auto-postpone al día siguiente (NO auto-reject)
  - Brief queda pending en Supabase
```

---

## 8. Métricas mínimas por post — A11.5 Analytics

A11.5 (cron analytics 11pm) consulta cada plataforma y popula `posts_published.metrics`:

| Métrica | Plataforma | Target Pre-Fase 1.0 | Target Fase 1.1 estable |
|---|---|---|---|
| Reach | IG | >2,000 | >5,000 |
| Saves | IG | >40 (2% reach) | >100 (2% reach) |
| Comments substantive (>10 chars) | IG | >2 | >5 |
| Shares | IG | >10 | >30 |
| Engagement rate | IG | >2.5% | >3% |
| Watch through 100% | IG/TT | >35% | >45% |
| Views | TikTok | >5,000 | >15,000 |
| FYP impressions | TikTok | >70% | >80% |
| Impressions | LinkedIn | >800 | >2,000 |
| Newsletter open rate | Beehiiv | >35% | >40% |
| Newsletter click rate | Beehiiv | >5% | >8% |

**Si una métrica está RED 3 días seguidos:** alerta Telegram Manuel + recomendación (cambiar hook? cambiar slot? cambiar formato?).

---

## 9. Plan de escalado de cadencia

| Stage | Volumen | Criterio para avanzar |
|---|---|---|
| Pre-Fase 1.0 | 0/día (testing interno) | Workflow video funciona end-to-end + 5 reels test aprobados Manuel |
| Fase 1.0 | 1-2/día | 7 días estables sin compliance violation + engagement >2% |
| Fase 1.1 — voice clone | 2/día estable | 14 días Fase 1.0 con métricas verde |
| Fase 1.2 — full cadence | 2-3/día (default 2, 3 si día tiene 3 items >70 score) | 30 días Fase 1.1 estable + voice clone Manuel activa |
| Fase 1.3 — repost system | 2-3 propios + 5-7 reposts a otras cuentas (modelo Riley Brown) | Solo si Fase 1.2 valida + Manuel decide expandir |

---

## 10. Compliance final pre-publish — A9 checklist

A9 Compliance valida ANTES del fanout:

- [ ] Sub_categoria diferente a posts mismo día
- [ ] Source_name diferente a posts mismo día
- [ ] Topical dedup pasa (max 2 keywords overlap últimos 7 días)
- [ ] Format coherente con sub_categoria y stage
- [ ] Plataformas target válidas según format
- [ ] Caption por plataforma dentro de límites
- [ ] Hashtags entre 7-10
- [ ] Brand hashtag presente
- [ ] AIGC label marcado para TikTok (voice clone activo)
- [ ] Disclaimer en caption si productos_mencionados.length > 0
- [ ] Subs incluidas en video (audio off compliance)
- [ ] Music license commercial verificada
