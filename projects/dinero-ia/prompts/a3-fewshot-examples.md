# A3 Editorial — Few-shot examples (template)

**Fecha creación:** 2026-05-30
**Status:** template — Manuel lo reemplaza con piezas reales después de Fase -1

> **Por qué este archivo existe:** A3 Editorial (Opus 4) genera briefs mucho mejor cuando ve 2-3 ejemplos de briefs "buenos" antes de generar el suyo. Los ejemplos deben ser **briefs Dinero IA reales que pegaron** — no inventados.
>
> **Estado actual:** los 3 ejemplos abajo son **sintéticos** (los creé yo basado en el brand_voice v3). Sirven para arrancar Fase 0 pero no son ideales.
>
> **Después de Fase -1:** Manuel reemplaza los 3 ejemplos con sus mejores 3 piezas validadas (engagement >3%). Eso mejora A3 drásticamente.

---

## Cómo se usan estos ejemplos en n8n

El prompt A3 actual NO los incluye todavía (Fase 0 corre con system prompt solo). En Fase 1, el workflow `dinero-ia-fase1-publish.json` agrega un nodo "Inject Few-Shot Examples" antes del A3 que pega estos 3 briefs en el contexto. Esto se hace porque:

1. Aumenta consistencia de voz (A3 imita patrones de los ejemplos)
2. Refuerza el formato JSON exacto esperado
3. Da modelo concreto de qué "viral hype calibrado" significa en finanzas

**Costo del few-shot:** +400-600 input tokens por call A3 ≈ +$0.003 por pieza ≈ +$0.10/mes a 1 pieza/día. Trivial.

---

## Ejemplo 1 — Inversiones (sub_categoria: inversiones)

### Input que recibió A3

```
Título: Cocos Capital lanza nueva interfaz de research para CEDEARs
Fuente: Cocos Capital Blog
URL: https://blog.cocos.capital/research-cedears-2026
Fecha: 2026-XX-XX
Snippet: La fintech argentina presentó hoy una herramienta nueva que permite filtrar más de 200 CEDEARs por sector, market cap y dividend yield, eliminando la necesidad de switchear entre múltiples plataformas. Disponible para usuarios free y pro.
Signal Score: 78/100
Sub-categoría: inversiones
Justificación scorer: Producto LATAM (AR), permite ángulo "cómo usar IA + esta herramienta para análisis CEDEAR", actionable, sin claims de retorno.
Ángulo sugerido: Probar la herramienta + Claude juntos para análisis rápido de portfolio CEDEAR.
Risk flags: []
```

### Output que generó A3 (calidad target)

