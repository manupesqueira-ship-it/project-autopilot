# PLAN v3 — Motor AI dirigido · EL MOVIMIENTO es el producto

> **Estado: CANÓNICO desde 2026-06-24.** Supersede `PLAN_SALTO_CALIDAD_v2.md` (kit Remotion
> estático). Esta es LA estrategia. Reencuadre y luz verde de Manuel: 2026-06-24.
> El código de data-viz/tipografía de Remotion+Blender NO se tira — se reusa como la capa
> "datos = código". Lo que muere es la idea de que una imagen/kit ESTÁTICO sea el producto.

---

## La estrategia en una frase

El producto es el **MOVIMIENTO**, no la imagen. Cada reel se arma en **capas**: el OBJETO/ESCENA
que se mueve lo da un **motor AI de pago** (caricatura-fino, NO foto-realista); los **DATOS** los
dibuja **CÓDIGO**; y un **LLM-director** decide qué activo usar y cuándo. Ese director ES el
sistema/workflow que faltaba.

## Reglas de juego (Manuel, 2026-06-24 — bloqueadas)

- **Calidad > velocidad > volumen.** Lo más nuevo y mejor hecho, aunque cueste más.
- **1 video/día, sin prisa.** Tarde horas, da igual; es automático.
- **Duración 45–65s, nunca pasar de ~90s** (banda LATAM media, Manuel 2026-06-24; arriba de 90 la
  distribución de IG cae — Mosseri). Más largo NO es relleno: **el hook se mantiene TODO el video** vía la
  *columna de retención* — open-loop, foreshadow, micro-cliffhangers, escalada, movimiento continuo,
  payoff+loop-back. Más largo ⇒ **más beats que se mueven** (2 clips i2v OK, ~$2.5 USD/reel; Manuel
  autorizó pagar más por sostener la retención). Referencia: Jenny Hoyos, 90%+ watch-through a 34s.
- **Presupuesto:** apuntar alto, objetivo **~$5,000 MXN/mes, techo $10,000** (~$287–575 USD).
  El dinero deja de ser el cuello — pero *"tampoco una máquina que quema dinero"*.
- **Cero parches:** primero la base dura y bien hecha (todo $0); cuando esté lista, aviso a
  Manuel y RECIÉN ahí se empieza a pagar e iterar.
- **premium ≠ realista:** estilo **caricatura-fino bloqueado**.
- **Datos SIEMPRE exactos** del brief; **color semántico**; **no mezclar lenguajes incoherentes**.

---

## Arquitectura en capas — el "menú cerrado" de tomas

La coherencia NO viene de una librería infinita; viene de un **menú CERRADO** de arquetipos por
el que pasa cualquier tema. El director elige + parametriza; nunca inventa libre.

| # | Arquetipo | Motor | Cuándo se usa | Ejemplo |
|---|---|---|---|---|
| 1 | **Mapa-zoom** | CÓDIGO (Mapbox/MapLibre) | geopolítica / país | Bukele → zoom globo a El Salvador + bandera encima |
| 2 | **Marca/logo** | logo **vector REAL** (banco de logos) animado en código | una empresa nombrada | Dell, United → wordmark armándose |
| 3 | **Objeto héroe** | **IA imagen→video** (de pago) | la cosa física de la nota | avión que entra/sale, barril, servidor |
| 4 | **Caricatura-personaje** | **IA i2v** + consistencia de personaje | un líder / CEO | Milei, Trump, Michael Dell |
| 5 | **Dato** | CÓDIGO (D3/Remotion, **ya existe** en `infra/remotion-render`) | los números | gráfica verde→rojo, contador |
| 6 | **Tipografía cinética** | CÓDIGO (Remotion, **ya existe**) | hook / remate | palabra o cifra que aterriza |

**La capa de datos (5,6) es la parte FÁCIL y ya resuelta** (reusar el catálogo Remotion). Mapas
(1) son código conocido. **La pieza NUEVA = objeto/personaje que se mueve (3,4) + el director.**

---

## El director — la creatividad (la pieza DIFÍCIL; NO está resuelta aún)

Es un **LLM (Claude)**: lee `tema + datos verificados` → emite un **shot-list** (por beat:
arquetipo, sujeto, movimiento, fuente del activo, razón). Constreñido al menú de 6 = coherente.

