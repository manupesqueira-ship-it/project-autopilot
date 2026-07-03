# AUDITORÍA PROFUNDA + PLAN DEL SALTO — 2026-07-03 (Fable 5)

> Encargo de Manuel: "revisada profunda a todo, encuentra qué tenemos mal, con qué nos quedamos,
> y qué podemos usar de internet. Aún nos hace falta un salto bastante grande."
> Método: 4 auditorías internas (repo/reels vs nuestras propias reglas) + 5 investigaciones de
> internet, 100 hallazgos verificados + evidencia de máquina (gates QC corridos sobre los reels).

---

## 1. QUÉ ESTÁ MAL (lo real, priorizado)

1. **IDENTIDAD ROTA** — 4 "fuentes de verdad" de look que se contradicen (papel `#F1ECE1` vs
   `#070707` vs `#0D1117` vs `#08090B`); 10 fondos, 3 dorados, 4 verdes conviviendo. `theme.ts`
   apunta a la paleta MUERTA (la importan ~70 archivos) y los beats nuevos hardcodean constantes
   con drift entre hermanos. Un reel hoy es ruleta de look.
2. **TIPOGRAFÍA CONTRA EL SPEC DEL DUEÑO** — Manuel dictó "grotesca finísima, MAYÚS, tracking
   ancho" (06-29) y el 100% de los beats nuevos usa Inter 800 bold. El rasgo más visible del look
   pedido está en el extremo opuesto. (A/B en píxeles enviado: msgs 110-111.)
3. **CRAFT PLANO "DE PROGRAMADOR"** — fills sólidos sin gradiente/rim/sombra, glow de un solo blur,
   easing lineal o default, springs con el rebote default de Remotion, cero stagger, cero motion
   blur, cero grano/viñeta/grade. La razón física del "bien pero no espectacular".
4. **SLIDESHOW, NO PIEZA EDITADA** — 1 de 13 transiciones del rulebook usada (dip-a-negro + mismo
   whoosh en 11/11 cortes), cero J/L-cuts, planos estáticos de 5-8s. **El reel de Nvidia FALLA
   nuestro propio gate anti-slideshow** (med 0.09 < 0.12; move 10% < 18%).
5. **ARCO ROTO EN EL RENDER** — el tratamiento aprobado del director tenía clímax al 80% (b7 en 2ª
   persona) y ScaleReveal (técnica firma); al renderizar se TIRARON 2 beats y nadie lo atrapó.
   Frame 0 vacío + promesa del hook al segundo 7 (ventana de 1.7s perdida).
6. **AUDIO DE PLANTILLA** — cama musical plana (el CTA suena igual que el hook), mismo whoosh para
   todo, sin silencio-antes-de-la-cifra, riser desalineado, cortes nunca al beat musical, y
   build_reels ignora `audio_master.py` (la cadena broadcast ya validada).
7. **BINDING VO↔VISUAL MUERTO** — la cifra héroe se revela 3-4s ANTES de que la voz la diga (land
   a ojo). Los timestamps por palabra de ElevenLabs YA se generan y no se usan.
8. **SIN GUARDIÁN DIRECTOR→RENDER** — `news_treatment.json` no lo consume ningún código; los gates
   QC existentes no están cableados a ningún build.
9. **ANARQUÍA DE PIPELINES** — 3 ensambladores + 4 directores incompatibles; los reels recientes se
   armaron por heredocs efímeros (masters vivían SOLO en Temp — ya rescatados a `out/{slug}/`).
10. **VIOLACIONES SEMÁNTICAS** — verde/rojo en comparaciones de magnitud (valencia falsa), moneda
    sin especificar, CTA que roza consejo de inversión (CNBV), logo como texto.
11. **CEMENTERIO ACTIVO** — 82 beats (50 legacy), one-offs con datos horneados como defaults,
    Root.tsx monolito 1,489 líneas.

## 2. QUÉ SE QUEDA (no tocar)

- **build916.py** = ensamblador canónico (cache + timeline + xfade + audio master + QC cableado).
- **audio_master.py** = cadena de audio broadcast validada. Todos los caminos deben llamarla.
- **Voz ElevenLabs Asgard v3 + /with-timestamps** — NO migrar de proveedor; dirigirla con audio
  tags v3. (~$22 USD/mes sobra para 45k chars.)
- **EChartsHero.tsx** = plantilla de la migración (único beat alineado a tokens + dual-theme).
- **Stack y doctrina**: Remotion + ECharts + FFmpeg + i2v solo héroes 10-25%.
- **DIRECTION_RULEBOOK + CREATIVE_PLAYBOOK** (el conocimiento es bueno; falta enforcement).
- **QC existente** (qc_gate, filter_motion, text_overlap_check) — detecta lo que Manuel ve a ojo.
- **tts_timestamps.py + words.json** = materia prima del binding, ya se genera gratis.
- Render local $0 (RTX 4060).

