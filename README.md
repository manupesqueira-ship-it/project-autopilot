# AI Brief LATAM — Multi-Agent Content System

Sistema automatizado de producción de contenido sobre IA para profesionales de Latinoamérica. Orquestado por n8n, powered by Claude + OpenAI + ElevenLabs.

**Estado:** Fase 1 en arranque (post-pivot 2026-05-10)
**Cuentas activas:** Instagram @breiflatam | TikTok @ai.brief.latam

## Stack

n8n (orquestador) + Anthropic Claude Opus 4 (editorial/scoring/compliance) + OpenAI gpt-image-2 (visuales) + ElevenLabs (voice clone, Fase 2) + Seedance 2.0 (video, Fase 2) + Buffer (auto-publish IG/TikTok) + Beehiiv (newsletter, Fase 3)

## Estructura del repo

```
project-autopilot/
├── docs/                              # Source of truth
│   ├── SYSTEM_DESIGN.md               # Arquitectura de 11 agents
│   ├── AGENTS_SPEC.md                 # Spec técnica por agent (A1-A11)
│   ├── STACK.md                       # Herramientas + costos
│   ├── ROADMAP.md                     # 4 fases con Definition of Done
│   ├── CONTENT_STRATEGY.md            # Ángulo editorial + métricas
│   ├── PROJECT_STATE.md               # Estado operativo actual
│   ├── EXPENSES.md                    # Tracking de gastos
│   └── AUDIT_2026-05-08.md            # Audit del Python MVP
│
├── prompts/                           # System prompts (versionados)
│   ├── signal-scorer-rubric.md        # 8 categorías Anexo B
│   ├── editorial-system-prompt.md     # Brief Smart Brevity
│   ├── fact-checker-prompt.md         # Verificación de claims
│   ├── content-composer-prompt.md     # Carousel + caption + reel
│   ├── compliance-rules.md            # Meta rules + brand voice
│   ├── brand-voice.md                 # Voz de marca completa
│   └── source-monitor-config.md       # Keywords + scoring weights
│
├── workflows/n8n/                     # Export JSON de workflows n8n
├── assets/brand/                      # Logos, templates, paletas
├── data/sources/                      # Configs de RSS, keywords
│
├── projects/                          # Properties (config por marca)
│   ├── dinero-ia/               # Priority #1 (activa)
│   ├── crypto-brief-latam/           # Pending (Fase 5+)
│   └── startup-radar-latam/          # Pending (Fase 6+)
│
└── legacy/python-mvp-2026-05-10/      # Snapshot del Python MVP descartado
    ├── agents/                        # 9 agents (98 tests)
    └── autopilot.py                   # CLI dispatcher
```

## Cómo navegar

1. Empezar por **`docs/SYSTEM_DESIGN.md`** — arquitectura completa del sistema
2. Ver **`docs/ROADMAP.md`** — las 4 fases y qué estamos construyendo ahora
3. Consultar **`docs/AGENTS_SPEC.md`** — spec técnica de cada agent
4. Los prompts en **`prompts/`** se usan como system prompts en los workflows de n8n

## Histórico

El repo contiene un Python MVP descartado en `legacy/python-mvp-2026-05-10/` (9 agents, 98 tests, pipeline CLI). Se pivotó a n8n + herramientas profesionales porque el MVP Python requería intervención manual, generaba visuales amateur (Pillow), y no tenía triggers ni auto-publish. Los prompts y la lógica de scoring se rescataron a `/prompts/`.
