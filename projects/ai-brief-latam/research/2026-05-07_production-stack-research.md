# Production Stack Research — AI Brief LATAM
**Date:** 2026-05-07
**Status:** Complete — decisions locked in PRODUCTION_STACK.md

> Research question: ¿Qué stack de producción de contenido maximiza engagement en LATAM y permite escalabilidad?

## Constraints del usuario
1. "No quiero que sean videos que se vean mucho con inteligencia artificial"
2. Maximizar engagement
3. LATAM como audiencia primaria
4. Permitir automatización futura
5. Costo MVP bajo

## Findings por dimensión

### Dimensión 1: Faceless vs Talking Head vs AI Avatar

| Métrica | Faceless | Talking head | AI Avatar |
|---|---|---|---|
| Completion rate (educational) | +61% vs face | baseline | -reach hasta 80% |
| Crecimiento subs YT top 100 (2025) | +340% vs face | baseline | NA |
| % viral educativo TikTok 10M+ views | 32% faceless | mayoría aún face | <5% |
| Compatibilidad con "no AI look" | ✅ | ✅ | ❌ |

**Cuentas faceless de referencia (info/finanzas):**
- Mike (anonymous finance, 500K followers, charts + voiceover)
- @factsdailyy (faceless facts page)
- @sicilysancienthistory (48.6K en 71 posts)

**Decisión:** FACELESS con texto en pantalla + B-roll + voz humana.
**Descartados:** Talking head (commitment de cara diaria), AI avatar (viola constraint + penalty algoritmo).

### Dimensión 2: Voz humana vs AI vs sin voz

**Estudio académico (TikTok 2026, ScienceDirect):**
- Ads con voz IA generan engagement MENOR que voz humana
- Bajar pitch de voz IA reduce el gap
- Voz IA de celebridad ≈ voz humana

**ReelBase analizó 10,000 Reels:**
- Performance "nearly identical" overall
- Voz humana gana en: emoción, trust, loyalty, retención, RPM
- Voz IA OK para: facts, top 10s, tech explainers, finance rundowns

**Industria de referencia:**
- MrBeast hires voice actors, NO AI, para internacionalización
- Faceless YT con AI voice "indistinguishable" en engagement, pero loyalty menor
- ElevenLabs free: 10K chars/mes

**Decisión:** Voz propia de Manuel como default + ElevenLabs como backup específico (multi-idioma o overflow).

### Dimensión 3: Acento / Español neutro

**Mexican Spanish (es-MX) = estándar industria:**
- Netflix, Disney+, HBO Max LatAm usan es-MX para doblaje
- Mexico City = capital del doblaje en español desde 1950s
- 130M speakers Mexico + 62M US Hispanos
- Comprensible de Argentina a California

**Reglas duras:**
- SÍ: ustedes, carro, computadora, celular, manejar
- NO peninsular: vosotros, vale, ordenador, móvil, coche
- NO MX extremo: chido, padre, no manches, órale
- NO AR extremo: vos sos, che, sheísmo (calle="cashe")
- NO caribe extremo: pa'lante, elisiones fuertes

**Decisión:** Acento mexicano CDMX neutralizado (Manuel ya vive en CDMX = ventaja sin entrenamiento).

### Dimensión 4: Canva Pro vs CapCut

**Para FACELESS info content específicamente:**
- Canva: design-first, 100M+ stock library, brand consistency, cloud collab, NO marca de agua, autopublish nativo
- CapCut: video-first, auto-captions más rápidos, pero owned by ByteDance (privacy), marca de agua en pro features (-72% reach si visible en IG)

**Sentencia experta:** "Para faceless informational video con stock footage = Canva often faster and easier" (Sonary 2026).

**Decisión:** Canva Pro como editor primario. CapCut descartado para MVP (riesgo marca de agua + privacy + no necesario para faceless info).

### Dimensión 5: Constraint "No AI Look"

**Penalty algoritmo IG 2026:**
- Pure AI-generated content: hasta -80% reach
- "Made with AI" label: -15% a -80% engagement
- Penalty aplica a: stock footage sin value-add, generic captions, contenido "AI-generated without human refinement"
- AI-ASSISTED text (captions, scripts) NO requiere label
- Mosseri admite Instagram NO puede detectar AI confiablemente

**Solución:**
- AI como ASISTENTE (script writing, research, edit) ✅
- AI como GENERADOR primario (avatar, voz primaria, imágenes 100%) ❌
- Stock footage de Pexels/Canva (filmado por humanos) ✅
- Voz humana ✅

## Stack final lockeado

| Tool | Costo/mo | Uso |
|---|---|---|
| Inoreader Free | $0 | Discovery |
| Claude Pro (chat) | $0 (ya pagado) | Script + research |
| iPhone Voice Memos | $0 | Grabar narración |
| Canva Pro | $14.99 | Editor primario |
| Beehiiv Free | $0 → $39 | Newsletter |
| **TOTAL MVP** | **$15/mo** | |

**Backup (NO contratar todavía):**
- ElevenLabs Pro ($22): solo multi-idioma futuro
- CapCut: solo casos específicos
- Submagic ($16): solo si Canva captions decepcionan post 5 piezas
- Perplexity Pro ($20): solo si research insuficiente

## Re-evaluación

Después de pieces #2 y #3 medir:
- Tiempo de grabación de voz por pieza
- Calidad de auto-captions Canva
- Variedad de B-roll disponible
- Engagement comparativo si hacemos test A/B con/sin voz

## Fuentes (web searches 2026-05-07)
1. Faceless vs talking head Instagram Reels engagement data 2026
2. AI voice vs human voice short form video engagement perception 2026
3. Acento neutral español narración Reels engagement Latinoamérica voz
4. Canva Pro vs CapCut comparison 2026 automation API workflow
5. Faceless news AI Instagram account format successful 100k followers
6. Instagram AI label detection penalty reach 2026 algorithm
