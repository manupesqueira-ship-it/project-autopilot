# Content Production Agents — Capa 2

Estos agentes son aplicaciones que corren sobre el control plane (core/). Cada agente tiene una responsabilidad acotada y se modula por la config de la property que lo invoca.

Ver MASTER_PLAN.md sección 6 para el catálogo completo.

## Estado del MVP (9 agentes)
- [x] source_monitor (F3) — 34 tests, RSS + scraping + dedup + scoring + CLI
- [x] signal_scorer (F3) — 12 tests, LLM scoring via Claude API + CLI
- [x] editorial (F4) — 11 tests, LLM brief generation + markdown export + CLI
- [x] fact_checker (F4) — 9 tests, LLM claim verification + verdicts + CLI
- [x] content_composer (F4) — 7 tests, carousel + caption + newsletter + reel script + CLI
- [ ] editorial (F4)
- [ ] fact_checker (F4)
- [ ] content_composer (F4)
- [ ] compliance (F4)
- [ ] financial_risk (F5, solo crypto)
- [ ] publisher (F4)
- [ ] analytics (F5)
- [ ] learning (F5)