## 3. EL SALTO (plan ordenado)

| # | E | Acción | Recurso de internet |
|---|---|---|---|
| 1 | M | **Arbitraje de look en píxeles** (A/B enviado) → `theme.ts` único (tokens de EChartsHero + Inter v4 opsz + escala hero/sub/label + labels mono MAYÚS) → migrar 8 beats nuevos, legacy a `_legacy/` | Inter v4 variable (rsms.me/inter), patrón Vercel eyebrows |
| 2 | L | **UN pipeline**: `compile_treatment.py` (tratamiento→guion build916, fail-loud) + regla dura: si no salió de `producir_noticia.py→build916→out/{slug}/`, no existe | build916 existente |
| 3 | M | **Tokens de movimiento** (`src/motion/tokens.ts`): 4 curvas nombradas (MD3 Emphasized enter), 3 springs (SMOOTH damping:200 default), `stagger()` obligatorio, odómetro por dígito + tabular-nums. Cero interpolate sin easing | material.io MD3, remotion github-unwrapped (MIT), GSAP staggers 20-100ms, Odometer.js |
| 4 | M | **Materialidad + luz**: gradiente 2-stops + rim + doble sombra (luz GLOBAL) en todo shape; `<PhysicalGlow>` 4 pasadas blur exponencial (4/12/36/100px, 50/30/15/8%) solo en el acento | teardown 0x100x (epta01.txt), deep-glow falloff inverse-square, Josh Comeau shadows |
| 5 | M | **Capa de cine global**: `<Grade>` (grain feTurbulence 3-8% + viñeta + aberración solo impactos), `<Camera>` (push-in 1.00→1.06 + parallax 2.5D 0.2/0.6/1.0x), `<IdleLife>` (@remotion/noise drift ±1-3px — ningún frame estático) | css-tricks grainy-gradients, @remotion/noise, receta Vox tracking-transition |
| 6 | L | **Gramática de edición**: @remotion/transitions ≥4.0.466 (zoomBlur, dreamyZoom capítulos, whipPan custom + CameraMotionBlur), J-cut (VO −0.4s), match cut por número compartido. Lista negra: cube/swirl/glitch | remotion.dev/docs/transitions, gl-transitions.com (MIT) |
| 7 | L | **Binding multisensorial**: land desde words.json (nunca a ojo) + paquete-reveal (silencio 0.5s + riser con pico en el land + boom) + sfxCues[] por beat + music_meta.json (BPM librosa) + snap-to-beat + whisperX fallback/QC | whisperX (MIT, forced alignment es), librosa ya en repo |
| 8 | M | **Contrato director v2 + filter_D**: director emite transición+audio+arco por beat (clímax 75-90%, close ≤10%, re-hook 45-55%); filter_D valida el MP4 FINAL vs tratamiento (beats, clímax timestamp, land↔sílaba <300ms, frame 0 no vacío). Exit 1 = no se entrega | blackdetect/silencedetect/pixel-diff ffmpeg |
| 9 | M | **Golden reel**: re-ensamblar Nvidia por el pipeline nuevo completo (restaurar b4+b7, close 4-5s, CTA sin verbo de inversión) + side-by-side vs actual → gate humano → primer master del registry | tratamiento ya guardado + doctrina de masters |

## 4. QUICK WINS (hechos ✅ / pendientes)

- ✅ **Rescate anti-pérdida**: masters Temp→`out/{slug}/` + commit de 30+ módulos/docs untracked
  (CANON.md estaba untracked!) — commit `ce77c81`.
- ✅ A/B de look renderizado y enviado (msgs 110-111).
- ⬜ Cablear `qc_gate.py` post-mux en build916.assemble() (exit≠0 bloquea). **NO publicar Nvidia como está** (falla motion gate).
- ⬜ Constantes compartidas en los 8 beats nuevos + quitar fallback Georgia de PhotoHero.
- ⬜ Greps: `spring()` sin config → `{damping:200}`; `tabular-nums` en todo count-up.
- ⬜ Fix valencia (ScaleReveal gris+acento; MinPayFeel sin verde en lo malo) + CTA Nvidia sin verbo de inversión.
- ⬜ FFMPEG_BIN en qc_gate.py + _loudness degrada a WARN.

## Estado
- **Decisión pendiente de Manuel**: look A (bold) vs B (finísima) — define el theme único.
- **Bloqueo**: `ELEVENLABS_API_KEY` vencida (401) → VO placeholder edge-tts.
- Orden de ejecución tras el arbitraje: 1 → 3 → 4 → 5 (kit visual) · 2 → 8 (pipeline+gates) · 6 → 7 (edición+binding) · 9 (golden).
