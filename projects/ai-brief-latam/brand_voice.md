# Brand Voice — AI × Finanzas LATAM
**Last updated:** 2026-05-29 (v3 — revisado por ADR-017 post-Deep-Research)
**Sources:**
- projects/ai-brief-latam/research/deep-research-2026-05/ (5 outputs)
- docs/DEEP_RESEARCH_SYNTHESIS.md (2026-05-20)
- docs/DECISIONS.md ADR-017 (2026-05-29)

> **Cambio crítico v3 vs v2 (ADR-017):**
> - Pivot de nicho: AI How-To genérico → **AI × Finanzas Personales LATAM** (vertical único)
> - Reset realista benchmarks: 100K en 12-18m → **10K en 12m / 30-50K en 24m**
> - Nuevo eje: **compliance financiero** (modelo educativo C.1 — disclaimer "no es asesoría")
> - Voz se mantiene viral hype calibrado pero **calibrada para audiencia finanzas LATAM**
> - Voice clone DEFERRED — decisión inicio Fase 2
>
> El nombre "AI Brief LATAM" se mantiene en archivos hasta confirmación de handle/dominio. El proyecto editorial se llama internamente **AI × Finanzas LATAM** (working name).

---

## Nicho y posicionamiento

**Antes (v2 post-ADR-016):** AI How-To LATAM — contenido práctico cómo usar IA para profesionales 25-45.
**Ahora (v3 post-ADR-017):** **AI × Finanzas Personales LATAM** — cómo USAR herramientas de IA para tomar mejores decisiones financieras personales en el contexto LATAM. Vertical único.

**Pregunta que cada pieza debe responder:** "¿Cómo uso IA para [decisión/análisis financiero concreto LATAM]?"

**Modelo de referencia:** Mis Propias Finanzas (1M IG, Colombia) y Pequeño Cerdo Capitalista (Sofía Macías, 660K libros) en tono confesional + educativo. **PERO** con dos diferenciadores:
1. **La IA es el cómo**, no el qué — somos el manual de IA para tu plata, no otro coach financiero
2. **LATAM-first**: instrumentos locales (CEDEARs, CDTs, plazos fijos UVA, fondos comunes, FCI, ETFs accesibles desde brokers LATAM) en moneda local con contexto inflación regional

Ejemplos del tipo de pieza:

- **Inversiones:** "El prompt que usé para analizar 5 CEDEARs en 10 min con datos LATAM" / "Probé Claude para armar mi portfolio. Lo que encontró fue contraintuitivo"
- **Presupuesto:** "Subí mi extracto de Mercado Pago a Claude. Encontró 4 suscripciones fantasma" / "El prompt que detecta tus gastos invisibles"
- **Ahorro/Inflación:** "Cómo armé mi escudo anti-inflación AR con IA en 30 min" / "Pregúntale a tu IA esto antes de elegir entre dólar MEP o blue"
- **Impuestos:** "El prompt para saber si conviene monotributo o responsable inscripto (con tu data real)" / "Cómo ChatGPT calculó mi devolución de Ganancias antes que mi contador"
- **Comparativas brokers/bancos:** "Probé IOL, Cocos y Bull Market con la misma pregunta a Claude. Esto pasó"
- **Jubilación/Largo plazo:** "El plan de retiro que armé con IA siendo freelance LATAM"

**Diferenciador defensible:** específico LATAM (no traducción gringa) + español neutro + finanzas reales + IA como herramienta + tono educativo NO asesor. No "vas a hacerte rico con esto", sí "vas a entender mejor tus números con esto".

---

## Compliance financiero (NUEVO eje v3 — ADR-017 sub-decisión C.1)

**Modelo:** educativo, no asesoría. Estilo Sofía Macías + Mis Propias Finanzas. Permite mencionar productos específicos (Cocos, IOL, GBM, Bitso, Buenbit) **con contexto y disclaimer**.

### Hard NO (financiero)

- "Invertí en X" (recomendación directa)
- "Vas a ganar Y%" (predicción de rendimientos)
- "Esto te hará rico" / "garantizado" / "sin riesgo"
- Mencionar instrumentos sin contexto del riesgo asociado
- Cifras sin fuente verificable
- Predicciones de mercado tipo "el bitcoin va a $X en Y meses"
- Consejos personalizados sin avisar que NO son personalizados