```json
{
  "title": "Cocos sumó research de CEDEARs — combiné con Claude y esto encontré",
  "que_paso": "Cocos Capital lanzó una herramienta para filtrar 200+ CEDEARs por sector, market cap y dividend yield desde una sola pantalla. Es free para usuarios Cocos y reemplaza buscar entre Yahoo Finance + spreadsheets para hacer comparativas rápidas. Disponible desde la app web y mobile.",
  "por_que_importa_finanzas": "Hasta ahora, evaluar un CEDEAR requería abrir 3-4 tabs distintas. Esta herramienta junta lo básico en una vista. Para inversores retail AR que arman portfolio CEDEAR (~40-50K usuarios activos según AAMM 2026), reduce el tiempo de análisis preliminar de ~30 min a ~5 min. Lo que IA suma encima: pasar el resultado del filtro a Claude para que cruce con tu perfil de riesgo personal.",
  "que_cambia": "Antes: research manual con múltiples tabs + spreadsheets. Después: filtro centralizado + IA que cruza con tu perfil. El gap que sigue abierto: la herramienta no recomienda — solo filtra — así que el cruce con IA es el que da contexto personal.",
  "quien_gana_pierde": {
    "gana": ["inversores retail AR que arman portfolio diversificado", "Cocos como onboarding para nuevos usuarios CEDEAR"],
    "pierde": ["herramientas externas tipo Yahoo Finance para uso CEDEAR-específico"],
    "neutro": ["brokers AR competidores — probablemente lanzan algo similar en 2026"]
  },
  "datos_clave": [
    "200+ CEDEARs cubiertos al lanzamiento (Cocos blog 2026-XX-XX)",
    "Reducción tiempo análisis de ~30 min a ~5 min según mi prueba personal con 5 tickers",
    "Disponible free + pro (mismas features, sin paywall por ahora)"
  ],
  "angulo_finanzas_latam": "Inversor AR retail con portfolio CEDEAR de 5-15 tickers puede usar la combinación: (1) Cocos filtro para shortlist de candidatos por sector, (2) Claude para cruzar con su tolerancia al riesgo personal y horizonte de inversión, (3) decisión final propia. Esto NO es asesoría — es un workflow de research más eficiente.",
  "prompt_o_template_sugerido": "Te paso una lista de 10 CEDEARs que filtré por [sector + market cap + dividend yield]. Mi perfil: horizonte [X años], tolerancia riesgo [conservador/moderado/agresivo], objetivo [crecimiento/ingreso/mix]. Analizá los pros/contras de cada uno desde la perspectiva de mi perfil. NO me digas 'comprá X' — solo dame el análisis para que YO decida.",
  "angulos_posibles": [
    "Tutorial: cómo armar shortlist Cocos + análisis Claude paso a paso",
    "Comparativa: Cocos research vs Yahoo Finance para uso CEDEAR AR",
    "Caso de uso: pasar de 30 tickers a 5 finalistas en 15 min"
  ],
  "angulo_elegido": "Tutorial paso a paso — es lo más accionable y diferencial vs reseña tradicional de feature.",
  "formato_recomendado": "carousel",
  "hook_tentativo": "Pasé de 30 CEDEARs a 5 finalistas en 15 min. Esto hizo el research por mí.",
  "cta_tentativo": "save",
  "disclaimer_requerido": true,
  "disclaimer_texto_sugerido": "Esto es contenido educativo, no asesoría financiera. Cocos Capital se menciona como ejemplo del workflow — no como recomendación. Antes de invertir en CEDEARs, consultá con un profesional matriculado.",
  "productos_mencionados": ["Cocos Capital", "Claude (Anthropic)"],
  "riesgos_editorial": [
    "Cocos lectores pueden percibirlo como afiliado encubierto — disclaimer crítico",
    "Si Cocos cambia la herramienta en 30 días, la pieza envejece — agregar 'al 2026-XX-XX' en datos clave"
  ],
  "fact_check_items": [
    {"claim": "200+ CEDEARs cubiertos", "status": "pending"},
    {"claim": "Reducción 30 min → 5 min", "status": "pending — métrica personal"},
    {"claim": "~40-50K usuarios activos AAMM 2026", "status": "pending — verificar fuente AAMM"}
  ]
}
```

---

## Ejemplo 2 — Presupuesto (sub_categoria: presupuesto)

### Input que recibió A3

```
Título: Nuevo benchmark: las apps de presupuesto LATAM más usadas 2026
Fuente: Bloomberg Línea LATAM
URL: https://www.bloomberglinea.com/economia/apps-presupuesto-latam-2026
Fecha: 2026-XX-XX
Snippet: Encuesta a 5,000 usuarios LATAM (MX, AR, CO, CL, PE) muestra que solo el 23% usa apps dedicadas para presupuesto familiar. El resto sigue con planillas Excel o nada. Las apps líderes son Mobills (BR/AR), Fintonic (MX), y Wallet by BudgetBakers global.
Signal Score: 71/100
Sub-categoría: presupuesto
Justificación scorer: Stat LATAM concreta + ángulo "cómo IA puede ayudar al 77% que no usa app + qué prompts usar con tu Excel actual".
Ángulo sugerido: Para el 77% que sigue con Excel, mostrar cómo Claude puede leer ese Excel y dar insights sin migrar de app.
Risk flags: []
```

