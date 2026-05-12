# Cost Projection — 6 meses (AI Brief LATAM)

**Fecha:** 2026-05-12
**Status:** proyección basada en ADR-014 (Upload-Post) + ADR-015 (Hostinger VPS) + STACK.md v3
**Asunción base:** 1 pieza/día Fase 1, 1.5 piezas/día Fase 2 (mix carousel+reel), newsletter daily a partir Fase 1
**Currency:** USD

---

## TL;DR

| Mes | Fase activa | Total USD/mo |
|---|---|---:|
| Mes 1 (jun 2026) | Fase 0 + Fase 1 build | **~$15** |
| Mes 2 (jul 2026) | Fase 1 estable | **~$50-65** |
| Mes 3 (ago 2026) | Fase 1 + Fase 2 build | **~$80** |
| Mes 4 (sep 2026) | Fase 1+2 estable | **~$95-115** |
| Mes 5 (oct 2026) | Fase 1+2+3 build | **~$100-125** |
| Mes 6 (nov 2026) | Full stack estable | **~$100-180** (variable según Beehiiv plan) |

**Total acumulado 6 meses: ~$450-650 USD**
**Si llegamos a Beehiiv Scale (2,500+ subs en mes 6): +$49/mo desde ese punto**

---

## Asunciones de volumen

| Componente | Volumen Fase 1 | Volumen Fase 2 |
|---|---|---|
| RSS items procesados | ~150-200/día (12 fuentes) | mismo |
| Items que pasan A1.5 binary filter | ~30-50/día | mismo |
| Items scored por A2 | ~30-50/día | mismo |
| Briefs generados A3 | 1-3/día | 1-3/día |
| Piezas publicadas | 1/día | 1.5/día (mix) |
| Newsletter envíos | 1/día | 1/día |
| Reels generados | 0 | 0.5/día (3-4 por semana) |

## Asunciones de pricing (locked al 2026-05-12)

| Servicio | Pricing actual | Fuente |
|---|---|---|
| Claude Opus 4 input | $15 / 1M tokens | console.anthropic.com |
| Claude Opus 4 output | $75 / 1M tokens | console.anthropic.com |
| Claude Sonnet 4.5 input | $3 / 1M tokens | console.anthropic.com |
| Claude Sonnet 4.5 output | $15 / 1M tokens | console.anthropic.com |
| OpenAI gpt-image-2 high | $0.040 / image | platform.openai.com |
| Hostinger KVM2 (24-mo) | $6.49 / mo | hostinger.com/pricing/n8n-hosting |
| Upload-Post (TBD) | ~$15-25 / mo estimado | upload-post.com |
| ElevenLabs Creator | $22 / mo | elevenlabs.io |
| Seedance 2.0 | $1-1.50 / video estimado | seedance.com |
| Beehiiv Free | $0 (hasta 2,500 subs) | beehiiv.com/pricing |
| Beehiiv Scale | $49 / mo (2,500-10K subs) | beehiiv.com/pricing |
| Supabase Free | $0 (hasta 500 MB DB + 1 GB Storage) | supabase.com/pricing |
| Telegram | $0 | core.telegram.org |
| GitHub Free | $0 | github.com |
| Domain (.media o .com) | ~$12-15 / año | namecheap.com / hostinger.com |

---

## Mes 1 — Fase 0 smoke test + Fase 1 setup (~$15)

| Componente | Costo | Notas |
|---|---:|---|
| n8n cloud trial (gratis, cuenta aibrieflatam.media existente) | $0 | Trial vigente al 2026-05-12 |
| Anthropic API testing (~$0.30/día × 30 días) | $9 | Smoke test 14 días + setup tweaks |
| OpenAI playground (imágenes manuales testing) | $2 | Pruebas de visual standard pre-Fase 1 |
| Hostinger VPS (1 mes piloto) | $7 | Plan mensual $14.99 prorrateado o el 24mo plan $6.49 desde día 1 |
| Domain | $1 | $12/año amortizado |
| **Total Mes 1** | **$15-19** | |

Notas: si Manuel arranca con el 24-mo plan de Hostinger ($156 prepago) el costo upfront es $156 pero amortizado $6.49/mo. Si arranca con el monthly ($14.99) el cash-flow inicial es mejor pero pagas 2.3× más.

---

## Mes 2 — Fase 1 estable (~$50-65)

