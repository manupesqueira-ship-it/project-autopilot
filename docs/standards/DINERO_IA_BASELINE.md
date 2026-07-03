# Dinero IA — Baseline "lo que funciona" (congelado 2026-06-15)

> Propósito: dejar por escrito el baseline VALIDADO del pipeline para que el
> escalado a **3 posts/día** no vuelva a re-litigar nada ya decidido. Si una
> idea futura contradice esto, gana esto (salvo que Manuel lo cambie explícito).
> La dirección de arte fina sigue mandándola la **Style Bible**; este doc fija
> el *sistema*, no el look.

---

## ✅ Lo que SÍ funciona — MANTENER

- **Sistema 100% propio y $0:** Remotion 4.x local + Blender (OptiX RTX 4060) +
  FFmpeg + n8n self-hosted. Nada de SaaS de paga como medio.
- **Recreación 1:1 de 0x100x + filtros QC en cadena:** cada beat clona un plano
  real de la referencia; QC A (programático: paleta/luminancia/safe-areas/motion)
  → B (juez visual vs ref) → C (video completo + loudness) → gate humano.
- **Voz = Asgard `eleven_v3`** (id `lJtjZw9ZjSbD9Zs9bOWq`), ElevenLabs
  `/with-timestamps`. **SIN subtítulos quemados** (la voz narra; el caption no se
  quema).
- **Color SEMÁNTICO locked:** verde=sube/seguro/marca · rojo=**SOLO** pérdida ·
  dorado=dinero · morado=solución. UN solo theme, consistente, profesional (NO
  viral): nunca cambiar fondo ni tamaño de número de forma decorativa.
- **Director (capa de decisión editorial codificada):** `infra/n8n/validator.py`
  R1–R11 (**34/34 tests**, validador lee el catálogo VIVO de `id="Beat..."` de
  `Root.tsx`; el `proposer` solo muestrea el subconjunto `FROZEN`)
  + `proposer.py` (esqueleto de guion $0 offline) + `ledger.py`+`ledger.json`
  (gate humano: solo registra un video tras OK de Manuel y recién ahí bloquea
  tema/combo) + Lane A (R10 recencia del **espectáculo wow** — tras el freeze
  Opción A 2026-06-19 las gráficas/datos quedan EXENTAS, son el lenguaje constante
  del canal) y Lane B (R11 rotación de puntas hook/clímax).
- **Catálogo de ~44 beats** (la verdad viva = leer `src/beats/` / los `id` de
  `Root.tsx`). **Rotación > cantidad:** el catálogo BASTA; el cansancio venía de
  falta de rotación, no de pocos tipos. No hace falta seguir agregando gráficas
  para escalar.
- **Transiciones:** **xfade real** en `build916.py` (`XFADE=0.35`, dip de música
  centrado en el silencio real entre voces). Los **cortes abruptos están
  RESUELTOS** — era el problema abierto #1, ya cerrado.
- **HeroCoin = moneda foto-real gpt-image en 2.5D** (`public/coins/<slug>.png`
  cacheada, generada con `infra/assembler/gen_coin.py`; Remotion le pone
  flotación + tilt 3D + glint + glow + count-up). Aceptada como "good enough".
  **Ya NO usa el Blender `coin.webm`.**
- **Datos SIEMPRE exactos del brief, nunca inventados.** Moneda explícita (USD o
  MXN), nunca "$X" a secas. El VO redondea ("alrededor de 200 millones"); el
  visual muestra la cifra exacta.
- **Nicho = finanzas personales LATAM en español** colgado de un hook macro de
  actualidad. El moat es la **precisión cultural** (CETES/pesos/inflación/
  modismos), no el look.

## ⛔ Caminos MUERTOS — NUNCA re-proponer

Cada uno se probó y Manuel lo rechazó. Re-proponerlos quema su confianza:

- Que **Claude arme el video desde cero en AE/ExtendScript** → "chafa" (test007/8/9).
- **Templates Envato ensamblados** como video completo → look genérico/incoherente.
- **Veo / IA generativa** (Kling/Hailuo/Higgsfield) como **medio principal** →
  "falta muchísimo", cero gráficas. Solo posible b-roll dentro del sistema.
- **Diseñador / freelancer externo** (ni one-time) → PROHIBIDO. Sistema 100% nuestro.
- **Plainly / pagar AE** sin replantear → no decidido; no pagar sin OK de Manuel.
- **Stack SaaS de publicación** (ContentStudio/Blotato/Beehiiv/carruseles/
  newsletter) → pivot muerto pre-video, archivado en `_archive/`.

---

## 🎯 Por qué esto importa para 3 posts/día

El cuello de botella a 3/día **no es la calidad del medio** (el baseline de arriba
ya produce video entregable end-to-end con gate humano), **es el MATERIAL**: hoy no
hay banco de temas, el brief se alimenta a mano. Por eso el siguiente paso es el
**banco de temas** (Fase 3), no pulir el "medio chafa". Decisión de Manuel:
**que fluya primero** — aceptar el baseline actual y dejar que el gate humano frene
lo malo, mientras se sube el volumen.
