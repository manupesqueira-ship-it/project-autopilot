# Brand Voice — AI How-To LATAM
**Last updated:** 2026-05-18 (revisado por ADR-016 pivot estratégico)
**Sources:**
- projects/ai-brief-latam/research/2026-05-07_format-and-voice-research.md
- projects/ai-brief-latam/research/2026-05-07_latam-specific-research.md
- projects/ai-brief-latam/docs/research/deep-research/2026-05-08_social-media-niches-2026.md
- docs/CRITICAL_REVIEW.md (2026-05-18) + ADR-016

> **Cambio crítico 2026-05-18 (ADR-016):**
> - Pivot de nicho: AI News brief → AI How-To práctico (cómo USAR herramientas IA)
> - Pivot de voz: anti-hype sobrio → viral hype calibrado (hook emocional + body sobrio)
> - Convicción full en UNA idea hasta validar
>
> El nombre "AI Brief LATAM" se mantiene en archivos hasta confirmación de nuevo nombre. El cambio físico (`projects/ai-brief-latam/` → nuevo path) está deferred.

---

## Nicho y posicionamiento

**Antes (v1):** AI Brief LATAM = news brief diario de IA. Modelo Rundown AI.
**Ahora (v2 post-ADR-016):** AI How-To LATAM = contenido práctico **cómo USAR herramientas IA** para tareas concretas. Modelo: tutorial actionable de Mafia IA + voz emocional Filo News.

**Pregunta que cada pieza debe responder:** "¿Cómo le hago para…?" en un dolor concreto del profesional LATAM.

Ejemplos del tipo de pieza:
- "Cómo usar Claude para responder 50 emails de tu jefe en 10 minutos"
- "El prompt secreto que un manager LATAM debería tener en el celular"
- "Probé 5 herramientas IA para presentaciones. Esta es la única que funciona en español"
- "Lo que NADIE te dice sobre usar ChatGPT en tu trabajo (y por qué te van a despedir si lo haces mal)"

**Diferenciador defensible:** específico LATAM + español neutro + práctico-accionable. No news, no theory, no philosophy.

---

## Voz editorial — modelo híbrido (calibrado por ADR-016)

**Filosofía:** Hook viral emocional + body sobrio práctico. **Engancha como Filo, entrega como Smart Brevity.**

### Hook (primeros 3 segundos del reel / primer 125 chars del caption)
- **EMOCIONAL, contrarian, o de revelación.** No técnico, no anti-hype puro.
- Permitido: "ESTO va a cambiar cómo trabajás", "El secreto que…", "Nadie te dice esto", "Probé X y…"
- Pasa los 3 requisitos del framework Rufusocial: ATENCIÓN + TENSIÓN + PROMESA

### Body (todo después del hook)
- **SOBRIO, práctico, paso-a-paso.** Smart Brevity puro.
- Cifras concretas con contexto
- "Por qué importa" obligatorio
- Datos > opiniones
- Anti-hype EN EL BODY (la regla aplica al cuerpo, no al hook)

### Por qué esta calibración

Critical Review identificó que las cuentas que llegan a >1M LATAM (NeoCom 1.4M, Filo 1.8M) usan hooks emocionales. Las "sobrias" (Startupeable 27K, Ecosistema 12K) tienen techo más bajo.

**Compromiso:** captamos atención como las virales, **pero entregamos valor real como las premium**. Audiencia llega por el hook, se queda por el contenido. Esta tensión es resoluble — no contradictoria.

---

## Reglas de voz (post-ADR-016)

### Hard YES
- Datos verificables con fuente (en body, no en hook)
- "Por qué importa" explícito en cada pieza
- Acción concreta y accionable (cada pieza enseña algo que el lector PUEDE hacer hoy)
- Reconocer incertidumbre cuando existe ("Probé X. Funciona PARA mí. Tu caso puede variar")
- Hook que pasa el framework Rufusocial (atención + tensión + promesa)

### Hard NO
- Hook técnico aburrido ("OpenAI lanza nuevo modelo")
- Body con hype injustificado (el body es sobrio aunque el hook sea emocional)
- Predicciones irresponsables sin caveat
- Listicles vacíos ("10 prompts para…")
- Memes baratos sin contexto
- Marca de agua de TikTok/CapCut (penalización LATAM 30-40% reach)
- Más de 1 emoji por frase

### Permitido bajo calibración (cambio post-ADR-016)
- Cifras grandes en hook con shock value, siempre que el body las contextualice
- Contrarian claims ("La verdad sobre X que…") siempre que el body presente evidencia
- Tono emocional en hook + CTA, sobrio en body
- "Esto cambia" / "Esto rompe" en hook, "según el research" / "en mi prueba" en body

