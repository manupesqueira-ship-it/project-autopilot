# ESTADO DINERO IA — mapa maestro (fuente de orientación)

> **Propósito:** un solo lugar para saber QUÉ es Dinero IA, qué sirve, qué está muerto,
> en qué iteración vamos y hacia dónde. Si te sientes perdido entre tantos pivots, empieza aquí.
> **Creado:** 2026-07-01. **Cubre 2 repos:** `project-autopilot` (reels) + `C:\Users\manup\dinero-ia-web` (web).
> No re-litigar caminos muertos (§5). Ante duda de estrategia: `PLAN_MOTOR_AI_v3.md` (reels) y §4 (arte).

---

## 1. El modelo mental — Dinero IA son 3 capas

```
                    DINERO IA (el negocio)
                            │
     ┌──────────────────────┼──────────────────────┐
  ① PRODUCTO            ② MARKETING             ③ STOREFRONT
  (lo que vendes)     (cómo atraes)          (dónde convierten)
     │                      │                       │
  Guía educativa      Reels de IG             Landing web
  semanal             @dinerolatam            dinero-ia-web
  personalizada       ────────────            ─────────────
  (país/objetivo/     repo:                   repo:
   etapa · 6 piezas)  project-autopilot       dinero-ia-web
```

Las 3 comparten **UN solo lenguaje visual** (biblia igloo.inc, §4). La montaña de la web y el
clip del alpinista son piezas que cruzan ② y ③ — por eso se sienten enredados: comparten
herramientas y estética, pero tienen estados y planes distintos.

---

## 2. ① EL PRODUCTO (canónico, 2026-06-29)

**Qué es:** guía educativa **semanal personalizada** según país, objetivo y etapa financiera.
Tagline: *"Tu dinero cambia cada semana. Tu plan también debería."*
Entrega **6 piezas**: (1) qué cambió · (2) por qué importa para SU contexto · (3) una prioridad
financiera general · (4) una acción educativa concreta · (5) una guía/herramienta localizada ·
(6) seguimiento de progreso.

**NO es:** newsletter/boletín · NO es asesoría registrada.
**Diferenciador:** personalización + seguimiento ("una misma noticia → planes distintos").

**Límites de cumplimiento (DUROS, CNBV):** no recomendaciones individualizadas de compra/venta ·
no % de cartera · no elegir inversiones · no ejecutar · no promesas de rendimiento. Todo va en
marco educativo. Declarar los límites SUBE la confianza (úsalos como prueba, no los escondas).

**"La Cima":** metáfora del SIGUIENTE PASO (claridad/hábito), NUNCA riqueza ni un monto.

---

## 3. ESTADO REAL POR CAPA

### ② REELS — `project-autopilot` · la plomería FUNCIONA, el director NO existe
**Vivo y validado ($0):**
- Pipeline end-to-end: `python build916.py guion_<slug>.json all` → voz ElevenLabs (Asgard,
  con timestamps) → render beats Remotion (catálogo ~61 beats) [+ Blender 3D] → ensamblado
  FFmpeg (música ducked + SFX + xfade) → `filter_delivery.py` (gate duro) → `out/{slug}/*_FINAL_916.mp4`.
- Orquestador completo = `infra/n8n/producir.py` (elige tema → produce → caption → sube Supabase →
  **gate humano Telegram** → encola → postea). **n8n MUERTO** (0 ejecuciones).
- QC automatizado (activo fuerte): validador de guion R1–R11 (34/34), filtros A/B/C, candado
  anti-slideshow `filter_motion.py` (8/8), `text_overlap_check.py`, gate de entrega duro.
- **6+ reels finales entregados.** Último: *El Salvador / apuesta Bitcoin* (30-jun, primer hero i2v de pago).

**Lo que FALTA (el cuello real):**
- **El director-LLM NO existe como código** — solo specs en `infra/director/`. El plan lo llama
  *"el sistema/workflow que faltaba"* y admite *"la pieza DIFÍCIL; NO está resuelta aún."*
- **GATE 1 (gratis, pendiente de Manuel):** juzgar shot-lists reales en papel.
- **GATE 2 (gasto, pendiente):** primer beat i2v de pago juzgado contra tu barra.
- Coincide con tu lección guardada: *"el cuello es MI dirección creativa"*, no el medio.

### ③ WEB — `dinero-ia-web` · commerce funciona, la landing no refleja la visión
**Vivo:**
- Stack Next 16 + React 19 + R3F + Tailwind 4. Landing `/` compuesta (hero+form, mockup, perks,
  ticker, número que crece, montaña, stats, **simulador**, precios).
- **Commerce real:** auth Supabase + checkout **Stripe** + cuenta/billing + archivo (`/archivo`) + `/n/[slug]`.
- Montaña viva = `MontanaAscent.tsx` (DOM-video scrub + brasas), motor validado ("ya fluye mucho mejor").

**3 DESAJUSTES a corregir (aquí está el "¿vamos bien?"):**
1. **La montaña buena vive en `/demo/ascenso`, NO en la landing.** `/` usa la montaña vieja
   `MountainClimbFeature` (foto + ruta, marcada `"PRUEBA"`). El trabajo bueno no lo ve el público.
