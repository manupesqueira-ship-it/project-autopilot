# Project State — Living Document

> Living document. Update after every working session.
> First thing to read at the start of any new session.

**Last updated:** 2026-05-07
**Active phase:** Fase 1 — Manual MVP de AI Brief LATAM (per MASTER_PLAN.md)
**Current status:** Piece #1 produced (V2, not published). Research completed (format/voice + LATAM-specific). Brand voice, templates, and tagline candidates in place. Next: produce pieces #2 and #3.

---

## Done ✅

### Repo & Infrastructure
- Split MIRA repo into two: `mira` (frozen snapshot) + `project-autopilot` (active dev)
- Bootstrap v2 architecture (core/, agents/, projects/, docs/)
- Both repos pushed to GitHub (manupesqueira-ship-it/{mira, project-autopilot})
- MASTER_PLAN.md v2 in repo
- README.md updated for v2
- .cursorrules updated for v2 three-layer architecture
- .gitignore updated for v2 (design files, media assets, analytics exports)
- PROJECT_STATE.md created as living state tracker
- DAILY_OPERATIONS.md created (Fase 1 playbook)
- ARCHITECTURE.md created (3-layer reference)
- .env.example created (template for future API keys)
- GitHub CLI (gh) installed and authenticated
- Backup tag pre-split-backup-20260506-1924 + branch backup-pre-cleanup-20260506 in mira repo
- Backup zip at C:\Users\manup\backups\mira-pre-split-20260506.zip

### Research completed (2026-05-07)
- Format/voice research: Smart Brevity framework, Reels length data 2026, caption length, top AI accounts US
  → `projects/ai-brief-latam/research/2026-05-07_format-and-voice-research.md`
- LATAM-specific research: Ecosistema Startup, Startupeable, DotCSV, Nicolas Abril, Digital Brain, IA al Día
  → `projects/ai-brief-latam/research/2026-05-07_latam-specific-research.md`

### Content production assets
- `brand_voice.md` — data-backed, Smart Brevity + LATAM hooks + idioma blacklist + benchmarks
- 4 reusable templates in `projects/ai-brief-latam/templates/`:
  - `brief_template.md` (internal editorial brief)
  - `video_script_template.md` (Reels 25-35s)
  - `caption_template.md` (<150 chars)
  - `newsletter_section_template.md` (250-400 words Smart Brevity)
- `tagline_candidates.md` — 5 data-backed candidates (deferred until naming locked)

### Pieces produced
- **Piece #001:** Anthropic Wall Street + Claude Opus 4.7 (V2)
  → `projects/ai-brief-latam/manual-mvp/pieces/2026-05-07_anthropic-wall-street-claude-opus-4-7.md`
  → Status: produced, NOT published (no Instagram account yet)
  → Includes: brief, video script (30s), caption (142 chars), newsletter section (350 words), production log

### External operational accounts
- Inoreader (Google sign-in, 240+ feeds, partial AI Brief LATAM folder)
- Beehiiv (14-day trial active, URL placeholder: aibrieflatam.beehiiv.com)
- Buffer (free tier)
- Canva Pro (30-day trial — REMINDER: cancel before day 28 if not keeping)

### Strategic decisions locked
- 3 properties (independent brands, no parent brand): AI brief video-first, Money/Crypto/Finanzas brief, Global crisis brief
- Priority order: AI #1, Money #2, Global #3
- Spanish neutral content (explicit blacklist: peninsular + extreme regional)
- Manual MVP first (3-4 weeks) before any agent automation
- Naming + Instagram handles DEFERRED until sample content exists
- Voice framework: Smart Brevity (Axios) + casual Morning Brew + LATAM emojis
- Newsletter (Beehiiv) is the central asset, IG is one acquisition channel

---

## In Progress 🔄
- (nothing actively in progress)

---

## Pending / Next Up ⏭️
1. Produce piece #2 of AI Brief LATAM manually end-to-end
2. Produce piece #3 (try carrusel format instead of Reel)
3. Document pieces #2 and #3 with full logs
4. Refine voice/format based on those 3 pieces
5. THEN: lock tentative naming + create Instagram Business account
6. THEN: publish first 3 pieces
7. Audit of core/ and docs/ — classify what serves v2 vs what gets archived

---

## Open decisions 🤔
- Naming for the 3 properties (deferred until pieces produced)
- Instagram handles (deferred)
- Whether to use a separate email per property for Instagram (vs personal)
- Final entity setup (LLC, persona física, etc. — defer until $1k+/mo revenue)
- Beehiiv URL "aibrieflatam" is placeholder, will rename when naming is locked
- Scheduler: Buffer vs Later vs Metricool (decide at end of Fase 1)
- Visual generation: Midjourney vs Recraft vs DALL-E vs Canva-only (decide after 5-10 pieces)

---

## Key references & context 📚

### Reference brands (NOT to copy, only strategic logic)
- **AI property (US benchmarks):** The Rundown AI (436K IG, 2M+ newsletter), Superhuman AI (1.5M newsletter, minimal IG), The Neuron (27K IG, 700K newsletter)
- **AI/Tech property (LATAM benchmarks):** Ecosistema Startup (12K IG, 10K+ newsletter), Startupeable (27K IG, 50K newsletter), Digital Brain (60K newsletter 42% open, minimal IG), DotCSV (104K IG, Spain)
- **Crypto/Money property:** 0x100x (Instagram) — premium, dark, institutional, funnel: free IG → newsletter → $100/mo premium research
- **Global property:** Tangle, Semafor, Morning Brew Global, Chartr

### LATAM benchmarks (realistic)
- 1K followers = base creíble
- 5K = niche success
- 12-30K = top tier (target for 12-18 months)
- 100K+ = exceptional (individual creators with years)

### Naming candidates considered (all deferred)
- AI: Pulso AI (taken), Radar AI (collision with RadarAI.top), Codigo Futuro AI, La Señal AI, AI Brief LATAM
- Money: Finanzas Sin Humo, Cripto Sin Humo, Capital 21, Future Money LATAM
- Global: Frontera Global, Mundo Crítico, Mapa Global

### Documents to consult
- `MASTER_PLAN.md` (root) — strategic plan v2, phases, agent catalog, annexes
- `ARCHITECTURE.md` (root) — 3-layer architecture reference
- `DAILY_OPERATIONS.md` (root) — Fase 1 daily workflow checklist
- `projects/ai-brief-latam/brand_voice.md` — data-backed voice rules
- `projects/ai-brief-latam/research/` — research files with sources