---

## Idioma

- **Español neutro LATAM.** Sin peninsular, sin extremos regionales.
- **NO usar (peninsular):** vosotros, vuestro, vale, tío/tía, hostia, mola
- **NO usar (extremo MX):** chido, padre, no manches, qué onda
- **NO usar (extremo AR):** vos sos, che, viste, boludo, posta
- **SÍ usar:** ustedes, nuestro, está bien, ¿no?, listo, claro, dale
- Vocabulario técnico en inglés cuando es estándar (AI, AGI, LLM, agent, prompt, deployment, enterprise, workflow).
- Cifras siempre con contexto en body (no "$1.5B" suelto, sino "$1.5B reportado por WSJ").

---

## Formato — How-To específico

### Reels (formato principal)
- **Largo:** 25-35 segundos (sweet spot validated)
- **Hook (0-3s):** emocional/contrarian + on-screen text grande
- **Body (3-22s):** los pasos concretos del how-to, jump cuts 3-4s, texto en pantalla siempre
- **Cierre (22-30s):** resultado mostrado + CTA específico ("Probalo en tu próxima reunión", "Guardá esto")
- **Audio:** voice clone Manuel (ADR-008) — voz humana clonada cuenta como humana para algoritmo
- **NO marca de agua TikTok/CapCut** (penalización LATAM 30-40%)

### Carousels Instagram (formato secundario Fase 1)
- **Slide 1 (HOOK):** cifra grande o claim emocional + visual standard §7
- **Slides 2-N (PASOS):** cada slide = 1 paso accionable, con screenshot/visual si aplica
- **Slide penúltima:** resultado/before-after o contexto LATAM
- **Slide final:** CTA + branding wordmark
- **Visual:** dark mode #0F0F10 + Inter + JetBrains Mono (POST_STANDARD §7)

### Captions IG
- **Largo:** bajo 150 chars total. Hook en primeros 125 chars (visible antes de "more").
- **Estructura:** hook emocional + 1 frase de promesa + CTA
- **Emojis:** 1-2 estratégicos máximo. Permitidos: ⚡ 🏦 💼 📊 → 🔥 ⚠️
- **Hashtags:** 5-10 niche. Mix volumen alto + nicho específico. NO 30 broad.

### TikTok captions
- 100-300 chars (más largo que IG)
- 3-5 hashtags trending
- Tono más casual que IG (mismo contenido, calibración distinta)

### Newsletter sections (Beehiiv)
- **Largo:** 250-400 palabras por sección
- **Estructura adoptada del template #12533:**
  - Subject line emocional + 5 alternates
  - Pre-header complementario
  - Intro sin saludo, hook directo
  - Top Story deep-dive Smart Brevity (sin meta-labels)
  - Quick Hits 3-5 stories breves
  - CTA close conversacional

---

## Hook framework Rufusocial — calibrado para how-to

Todo hook (Reel, caption, subject line) debe pasar las 3 condiciones:

1. **ATENCIÓN** — patrón emocional: cifra inesperada / claim contrarian / pregunta directa / revelación
2. **TENSIÓN** — el lector tiene UN problema concreto que la pieza promete resolver
3. **PROMESA** — beneficio específico y testeable ("vas a aprender X en 3 minutos", "vas a evitar este error")

**Crítico:** hook debe funcionar SIN sonido. Subtítulos = parte del hook visual. Primeros frames deben comunicar por sí solos.

### Ejemplos calibrados para AI How-To LATAM

| Hook | ATENCIÓN | TENSIÓN | PROMESA |
|---|---|---|---|
| "Despedí a mi analista. Esto hace Claude por la mitad del costo." | Contrarian fuerte | "¿Funcionará para mí?" | Reducción de costo concreta |
| "El prompt que usé para escribir 50 emails en 20 min" | Cifra específica | "Yo tardo más" | Acceso al prompt |
| "Probé 5 IAs para tu industria. Solo UNA sirve." | Pregunta latente | "¿Cuál?" | Comparativa práctica |
| "Esto va a destruir tu reputación si lo haces mal con IA" | Riesgo emocional | "¿Lo estoy haciendo mal?" | Cómo evitarlo |

---

## Comunidad como pilar

- "Comunidad" pega más que "audiencia" o "lectores" en LATAM
- Mencionar comunidad explícitamente en bio, taglines, CTAs cuando aplique
- "Únete a la comunidad" > "Síguenos"
- "Lectores" sirve como sinónimo neutral

---

## Tagline formula LATAM (calibrada para how-to)

