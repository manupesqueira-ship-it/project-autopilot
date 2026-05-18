# Post Standard — AI Brief LATAM

**Fecha:** 2026-05-12
**Status:** primera versión consolidada. Secciones marcadas "✋ PROPUESTA" requieren confirmación de Manuel.
**Reemplaza dispersión en:** `brand_voice.md`, `research/2026-05-07_format-and-voice-research.md`, `research/2026-05-07_latam-specific-research.md`, `research/2026-05-07_production-stack-research.md`, `docs/research/deep-research/_synthesis/*`, hallazgos de los 6 deep research.

> Este documento es la referencia ÚNICA que el sistema enforce. Cada prompt (a2-scorer, a3-editorial, a4-fact-checker, a7-copy-composer, a9-compliance) y cada decisión de gpt-image-2 / Seedance / ElevenLabs lee de acá. Si hay contradicción entre este doc y otro, **este gana**. Cuando se actualice, todos los prompts deben re-revisarse.

---

## 1. Voz editorial

**Framework:** Smart Brevity (Axios) + Morning Brew (casual sobrio).
**Source:** vendido por $525M (Axios) + $250M lifetime revenue (Morning Brew), validado en 9M+ posts (Socialinsider).

### Reglas duras (no negociables)

1. **Bold phrases ("axiomas") + 1 frase o bullets.** No párrafos largos.
2. **"Por qué importa" SIEMPRE presente.** Es el ingrediente sagrado. Nunca se omite.
3. **Subject-verb-object simple.** Escribir como humano, no como corporativo.
4. **Datos > opiniones.** Cifras concretas pegan más que adjetivos.
5. **Bottom line al final.** Cierre con la conclusión accionable.

### Refinamiento del template #12533 (adoptado 2026-05-12)

Smart Brevity SIN meta-labels obvios. NO usar etiquetas literales como "El Recap:" o "Bottom Line:" en el texto visible. La estructura debe FLUIR sin marcas que el lector identifique como template. Ejemplo:

❌ Mal:
> **Por qué importa:** Esto cambia las reglas de privacy en LATAM.
>
> **Bottom line:** Vas a tener que auditar tu stack en 60 días.

✅ Bien:
> Esto cambia las reglas de privacy en LATAM — la auditoría de stack pasa de "buena práctica" a obligación a 60 días.

(El "por qué importa" y el "bottom line" están AHÍ, pero invisibles como labels.)

---

## 2. Idioma

**Español neutro LATAM.** Sin peninsular, sin extremos regionales.

| ❌ NO usar | ✅ SÍ usar |
|---|---|
| **Peninsular:** vosotros, vuestro, vale, tío/tía, hostia, mola, ordenador, móvil, coche | ustedes, nuestro, está bien, ¿no?, listo, claro, dale, computadora, celular, carro |
| **MX extremo:** chido, padre, no manches, qué onda, órale | (mismos neutrales que arriba) |
| **AR extremo:** vos sos, che, viste, boludo, posta, sheísmo ("cashe", "plasha") | tú/usted, listo, claro |
| **Caribe extremo:** pa'lante, elisiones fuertes de "s" | pronunciación neutralizada |

- **Vocabulario técnico en inglés cuando es estándar:** AI, AGI, LLM, agent, deployment, enterprise, brief.
- **Cifras siempre con contexto:** no "$1.5B" suelto, sino "$1.5B reportado por WSJ".

---

## 3. Hook framework (Rufusocial 2026)

**Source:** Rufusocial (marzo 2026), confirmado por research social-media-niches-2026.

Todo hook (Reel o caption) debe pasar las **3 condiciones obligatorias**:

| # | Condición | Cómo se materializa |
|---|---|---|
| 1 | **ATENCIÓN** | Número inesperado, frase contraintuitiva, pregunta directa, claim sorprendente |
| 2 | **TENSIÓN** | Vacío de información, problema sin resolver, conflicto que el espectador quiere ver cerrado |
| 3 | **PROMESA** | Anticipa recompensa concreta (vas a aprender X, evitar error Y, descubrir Z) |

**Crítico:** el hook debe funcionar SIN sonido. Subtítulos = parte del hook visual. Primeros frames deben comunicar por sí solos.

### Hook families validados (del research)

Steal estos patrones como punto de partida:

- "This changes everything for [audience]…"
- "What nobody is explaining about [topic]…"
- "The real reason [event] happened…"
- "You're reading this [headline] wrong…"
- "This one chart/map explains…"
- "If you work in [job], this matters now…"
- "Before you believe the headline, watch this…"

Traducidos a español neutro:

