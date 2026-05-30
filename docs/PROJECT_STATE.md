# PROJECT_STATE.md — Project Autopilot

**Last updated:** 2026-05-08
**Active phase:** Fase 3-4 — Agents MVP operativos + Manual MVP en curso
**Current status:** 9/9 MVP agents implementados (98 tests). Pipeline end-to-end funcional. 6 pieces produced (0 published). Next: usar pipeline para producir contenido + crear Instagram account.

---

## Done ✅

### Agent system — 9/9 MVP complete (2026-05-08)
- **Source Monitor** (34 tests) — 12 fuentes RSS + Anthropic Blog scraping, dedup 30d, scoring heurístico 6 dimensiones (90 keywords), CLI `scan`
- **Signal Scorer** (12 tests) — LLM scoring (Opus 4) con rubric 8 categorías del Anexo B, clasificación strong/consider/discard, CLI `score`
- **Editorial** (11 tests) — Genera briefs Smart Brevity con ángulo LATAM, hook framework, fact-check items, CLI `brief`
- **Fact-Checker** (9 tests) — Verifica claims con 4 niveles de severidad, verdicts pass/pass_with_edits/needs_review/fail, CLI `check`
- **Content Composer** (7 tests) — Genera carousel (5-7 slides) + caption + newsletter section + reel script, CLI `compose`
- **Compliance** (9 tests) — Revisa Meta rules + brand voice + forbidden patterns, verdicts approved/warnings/blocked, CLI `comply`
- **Human Approval** (6 tests) — Interactive CLI + auto-approve mode, decision recording, CLI `approve`
- **Publisher** (5 tests) — Export files listos para Canva/Buffer/Beehiiv, CLI `publish`
- **Analytics** (5 tests) — Pipeline metrics + API costs + weekly reports + recommendations, CLI `analytics`
- **Run-all command** — `python autopilot.py run-all -p dinero-ia` ejecuta el pipeline completo

### Pipeline end-to-end
```
scan → score → brief → check → compose → comply → approve → publish → analytics
```
- Total pipeline run: ~2 min, ~$1-2 API cost (Opus 4)
- Output: publish-ready files (caption.txt, slides.md, newsletter.md, reel_script.md)

### Configuration
- `.env` con `ANTHROPIC_API_KEY` (Opus 4)
- 12 RSS sources activas + Anthropic Blog scraping
- 90 keywords curados (51 high-priority, 39 normal) across 5 categorías
- Brand voice, compliance rules, risk profile configurados

### Architectural setup
- Repos split: project-autopilot (active) + mira (frozen snapshot)
- v2 architecture bootstrap: core/, agents/, projects/
- README, ARCHITECTURE, DAILY_OPERATIONS, .cursorrules, .gitignore, .env.example v2
- PROJECT_STATE.md tracker
- GitHub CLI installed and authenticated
- Both repos pushed to https://github.com/manupesqueira-ship-it/

### Research (3 sessions, 19 web searches)
- Session #1: Format/voice US — `projects/dinero-ia/research/2026-05-07_format-and-voice-research.md`
- Session #2: LATAM-specific — `projects/dinero-ia/research/2026-05-07_latam-specific-research.md`
- Session #3: Production stack — `projects/dinero-ia/research/2026-05-07_production-stack-research.md`

### Content production assets
- `brand_voice.md` con voz/acento sections (Mexican neutral, blacklist explícita)
- 4 templates reusables: brief, video_script, caption, newsletter_section
- `tagline_candidates.md` (deferred hasta naming)

### Pieces produced (6 total, 0 published)
- **Piece #001:** Anthropic Wall Street + Claude Opus 4.7 (hook: cifra)
- **Piece #002:** Corgi insurtech $1.3B unicornio (hook: pregunta)
- **Piece #003:** Google mata Project Mariner (hook: contrarian)
- **Piece #004:** Anthropic x SpaceX 220K GPUs (hook: cita irónica)
- **Piece #005:** Uber x OpenAI drivers assistant (hook: predicción)
- **Piece #006:** Claude Code vs Codex guerra coding (hook: benchmark)

### Production stack LOCKED
- Camera: FACELESS (texto + B-roll, no face, no AI avatar)
- Voice: Manuel (es-MX neutral)
- Editor: Canva Pro
- Cost MVP: $15/mo + ~$1-2/day API (Opus 4)