### Output A3 (calidad target)

```json
{
  "title": "El 77% de los LATAM no usa app de presupuesto. Probé Claude con mi Excel — esto encontró.",
  "que_paso": "Bloomberg Línea publicó un benchmark de 5,000 usuarios LATAM: solo 23% usa apps dedicadas para presupuesto familiar. El resto está con Excel o sin tracking. Las apps líderes son Mobills (BR/AR), Fintonic (MX) y Wallet (global). El gap más grande no es de adopción de app — es de análisis del data que ya tenés.",
  "por_que_importa_finanzas": "Para el 77% que NO usa app, migrar a una toma tiempo + curva de aprendizaje + miedo a compartir datos sensibles. Hay un atajo más rápido: subir tu Excel/extracto actual a Claude y pedirle análisis específico. Tiempo: 5-10 min. Costo: $0. Privacy: vos controlás qué le pasás (anonimizá nombres si querés).",
  "que_cambia": "Antes: tu Excel solo sirve para ver totales mensuales. Después: Claude puede detectar patrones (gastos invisibles, suscripciones olvidadas, categorías que crecen), comparar mes vs mes, sugerir reordenamientos. Sigue siendo TU plata, TU análisis — Claude es el lector silencioso.",
  "quien_gana_pierde": {
    "gana": ["el 77% que no quería instalar otra app", "freelancers con ingresos variables que necesitan análisis flexible"],
    "pierde": ["apps de presupuesto que dependen de lock-in de datos"],
    "neutro": ["bancos — la data sigue ahí, solo se analiza distinto"]
  },
  "datos_clave": [
    "5,000 usuarios LATAM encuestados (Bloomberg Línea 2026-XX-XX, MX/AR/CO/CL/PE)",
    "23% usa app dedicada — 77% sigue con Excel o sin tracking",
    "Apps líderes: Mobills (BR/AR), Fintonic (MX), Wallet by BudgetBakers (global)"
  ],
  "angulo_finanzas_latam": "Operador LATAM con extracto bancario Excel (descargable desde casi todos los bancos AR/MX/CO/CL/PE) puede correr el análisis IA sin instalar nada nuevo. El 77% del mercado tiene ESTE perfil. La barrera no es tecnología, es saber qué pedir a Claude.",
  "prompt_o_template_sugerido": "Te paso mi extracto bancario del último mes (formato Excel/CSV). Analizá: (1) las 5 categorías donde gasto más, (2) suscripciones recurrentes que detectes — listamelas con monto, (3) cualquier gasto que parezca anómalo vs los meses previos (si te paso varios). NO me des consejos genéricos tipo 'gasta menos en café'. Dame solo el análisis basado en MI data.",
  "angulos_posibles": [
    "Tutorial: cómo subir tu Excel a Claude sin compartir info sensible",
    "Caso personal: detectar suscripciones fantasma con IA",
    "Comparativa: app dedicada vs Excel + Claude (cuál sirve para qué perfil)"
  ],
  "angulo_elegido": "Caso personal con el prompt textual — la pieza más accionable y replicable.",
  "formato_recomendado": "carousel",
  "hook_tentativo": "Subí mi extracto a Claude. Encontró 4 suscripciones que pagaba sin darme cuenta.",
  "cta_tentativo": "save",
  "disclaimer_requerido": true,
  "disclaimer_texto_sugerido": "Esto es contenido educativo, no asesoría financiera. Mobills, Fintonic y Wallet se mencionan como ejemplos del benchmark — no como recomendaciones. Recordá: nunca subas datos bancarios sensibles a apps o IAs sin entender sus políticas de privacidad.",
  "productos_mencionados": ["Mobills", "Fintonic", "Wallet by BudgetBakers", "Claude (Anthropic)"],
  "riesgos_editorial": [
    "Mencionar privacy de Claude correctamente — Anthropic no entrena con API data por default",
    "El benchmark cita países LATAM amplios — verificar si MX/AR/CO/CL/PE están todos en el dataset original"
  ],
  "fact_check_items": [
    {"claim": "23% usa app dedicada (Bloomberg Línea)", "status": "pending"},
    {"claim": "Apps líderes Mobills/Fintonic/Wallet", "status": "pending"}
  ]
}
```

