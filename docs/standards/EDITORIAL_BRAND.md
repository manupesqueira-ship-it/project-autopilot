# EDITORIAL BRAND — biblia de marca ejecutable (Dinero IA)

> Fuente ÚNICA de color, tipografía, movimiento y layout del sistema de reels.
> **SUPERSEDE** la paleta de `CANON.md §3`, la sección de color de `CLAUDE.md` y el
> `DINERO_IA_STYLE_BIBLE.md` en lo que a color/tipo/motion respecta. Valores extraídos
> DEL CÓDIGO que sí se renderiza (`EditorialReel.tsx` / `MapZoomEditorial.tsx`), no de una
> aspiración. Si un doc viejo describe dorado/morado/neón, está obsoleto: gana este.

---

## 1. Paleta (hex EXACTOS, los que renderiza el motor)

| Token | Hex | Uso |
|---|---|---|
| `PAPER` | `#F1ECE1` | Fondo de todo (y océano en mapas). El papel se funde con la página. |
| `INK` | `#1B1712` | Tinta: titulares, cifras, texto principal, hairline gruesa del masthead. |
| `ACCENT` (oxblood) | `#9E2B22` | **El ÚNICO acento.** Palabra clave del titular, kicker, país protagonista. |
| `ACCENT_HI` | `#C24A3F` | Realce del acento (borde del país en el mapa, highlights). |
| `GREEN` | `#1F7A4D` | Ganancia / sube (verde editorial apagado, NUNCA neón). |
| `MUTE` | `#7A7264` | Texto secundario, edición, fuente, etiquetas tenues. **(canónico)** |
| `HAIR` | `#CDC4B2` | Hairlines finas (regla del pie). |
| `LAND` | `#DED6C6` | Tierra vecina en mapas (contexto, gris cálido). |

⚠️ **Bug a corregir:** `MapZoomEditorial.tsx` usa `MUTE = #8A806F` y `ACCENT_HI` propio;
alinear a `MUTE = #7A7264`. (Extraer estos tokens a un `editorial_brand.ts` compartido.)

## 2. Color SEMÁNTICO (regla dura)
- **Verde `#1F7A4D` = sube / ganancia.** Siempre.
- **Oxblood `#9E2B22` = ACENTO, no pérdida.** Es el color de énfasis de marca (una palabra por
  titular, el kicker, el país). NO pintar "victorias" ni "pérdidas" con oxblood por semántica.
- **La PÉRDIDA se codifica por contexto y movimiento** (una barra que cae, una cifra que se
  erosiona, flecha/eje a la baja), NO por un rojo-de-pérdida separado. Un solo acento, disciplina.
- Un solo theme constante: **NUNCA** cambiar color de fondo ni tamaño de cifra de forma
  decorativa entre escenas.

## 3. Tipografía
- Familia: **Inter (InterVar)**, cargada vía `staticFile("Inter-Variable.ttf")` + `loadFont`.
- Titulares/cifras: peso 800, tracking negativo (`-0.03em`), line-height ~1.0-1.05.
- Kickers/etiquetas: peso 700, MAYÚSCULAS, tracking ANCHO (`0.2em`-`0.28em`), en oxblood o mute.
- Cifras que se desbordan → `fitSize()` (auto-encoge; k=0.53) contra el ancho de columna. Nunca cruzar el margen.

## 4. Movimiento (nada estático)
- **Deriva constante** global: el contenido flota (sine translate ~7px + scale ~0.6%) — el marco
  (masthead/fuente) queda fijo. Sin tramo muerto > 2.5s (gate `filter_motion`).
- **HOOK visible desde el frame 0** (portada del grid + freno de scroll): la primera escena no
  entra con fade; el número/gancho está a opacity 1 desde el inicio.
- **Transición = dip-a-papel** entre escenas: la escena sale fundiéndose al papel y la siguiente
  sube desde el papel, DENTRO de sus propios frames (no desincroniza audio). El marco persiste =
  page-turn de revista. SFX de transición suave (no un whoosh que compite).
- Charts: la cifra cuenta, las barras crecen con spring, el ganador tiene glow/sweep. Durante un
  chart NO va título textual encima (el chart domina, la voz narra).

## 5. i2v — SIEMPRE integrado (nunca crudo)
- El i2v va como **FIGURA editorial**: enmarcado (margen de papel + borde de tinta 1.5px) +
  **tratado** (grade `grayscale(0.36) sepia(0.2) saturate(1.1) contrast(1.09)` + tinte oxblood
  0.1 overlay + grano) + **pie de foto** editorial + ken-burns lento. NUNCA full-bleed crudo.
- Máx 1-2 hero i2v por reel. **Logos / mapas / banderas / números = vector real (código); la IA
  NUNCA dibuja texto ni marcas.**

## 6. Layout (marco del informe)
- Márgenes: `M = 96` px laterales.
- **Masthead** arriba: "DINERO IA" (INK, tracking `0.28em`) + edición (MUTE) + regla INK de 2px (y~130).
- **Pie** abajo en `y=1574` (regla HAIR en 1548) — FUERA de la banda que tapa la UI de IG. La fuente
  (MUTE) y el folio (INK). Contenido en la banda segura ~`y 250-1450`.
- **Texto NUNCA sobre imagen/hero** — sobre papel o scrim plano. Gate en píxeles: `qc_gate.py`
  (`text_overlap_check`). Ver `LAYOUT_CONTRACT.md`.

## 7. Menú de escenas (cerrado)
`cover · mapzoom · bignum · compare · fallchart · payoff · plate · hero_i2v · close`.
El director SOLO elige de aquí; crecer el menú = agregar escenas $0 (pictograma/símbolo), no arte libre.

---
*Doctrina viva 2026-07-02. Tokens a extraer a `src/beats/editorial_brand.ts` (pendiente P1.7 código).*