**Estructura:** VALOR PRÁCTICO + TIEMPO + IDIOMA/REGIÓN + PRECIO

Ejemplos a testear para nuestro caso:
- "IA práctica para profesionales LATAM. 3 min al día. Gratis."
- "Cómo usar IA en tu trabajo, en español, sin enrolarte en cursos caros."
- "El how-to de IA que tu equipo necesita. LATAM, gratis, diario."

(El tagline definitivo se elige después de Fase -1 con data de qué resuena con audiencia real.)

---

## Multi-channel strategy

- **Activo central:** newsletter Beehiiv (propiedad propia, no depende de algoritmos IG/TikTok)
- **IG + TikTok:** canales de adquisición que dirigen a newsletter
- **LinkedIn (Fase 1.5):** evaluar — Startupeable demostró que LinkedIn funciona LATAM B2B
- **WhatsApp Channels:** evaluar Fase 2+ — canal creciente LATAM
- **Pattern probado:** cross-pollination podcast → newsletter → IG → LinkedIn

---

## Benchmarks realistas (recalibrados para how-to + viral path)

**Antes (v1 sobrio):** 12-30K en 12-18 meses = home run.

**Ahora (v2 calibrado):**
- 5K = base creíble (Fase -1 validation)
- 15K = niche success
- 50K = top tier (objetivo 12 meses, viable con voz emocional + how-to)
- 100K = excepcional (objetivo 18-24 meses)
- 500K+ = NeoCom/Filo level (24-36 meses si el viral path engancha)

**Target north star Manuel:** audiencia masiva (>100K en 12-18 meses). El path "viral hype calibrado + how-to práctico + LATAM" es la apuesta más coherente con esto.

---

## Hard NO's (post-ADR-016)

- Body con hype injustificado (el hook puede ser emocional, el body NO)
- Predicciones irresponsables sin caveat ("este modelo va a destruir X industria" sin matiz)
- Listicles sin sustancia ("10 prompts para ganar dinero con IA" — vacuo)
- Memes baratos sin valor educativo
- Marca de agua de otras plataformas
- Más de 1 emoji por frase
- Pasar Smart Brevity por encima de claridad ("axiomas" no deben ser indescifrables)

---

## Hard YES's (post-ADR-016)

- Datos verificables con fuente (en body)
- "Por qué importa" explícito
- Acción concreta y accionable en cada pieza
- Voz neutral y respetuosa en body
- Reconocer incertidumbre cuando existe
- Hook emocional que pasa Rufusocial framework
- Mostrar Manuel como persona (face/voice ocasional) — autenticidad LATAM 2026

---

## Voz narrada — clarification (post-ADR-008 + ADR-016)

**Voz primaria:** ElevenLabs voice clone de Manuel (ADR-008 — voice clone 100%).
**Pre-requisito:** grabación de 20-30 min pendiente (script en `docs/voice-clone/recording-script.md`).
**Mientras tanto:** Manuel narra manualmente con iPhone Voice Memos (fallback documentado).

**Reglas de pronunciación neutralizada (cuando narre manual o el clone hable):**
- SÍ: ustedes, carro, computadora, celular, manejar, platicar
- SÍ: pronunciar "z" y "c" como "s" (no ceceo)
- NO peninsular: vosotros, vale, tío, ordenador, móvil, coche, ceceo
- NO MX extremo en narración: chido, padre, no manches, órale
- NO AR extremo: vos sos, che, sheísmo (calle="cashe"), playa="plasha"
- NO caribe extremo: pa'lante, elisiones fuertes de "s"

**Estilo de lectura para how-to:**
- Pausas marcadas en hook (3 segundos cuentan triple)
- Bajada de tono en datos clave (autoridad)
- **Aceleración con energía emocional al pivote del problema** (calibración viral)
- Cierre con ritmo ascendente en CTA + tono de "te puede pasar"

**Justificación data:** voz humana clonada de Manuel cuenta como humana para algoritmo (research production-stack confirmado). Cero riesgo "Made with AI" label penalty si la voz suena humana.

---

## Notas sobre el rename del proyecto

El nombre **"AI Brief LATAM"** está pegado en:
- Carpeta `projects/ai-brief-latam/`
- Múltiples archivos .md con título
- Email business `aibrieflatam.media@gmail.com`

**Decisión pendiente:** Manuel confirma nombre nuevo en sesión futura. Opciones tentativas:
- "AI How-To LATAM"
- "IA Práctica LATAM"
- "Manual IA" (corto, brandable)
- "Práctica IA" (LATAM-friendly)
- "Cómo IA" (super corto, viral-friendly)

El rename físico (`git mv` + updates) se hace de una vez cuando el nombre esté locked.
