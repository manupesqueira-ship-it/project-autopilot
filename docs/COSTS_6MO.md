# Cost Projection — 6 meses (AI × Finanzas LATAM)

**Fecha:** 2026-05-29 (v2 post-ADR-017)
**Status:** proyección basada en ADR-017 (stack SaaS-first: ContentStudio + Blotato + Beehiiv + n8n cloud trial)
**Asunción base:** 1 pieza/día Fase 1, 1.5 piezas/día Fase 2 (mix carousel+reel), newsletter desde Fase 1
**Currency:** USD

---

## TL;DR

| Mes | Fase activa | Total USD/mo |
|---|---|---:|
| Mes 1 (jun 2026) | Fase -1 validación + Inflection Lever Track | **~$5-25** |
| Mes 2 (jul 2026) | Fase 0 smoke + Fase 1 setup | **~$50** |
| Mes 3 (ago 2026) | Fase 1 estable | **~$80-100** |
| Mes 4 (sep 2026) | Fase 1+2 build | **~$95-140** (depende voice clone) |
| Mes 5 (oct 2026) | Fase 1+2 estable + Fase 3 setup | **~$100-140** |
| Mes 6 (nov 2026) | Full stack + Beehiiv decision | **~$110-180** |

**Total acumulado 6 meses: ~$440-585 USD** (vs $544-735 en v1 — leve reducción por SaaS Fase 1)
**Si llegamos a Beehiiv Scale (2,500+ subs en mes 6): +$43/mo desde ese punto**

---

## Asunciones de volumen

| Componente | Volumen Fase 1 | Volumen Fase 2 |
|---|---|---|
| RSS items procesados (ContentStudio + n8n) | ~100-150/día (15-20 fuentes mix IA + finanzas) | mismo |
| Items que pasan filtro inicial | ~20-30/día | mismo |
| Items scored por A2 | ~20-30/día | mismo |
| Briefs generados A3 | 1-3/día | 1-3/día |
| Piezas publicadas | 1/día (carousel + caption) | 1.5/día (mix) |
| Newsletter envíos | 1/día | 1/día |
| Reels generados | 0 | 0.5/día (3-4 por semana) |

## Asunciones de pricing (locked al 2026-05-29)

| Servicio | Pricing actual | Fuente |
|---|---|---|
| ContentStudio Standard | **$19/mo** | contentstudio.io/pricing (Report 01) |
| Blotato Starter | **$29/mo** | blotato.com/pricing (Report 01) |
| Beehiiv Launch | **$0** (hasta 2,500 subs) | beehiiv.com/pricing |
| Beehiiv Scale | **$43/mo** anualizado | beehiiv.com/pricing |
| n8n cloud trial | **$0** | n8n.io |
| n8n cloud Starter (si trial se acaba) | €24/mo | n8n.io |
| Claude Opus 4 input/output | $5 / $25 per MTok | console.anthropic.com (Report 05) |
| Claude Sonnet 4.5 input/output | $3 / $15 per MTok | console.anthropic.com |
| OpenAI gpt-image-2 high | $0.040 / image | platform.openai.com (Report 05) |
| ElevenLabs Creator (Fase 2) | $11 primer mes (deal) → $22/mo | elevenlabs.io |
| Seedance 2.0 (Fase 2) | ~$1-1.50 / video | seedance.com |
| Supabase Free | $0 (hasta 500 MB + 1 GB Storage) | supabase.com |
| Telegram | $0 | core.telegram.org |
| GitHub Free | $0 | github.com |
| Domain (.media o .com) | ~$12-15 / año | namecheap.com / hostinger.com |
| ChatGPT Plus (Fase -1 manual) | $20/mo | openai.com |

---

## Mes 1 — Fase -1 validación + Inflection Lever Track (~$5-25)

| Componente | Costo | Notas |
|---|---:|---|
| ChatGPT Plus (DALL-E + visuales manuales para validación) | $0-20 | $0 si Manuel ya lo tiene activo; $20 si lo activa |
| Anthropic API (briefs en chat con Claude para validación, ~$0.30/día × 14 días) | $4 | Manuel usa Claude.ai chat (gratis) para mayoría — costo solo si Pro |
| Telegram, GitHub | $0 | |
| **Total Mes 1** | **$5-25** | Variable según si ChatGPT Plus ya activo |