2. **La landing sigue en framing NEWSLETTER**, no en el producto nuevo (guía semanal personalizada,
   landing producto-primero de 11 secciones que muestra un plan real). La visión nueva no está construida.
3. **La web no habla la biblia de arte.** Usa `#08090d` + esmeralda + Geist (SaaS correcto), no el
   igloo.inc dictado (`#070707` + grotesca finísima + minimalismo extremo). La estética locked no está aplicada.

**Basura para limpiar:** ~110 `tmp_*` en la raíz, logs, `.venv_i2v/`, `tools/`, perfiles Chrome; `DemoNav` desactualizado.

---

## 4. LOOK & FEEL — biblia de arte UNIFICADA (igloo.inc) · vale para video Y web

- **Lienzo:** vacío NEGRO MATE `#070707`, espacio negativo inmenso, UN elemento a la vez.
- **Paleta:** negro mate + azules fríos/carbón + UN acento cálido (fuego naranja) o verde esmeralda.
  Color solo cuando significa algo. (Convive con color semántico: verde=sube/marca · rojo=pérdida ·
  dorado=dinero · morado=solución.) CERO neón/saturación/viral.
- **Luz:** volumétrica suave, bloom delicado, sombras frías.
- **Movimiento:** lento, con easing, deliberado (estilo GSAP). La cámara casi no se mueve.
- **Tipografía:** grotesca finísima, MAYÚSCULAS, tracking ancho, baja opacidad, una línea a la vez.
- **Material:** CG de alta (vidrio/hielo/brasas) + niebla + grano. Nada de clipart/stock.
- Refs: **igloo.inc, Lusion, ManvsMachine**. Reparte de medios: objeto héroe = i2v/Blender ·
  geografía/banderas/datos/logos = CÓDIGO (la IA destroza texto; logos = vector real).

---

## 5. CEMENTERIO — caminos y herramientas MUERTOS (no re-proponer)

Cada uno se probó y se rechazó. Re-proponerlos quema confianza.

| Muerto | Por qué |
|---|---|
| **n8n** como orquestador | 0 ejecuciones jamás; reemplazado por `producir.py` + Task Scheduler |
| **After Effects + Nexrender + plantillas Envato** | look genérico/incoherente; suscripciones canceladas |
| **Sora 2 / Veo / Runway** como medio | foto-realistas, caros; el plan los prohíbe |
| **Diseñador / freelancer externo** | prohibido; sistema 100% nuestro |
| **Craft desde cero por Claude en código** (AE/Remotion/Blender como HERO) | "chafa" (test007/8/9; monedas hero; charts a mano) |
| **IA generativa como MEDIO PRINCIPAL del reel** | look-IA, cero gráficas. Sobrevive SOLO como hero ~10-20% |
| **Montaña web:** pico de vidrio (`HeroAscent`), hielo R3F (`IceAscent`), GLTF pro (`ModelAscent`), fuego-textura (`MontanaScene`) | 4 intentos superados; vivo solo `MontanaAscent` |
| **Data-viz 2D a mano pulida** | "dramáticamente aburrido"; replantear a craft pro/movimiento |
| **Dividir el look en varias tabs** | sale incoherente; 1 fuente de verdad |

**Regla:** el i2v es hero-layer (objeto/personaje ~10-20%), NO el lecho de cada beat. El grueso = código.

---

## 6. HERRAMIENTAS VIVAS

- **Render reels ($0):** Remotion 4.x · Blender 5.1 (RTX 4060/OptiX) · FFmpeg.
- **Voz:** ElevenLabs `eleven_v3`, voz Asgard `lJtjZw9ZjSbD9Zs9bOWq`.
- **i2v hero (pago):** Higgsfield Plus $50/mo (Seedance/Kling) · fal.ai/Kling ~$0.56–0.90/clip · Seedream (stills).
- **Web:** Next 16 · R3F · Tailwind 4 · Supabase (auth+storage) · Stripe · Lenis.
- **Dirección/planner:** Claude.
- **Gastos vs objetivo:** vas MUY por debajo del techo (~$5,000 MXN/mo objetivo). Recurrente real ≈
  Higgsfield $50 + ElevenLabs (centavos) + Anthropic $1–3/día. Colgando: Gemini ~$500 MXN prepago sin usar.

---

## 7. ROADMAP — el próximo salto NO es más código, es DIRECCIÓN

**Patrón raíz:** la plomería va por delante de la dirección. Toca **converger**, no explorar más.

**② Reels →** construir director-LLM → **GATE 1** (shot-lists reales en papel, $0) → **GATE 2**
(primer i2v de pago juzgado). El resto ya existe.

**③ Web →** (1) reconstruir `/` a producto-primero (11 secciones, mostrar un plan semanal real);
(2) aplicar biblia igloo.inc al theme; (3) meter `MontanaAscent` a la landing y jubilar las 4
muertas + `MountainClimbFeature`; (4) limpiar basura.

**① Producto →** confirmar que la guía semanal personalizada se define/produce cada semana (cómo se genera).

**Regla de convergencia:** UN frente a la vez (no dividir). Decisiones de dirección se cierran con
Manuel ANTES de construir. Cada entrega = capacidad/tema nuevo, no repetir demos.
