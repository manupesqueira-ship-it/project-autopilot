# PLAN GRAMÁTICA VISUAL — v4 (canónico)

> Fuente de verdad del carril **reels** de Dinero IA tras GATE 0 (2026-06-27).
> Sustituye, para esta fase, a `PLAN_MOTOR_AI_v3.md` y `PLAN_SALTO_CALIDAD_v2.md`
> (no los borra; los enmarca). El newsletter es OTRA terminal y NO entra aquí.

---

## 0. En una frase

La plomería ya funciona end-to-end (tema → guion → voz → render → QC → Telegram →
publica). Lo que falta NO es técnico: falta una **gramática visual validada a mano**.
Dejamos de reinventar el arte por video; construimos **masters** (unidades visuales
excepcionales validadas a mano), los documentamos, y automatizamos **solo** lo aprobado.

---

## 1. Diagnóstico (por qué v4 existe)

- Se automatizó una disciplina creativa **antes** de definir manualmente un sistema
  creativo que funcione. El modelo intenta **reinventar la dirección de arte en cada
  video** → resultados incoherentes (dos mundos, tramos estáticos, conceptos literales).
- La solución NO es más agentes / modelos / shaders / templates / componentes. Es:
  1. crear a mano UNA unidad visual excepcional,
  2. entender por qué funciona,
  3. convertirla en reglas/presets/componentes (un **master**),
  4. automatizar SOLO lo que ya tiene solución visual aprobada,
  5. mantener un **gate humano** para gusto / verdad / publicación.

## 2. Doctrina de medios — FINAL (GATE 0, decisión 1)

> **Motion determinista domina la ESTRUCTURA. I2V domina el IMPACTO.**

- **Motion graphics deterministas** (Remotion/código) = la **columna temporal y
  estructural** de cada reel. Son la mayoría del metraje. Deterministas **≠** planos:
  cámara, parallax, transformación, progresión, tipografía cinética, gráficas que
  evolucionan, transiciones intencionadas. **Nada estático** sigue vigente.
- **I2V** (Kling/fal.ai) = **solo** momentos de máximo impacto perceptual (hook, héroe,
  clímax, metáfora física, transición extraordinaria). **Sin cuota rígida** (~10–25% como
  orientación; varía por historia). Recurso extraordinario, no el lecho de cada beat.
- **Blender** = objetos hero puntuales que necesitan consistencia (moneda, caja fuerte,
  objeto simbólico). No para que cada beat sea 3D.
- **Datos / logos / cifras / mapas / charts** = SIEMPRE deterministas (la IA no rinde
  texto/cifras exactas confiables). Los logos se bajan como vector real, no se generan.
- La **integración** entre capas viene de grade / grano / cámara / blur / profundidad /
  curvas de movimiento / transiciones / ritmo — no de generar todo con IA.

## 3. Estrategia: 3 Golden Reels que DEFINEN el sistema

No son para llenar el calendario. Son las **piezas-patrón** de las que se extraen los
masters. Orden **C → B → A** (GATE 0, decisión 2):

- **C — comparación / decisión** (primero): mucho dato exacto, menos cine, 2 escenarios,
  resultado visible. Tema fijado: *"$100,000 MXN durante 12 meses: efectivo vs. invertir
  a una tasa determinada, descontando inflación."*
- **B — explicación**: un concepto (tasa real / inflación / costo de oportunidad) +
  metáfora visual consistente + 1–2 charts + cambio de estado claro.
- **A — noticia**: objeto/escena hero + cifra principal + chart simple + payoff.

Criterio de aceptación de cada golden reel: *"Esto es Dinero IA; los futuros videos deben
sentirse de la misma familia."*

## 4. El sistema de masters

Un **master** = una unidad visual validada a mano, documentada y parametrizada, lista para
que el LLM la **ejecute** (no la reinvente).

- **`infra/grammar/masters/master.schema.json`** — contrato de un `master.json`
  (id, familia, objetivo narrativo, layout/slots, timing/curvas, motion permitido/prohibido,
  paleta semántica, tipografía, contrato de datos + límites de caracteres, criterios de
  aceptación, errores comunes, cuándo NO usarse, procedencia).
- **`infra/grammar/masters/registry.json`** — índice de masters **aprobados** (hoy vacío)
  + los **planeados** que se derivarán del Reel C.
- **`infra/grammar/masters/FICHA_TEMPLATE.md`** — la ficha humana (documentación) de cada
  master, espejo del schema.
- Las **composiciones Remotion** de cada master aprobado vivirán en
  `infra/remotion-render/src/masters/` (código), derivadas de styleframes aprobados.

### Flujo corregido (una idea mala muere en el STORYBOARD, no tras el master de audio)

```
Tema → guion editorial → 3 conceptos visuales en 1 frase → storyboard 8-12 frames →
styleframes clave → animatic baja-res → APROBACIÓN visual → producción → QC → Telegram → publicación
```

Por escena importante: **3 styleframes** (inicial / máxima-información / salida). NO animar
hasta que funcionen como imágenes (una animación no rescata una mala composición).
Implementar UNA escena a la vez desde styleframes + tabla de keyframes ("no agregues
decisiones creativas"). Comparar side-by-side vs referencia (loop, 0.25×, overlay).
Aprobar → convertir en **master documentado**.

## 5. Familias de escena + dirección estructurada

Reducir el sistema a **6–8 familias** con variantes CONTROLADAS (no ~50 componentes sueltos):
1) hook tipográfico · 2) objeto hero · 3) cifra protagonista · 4) comparación ·
5) chart de tendencia · 6) mapa/geografía · 7) cadena causal · 8) payoff + CTA.

