# Roadmap — AI How-To LATAM (v4, 2026-05-18)

> **Cambios v4 vs v3** (ADR-016 pivot estratégico):
> - **NUEVO: Fase -1 "Validación Manual"** antes de cualquier ejecución técnica. Manuel publica 5-10 piezas manualmente con prompts directos en Claude.ai para validar voz/nicho antes de comprometer recursos.
> - **Pivot de nicho:** AI News brief → AI How-To práctico (Critical Review identifica saturación en news brief español).
> - **Pivot de voz:** Anti-hype sobrio → Viral hype calibrado (hooks emocionales + body sobrio Smart Brevity).
> - **Eliminada Fase 5 multi-property:** convicción full en UNA idea hasta validar. Crypto Brief / Startup Radar diferidos sin compromiso.
> - **Decision point post-Fase -1:** Build vs Buy (Blotato AI cubre 70% del pipeline a $29-97/mo).
>
> **Nombre del proyecto:** sigue como "AI Brief LATAM" en archivos hasta confirmación de nuevo nombre. Cambio físico de carpeta deferred.

---

## Fase -1 — Validación Manual (Semana 1, NUEVA)

**Objetivo:** Validar la voz/nicho/ángulo con audiencia real antes de invertir en pipeline técnico. **Si esto no funciona, NADA del plan posterior tiene sentido.**

### Por qué existe esta fase

El Critical Review (`docs/CRITICAL_REVIEW.md`) identificó que estábamos sobre-diseñando antes de validar. Esta fase corrige el orden: producto-mercado FIRST, producto-fábrica DESPUÉS.

### Alcance

- 5-10 piezas publicadas manualmente (no automatizado)
- Cuenta personal de Manuel o cuenta de prueba (no AI Brief LATAM brand todavía)
- Mix de tópicos how-to IA + medir engagement por pieza
- **Sin pipeline n8n.** Manuel usa Claude.ai directo + DALL-E playground o Canva.

### Tareas

1. **Manuel:** definir 5-10 tópicos how-to que quiere probar (ej: "Cómo usar Claude para reducir tu tiempo en X tarea", "5 prompts que cualquier manager LATAM debería tener")
2. **Manuel + Claude (chat):** generar cada brief con prompt directo (siguiendo `docs/MANUAL_OPERATIONS.md`)
3. **Manuel:** generar visuales en DALL-E playground siguiendo `docs/POST_STANDARD.md` §7
4. **Manuel:** publicar en cuenta personal o test cada 1-2 días durante 1-2 semanas
5. **Track engagement** en un .md simple: views, saves, comments, shares por pieza
6. **Decision criteria:**
   - **Funciona:** >2% engagement promedio (saves+comments)/views, ≥1 comentario sustantivo por pieza → seguir a Build vs Buy decision
   - **No funciona:** <1% engagement promedio, comentarios genéricos → iterar voz, considerar pivot de nicho, **NO construir pipeline**

### Definition of Done Fase -1

- [ ] 5-10 piezas publicadas
- [ ] Engagement medible (mejor o peor que 2%)
- [ ] Manuel tiene **convicción informada** sobre seguir con AI How-To LATAM o pivot
- [ ] Decisión "Build vs Buy" tomada (Blotato evaluation paralelo)

### Bloquea Fase 0

**Sí.** No avanzar a smoke test técnico si Fase -1 no valida la voz.

---

## Decision Point post-Fase -1

Después de Fase -1, Manuel + Claude evalúan:

```
                    ┌─ Pivot nicho (otra propuesta)
                    │
   Voz NO funciona ─┼─ Iterar voz + retest 1 ronda más
                    │
                    └─ Pausar proyecto, evaluar otra cosa
   ───────────────────────────────────────────────────
                    ┌─ Buy → Blotato AI 30 días
                    │  → si funciona: full Blotato
                    │  → si no: vuelve a Build
   Voz SÍ funciona ─┤
                    └─ Build → Fase 0 smoke test
                       → Fase 1 pipeline completo
```

---

## Fase 0 — Smoke test (Semana 2-3, condicional)

**Objetivo:** Validar que la cadena LLM (scoring + editorial) llega a Telegram con un brief decente. NO publica, NO genera imágenes. Solo prueba el corazón del pipeline antes de invertir en Fase 1.

### Alcance

