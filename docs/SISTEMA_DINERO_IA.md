# SISTEMA DINERO IA — plan maestro (fuente única de verdad operativa)

> Documento maestro del sistema de producción de reels. Sintetiza dos auditorías
> multi-agente (arquitectura + calidad, 2026-07-02). SUPERSEDE la parte de estrategia/
> agentes de `CANON.md`. Regla de oro: si algo contradice este doc, gana este doc.
> `CLAUDE.md` sigue válido solo para lo técnico (cómo correr + gotchas).

---

## 1. Diagnóstico — dónde nos trabamos (la verdad incómoda)

1. **"Datos exactos con fuente" es hoy esperanza-de-prompt, no una garantía.** No hay
   nada que lo haga cumplir. Prueba: el BTC muestra **$475M** cuando la fórmula da
   **$477M** (7,700 × $61,900); el petróleo dice **"subió esta semana"** sin fecha. El
   moat declarado del canal (credibilidad) no está protegido por código.
2. **El director está PARTIDO en dos** (`director_editorial.py` produce, `director_treatment.py`
   idea con opciones) y no se hablan → por eso los reels 4 y 5 los escribí **a mano**. El
   cuello #1 que Manuel repite ("el cuello es MI dirección") sigue abierto.
3. **El i2v NO está cableado al director** — el agente no puede elegir "petróleo→barril,
   United→avión"; hoy lo hago yo. Es justo la creatividad que se quiere automatizar.
4. **Bugs de píxeles en reels ya entregados:** la cita de fuente cae en la banda inferior
   tapada por la UI de IG (y se trunca a 798px); la cifra héroe del latte ($1,074,962) se
   desborda del safe-area; el frame 0 (portada del grid + freno de scroll) es casi papel
   en blanco con 0.35s de audio muerto.
5. **Docs contradictorios:** `CANON.md §3` describe una paleta (dorado/morado/neón) que
   NADIE renderiza; el acento oxblood está sobrecargado (pinta victorias con color de pérdida).
6. **Pipeline frágil:** renders lentos, jobs largos en background se matan, i2v se RE-PAGA
   tras un crash a media tanda, la voz se reusa aunque se corrija una cifra hablada.

**Conclusión:** el sistema PRODUCE, pero le faltan las BASES de confiabilidad (datos,
dirección unificada, gates de píxel) para escalar sin publicar errores.

---

## 2. EL keystone (ambas mesas coinciden)

> **Construir un GATE "VERIFY" determinista (Python, no-LLM) + un LEDGER de datos tipado
> que corra ANTES del render.** Cada cifra vive como
> `{value, unit, currency, source, url, as_of, method}`. El Director la referencia por
> CLAVE — NO teclea números ni redacta el pie de fuente.

El gate: (a) **FALLA** si sobrevive cualquier `<<verify>>`; (b) **RECALCULA** las cifras
derivadas (unidades×precio, interés, erosión) desde `method` y rechaza si no cuadran con lo
mostrado (habría cazado el 475M); (c) **COMPONE** el pie de fuente desde la procedencia y
bloquea `as_of` rancio + claims temporales relativos ("esta semana/hoy") sin fecha en
carril=noticia (mata el "petróleo subió esta semana"); (d) deriva **visual=exacto / VO=redondeado**
del mismo ledger. Falla en segundos, no tras 6.5 min de render. Es la precondición para
automatizar el director sin publicar cifras inventadas. *Ojo honesto: hace los números
TRAZABLES, no verdaderos — las cifras VIVAS siguen necesitando fuente primaria + tu OK.*

---

## 3. La arquitectura — "el estudio" (tú diriges, el LLM implementa)

