# Stack — AI × Finanzas LATAM (v4, 2026-05-29)

> **Cambios v4 vs v3** (ADR-017 post-Deep-Research):
> - **Stack SaaS-first:** ContentStudio + Blotato + Beehiiv reemplaza n8n custom + Upload-Post.
> - **Upload-Post → DESCARTADO** (no aparece en análisis competitivo Report 01). Blotato (que era plan B en v3) toma su lugar.
> - **Hostinger VPS → DIFERIDO** (n8n cloud trial gratis primero; VPS solo si trial se acaba o necesitamos community nodes).
> - **n8n rol reducido** a solo moat editorial (4 agents: scorer + fact-check + compliance + Telegram HITL).
> - **Beehiiv adelantado** a Fase 1 (era Fase 3 en v3).
> - **ElevenLabs / Seedance / Canva** mantienen Fase 2 pero voice clone diferido a decisión Fase 2.
> - **Costos Fase 1:** ~$80-100/mo (mismo rango que v3, pero menos overhead).

## Herramientas del sistema

| Tool | Purpose | Plan / Cost | Status |
|------|---------|-------------|--------|
| **ContentStudio Standard** | Hub social: RSS discovery + AI captions/hashtags + approvals + scheduling + multi-platform publish (IG/TikTok/LinkedIn/X/YouTube/Threads) | **$19/mo** | Por crear cuenta (Fase 1) — ADR-017 |
| **Blotato Starter** | Carousel generation + AI images + AI voices + social API + community nodes oficiales n8n/Make | **$29/mo** | Por crear cuenta (Fase 1) — ADR-017 |
| **Beehiiv Launch** | Newsletter publishing + AI editor + automations + welcome sequence + analytics | **$0** (gratis hasta 2,500 subs) → **$43/mo Scale** (anualizado) | Por crear cuenta (Fase 1) — ADR-017 |
| **n8n cloud trial** | Orquestación del moat editorial (4 agents) + Telegram HITL | **$0** (trial gratis) | Por activar cuenta existente aibrieflatam.media@gmail.com — ADR-017 |
| **Anthropic API** (Opus 4 + Sonnet 4.5) | LLMs editoriales (A2 + A3 + A4 + A9 + A11) | ~$25-42/mo Fase 1 | Por configurar API key |
| **OpenAI API** (gpt-image-2) | Image gen backup si Blotato no rinde para visuales financieros editoriales | ~$6-8/mo Fase 1 | Por configurar API key |
| **Telegram Bot API** | HITL bidireccional (preview + approval + feedback edit-loop) | Free | Por crear bot vía @BotFather |
| **Supabase** | DB Postgres + Storage assets + Auth (Fase 7+ landing/comunidad) | Free tier → Pro $25/mo eventualmente | Diferido (no urgente Fase 1) |
| **Seedance 2.0** | Video generation imagen→video reels | ~$15/mo estimado | Fase 2 |
| **ElevenLabs Creator** | Voice clone TTS para reels + podcast | $11 primer mes (deal 50% off) → $22/mo | Fase 2 — **decisión final post-Fase 1** (ADR-008 DEFERRED) |
| **Lovable.dev** | Landing newsletter (Fase 3) | Free → $20/mo plan básico | Fase 3 |
| **Canva Pro** | Post-procesado opcional imágenes (typography touch-ups) | $14.99/mo | Fase 2 opcional |
| **Dominio + DNS** | `aifinanzas.media` o handle similar (TBD) | ~$12/año (~$1/mo) | Por registrar después de Fase -1 con nombre decidido |
| **GitHub** | Repositorio + audit trail markdown briefs | Free | Activo |

### Diferidos (NO en stack hoy)

| Tool | Por qué diferido | Reabrir cuándo |
|---|---|---|
| **Hostinger VPS KVM2** | n8n cloud trial cubre Fase 0-1. VPS solo si trial se acaba o necesitamos community nodes que cloud bloquea. | Cuando el trial se acabe O al pasar a producción seria 24/7 |
| **Upload-Post** | No aparece en análisis competitivo del Report 01. Blotato cubre el caso con mejor integración n8n. | Si Blotato + ContentStudio ambos fallan |
| **Cursor** | Manuel no edita prompts manualmente; Claude lo hace desde chat | Si Manuel empieza a iterar prompts solo |
| **Perplexity Pro** | Claude web_search nativo cubre el fact-check del pipeline | Si fact-check financiero requiere tool más robusta |
| **Inoreader** | RSS directo en ContentStudio + n8n suficiente para fuentes confirmadas | Si querés sumar fuentes finanzas sin RSS (Bloomberg Línea, Infobae Tecno) |
| **Meta Graph API directo** | ContentStudio + Blotato intermedian | Si ambos SaaS fallan |

## Costo proyectado por fase (recalculado ADR-017)

> Ver `docs/COSTS_6MO.md` para proyección detallada mes a mes (recalculada también).

### Fase -1 (validación manual, 1-2 semanas): **~$5-10**

| Componente | Costo |
|---|---:|
| ChatGPT Plus (DALL-E + visuales manuales) | $20 (Manuel ya lo tiene o $20 si lo activa este mes) |
| Anthropic API (~$0.30/día × 14 días) | $4 |
| Telegram, GitHub | $0 |
| **Total Fase -1 (one-time)** | **~$5-25** (depende si ChatGPT Plus ya activo) |

### Fase 0 (smoke test, ~1 semana): **~$10-15**

