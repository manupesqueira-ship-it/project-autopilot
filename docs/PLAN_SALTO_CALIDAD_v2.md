# PLAN SALTO DE CALIDAD v2 — Dinero IA

> **Acción de implementación de este plan:** escribir este contenido en
> `docs/PLAN_SALTO_CALIDAD_v2.md`. NO se escribe código todavía. Este documento ES el
> entregable. Lo que sigue es el plan accionable y priorizado.

---

## Contexto (por qué este plan)

Dinero IA produce reels 9:16 de finanzas personales LATAM, faceless, $0 marginal. El
pipeline (LLM planner → ElevenLabs → Remotion + Blender → QC A/B/C → FFmpeg → gate
Telegram → IG) funciona técnicamente, pero el output es "competente pero genérico" y en
3+ semanas no cruza de bueno a premium. El diagnóstico (segunda opinión, ya dado) concluye
que **el medio es correcto** (cuando se clona fielmente un plano real de la referencia —
ej. `LineChartSemantic.tsx` — el resultado SÍ es premium) y que **el cuello de botella es
de ejecución/estandarización, no de herramienta**: nunca se congeló un sistema de diseño
terminado. La cura es un **Motion Design System** de ~8-10 arquetipos diseñados a la
perfección UNA vez y congelados, con la dirección de arte inyectada en *design-time* y el
LLM reducido a *elegir escena + rellenar datos*.

Este plan baja eso a cambios concretos por archivo, en dos carriles: **A** ($0, empieza ya)
y **B** (gateado por gasto de Manuel).

---

## Hallazgos verificados (donde el código contradice el brief — gana el código)

> ### ⚠️ CORRECCIÓN (2026-06-19, re-verificada empíricamente en el checkout local)
>
> Antes de tocar nada corrí `npx remotion compositions` contra el disco real de Manuel.
> **El build está VERDE:** bundleó en ~3.8s y listó las 50 composiciones, incluidos
> exactamente los módulos que el hallazgo #1 daba por "fantasma". Tres de los cuatro
> hallazgos de abajo son **falsos en este checkout** — fueron derivados contra `origin/main`
> (el remoto), no contra el disco local:
>
> - **Hallazgo #1 (FALSO aquí):** los 8 módulos supuestamente ausentes **sí existen** en
>   disco — `beats/StoryHook`, `beats/NapkinWriteOn`, `beats/NewspaperSetPiece`,
>   `beats/PhoneSetPiece`, `beats/ChalkboardSetPiece`, `beats/TicketSetPiece`,
>   `studio/BrandSignature`, `R1Montage` — y **`src/anim.ts` también existe**. El bundle
>   compila. → **A0 (llegar a build verde) ya está satisfecho**; colapsa a "confirmar build
>   verde + reconciliar git para que el repo refleje el disco".
> - **Hallazgo #3 (FALSO aquí):** `director.py`, `producir.py`, `setpiece_catalog.json` y
>   `anim.ts` **sí existen** en disco. (La decisión de archivar set-pieces en A1 sigue siendo
>   válida como dirección — pero no es porque sean vaporware.)
> - **Hallazgo #4 (FALSO aquí):** hay **45 beats** en `src/beats/*.tsx`, no 39. El síntoma
>   de fondo ("se agregan tipos en vez de perfeccionar pocos") **sí se sostiene** — solo el
>   conteo estaba mal.
> - **Hallazgo #2 (SE SOSTIENE):** el reframe del LLM es quirúrgico/localizado, no sistémico.
>   La fuga de "arte en runtime" (color en hex, conteo de líneas/barras) es real y A2 la cierra.
>
> **Causa de la discrepancia:** el plan se escribió contra el remoto; este checkout tiene todo
> ese trabajo como ~70 archivos sin commitear + 7 commits sin pushear — exactamente el
> *"Riesgo de sync git (alto)"* que el propio plan marca más abajo. Por eso el **primer paso
> real es reconciliar git** (Carril A, antes de A1) para que el estado del repo coincida con la
> realidad del disco. **La dirección estratégica del plan (Motion Design System, A1–A6) queda
> intacta y validada.** El texto original de Manuel se preserva sin cambios abajo.