### Hard YES (financiero)

- Disclaimer en cada pieza: "Esto no es asesoría financiera. Consultá a un profesional antes de invertir."
- Mostrar el proceso (cómo usar IA para evaluar) > recomendar el resultado
- Cifras con fuente: "Según el balance Q3 de [empresa], publicado en [link]"
- Mencionar riesgo cuando se habla de instrumentos: "El plazo fijo UVA ajusta por inflación pero tiene 90/180 días mínimo"
- Aclarar moneda y contexto regulatorio del país
- Ser explícito sobre los límites de la IA: "Claude no tiene datos en tiempo real; verificá las cifras antes de decidir"

### Reglas que mencionar productos requieren

| Tipo | Regla |
|---|---|
| Broker / banco / fintech | Mencionar como ejemplo o comparativa, no como recomendación. "Yo uso X" es OK con disclaimer. "Usá X" no es OK. |
| Activo específico (acción, ETF, crypto) | Solo en contexto educativo. "Cómo evaluar X con IA" sí; "Comprá X" no. |
| Estrategia financiera | Presentar como una opción entre varias, no como solución universal. |
| Comisiones / tasas | Citar fuente y fecha. Sujetas a cambio. |

---

## Voz editorial — modelo viral hype calibrado (sin cambio v2→v3, recalibrado para finanzas)

**Filosofía:** Hook viral emocional + body sobrio práctico + disclaimer claro. **Engancha como Filo, entrega como Smart Brevity, protege como Sofía Macías.**

### Hook (primeros 3 segundos del reel / primer 125 chars del caption)

- **EMOCIONAL, contrarian, o de revelación.** Calibrado para audiencia finanzas LATAM.
- Permitido: "Esto va a cambiar cómo manejás tu plata", "El secreto que tu banco no te dice", "Probé X y…", "Lo que mi contador no vio"
- Pasa los 3 requisitos del framework Rufusocial: ATENCIÓN + TENSIÓN + PROMESA
- **Calibración finanzas:** evitar promesas de rendimiento. "Esto te va a hacer rico" → NO. "Esto te va a ahorrar 2 horas haciendo tu presupuesto" → SÍ.

### Body (todo después del hook)

- **SOBRIO, práctico, paso-a-paso.** Smart Brevity puro.
- Cifras concretas con contexto + fuente
- "Por qué importa" obligatorio
- Datos > opiniones
- **Disclaimer financiero presente** (puede ser corto: "Esto no es asesoría — verificá con tu contador")
- Anti-hype EN EL BODY (la regla aplica al cuerpo, no al hook)

### Por qué esta calibración (re-revisada con Deep Research)

Reports 02+03 confirmaron: las cuentas LATAM que crecen sostenidamente combinan hook emocional + body sobrio. En finanzas específicamente, el dataset de Mis Propias Finanzas / Sofía Macías muestra que **el tono confesional + datos reales + admisión de errores** pega más que el "guru financiero" o el "anti-hype seco".

**Compromiso:** captamos atención como las virales LATAM, **pero entregamos valor educativo y protección legal como las premium**. Audiencia llega por el hook, se queda por el contenido, vuelve por la confianza.

---

## Reglas de voz (v3 — finanzas)

### Hard YES

- Datos verificables con fuente (en body, no en hook)
- "Por qué importa" explícito en cada pieza
- Acción concreta que el lector puede hacer hoy (probar un prompt, hacer una consulta a IA con sus datos)
- Reconocer incertidumbre cuando existe ("Probé X. Funcionó para mí. Tu situación puede ser distinta")
- Hook que pasa Rufusocial framework
- **Disclaimer financiero en cada pieza** (corto, no invasivo)
- Mostrar Manuel/persona como aprendiz, no como gurú
- Admitir errores y aprendizajes

### Hard NO

