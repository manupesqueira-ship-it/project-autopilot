# Investigación: la fuente del motion design (2026-07-03)

8 agentes en paralelo, ~90 fuentes verificadas. Contexto: Manuel pausó el build ("cada cosa tiene
corrección; el motion sale bajo la barra") y dio luz verde a investigar de dónde sale motion de clase
mundial AUTOMATIZABLE. Decisiones previas de Manuel: reels = MISMO mundo visual que la página
(igloo/Terminal: #070707, hueso, esmeralda en la transición, grotesca fina + mono); masters congelados
"literalmente perfectos".

**Plan resultante (canónico):** https://claude.ai/code/artifact/85670f72-aabc-40d3-b9f0-0d7d12b5419a
**Plan maestro del proyecto (Manuel):** https://claude.ai/code/artifact/2e1e3536-95de-4b7a-818e-0cf03b1302b3

## Veredicto en una línea

Remotion se queda como renderer; el TIMING sale de tokens publicados (H&R 2007, MD3, Carbon, Netflix,
Bostock — ver `motion_specs.txt`, tiene la tabla completa con fuentes); el MODELO operativo es broadcast
(Vizrt/CNBC/BBC: masters con estados congelados, el director solo llena campos — ver
`masters_workflow.txt`); GSAP-en-Remotion (timeline pausado + seek por frame) unifica el lenguaje
web↔reels (ver `gsap_remotion.txt`); la línea "trabada" se arregla con d3-shape + evolvePath
(dashoffset por longitud, ver `diagnostico.txt`).

## Archivos

- `gsap_remotion.txt` — determinismo GSAP en Remotion (patrón HeyGen), SplitText gratis, gotchas duros
- `echarts_native.txt` — capturar la animación nativa de ECharts con reloj virtual (viable, fase 2)
- `motion_canvas.txt` — abandonado; robar el patrón time-events-as-JSON (sync con TTS)
- `cavalry_otros.txt` — Cavalry GRATIS (Canva abr-2026) como mesa de autor → Lottie; Jitter/Rive/Fable no
- `motion_specs.txt` — LA TABLA de tokens de timing con fuente por número (congelar como motion.tokens.json)
- `diagnostico.txt` — por qué el draw-on se ve "trabado" + fixes exactos (evolvePath, Bostock racing, countUp)
- `referencias.txt` — el tablero de 10 referencias (7 enviadas a Telegram msgs 115-122, 2 descartadas en píxeles)
- `masters_workflow.txt` — gobernanza: tokens W3C + masters broadcast + lock de estudio (picture-lock)

## Estado al cierre de sesión

Pendiente de Manuel: (D1) SÍ/NO a las 7 referencias del tablero; (D2) aprobar el plan/proceso de lock;
(D3) ¿Cavalry como mesa de autor en R2? NADA se construye hasta su OK (regla dura 2026-07-03).