Leído el código real en este checkout. Tres correcciones importantes al supuesto de partida:

1. **El bundle de Remotion NO compila tal como está en el repo.** `src/Root.tsx` importa 8
   módulos que no existen en disco: `beats/StoryHook`, `beats/NapkinWriteOn`,
   `beats/NewspaperSetPiece`, `beats/PhoneSetPiece`, `beats/ChalkboardSetPiece`,
   `beats/TicketSetPiece`, `studio/BrandSignature`, `R1Montage`. Además
   `beats/BigNumberCounter.tsx:11` hace `import { riseIn } from "../anim"` y `src/anim.ts`
   **no existe**. Cualquier `npx remotion render` debería fallar al bundlear. → O estos
   archivos son trabajo local sin commitear en la máquina de Manuel, o el sistema de
   set-pieces es vaporware a medio construir. **Precondición A0 del plan: llegar a un build
   verde.** (Confirmar con Manuel si hay trabajo local sin pushear; ver Riesgos.)

2. **El LLM ya NO compone libremente** — el reframe está a medio hacer. El planner solo
   rellena *props estructurados*; no puede pasar `fontSize`, `x/y`, `layout`. La fuga de
   "arte en runtime" es **estrecha y localizada**, no sistémica:
   - El LLM elige el **color en hex** de la cifra (`color: "#00D9A5|#FF6B6B|#D4A574"` en
     `BeatBigNumber`/`BeatHeroCoin`, `planner_system_prompt.txt:20,61`).
   - El LLM elige **cuántas líneas / qué palabras accent** (`BeatKinetic`), **cuántas
     barras / puntos / labels** (`BeatBars`, `BeatTrendBreak`).
   `validator.py` valida arco/estructura/timing/ledger (R1–R11 duras) y solo *advierte*
   sobre color semántico (W-color, warning). → El reframe A2 es quirúrgico, no una
   reescritura.

3. **`director.py`, `producir.py`, `setpiece_catalog.json` y `anim.ts` no existen.**
   `proposer.py:37` importa `direct` de un `director` ausente. El "casting de set-pieces"
   está referenciado pero sin implementar. → No los resucitamos: los set-pieces se archivan
   (Carril A1), y la orquestación se simplifica en vez de completar el stub.

4. **Hay 39 beats implementados, no 45** (`src/beats/*.tsx`). Con los 6 fantasma referenciados
   (set-pieces + StoryHook) la "intención" eran ~45. El síntoma del diagnóstico se confirma:
   se agregan tipos en vez de perfeccionar pocos.

5. **Blender es 100% procedural.** `infra/blender/coin_hero.py` (307 líneas) genera geometría
   desde cero cada corrida (`primitive_cylinder_add`, `primitive_torus_add`, texto extruido),
   ilumina por código (4 luces hardcodeadas + gradiente nodal), exporta PNG RGBA → `encode_host.py`
   → WebM VP9 yuva420p. **No hay `.blend` terminados guardados.** Esto es exactamente lo que A5 ataca.

6. **El master de audio ya es sólido.** `build916.py` aplica `loudnorm I=-16:TP=-1.5:LRA=11`
   (pre y post), ducking por sidechain (ratio 6:1) y un dip super-gaussiano centrado en los
   huecos audibles reales. **Falta** de-ess, EQ y compresión de carácter (A6 los agrega).
   Voz: Asgard `eleven_v3`, `stability 0.38 / similarity 0.8 / style 0.25 / speaker_boost`.

---

## CARRIL A — Trabajo $0, empieza ya (sin gasto, sin diseñador)

> Orden recomendado por impacto/dependencia: **A0 → A1 → A3 → A2 → A4 → A6 → A5.**
> A0/A1 desbloquean todo; A3/A2 son el corazón del salto; A4 es barato y protege; A6 es
> alto-impacto/bajo-esfuerzo; A5 es el más caro y va al final.

### A0 — Precondición: build verde y `anim.ts` canónico *(prerequisito, no opcional)*

El sistema debe bundlear en un checkout limpio antes de cualquier otra cosa.

