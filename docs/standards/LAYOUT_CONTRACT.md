# Contrato de Layout — carriles (texto NUNCA encima de imagen)

**Estado:** ✅ VIVO · regla DURA · gana sobre cualquier criterio "a ojo".
**Por qué existe:** es la corrección MÁS repetida de Manuel (~20 reincidencias). El texto/caption
montado sobre el hero (moneda, foto, gráfica) es rechazo automático. Revisar "a ojo" ya falló
demasiadas veces → ahora se **garantiza por construcción** y se **verifica por máquina** (gate
fail-loud). Si algo de este doc contradice otra guía, gana este doc.

---

## 1. La regla (carriles)

Cada beat se reparte en **carriles** que NO se pisan:

- **Carril HERO** (imagen / video i2v / gráfica / foto): vive en su zona, normalmente el tercio
  superior–central. Puede tener textura, brillo, niebla, movimiento.
- **Carril TEXTO** (hook, kicker, caption, labels, cifras tipográficas): vive en una **banda
  reservada** sobre **fondo plano oscuro** (`#070707`). Nunca toca píxeles "ocupados" del hero.
- Entre carriles hay **margen muerto** (banda de respiro) — nunca se solapan, ni en el frame
  pico del movimiento.

**Traducción dura:** la letra SIEMPRE se lee sobre negro mate plano. Si hay imagen detrás de la
letra (brillo/borde/textura del hero dentro de la caja del texto) → está MAL, no se entrega.

---

## 2. Garantía POR CONSTRUCCIÓN (no negociable)

No basta "acomodarlo y revisar". Todo texto que conviva con imagen se construye así:

1. **Banda reservada + scrim.** El texto va dentro de una banda con un **velo a negro plano**
   detrás (gradiente que llega a `#070707` opaco bajo la letra). El hero queda completamente
   velado en esa banda. Usar el primitivo compartido cuando exista (`PremiumStage` + velo
   inferior); si un beat nuevo pone texto sobre imagen, **hereda ese velo**, no inventa el suyo.
2. **El hero no entra al carril de texto.** Subir el hero (`objectPosition` alto), o reservarle
   un tope, de modo que su borde inferior + su glow/niebla queden **por encima** de la banda de
   texto con margen. Si el hero hace push-in/scale, calcular el carril con el frame de **escala
   máxima** (el hero más grande), no con el inicial.
3. **El texto no flota hacia el hero.** Si el bloque de texto deriva (drift/breathe), su recorrido
   completo se queda dentro de la banda. Nunca se centra el texto encima del objeto.
4. **Durante una gráfica NO va título encima** (regla locked del Style Bible). El kicker es una
   banda de texto SEPARADA arriba, sobre negro plano; la gráfica domina su propio carril.

---

## 3. Gate automático (fail-loud) — `infra/qc/text_overlap_check.py`

La verificación "a ojo" ya no es suficiente. El gate mide en PÍXELES si hay imagen activa detrás
del texto y **bloquea la entrega** si la hay:

- Detecta las **líneas de texto** (trazos finos y brillantes agrupados en filas densas — esto
  distingue una caption real de la textura del hero, p.ej. el grabado de la moneda o una cara).
- Para cada línea de texto, mide el **fondo alrededor de los trazos** (excluyendo el halo de
  anti-aliasing): si ese fondo es brillante/con textura → hay hero detrás del texto = **empalme**.
- Muestrea varios frames por beat (incluye los **extremos del movimiento**). Si el empalme persiste
  → `exit 1` (FAIL) con un JSON que nombra el beat y los frames culpables.

**Cómo correrlo:**
```
python infra/qc/text_overlap_check.py out/<slug>/<slug>_FINAL_916.mp4 \
       out/<slug>/<slug>.timeline.json
```
- `exit 0` = todos los beats tienen el texto sobre fondo plano (PASS).
- `exit 1` = al menos un beat tiene texto encima de imagen (FAIL) → corregir antes de entregar.

Va atado al gate de entrega (junto a `filter_delivery.py`): ningún reel llega a Manuel con empalme.

---

## 4. Verificación humana — SIEMPRE en MOVIMIENTO, en píxeles

El gate es el cinturón; esto son los tirantes. Antes de entregar:

- Mirar **frames reales** del MP4 final (no metadata, no el still de diseño): extraer el frame de
  **entrada**, el de **mitad** y el de **pico de movimiento** (push-in máximo / drift máximo) de
  CADA beat con texto+imagen. Un still puede pasar y el clip no.
- Confirmar que la letra se lee sobre negro plano y que el borde del hero (incluida niebla/glow)
  no entra a la caja del texto en NINGÚN frame del rango.

---

## 5. Antecedentes (por qué cada cláusula)

- 2026-06-30 — hook El Salvador: el borde inferior de la moneda ₿ (i2v) montaba sobre "UN PAÍS
  ENTERO" al crecer el push-in. Manuel: *"esta fatal esto… YA VAN 20 VECES"*. Fix por
  construcción: subir la moneda, velo a negro plano bajo el texto, bajar el bloque a la banda
  limpia. → origen de este contrato.
- 2026-06-15 — la moneda de `BeatHeroCoin` tapaba el caption al flotar (mismo patrón).