| # | Pieza | Tipo | Qué hace |
|---|---|---|---|
| 1 | **Investigador-Verificador** | 🤖 agente | Elige/prioriza tema, saca cada cifra-insumo con fuente/fecha/moneda, puntúa visualizabilidad. `<<verify>>` lo dudoso. |
| 2 | **Motor de datos (calculadora)** | ⚙️ código | Computa las cifras DERIVADAS (FV, erosión, 72, 4%…) y emite `datasheet.json` (SOURCED vs COMPUTED). **Nadie teclea números.** *(pieza nueva)* |
| 3 | **Director creativo (mono)** | 🤖 agente | Por beat: **2-3 opciones de sujeto/metáfora** (barril/avión/billete) + VO + hook + medio + transición. **NO auto-elige.** |
| 4 | **Compilador + Validador** | ⚙️ código | Aterriza tu elección a `reel_def`; **bindea props de la datasheet**; linter de PROCEDENCIA (cifra huérfana = BLOQUEA); R1-R11; gate de assets. |
| 5 | **Motor de producción** | ⚙️ código | Render Remotion + voz Asgard + i2v (dry-run $0 por defecto) + ensamblado (música/SFX/mux). |
| 6 | **QC de máquina (gate duro)** | ⚙️ código | Enchufa al gate: text-overlap, motion (anti-slideshow), paleta/safe-area, loudness, compliance CNBV, hook. Frena ANTES de tu ojo. |
| 7 | **Crítico creativo** | 🔀 híbrido | ASESOR, nunca bloquea: taste + **OCR de números horneados vs datasheet**. Notas para ti. |
| 8 | **Orquestador + cola/ledger** | ⚙️ código | `producir.py` re-apuntado a `build_reels`: cola→QC→caption→publicar→ledger (dedup/rotación, topes de gasto). |
| — | **MANUEL (showrunner)** | 🧑 humano | 4 compuertas ↓ |

**Tus 4 compuertas:** **G0** OK ligero a datos VIVOS dudosos (batcheable) · **G1** (LA de dirección)
ves las 2-3 opciones/beat **en papel** y **eliges** antes de renderizar/gastar (rechazo = $0) ·
**G2** apruebas el primer i2v de PAGO (doble candado) · **G3** [OK]/[Basura] del MP4 por Telegram.

**Flujo:** tema → (1) investiga → **G0** → (2) datasheet → (3) director propone opciones →
**G1 eliges** → (4) compila+valida → (si i2v) stills $0 → **G2** → (6) produce → (7) QC píxeles →
(8) crítico advisory → **G3** → publica. FAIL en cualquier gate → vuelve al agente culpable, no al inicio.

---

## 4. Las reglas duras (el estándar)

1. **UN renderer canónico:** `EditorialReel` (papel-oxblood). El director SOLO elige del menú
   cerrado. No inventa arte ni render de cero. (build916/60-beats = legacy.)
2. **Datos exactos por PROCEDENCIA, no por fe:** toda cifra del reel debe existir exacta en la
   datasheet (sourced o computed) o `<<verify>>` bloquea. Cifras vivas = fuente primaria + G0.
3. **Moneda siempre explícita** (USD/MXN). VO redondea; visual exacto; el crítico verifica por OCR.
4. **Tú diriges en G1** en papel antes de renderizar/gastar. El LLM propone 2-3 opciones, no auto-elige.
5. **Arco fijo:** cover(hook) → ≥2 datos visuales distintos → clímax (cifra protagonista) → close(CTA).
   4-6 beats. Prohibido repetir tipo de escena consecutivo.
6. **Transiciones SOLO del set que el renderer implementa** (hoy: fade/whoosh/flash), por tabla
   determinista. Prohibido "elegir" transiciones no-renderizables.
7. **Texto NUNCA sobre el hero/imagen** — sobre negro/scrim plano, verificado en píxeles. Durante
   un chart no va título encima.
8. **i2v INTEGRADO siempre:** enmarcado + grade + grano + pie de foto, nunca full-bleed crudo.
   Máx 1-2 hero i2v/reel, solo tras styleframe $0 aprobado + G2 (doble candado). **Logos/mapas/
   banderas/números = vector real; la IA NUNCA dibuja texto ni marcas.**
9. **Color:** oxblood = ÚNICO acento; verde=sube, rojo=SOLO pérdida. Un solo theme, sin decorar por escena.
10. **Movimiento constante:** cada beat se mueve; `filter_motion` es gate duro; sin tramo muerto >2.5s.
11. **Compliance CNBV:** nada de rendimiento garantizado / "sin riesgo" / asesoría individualizada.
12. **Ningún gasto ni publicación** sin gates de código en verde + tu OK (G3); todo cargo a `EXPENSES.md`.

