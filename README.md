# Project Autopilot

Sistema multi-agente para construir, operar y escalar un portafolio de propiedades de medios digitales en Latinoamérica.

## Qué es

Un sistema operativo de agentes donde la IA hace el trabajo pesado (research, drafts, fact-check, composición, compliance) y el humano es el editor jefe que aprueba antes de publicar.

Tres reglas que ordenan todo:
1. **Manual antes que automatizado.** Operar a mano antes de que los agentes ejecuten.
2. **Una property antes que tres.** Las demás esperan a que la primera tenga tracción.
3. **Human-in-the-loop.** Ningún post sale sin aprobación humana.

## Arquitectura — 3 capas

```
CAPA 3 — projects/     Properties (config por marca/proyecto)
CAPA 2 — agents/       Content production agents (apps)
CAPA 1 — core/         Control plane (kernel genérico)
```

## Properties

| Property | Status | Fase |
|---|---|---|
| **AI Brief LATAM** | Active | Fase 1 — Manual MVP |
| Crypto Brief LATAM | Pending | Fase 5 |
| Startup Radar LATAM | Pending | Fase 6 |

## Estructura del repo

```
project-autopilot/
├── MASTER_PLAN.md              # Plan estratégico v2
├── core/                       # Capa 1 — Control plane
├── agents/                     # Capa 2 — Content production agents
│   ├── source_monitor/
│   ├── signal_scorer/
│   ├── editorial/
│   ├── fact_checker/
│   ├── content_composer/
│   ├── compliance/
│   ├── financial_risk/
│   ├── publisher/
│   ├── analytics/
│   └── learning/
├── projects/                   # Capa 3 — Properties
│   ├── ai-brief-latam/         # Priority #1 (active)
│   ├── crypto-brief-latam/     # Priority #2 (pending)
│   └── startup-radar-latam/    # Priority #3 (pending)
└── docs/                       # Project state, runbooks, standards
    └── PROJECT_STATE.md        # Living document — leer primero
```

## Documentos clave

- **`docs/PROJECT_STATE.md`** — Estado actual del proyecto. Leer siempre primero.
- **`MASTER_PLAN.md`** — Plan estratégico completo: arquitectura, fases, catálogo de agentes, playbook.
- **`.cursorrules`** — Reglas para Cursor/Claude Code al trabajar en este repo.

## Estado actual

**Fase 1 — Manual MVP de AI Brief LATAM.** Producir 12-18 piezas a mano, documentar cada una, identificar qué automatizar. Ver `MASTER_PLAN.md` sección 7 para detalle de todas las fases.
