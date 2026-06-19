# Dinero IA — Style Bible (FUENTE DE VERDAD ÚNICA)

**Versión:** 2.2 · **Fecha:** 2026-06-19 (base 2026-06-03) · **Estado:** ACTIVO
**Reemplaza a:** `docs/standards/VISUAL.md` (v1.0 — arquitectura muerta gpt-image-2/Seedance, NO usar)
**Base empírica:** teardown frame-by-frame de @0x100x + 13 creators benchmark + 8 directivas de Manuel + iteraciones de quality-bar (test015→test017) + pipeline propio Remotion/Blender end-to-end.
**v2.2 (2026-06-19):** §8 REESCRITA — método vigente = sistema PROPIO (recreación 1:1 de 0x100x + Remotion/Blender/FFmpeg local + cadena de filtros QC, todo $0). Plantillas Envato/AE/Nexrender/n8n RECHAZADAS (gate 2026-06-11, ver §9). Congelamiento de gastos más estricto: $0, AE+Envato cancelados.

> Este es el ÚNICO documento de estándares vivo de Dinero IA. Toda la investigación que Manuel mandó está destilada aquí. Si algo contradice este doc, gana este doc. Si falta algo que Manuel mandó, se agrega aquí — no en otro archivo nuevo.

---

## 0. La verdad incómoda (leer primero)

Llevamos 3 iteraciones aterrizando en **"competente pero genérico — la misma calidad"**. Eso NO es un problema de técnica (más glow, más 3D, más limpieza). Es un problema de **MÉTODO**:

- Hemos estado **GENERANDO** escenas desde un guion y estilizándolas con **un truco nuevo por ronda** (limpiar fondo → moneda 3D). Ese método converge en "buen motion-graphics genérico" y **nunca** en premium.
- Premium = **cientos de microdecisiones deliberadas de un director de arte por cada plano** (qué está en pantalla, dónde, qué se mueve, a dónde va el ojo, el ritmo exacto). No son 5 técnicas apiladas.
- La moneda 3D **no movió la aguja** porque un asset genérico soltado en una composición genérica sigue siendo genérico. **El 3D no es magia; lo que falta es dirección de arte integrada.**
- **El medio (Remotion/código) NO es el techo duro.** Agencias publican anuncios premium hechos en Remotion. El techo es que **no hay director de arte tomando decisiones** — estamos auto-generando.

**Conclusión:** el cambio que se necesita es de método, no de herramienta. Ver §8.

---

## 1. La referencia: ADN de @0x100x (crypto edu, 434K)

Lo que hace que se vea premium, en orden de impacto:

1. **Fondo = escenario limpio**, NO campo de partículas. Negro real (o estudio blanco/gris en recaps) + UN spotlight/glow radial + viñeta. La profundidad la da el OBJETO, no el clutter.
2. **Objetos hero en 3D real** (vidrio, metal glossy, plástico, soft-body) con reflejos sobre piso glossy, sombras suaves, DOF. **Diferenciador #1** vs SVG planos. Hechos por diseñadores en AE + Element3D/C4D.
3. **Lighting con color semántico:** key light + rim/glow. Verde vibrante = marca/sube. Rojo = pérdida. Dorado = dinero. Morado = solución/producto.
4. **Tipografía:** sans limpia chica (Helvetica/Inter), reveal palabra-por-palabra, **palabra CLAVE en bold o color**. Texto grande SOLO para divisores/punchlines.
5. **Motion calmado:** cámara lenta (push/pan), física real (caída/settle/echo-trails), parallax por profundidad, **DOF fuerte** (fore/back borrosos, hero nítido).
6. **Charts:** línea dibujada izq→der, fill verde que vira a ROJO en el peligro, dot glowing sobre la curva, labels "+$5000". Bell-curve para "vender el techo". Oscuros, glowing, NO barras planas.
7. **Metáforas concretas:** filmstrip 35mm = recap, casas = propiedad, multitud 3D = "miles", robot = AI. Concreto > abstracto.
8. **Pacing:** ~2-3.5s por beat, tight, **sincronizado a la palabra**.

**Técnicas baratas de 0x100x replicables HOY en 2D:** neon line-art (stick-figure verde glowing, velas que se prenden, línea ascendente glowing sobre negro = stroke SVG + glow, NO 3D). Números split-color ("20" blanco + "24" verde). Caption posición variable pero siempre chica + word-by-word.

---

## 2. Decisiones BLOQUEADAS (no re-litigar sin Manuel)