**Nota:** la Fase -1 es manual — no se activa pipeline SaaS ni cloud todavía. Manuel publica con cuenta personal. **Cero compromiso de SaaS hasta validar voz.**

---

## Mes 2 — Fase 0 smoke + Fase 1 setup (~$50)

| Componente | Costo | Notas |
|---|---:|---|
| ContentStudio Standard (activar segunda mitad del mes) | $10 | Activación parcial |
| Blotato Starter (activar segunda mitad del mes) | $15 | Activación parcial |
| Beehiiv Launch | $0 | Gratis hasta 2,500 subs |
| n8n cloud trial | $0 | Sigue gratis |
| Anthropic API testing (Fase 0 smoke + setup) | $15 | A2 + A3 + A9 testing intensivo + iteración |
| OpenAI playground (image gen testing) | $3 | Pruebas pre-Fase 1 |
| Domain | $1 | $12/año amortizado |
| **Total Mes 2** | **$44** | Setup parcial, no full Fase 1 |

---

## Mes 3 — Fase 1 estable (~$80-100)

| Componente | Costo | Notas |
|---|---:|---|
| ContentStudio Standard | $19 | Hub social full |
| Blotato Starter | $29 | Carousels full |
| Beehiiv Launch | $0 | Gratis hasta 2,500 subs |
| n8n cloud trial → si se acaba, Starter | $0-30 | Probablemente trial alcanza Mes 3, Starter desde Mes 4-5 |
| Anthropic API Fase 1 (moat editorial: A2 + A3 + A4 + A9 + A11) | $25-42 | Ver breakdown abajo |
| OpenAI gpt-image-2 (backup visual si Blotato no rinde) | $6-8 | 5-7 slides × 30 días × $0.04 |
| Domain | $1 | |
| Telegram, GitHub, Supabase Free | $0 | |
| **Total Mes 3** | **$80-110** | |

### Breakdown Anthropic Mes 3 (detallado — moat editorial 4 agents, no 12)

| Agent | Modelo | Calls/día | Input tok/call | Output tok/call | Costo/día | Costo/mes |
|---|---|---:|---:|---:|---:|---:|
| A2 Scorer | Sonnet 4.5 | 20-30 | 500 | 300 | $0.18 | $5.40 |
| A3 Editorial AI×Finanzas | Opus 4 | 1 | 4,000 (incluye few-shot examples financieros) | 1,500 | $0.06 | $1.80 |
| A4 Fact-check financiero (web_search) | Opus 4 | 1 | 5,000 (incluye search results) | 1,000 | $0.05 | $1.50 |
| A9 Compliance v2 (18 reglas) | Opus 4 | 3-4 (× content types) | 3,000 | 1,000 | $0.13 | $3.90 |
| A11 Editor (cuando Manuel edita) | Opus 4 | 0.5 avg | 3,000 | 2,000 | $0.04 | $1.20 |
| **Total Anthropic moat editorial** | | | | | **$0.46/día** | **~$14/mo** |

**Diferencia vs v1 ($42/mo):** v1 incluía A7 Copy Composer + A8d Newsletter Composer en Opus que ahora corren en SaaS (Blotato + Beehiiv AI editor). El moat editorial puro es **~3× más barato en LLM cost.**

**Realista esperado Mes 3 con buffer:** $25-42/mo Anthropic (porque iteración + edge cases empujan más calls reales que el ideal).

---

## Mes 4 — Fase 2 setup (~$95-140)

