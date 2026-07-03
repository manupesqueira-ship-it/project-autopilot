# DINERO IA — DOCUMENTO CANÓNICO (fuente ÚNICA de verdad)

> **Este doc reemplaza como fuente de verdad a:** la estrategia de `CLAUDE.md`, la
> `Style Bible`, `PLAN_SALTO_CALIDAD` v1/v2, `PLAN_MOTOR_AI_v3`, `PLAN_GRAMATICA_VISUAL_v4`,
> `ROADMAP.md` y `DECISIONS.md`. Esos quedan como **histórico** (audit trail), no como reglas vivas.
>
> **Regla de oro:** si algo contradice este documento, gana este documento.
> `CLAUDE.md` sigue siendo válido SOLO para lo técnico (cómo correr + gotchas).
>
> Última actualización: **2026-07-01** · Auditoría completa contra el repo real.

---

## 1. El producto (no ha cambiado en 6 pivots — es tu núcleo estable)

Reels verticales 9:16 de **finanzas personales LATAM en español**, colgados de un hook macro
de actualidad. **Moat = precisión cultural** (CETES, pesos, inflación, AFORE, modismos), no el look.
Voz narra (Asgard, ElevenLabs). $0 en el render; gasto solo en el impacto i2v.

---

## 2. Estado REAL del sistema (verificado 2026-07-01)

