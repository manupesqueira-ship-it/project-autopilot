# Python MVP Snapshot — 2026-05-08/10

Snapshot de los 9 agents Python construidos 2026-05-08. Preservado como referencia histórica.

Los prompts y la lógica de scoring se extraen a `/prompts/` para uso en el nuevo sistema n8n.
El código ejecutable de aquí NO se usa más.

## Contenido

- `agents/` — 9 agents del MVP (source_monitor, signal_scorer, editorial, fact_checker, content_composer, compliance, human_approval, publisher, analytics)
- `autopilot.py` — CLI dispatcher (run-all, scan, score, brief, check, compose, comply, approve, publish, analytics)

## Stats al momento del snapshot

- 98 tests passing
- 12 fuentes RSS + Anthropic Blog scraping
- Pipeline end-to-end funcional (scan → publish)
- Claude Opus 4 para 5 agents LLM

## Por qué se descartó

Se pivotó a un stack profesional orquestado por n8n (2026-05-10):
- Python CLI requería intervención manual en cada paso
- Generación visual con Pillow era amateur
- Sin triggers automáticos, sin scheduling, sin auto-publish
- El nuevo sistema usa n8n + gpt-image-2 + ElevenLabs + Buffer para automatización real
