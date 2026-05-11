# Stack — AI Brief LATAM (v2, 2026-05-10)

## Herramientas del sistema

| Tool | Purpose | Plan / Cost | Status |
|------|---------|-------------|--------|
| **n8n Cloud** | Orquestación de workflows multi-agente | ~$24/mo (o self-hosted en Hostinger VPS) | Por configurar |
| **Anthropic API (Claude Opus 4)** | LLM principal para editorial, fact-check, compliance, copy | ~$1-3/day (~$30-90/mo) | API key activa |
| **OpenAI API (gpt-image-2)** | Generación de imágenes para carousels 1080x1080 | ~$0.02-0.08/imagen (~$15-50/mo a 21 imgs/week) | API key activa |
| **Seedance 2.0** | Generación de video para reels (imagen+guion a video) | TBD | Fase 2 |
| **ElevenLabs** | Voice clone de Manuel + TTS para voiceover de reels/podcast | Creator plan $22/mo | Fase 2 |
| **Canva Pro** | Templates de diseño, assets visuales complementarios | $14.99/mo | Fase 2 (opcional) |
| **Beehiiv** | Plataforma de newsletter (brief extendido por email) | Free tier → $49/mo (Scale) | Fase 3 |
| **Lovable.dev** | Landing page / sitio web del proyecto | Pricing TBD | Fase 3+ (opcional) |
| **Blotato (a evaluar) \| Upload-Post (a evaluar) \| Buffer (fallback)** | Auto-publish a Instagram + TikTok en horarios programados | Pendiente — depende de research comparativo (Blotato ~$15-30/mo, Upload-Post ~$10-25/mo, Buffer $6/mo) | Por evaluar |
| **Telegram Bot API** | Human-in-the-loop: aprobación de contenido en Fase 1 | Gratis | Por configurar |
| **Spotify for Podcasters** | Distribución de episodios de podcast | Gratis | Fase 4 |
| **GitHub** | Repositorio de código, prompts, documentación | Gratis | Activo |
| **Cursor** | IDE para desarrollo (no runtime, solo dev tool) | Dev tool (no costo runtime) | Activo |

## Costo estimado por fase

### Fase 1 MVP (texto + carousels): ~$100-150/mo

| Concepto | Estimado |
|----------|----------|
| n8n Cloud | $24 |
| Claude Opus 4 API (~63 calls/week scoring + editorial + compliance) | $30-90 |
| gpt-image-2 (~84 imágenes/mo, 4 slides x 21 posts) | $15-50 |
| Publisher (Blotato \| Upload-Post \| Buffer — TBD post-research) | $6-30 |
| Telegram Bot | $0 |
| GitHub | $0 |
| **Total Fase 1** | **~$75-195/mo** |

### Fase 2 (+reels): +$35-40/mo adicional
- ElevenLabs Creator: $22/mo
- Seedance 2.0: TBD (~$10-15/mo estimado)
- Canva Pro (opcional): $14.99/mo

### Fase 3 (+newsletter): +$0-49/mo adicional
- Beehiiv: Free tier inicialmente, Scale plan $49/mo al crecer

### Fase 4 (+podcast): +$0/mo adicional
- Spotify for Podcasters: Gratis

## Notas

- Los costos de API (Claude, OpenAI) son variables y dependen del volumen real de tokens. Las estimaciones asumen 3 piezas/día con prompts optimizados.
- n8n puede migrarse a self-hosted en Hostinger VPS para reducir costos si el volumen de ejecuciones lo justifica.
- Cursor es una herramienta de desarrollo, no un costo de runtime del sistema.
- El email del sistema es aibrieflatam@gmail.com (business) y manupesqueira@gmail.com (personal/n8n).