- "Esto cambia todo para [audiencia]…"
- "Lo que nadie está explicando sobre [tema]…"
- "La razón real de por qué [evento] pasó…"
- "Estás leyendo mal este titular…"
- "Este gráfico/mapa lo explica…"
- "Si trabajás en [rol], esto importa AHORA…"
- "Antes de creerle al titular, mirá esto…"

### Primeros 3 segundos = TODO

- 50% de viewers se va si el hook no agarra en los primeros 3s (CreatorsJet, Socialinsider).
- Cifras grandes funcionan: "$10M ARR con 12 empleados — así lo hizo The Rundown."
- Pregunta directa funciona: "¿Tu pyme va a necesitar AI compliance en 2026?"
- Contraintuición funciona: "El error #1 en adopción de IA NO es elegir mal el modelo."

---

## 4. Format pillars (4 — restricción Fase 1)

**Source:** social-media-niches-2026 deep research + application-roadmap. **Adoptados como restricción obligatoria Fase 1** (no testear más formatos hasta validar estos).

Toda pieza tiene que encajar en uno de estos 4 patterns:

| # | Pillar | Duración / Forma | Cuándo se usa |
|---|---|---|---|
| 1 | **Explainer 35-75s** | Reel o carousel 5-7 slides con hook brutal en 3s | News flash, lanzamiento de modelo, anuncio |
| 2 | **Chart / map / data breakdown** | Carousel data-heavy o reel con voice over de gráficos | Datos de mercado, comparativas, métricas |
| 3 | **Ranking / myth-buster** | Carousel listicle o reel "5 cosas que…" | Tools comparativas, errores comunes, "10 X que…" |
| 4 | **"What this means for you"** | Carousel práctico o reel call-to-action | Implicaciones para founders/CFOs/marketers LATAM |

El campo `formato_recomendado` del brief A3 debe elegir UNO de estos 4 (no inventar nuevos en Fase 1).

---

## 5. Especificaciones técnicas por formato

### 5.1 Reels (formato principal Fase 2+)

| Dimensión | Spec | Source |
|---|---|---|
| **Largo** | **25-35 segundos** (sweet spot validated) | format-and-voice-research |
| **Aspect ratio** | 9:16 (1080×1920px) | platform standard |
| **Hook** | Primeros 3s = pattern interrupt brutal. Cifra grande, frase contraria, claim sorprendente | format-and-voice-research |
| **Pacing** | Jump cuts cada 3-4 seg | brand_voice.md |
| **Texto en pantalla** | SIEMPRE (muchos ven sin sonido) | brand_voice.md |
| **Audio** | Voz humana (Manuel) o voice clone ElevenLabs (cuando esté grabada) | ADR-008 + production-stack-research |
| **Música** | Opcional, sin marca de agua TikTok/CapCut (penalización 30-40% reach LATAM) | format-and-voice-research |
| **Cierre** | CTA específico ("Guardá esto", "Compartí con tu equipo"). NO "Seguinos" genérico | brand_voice.md |
| **Completion target** | 30-90s = SAVES & SHARES (lo que queremos como news brief) | format-and-voice-research |

### 5.2 Carousels (formato principal Fase 1)

| Dimensión | Spec | Source |
|---|---|---|
| **Cantidad de slides** | 5-7 (sweet spot) | a7-copy-composer + research |
| **Dimensión** | 1080×1080px (cuadrado) | platform standard |
| **Slide 1** | HOOK visual: cifra grande, claim sorprendente, o pregunta directa | a7-copy-composer |
| **Slides 2 a (n-2)** | Datos clave, antes/después, quién gana/pierde, breakdown | a7-copy-composer |
| **Slide (n-1)** | Ángulo LATAM con acciones específicas | a7-copy-composer |
| **Slide final** | CTA + branding (logo + handle) | a7-copy-composer |
| **Texto por slide** | Máx 30-40 palabras (legible en mobile) | propuesta |
| **Tono visual** | Ver §7 (Visual Standard) | ↓ |

### 5.3 Caption (Instagram)

| Dimensión | Spec | Source |
|---|---|---|
| **Largo total** | **<150 chars** (sweet spot) | brand_voice.md + Socialinsider 9.1M posts |
| **Hook visible (pre-"more")** | Primeros **125 chars** son críticos | brand_voice.md |
| **Estructura** | Hook con cifra + 1 frase contexto + CTA | brand_voice.md |
| **Emojis** | 1-2 estratégicos máximo. Permitidos: ⚡ 🏦 💼 📊 → | brand_voice.md |
| **Hashtags** | **5-10 niche** (NO 30 broad). Mix volumen alto + nicho | brand_voice.md |

### 5.4 TikTok caption (paralelo a IG)