- 1 fuente RSS (OpenAI Blog)
- A2 Signal Scorer (Sonnet 4.5) + A3 Editorial (Opus 4)
- Output: brief en formato Smart Brevity llegando a Telegram en <2 min
- Sin Fact-Check, sin Carousel, sin Compliance, sin Publishing
- Trigger manual (no cron)

### Tareas

1. **Manuel: crear Telegram bot vía @BotFather** (~5 min)
2. **Manuel: sacar Anthropic API key** + cargar $10-20 USD billing (~5 min)
3. **Manuel: importar `infra/n8n/fase0.json` a n8n cloud trial** (~5 min)
4. **Manuel: pegar credenciales en el workflow** (~5 min)
5. **Manuel: Execute Workflow → recibir brief en Telegram** (~2 min)
6. **Manuel + Claude (chat): evaluar calidad del brief** — ¿voz, hook, ángulo LATAM cumplen estándar?
7. Iterar prompts A2/A3 si la calidad baja del estándar (1-3 iteraciones esperadas)
8. **Definition of Done Fase 0:** ≥3 briefs decentes en Telegram en una semana

### Bloqueante para Fase 1

Si Fase 0 no entrega briefs publicables, NO avanzar a Fase 1. El problema está en prompts o señal de fuentes, no en automatización.

---

## Fase 1 — Pipeline texto + carousels + newsletter (Semanas 2-4)

**Objetivo:** Pipeline completo automatizado que produce y publica 1 pieza/día (carousel IG + TikTok caption + sección newsletter), aprobada por humano via Telegram.

### Alcance

- **Agentes activos:** A1 (Source Monitor), A1.5 (Binary Filter), A2 (Scorer), A3 (Editorial), A4 (Fact-Checker), A5 (Visual Director), A7 (Copy Composer), A8a (Visual Generator gpt-image-2), A8d (Newsletter Composer), A9 (Compliance), A10 (Publisher Upload-Post), A11 (Editor LLM HITL)
- **Output diario:** 1 carousel IG (5-7 slides) + 1 caption TikTok paralelo + 1 sección newsletter Beehiiv
- Sin video, sin audio (Fase 2)
- **HITL bidireccional Telegram** — Manuel aprueba/edita/rechaza
- Horario único: ~8 AM CDMX (post + newsletter envío simultáneo)

### Fuentes (12 confirmadas + 3 propuestas para activar)

Activas confirmadas RSS:
- OpenAI Blog, Anthropic, Google AI (oficial)
- TechCrunch AI, The Verge AI, Ars Technica, Wired, Fortune (anglo)
- Latent Space (newsletter), Hacker News (community)
- Contxto, LatamList (LATAM)

Propuestas verificadas pendientes activar (OPEN_QUESTIONS F):
- Xataka IA, Genbeta IA, Hipertextual (ES — peninsular, filtrar con A1.5)
- La Nación Tecnología (AR — único LATAM nativo con RSS funcional)
- Startupeable (newsletter LATAM)

### Tareas

#### Semana 2 — Infrastructure

1. **Manuel: aplicar runbook `hostinger-vps-n8n-setup.md`** (~60-90 min) — paso 1-7
2. **Manuel: crear cuenta Supabase + aplicar migration `infra/supabase/migrations/001_initial.sql`** (~30 min)
3. **Manuel: crear cuenta Upload-Post + conectar IG + TikTok via OAuth** (~30 min)
4. **Claude (chat): migrar fase0.json al VPS + extender a Fase 1 workflow** (~2-4 sesiones)
5. **Claude: instalar `n8n-nodes-upload-post` community node en el VPS** (1 click n8n UI)
6. **Manuel: registrar dominio + configurar SSL via Let's Encrypt** (~15 min, opcional)

#### Semana 3 — Pipeline completo

7. **Implementar A1**: Schedule trigger 1× día + Split In Batches × 12 fuentes RSS + dedup Supabase upsert
8. **Implementar A1.5**: Binary filter pre-scoring (Sonnet 4.5 cheap)
9. **Implementar A2**: scoring rúbrica 8 categorías + sort + split top vs shortlist
10. **Implementar A3**: editorial brief Smart Brevity con few-shot examples (usar briefs de Fase 0 como seeds)
11. **Implementar A4**: AI Agent con web_search Tool (Anthropic native)
12. **Implementar A5 + A8a**: visual direction → gpt-image-2 API loop
13. **Implementar A7**: copy composer (carousel + caption + tiktok + reel script placeholder)
14. **Implementar A8d**: newsletter composer (subject + intro + top + quick hits)
15. **Implementar A9**: compliance check 15 reglas con retry loop

