# Roadmap — AI Brief LATAM (v2, 2026-05-10)

## Fase 1 — Pipeline texto + carousels (Semana 1-2)

**Objetivo:** Pipeline funcional que produce y publica 3 carousels de IG por día, aprobados por humano via Telegram.

### Alcance
- Agentes activos: A1 (Source Monitor), A2 (Signal Scorer), A3 (Editorial), A4 (Fact-Checker), A7 (Copy Composer), A8a (Visual Generator/gpt-image-2), A9 (Compliance), A10 (Publisher/Buffer)
- Output: 3 carousels Instagram/día (1080x1080, 4-8 slides cada uno)
- Crosspost automático a TikTok via Buffer
- Sin video, sin audio, sin podcast, sin newsletter
- Aprobación humana obligatoria via Telegram Bot antes de cada publicación
- Horarios de publicación: 8 AM, 1 PM, 7 PM CDMX

### Agentes inactivos en Fase 1
- A5 (Visual Director) — dirección visual simplificada dentro de A8a
- A6 (Audio Director) — no hay audio en Fase 1
- A8b (Video Generator) — no hay reels en Fase 1
- A8c (Audio Generator) — no hay voiceover en Fase 1
- A8d (Newsletter Generator) — no hay newsletter en Fase 1
- A11 (Analytics) — métricas manuales en Fase 1

### Tareas
0. **(Preliminar) Importar 5 templates base a n8n cloud y inspeccionar nodes JSON** antes de construir desde cero. Referencias del research `2026-05-11_n8n-templates-research.md`:
   - **#12533** (Maksudur Rahman) — Curate AI newsletter from RSS + LLM scoring + Slack HITL: el esqueleto más completo
   - **#6389** (Daniel Shashko) — Smart RSS + Baserow dedup persistente: único patrón de dedup serio
   - **#4399** (Davide Boizza) — Anthropic AI Agent Claude Sonnet 4/Opus 4 con web_search Tool: crítico para A4 fact-check
   - **#4028** (Juan Carlos Cavero) — Carousel TikTok+IG con gpt-image-1 (swap a gpt-image-2): patrón "1 img + N edits estilísticamente consistentes"
   - **#9472** (Yasser Sami) — LinkedIn posts con Telegram approval + feedback loop, **o #5773** (Femi Ad) — Social media posts con Telegram approval + Upload-Post multi-plataforma
   - Acceptance: cada template importado en una instance de prueba, JSON inspeccionado, lista de nodes y decisiones que sirven anotada en `docs/research/deep-research/n8n-templates-notes.md` (a crear).
1. Configurar n8n Cloud (o self-hosted en Hostinger)
2. Implementar A1: RSS feeds + deduplicación + keyword filter
3. Implementar A2: Claude Sonnet scoring con rúbrica de 8 categorías
4. Implementar A3: Claude Opus 4 editorial brief (Smart Brevity + LATAM angle)
5. Implementar A4: Claude Opus 4 fact-checking contra fuentes
6. Implementar A7: Claude Opus 4 caption + hashtags
7. Implementar A8a: gpt-image-2 carousel generation (1080x1080)
8. Implementar A9: Claude Opus 4 compliance check (Meta rules + brand voice)
9. Configurar Telegram Bot para aprobación human-in-the-loop
10. Configurar Buffer para auto-publish IG + TikTok
11. Test end-to-end: primer carousel publicado
12. Correr 7 días completos (21 carousels)

### Definition of Done
- [ ] 21 carousels publicados en una semana completa (3/día x 7 días)
- [ ] 0 errores de fact-check detectados post-publicación
- [ ] Workflow n8n estable sin intervención manual (excepto aprobación Telegram)
- [ ] Costos de API dentro del rango estimado ($75-170/mo)

---

## Fase 2 — Reels con voice clone (Semana 3-4)

**Objetivo:** Agregar reels con voz clonada al mix de contenido. Pasar de 100% carousels a mix carousel/reel.