| Dimensión | Spec | Source |
|---|---|---|
| **Largo total** | 100-300 chars (más largo que IG) | propuesta |
| **Tono** | Más casual, conversacional que IG | propuesta |
| **Hashtags** | 3-5 trending (no niche, algoritmo TT favorece broad) | propuesta |
| **Sample mix** | `#fyp #ia #tech #latam` + 1 contextual | propuesta |

### 5.5 Newsletter (Beehiiv, daily Fase 1)

**Estructura completa** (adoptada del template #12533 + adaptada al contexto LATAM):

```
[SUBJECT LINE]            ← 1 principal + 3-5 alternates generadas
[PRE-HEADER TEXT]         ← preview del email pre-open

[INTRO]
  Paragraph 1: hook directo (sin saludo), 2-3 frases
  Paragraph 2: contexto del día

[TOP STORIES (1-3)]
  Story 1:
    The Lead (intro 2-3 frases, sin label, con link)
    Key Details (the meat: specs, context, ángulo LATAM)
  Story 2: idem
  Story 3: idem

[QUICK HITS (3-5)]         ← stories que pasaron el filtro pero NO entraron en deep dive
  - Story 4: 1-2 frases + link
  - Story 5: 1-2 frases + link
  ...

[VIRAL VIDEO IDEAS]        ← 3 conceptos para el reel del día siguiente
  Concept 1 (Contrarian/Pattern Interrupt): título + 2 frases
  Concept 2 (Actionable Listicle/Hack): título + 2 frases
  Concept 3 (Story/Visual Metaphor): título + 2 frases

[FOOTER]
  Unsubscribe + dirección física (CAN-SPAM compliance)
  Logo + handle de IG
```

| Dimensión | Spec |
|---|---|
| **Largo total** | 600-1200 palabras (extended brief, NO copy del caption) |
| **Por qué importa** | Obligatorio, presente sin label literal |
| **Fuentes** | Linkeadas inline, no en footer |
| **CTA** | Variable: "Save this", "Share with your team", "Reply with your take" |

---

## 6. Audio standard (reels Fase 2+)

| Dimensión | Spec | Source |
|---|---|---|
| **Voz primaria** | Voice clone ElevenLabs de Manuel | ADR-008 |
| **Voz backup** | ElevenLabs default voices (solo multi-idioma o emergencia) | production-stack-research |
| **Acento** | Español neutro mexicano CDMX | production-stack-research |
| **Estilo lectura** | Pausas marcadas en hook (3s cuentan triple), bajada de tono en datos clave, aceleración en lista de hechos, ascendente en CTA | brand_voice.md |
| **Música** | NO marca de agua TikTok/CapCut. Solo stock con licencia o ambient sin copyright | format-and-voice-research |
| **Subtítulos** | OBLIGATORIOS (texto en pantalla siempre) | brand_voice.md |

### Reglas de pronunciación neutralizada (voice clone)

- **SÍ:** ustedes, carro, computadora, celular, manejar, platicar
- **SÍ:** pronunciar "z" y "c" como "s" (no ceceo)
- **NO peninsular:** vosotros, vale, ordenador, móvil, coche, ceceo
- **NO MX extremo:** chido, padre, no manches, órale
- **NO AR extremo:** vos sos, che, sheísmo ("calle"="cashe")

---

## 7. Visual Standard ✋ PROPUESTA (requiere confirmación Manuel)

> Esta sección NO existía hasta hoy. La propongo basándome en las cuentas LATAM benchmark (Ecosistema Startup, Startupeable, Mafia IA, Explicable) y el insight de research "minimalista tech sobrio > maximalista colorido" para audiencias profesionales.

### Dirección general: minimalismo profesional sobrio

**Reference accounts a copiar (en format architecture, no en assets):**
- Ecosistema Startup (LATAM, 12K IG) — casual sobrio, paleta tech
- Startupeable (LATAM, 27K IG) — premium analítico, tipografía limpia
- The Rundown AI (US, 436K IG) — minimalismo extremo, sin emojis bio

### Paleta de colores ✋ PROPUESTA

```
Background primary:    #0F0F10 (casi-negro, NO puro #000000)
Background secondary:  #1A1A1C (gris muy oscuro)
Text primary:          #FAFAFA (casi-blanco para contraste WCAG AA)
Text secondary:        #A0A0A8 (gris claro para subtítulos)
Accent / highlight:    #00D9A0 (verde-aqua para CTAs y data points)
Accent secondary:      #FF6B35 (naranja vibrante solo para alertas/urgencia)
Error / hard NO:       #E63946 (rojo solo para flags compliance)
```

**Por qué dark mode:** audiencia profesional en mobile lee en horarios mixtos (mañana, noche). Dark mode reduce fatiga visual + asociación visual "tech-pro" (vs light mode más "lifestyle/wellness"). El research de Visual Director (template #12533 inferido) y benchmarks LATAM apuntan a dark.

**Alternativa light mode** si Manuel prefiere:
```
Background:     #FAFAFA
Text primary:   #0F0F10
Text secondary: #4A4A52
Accent:         #006B4F (verde más oscuro para contraste)
```

### Tipografía ✋ PROPUESTA

- **Headlines (slide 1 hook, newsletter headline):** **Inter** o **Söhne** — bold weight, tracking ajustado
- **Body (slides 2-n, newsletter body):** **Inter** — regular o medium, line-height generoso
- **Mono (datos / cifras / URLs):** **JetBrains Mono** o **IBM Plex Mono**

**Por qué:** Inter es free (Google Fonts), excelente para mobile, usada por benchmarks tech (Vercel, Stripe, Linear). Söhne es paid premium si querés diferenciación pero no necesaria.

### Layout de carousel ✋ PROPUESTA

```
┌─────────────────────────────────┐
│                                 │
│      [HOOK BIG TEXT]            │  ← Slide 1: 24-36pt headline
│                                 │     centered, máx 8 palabras
│      $10M ARR con 12 empleados │     accent color en cifra
│                                 │
│            (small) AI Brief LATAM  ← handle bottom-right, 10pt
└─────────────────────────────────┘

┌─────────────────────────────────┐
│  ━━━━━━━━━                       │  ← Slides 2-n: 18pt headline
│  ¿Cómo lo lograron?              │     left-aligned
│                                 │
│  • Dual revenue stream          │  ← body: 14pt, bullets
│  • Bootstrapped 100%             │
│  • AI tooling stack             │
│                                 │
│  (small) Fuente: NGM 2026  →    │  ← source attribution bottom
└─────────────────────────────────┘

┌─────────────────────────────────┐
│                                 │
│   ¿Y para LATAM?                │  ← Slide (n-1): ángulo LATAM
│                                 │     accent color
│   El playbook aplica para       │
│   newsletters B2B españolas.    │
│                                 │
│   ¿Qué vertical te interesa?    │  ← question prompt → engagement
└─────────────────────────────────┘

┌─────────────────────────────────┐
│   GUARDÁ ESTO                   │  ← Slide final: CTA específico
│                                 │
│   📧 Newsletter daily.           │  ← link / handle
│      Link en bio.               │
│                                 │
│   @aibrieflatam                 │  ← branding final
└─────────────────────────────────┘
```

### Watermark / branding en imágenes ✋ PROPUESTA

- **Cada slide:** handle "@aibrieflatam" o "AI Brief LATAM" en bottom-right, font 10-12pt, color secondary (gris claro/oscuro según fondo), opacity ~60%.
- **NO marca de agua TikTok/CapCut.** Penalización 30-40% reach LATAM (research confirmado).
- **Logo:** TBD (Manuel — ¿tenés ya el logo o lo diseñamos? Si no hay, usamos solo wordmark "AI Brief LATAM" en Inter Bold).

### Mock-up ASCII del carousel ✋ PROPUESTA

Visualización de las 5 slides de un carousel típico aplicando el estándar. Sirve como referencia visual antes de gastar tokens con gpt-image-2.

#### Slide 1 — HOOK (1080×1080)

```
┌──────────────────────────────────────────────────┐
│ #0F0F10 (dark charcoal)                          │
│                                                  │
│                                                  │
│   80%                          ← #00D9A0 mint,   │
│   ┌─────┐                        Inter Bold,     │
│   │     │                        ~280pt          │
│                                                  │
│   de profesionales                               │
│   LATAM ya usa IA                ← #FAFAFA       │
│   en el trabajo.                   Inter Bold,   │
│                                    ~64pt         │
│                                                  │
│                                                  │
│                                                  │
│                                                  │
│                                                  │
│                          AI BRIEF LATAM          │
│                          ───────────             │
│                          JetBrains Mono 14pt     │
│                          #8A8A8E opacity 60%     │
└──────────────────────────────────────────────────┘

Composición: 60% canvas vacío, texto en upper-left.
Cifra masiva como punto focal. Sin íconos, sin imágenes.
```

#### Slide 2 — DATA POINT

```
┌──────────────────────────────────────────────────┐
│ #0F0F10                                          │
│                                                  │
│   LO QUE PASÓ            ← #8A8A8E gris,         │
│                            JetBrains Mono 18pt   │
│                                                  │
│   Encuesta IDC LATAM     ← #FAFAFA Inter Bold    │
│   en 7 países muestra      ~48pt                 │
│   adopción explosiva                             │
│   en 2026.                                       │
│                                                  │
│   ─────────────────────                          │
│                                                  │
│   • +42% YoY MX           ← #FAFAFA Inter        │
│   • +38% YoY BR             Medium ~32pt         │
│   • +29% YoY AR                                  │
│                                                  │
│                          AI BRIEF LATAM          │
└──────────────────────────────────────────────────┘

Composición: estructura lead + bullets, datos puros, sin
emojis. Línea divisora ────── separa contexto de cifras.
```

#### Slide 3 — COMPARISON (antes / después)

```
┌──────────────────────────────────────────────────┐
│ #0F0F10                                          │
│                                                  │
│   2024              2026                         │
│                                                  │
│   18%               80%        ← cifras grandes  │
│                                  Inter Bold      │
│   ┌─────┐         ┌─────┐        ~180pt          │
│   │     │         │ #00D9A0      número derecho  │
│   │  ▓  │         │  ▓▓▓ │       en mint accent  │
│   │     │         │ ▓▓▓▓▓│                       │
│   └─────┘         └─────┘        ← barras simples│
│                                    Unicode block │
│                                                  │
│   Uso ocasional   Uso diario   ← #8A8A8E Inter   │
│                                  Medium ~28pt    │
│                                                  │
│                          AI BRIEF LATAM          │
└──────────────────────────────────────────────────┘

Composición: split vertical, two-column. Visualización
mínima con caracteres Unicode (▓ █ ▒ ░) si gpt-image-2
no genera gráficos consistentes. Alternativa: barras
post-procesadas en Pillow/Sharp.
```

#### Slide 4 — LATAM ANGLE (penúltima)

```
┌──────────────────────────────────────────────────┐
│ #0F0F10                                          │
│                                                  │
│   QUÉ SIGNIFICA PARA TI  ← #8A8A8E gris,         │
│                            JetBrains Mono 18pt   │
│                                                  │
│   Si trabajás en            ← #FAFAFA Inter      │
│   banca/retail LATAM,         Bold ~48pt         │
│   tu competencia                                 │
│   ya está usando IA.                             │
│                                                  │
│   ─────────────────────                          │
│                                                  │
│   Acciones esta semana:                          │
│                                                  │
│   1. Identificá 1 task      ← #FAFAFA Inter      │
│      que repetís diario       Medium ~28pt       │
│   2. Pedí a ChatGPT que                          │
│      te asista 5 días                            │
│   3. Mediá el ahorro                             │
│                                                  │
│                          AI BRIEF LATAM          │
└──────────────────────────────────────────────────┘

Composición: ángulo LATAM con acciones concretas.
Numbered list es POR ALGO — el orden señala prioridad
y se save-ea mejor que bullets (research social media).
```

#### Slide 5 — CTA + branding (última)

```
┌──────────────────────────────────────────────────┐
│ #0F0F10                                          │
│                                                  │
│                                                  │
│                                                  │
│         AI BRIEF                ← wordmark       │
│         LATAM                     Inter Bold     │
│                                   ~96pt          │
│                                   #FAFAFA        │
│         ────────────                             │
│         JetBrains Mono            ← tagline      │
│         #8A8A8E 20pt              gris bajo      │
│                                                  │
│         Noticias de IA                           │
│         para LATAM, en 3 min.   ← Inter Medium   │
│                                   #FAFAFA 32pt   │
│                                                  │
│         → Guardá este post                       │
│         → Compartí con tu                        │
│           equipo                  ← CTA, Inter   │
│         → Suscribite (link bio)   Medium #00D9A0 │
│                                   accent en →    │
│                                                  │
└──────────────────────────────────────────────────┘

Composición: centered, todo el mensaje en upper-center.
Tres acciones concretas. Mint accent en arrows guía la
mirada. NO emojis, NO "swipe to see more".
```

#### Notas de aplicación

| Decisión visual | Por qué |
|---|---|
| **Misma slide template para los 5** | Consistencia inmediata, no decision-fatigue para A5 |
| **#00D9A0 mint accent SOLO en data + arrows** | Si todo es accent, nada es accent — restringido a 1 elemento por slide |
| **Watermark idéntico en TODAS** | Anclaje cognitivo — visible pero discreto |
| **NO emojis dentro de la imagen** | Emojis viven en el caption, no en el visual (regla del POST_STANDARD §3.5) |
| **Cifras > texto en hierarchy** | Hook visual = la cifra. El texto la contextualiza. |
| **Negative space ≥ 40%** | Editorial premium ≠ feed cargado |
| **Tipografía fija (Inter + JBM)** | Brand recognition cross-feed |

#### Limitaciones conocidas de gpt-image-2

1. **Tipografía:** gpt-image-2 renderiza Inter de forma inconsistente. Si la calidad cae, considerar **post-procesado en Pillow/Sharp** (generar fondo limpio + agregar texto programáticamente con FreeType).
2. **Barras / gráficos:** poco confiables. Fallback: Unicode block characters (▓▒░█) o post-procesado con matplotlib headless.
3. **Watermark:** el wordmark "AI BRIEF LATAM" en bottom-right tiende a deformarse. **Mejor agregarlo en post-procesado** como overlay PNG.
4. **Resolución:** gpt-image-2 max nativo 1024×1024. Up-rezear a 1080×1080 con Lanczos resampling para IG carousel native.

### Mock-up ASCII del newsletter (Beehiiv daily) ✋ PROPUESTA

Equivalente al mock-up del carousel pero para el formato newsletter. Email se ve básicamente como texto + 1-2 imágenes opcionales. Estructura adoptada del template #12533 traducida al español neutro LATAM.

```
┌───────────────────────────────────────────────────────────────────┐
│  [Subject line en inbox]                                          │
│  ────────────────────────────────────────                         │
│  ▌80% LATAM ya usa IA. Acá los datos que faltaban.   ← 30-60 ch  │
│                                                                   │
│  [Pre-header text, gris claro en preview]                         │
│  Encuesta IDC + qué hace tu competencia esta semana   ← 40-90 ch │
└───────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║          AI BRIEF LATAM                                           ║
║          ──────────────                                           ║
║          Martes 12 de mayo, 2026                                  ║
║                                                                   ║
║  ───────────────────────────────────────────────────────────      ║
║                                                                   ║
║  La mayoría de las encuestas LATAM sobre adopción IA medía 2024.  ║
║  El número del 18% se quedó pegado en headlines un año entero.    ║
║  El último corte de IDC, publicado ayer, muestra otro mundo.      ║
║                                                                   ║
║  ┌──────────────────────────────────────────────────────────┐    ║
║  │ El 80% de profesionales LATAM ya usa IA en el trabajo    │    ║
║  │ ──────────────────────────────────────────────────────── │    ║
║  │                                                          │    ║
║  │ IDC encuestó 12,000 knowledge workers en 7 países entre  │    ║
║  │ enero y marzo de 2026. La adopción saltó de 18% a 80%    │    ║
║  │ year-over-year. → Reporte completo (link)                │    ║
║  │                                                          │    ║
║  │ Los números por país: MX +42%, BR +38%, AR +29%, CO      │    ║
║  │ +35%, CL +31%. Ningún país bajo +25%. La velocidad de    │    ║
║  │ adopción supera la curva US 2024 (60% en mismo período). │    ║
║  │                                                          │    ║
║  │ El uso no es uniforme: 67% lo usa para tareas internas   │    ║
║  │ (resumen de docs, drafting), solo 23% para customer-     │    ║
║  │ facing. El gap señala dónde está la oportunidad real:    │    ║
║  │ automatizar customer service en LATAM antes que la       │    ║
║  │ competencia.                                             │    ║
║  │                                                          │    ║
║  │ Si trabajás en retail, fintech o telco LATAM, tu equipo  │    ║
║  │ ya está usando IA — la pregunta es si lo estás midiendo. │    ║
║  │ Empezá midiendo qué tareas y cuántas horas.              │    ║
║  └──────────────────────────────────────────────────────────┘    ║
║                                                                   ║
║  ───────────────────────────────────────────────────────────      ║
║                                                                   ║
║  Quick Hits                                                       ║
║                                                                   ║
║  → Anthropic abrió oficina en CDMX. Primer hire es head de        ║
║    enterprise sales LATAM. (link)                                 ║
║                                                                   ║
║  → Mercado Libre integra Claude en su CRM interno. 40K            ║
║    empleados con acceso desde abril. (link)                       ║
║                                                                   ║
║  → CNBV México publicó guía de uso IA en banca. No prohíbe        ║
║    nada, exige logging y human-in-the-loop. (link)                ║
║                                                                   ║
║  → Kavak cortó 30% del equipo de QA después de implementar        ║
║    agentes Claude para revisión de listings. (link)               ║
║                                                                   ║
║  → Bitso lanzó "Bitso AI" — un asistente conversacional para      ║
║    onboarding crypto. Disponible solo MX por ahora. (link)        ║
║                                                                   ║
║  ───────────────────────────────────────────────────────────      ║
║                                                                   ║
║  ¿Algo de esto te cambió la semana?                               ║
║                                                                   ║
║  Respondé este mail con tu take. Lo leo todo — los mejores         ║
║  responses los incluyo en el newsletter del jueves (con           ║
║  crédito + link a tu perfil si querés).                            ║
║                                                                   ║
║  Hasta mañana,                                                    ║
║  Manuel                                                           ║
║                                                                   ║
║  ───────────────────────────────────────────────────────────      ║
║                                                                   ║
║  AI BRIEF LATAM · Noticias de IA para LATAM en 3 minutos          ║
║                                                                   ║
║  [Suscribite] [Compartí]   ← Beehiiv buttons                      ║
║                                                                   ║
║  ───────────────────────────────────────────────────────────      ║
║                                                                   ║
║  [Footer CAN-SPAM]                                                ║
║  AI Brief LATAM · <dirección física pendiente OPEN_QUESTIONS M>   ║
║  Te enviamos esto porque te suscribiste en aibrieflatam.media     ║
║  [Unsubscribe] [Update preferences]                               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

#### Notas de aplicación

| Decisión | Por qué |
|---|---|
| **Sin saludo en el intro** | Adoptado de The Rundown / Morning Brew — el reader abrió porque le interesa el contenido, no porque te quiera saludar |
| **Bloque visual para Top Story** | Diferencia visual que separa deep-dive de quick hits sin usar meta-labels |
| **Quick Hits con `→` arrow** | Indicador visual de "rapid scan" — el reader sabe que esto es para escanear rápido |
| **CTA reply real** | "Respondé este mail" funciona como engagement signal (Beehiiv mide replies) y como source de feedback para mejorar |
| **Firma "Manuel"** | Personalidad — Newsletter sin firma humana se siente generada |
| **Footer Beehiiv standard** | Compliance CAN-SPAM cubierto por Beehiiv si cargás dirección física en settings |

#### Limitaciones conocidas Beehiiv

1. **Subject A/B testing:** Beehiiv lo soporta nativo. Los 5 alternates de A8d se cargan automático.
2. **Imágenes en el email:** soportadas pero penalizan deliverability si el ratio image/text es alto. Mantener email **text-heavy** (1 imagen máx por edición).
3. **Links:** Beehiiv reescribe links para tracking. UTMs custom no necesarios.

---

## 8. LATAM-specific rules

**Source:** latam-specific-research.md (7 hallazgos clave).

### Reglas obligatorias

1. **Emojis SÍ se usan** — TODAS las top cuentas LATAM usan emojis en bio. Lista aprobada: ⚡ 🏦 💼 📊 → 🤖 📧
2. **"Comunidad" es código cultural** — pega más que "audiencia" o "lectores". Usar en bio, CTAs, taglines.
3. **Tagline formula:** VALOR + TIEMPO + IDIOMA/REGIÓN + PRECIO. Ejemplo: "Noticias de IA para LATAM. 5 min. Gratis cada día."
4. **Multi-channel funnel** — Newsletter es activo central, IG y TikTok son canales de adquisición. NO all-in en IG.
5. **Caras reales > postureo pulido** (+25% retención). Cuando aplique, mostrar caras del equipo.
6. **Hooks framework Rufusocial** (ver §3).
7. **Sin marca de agua TikTok/CapCut.**

### Benchmarks realistas (anclaje mental)

- 1K followers = base creíble
- 5K = niche success
- 12-30K = top tier LATAM (Ecosistema Startup, Startupeable)
- 100K+ = excepcional (DotCSV, Nicolas Abril)
- 400K+ = no existe equivalente regional. The Rundown AI no tiene par LATAM.

**Target realista AI Brief LATAM:** 12-30K en 12-18 meses sería un home run.

---

## 9. Hard NO's (compliance enforced)

**Source:** brand_voice.md + a9-compliance.md.

### Lista absoluta — NUNCA publicar

1. **Hype injustificado** ("revolutionary", "game-changing" sin razón)
2. **Predicciones irresponsables** ("este modelo va a destruir X industria")
3. **Listicles sin sustancia** ("10 prompts para ganar dinero con IA")
4. **Memes baratos** (sin valor editorial)
5. **Marca de agua de otras plataformas** (TikTok/CapCut/Veo)
6. **Más de 1 emoji por frase**
7. **Cifras sin fuente** ("$1B" sin "reportado por X")
8. **Copy textual de otra fuente** sin transformación sustancial
9. **Claims financieros sin disclaimer** (raro en how-to IA, pero aplica si la pieza toca dinero/inversión)
10. **Forbidden patterns:** "esto va a cambiar el mundo", "el fin de [industria]", "reemplaza completamente a"

### Hard YES's — siempre

1. **Datos verificables con fuente**
2. **"Por qué importa" explícito** (en estructura, no como label)
3. **Ángulo LATAM concreto**
4. **Voz neutral y respetuosa**
5. **Reconocer incertidumbre cuando existe** ("WSJ reportó X, fuente no confirmada")

---

## 10. Quality bar / kill criteria

### Cuándo se descarta una pieza automáticamente

| Trigger | Acción |
|---|---|
| A2 Signal Scorer: `total_score < 50` | Discard, no avanza |
| A4 Fact-Checker: `verdict = fail` | Discard, vuelve al siguiente del shortlist |
| A4 Fact-Checker: `critical_issues.length > 0` | Discard salvo override Manuel |
| A9 Compliance: `verdict = blocked` después de 2 reintentos | Discard |
| A9 Compliance: `blocks.length > 0` (cualquier block) | Re-generar A7, max 2 reintentos |
| Más de 2 risk_flags previos del scorer | Flag + review Manuel obligatoria |

### Cuándo se manda con FLAG amarillo

| Trigger | Acción |
|---|---|
| A4 verdict = `pass_with_edits` | Auto-aplica suggested_rewrites, sigue |
| A4 verdict = `needs_review` | Telegram con FLAG amarillo, espera Manuel |
| A9 verdict = `approved_with_warnings` | Telegram con FLAG amarillo + lista warnings |

---

## 11. Métricas priorizadas (algoritmo 2026)

**Source:** social-media-niches-2026 + brand_voice.md.

### Orden de prioridad

1. **Watch time / average completion** (no completion absoluto, retention curve)
2. **Shares + Saves** (saves > follows en algoritmo 2026)
3. **Follows** (no es la métrica madre)
4. **Raw views** (no engagement, no significa nada)

### Targets Fase 1 (soft, primer mes)

- 200-500 followers en 30 días
- 30-80 newsletter signups en 30 días
- Engagement rate >4% en 5+ piezas
- 0 errores de fact-check detectados post-publicación

### Criterios para "validar el formato" (post-Fase 1)

- **Doblar down** cuando 2 de las últimas 10 piezas hacen 3× median views, shares/saves arriba del average, comentarios pidiendo más
- **Iterar prompt** cuando 5 piezas seguidas tienen hold rate <30% en primeros 3s
- **Matar el formato** después de 15-20 piezas con weak hold + 0 shares/saves

---

## 12. Frecuencia y cadencia

**Source:** ADR-011 + OPEN_QUESTIONS A.

| Fase | Output diario |
|---|---|
| **Fase 1** | 1 carousel IG + 1 TikTok caption (paralelo) + 1 newsletter section. **Mismo trigger ~6 AM CDMX, publish ~8 AM CDMX.** |
| **Fase 2** | + 1 reel (mismo brief o brief alterno según `formato_recomendado`) |
| **Fase 3** | + landing page activa |
| **Fase 4** | + 1 podcast episode/semana |

**Re-evaluar daily → weekly newsletter** si open rate < 25% o fricción operativa es alta.

---

## 13. Cómo este doc se aplica en el sistema

Cada prompt apunta a este doc:

- **a2-signal-scorer.md** → enforza §1 (voz), §8 (LATAM rules), §9 (hard NOs)
- **a3-editorial.md** → enforza §1 (Smart Brevity), §3 (hook), §4 (format pillars), §8 (LATAM)
- **a4-fact-checker.md** → enforza §9 (hard NOs sobre claims sin fuente)
- **a7-copy-composer.md** → enforza §1 (voz), §5 (specs por formato), §9 (hard NOs)
- **a9-compliance.md** → enforza §9 completo + §2 (idioma) + §1 (voz)
- **gpt-image-2 prompts (A8a):** enforza §7 (visual standard)
- **ElevenLabs (A8c, Fase 2):** enforza §6 (audio standard)

Cuando se actualiza este doc, los prompts deben actualizarse también. Tarea: agregar `<!-- POST_STANDARD §X -->` comments en cada prompt indicando qué sección referencia.

---

## 14. Open items en este doc

- [ ] §7 Visual standard — Manuel confirma paleta + tipografía + layout o propone cambios
- [ ] §7 Logo — ¿existe o lo diseñamos?
- [ ] §5.5 Newsletter footer dirección física (CAN-SPAM) — necesitamos dirección
- [ ] §6 ElevenLabs voice — pendiente grabación 20 min de Manuel
- [ ] §10 Override Manuel de critical_issues — definir cómo se ejerce desde Telegram
- [ ] Audit periódico — revisar este doc cada 30 días o post 12-18 piezas para iterar