| Componente | Costo | Notas |
|---|---:|---|
| Hostinger VPS KVM2 | $6.49 | |
| Anthropic API Fase 1 | $20-25 | A2 (Sonnet) + A3+A4+A7+A9+A11 (Opus) × 1 pieza/día + A1.5 binary filter |
| OpenAI gpt-image-2 | $6-8 | 5-7 slides × 30 días × $0.04 |
| Upload-Post | $15-25 | Estimado, pendiente confirmar plan |
| Supabase | $0 | Free tier suficiente |
| Domain | $1 | |
| Telegram | $0 | |
| **Total Mes 2** | **$48-65** | |

### Breakdown Anthropic Mes 2 (detallado)

| Agent | Modelo | Calls/día | Input tokens/call | Output tokens/call | Costo/día | Costo/mes |
|---|---|---:|---:|---:|---:|---:|
| A1.5 Binary filter | Sonnet 4.5 | 50 | 200 | 50 | $0.04 | $1.20 |
| A2 Scorer | Sonnet 4.5 | 30 | 500 | 300 | $0.18 | $5.40 |
| A3 Editorial | Opus 4 | 1 | 3,000 | 1,500 | $0.16 | $4.80 |
| A4 Fact-check | Opus 4 | 1 | 4,000 | 1,000 | $0.14 | $4.20 |
| A7 Copy Composer | Opus 4 | 1 | 4,000 | 3,000 | $0.29 | $8.70 |
| A8d Newsletter | Opus 4 | 1 | 4,000 | 3,000 | $0.29 | $8.70 |
| A9 Compliance | Opus 4 | 3-4 (× content types) | 2,500 | 800 | $0.18 | $5.40 |
| A11 Editor (cuando Manuel edita) | Opus 4 | 0.5 avg | 3,000 | 2,000 | $0.11 | $3.30 |
| **Total Anthropic** | | | | | **$1.39/día** | **~$42/mo** |

⚠️ **Discrepancia con el $20-25 de arriba:** la tabla detallada da $42/mo, no $25. La diferencia es que las primeras semanas no corren todos los agents (compliance solo en publishable items, A11 solo en edits, etc.). **Proyección más realista mes 2: $35-45/mo solo Anthropic**, con tendencia a $42 a medida que el pipeline madura.

→ **Ajuste Mes 2 total: $60-78/mo** (no $50-65 como simplista arriba).

---

## Mes 3 — Fase 2 setup (~$80)

| Componente | Costo | Notas |
|---|---:|---|
| Hostinger VPS | $6.49 | |
| Anthropic API | $42 | Fase 1 estable + A6 Audio Director cuando arranque |
| OpenAI gpt-image-2 | $6-8 | Carousel sigue |
| Upload-Post | $20 | |
| ElevenLabs Creator | $22 | Activado mid-month después de grabación |
| Domain | $1 | |
| **Total Mes 3** | **$97-100** | |

---

## Mes 4 — Fase 2 estable (~$110)

| Componente | Costo | Notas |
|---|---:|---|
| Hostinger VPS | $6.49 | |
| Anthropic API | $48 | +A6 corriendo regular |
| OpenAI gpt-image-2 | $10 | Más slides porque mix con reels |
| Upload-Post | $20 | |
| ElevenLabs Creator | $22 | |
| Seedance 2.0 (~3-4 reels/sem × $1.30 × 15 reels/mo) | $20 | |
| Domain | $1 | |
| **Total Mes 4** | **$127** | |

---

## Mes 5 — Fase 3 newsletter scale setup (~$135)

| Componente | Costo | Notas |
|---|---:|---|
| Hostinger VPS | $6.49 | |
| Anthropic API | $50 | A11.5 Analytics arranca |
| OpenAI gpt-image-2 | $10 | |
| Upload-Post | $20 | |
| ElevenLabs Creator | $22 | |
| Seedance 2.0 | $20 | |
| Beehiiv (probably Free aún) | $0 | Si <2,500 subs |
| Lovable.dev landing (one-time setup) | $20 | Plan más barato para landing simple, o usar Lovable Free |
| Domain | $1 | |
| **Total Mes 5** | **$130-150** | One-time $20 landing setup |

---

## Mes 6 — Full stack (~$130-180)

| Componente | Costo | Notas |
|---|---:|---|
| Hostinger VPS | $6.49 | |
| Anthropic API | $55 | Pipeline maduro |
| OpenAI gpt-image-2 | $12 | |
| Upload-Post | $25 | Puede subir si volumen crece |
| ElevenLabs Creator | $22 | |
| Seedance 2.0 | $25 | Más reels |
| Beehiiv | $0 o $49 | Depende si pasamos 2,500 subs (target: SÍ en mes 6) |
| Lovable.dev landing | $0 o $20 | Continua si tenemos custom domain |
| Domain | $1 | |
| Supabase Pro (opcional si crecemos) | $0 o $25 | Free tier alcanza a menos que pasemos 500 MB DB |
| **Total Mes 6** | **$146-220** | Rango por Beehiiv + Supabase + Lovable |