El director (LLM) **no** emite instrucciones abiertas. Emite una **selección estructurada**
de un menú cerrado, p.ej. `{scene_family, subject, nodes[], camera_preset, tempo,
semantic_color, transition_out}`, validada por `validator.py`.

**No toda noticia es reel.** Scoring por historia (`editorial_relevance, audience_impact,
visualizability, shelf_life, evidence_quality`) → router `reel | carousel | story |
newsletter | reject`. La automatización NO fuerza un reel diario cuando el tema no lo merece.

## 6. Herramientas de dirección que se construyen AHORA

Cada una existe **solo** para acercar la primera escena aprobable del Reel C. No son
plataforma:

- **Teardown mínimo** (`infra/grammar/teardown/`): descompone un MP4 de referencia en
  escenas usando múltiples señales (cortes duros, histograma, flujo óptico, texto
  aparece/desaparece, cambios de composición, golpes de audio) + **fronteras manuales**.
  Razón: para copiar el *timing/curvas* de una referencia hay que medirla, no adivinarla.
- **Storyboard Lab mínimo** (`infra/remotion-render/src/storyboardlab/`): crear styleframes,
  ver el storyboard, exportar PNG, mostrar safe-areas, comparar versiones, y graduar un
  styleframe aprobado a composición Remotion. Reemplaza a Figma (que queda **opcional**).
  Razón: resolver **composición** antes que animación, dentro del mismo renderer.
- **Comparación lado a lado** (`infra/grammar/sidebyside/`): referencia vs. nuestro
  (side-by-side + overlay 50% + loop 0.25×). Razón: el juicio es por píxeles, no por
  recuerdo.

## 7. Golden Reel C — alcance y masters objetivo

Brief en `infra/grammar/reel_c/` (`brief.md` editorial + `brief.json` máquina). Debe llevar:
fecha de corte explícita, tasa e inflación **verificadas**, supuestos visibles, escenario
ilustrativo, tratamiento fiscal correcto cuando aplique, conclusión educativa (no
recomendación individualizada). **Las cifras NO se inventan** → van como `<<verify>>` hasta
confirmarse con fuente.

Masters reutilizables a derivar del Reel C (GATE 0):
`ComparisonSplit · PrincipalCounter · NominalVsReal · InflationErosion · OutcomeReveal · DecisionClose`.

## 8. Guardrails de alcance (lo que NO se hace)

- No generalizar antes de necesitarlo; no construir una plataforma completa; no agregar
  abstracciones a futuro.
- No tocar el pipeline probado end-to-end (n8n/qc/assembler/voz/Composition existente).
  Lo nuevo vive aislado en `infra/grammar/` y `src/storyboardlab/` (registro additivo).
- No producir el reel completo todavía; no auto-aprobar estética. **El fundador dirige; el
  LLM implementa.**
- No seguir ampliando catálogo de componentes: cada componente nuevo se DERIVA de una
  escena ya validada.
- Cada pieza debe justificar **cómo acerca la primera escena aprobable**.

## 9. Plan por fases (con gates)

- **Fase 0 — andamiaje de dirección (AHORA, $0):** plan persistido + schema/registry/ficha +
  marcado legacy + teardown mínimo + side-by-side + brief Reel C validado + Storyboard Lab
  mínimo + lista de pendientes-por-referencia. **Gate:** Manuel revisa el andamiaje.
- **Fase 1 — teardown de la referencia (al llegar el MP4):** contact sheet, shot list,
  timeline, waveform, tabla frame-a-frame, motion primitives. **Gate:** Manuel valida la lectura.
- **Fase 2 — storyboard + styleframes de la escena 1 (Reel C):** 8–12 frames sin animar →
  3 styleframes. **Gate:** aprobación visual como imagen.
- **Fase 3 — 1 escena implementada + master:** animar desde tabla de keyframes; comparar
  vs. referencia; documentar el master. **Gate:** píxeles vs. barra de Manuel.
- **Fase 4 — resto del Reel C con masters → animatic con voz → QC → publicar → medir retención.**
- **Fase 5 — repetir B y A; parametrizar; automatizar SOLO lo aprobado.**

## 10. Diferido hasta el MP4 de referencia

Ver `infra/grammar/PENDIENTE_REFERENCIA.md`. Resumen: el teardown real, la extracción de
timing/curvas, y el side-by-side con referencia esperan el archivo + segundos exactos. Todo
lo **independiente de referencia** (schemas, brief, lab, estructura de herramientas) avanza ya.

## 11. Reglas operativas del agente

Evidencia, no afirmaciones (medir píxeles/MP4 real). Slices cortos y rechazables. Sin
inventar progreso. Sin expandir alcance. Reversibilidad (rama + commit + preview). Artefactos
de revisión por escena (MP4 + frames inicial/medio/final + side-by-side + JSON + diffs).
Verdad editorial primero; moneda explícita (USD o MXN); registrar todo gasto en
`docs/EXPENSES.md`; $0 por defecto, sin herramientas de paga nuevas sin OK.