- Hook técnico aburrido ("Nuevo modelo de Claude lanzado")
- Body con hype injustificado o predicciones de mercado
- Recomendaciones financieras específicas sin contexto
- Promesas de rendimiento
- Listicles vacíos ("10 acciones para hacerte rico")
- Memes baratos sin contexto educativo
- Marca de agua de TikTok/CapCut (penalización LATAM 30-40% reach)
- Más de 1 emoji por frase
- Datos sin fuente
- Tono de "guru" o "yo sé y tú no"

### Permitido bajo calibración

- Cifras grandes en hook con shock value, siempre que el body las contextualice con fuente
- Contrarian claims ("La verdad sobre X que tu broker no te dice") siempre que el body presente evidencia
- Tono emocional en hook + CTA, sobrio en body
- Mencionar productos específicos (Cocos, IOL, GBM, Bitso) **con disclaimer y como ejemplo, no recomendación**
- "Esto puede cambiar tu plata" / "Esto me ahorró" en hook, "según el balance" / "en mi prueba" en body

---

## Idioma

(Sin cambio v2 — sigue español neutro LATAM)

- **Español neutro LATAM.** Sin peninsular, sin extremos regionales.
- **NO usar (peninsular):** vosotros, vuestro, vale, tío/tía, hostia, mola
- **NO usar (extremo MX):** chido, padre, no manches, qué onda
- **NO usar (extremo AR):** vos sos, che, viste, boludo, posta
- **SÍ usar:** ustedes, nuestro, está bien, ¿no?, listo, claro, dale
- **Vocabulario técnico finanzas en español + caveat regional:**
  - "Plazo fijo" (universal LATAM) > "depósito a plazo" (peninsular)
  - "Acción" / "ETF" / "CEDEAR" (AR específico — explicar primera vez)
  - "Renta variable / fija" (universal técnico)
  - "Tasa nominal / efectiva" (universal LATAM)
  - "Inversión" / "ahorro" / "presupuesto" / "ganancia" (universal)
- **Vocabulario técnico IA en inglés cuando es estándar:** AI, AGI, LLM, prompt, agent, deployment, workflow.
- **Cifras siempre con contexto:** no "$1,000 ganaron" sino "$1,000 ganaron en 12 meses según [fuente]"
- **Moneda explícita:** "USD 1,000" / "ARS 1.000.000" / "MXN 20,000" / "COP 4.000.000" — nunca "$1,000" suelto.

---

## Formato — AI × Finanzas específico

### Reels (formato principal post-Fase 2)

- **Largo:** 25-35 segundos (sweet spot validated)
- **Hook (0-3s):** emocional/contrarian + on-screen text grande
- **Body (3-22s):** los pasos concretos del análisis con IA, jump cuts 3-4s, screenshots de IA + balance/extracto si aplica
- **Cierre (22-30s):** resultado + disclaimer rápido ("Esto no es asesoría — probalo con tus datos") + CTA
- **Audio:** decisión voice clone vs manual deferida a Fase 2 (ADR-008 DEFERRED)
- **NO marca de agua TikTok/CapCut**

### Carousels Instagram (formato principal Fase 1)

- **Slide 1 (HOOK):** cifra grande o claim emocional + visual standard §7
- **Slide 2 (CONTEXTO):** "Por qué importa" + qué problema resuelve
- **Slides 3-N (PASOS):** cada slide = 1 paso del análisis con IA, con screenshot de prompt/respuesta si aplica
- **Slide penúltima:** resultado/aprendizaje + caveat ("Esto fue mi caso. Tu situación puede ser distinta")
- **Slide final:** **DISCLAIMER OBLIGATORIO** + CTA + branding
  - Texto base: "Esto no es asesoría financiera. Consultá a un profesional antes de tomar decisiones con tu plata."
- **Visual:** dark mode #0F0F10 + Inter + JetBrains Mono (POST_STANDARD §7)
- **Slide compliance audit:** A9 verifica que slides 1 y final cumplan reglas financieras

### Captions IG

