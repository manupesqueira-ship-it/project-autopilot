# Stack — AI Brief LATAM (v3, 2026-05-12)

> **Cambios v3 vs v2:**
> - n8n cloud → **Hostinger VPS self-hosted** (ADR-015)
> - Buffer placeholder → **Upload-Post** (ADR-014)
> - **Supabase** confirmado como DB + Storage + Auth (decisión C de OPEN_QUESTIONS)
> - **Telegram bidireccional** (no solo send) — patterns adoptados del #12533 deep review
> - Costos reproyectados: Fase 1 ~$30-45/mo (era $100-150 en v2)
> - Cursor + Perplexity diferidos (no en stack actual)

## Herramientas del sistema

| Tool | Purpose | Plan / Cost | Status |
|------|---------|-------------|--------|
| **Hostinger VPS KVM2** | Self-hosted n8n + docker stack | **$6.49/mo** (24-mo plan) | Por provisionar (ver `runbooks/hostinger-vps-n8n-setup.md`) |
| **n8n Community Edition** | Orquestación de workflows multi-agente self-hosted | Free (en el VPS) | Por instalar (template Hostinger one-click) |
| **Anthropic API** (Claude Opus 4 + Sonnet 4.5) | LLMs editoriales (A2-A11) | ~$24/mo Fase 1 (1 pieza/día) | Por configurar API key |
| **OpenAI API** (gpt-image-2) | Generación imágenes carousel | ~$6-8/mo (5-7 imgs × 30 días × $0.04) | Por configurar API key |
| **Upload-Post** | Auto-publish carousel IG + TikTok (community node n8n oficial) | TBD según plan (~$15-25/mo estimado) | Por crear cuenta — ADR-014 |
| **Supabase** | DB Postgres + Storage assets + Auth (Fase 7+) | Free tier (cubre Fase 1-2) → Pro $25/mo eventualmente | Por crear cuenta (deferred) |
| **Telegram Bot API** | HITL bidireccional (preview + approval + feedback edit-loop) | Free | Por crear bot vía @BotFather |
| **Seedance 2.0** | Video generation imagen→video reels | TBD (~$15/mo estimado) | Fase 2 |
| **ElevenLabs Creator** | Voice clone TTS para reels + podcast | $22/mo | Fase 2 (requiere grabación 20 min) |
| **Beehiiv** | Plataforma newsletter Smart Brevity daily | Free tier → Scale $49/mo cuando >2,500 subs | Fase 3 |
| **Canva Pro** | Post-procesado opcional de imágenes (typography touch-ups) | $14.99/mo | Fase 2 opcional |
| **Dominio + DNS** | `aibrieflatam.media` o similar (Namecheap/Hostinger) | ~$12/año (~$1/mo) | Por registrar |
| **GitHub** | Repositorio + audit trail markdown briefs | Free | Activo |
| **Buffer (backup)** | Manual fallback si Upload-Post outage | $0 si no se usa (free tier solo schedule manual) | Standby |

### Diferidos (NO en stack hoy)

| Tool | Por qué diferido | Reabrir cuándo |
|---|---|---|
| **Cursor** | Manuel no edita prompts manualmente; Claude lo hace desde chat | Si Manuel empieza a iterar prompts solo |
| **Perplexity Pro** | Claude web_search nativo cubre el fact-check del pipeline; Perplexity sería para Manuel personal | Si AI How-To LATAM valida y necesita Deep Research frecuente, o si los 5 prompts del 2026-05-18 requieren tool más robusta |
| **Inoreader** | n8n directo a RSS es suficiente para las fuentes confirmadas | Si querés sumar fuentes sin RSS (Bloomberg Línea, Infobae, Pulso Social) |
| **Lovable.dev** | No hay landing en Fase 1-2 | Fase 3+ si la newsletter necesita captura propia |
| **Meta Graph API directo** | Upload-Post intermedia | Si Upload-Post + Blotato ambos fallan |

## Costo proyectado por fase

> Ver `docs/COSTS_6MO.md` para proyección detallada mes a mes.

### Fase 0 (smoke test, 1-2 semanas): **~$5/mo**