- Crear `infra/remotion-render/src/anim.ts` con las utilidades canónicas que el código ya
  asume (Style Bible §5.4): `riseIn(frame, fps, {delay, distance, overshoot})` y un set de
  configs de spring nombradas (los `{damping,mass}` hoy repetidos inline: 14/0.7 estándar,
  12/0.6 rápida, 16/0.5 muy rápida). Esto centraliza el "easing overshoot + settle" que pide
  la Style Bible y elimina la divergencia entre beats.
- Reconciliar `Root.tsx`: los imports fantasma se resuelven **eliminándolos** como parte de
  A1 (los set-pieces se archivan), no creándolos.
- **Archivos:** crear `src/anim.ts`; editar `src/Root.tsx`, `src/beats/BigNumberCounter.tsx`.
- **Esfuerzo:** 0.5 día. **Impacto:** desbloquea todo lo demás (sin esto nada renderiza).

### A1 — Congelar el kit maestro: 10 arquetipos, archivar el resto

Criterio: **cobertura del catálogo de temas con el mínimo de escenas**, no variedad. Cada
arquetipo ancla a un plano premium de la referencia 0x100x. **KIT CONGELADO (10):**

| # | Arquetipo (componente) | Slot narrativo | Ancla premium de la referencia | Por qué se queda |
|---|---|---|---|---|
| 1 | `KineticText` | Hook (texto) | Tipografía sans revelada palabra-por-palabra, sync a voz | Hook verbal; ya usa `wordFrames` reales de ElevenLabs |
| 2 | `StatCallout` | Hook (cifra-shock) | Número gigante limpio sobre fondo oscuro | Pareja de rotación de #1 en el slot hook (R11 exige ≥2) |
| 3 | `LineChartSemantic` | Dato / WOW (tendencia) | Línea I→D, relleno verde→rojo, glow, dot con reflejo | **El plano probado-premium.** Absorbe `TrendBreak` y `RecoveryChart` por parámetro de fase |
| 4 | `BarsValue` | Dato (magnitudes ordenadas) | Barras con peso/volumen e iluminación direccional | Cubre "cuánto cuesta/rinde X"; ya tiene cara 2.5D iluminada |
| 5 | `PictogramPersons` | Dato (proporción/relato) | Grid "X de cada 100" que ilumina celdas | Relatabilidad personal-finance + moat LATAM ("X de cada 100 mexicanos") |
| 6 | `VersusCards` | Dato (A vs B) | Dos elementos enfrentados con multiplicador | Comparación es el 50% de finanzas (ahorro vs inversión, peso vs dólar) |
| 7 | `MapZoom` | WOW (hook macro) | Fly-in vectorial a país, profundidad fija | El "hook macro de actualidad" geográfico (inflación MX, BTC El Salvador) |
| 8 | `BigNumberCounter` | Clímax (cifra) | Cifra que aterriza, color semántico, reflejo en piso | Cierre numérico; sincronizado por `countEndFrame` |
| 9 | `HeroCoin` → `HeroObject` | Clímax (objeto) + **firma de marca** | Objeto 3D con peso (vidrio/metal/glossy, DOF) | Pareja de rotación de #8 al clímax **y** el objeto de firma recurrente (Style Bible §5.8) |
| 10 | `CtaClose` | Cierre (CTA) | Cierre tipográfico limpio con open-loop | No negociable; cierra el loop al siguiente video |

**Opcionales provisionales (NO en el kit; promover solo si un tema lo exige de verdad, con
OK):** `DonutChart` (reparto de presupuesto), `Timeline` (hito histórico macro). Se dejan en
el repo pero fuera del catálogo del proposer.