### Operational accounts
- ✅ Inoreader (244 items unread en folder "AI Brief LATAM")
- ✅ Beehiiv 14d trial (aibrieflatam.beehiiv.com) — revisar 2026-05-21
- ✅ Buffer Free
- ✅ Canva Pro 30d trial — CANCELAR DAY 28 (~2026-06-04) si no se queda
- ✅ Anthropic API key configurada (.env)
- ❌ Instagram NOT created (deferred per directive)
- ❌ Domains NOT purchased

---

## In Progress 🔄
- (nothing actively in progress)

---

## Pending / Next Up ⏭️

**Inmediato (próxima sesión):**
1. Correr pipeline completo con contenido fresco: `python autopilot.py run-all -p dinero-ia`
2. Revisar output, iterar scoring/compliance thresholds si hace falta
3. Lock naming + create Instagram Business account
4. Publicar primeras 3 piezas en IG (manual, usando files exportados por Publisher)
5. Compilar primer newsletter desde newsletter sections generadas

**Mediano plazo:**
6. Refinar voz/formato basado en métricas reales post-publicación
7. Calibrar keyword weights basado en qué items rankean bien
8. Conectar Inoreader API cuando el pipeline demuestre valor (M3/M4 del source_monitor)
9. Research benchmarks Money property + Crisis property

**Fase 5+ (cuando pipeline está calibrado):**
10. Financial Risk Agent (solo para crypto-brief-latam)
11. Activar segunda property (crypto-brief-latam) — solo config, sin tocar código de agents
12. Considerar legal entity (LLC vs persona física) cuando $1k+/mo

---

## Open decisions / unknowns 🤔
- Naming definitivo de las 3 properties (deferred hasta MVP valida)
- Instagram handles
- Email separado por property vs personal
- Beehiiv URL final (cuando naming locked)
- Scheduler post-Fase 1: Buffer vs Later vs Metricool vs Canva Content Planner nativo
- Visual generation IA: si llega a necesitarse (Midjourney/Recraft/gpt-image-2)

---

## Key references & context 📚

### CLI quick reference
```bash
# Full pipeline (auto-approve mode)
python autopilot.py run-all -p dinero-ia --auto-approve

# Individual steps
python autopilot.py scan -p dinero-ia
python autopilot.py score -p dinero-ia --max-items 10
python autopilot.py brief -p dinero-ia --items 3
python autopilot.py check -p dinero-ia
python autopilot.py compose -p dinero-ia
python autopilot.py comply -p dinero-ia
python autopilot.py approve -p dinero-ia     # interactive
python autopilot.py publish -p dinero-ia
python autopilot.py analytics -p dinero-ia
```

### Documents to consult (en orden de prioridad para nueva sesión)
1. `PROJECT_STATE.md` (este archivo)
2. `MASTER_PLAN.md` (root) — strategic plan v2
3. `agents/README.md` — checklist de agents y status
4. `docs/PRODUCTION_STACK.md` — decisiones lockeadas de producción
5. `projects/dinero-ia/brand_voice.md` — voz + acento + reglas duras

### Reference brands (NO copiar, solo lógica estratégica)
- **AI property US:** The Rundown AI (436K IG, 2M+ newsletter), Superhuman AI (1.5M newsletter)
- **AI/Tech LATAM:** Ecosistema Startup (12K IG), Startupeable (27K IG), Digital Brain (60K newsletter)

### Realistic LATAM benchmarks
- 1K = base creíble
- 5K = niche success
- 12-30K = top tier (target 12-18 meses)

---

## Meta-principios establecidos

1. **Research strategic, test operational.** Decisiones brand-defining merecen research; tooling se decide y se itera.
2. **Sequence rule.** Sistema → contenido → refinar → brand/handles. NUNCA al revés.
3. **No sycophancy.** Pushback honesto > eco con vocabulario.
4. **Hard constraint "no AI look".** AI como ASISTENTE OK; AI como GENERADOR primario NO.
5. **Naming = LAST decision.** Hasta que el sistema produzca contenido validable, no se locka branding.
6. **No construir agent N+1 hasta que la operación demuestre que hace falta.**