**Ejemplo "Dell sube por resultados":**
- Beat marca → **logo real** de Dell (identidad instantánea).
- Beat objeto → **lo que los DATOS movieron**: si la nota es de servidores de IA, muestra un
  *servidor* estilizado, NO una laptop al azar. Esa elección (leer el artículo, saber qué hace
  Dell, elegir el objeto que cuenta la historia) **ES la creatividad** — y es trabajo de un LLM.

**Hallazgo de diseño (sube calidad, mata "look-IA"):** **los logos/marcas NO se generan con IA**
(la IA destroza texto — pasó con texto horneado en barras de oro). Se **bajan como vector real**
y se animan en código. La IA solo genera el OBJETO/personaje.

**Cómo se valida la creatividad:** se PRUEBA en **$0** sobre temas reales; Manuel juzga los
**shot-lists en papel** ANTES de que se pague nada. NO se vuelve a afirmar "está resuelta".

---

## Fases de construcción (todo $0, ANTES de pagar un peso)

- **F1 — Menú de tomas (spec).** Los 6 arquetipos: cuándo se usa, cómo se renderiza, params del
  estilo bloqueado. Define el contrato del shot-list.
- **F2 — Director-LLM.** `tema + datos → shot-list` (JSON estructurado, constreñido al menú).
  Probarlo en N temas reales hasta que la dirección salga buena consistente.
  → **GATE 1 (gratis):** Manuel juzga los shot-lists en papel (incluido uno tipo Dell).
- **F3 ✅ — Fuentes de activos.** Banco de logos (vector real), mapas (código), data-viz (reuso),
  y el **wrapper del motor i2v** (`infra/assembler/i2v_engine.py`, provider-abstracted, dry-run
  por defecto = $0; ruta de pago con doble candado `--live` + `I2V_ALLOW_SPEND=1`).
- **F4 ✅ — Estilo bloqueado + consistencia de personajes.** Registro único
  `infra/n8n/character_roster.json` (espejo de `hero_assets.json`): estilo de casa bloqueado,
  método de consistencia ($0-primero = still cacheado como ancla + LoRA local; Seedream sequential
  de respaldo), política de figuras públicas. `validator.py` lee el ROSTER del registro (sin drift).
- **F5 ✅ — Candado anti-slideshow + ensamblador.**
  - *Candado* = `infra/qc/filter_motion.py`: mide movimiento GLOBAL (mediana + fracción en banda
    real, robusto a picos de corte) y REPRUEBA el slideshow que `filter_a` deja pasar (cards con
    micro-pulso). Piso calibrado MEDIAN≥0.12 / MOVING≥18% (pasa los 10 FINAL aprobados, reprueba
    hard-cut y Ken-Burns-casi-quieto). Regresión: `infra/qc/test_filter_motion.py` (8/8).
  - *Ensamblador 9:16* = **YA existe, sin plomería nueva**: un clip i2v entra como `hero.video_url`
    de un beat `kind:"hero_3d"` → `HeroBeat` lo compone con `OffthreadVideo` sobre el StudioScene
    (`Composition.tsx`), igual que el WebM de Blender; `build916.py` ensambla → `filter_motion` lo
    gatea. **Pendiente de GATE 2 (decisión de arte, no código):** el MP4 de Kling NO trae alfa →
    decidir objeto-enmarcado (keyear a WebM-alpha) vs full-bleed (still de Seedream ya sobre el set)
    al ver el primer clip real.
- → **GATE 2 (gasto):** con la base lista + OK de Manuel, **primer render de pago de UN beat
  real** que se mueve → lo verifico yo (pixeles) → Manuel juzga vs su barra.
- **F6 — Producción.** Cablear `director → render → QC → ensamblado`; automatizar 1/día.

---

## Stack de motores (premium, quality-first) — verificar EN VIVO antes de gastar

Todo **pay-per-use** (fal.ai/Replicate/oficial), **SIN suscripción** → se puede testear 1 reel
suelto sin comprometerse a un plan.

- **Still (identidad + estilo de casa):** **ByteDance Seedream 4.5** — hasta 10–14 imágenes de
  referencia + "Edit Sequential" para fijar personaje/objeto en una serie, salida hasta 4K.
- **Imagen→Video (el que mueve):** **Kling 3.0 Pro** — el mejor estilizado de 2026; **Motion
  Brush** = pintar el camino del movimiento sobre el still (mejor control de "objeto entra/sale"
  + cámara), 10s, 1080p@30fps, audio nativo. Alternativa anime-puro más barata: **PixVerse V4.5**.