| Componente | Costo |
|---|---:|
| n8n cloud trial | $0 |
| Anthropic API (~$0.50/día × 7 días testing) | $4 |
| Telegram, GitHub | $0 |
| **Total Fase 0** | **~$5-10** |

### Fase 1 (texto + carousels + newsletter, 1 pieza/día): **~$80-100/mo**

| Componente | Costo |
|---|---:|
| ContentStudio Standard | $19 |
| Blotato Starter | $29 |
| Beehiiv Launch | $0 |
| n8n cloud trial (gratis hasta limit) | $0 |
| Anthropic API (Opus + Sonnet — moat editorial 4 agents) | $25-42 |
| OpenAI gpt-image-2 (backup visual) | $6-8 |
| Dominio + DNS | $1 |
| Supabase free tier | $0 |
| Telegram | $0 |
| **Total Fase 1** | **~$80-100/mo** |

### Fase 2 (+reels): **+$15-40/mo (según decisión voice clone)**

| Componente | Costo si voice clone | Costo si narración manual |
|---|---:|---:|
| ElevenLabs Creator | $22 | $0 |
| Seedance 2.0 (~10 reels/mes × $1.50) | $15 | $15 |
| Canva Pro (opcional) | $15 | $15 |
| **Delta Fase 2** | **+$37-52/mo** | **+$15-30/mo** |
| **Total Fase 1+2** | **~$115-150/mo** | **~$95-130/mo** |

### Fase 3 (+landing + Beehiiv Scale + revenue test): **+$0-65/mo**

| Componente | Costo |
|---|---:|
| Lovable.dev (landing) | $0-20 |
| Beehiiv Scale (>2,500 subs) | $0 si no llegamos / $43 si sí |
| Tracking analytics propio (n8n) | $0 |
| **Delta Fase 3** | **+$0-63/mo** |

### Fase 4 (+podcast + community): **+$0-60/mo**

| Componente | Costo |
|---|---:|
| Spotify for Podcasters | $0 |
| Skool / Whop (si elegimos pago) | $0-59 |
| **Delta Fase 4** | **+$0-59/mo** |

## Por qué este stack vs v3

| Cambio | v3 (2026-05-12) | v4 (2026-05-29) | Razón |
|---|---|---|---|
| Publishing | Upload-Post community node en n8n | **ContentStudio + Blotato (SaaS)** | Report 01: ContentStudio G2 4.6/372 + Blotato community node n8n oficial. Upload-Post no aparece en análisis competitivo. |
| n8n hosting | Hostinger VPS self-hosted $6.49/mo | **n8n cloud trial (gratis) primero, VPS deferred** | Report 05: n8n CVEs reales 2025-2026. Cloud reduce supply chain risk + setup time. VPS si trial no alcanza. |
| Carousel generation | gpt-image-2 directo + Python custom | **Blotato AI Agent Carousel Maker** | Report 01: cubre el caso con templates + community node n8n. Mejor que custom para SMB. |
| Newsletter timing | Fase 3 (escalado post-Fase 1+2) | **Fase 1 desde día 1** | Reports 02+05: newsletter es el canal más durable. Adelantar = más tiempo de compounding. |
| Voice clone | Activado Fase 2 (ADR-008) | **DEFERRED — decisión final inicio Fase 2** | Report 05: TikTok auto-etiqueta voice clone realista. Pivot a finanzas refuerza autoridad personal Manuel. |
| LLM principal | Opus 4 + Sonnet 4.5 | Sin cambio | Sigue siendo óptimo |
| Image gen | gpt-image-2 | gpt-image-2 (vía Blotato) | Mismo modelo, ahora orquestado por Blotato |
| Nicho stack | AI How-To LATAM genérico | **AI × Finanzas LATAM** (vertical único) | ADR-017 cambio 2 |
| HITL | Telegram bidireccional + A11 Editor LLM | Sin cambio | Pattern probado |

## Notas operacionales

- **Email business:** `aibrieflatam.media@gmail.com` (sigue activo — usar para todas las cuentas: ContentStudio, Blotato, Beehiiv, Anthropic, OpenAI, n8n cloud, Telegram Bot). Cuando se decida nombre nuevo, redirigir desde nuevo dominio.
- **Email personal:** `manupesqueira@gmail.com` (NO usar para servicios del proyecto)
- **Variables de entorno:** todas en n8n cloud credentials (cifradas en cloud). NUNCA en repo.
- **Backup:** export semanal del workflow JSON de n8n a GitHub (`infra/n8n/exports/`)
- **Supply chain risk mitigation:**
  - SaaS (ContentStudio + Blotato + Beehiiv) tienen sus propios SLAs
  - n8n cloud reduce el riesgo vs self-hosted con community nodes
  - Plan B documentado por capa (ver tabla arriba)

## Open items del stack

- [ ] Confirmar plan ContentStudio (Standard $19 alcanza para Fase 1; Advanced $49 si necesitamos más cuentas)
- [ ] Confirmar plan Blotato (Starter $29 cubre carousels + AI images; Creator $97 si necesitamos AI videos)
- [ ] Dominio + handle — Manuel decide post Fase -1
- [ ] Datacenter region n8n cloud — verificar latencia LATAM al activar
- [ ] Investigar ContentStudio + Blotato + Beehiiv reviews 2026 actualizados antes de comprometer (deal vigente en cada uno)
- [ ] Decisión voice clone Fase 2 (ADR-008 DEFERRED)