---

## 5. Los pasos exactos (orden de ataque)

### 🔴 P0 — arreglos inmediatos (minutos, $0, en reels ya entregados)
- **P0.1** Corregir datos: BTC bignum $475M → **$477M** (7,700 × $61,900), dejar "≈475" solo en VO;
  declarar en el pie del Reel 1 el supuesto de rendimiento (~ilustrativo), INEGI no publica retornos.
- **P0.2** Sacar la cita de fuente + captions de la banda inferior tapada por IG (reservar banda de pie,
  2 líneas / auto-encoger, que no se trunquen).
- **P0.3** Hook a frame 0 + matar los 0.35s de audio muerto del inicio (número visible desde frame 0,
  SFX-hit en t=0 solo en b1, thumbnail del post).
- **P0.4** `fitSize` acotado a columna en `compare` (el $1,074,962 se desborda del safe-area).

### 🟠 P1 — las bases del sistema (el gran trabajo)
- **P1.1 [KEYSTONE] ✅ NÚCLEO CONSTRUIDO** (`infra/assembler/datasheet.py`): ledger tipado + calculadora
  determinista + `verify_reel()`. Auto-prueba en verde: caza el $475M (recomputa 476.63M→477) y el "esta
  semana" sin fecha; compone el pie de fuente. Primer ledger real: `datasheets/btc_apuesta.json`.
  FALTA (P1.1b): bindear las cifras de `reels_defs` a claves del ledger + llamar `verify_reel()` en
  `build_reels.py` ANTES del render (que BLOQUEE), y autorar el datasheet de cada reel.
- **P1.2** Motor de datos (calculadora determinista) ✅ incluido en `datasheet.py` (multiply/sum/diff/
  pct_change/real_value/fv_annuity). FALTA: binder datasheet→props en el compilador.
- **P1.3** Unificar los dos directores en UN `director.py` "writers-room" (IDEA→ELIGE→VERIFICA);
  arreglar el reintento roto y el KeyError.
- **P1.4** Cablear i2v al director (menú + VALID + manifest de clips existentes para reuso $0 + G2 para nuevos).
- **P1.5** Idempotencia i2v (no re-pagar tras crash; reconciliar con `generate list`) + cache de voz por hash.
- **P1.6** Fix del mapa por-país (agrandar protagonista, centrar por bbox) + re-targetear `validator.py` al schema editorial + enchufar los filtros de píxel al gate.
- **P1.7** Doctrina de color + `docs/standards/EDITORIAL_BRAND.md` como marca ejecutable (theme unificado).

### 🟡 P2 — robustez y escala
- **P2.1** Colapsar `build_reels`/`re_render`/`finish_reel_audio` en UN DAG content-addressed
  (mata lógica triplicada + bug `-shortest` que recorta el CTA; pre-check que falle si falta un asset).
- **P2.2** Gramática de transiciones sobria renderizable + `<EditorialPlate>` que hornee el tratamiento i2v único.
- **P2.3** Escenas metafóricas $0 nuevas (pictograma/símbolo/objeto-tipográfico) para subir el techo creativo sin pagar i2v.
- **P2.4** Loop de mejora: biblioteca de metáforas few-shot (sujeto→visual aprobados por ti) + realimentación de retención IG.

---

## 6. La creatividad, resuelta (cómo se vuelve "ultra")
Divergente en la IDEA, convergente en el MEDIO, honesta en el TECHO:
- El director nombra **LA COSA** a mostrar (no "una gráfica"): 2-3 opciones/beat.
- **Tú eliges** en G1 (tu gusto es la barra, no la auto-selección del LLM).
- Techo real ≈ 1 hero i2v/reel; el resto sube con **escenas metafóricas $0** + charts/mapas con dignidad.
- Transiciones y sujetos SIEMPRE del catálogo renderizable (crear dirección no-renderizable = prohibido).

---
*Estado 2026-07-02: 5 reels + flagship entregados. Bases pendientes = este plan. Empezar por P0 (hoy) → P1.1 keystone.*