- **Estética = profesional consistente, NO viral.** UN solo theme de principio a fin. NUNCA cambiar color de fondo ni tamaño de número entre escenas de forma decorativa. (v11 "viral" RECHAZADO; v10 cinematográfico constante APROBADO.)
- **Color SEMÁNTICO, nunca decorativo:** verde=sube/seguro/marca · rojo=SOLO pérdida real · teal `#5BC0BE`=neutro/asignación (gasto rutinario, salida que NO es pérdida) · dorado=dinero · morado=solución/producto. Shift de color permitido SOLO si es semántico dentro del theme oscuro.
- **Nicho = HÍBRIDO:** finanzas personales LATAM en español, cada video colgado de un hook/noticia macro de actualidad. (No gringo-traducido, no calculadora genérica.)
- **Moat = precisión cultural LATAM** (pesos/CETES/inflación/Nubank/modismos), NO el look. El look nos pone al nivel; la cultura nos hace compartibles.
- **Fondo oscuro pero BIEN ILUMINADO**, no vacío negro. (test015 quedó "ligeramente muy oscuro": subir luminancia del piso charcoal→slate, key más brillante, viñeta menos agresiva, más bloom.)

---

## 3. Paleta (locked)

| Rol | Hex | Uso |
|---|---|---|
| Fondo base | `#0D1117` / gradiente `#1B2433→#141C28→#0D131C` | backgrounds |
| Dorado (dinero/cifras) | `#D4A574` | montos, %, números clave |
| Verde/mint (sube/seguro/IA/marca) | `#00D9A5` | data positiva, acento de marca |
| Rojo (pérdida) | `#FF6B6B` | SOLO pérdida real (cifra negativa / caída / dinero perdido). NUNCA para un gasto rutinario o salida planeada |
| Teal (neutro / asignación) | `#5BC0BE` | salidas/gastos rutinarios que NO son pérdida (renta, comida…), barras neutras, decrementos de waterfall sin `loss`. Existe para que el rojo no se use en outflows que no son pérdida |
| Texto primario | `#FFFFFF` | hooks, headlines |
| Texto secundario | `#A0A0B0` | captions, fuentes, fechas |

**Prohibido:** verde corporativo `#00A86B` (confusión de marca), magenta neon, fondo claro/white mode (salvo "modo estudio" controlado), >2 acentos por escena.

---

## 4. Tipografía (locked)

- **Hooks:** Inter Bold/Extra-Bold (700-800), 84-110pt, tracking -0.02em, line-height 1.1.
- **Headlines:** Inter Bold, 56-72pt.
- **Body:** Inter Medium, 36-48pt, line-height 1.4.
- **Cifras destacadas:** Inter Black (900), 100-140pt, color dorado.
- **Captions/fuentes/mono:** JetBrains Mono Regular, 22-28pt, gris.
- Una sola familia sans por escena. Mono SOLO en captions/fuentes.

---

## 5. Las 8 directivas de Manuel (alto retorno — integrar a TODO)

1. **Sound design (no solo música):** librería ~10 SFX micro (0.2-0.5s): whoosh en cámara, impact/thud cuando aterriza un número, tick al aparecer keyword, clink de moneda, swell antes del punchline. Disparar en start_frame + sub-eventos.
2. **Muted-first (80% ve sin sonido):** caption burned-in cuenta la historia solo; frame 0 debe frenar el scroll congelado. Test: pausar en seg 0 → "¿me frena?".
3. **Moat = LATAM** (ver §2).
4. **Easing overshoot, nunca lineal:** anticipation + overshoot + settle (spring rebote SUTIL), stagger 2-4 frames. No el bouncy del v11.
5. **Bloom global + grano sutil (3-5%):** unifica y mata la frialdad "CGI demasiado limpio". (Hornear glow, no blur full-screen por frame.)
6. **Espacio negativo y silencios INTENCIONALES:** dejar el punchline respirar sobre negro un beat. Contraste vacío→lleno hace pegar el dato. (OJO: distinto de los "silencios raros" por bug de timing — ver §7.)
7. **Retención: open-loop al inicio + payoff al final + loop-back** (última línea conecta con la primera → replays).
8. **Activo de marca recurrente (firma):** UN objeto/mascota propio en CADA video, reconocible en 0.5s. **Sistema CONSTRUIDO** (`src/studio/BrandSignature.tsx`, $0): "bug" de esquina que respeta las safe-areas del 9:16, entra con el easing LOCKED (§5.4) y no compite con el contenido; arquitectura de set-piece (OBJETO de marca = asset en `public/brand/<slug>.png`, slug por prop; sin asset → **placeholder PROCEDURAL $0** = chip neutro "dinero sube" + wordmark, render-testable HOY). Composición QC `BrandSignature` (con backdrop) para juzgar tamaño/posición/sutileza en R1. **PENDIENTE de Manuel (gate):** (a) **definir cuál es la mascota** (será el primer asset 3D orgánico — gpt-image PNG **[👁️ ~$3 MXN]** o frame hero del modelo 3D, ambos caen en el mismo slot PNG); (b) aprobar el look de la firma; (c) decidir el wire-up "en cada video" (overlay único en el ensamblado — se prende cuando el look esté aprobado, NO se toca el master aprobado sin su OK). El componente NO inventa la identidad de marca: es el SLOT + el sistema.

