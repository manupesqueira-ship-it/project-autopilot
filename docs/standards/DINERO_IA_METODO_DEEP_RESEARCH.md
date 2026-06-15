# Dinero IA — Deep Research: cómo subir el nivel (método de producción)

> Fecha: 2026-06-04. Detona esto: el camino "construir gráficos a mano" (Remotion from-scratch y luego AE ExtendScript) produce output "chafa"/genérico. Rechazado por Manuel. Pregunta: ¿con qué herramienta y qué pipeline llegamos al nivel @0x100x?

## TL;DR — el hallazgo central

**El gap NO es el medio (AE/Remotion), es el MÉTODO: generar gráficos desde cero.**
Cavar el gráfico ícono por ícono / barra por barra converge SIEMPRE en genérico, sin importar la herramienta. La diferencia entre lo nuestro y @0x100x es **craft de diseñador**, no tecnología.

**La solución que converge en las 5 investigaciones:** dejar de generar desde cero y en su lugar **riggear plantillas premium de diseñador (Envato Elements) como comps-beat fijas, alimentadas por datos vía Nexrender**, voz ElevenLabs, hero 3D opcional en Blender, todo orquestado en UN workflow n8n parametrizado con nodos de QC automatizables + un único gate humano de aprobación.

Esto:
- usa SOLO cosas que ya tenemos / son $0 (AE, Nexrender, Envato Elements ya suscrito, ElevenLabs ya con cuota, Blender, ffmpeg, n8n).
- alcanza ~85–90% del nivel @0x100x sin contratar diseñador.
- es replicable/parametrizable (un beat = una plantilla + un JSON de datos).

---

## 1. ¿Sirve algún AI video tool para esto? — NO para charts

- Runway / Pika / Sora / Kling / Luma: generan B-roll, objetos 3D, ambiente. **NO pueden generar charts financieros precisos** (números exactos, barras a escala, ejes correctos). Alucinan dígitos y geometría.
- Veredicto: AI-video se queda como **aditivo** (hero shots, texturas, fondos 3D), nunca como el motor de data-viz. → Despriorizar la tarea de "probar 1 AI-motion tool" como camino principal.

## 2. Data-viz programática — la herramienta nueva que SÍ vale: Cavalry

| Herramienta | Costo | Headless/automatizable | Veredicto |
|---|---|---|---|
| **Cavalry** | **FREE** (CLI headless = Enterprise pago) | Sí en UI; CLI pago | Defaults grado-diseñador, lee CSV/JSON, charts premium. **Piloto recomendado** para beats de gráfica. |
| Revideo (MIT) | $0 | Sí, render API headless | Buen fallback OSS si queremos código. |
| ECharts SSR | $0 | Sí | Charts correctos pero estética "dashboard", requiere mucho styling. |
| Remotion from-scratch | $0 | Sí | YA probado → chafa. No volver. |

Cavalry gratis es lo único nuevo que vale meter al banco de pruebas. **CLI headless es de pago → respetar freeze; usar UI gratis para riggear, exportar manual.**

## 3. Render-as-a-service (Plainly, Creatomate, etc.) — NO migrar

Ya tenemos el mejor stack $0: **Nexrender (OSS) + AE + Envato + ElevenLabs + n8n + ffmpeg.** Los SaaS de render cobran por minuto/render y no dan más calidad que nuestro propio AE. No pagar.

## 4. Cómo consolidar en n8n (la parte que no sabías cómo armar)

Pipeline canónico de 6 etapas, UN solo workflow parametrizado por nicho:

```
1. GUION    → LLM genera/valida script JSON (beats, narración, datos, captions)
2. VOZ      → ElevenLabs with-timestamps → mp3 + timings (clava pacing)
3. VISUALES → Nexrender rellena plantillas Envato con datos (1 beat = 1 template + 1 JSON)
              (+ Blender hero opcional, + Cavalry chart opcional)
4. ENSAMBLE → ffmpeg: monta beats por timestamps + música + subs + mux
5. QC       → automatizable + 1 gate humano
6. PUBLISH  → (futuro) o entrega para revisión
```

**Nodos de Control de Calidad (lo que pediste, una por especificación):**

*Automáticos (ffprobe / ffmpeg):*
- Resolución == 1080×1920, fps, duración dentro de rango.
- Loudness LUFS (audio normalizado, -14 LUFS).
- Paleta: muestreo de frames + ΔE contra la paleta del Style Bible (detecta drift de color).
- Presencia de audio en todos los tramos (no silencios).

*Subjetivo (LLM/vision-judge):*
- Extraer N frames → modelo de visión los puntúa contra una **rúbrica @0x100x** (limpieza de fondo, jerarquía tipográfica, color semántico correcto, "se ve premium"). Score < umbral → rechazo automático con motivo.

*Humano (1 solo gate):*
- Nodo Wait con Approve/Reject. Único punto manual. Si rechaza, vuelve a la etapa marcada.

**Gotcha técnico n8n:** en n8n v2.0 el nodo *Execute Command* está deshabilitado por defecto → para correr Nexrender/ffmpeg/Blender hay que **co-locar un worker** (mismo host) o exponerlos por **webhook a un worker local**. No es bloqueante, solo arquitectura.

## 5. Cómo lo hace @0x100x realmente (teardown)

Stack real: **AE + Element 3D + Deep Glow + Trapcode Particular** (plugins de diseñador pro).
Sin diseñador y sin esos plugins de pago, el atajo al ~85–90% es:
- **Packs de plantilla premium de Envato Elements** (ya suscrito = $0 marginal). Nombres concretos detectados:
  - "Statistics — Corporate CSV Data-Driven Infographics"
  - "BigData Ultimate Infographics"
  - "Animated Corporate Financial Data Dashboard"
  - (+ "Dark Numbers" y Pack3 que ya validaste como craft pro)
- **Data-drive** esas plantillas vía Nexrender (JSON por beat).
- **Hero 3D** puntual en Blender (moneda/objeto premium, ya validado POC).
- **~10–15 min de polish manual** por video (lo que un humano sí aporta).

## 6. Recomendación

1. **Parar** de construir gráficos a mano. Definitivo.
2. **Catálogo de beats = catálogo de plantillas Envato rigged.** Cada beat type (barras, pie, pictograma, línea, tarjeta-noticia) = 1 plantilla premium fija, parametrizada por JSON.
3. **Nexrender** como motor de relleno de datos (ya instalado, $0).
4. **ElevenLabs timestamps** para pacing (ya validado).
5. **Blender hero** aditivo (ya validado).
6. **n8n** = orquestador del workflow único de 6 etapas con QC (ffprobe + vision-judge + 1 gate humano).
7. **Piloto Cavalry (gratis)** solo para beats de gráfica donde Envato no alcance. CLI de pago = NO sin OK.

**Costo de todo esto: $0 marginal.** Nada nuevo de pago. Respeta el freeze.

## 7. Riesgos / lo que falta decidir
- Confirmar 2–3 packs Envato OSCUROS de charts que casen con el Style Bible (Pack 1 no servía; "Dark Numbers" sí).
- Definir la rúbrica @0x100x exacta para el vision-judge.
- Decidir host del worker para Execute Command/webhook (VPS o local).