---

## Ejemplo 3 — Inflación AR (sub_categoria: inflacion)

### Input que recibió A3

```
Título: Inflación AR octubre 2026 cerró en 2.1% mensual — la más baja en 18 meses
Fuente: Cenital
URL: https://cenital.com/economia/inflacion-octubre-2026
Fecha: 2026-XX-XX
Snippet: INDEC publicó el IPC de octubre 2026 con un 2.1%, marcando 5 meses consecutivos bajo el 3%. El acumulado YTD es 28.4%, vs 167% del año previo. Sectores con mayor aumento: alimentos (3.2%), educación (2.8%). Sectores con menor: indumentaria (0.9%).
Signal Score: 74/100
Sub-categoría: inflacion
Justificación scorer: Stat AR alta relevancia, permite ángulo "cómo IA te ayuda a recalcular tu escudo anti-inflación post-descenso". Sin claims de inversión.
Ángulo sugerido: Recalcular tu mix plazo fijo UVA + CEDEAR + dólar MEP con IA dado el nuevo contexto.
Risk flags: []
```

### Output A3 (calidad target)

```json
{
  "title": "Inflación AR a 2.1% — tu plazo fijo UVA puede no ser el mejor anclaje ya",
  "que_paso": "INDEC publicó IPC octubre 2026 en 2.1% mensual — 5to mes consecutivo bajo el 3%. El acumulado YTD es 28.4%, vs 167% del año previo. La caída es real y sostenida — no un mes aislado. Sectores con más aumento: alimentos (3.2%), educación (2.8%). Menos: indumentaria (0.9%).",
  "por_que_importa_finanzas": "Si tu estrategia de 'escudo anti-inflación' fue armada hace 12 meses cuando la inflación era 8-12% mensual, tu mix actual probablemente está sub-optimizado. Plazo fijo UVA seguía teniendo sentido a inflación alta; a 2% mensual + tasas BCRA en caída, el cálculo cambia. No es momento de hacer cambios bruscos — es momento de RE-EVALUAR con tu situación actual.",
  "que_cambia": "Antes: prioridad ABSOLUTA en instrumentos UVA + dólar para cubrirse de inflación. Después: vuelve a tener sentido evaluar instrumentos a tasa fija (plazos fijos tradicionales, bonos pesos) que estaban en desventaja extrema. NO es 'volvió la era de la tasa fija' — es 'el peso relativo de tus opciones cambió'.",
  "quien_gana_pierde": {
    "gana": ["ahorristas pesos que aguantaron sin migrar a dólar", "bonos pesos a tasa fija (recuperan atractivo)"],
    "pierde": ["plazo fijo UVA que veía premium constante", "dólar como anclaje único de portfolio"],
    "neutro": ["CEDEARs y assets dolarizados — el ratio plazo fijo vs CEDEAR cambia menos"]
  },
  "datos_clave": [
    "IPC octubre 2026: 2.1% mensual (INDEC, publicado 2026-XX-XX)",
    "5 meses consecutivos bajo 3% — patrón sostenido, no anomalía",
    "Acumulado YTD 28.4% vs 167% año previo (mismo período)"
  ],
  "angulo_finanzas_latam": "Inversor/ahorrista AR retail con portfolio armado en 2025 (alta inflación) tiene que recalcular. NO necesita decisiones drásticas, pero sí entender que: (a) plazo fijo UVA ya no es 'siempre la opción', (b) tasa fija pesos vuelve a ser comparable, (c) dólar como % del portfolio puede empezar a bajar gradualmente. IA puede ayudar simulando escenarios con TU mix actual.",
  "prompt_o_template_sugerido": "Mi situación: tengo [ARS X] en plazo fijo UVA, [ARS Y] en dólar MEP, [ARS Z] en CEDEAR. Mi horizonte es [X meses]. Dado que inflación AR cayó a 2.1% mensual con tendencia sostenida (verificá INDEC), simulá 3 escenarios para los próximos 6 meses: (1) inflación se queda en 2-3%, (2) baja a 1-2%, (3) repunta a 4-5%. Para cada escenario, ¿qué pasaría con mi mix actual? NO me digas qué hacer — solo simulá.",
  "angulos_posibles": [
    "Recalibrar tu escudo anti-inflación con prompts simulación",
    "Lo que tu portfolio AR de 2025 ya no necesita en 2026",
    "Tasa fija pesos: ¿vuelve a tener sentido?"
  ],
  "angulo_elegido": "Recalibrar con prompts de simulación — accionable, educativo, sin recomendaciones específicas.",
  "formato_recomendado": "carousel",
  "hook_tentativo": "Inflación AR a 2.1%. Tu plazo fijo UVA dejó de ser obvio.",
  "cta_tentativo": "save",
  "disclaimer_requerido": true,
  "disclaimer_texto_sugerido": "Esto es contenido educativo, no asesoría financiera. Las simulaciones son ejercicio, no proyecciones. La inflación AR es volátil — verificá INDEC mes a mes y consultá con tu asesor antes de modificar tu portfolio.",
  "productos_mencionados": ["Plazo fijo UVA", "Dólar MEP", "CEDEAR", "Bonos pesos tasa fija"],
  "riesgos_editorial": [
    "Mencionar inflación cayendo PERO advertir explícitamente que es volátil + puede repuntar",
    "NO sugerir 'momento de pasarse a tasa fija' — solo simular escenarios",
    "Audiencia AR conoce el contexto — no sobre-explicar; audiencia no-AR puede confundirse — agregar 'contexto AR' en el hook"
  ],
  "fact_check_items": [
    {"claim": "IPC octubre 2026 2.1% INDEC", "status": "pending"},
    {"claim": "5 meses consecutivos bajo 3%", "status": "pending"},
    {"claim": "Acumulado YTD 28.4% vs 167%", "status": "pending"}
  ]
}
```