---

## 6. Reglas de charts (locked)

- Durante un chart NO hay título/subtítulo de texto encima (compite con la voz). El icono indicativo arriba SÍ.
- Si hace falta contexto, va en un **beat de texto SEPARADO antes** del chart.
- Línea dibujada izq→der, semántica verde→rojo, dot glowing, labels de dato, valor final highlighted. Oscuro y glowing, no barras planas.
- La voz hace el storytelling completo durante el chart.

---

## 7. Pacing y audio (RESUELTO — verificado en código 2026-06-19)

**Problema reportado (test017):** "despasado, silencios raros." **Causa raíz original:** los beats usaban duración FIJA (`duration_frames`) no atada al voiceover → aire muerto o corte a destiempo.

**RESUELTO en `infra/assembler/build916.py`:**
- **Duración atada a la voz:** cada beat dura `LEAD + dur(VO_mp3) + TAIL` frames (≈línea 220), calculado por-beat de la duración REAL del mp3 de ElevenLabs. Ya NO hay `duration_frames` fijo.
- **Animación sincronizada a la palabra:** `apply_cues()` lee `words.json` (timestamps por palabra de ElevenLabs `/with-timestamps`) y ata cada cue (growWords, pulseWords, countEnd, kinetic word-by-word…) al frame de SU palabra en la voz.
- **Costura sin pisar la voz:** el xfade (0.35s) cae DENTRO del silencio LEAD/TAIL; el dip de música se centra en el HUECO AUDIBLE real (fin de la última palabra → inicio de la primera de la siguiente, vía `words.json`), no en el borde del mp3.
- **Guard de entrega:** `filter_delivery.py` mide los huecos reales entre voces (`vo_stem`) + loudness/TP/duración sobre el MP4 ENTREGADO; exit!=0 BLOQUEA la entrega.

**Silencio remanente = INTENCIONAL:** queda ~1.0s de respiro entre voces (`LEAD 0.25 + TAIL 1.10 − XFADE 0.35`), puntuado por el SFX de transición y el dip de música — es el "breath beat" de §5.6, no un bug. El video auto-producido del 2026-06-19 pasó QC 12/12 sin queja de pacing.

---

## 8. EL MÉTODO (VIGENTE — reescrito 2026-06-19)

Probado empíricamente: **generar-desde-cero topa por debajo de la barra de Manuel** (test007/8/9/015). El gap es **craft / dirección de arte**, no técnica ni medio (§0). Y **comprar** craft empaquetado tampoco funcionó: las plantillas de marketplace (**Envato AE + Nexrender + n8n**, que fueron este §8 hasta el 2026-06-10) dieron un look genérico/viejo e incoherente entre beats → **RECHAZADO en el gate 2026-06-11** (ver §9). AE + Envato Elements quedaron CANCELADOS.

**Método VIGENTE — sistema PROPIO "recreación 1:1 de 0x100x + cadena de filtros QC" (todo $0):**

La forma de ADQUIRIR craft sin generar de cero ni pagar plantillas es **clonar el trabajo de un pro plano por plano**: cada beat recrea un plano real de la referencia 0x100x (cuya dirección de arte ya está resuelta) y luego se **parametriza con los datos exactos del guion**. No se inventa dirección de arte: se hereda de la referencia y se rellena con el dato LATAM.

**El motor (todo local, $0):**
1. **Render 2D:** Remotion 4.x local. Cada beat = un componente en `infra/remotion-render/src/beats/` (la **fuente viva del catálogo**, ~39 beats — leer la carpeta, no fiarse de un número fijo). Theme y paleta semántica en `src/theme.ts`.
2. **3D hero (cuando aplica):** Blender 5.1, OptiX en la RTX 4060 → PNG alpha → WebM VP9 yuva420p → Remotion `<OffthreadVideo transparent>`. Para objetos hero y set-pieces con volumen real.
3. **Voz:** ElevenLabs `/with-timestamps`, voz **Asgard `eleven_v3`** (id `lJtjZw9ZjSbD9Zs9bOWq`). Los timestamps atan cada beat al audio (§7).
4. **Ensamblado:** FFmpeg vía `infra/assembler/build916.py` — VO + renders + música ducked + SFX + xfade en costuras → `out/{slug}/{slug}_FINAL_916.mp4` (9:16).

