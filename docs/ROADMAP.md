# Roadmap — Dinero IA (v6, 2026-06-01)

> **Cambios v6 vs v5** (post smoke test 2026-06-01 + ADR-018/019):
> - **Fase -1 manual SKIPPED** (Manuel decidió no hacer 10 piezas manuales — feedback 2026-05-30)
> - **Fase 0 smoke test ✅ COMPLETADO** (moat editorial validado en n8n cloud)
> - **Fase 1 redefinida = video-first** (reels + voice + música desde día 1, ADR-018)
> - **Cadencia 2-3 posts/día** con anti-canibalización + slots horarios LATAM (ADR-019)
> - **Voice clone ACTIVA** desde día 1 con ElevenLabs voice library, swap a clone Manuel post-grabación
> - **Inflection Lever Track híbrido:** Claude escribe DMs personalizados, Manuel envía
>
> **Filosofía v6:** "máximo nivel + automatizado + sin prisa". Calidad > velocidad. No publicar hasta que el pipeline produzca videos a nivel de top performers US+LATAM.

---

## Estado actual (2026-06-01)

```
✅ DISEÑO          completo (5 Deep Research + brand voice + compliance + sources)
✅ Fase -1 manual  SKIPPED por decisión Manuel (no quiere operación manual prolongada)
✅ Fase 0 smoke    COMPLETADO (A2 + A3 + A9 + Telegram funciona en n8n cloud)
🔄 Pre-Fase 1     EN CURSO (research US+LATAM + standards + workflows video)
⬛ Fase 1.0       arranque producción (voice library + Seedance + música)
⬛ Fase 1.1       swap voice clone Manuel post-grabación
⬛ Fase 2-4       no diseñado todavía
```

---

## Pre-Fase 1 — Research + Standards + Build (Semanas 1-3, sin output público)

**Objetivo:** dejar el pipeline video-first armado, testeado y estandarizado ANTES de comprometer cuentas SaaS recurrentes. Manuel no publica nada todavía. Todo el trabajo es interno.

### Bloque A — Research benchmark Top performers (Semana 1, Claude)
- Agent paralelo: Top 12-15 creators US+LATAM en AI/Tech/Finance video
- Output: `projects/dinero-ia/research/2026-06-01_top-performers-benchmark.md`
- Insights cross-cutting: hook formulas top-5, duración óptima, color palettes, music styles, growth path

### Bloque B — Standards documentados (Semana 1-2, Claude)
- `docs/standards/VISUAL.md`: palette + fonts + transitions + composición keyframes Seedance
- `docs/standards/VOICE.md`: tone + pace + ElevenLabs voice_settings + SSML markers
- `docs/standards/MUSIC.md`: mood × sub_categoria + license-free sources + sync timing
- `docs/standards/POSTING.md`: horarios LATAM por país + cadencia + anti-canibalización

### Bloque C — Pipeline video workflows v2 (Semana 2-3, Claude)
- Workflow `infra/n8n/dinero-ia-fase1-publish-v2.json` con agents A5/A6/A7/A8a-e
- Migration SQL `infra/supabase/migrations/002_video_assets.sql` (tabla assets_storage)
- Cron triggers x3 (slots) en vez de manual trigger
- `topical_dedup` code node para anti-canibalización
- A2 Scorer umbral 65 (no 60)

### Bloque D — Voice clone setup (Semana 2-3, Manuel + Claude)
- `docs/voice-clone/recording-script.md` — script de 20-30 min para grabación
- Runbook ElevenLabs onboarding + voice library selection
- Runbook Seedance 2.0 onboarding + Supabase Storage bucket
- Manuel graba cuando puede (no bloqueante; arrancamos con voice library)

### Definition of Done Pre-Fase 1

- [ ] Research US+LATAM completo con 12-15 performers analizados
- [ ] 4 docs de standards publicados en `docs/standards/`
- [ ] Workflow video v2 importado a n8n cloud + smoke test exitoso (1 reel completo end-to-end)
- [ ] Manuel tiene cuentas activas: ElevenLabs + Seedance + Supabase + ContentStudio + Blotato + Beehiiv
- [ ] Voice library seleccionada en ElevenLabs (español neutro LATAM)
- [ ] Template visual Blotato `dinero-ia-dark-editorial` creado (carouseles opcionales)
- [ ] Manuel aprueba 3 reels test antes de activar producción

**Bloquea Fase 1.0:** sí. No arrancamos producción 2-3/día hasta que el smoke test video pase y los standards estén locked.

---

## Fase 1.0 — Producción arranque (Semanas 4-5, video con voice library)

**Objetivo:** primeros 30-50 reels publicados con pipeline 100% automatizado + HITL Telegram. Voz library mientras Manuel graba.

### Alcance