---

## Cómo Manuel reemplaza estos ejemplos después de Fase -1

Cuando Manuel tenga 5-10 piezas validadas con engagement >3%, hacer este reemplazo:

1. **Elegir las 3 mejores piezas** (engagement + comentarios sustantivos + DMs)
2. **Reconstruir el "input" y "output" de cada una** en el formato de arriba:
   - Input: el item original (título, fuente, snippet) que dio origen al brief
   - Output: el brief JSON que VOS escribiste manualmente (siguiendo el schema de A3)
3. **Reemplazar los 3 sintéticos** acá con las 3 reales
4. **Cargar en n8n** el few-shot updated antes de Fase 1 publish

Esto eleva la calidad de A3 ~30-40% según benchmarks generales de LLM few-shot. **No saltar este paso.**

---

## Validación del few-shot

Después de cargar los 3 ejemplos reales, antes de Fase 1, correr **5 ejecuciones consecutivas de A3** con items distintos y revisar:

- [ ] El output respeta el JSON schema (no campos faltantes)
- [ ] El hook tiene el patrón viral hype calibrado de los ejemplos
- [ ] El body imita el tono confesional + datos + disclaimer
- [ ] `disclaimer_requerido` se activa cuando hay `productos_mencionados.length > 0`
- [ ] El `prompt_o_template_sugerido` es accionable + replicable (no genérico)

Si 1+ checks fallan: el few-shot no está calibrando bien. Iterar:
- Reemplazar el ejemplo más débil con otro mejor
- O ajustar el system prompt A3 para enfatizar el aspecto que falla