| Componente | Costo | Notas |
|---|---:|---|
| ContentStudio + Blotato + Beehiiv | $48 | Sin cambio |
| n8n cloud (cloud Starter probable a esta altura) | $30 | Trial probablemente acabó |
| Anthropic API | $42 | Fase 1 estable + A6 Audio Director cuando arranque |
| OpenAI gpt-image-2 | $8 | Sigue carousel |
| **Voice clone decision (ADR-008 resuelto):** | | |
| ─ Opción A: ElevenLabs Creator | $11 primer mes (deal) | Activado mid-month |
| ─ Opción B: Narración manual | $0 | Sin costo extra |
| Seedance 2.0 (~3-4 reels/sem × $1.30) | $15 | Si Fase 2 arranca |
| Domain | $1 | |
| **Total Mes 4 si voice clone (A)** | **~$155** | |
| **Total Mes 4 si manual (B)** | **~$144** | |

---

## Mes 5 — Fase 2 estable + Fase 3 setup (~$100-160)

| Componente | Costo | Notas |
|---|---:|---|
| ContentStudio + Blotato + Beehiiv (probablemente todavía Free) | $48 | |
| n8n cloud Starter | $30 | |
| Anthropic API | $45 | A11.5 Analytics arranca |
| OpenAI gpt-image-2 | $10 | Más slides porque mix con reels |
| ElevenLabs Creator (si voice clone activo) | $22 | Precio normal post-deal |
| Seedance 2.0 | $18 | Más reels |
| Beehiiv (probablemente todavía Free) | $0 | <2,500 subs todavía |
| Lovable.dev landing (one-time setup) | $20 | O Free tier según template |
| Domain | $1 | |
| **Total Mes 5** | **$144-194** | One-time $20 landing setup |

---

## Mes 6 — Full stack (~$130-200)

| Componente | Costo | Notas |
|---|---:|---|
| ContentStudio + Blotato | $48 | |
| Beehiiv | $0 o $43 | Decisión Scale si llegamos a 2,500 subs |
| n8n cloud Starter | $30 | |
| Anthropic API | $50 | Pipeline maduro |
| OpenAI gpt-image-2 | $12 | |
| ElevenLabs Creator (si voice clone) | $22 | |
| Seedance 2.0 | $25 | Más reels |
| Lovable.dev landing | $0-20 | Continua si custom domain |
| Domain | $1 | |
| Supabase Pro (opcional si crecemos) | $0 o $25 | Free tier alcanza a menos que pasemos 500 MB DB |
| **Total Mes 6** | **$163-236** | Rango por Beehiiv + voice + Supabase |

---

## Total acumulado 6 meses (recalculado v2)

| Mes | Min | Realista | Max |
|---|---:|---:|---:|
| 1 | $5 | $15 | $25 |
| 2 | $40 | $50 | $60 |
| 3 | $80 | $95 | $115 |
| 4 | $95 | $130 | $160 |
| 5 | $100 | $145 | $195 |
| 6 | $130 | $170 | $235 |
| **Suma 6 meses** | **$450** | **$605** | **$790** |

**Promedio mensual:** ~$100/mo (vs $107/mo en v1)
**Equivalente anual estable post-launch:** ~$1,600-2,300/año (vs $1,800-2,500 v1)

---

## Comparación vs alternativas

| Alternativa | Costo Fase 1 | Trade-off |
|---|---:|---|
| **Stack ADR-017 (SaaS-first)** | $80-100/mo | Buy-first plumbing + custom moat. Menos overhead, menos supply chain risk. |
| Stack v3 anterior (Upload-Post + n8n Hostinger) | $80-100/mo | Mismo precio, más overhead técnico, más supply chain risk |
| n8n cloud Pro + ContentStudio + Blotato | $130-150/mo | +$50/mo, sin community nodes restriction si necesitamos |
| Make.com + Buffer + Airtable + Mailchimp | $100-140/mo | Workflow visual diferente; menos extensible para moat editorial |
| Custom Python stack en GCP/AWS | $50-90/mo + horas dev | Más custom, mucho más mantenimiento, supply chain risk si community libs |
| Manual operations (sin pipeline, Fase -1 extendida) | $25-50/mo | $25-50 + 22h/mes de Manuel = costo real ~$700-1,500/mo a $30-65/hora |