- **Consistencia de personaje recurrente:** **Higgsfield Soul ID** (entrena 1 vez con ~20 fotos,
  identidad persistente entre sesiones; tiene MCP de Claude Code) y/o **LoRA por personaje**
  (15–20 imgs, 95%+ fidelidad) para los 1–2 caricaturas más usados. Seedream sequential cubre
  el estilo de casa.
- **NO usar:** Sora 2 (OpenAI lo está apagando: app abr-2026 / API sep-2026), Veo 3.1 / Runway
  Gen-4.5 (tiran a foto-realista y caros). LTX-2 = opción self-host $0 a futuro (IC-LoRA).

**Costo estimado (1/día, ~30/mes):** un reel realista lleva 2–4 clips i2v (los beats de objeto/
personaje; el resto es código $0) + un par de stills. Kling v3 ≈ $0.084–0.14/seg → ~$1/clip 8s.
**Por reel ≈ $3–9 USD (~$50–155 MXN)** con margen para re-rolls (calidad-primero). **Por mes ≈
$90–270 USD (~$1,560–4,700 MXN)** — dentro del objetivo de $5,000 MXN con holgura. (TC ~17.4.)

**Flags a verificar antes de pagar:** (1) 9:16 @ 1080p explícito en Kling/Seedance (las páginas
dicen "varios aspect ratios/1080p" sin confirmar 9:16@1080p — checar el param en fal). (2) Soul ID
está pensado para *parecido de persona real*; para **caricaturas de figuras públicas** confirmar
la política de la plataforma sobre identidades reales (alternativa más segura y controlada = LoRA
propio o caricatura suficientemente estilizada). (3) Licencia comercial por-modelo en fal.

---

## Adaptar vs construir (no reinventar; Manuel: "seguro ya hay sistemas, encontrarlos/adaptarlos")

**ADAPTAR (open-source, la plomería YA vale la pena en 2026):**
- **ViMax** (`HKUDS/ViMax`, MIT) — multi-agente Director/Screenwriter/Producer; el codebase más
  limpio para levantar la lógica de **director/orquestación + shot-list**.
- **HyperFrames** (`heygen-com/hyperframes`, Apache-2.0) — "escribe HTML, renderiza video, para
  agentes": GSAP/Three/Lottie = tipografía/charts code-motion (o seguir con nuestro Remotion).
- **OpenMontage** (`calesthio/OpenMontage`, AGPL) — **blueprint** (no forkear cerrado); de aquí
  sale la idea del **candado anti-slideshow** (se niega si >80% estático).
- Wrappers de proveedor (estilo `anil-matcha/open-generative-ai`, MIT) sobre Seedance/Kling/ElevenLabs.

**CONSTRUIR Y POSEER (el moat — ningún repo lo tiene):** el **director afinado a la marca +
precisión finanzas-LATAM** (CETES/inflación/FX, redondeo de narración, safe-areas, color
semántico), el **arte/look bloqueado**, y la **capa de datos exactos**.

---

## Qué NO hacer (anti-objetivos)

- **NO** imágenes estáticas como entregable (rechazado 2026-06-23).
- **NO** generar logos/texto/marcas con IA → se bajan como vector real.
- **NO** mezclar lenguajes visuales incoherentes en un mismo video.
- **NO** parches sobre base floja; **NO** pagar/iterar antes de que la base esté lista + OK de Manuel.
- **NO** foto-realismo (premium ≠ realista).
- **NO** re-proponer caminos muertos: AE/Nexrender/plantillas Envato, generación-desde-cero de
  craft por Claude, diseñador externo.

---

## Estado / próximo paso

**Base F1→F5 ✅ construida y verificada ($0).** Todo el camino existe sin tocar dinero: director
(F2) → menú/activos (F1/F3) → estilo+roster (F4) → candado anti-slideshow + ensamblador `hero_3d`
(F5). Siguientes pasos, ambos requieren a Manuel:
1. **GATE 1 (gratis):** enseñarle shot-lists reales del director (incluido uno tipo Dell) en papel.
2. **GATE 2 (gasto):** con su OK → primer beat i2v de pago real (Seedream+Kling) → verifico pixeles
   yo mismo (mediana/duración/encuadre, no solo metadata) → Manuel juzga vs su barra. Aquí se
   resuelve la única decisión abierta de F5 (objeto-enmarcado vs full-bleed) con un clip real enfrente.