- **Largo:** bajo 150 chars total. Hook en primeros 125 chars (visible antes de "more").
- **Estructura:** hook emocional + 1 frase promesa + CTA
- **Disclaimer:** si la pieza menciona productos específicos, agregar al final "⚠️ Educativo, no asesoría"
- **Emojis:** 1-2 estratégicos máximo. Permitidos: ⚡ 💰 📊 → 🔥 ⚠️ 💼
- **Hashtags:** 5-10 niche. Mix finanzas LATAM + IA. Ej: #FinanzasPersonales #InversionesLATAM #IAparaTodos #CEDEARs #PresupuestoFamiliar

### TikTok captions

- 100-300 chars (más largo que IG)
- 3-5 hashtags trending finanzas LATAM
- Tono más casual que IG
- Disclaimer puede ser visual en el reel mismo, no obligatorio en caption

### Newsletter sections (Beehiiv)

- **Largo:** 250-400 palabras por sección principal
- **Estructura:**
  - Subject line emocional + 5 alternates
  - Pre-header complementario
  - Intro sin saludo, hook directo
  - Top Story: el análisis del día con IA (Smart Brevity)
  - Quick Hits: 3-5 movimientos relevantes finanzas+IA LATAM
  - "Prompt de la semana": el prompt textual que el suscriptor puede copiar
  - **Disclaimer footer:** disclaimer financiero estandarizado + unsubscribe
  - CTA close conversacional

---

## Hook framework Rufusocial — calibrado para finanzas

Todo hook debe pasar las 3 condiciones:

1. **ATENCIÓN** — patrón emocional: cifra inesperada / claim contrarian / pregunta directa / revelación
2. **TENSIÓN** — el lector tiene UN problema financiero concreto que la pieza promete entender
3. **PROMESA** — beneficio específico y testeable, **NUNCA rendimiento prometido**

**Crítico:** hook debe funcionar SIN sonido. Subtítulos = parte del hook visual. Primeros frames deben comunicar por sí solos.

### Ejemplos calibrados AI × Finanzas LATAM

| Hook | ATENCIÓN | TENSIÓN | PROMESA |
|---|---|---|---|
| "Probé Claude con mi extracto. Encontró $40K que no veía." | Cifra específica + contrarian | "¿Yo también tendré dinero invisible?" | Detectar tus propios gastos invisibles |
| "El prompt que mi contador no querría que tengas" | Revelación con tensión | "¿Estoy pagando de más?" | Acceso al prompt |
| "Tu plazo fijo está perdiendo plata. La IA te dice cuánto." | Claim contrarian + cifra latente | "¿Cuánto exactamente?" | Saber tu pérdida real |
| "Pregunté a 3 IAs sobre CEDEARs. Una me hizo cambiar de opinión." | Pregunta latente | "¿Cuál?" | Comparativa práctica |

---

## Comunidad como pilar

(Sin cambio v2)

- "Comunidad" pega más que "audiencia" o "lectores" en LATAM
- "Únete a la comunidad" > "Síguenos"
- Para finanzas: comunidad como espacio de aprendizaje, NO de tips de inversión

---

## Tagline formula — finanzas LATAM

**Estructura:** VALOR PRÁCTICO + TIEMPO + IDIOMA/REGIÓN + DISCLAIMER

Ejemplos a testear post Fase -1:

- "Cómo usar IA para tu plata. LATAM. 5 min al día. Educativo, no asesoría."
- "Tu manual de IA para finanzas personales. En español. Sin BS, sin gurús."
- "IA práctica para tu plata, en LATAM, sin asesoría. El daily que tu billetera necesita."

(El tagline definitivo se elige post Fase -1 con data.)

---

## Multi-channel strategy

(Recalibrado v3)

- **Activo central:** **newsletter Beehiiv DESDE DÍA 1** (Fase 1, no Fase 3) — Reports 02+05: el canal más durable + el menos volátil.
- **IG + TikTok:** canales de adquisición que dirigen a newsletter
- **LinkedIn (Fase 1.5):** evaluar — finanzas LATAM tiene tracción B2B (gerentes, founders)
- **WhatsApp Channels:** evaluar Fase 2+ — canal creciente LATAM para finanzas
- **Pattern probado:** cross-pollination podcast → newsletter → IG → LinkedIn

---

## Benchmarks realistas (RESET v3 — ADR-017)

**Antes (v2):** 5K base, 15K niche, 50K target 12m, 100K excepcional, 500K+ NeoCom level
**Ahora (v3 — calibrado al dataset Report 03):**