**Conclusión:** el stack SaaS-first del ADR-017 cuesta lo mismo que el custom v3 pero con mucho menos overhead. **El delta de valor está en el tiempo de Manuel ahorrado en setup + mantenimiento**, no en el ahorro mensual cash.

---

## Revenue targets para break-even (recalibrado v2)

A $100/mo costo promedio Mes 3 estable, break-even requiere:

| Estrategia | Required revenue/mo |
|---|---:|
| Sponsored sections (1× $250/sponsor) | 1 sponsored/2-3 meses |
| Affiliate brokers/fintechs LATAM (Cocos/IOL/GBM/Bitso) | 5-10 conversiones/mo si comisión $10-20 |
| Premium newsletter $5-10/mo | 10-20 subs |
| Curso "AI para tu plata" $50-100 | 1-2 ventas/mo |
| Comunidad Skool/Whop $5-10/mo | 10-20 miembros |

**Realistic timeline (ADR-017 reset):** revenue test en Mes 5-6, break-even Mes 8-10, monetización seria Mes 12+.

---

## Sensitivities — qué hace cambiar el total

### Si voice clone se difiere indefinidamente (Manuel decide narración manual)

- ElevenLabs $22/mo no se activa
- **Total ajuste: -$22/mo desde Fase 2** → 6mo final ~$430-680

### Si Manuel publica 2-3 piezas/día (no 1)

- Anthropic +2-3× → +$30-60/mo
- OpenAI gpt-image-2 +2× → +$10/mo
- ContentStudio/Blotato no escalan con volumen en planes Standard/Starter (publish unlimited)
- **Total ajuste: +$40-70/mo, llevando Mes 6 a ~$200-300**

### Si Beehiiv crece más rápido al Scale

- Si llegamos a 2,500 subs en mes 4 (no 6) → +$43/mo desde mes 4 = +$130 extra en los 6 meses
- **Total ajuste: +$130 al total 6mo**

### Si Manuel decide NO Fase 2 (sin reels)

- ElevenLabs $22/mo no se activa
- Seedance $15-25/mo no se activa
- Canva Pro opcional $15/mo no se activa
- **Total ajuste: -$50-60/mo desde Fase 2** → 6mo final ~$370-500

### Si necesitamos n8n cloud Pro (no Starter)

- +$36/mo desde Mes 4 cuando trial se acabe
- **Total ajuste: +$108 acumulado**

### Si pivot serio post Fase -1 (no llegamos a Fase 1)

- Stack SaaS NO se activa → ahorro $48/mo desde Mes 2
- **Total ajuste: -$240+ acumulado**, pero proyecto se pivota o pausa
- Solo costo es Mes 1 ($5-25) + Mes 2 si arrancó setup ($40-60)

---

## Recommendation para Manuel (v2 post-ADR-017)

1. **NO comprar nada en Mes 1 (Fase -1).** Validar manual con ChatGPT Plus existente + Claude.ai chat. Cero compromiso SaaS hasta validar voz.
2. **Activar SaaS recién Mes 2 (Fase 0 + setup Fase 1)** — y solo si Fase -1 valida la voz. Si no, no activar nada y pivot/pausa.
3. **Pagar ContentStudio + Blotato mensual al inicio** ($19 + $29 = $48), no anual. Hasta confirmar que el stack funciona 30 días, no commit anual.
4. **Beehiiv Free hasta saturar 2,500 subs** — no pagar Scale antes de tiempo.
5. **Voice clone diferir hasta Fase 2 cerca** — no comprar ElevenLabs antes de necesitarlo.
6. **Anthropic billing $30 inicial Mes 2** (cubre setup + smoke test). Aumentar gradual.
7. **Tracking de costos en `infra/costs-actual.md`** desde Mes 2 — sin esto, los actuals vs estos estimados son adivinanza.

Budget recomendado para presentar (Year 1):
- **Year 1 con voice clone activado: $1,400-2,300**
- **Year 1 sin voice clone: $1,100-2,000**
- **Year 1 si pivot Fase -1: $50-150** (validación + abort)

Compara con costo de un creator freelance LATAM ($800-2,000/mo solo content) — el automatizado paga 1 freelance al mes.