### Alcance
- Grabar samples de voz de Manuel para ElevenLabs voice clone
- Activar A5 (Visual Director) y A6 (Audio Director)
- Activar A8b (Video Generator/Seedance 2.0) y A8c (Audio Generator/ElevenLabs)
- Output: mix de 2 carousels + 1 reel por día (o 1 carousel + 2 reels según performance)
- Transición gradual a auto-publish para contenido high-score (si Fase 1 completada sin errores por 14 días)

### Tareas
1. Grabar 30+ minutos de voz de Manuel para voice clone
2. Configurar ElevenLabs voice clone
3. Implementar A5: Visual Director (dirección visual detallada)
4. Implementar A6: Audio Director (guion de voiceover + dirección de reel)
5. Implementar A8b: Seedance 2.0 video generation
6. Implementar A8c: ElevenLabs TTS con voz clonada
7. Integrar video + audio en workflow n8n
8. Test end-to-end: primer reel publicado
9. Calibrar mix carousel/reel según engagement
10. Evaluar transición a auto-publish

### Definition of Done
- [ ] 14 reels publicados en dos semanas
- [ ] 0 errores de fact-check o compliance
- [ ] Mix carousel/reel funcionando (decisión automática por pieza)
- [ ] Voice clone con calidad aceptable (>80% naturalidad percibida)

---

## Fase 3 — Newsletter + landing (Semana 5-6)

**Objetivo:** Agregar canal de newsletter para capturar audiencia propia y reducir dependencia de algoritmos de redes sociales.

### Alcance
- Activar A8d (Newsletter Generator/Beehiiv)
- Crear landing page para captura de emails
- Brief extendido diario por email (curación de las 3 noticias del día)
- CTA en posts de IG/TikTok hacia newsletter

### Tareas
1. Configurar Beehiiv (free tier inicial)
2. Implementar A8d: generación de newsletter desde briefs del día
3. Diseñar template de email (brand consistent)
4. Crear landing page (Lovable.dev o alternativa)
5. Agregar CTA de newsletter en captions de IG/TikTok
6. Implementar A11 (Analytics) para tracking cross-canal
7. Configurar welcome sequence para nuevos suscriptores
8. Test end-to-end: primera newsletter enviada

### Definition of Done
- [ ] 30 newsletters enviadas (una por día durante 30 días)
- [ ] 100 suscriptores orgánicos
- [ ] Landing page funcional con formulario de captura
- [ ] Open rate >40% en newsletters

---

## Fase 4 — Podcast / audio (Mes 2+)

**Objetivo:** Agregar formato podcast para audiencias que prefieren audio. Distribución via Spotify for Podcasters.

### Alcance
- A8c genera episodios completos (5-10 min) con voz clonada
- Resumen semanal de las noticias top en formato podcast
- Distribución via Spotify for Podcasters
- Cross-promotion en IG/TikTok/Newsletter

### Tareas
1. Definir formato de episodio (duración, estructura, música)
2. Extender A8c para generar episodios largos (no solo voiceover de reels)
3. Configurar Spotify for Podcasters
4. Crear artwork de podcast (gpt-image-2 o Canva)
5. Implementar workflow de publicación semanal
6. Agregar cross-promotion en otros canales
7. Test end-to-end: primer episodio publicado

### Definition of Done
- [ ] 10 episodios publicados
- [ ] Primeros 50 plays acumulados
- [ ] Distribución automática via n8n workflow
- [ ] Cross-promotion implementada en IG/TikTok/Newsletter

---

## Timeline visual

```
Semana  1  2  3  4  5  6  7  8
Fase 1  ████████
Fase 2           ████████
Fase 3                    ████████
Fase 4                             ████████████...
```

## Métricas de éxito acumuladas

| Métrica | 30 días | 60 días | 90 días |
|---------|---------|---------|---------|
| Followers IG | 500 | 1,500 | 5,000 |
| Newsletter subs | - | 300 | 800 |
| Engagement >4% | 5+ piezas | 15+ piezas | Consistente |
| Fact-check errors | 0 | 0 | 0 |
| Revenue test | - | - | Primer test |
