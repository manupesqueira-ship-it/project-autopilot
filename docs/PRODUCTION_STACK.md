# Production Stack — LOCKED 2026-05-07

**Status:** Locked. Re-evaluar después de pieces #2 y #3.
**Justificación completa:** `projects/dinero-ia/research/2026-05-07_production-stack-research.md`

---

## Decisiones lockeadas

### Camera / face
**FACELESS** — texto en pantalla + B-roll de stock + voz humana.
- ❌ Talking head (descartado: requiere commitment de cara diaria)
- ❌ AI avatar (descartado: viola "no AI look" + penalty algoritmo hasta -80%)
- **Data:** Faceless educational +61% completion rate; top 100 YT faceless +340% subs vs face-based en 2025; 32% viral educativo TikTok ya es faceless.

### Voz
**Manuel (voz humana, español neutro mexicano CDMX)** como default.
- Backup: ElevenLabs ($22/mo, free tier 10K chars/mes) solo para multi-idioma futuro u overflow específico
- ❌ AI voice como primary (descartado: -engagement vs humana en TikTok 2026 ScienceDirect study; -trust/loyalty/RPM)
- **Data:** Mexican Spanish es-MX = estándar industrial Netflix/Disney+/HBO Max LATAM desde 1950s. Manuel ya vive en CDMX = ventaja sin entrenamiento.

### Editor primario
**Canva Pro** ($14.99/mo).
- Backup: CapCut SOLO para casos específicos (no MVP)
- **Data:** Para faceless info content con stock footage, Canva es objetivamente más rápido (Sonary 2026). CapCut tiene marca de agua que penaliza algoritmo hasta -72% reach en IG. CapCut es ByteDance (privacy concern).

### Acento (rules duras)
- **SÍ:** ustedes, carro, computadora, celular, manejar, platicar
- **NO peninsular:** vosotros, vale, tío, ordenador, móvil, coche, ceceo
- **NO MX extremo:** chido, padre, no manches, órale (en narración)
- **NO AR extremo:** vos sos, che, sheísmo (calle="cashe"), playa="plasha"
- **NO caribe extremo:** pa'lante, elisiones fuertes de "s"

---

## Stack actual ($/mo)

| Tool | Costo | Uso |
|---|---|---|
| Inoreader Free | $0 | Discovery noticias |
| Claude Pro | $0 (ya pagado) | Script + research |
| iPhone Voice Memos | $0 | Grabar narración |
| Canva Pro | $14.99 | Editor + captions + publish |
| Beehiiv | $0 → $39 después | Newsletter |
| **TOTAL MVP** | **$15/mo** | |

---

## ⚠️ Trial deadlines (CRÍTICO)

- **Canva Pro trial:** cancelar día 28 (≈2026-06-04) si NO se queda
- **Beehiiv trial:** revisar día 14 (≈2026-05-21) — luego free tier hasta 2.5K subs

---

## Backup tools (NO contratar todavía)

| Tool | Costo | Cuándo activar |
|---|---|---|
| ElevenLabs Pro | $22/mo | Solo cuando empiece multi-idioma (ej. versión EN) |
| CapCut | $0 free | Solo para piezas específicas con jump cuts sincronizados a audio trending |
| Submagic | $16/mo | Solo si auto-captions de Canva decepcionan después de 5 piezas reales |
| Perplexity Pro | $20/mo | Solo si research de Claude+Inoreader queda corto |

---

## Setup grabación voz (mínimo viable)

1. **Hardware:** iPhone + app "Voice Memos" o "Just Press Record"
2. **Espacio:** Habitación con ropa/cortinas/alfombra (absorbe eco)
3. **Timing:** 5-10 min por pieza (con retomas)
4. **Edición:** Canva audio editor o Audacity (free) para limpiar respiración/silencios
5. **Export:** WAV o MP3 alta calidad → import a Canva

---

## Pipeline producción end-to-end

```
1. RESEARCH    → Inoreader + Claude web search
2. SCRIPT      → Claude (markdown a repo, aplica brand_voice + templates)
3. VOZ         → iPhone Voice Memos (5-10 min)
4. VISUAL      → Canva Pro (texto frames + B-roll stock + audio)
5. CAPTIONS    → Canva auto-captions (revisar + corregir manualmente)
6. AUDIO BG    → Canva audio library (lo-fi corporate sutil)
7. PUBLICACIÓN → Canva Content Planner (alternativa: Buffer)
8. NEWSLETTER  → Beehiiv (sección Smart Brevity per template)
```

---

## Constraint check final ("no debe verse con IA")

| Elemento | ¿Pasa? | Por qué |
|---|---|---|
| Faceless format | ✅ | Faceless ≠ AI-made |
| Voz Manuel | ✅ | Voz humana, cero label IA |
| Stock footage Pexels/Canva | ✅ | Filmado por humanos |
| Texto en pantalla | ✅ | Escrito por humano (Manuel + Claude asistencia) |
| Auto-captions Canva | ✅ | AI-asistido, no requiere label per Meta |
| AI avatar | ❌ DESCARTADO | Violaría constraint |
| AI voice primary | ❌ DESCARTADO | Riesgo label + -engagement |

**Conclusión:** Stack pasa el constraint sin compromisos.

---

## Re-evaluación programada

Después de producir pieces #2 y #3 (con stack en uso real), medir:

1. **Tiempo real de grabación de voz** por pieza — ¿es sostenible o agota?
2. **Calidad de auto-captions de Canva** — ¿necesitamos Submagic?
3. **Variedad de B-roll en Canva** — ¿alcanza o necesitamos Storyblocks/Pexels Pro?
4. **Tiempo total de ensamble en Canva** por pieza — ¿es sostenible para frecuencia objetivo?
5. **Calidad del audio del iPhone** — ¿necesitamos micrófono USB ($30-100)?

Si alguna métrica falla → ajustar stack puntualmente. NO refactor masivo.

---

## Referencias data

- `projects/dinero-ia/research/2026-05-07_production-stack-research.md` — síntesis completa de las 6 web searches
- `projects/dinero-ia/research/2026-05-07_format-and-voice-research.md` — research US (sesión #1)
- `projects/dinero-ia/research/2026-05-07_latam-specific-research.md` — research LATAM (sesión #2)
- `projects/dinero-ia/brand_voice.md` — sección "Voz narrada" para reglas operativas