**Creatividad con barandales (NUNCA prompt en blanco):** un **director** castea de un **catálogo cerrado de set-pieces** (`infra/n8n/setpiece_catalog.json` — servilleta ✅, periódico, hero-shot, etc.) en vez de inventar libremente cada video. Da variedad SIN romper la coherencia ni reintroducir el error de "cambio no solicitado".

**Cadena de filtros QC (sube el piso de calidad sin humano):**
- **Filtro A** (`infra/qc/filter_a.py`): programático — paleta, luminancia, safe-areas, motion. Exit 1 = FAIL.
- **Filtro B** (`filter_b_prepare.py`): juez visual del beat vs. la referencia 0x100x.
- **Filtro C** (`filter_c_prepare.py`): video completo + loudness.
- **Gate humano:** Manuel aprueba/rechaza el MP4 final por **Telegram** (`infra/distribution/telegram_bot.py`).

**Orquestación + distribución:** el motor real es un orquestador Python (`infra/n8n/producir.py`) corrido por Windows Task Scheduler — **NO n8n como servidor** (importado pero 0 ejecuciones, ver §9). Producir LOCAL (Blender/RTX 4060) + publicar NUBE (Supabase + Edge Function). `infra/distribution/publish_ig.py` postea a IG (Graph API, ya probado).

**CONGELAMIENTO DE GASTOS (2026-06-19, más estricto que la v2.1):** todo el pipeline corre **$0**. CERO herramientas/suscripciones/APIs nuevas de paga sin OK explícito de Manuel. AE (~$23/mo) + Envato Elements ($16/mo) quedaron CANCELADOS junto con el método de plantillas. Único costo marginal posible, siempre avisando antes: créditos puntuales de gpt-image-1 (~$0.17 USD/≈$3 MXN por asset) y planner Anthropic (~$0.03-0.05/guion). Ver `docs/EXPENSES.md` y `memory/feedback_congelamiento_gastos.md`.

**Extensibilidad:** el pipeline es modular por-segmentos (cada beat es un componente aislado) para que (a) Manuel lo toque él mismo y (b) agregar a futuro un segmento de presentador/avatar realista sea ADITIVO, no un rewrite.

**Pipeline 3D validado:** Blender local RTX 4060 (OptiX ~2.3s/frame) → PNG alpha → WebM VP9 yuva420p → Remotion `<OffthreadVideo transparent>`. Ver `memory/project_dinero_ia_3d_pipeline.md`.

---

## 9. Qué está MUERTO / no usar (NUNCA re-proponer)

Cada uno se probó y Manuel lo rechazó. Re-proponerlos quema su confianza.

- **Plantillas Envato AE + Nexrender + n8n** (era el §8 hasta 2026-06-10): look genérico/viejo, 3 lenguajes visuales incoherentes por video. **RECHAZADO en gate 2026-06-11.** AE + Envato Elements CANCELADOS. Plainly/pagar AE solo quedaría como motor PUNTUAL de charts, NO decidido — no pagar sin replantear con Manuel.
- **Que Claude arme el video desde cero** en AE/ExtendScript/Remotion-puro como "yo lo genero": salió "chafa" (test007/8/9). El camino vigente es recrear 1:1 un plano real, no inventar dirección de arte.
- **Veo / IA generativa** (Kling/Hailuo/Higgsfield/Seedance) como **medio principal**: "falta muchísimo", cero gráficas, look-IA. Queda SOLO como posible b-roll dentro del sistema propio.
- **Diseñador / freelancer externo** (ni one-time): PROHIBIDO. El sistema es 100% nuestro y automatizado.
- **n8n como servidor de orquestación:** `workflow_dinero_ia.json` está importado pero con 0 ejecuciones — nunca produjo un video. Reemplazado por `producir.py` + Windows Task Scheduler.
- `docs/standards/VISUAL.md` v1.0 — arquitectura gpt-image-2 + Seedance + agentes A5/A8. Superseded por este doc.
- **`docs/ROADMAP.md` v6** — era SaaS/cloud ($270-440/mo: n8n cloud, Seedance, Supabase, ContentStudio, Blotato, Beehiiv). SUPERSEDED por el sistema propio $0; se mantiene solo como audit trail.
- Estética "viral de alto impacto" (v11): fondos que cambian de color, números gigantes variables, springs bouncy. RECHAZADO.
- "Otra pasada de 2D genérico" como camino a premium. El 2D es el PISO (datos/charts); no es el diferenciador.
