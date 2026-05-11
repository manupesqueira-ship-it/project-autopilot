# n8n Templates — Notas de inspección y adaptación

> Bitácora operacional. Cuando importes un template, registralo acá ANTES de modificar nada.

## Templates a importar (Fase 1)

| ID n8n | Nombre | URL | Función esperada | Status |
|---|---|---|---|---|
| #12533 | Curate AI newsletter from RSS | https://n8n.io/workflows/12533 | A1+A2+A3 esqueleto + HITL Slack→Telegram | ⏳ pending |
| #6389 | Smart RSS + Baserow (dedup) | https://n8n.io/workflows/6389 | Dedup persistente, patrón portable | ⏳ pending |
| #4399 | Anthropic AI Agent Sonnet 4 + web_search | https://n8n.io/workflows/4399 | A4 fact-checker con Claude nativo + web | ⏳ pending |
| #4028 | Carousel gpt-image-2 | https://n8n.io/workflows/4028 | A8a visual generator (swap gpt-image-1 → gpt-image-2) | ⏳ pending |
| #9472 o #5773 | Telegram HITL | https://n8n.io/workflows/9472 (o /5773) | A9 human approval | ⏳ pending |

## Por cada template importado — completar esta plantilla:

### Template: [ID + Nombre]
- **Fecha importación:**
- **URL original:**
- **Nodos que usa:**
- **Adaptaciones aplicadas:**
- **Lo que conservé del original:**
- **Lo que descarté:**
- **Issues encontrados al ejecutar:**
- **Decisión final:** mantener / descartar / fusionar con otro
- **Tiempo invertido:**

## Gaps custom identificados durante adaptación

(lista que crece cada vez que descubrimos algo que ningún template resuelve)

### Conocidos de antemano (del research 2026-05-11)
- **Rubric scoring de 8 categorías LATAM-aware** — ningún template lo tiene. Hay que construirlo desde cero como custom Function/AI Agent node con prompt detallado.
- **Buffer GraphQL publish para carousel IG** — no hay node oficial. Único ejemplo público (ghwoodard/n8n-social-media-automation) tiene 0 stars. Alternativas: Blotato, Upload-Post, Meta Graph API directo.
- **gpt-image-2 swap** — todos los templates 2026 apuntan a gpt-image-1/DALL-E. Swap manual obligatorio.
- **Claude prompt caching** — el node nativo Anthropic NO expone cache_control. Para system prompts grandes (scoring rubric), fallback a HTTP Request con headers cache_control.

### Descubiertos durante import (a llenar)
- _(vacío)_