- Cadencia: 2-3 posts/día siguiendo slots ADR-019
- Formato dominante: reel video 25-35s (90%) + carousel ocasional (10%)
- Newsletter Beehiiv: 1 envío diario consolidando los 2-3 posts del día
- Voice: ElevenLabs library (español neutro LATAM masculino)
- HITL Telegram: aprobar/editar/regenerar/rechazar cada brief antes de publish

### Métricas Go/No-Go a Fase 1.1

- ≥30 reels publicados en 2 semanas con 0 compliance violations
- Engagement rate IG/TT >2% saves+comments/views
- Workflow estable >95% (max 2 failures/semana)
- Costo Anthropic + Seedance + ElevenLabs dentro de rango ($270-440/mo)
- Manuel sin necesidad de intervenir más de 30 min/día

### Bloquea Fase 1.1

Sí. No swap a voice clone Manuel hasta que voice library produzca reels que pasen métricas Go/No-Go.

---

## Fase 1.1 — Voice clone Manuel + producción estable (Semanas 6-7)

**Objetivo:** swap a voice clone Manuel + producción 2-3/día estable + primeros insights del algoritmo.

### Alcance

- Manuel graba 20-30 min siguiendo script
- ElevenLabs entrena voice clone (~30 min después de upload)
- Swap voice_id en A8c node (un parameter change)
- Continúa producción 2-3/día con voice clone
- Primer analytics review semanal: qué hooks pegan, qué sub_categorias rinden, qué horarios funcionan

### Métricas

| Métrica | 30 días | 60 días | 90 días | 180 días |
|---------|---------|---------|---------|---------|
| Reels publicados | 60-90 | 120-180 | 180-270 | 360-540 |
| Followers IG | 500-1,500 | 2,000-5,000 | 5,000-10,000 | 10K-20K |
| Newsletter subs | 200-500 | 600-1,500 | 1,500-3,500 | 3,500-7,000 |
| Avg engagement rate | >2% | >2.5% | >3% | >3% |
| Compliance violations | 0 | 0 | 0 | 0 |
| Costo total mensual | ~$300-400 | ~$350-450 | ~$350-450 | ~$400-500 |

> Reset realista calibrado a 2-3/día post-ADR-019. Más volumen → potencial growth más rápido si hooks pegan, pero también más quema si calidad baja.

---

## Fase 2 — Optimización + experimentos (Mes 3-4)

**Objetivo:** afinar hooks, sub_categorias top, horarios óptimos según data real.

- A/B test de hooks (mismo brief → 2 variantes de hook → mejor performance gana)
- Análisis de cuáles sub_categorias generan más saves vs más reach
- Ajuste de slots según engagement por hora
- Inflection Lever Track activo: Manuel envía DMs personalizados que Claude escribe
- Primer revenue test (affiliate broker / sponsored section)

---

## Fase 3 — Landing + monetización + community (Mes 4-6)

- Landing dineroia.com con captura email
- Migrar Beehiiv a Scale ($43/mo) cuando llegues a 2,500 subs
- Sponsored sections / affiliate brokers LATAM
- Community Telegram channel o Skool

---

## Fase 4 — Podcast + expansión (Mes 6+)

- Episodio semanal con voice clone Manuel
- Posible expansión LinkedIn dedicada (Fase 1.5 si data indica)
- Evaluar nicho secundario (post 10K subs validados)

---

## Timeline visual v6

```
Semana       1   2   3   4   5   6   7   8   9   10  11  12
Pre-Fase 1   ▓▓▓▓▓▓▓▓                                       ← research + standards + build
Fase 1.0           ▓▓▓▓▓▓▓▓                                  ← arranque voice library
Fase 1.1                  ▓▓▓▓▓▓                              ← swap voice clone
Fase 2                          ▓▓▓▓▓▓▓▓▓▓                    ← optimización
Fase 3                                  ▓▓▓▓▓▓▓▓▓ ...         ← monetización
Inflection   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (siempre)  ← Claude escribe, Manuel envía
```

---

## Diferencias clave v6 vs v5

| Concepto | v5 (ADR-017) | v6 (ADR-018/019) |
|---|---|---|
| Fase -1 manual | 10 piezas Manuel + 10 DMs Manuel en 2 semanas | SKIPPED por feedback Manuel |
| Fase 0 status | No iniciado | ✅ Completado smoke test |
| Formato Fase 1 | Texto + carouseles | Video reels con voz + música |
| Voice clone | Diferida Fase 2 | Activa Fase 1 (library → clone Manuel) |
| Cadencia Fase 1 | 1/día | 2-3/día con slots |
| A2 Scorer umbral | 60 | 65 |
| Costo Fase 1 | $130-180/mo | $270-440/mo |
| Tiempo a primer post | 2 semanas (Fase -1 manual) | 3-4 semanas (Pre-Fase 1 técnico) |
| Inflection Lever | Manuel manual outreaches | Híbrido: Claude escribe DM, Manuel envía |