**Archivar (mover a `infra/remotion-render/src/beats/_archive/` y quitar de `Root.tsx` +
`proposer.py` pools):** AssetCard, BarRace, BubbleChart, CandlestickChart, CharacterCard,
DebateCards, DialGauge, FunnelChart, Heatmap, Histogram, LogoWall, LollipopChart, MultiMap,
NewsCard, ProgressRing, RadarChart, SankeyFlow, ScaledIcon, Scoreboard, SlopeChart,
StackedAreaChart, Testimonial, TickerTape, Treemap, RecoveryChart\*, TrendBreak\* (\*plegados
en #3 vía parámetro). Más los 6 fantasma (StoryHook + 5 set-pieces) que se borran de los
imports. Racional de archivado: charts de analista cripto/trading (Sankey/Radar/Treemap/
Candlestick/Histogram/Funnel/Lollipop/Bubble/Heatmap) no son staples de finanzas-personales
LATAM; los dependientes de PNG/caricatura (Character/Debate/Testimonial) y de logos
(News/LogoWall) son asset-hungry y propensos a fallback feo.

- **Archivos:** `src/Root.tsx` (quitar Composition + import de cada archivado), `src/beats/_archive/`
  (nueva carpeta), `src/CatalogGallery.tsx`, `infra/n8n/proposer.py` (pools `WOW`/`DATA_VISUAL`/
  `CHARTS`/`LANDING`), `infra/n8n/validator.py` (`TYPES`, `HOOK_TYPES`, `WOW`, `DATA_VISUAL`).
- **Esfuerzo:** 1 día. **Impacto:** ALTÍSIMO — define el sistema; sin esto todo lo demás flota.

### A3 — Endurecer los 10 para que el output feo sea IMPOSIBLE

La dirección de arte se garantiza en el componente, no se confía al input. Por cada arquetipo
del kit:

- **Auto-fit de números (hoy NO existe — tamaños fijos `128`, `50/38`).** Añadir un hook/
  componente `<AutoFitNumber max=… min=… maxWidth=…>` que reduzca `fontSize` con `clamp()`
  hasta caber en el ancho seguro. Usar en `BigNumberCounter`, `StatCallout`, `BarsValue`,
  `VersusCards`. Un número largo nunca se sale del cuadro.
- **Color SOLO por enum semántico (elimina la fuga del hex libre).** Definir en `theme.ts` un
  `ROLE = { gain:green, loss:red, money:gold, neutral:teal, solution:purple }` y que los
  componentes acepten `role: keyof ROLE` (NO `color: string`). El hex deja de ser superficie
  de input. (Ver A2 para el lado planner.)
- **Safe-areas garantizadas por el componente:** un `<SafeFrame>` wrapper (márgenes 9:16 +
  zona de captions/UI de IG) que recorta/posiciona el contenido; ningún beat dibuja fuera de él.
- **Conteos de slots fijos:** Kinetic = 2-3 líneas, ≤1 accent/línea, *auto-derivado* (no input
  libre); Bars = 3-5 barras; LineChart = N puntos acotado. Lo que exceda se trunca/colapsa con
  regla determinista, no se rompe el layout.
- **Archivos:** `src/theme.ts` (enum ROLE + helper), nuevo `src/studio/AutoFitNumber.tsx`,
  nuevo `src/studio/SafeFrame.tsx`, y los 10 componentes del kit para consumirlos.
- **Esfuerzo:** 2-3 días. **Impacto:** ALTO — convierte "depende del input" en "imposible fallar".

### A2 — Reframe runtime→design-time: el LLM elige escena + datos, jamás compone

Quirúrgico, apoyado en que el reframe ya está a medias. Tres cambios:

1. **`planner_system_prompt.txt`** — quitar TODA mención de hex de color, tamaños y
   composición libre. Reemplazar `"color": "#00D9A5|#FF6B6B|#D4A574"` por
   `"role": "gain|loss|money|neutral|solution"`. El prompt pasa a un contrato estricto:
   *"rellena estos slots de datos con cifras EXACTAS del brief + moneda explícita; elige
   role semántico; NO eliges layout, tamaño, posición ni color"*. Accents de Kinetic se
   auto-derivan (cifra/keyword), no los pide al LLM.
2. **`proposer.py`** — restringir los pools al kit de 10 (A1) y mantener el casting de
   estructura (arco hook→wow→datos→clímax→CTA) en Python, no en el LLM. El stub `director`
   ausente se elimina del import; el "casting" se reduce a elegir arquetipo del kit + lane de
   rotación (ya existe lane A/B). Sin set-pieces, sin `setpiece_catalog.json`.
3. **`validator.py`** — con color por enum, **W-color se vuelve innecesaria** (el feo es
   imposible por construcción). Endurecer en cambio: rechazar (duro) si el `role` de un beat
   = `loss` sin lenguaje de pérdida en el VO, y viceversa (mover la lógica `_vo_has_loss()`
   de warning a error). Mantener R1–R11. Añadir validación de **schema de props** (rechazar
   campos desconocidos o fuera de enum, hoy se ignoran silenciosamente).
- **Archivos:** `infra/n8n/planner_system_prompt.txt`, `infra/n8n/proposer.py`,
  `infra/n8n/validator.py`; `build916.py:apply_cues()` no cambia (los cues siguen igual).
- **Esfuerzo:** 1.5-2 días. **Impacto:** ALTO — cierra la convergencia-al-promedio en su origen.

### A4 — Fail-loud: matar los fallbacks procedurales

Un asset faltante debe **abortar el render**, nunca sustituir con arte de programador.

| Fallback procedural hoy | Ruta | Acción |
|---|---|---|
| Monograma si falta logo | `src/studio/BrandLogo.tsx:93-106` | Arquetipos del kit no usan logos (LogoWall/News archivados) → si algún slot pide logo y falta, `throw` con mensaje claro |
| Silueta SVG si falta caricatura | `src/beats/DebateCards.tsx:33-46` | DebateCards archivado (A1) → eliminado |
| Bandera `null` silenciosa | `src/beats/MapZoom.tsx:98-100` | Si falta la bandera del país, `throw` en vez de render vacío |
| "Lingote"/volumen faux por código | `BarsValue` 2.5D polygons, `BigNumberCounter` extrude textShadow, `HeroCoin` glint | **Decisión de diseño, no eliminar a ciegas:** el faux-3D 2D es legítimo en 2D. Lo que se prohíbe es **sustituir un asset 3D faltante (PNG de HeroCoin) por una forma plana**. `HeroCoin` debe `throw` si `public/coins/<slug>.png` no existe (hoy ¿qué hace?: verificar y endurecer). |

Implementar un helper `requireAsset(path)` (en `src/studio/`) que lance `delayRender`-error
legible si el archivo no está, y usarlo en todo punto que cargue PNG/WebM. El render falla
ruidoso → el QC/gate lo detecta, nunca llega arte chafa al video.
- **Archivos:** nuevo `src/studio/requireAsset.ts`, `HeroCoin.tsx`, `MapZoom.tsx`,
  `BrandLogo.tsx` (o su retiro), `CharacterCard.tsx` (archivado).
- **Esfuerzo:** 1 día. **Impacto:** MEDIO-ALTO — barato, evita la regresión silenciosa a genérico.

### A5 — Blender: de geometría procedural a `.blend` terminados con swap

Convertir `coin_hero.py` (genera-desde-cero) en **escenas `.blend` pre-construidas,
iluminadas y terminadas** que solo intercambian objeto/material/texto.

- **Construir 1-2 `.blend` maestros** (turntable hero) UNA vez, a mano en Blender: cámara con
  DOF, HDRI/estudio de 3 puntos terminado, piso con reflejo, materiales glass/metal/glossy
  calibrados. Guardar en `infra/blender/scenes/hero_turntable.blend`.
- **Reescribir el script** a un *runner* que haga `bpy.ops.wm.open_mainfile(hero_turntable.blend)`
  → localizar el objeto-slot vacío → **importar/asignar** la malla del activo (de una librería
  de `.blend`/`.obj` curados) + material del enum semántico + texto → render. **Cero
  `primitive_*_add`, cero luces por código.**
- Mantener el pipeline de export que ya sirve: PNG RGBA → `encode_host.py` → WebM VP9
  yuva420p → `<OffthreadVideo transparent>`. No tocar.
- Si falta el `.blend` del activo pedido → fail-loud (A4), no generar primitiva.
- **Archivos:** `infra/blender/scenes/*.blend` (nuevos, a mano), reescritura de
  `infra/blender/coin_hero.py` → `render_hero.py`; `encode_host.py` sin cambios.
- **Esfuerzo:** 2-3 días (incluye modelar/iluminar a mano los maestros). **Impacto:** MEDIO —
  el 3D es UN beat (HeroObject); alto valor de marca pero menor cobertura que A1-A3.

### A6 — Voz: selección, settings y master de audio

La voz hoy es 5/10 por selección+dirección, no por plataforma.

- **Selección:** evaluar 2-3 voces LATAM masculinas de la biblioteca ElevenLabs contra Asgard
  con el MISMO guion (A/B ciego). Mantener `eleven_v3`. (Voice-clone de Manuel sigue en ADR-018
  como Fase 1.1, no bloquea.)
- **Settings:** bajar `stability` a **0.30-0.35** (más expresivo/humano), `style` 0.25-0.30,
  `similarity_boost` 0.8. Cambio en `infra/voz/tts_timestamps.py:VOICE_SETTINGS`.
- **Guion para el oído:** en `planner_system_prompt`/`VOICE.md`, frases cortas, una idea por
  respiración, cifras habladas con redondeo natural ("casi un millón") aunque el visual muestre
  la exacta (ya cubierto por W-round).
- **Cadena de master (agregar al final de la actual, antes del `loudnorm` final en
  `build916.py:assemble()`):** sobre el stem de VO ya normalizado, insertar en el filtro
  ffmpeg: **highpass ~80Hz → de-esser (`deesser` o banda 5-8kHz con `acompressor`
  sidechain) → EQ de presencia (suave +2-3dB ~3-5kHz, `equalizer`) → compresor de carácter
  (`acompressor` ratio 3:1, attack 10ms, release 120ms)**. Esto va ANTES del ducking/mezcla,
  no reemplaza el `loudnorm` final ni el sidechain.
- **Archivos:** `infra/voz/tts_timestamps.py` (settings), `infra/assembler/build916.py`
  (cadena de filtros en `assemble()`), `docs/standards/VOICE.md`.
- **Esfuerzo:** 1-1.5 días. **Impacto:** ALTO/bajo-esfuerzo — la voz se percibe en cada segundo.

---

## CARRIL B — Gateado por gasto de Manuel (NO ejecutar sin su OK)

> ⚠️ **GATEADO.** Requiere OK explícito de Manuel **y** revisar el veto vigente a externos
> (CLAUDE.md / Style Bible §9: "diseñador/freelancer externo PROHIBIDO"). Esta palanca es la
> excepción explícita "one-time para especificar el kit maestro, NO por video". Presentar como
> decisión de gasto, no ejecutar.

### B1 — Brief listo-para-enviar a un motion designer ONE-TIME

**Qué entrega (mapeado 1:1 a los 10 arquetipos de A1):**
- **10 style-frames 9:16 (1080×1920), uno por arquetipo del kit**, en el peor caso de datos
  (números largos, 5 barras, etc.), exportados como PNG + el fuente (AE/Figma/.blend).
- **Spec de motion por frame, con VALORES concretos** (no adjetivos): gradiente de fondo (stops
  hex + ángulo), radio/opacidad de glow y bloom, tamaños de fuente por rol tipográfico (hook/
  headline/cifra/caption), curvas de easing (cubic-bezier exactas o spring damping/mass),
  movimientos de cámara (amplitud px + Hz), y **timing por beat** (frames de entrada/hold/salida).
- **Formato:** un PDF de spec + tabla de tokens (mapeable a `theme.ts` y `anim.ts`) + los
  fuentes. El equipo **reconstruye en Remotion** (no se integra el fuente del diseñador como
  video — eso es el camino muerto Envato/AE rechazado en el gate 2026-06-11).

**Dos niveles de gasto:**
- **Completo (~$2,000-4,000 USD):** 10 style-frames + spec de motion + 1-2 ciclos de revisión.
- **Reducido (~$800-1,500 USD):** solo style-frames + spec; el equipo reconstruye todo el motion.

**ROI esperado:** convierte el techo de ejecución (la barra que 3 semanas no se alcanzó) en un
spec congelado y reproducible. Si destraba el salto a premium, el costo se amortiza en días de
no-iteración. **Riesgo:** que el spec no se respete en la reconstrucción → mitigar con A3
(componentes que hacen cumplir los tokens).

### B2 — Gasto opcional nice-to-have (prioridad BAJA)

- **Créditos chicos de IA para b-roll atmosférico de FONDO** (no como medio principal — eso es
  camino muerto): texturas/loops sutiles detrás del fondo limpio. Monto: <$20 USD de prueba.
  **Prioridad baja, solo si A1-A6 ya entregaron y falta "aire" atmosférico.** Gateado igual.

---

## Cierre

### La UNA cosa de mayor impacto en 30 días
**Congelar el kit de 10 arquetipos endurecidos (A0+A1+A3+A2) y producir los próximos videos
SOLO con ellos.** Es el cambio que el diagnóstico identifica como la cura raíz: estandarización
brutal sobre pocas escenas perfectas. Todo lo demás (Blender, voz, diseñador) es multiplicador
sobre esa base; sin ella, siguen oscilando entre inventar (feo) y clonar (inescalable).

### Riesgos y supuestos
- **Riesgo de sync git (alto):** los 8 imports fantasma + `anim.ts` ausente sugieren trabajo
  local sin pushear O un sistema a medio construir. **Antes de archivar, confirmar con Manuel**
  si esos archivos existen en su Windows sin commitear; si existen, traerlos y evaluarlos en
  vez de borrar imports a ciegas. El plan asume el estado del repo remoto como verdad.
- **Supuesto:** la cobertura de temas LATAM se logra con 10 escenas. Si aparece un tema que
  ninguna cubre, la regla es **NO crear un beat nuevo** (anti-objetivo): reescribir el ángulo
  para que entre en el kit, o promover un opcional provisional con OK.
- **Riesgo:** endurecer validator (enum + schema) podría rechazar guiones viejos. Aceptable —
  "esos ya fueron" (CLAUDE.md); no re-sembrar guiones viejos.
- **Supuesto:** A5 (Blender a mano) depende de tiempo de modelado de Manuel/equipo; si no hay,
  HeroObject queda con el `.blend` actual congelado como único hero hasta tener más.

### Qué NO hacer (anti-objetivos)
- **NO agregar beats nuevos.** El kit es 10. Crecer el catálogo es el síntoma, no la solución.
- **NO migrar de herramienta** (AE/C4D/Cavalry/Plainly). El medio (Remotion+Blender) ya alcanza
  la barra; el techo es ejecución.
- **NO inventar dirección de arte en runtime.** El LLM elige escena + datos + role semántico;
  jamás color hex, layout, tamaño ni posición.
- **NO resucitar caminos muertos:** Envato/AE como video, Veo/IA generativa como medio,
  set-pieces a medio construir, n8n como servidor. Los set-pieces fantasma se archivan, no se
  completan.
- **NO reintroducir fallbacks "bonitos".** Asset faltante = render que falla ruidoso.

---

## Verificación (cómo se prueba end-to-end tras implementar)

1. **Build verde (A0):** `npx remotion render <CompId>` de cada uno de los 10 arquetipos
   bundlea y renderiza sin error de import.
2. **Imposible-feo (A3):** renderizar cada arquetipo con datos de borde (número de 12 dígitos,
   5 barras, texto largo) → ningún elemento se sale del `SafeFrame`; correr `infra/qc/filter_a.py`
   (safe-areas/paleta/luminancia) → exit 0.
3. **Reframe (A2):** correr el planner sobre 3 temas de `temas_cola.json`; inspeccionar el JSON
   → cero campos `color`/hex, solo `role`; `validator.py guion_*.json --ledger` pasa R1–R11 y la
   nueva regla role↔pérdida.
4. **Fail-loud (A4):** borrar un `public/coins/<slug>.png` y renderizar HeroObject → el render
   ABORTA con mensaje legible (no produce forma plana).
5. **Voz (A6):** A/B ciego de la voz nueva vs Asgard; medir loudness/TP del master
   (`filter_c_prepare.py`) sigue en `I=-16/TP=-1.5`; de-ess audible en sibilantes.
6. **End-to-end:** `python build916.py guion_<slug>.json all` produce `*_FINAL_916.mp4`;
   pasa Filtro A → B → C; gate humano de Manuel.