#### Semana 4 — HITL + Publishing

16. **Implementar Telegram HITL bidireccional**: Send Message + inline keyboard + Telegram Trigger + parse callback
17. **Implementar A11 Editor LLM**: aplicar feedback parcial sin regenerar
18. **Implementar A10 Publisher**: Upload-Post node con carousel IG + TikTok crosspost
19. **Configurar Beehiiv API**: crear publicación, configurar from address, footer CAN-SPAM
20. **Test end-to-end**: primera pieza completa publicada (carousel + TikTok + newsletter)
21. **Correr 7 días**: 7 piezas publicadas con HITL aprobando cada una

### Definition of Done Fase 1

- [ ] 7 piezas publicadas en 7 días (1/día consistente)
- [ ] 0 errores de fact-check post-publicación
- [ ] 0 violaciones de compliance detectadas por audiencia
- [ ] Workflow estable >95% (max 1 failure por semana)
- [ ] Costo Anthropic + OpenAI + Upload-Post dentro de $30-50/mo
- [ ] Newsletter Beehiiv enviada cada día con open rate >25%

---

## Fase 2 — Reels con voice clone (Semanas 5-7)

**Objetivo:** Sumar reels al mix de contenido (carousel + reel + newsletter).

### Pre-requisitos Fase 2

- [ ] **Manuel graba 20-30 min de voz** siguiendo `docs/voice-clone/recording-script.md`
- [ ] **Cuenta ElevenLabs Creator** ($22/mo activada)
- [ ] **Voice clone training completado** (~10 min después de upload)
- [ ] **Fase 1 estable 14 días** sin intervención manual extra

### Alcance

- **Agentes activos nuevos:** A6 (Audio Director), A8b (Video Generator Seedance), A8c (Audio Generator ElevenLabs)
- **Output:** 1 carousel + 1 reel por día (alternancia o decisión por pieza según `formato_recomendado` del brief)
- Voice clone 100% (NO TTS genérico)
- Seedance anima keyframes generados por gpt-image-2

### Tareas

1. Configurar ElevenLabs voice clone (post-grabación)
2. Implementar A6 Audio Director (SSML + pacing instructions)
3. Implementar A8c ElevenLabs API (TTS con voice clone)
4. Implementar A8b Seedance 2.0 (imagen→video con voice como audio track)
5. Integrar A8a (keyframes) + A8b (video) + A8c (audio) en el workflow
6. Test: primer reel publicado vía Upload-Post (también soporta video)
7. Calibrar voice_settings (stability + similarity_boost + style) en primeras 5 piezas
8. Decidir mix carousel/reel según engagement de primeras 2 semanas

### Definition of Done Fase 2

- [ ] 14 reels publicados en 2 semanas
- [ ] Voice clone con calidad aceptable (>80% naturalidad percibida en blind test)
- [ ] Engagement reel ≥ carousel (medible por save_rate + watch_through_rate)

---

## Fase 3 — Newsletter scale + landing (Semanas 8-10)

**Objetivo:** Pasar la newsletter de "anexa al pipeline" a "activo principal de audiencia propia". Crear landing para captura orgánica.

> **Nota:** A8d Newsletter Composer ya corre desde Fase 1. Fase 3 NO la activa por primera vez — la **escala** con landing + captura propia + Beehiiv Scale plan.

### Alcance

- Landing page con captura email (Lovable.dev o alternativa)
- CTA newsletter en captions IG + TikTok cada pieza
- Welcome sequence Beehiiv (3 emails) para nuevos suscriptores
- Migrar Beehiiv Free → Scale ($49/mo) cuando llegue a 2,500 subs
- Implementar A11.5 Analytics (cross-canal: IG, TikTok, newsletter open/click)

### Tareas

1. Diseñar landing con value prop específico (3 min/día, LATAM, sin hype)
2. Crear landing en Lovable.dev (~1 día)
3. Conectar landing → Beehiiv API para suscripción automática
4. Welcome sequence: email 1 (intro) + email 2 (top 5 piezas históricas) + email 3 (encuesta tema favorito)
5. Agregar CTA newsletter en A7 Copy Composer (caption IG + TikTok)
6. Implementar A11.5 Analytics — cron diario fetch métricas de Upload-Post + Beehiiv → Supabase
7. Dashboard simple en Supabase view o Metabase (opcional)