| Componente | Costo |
|---|---:|
| n8n cloud trial gratis (cuenta aibrieflatam.media — ya activa) | $0 |
| Anthropic API (~$0.50/día × 14 días testing) | $7 |
| Telegram, GitHub | $0 |
| **Total Fase 0 (one-time durante 2 semanas)** | **~$7** |

### Fase 1 (texto + carousels, 1 pieza/día): **~$30-45/mo**

| Componente | Costo |
|---|---:|
| Hostinger VPS KVM2 (self-hosted n8n) | $6.49 |
| Anthropic API (Opus 4 + Sonnet 4.5 — 1 pieza/día con A2+A3+A4+A7+A9+A11) | $20-25 |
| OpenAI gpt-image-2 (5-7 slides × 30 días × $0.04) | $6-8 |
| Upload-Post (~$15-25 según plan) | $15-25 |
| Dominio + DNS | $1 |
| Supabase free tier | $0 |
| Telegram | $0 |
| **Total Fase 1** | **~$48-65/mo** |

### Fase 2 (+reels con voice clone): **+$40-50/mo**

| Componente | Costo |
|---|---:|
| ElevenLabs Creator | $22 |
| Seedance 2.0 (~10 reels/mes × $1.50) | $15 |
| Canva Pro (opcional, post-procesado) | $15 |
| **Delta Fase 2** | **+$37-52/mo** |
| **Total Fase 1+2** | **~$85-115/mo** |

### Fase 3 (+newsletter Beehiiv): **+$0-49/mo**

| Componente | Costo |
|---|---:|
| Beehiiv Free (hasta 2,500 subs) | $0 |
| Beehiiv Scale (>2,500 subs) | $49 |
| **Delta Fase 3 (escalado)** | **+$0-49/mo** |

### Fase 4 (+podcast): **+$0**

Spotify for Podcasters gratis. ElevenLabs ya activo de Fase 2.

## Por qué este stack vs v2

| Cambio | v2 (2026-05-10) | v3 (2026-05-12) | Razón |
|---|---|---|---|
| n8n hosting | Cloud $24/mo | Hostinger VPS $6.49/mo | Self-hosted permite community nodes (Upload-Post) sin restricción + ahorro $200+/año |
| Publisher | Buffer/Blotato/Upload-Post sin definir | **Upload-Post** locked (ADR-014) | Community n8n node oficial, multi-platform IG+TikTok, mejor que Blotato (Trustpilot 2.0/5) |
| DB/Storage | TBD entre Supabase/Sheets/Airtable | **Supabase** locked | "Todo en un lugar" pesa más que setup time |
| LLM principal | Claude Opus 4 | Claude Opus 4 (A3/A4/A7/A9/A11) + Sonnet 4.5 (A2 scoring) | Sonnet 5× más barato para batch scoring |
| Voice | ElevenLabs Creator | ElevenLabs Creator | Sin cambio |
| Image gen | gpt-image-2 | gpt-image-2 | Sin cambio (ADR-013) |
| Visual standard | TBD | Dark mode + Inter + JetBrains Mono (POST_STANDARD §7) | Documentado, pending Manuel confirm |
| HITL | Telegram send-only | **Telegram bidireccional** + A11 Editor LLM con feedback-loop | Pattern del #12533 deep review |

## Notas operacionales

- **Email business:** aibrieflatam.media@gmail.com (cuenta n8n cloud trial activa, GitHub eventualmente, Supabase, Upload-Post, etc.)
- **Email personal:** manupesqueira@gmail.com (NO usar para servicios del proyecto a menos que sea necesario)
- **Variables de entorno:** todas en n8n credentials (cifradas en SQLite del VPS). NUNCA en repo.
- **Backup:** cron diario en VPS exporta workflows + DB a S3/B2. Ver runbook.

## Open items del stack

- [ ] Plan Upload-Post — falta confirmar precio exacto (depende del volumen de posts/mes)
- [ ] Dominio — Manuel decide handle/dominio (OPEN_QUESTIONS L)
- [ ] Backup externo S3 vs B2 vs nada — decisión cuando se aplique el runbook
- [ ] Datacenter region Hostinger — BR (São Paulo) por defecto, verificar disponibilidad al comprar