| Hito | Plazo realista | Caveat |
|---|---|---|
| **5K subs newsletter** | 6-9 meses | Base creíble con cadencia + inflection lever |
| **10K subs newsletter** | 12 meses | Target base case (45-65% prob según Report 03) |
| **30-50K subs newsletter** | 24 meses | Top decile con automatización + lever activo |
| **100K subs newsletter** | 36+ meses | Requiere equipo o expansión sub-nicho |
| **15K-25K IG followers** | 12 meses | Si el viral path funciona en finanzas |
| **8K-15K LinkedIn (Fase 1.5)** | 12 meses | Si B2B finanzas resuena |

**North star Manuel:** audiencia masiva como **horizonte de largo plazo (24-36m+)**, no target de 12-18m. **10K subs newsletter en 12m es realmente un buen resultado.** El path "viral hype calibrado + AI×Finanzas + LATAM + Inflection Lever Track" es la apuesta más coherente con esto.

**Calibración crítica:** si en mes 6 estamos en <2K subs, NO panic — replantear hook + sub-nicho específico (¿inversiones vs presupuesto vs impuestos?). Si en mes 12 estamos en <5K, replantear nicho serio.

---

## Hard NO's (post-ADR-017, recalibrado finanzas)

- Body con hype injustificado (el hook puede ser emocional, el body NO)
- **Recomendaciones específicas de inversión** ("comprá X")
- **Predicciones de rendimiento o mercado**
- Predicciones irresponsables sin caveat
- Listicles sin sustancia ("10 acciones para hacerte rico con IA")
- Memes baratos sin valor educativo
- Marca de agua de otras plataformas
- Más de 1 emoji por frase
- Datos sin fuente
- **Cifras de moneda sin contexto inflación / país**
- Tono de "guru" o "yo sé y tú no"

---

## Hard YES's (post-ADR-017)

- Datos verificables con fuente (en body)
- "Por qué importa" explícito
- **Disclaimer financiero en cada pieza con productos específicos**
- Acción concreta accionable (el lector puede usar el prompt hoy)
- Voz neutral, educativa, respetuosa
- Reconocer incertidumbre y errores propios
- Hook emocional que pasa Rufusocial framework
- Mostrar Manuel como aprendiz/explorador, no gurú
- Mencionar moneda + país + fecha cuando se citan cifras

---

## Voz narrada — DEFERRED (ADR-008 + ADR-017)

**Status:** decisión final voice clone vs manual narration **deferida a inicio Fase 2** (cuando Fase 1 estable + Manuel a 30 días de Fase 2).

**Razones del deferral:**
- Report 05: TikTok ya auto-etiqueta voice clone realista — disclosure obligatorio
- Pivot a finanzas refuerza autoridad personal (Manuel como persona puede sumar más credibilidad que voz AI)
- Hasta Fase 2 no se necesita decidir

**Mientras tanto (Fase 0-1):** carouseles + captions, sin audio. Si llegamos a Fase 2: 3 opciones según data:
- **A) Voice clone 100% ElevenLabs** ($11 primer mes deal → $22/mo) — escala alto, label obligatorio
- **B) Narración manual Manuel** ($0) — autoridad alta, escala limitada
- **C) Híbrido:** clone para informativo, manual para opiniones — balance

(Si elegimos A o C, las reglas de pronunciación neutralizada que estaban en v2 se reactivan.)

---

## Notas sobre el rename del proyecto

El nombre **"AI Brief LATAM"** está pegado en:
- Carpeta `projects/ai-brief-latam/`
- Múltiples archivos .md con título
- Email business `aibrieflatam.media@gmail.com`

**Decisión pendiente:** Manuel confirma nombre nuevo post Fase -1. Opciones tentativas (finanzas-focused):

- "AI Finanzas LATAM"
- "IA para tu Plata"
- "Plata con IA"
- "Manual de Plata IA"
- "Finanzas con Bot" / "Bot Finanzas"
- "TuBot Financiero LATAM"

El rename físico se hace de una vez cuando el nombre + handle + dominio estén locked.