### Definition of Done Fase 3

- [ ] 800 suscriptores newsletter en 30 días post-launch
- [ ] Landing con conversion rate ≥3% (sesiones → suscripción)
- [ ] Welcome sequence con open rate ≥50%
- [ ] Newsletter daily open rate sostenido >30%

---

## Fase 4 — Podcast (Meses 3+)

**Objetivo:** Agregar formato podcast para audiencias que prefieren audio. Distribución via Spotify for Podcasters.

### Alcance

- Episodio semanal de 5-10 min (Smart Brevity audio = el top story de la semana)
- Voz clonada de Manuel (ya activa desde Fase 2)
- Distribución Spotify + Apple Podcasts (free)
- Cross-promotion en IG/TikTok/Newsletter

### Tareas

1. Definir formato episodio (duración, estructura, música de intro/outro)
2. Extender A8c para generar episodios largos (no solo voiceover de 30s reels)
3. Configurar Spotify for Podcasters
4. Crear artwork con gpt-image-2 (consistent con visual standard)
5. Implementar workflow publicación semanal (cron lunes 6 AM)
6. Cross-promotion en otros canales

### Definition of Done Fase 4

- [ ] 10 episodios publicados consecutivos
- [ ] 50+ plays acumulados (early stage acceptable)
- [ ] Distribución automática via n8n workflow

---

## Fases futuras (no committed — solo después de validar Fase 1+2+3)

### Fase 5 — Monetización (Mes 4+)

Solo se evalúa después de >5K subs/followers reales en AI How-To LATAM.

- Sponsored sections en newsletter
- Affiliate links en piezas relevantes (herramientas IA que recomendamos)
- Pro tier ($X/mo) con contenido extra
- Cursos / workshops específicos

### Fase 6 — Consumer product (post-revenue validation)

Si la audiencia llega a 10K+ newsletter / 5K+ IG y hay revenue probado, evaluar producto: app móvil, Chrome extension, o herramienta SaaS para audiencia.

### Multi-property (DIFERIDO sin compromiso por ADR-016)

**No considerar hasta que AI How-To LATAM tenga >5K subs/followers reales.** Multi-property prematuro contradice north star "convicción full en una idea". Cuando se considere eventualmente, las opciones serán: Crypto LATAM, Startup Radar LATAM, o nicho que se valide en Deep Research.

---

## Timeline visual

```
Semana    1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
Fase -1   ▓▓                                          ← Validación Manual
Fase 0       ▓▓                                       ← solo si voz funciona
Fase 1          ▓▓▓▓▓▓▓▓                              ← solo si Fase 0 entrega
Fase 2                   ▓▓▓▓▓▓                       ← solo si Fase 1 valida
Fase 3                          ▓▓▓▓▓▓▓               ← scale newsletter
Fase 4                                  ▓▓▓▓▓▓ ...    ← podcast
Fase 5+                                              (revenue + product)
```

Las fases siguientes son **condicionales** sobre el éxito de la anterior. No comprometemos Fase 1 hasta que Fase 0 entregue briefs decentes. No comprometemos Fase 2 hasta que Fase 1 entregue 7 días estables. Etc.

## Métricas de éxito acumuladas

| Métrica | 30 días | 60 días | 90 días | 180 días |
|---------|---------|---------|---------|---------|
| Followers IG | 300 | 1,200 | 3,500 | 8,000 |
| Newsletter subs | 100 | 400 | 1,200 | 3,500 |
| Engagement IG >3% | Goal | 5+ piezas/mes | 10+ piezas/mes | Consistente |
| Newsletter open rate | >35% | >35% | >32% | >30% |
| Fact-check errors públicos | 0 | 0 | 0 | 0 |
| Compliance violations | 0 | 0 | 0 | 0 |
| Costo total mensual | $7-10 (Fase 0+) | $50-70 (Fase 1) | $85-115 (Fase 2) | $100-180 (Fase 3) |
| Revenue test | - | - | Primer test | Sponsored section |

> **Nota:** estos targets son conservadores. Si la voz/ángulo resuena bien, los benchmarks LATAM real-world (Ecosistema Startup 12K, Startupeable 27K en 12-18 meses) sugieren que 8K en 6 meses es alcanzable. Si no resuena, ajustar buyer persona (OPEN_QUESTIONS J).
