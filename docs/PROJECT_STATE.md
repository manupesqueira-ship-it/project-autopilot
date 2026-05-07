# PROJECT_STATE.md — Project Autopilot

**Last updated:** 2026-05-07 (fin del día)
**Active phase:** Fase 1 — Manual MVP de AI Brief LATAM
**Current status:** Piece #1 produced V2 (no publicada). Production stack LOCKED. Research completado en 3 sesiones (19 web searches). Próximo: piece #2 con stack en uso real.

---

## Done ✅

### Architectural setup
- Repos split: project-autopilot (active) + mira (frozen snapshot)
- v2 architecture bootstrap: core/, agents/, projects/
- README, ARCHITECTURE, DAILY_OPERATIONS, .cursorrules, .gitignore, .env.example v2
- PROJECT_STATE.md tracker
- Backups: tag pre-split-backup-20260506-1924, branch backup-pre-cleanup-20260506, zip C:\Users\manup\backups\
- GitHub CLI installed and authenticated
- Both repos pushed to https://github.com/manupesqueira-ship-it/

### Research (3 sessions, 19 web searches)
- Session #1: Format/voice US — `projects/ai-brief-latam/research/2026-05-07_format-and-voice-research.md`
- Session #2: LATAM-specific — `projects/ai-brief-latam/research/2026-05-07_latam-specific-research.md`
- Session #3: Production stack — `projects/ai-brief-latam/research/2026-05-07_production-stack-research.md`

### Content production assets
- `brand_voice.md` con voz/acento sections (Mexican neutral, blacklist explícita)
- 4 templates reusables: brief, video_script, caption, newsletter_section
- `tagline_candidates.md` (deferred hasta naming)

### Pieces produced
- **Piece #001:** Anthropic + Wall Street + Claude Opus 4.7
  - V2 lista, NOT published
  - Path: `projects/ai-brief-latam/manual-mvp/pieces/2026-05-07_anthropic-wall-street-claude-opus-4-7.md`
  - Includes: brief, video script (30s), caption (142 chars), newsletter section (350 words), production log

### Production stack LOCKED
- `docs/PRODUCTION_STACK.md` con decisiones data-backed
- Camera: FACELESS (texto + B-roll, no face, no AI avatar)
- Voice: Manuel (es-MX neutral)
- Editor: Canva Pro
- Cost MVP: $15/mo

### Curaduría piece #2
- 31 artículos AI-relevantes extraídos de Inoreader hoy
- Top recomendación: **Insurance startup Corgi $1.3B valuation 4 months after Series A** (TechCrunch)
- Razones: cifra brutal, no-Anthropic, continúa tema agentes verticales, LATAM angle insurtech (Pomelo, 123Seguro, Aon)
- Plan B: Google shuts down Project Mariner (The Verge) — contrarian narrative

### Operational accounts
- ✅ Inoreader (244 items unread en folder "AI Breif LATAM" [typo a corregir])
- ✅ Beehiiv 14d trial (URL placeholder aibrieflatam.beehiiv.com) — revisar 2026-05-21
- ✅ Buffer Free
- ✅ Canva Pro 30d trial — ⚠️ CANCELAR DAY 28 (≈2026-06-04) si no se queda
- ❌ Instagram NOT created (deferred per directive)
- ❌ Domains NOT purchased

### Strategic decisions LOCKED
1. 3 properties (independent brands, no parent brand): AI brief #1, Money brief #2, Crisis brief #3
2. Sequence rule: build → sample content → refine → THEN brand/handles
3. Spanish neutral con blacklist explícita
4. Manual MVP first (3-4 semanas) antes de cualquier agent
5. Newsletter (Beehiiv) = activo central; IG es UN canal entre varios
6. Voice framework: Smart Brevity (Axios) + casual Morning Brew + LATAM emojis
7. Production stack: faceless + voz humana + Canva Pro
8. Constraint duro: "no debe verse con IA" filtra todas las decisiones de tools

---

## In Progress 🔄
- (overnight: si se corre el prompt overnight, audit de core/docs + research competitivo)

---

## Pending / Next Up ⏭️

**Inmediato (próxima sesión):**
1. Producir piece #2 (Corgi insurtech) end-to-end con stack en uso real
2. Validar tiempos de grabación de voz + ensamble Canva
3. Producir piece #3 (try formato carrusel para A/B vs Reel)

**Mediano plazo:**
4. Refinar voz/formato basado en pieces #2 y #3
5. THEN: lock tentative naming + create Instagram Business account
6. THEN: publicar primeras piezas
7. Audit completo de core/ y docs/ (clasificar v2 vs archivar) — programado para overnight
8. Research benchmarks Money property + Crisis property (todavía no tocadas)

**Fase 2+ (cuando MVP valida):**
9. Codear primeros agentes (source_monitor, signal_scorer)
10. Automatizar pipeline de discovery
11. Considerar legal entity (LLC vs persona física) cuando $1k+/mo

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

### Reference brands (NO copiar, solo lógica estratégica)
- **AI property US:** The Rundown AI (436K IG, 2M+ newsletter), Superhuman AI (1.5M newsletter), The Neuron (27K IG, 700K newsletter)
- **AI/Tech LATAM:** Ecosistema Startup (12K IG, 10K+ newsletter), Startupeable (27K IG, 50K newsletter), Digital Brain (60K newsletter 42% open), DotCSV (104K IG, Spain)
- **Crypto/Money:** 0x100x (premium dark institutional, funnel free IG → newsletter → $100/mo premium)
- **Global crisis:** Tangle, Semafor, Morning Brew Global, Chartr

### Realistic LATAM benchmarks
- 1K = base creíble
- 5K = niche success
- 12-30K = top tier (target 12-18 meses)
- 100K+ = exceptional

### Documents to consult (en orden de prioridad para nueva sesión)
1. `PROJECT_STATE.md` (este archivo)
2. `MASTER_PLAN.md` (root) — strategic plan v2
3. `docs/PRODUCTION_STACK.md` — decisiones lockeadas de producción
4. `docs/SESSION_LOGS/2026-05-07_full-day.md` — captura completa del día
5. `projects/ai-brief-latam/brand_voice.md` — voz + acento + reglas duras
6. `projects/ai-brief-latam/research/` — 3 archivos de research

---

## Meta-principios establecidos

1. **Research strategic, test operational:** Decisiones brand-defining y de algoritmo merecen research; tooling operacional se decide y se itera.
2. **Sequence rule:** Sistema → contenido sample → refinar → brand/handles. NUNCA al revés.
3. **No sycophancy:** Pushback honesto > eco con vocabulario. Manuel prefiere disagreement constructivo.
4. **Hard constraint "no AI look":** Filtra todas las decisiones de tools. AI como ASISTENTE OK; AI como GENERADOR primario NO.
5. **Naming = LAST decision:** Hasta que el sistema produzca contenido validable, no se locka nada de branding.