**Lo que funciona (tu activo):**
- Pipeline end-to-end $0: guion → voz → render Remotion → ensamblado FFmpeg → QC → gate Telegram → publicar. Orquestador real = `infra/n8n/producir.py` (Python, **no** n8n).
- 60 componentes de beat en `remotion-render/src/beats/`.
- **10 reels** producidos. **18 temas aprobados en cola + 8 guiones escritos** sin producir.
- Auto-publicación IG probada (video #1 ya salió a @dinerolatam).
- Gates en píxeles: `filter_delivery.py` (voces/loudness) + `text_overlap_check.py` (empalme).
- Gasto total del proyecto: **~$180–210 USD**. Única suscripción viva: Higgsfield $50/mes.

**Lo que NO está listo (la verdad incómoda):**
- Solo **1 de 10 reels** (El Salvador BTC) usa el look nuevo — y **no cumple la barra** (Manuel).
  Se construyó a mano sin gramática fija → cada beat fue una pelea → caro de parchar. Se retira como aprendizaje, no se sigue parchando.
- **i2v nunca se ha ejecutado en vivo** (motor de paga sin validar; espera gate de Manuel).
- **Planner/Director LLM congelado** — el guion se escribe a mano.
- **Blender huérfano** del render (hoy el pipeline usa gpt-image, no Blender).
- Basura acumulada en raíz (test00*.mp4, test_voice_v*.mp3) y beats sin uso real.

---

## 3. Doctrina RESUELTA (fin de las contradicciones)

Estas eran las 3 grietas que hacían sentir que "las reglas se mueven". Quedan cerradas aquí:

1. **Rol del i2v (Higgsfield/Kling):** i2v = **IMPACTO puntual (~10–25% del metraje)**; el
   motion determinista en código domina la estructura. (Se adopta v4. Supera la prohibición
   literal de la Style Bible §9 y CLAUDE.md, que decían "solo b-roll" — quedan obsoletas.)
2. **El cuello de botella real:** NO es el banco de temas (sobra material: 18+8 esperando).
   Es **(a) la gramática visual sin fijar** y **(b) que nunca se ha publicado en serio**.
3. **Quién dirige:** el **fundador (Manuel) dirige, el LLM implementa**. Nunca inventar arte
   desde cero; el sistema **selecciona de un menú validado a mano**.

**Decisiones bloqueadas (no re-litigar sin Manuel):** un solo theme consistente, NO viral ·
color semántico (verde=sube/marca, rojo=SOLO pérdida, dorado=dinero, morado=solución) ·
SIN subtítulos quemados · durante un chart no va título encima · datos SIEMPRE exactos con
moneda explícita · texto NUNCA sobre imagen (carriles hero/texto separados) ·
$0 default; presupuesto i2v ~$5,000 MXN/mes (techo $10,000) · nada de externos/freelancers.

---

## 4. MODELO OPERATIVO — "el estudio" (APROBADO por Manuel 2026-07-01)

**Principio rector:** *agente donde hay juicio que varía; código donde la regla es fija.*
(Los agentes fallaron antes por pedirles artesanía determinista. Brillan en decidir/escribir/dirigir/criticar.)

**Manuel = Showrunner.** Aprueba la gramática y el gate. No dibuja píxeles.

| # | Rol | Tipo | Trabajo | Entrada → Salida |
|---|---|---|---|---|
| 1 | **Scout** | 🤖 Agente | Encuentra tema, saca cifras **verificadas/exactas**, puntúa visualizabilidad | noticia → brief con datos + fuentes |
| 2 | **Guionista** ("traductor") | 🤖 Agente | Guion con gancho/arco/CTA en lenguaje que capta atención; entrenado con los mejores hooks + rúbrica | brief → guion JSON |
| 3 | **Director Creativo** | 🤖 Agente | Emite spec beat-por-beat SELECCIONANDO del menú de gramática (escena/gráfica/i2v/SFX/ritmo). Nunca inventa. | guion + menú → timeline JSON |
| — | Voz, render, gráficas, ensamblado | ⚙️ Código | Ya existe y funciona | timeline → MP4 |
| 4 | **Crítico / QC** | 🤖 Agente | Ve el reel armado contra la rúbrica, marca fallos (adversarial) + corre gates | MP4 → veredicto |
| — | Caption + publicar + medir | ⚙️ Código (+ agente ligero de copy) | Casi listo | MP4 → post + métricas |

**Candado de orden:** el Director Creativo (#3) **no se puede construir antes de que exista el
menú**. Primero se fija la gramática; después el director ordena de ella.

---

## 5. La GRAMÁTICA VISUAL (el menú que hay que construir y fijar)

~6 "masters" de escena, cada uno con **gráfica + SFX + movimiento horneados** y aprobados UNA vez:

`PrincipalCounter` (cifra titular) · `ComparisonSplit` (A vs B / invertido vs actual) ·
`NominalVsReal` (nominal vs real) · `InflationErosion` (la inflación comiéndose el dinero — tu moat) ·
`OutcomeReveal` (la consecuencia/payoff) · `DecisionClose` (cierre + CTA + open loop).

- **Gráficas:** se elige de este shortlist, NO de los 24 componentes sueltos (esa dispersión es
  por qué los reels se sienten inconsistentes).
- **SFX:** kit chico mapeado a tipo de beat (riser→reveal · impacto→caída · tick→conteo · whoosh→transición),
  no decisión por-video.
- Fuente viva del catálogo: `remotion-render/src/beats/`. La gramática es el subconjunto **aprobado**.

---

## 6. ROADMAP (orden de ataque)

1. ✅ **Este documento** + archivar los docs viejos como histórico.
2. **Construir y FIJAR la gramática** en 1 golden reel hecho bien (no parchar El Salvador):
   los 6 masters con su gráfica+SFX+movimiento, validados a mano por Manuel. *Aquí la calidad
   se diseña, no se parcha.*
3. **Levantar los agentes uno a uno**, cada uno enchufado a la gramática ya fija:
   Guionista → Director → Scout → Crítico.
4. **Correr el loop, publicar y medir** retención; iterar la gramática con datos reales.

---

## 7. Caminos MUERTOS (nunca reproponer — quema confianza)

n8n como orquestador (0 ejecuciones) · agentes Python que hacen artesanía · SaaS de publicación ·
video generativo como MEDIO principal · Claude armando el video en After Effects · templates Envato ·
AE+Nexrender · diseñador/freelancer externo · kit estático como "el producto".

---

## 8. Técnico

Cómo correr el pipeline + gotchas (fuentes Remotion, FFmpeg concat, loudnorm, UTF-8/BOM, etc.)
viven en **`CLAUDE.md` §pipeline y §gotchas** — esa parte de CLAUDE.md sigue vigente.
Gastos: `docs/EXPENSES.md`. Costo por corrida: `infra/assembler/ledger.json`.