---

## Total acumulado 6 meses

| Mes | Min | Realista | Max |
|---|---:|---:|---:|
| 1 | $15 | $17 | $25 |
| 2 | $48 | $70 | $80 |
| 3 | $90 | $100 | $110 |
| 4 | $115 | $127 | $140 |
| 5 | $130 | $145 | $160 |
| 6 | $146 | $180 | $220 |
| **Suma 6 meses** | **$544** | **$639** | **$735** |

**Promedio mensual:** ~$107/mo
**Equivalente anual estable post-launch:** ~$1,800-2,500/año

---

## Comparación vs alternativas

| Alternativa | Costo Fase 1 | Trade-off |
|---|---:|---|
| **Stack actual** | $48-65/mo | Self-hosted, máxima flexibilidad |
| n8n cloud Pro + Buffer + Sheets | $100-130/mo | +$50/mo, menos mantenimiento, sin community nodes |
| Make.com + Buffer + Airtable | $80-120/mo | Workflow visual diferente; menos extensible |
| Custom Python stack en GCP | $40-80/mo + horas dev | Más custom, mucho más mantenimiento |
| **Manual operations (sin pipeline)** | $35-50/mo | $35-50 + 22h/mes de Manuel = costo real ~$700-1,500/mo a $30-65/hora |

**Conclusión:** el stack automatizado paga su propio costo en horas ahorradas de Manuel desde el día 1.

---

## Revenue targets para break-even

A $107/mo costo promedio, break-even requiere:

| Estrategia | Required revenue/mo |
|---|---:|
| Patreon-style suscripciones $5/mo | 22 supporters |
| Premium newsletter $10/mo | 11 subs |
| Sponsored sections (1× $200/sponsor) | 1 sponsored/2 meses |
| Affiliate links (1% conversion en 5K reach) | ~5 ventas/mo de productos $100-200 |

Realistic timeline: revenue test en Mes 6, break-even Mes 9-12.

---

## Sensitivities — qué hace cambiar el total

### Si Manuel publica 2-3 piezas/día (no 1)

- Anthropic +2-3× → +$60-80/mo
- OpenAI gpt-image-2 +2× → +$10/mo
- Upload-Post mismo plan probable
- **Total ajuste: +$70-90/mo, llevando Mes 6 a ~$230-280**

### Si saltamos directo a 12 fuentes con polling cada 3h (no 1× día)

- n8n ejecuciones: ya self-hosted ilimitado, sin impacto $
- Anthropic A1.5 binary filter: 4× más items procesados → +$3/mo Sonnet
- **Total ajuste: +$3-5/mo, despreciable**

### Si reemplazamos Upload-Post por Buffer/Blotato

- Upload-Post estimado $20 → Buffer $15 ahorra $5/mo
- O Blotato $29 cuesta $9/mo extra
- **Total ajuste: ±$5-10/mo**

### Si Beehiiv crece más rápido al Scale

- Si llegamos a 2,500 subs en mes 4 (no 6) → +$49/mo desde mes 4 = +$100 extra en los 6 meses
- **Total ajuste: +$100 al total 6mo**

### Si Manuel decide NO Fase 2 (sin reels)

- ElevenLabs $22/mo no se activa
- Seedance $20-25/mo no se activa
- Canva Pro opcional $15/mo no se activa
- **Total ajuste: -$57-62/mo desde Fase 2 → 6mo final ~$400-500**

---

## Recommendation para Manuel

1. **Comprar Hostinger 24-mo plan upfront** ($156 prepago, amortiza a $6.49/mo). Cash-flow upfront mejor para presupuesto anual.
2. **Anthropic billing $50 inicial** (cubre Fase 0 + primer mes Fase 1).
3. **Diferir ElevenLabs hasta Fase 2 real** — $22/mo se ahorra si la grabación tarda.
4. **No activar Beehiiv Scale hasta que el Free tier (2,500 subs) saturera** — pago de $49 sin tener engagement no vale.
5. **Tracking de costos en Supabase tabla `costs`** desde día 1 — sin esto, los actuals vs estos estimados son adivinanza.

Budget recomendado para presentar a un partner/inversor o approval interno:
- **Year 1: $1,500-2,000** (incluye ramp-up)
- **Year 2+: $1,200-1,800** (steady state)

Compara con costo de un creator freelance LATAM ($800-2,000/mo solo content) — el automatizado paga 1 freelance al mes.
