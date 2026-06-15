# Dinero IA — Style Bible (FUENTE DE VERDAD ÚNICA)

**Versión:** 2.1 · **Fecha:** 2026-06-03 · **Estado:** ACTIVO
**Reemplaza a:** `docs/standards/VISUAL.md` (v1.0 — arquitectura muerta gpt-image-2/Seedance, NO usar)
**Base empírica:** teardown frame-by-frame de @0x100x + 13 creators benchmark + 8 directivas de Manuel + 3 iteraciones de quality-bar (test015→test017).
**v2.1:** §8 cerrada — método DECIDIDO (plantillas Envato + Nexrender + n8n, sin diseñadores) + congelamiento de gastos.

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
8. **Activo de marca recurrente (firma):** UN objeto/mascota propio en CADA video, reconocible en 0.5s. **PENDIENTE: definir cuál es la mascota de Dinero IA** (será el primer asset 3D orgánico).

---

## 6. Reglas de charts (locked)

- Durante un chart NO hay título/subtítulo de texto encima (compite con la voz). El icono indicativo arriba SÍ.
- Si hace falta contexto, va en un **beat de texto SEPARADO antes** del chart.
- Línea dibujada izq→der, semántica verde→rojo, dot glowing, labels de dato, valor final highlighted. Oscuro y glowing, no barras planas.
- La voz hace el storytelling completo durante el chart.

---

## 7. Pacing y audio (BUG a arreglar, independiente del método)

**Problema reportado (test017):** "despasado, silencios raros." **Causa raíz:** los beats usan duración FIJA (`duration_frames`) no atada a la duración real del voiceover → cuando la voz termina antes/después del beat, aparece aire muerto o el corte cae a destiempo.

**Fix:** tomar timestamps de palabra de ElevenLabs (API devuelve timing por carácter/palabra) y **atar cada beat al audio** — el corte cae con la voz, sin silencios. Regla: ningún beat queda en silencio salvo un "breath beat" INTENCIONAL (§5.6). Esto es ortogonal al fork de método; se arregla en cualquier camino.

---

## 8. EL MÉTODO (DECIDIDO 2026-06-03)

Probado empíricamente 3 veces: **generar-desde-cero topa por debajo de la barra de Manuel.** El gap es **craft / dirección de arte**, no técnica ni medio. La forma más barata de ADQUIRIR craft es partir del trabajo de un pro, no seguir generando de cero.

**Decisión (Manuel, 2026-06-03):** rechazó contratar diseñadores (esperar/pagar de más) y recrear 1:1 en código (sin sentido). Camino elegido:

> **Plantillas premium de marketplace + automatización propia.**
> 1. **Diseño base:** plantillas AE premium nivel 0x100x compradas en **Envato Elements** ($16/mo, ya autorizado). El marketplace es la fuente de craft; NO se contrata a nadie.
> 2. **Automatización:** **Nexrender** (gratis, open-source) llena datos + renderiza AE headless, orquestado por **n8n**. Envato NO tiene API de render; es solo el origen del asset.
> 3. **Datos/charts variables:** los maneja el código/CSV (paleta semántica §2-3 inyectada por job).
> 4. **3D propio cuando aplique:** pipeline Blender validado (abajo) para hero objects + mascota.

**Restricción dura (CONGELAMIENTO DE GASTOS, 2026-06-03):** After Effects (~$23/mo tras trial 7 días) es la **ÚLTIMA herramienta de paga autorizada**. CERO suscripciones nuevas sin OK explícito de Manuel. Si AE no valida el camino dentro del trial → cancelar (costo $0), NO pivotar a otra herramienta de paga. Ver `docs/EXPENSES.md` y `memory/feedback_congelamiento_gastos.md`.

**Requisito de extensibilidad:** el pipeline debe ser modular por-segmentos (intro → datos → outro) para que (a) Manuel pueda ajustarlo él mismo con el tiempo y (b) agregar a futuro un segmento de presentador/avatar realista (HeyGen/Synthesia/D-ID) sea ADITIVO, no un rewrite. Por eso AE-templates (editables visualmente) ganan sobre Remotion-puro cuando empatan.

**Estado de validación (2026-06-04 — MÉTODO VALIDADO ✓):** Nexrender 1.63.3 ✓. AE 2026 + aerender ✓. Render base de "Dark Numbers" (Pack 2) salió OK en 2m19s y **Manuel lo aprobó: "se ve muy bien"** — el craft de una plantilla de marketplace SÍ clarea la barra (primera vez en el proyecto). Esto confirma §0/§8.
**Arquitectura multi-plantilla por COMPONENTE:** ninguna plantilla sola hace todo. Se ensamblan beats:
- **Beat de número** → "Dark Numbers" (validado). Solo contadores, NO tiene charts.
- **Beat de chart** (pie/línea/barras) → **Pack 3 "Modern Infographic Data Visualization"** (Envato, GANADOR): oscuro, 4K 3840x2160 60fps, glow, control de Color por elemento, 20 escenas modulares. Varias YA son financieras: `Infographics_02` Growth Stocks (línea), `_03` Portfolio Balance, `_07/_08` ±% verde/rojo, `_09` Investment Growth, `_11` Crypto Wallet (BTC/ETH/USDT). Archivo: `infra/ae-pipeline/templates/Pack3_DataViz.aep`.
- **Banco de layouts (no premium tal cual)** → Pack 4 "Modern Animated Infographics" (CandyMustache): enorme y recoloreable PERO base plana/clara/corporativa (como Pack 1). Usar solo para tomar prestado un layout puntual, ya oscurecido. NO como cara principal.
- **Descartado:** Pack 1 "Statistics CSV" (blanco/plano).
- **Hero/mascota 3D** → pipeline Blender (abajo).
**Pendientes técnicos:** conseguir plantilla de charts oscura; reencuadre 16:9→9:16; tematizar a paleta §3; inyectar `data/payload_cetes_vs_banco.json` vía Nexrender; ensamblar beats en n8n.

**Pipeline 3D ya validado (complementa, no reemplaza):** Blender local RTX 4060 (OptiX ~2.3s/frame) → PNG alpha → WebM VP9 yuva420p → Remotion `<OffthreadVideo transparent>`. Ver `memory/project_dinero_ia_3d_pipeline.md`.

---

## 9. Qué está MUERTO / no usar

- `docs/standards/VISUAL.md` v1.0 — arquitectura gpt-image-2 + Seedance + agentes A5/A8. Superseded por este doc.
- Estética "viral de alto impacto" (v11): fondos que cambian de color, números gigantes variables, springs bouncy. RECHAZADO.
- "Otra pasada de 2D genérico" como camino a premium. El 2D es el PISO (datos/charts); no es el diferenciador.
