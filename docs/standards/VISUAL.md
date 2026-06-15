> ⚠️ **OBSOLETO (2026-06-03).** Este doc describe una arquitectura MUERTA (gpt-image-2 + Seedance + agentes A5/A8). La pipeline real es Remotion + Blender. **Fuente de verdad vigente: [`DINERO_IA_STYLE_BIBLE.md`](./DINERO_IA_STYLE_BIBLE.md).** Se conserva solo por audit trail (la paleta y tipografía siguen vigentes y están migradas al Style Bible).

# Visual Standard — Dinero IA

**Versión:** 1.0
**Fecha:** 2026-06-01
**Base:** `projects/dinero-ia/research/2026-06-01_top-performers-benchmark.md` (13 creators analizados)
**Aplica a:** A5 Visual Director, A8a Image Gen (gpt-image-2), A8b Video Gen (Seedance), A8e Compositor

> Este doc es el source-of-truth visual. Cualquier prompt que A5 genere, cualquier keyframe que A8a renderice, cualquier video que A8b anime — debe cumplir estos standards. Si un node los rompe sin justificación, A9 Compliance lo bloquea.

---

## 1. Paleta de color (locked)

| Rol | Hex | Uso |
|---|---|---|
| **Fondo dominante** | `#0D1117` | Backgrounds de keyframes, base universal |
| **Fondo secundario** | `#1A1A2E` | Variante levemente más cálida para escenas con texto largo |
| **Acento principal (cifras / data)** | `#D4A574` | Dorado cálido — números, montos, %, llamadas a la cifra |
| **Acento secundario (data positiva / IA)** | `#00D9A5` | Cyan-mint — para resaltar IA/tech, contrastar con dorado |
| **Texto primario** | `#FFFFFF` | Headlines, hooks, on-screen text bold |
| **Texto secundario** | `#A0A0B0` | Body text, fuentes, fechas, captions discretos |
| **Alerta / riesgo** | `#FF6B6B` | Solo para disclaimers críticos o cifras negativas |

**Filosofía:** dark mode tech (estilo Rowan/Riley/DotCSV) + acento dorado cálido (estilo Codie/Humphrey) — el cruce evita caer en "AI grifter neon" puro o "banco verde corporativo".

### Combinaciones prohibidas

- ❌ Verde corporativo `#00A86B` (es Mis Propias Finanzas — confusión de marca)
- ❌ Magenta neon `#FF00C8` (cae en estética AI hype Matt Wolfe — perdemos seriedad financiera)
- ❌ Fondo claro / white mode (rompe identidad)
- ❌ Más de 2 acentos por slide (saturación)

---

## 2. Tipografía

| Uso | Familia | Peso | Tamaño relativo |
|---|---|---|---|
| **Hook principal** (slide 1 / primer 3s) | Inter | Bold (700) o Extra-Bold (800) | 84-110 pt en 1080×1920 |
| **Headlines secundarios** | Inter | Bold (700) | 56-72 pt |
| **Body / explicativo** | Inter | Medium (500) | 36-48 pt |
| **Cifras destacadas** | Inter | Black (900) | 100-140 pt — siempre con acento `#D4A574` |
| **Captions / fuentes / fechas** | JetBrains Mono | Regular (400) | 22-28 pt — siempre `#A0A0B0` |
| **Disclaimer** | JetBrains Mono | Regular (400) | 24-30 pt — `#A0A0B0` |

**Fallbacks aceptables si Inter no está disponible:** Roboto Bold, Manrope Bold.
**Fallbacks aceptables para JetBrains Mono:** Fira Code, IBM Plex Mono.

### Reglas tipográficas duras

1. **Una sola familia sans por slide** (Inter solo). Mezclar Inter + Roboto = no.
2. **Mono solo en captions, fuentes, código.** Nunca para hooks o body.
3. **Tracking:** -0.02em para hooks, 0 para body, +0.02em para mono.
4. **Line-height:** 1.1 para hooks, 1.4 para body.

---

## 3. Composición de keyframes (Seedance input)

Los keyframes que A8a genera con gpt-image-2 son los inputs que A8b (Seedance) anima. La composición debe estar diseñada para ANIMACIÓN, no para imagen estática.

### Reglas de composición

| Regla | Detalle |
|---|---|
| **Formato** | 1080×1920 (vertical 9:16) — NUNCA cuadrado o landscape |
| **Safe area** | 100px margen superior + 200px margen inferior (deja espacio para UI Instagram/TikTok) |
| **Foco central** | El elemento principal en el tercio central (no el centro exacto — leve offset alto) |
| **Negative space generoso** | 40-60% del frame debe ser espacio vacío. Saturación de elementos = no parece premium |
| **Movimiento implícito** | Cada keyframe debe sugerir hacia dónde se anima (líneas de fuga, flechas implícitas, gradientes direccionales) — Seedance interpola mejor con dirección clara |
| **Sin caras reales humanas** | NUNCA. Solo screenshots reales de IAs, props abstractos, dataviz, símbolos |
| **Screenshot real de Claude/ChatGPT** | Cuando aplique, mostrar UI real con prompt + respuesta — diferencial único Dinero IA |

### Tipos de keyframes (catalogados)

| Tipo | Función | Ejemplo Seedance prompt |
|---|---|---|
| **K1 — Hook frame** | Slide 1 con hook + cifra grande | Centered bold text, golden accent on number, dark background, minimal animation suggestion (scale-in) |
| **K2 — Data frame** | Visualización de cifra/contexto | Number with source attribution below in mono, dark, possible chart hint as silhouette |
| **K3 — Screenshot frame** | UI real de Claude/ChatGPT | Real Claude.ai or ChatGPT screenshot composite over dark gradient, with annotation arrows pointing to key text |
| **K4 — Step frame** | Paso del prompt o workflow | Numbered "1." or "2." with body text, dark, golden number badge |
| **K5 — Comparison frame** | Antes vs después / opción A vs B | Two columns or side-by-side stacked, dark, mint accent on winner side |
| **K6 — Disclaimer frame** | Cierre obligatorio si productos | Small text bottom-area, mono font, gray color, branded logo bottom-right |

---

## 4. Logo y branding consistente

**Wordmark:** "Dinero IA" en Inter Black 32pt, color `#D4A574`, posición bottom-right con padding 60px.

**Watermark:** aparece en TODOS los frames (incluso K1 hook) pero discreto — no domina la composición.

**Variante:** en frames muy minimales (K1 hook), wordmark se mueve a bottom-center con tamaño 24pt y color `#A0A0B0` (menos prominente).

---

## 5. Estilo de animación (A8b Seedance)

**Filosofía:** las animaciones deben ser **sutiles, no épicas**. Estilo editorial premium (NYT, Bloomberg) — NO TikTok hype con zoom-shake-cuts cada 0.5s.

### Patrones de animación aceptables

| Pattern | Cuándo usar | Duración |
|---|---|---|
| **Scale-in suave** | Hook reveal, cifra grande aparece | 0.6-0.9s |
| **Slide-up** | Body text entra desde abajo | 0.4-0.6s |
| **Fade + scale** | Transición entre frames | 0.3-0.5s |
| **Cifra animada (counter)** | Cifra grande sube de 0 al valor | 1.0-1.5s |
| **Highlight pulse** | Cifra destacada pulsa una vez | 0.5s |
| **Cut directo** | Cambio rápido de frame | instantáneo |

### Patrones prohibidos

- ❌ Zoom-shake repetitivo
- ❌ Rotación 360°
- ❌ Glitch effects (cae a AI hype)
- ❌ Particle effects elaborados
- ❌ Lens flares
- ❌ Flash blanco entre cortes

### Frecuencia de cortes

- **Hook (0-3s):** 1 frame fijo, animation interna sutil (scale-in)
- **Body (3-40s):** corte cada **2.5-4 segundos** (sweet spot Hoyos = retention sin sobrecarga)
- **Cierre (40-55s):** 1-2 frames últimos, transition suave a disclaimer

**Total estimado de frames por reel de 45s:** 10-14 frames.

---

## 6. Prompts gpt-image-2 — template estándar

A8a debe generar prompts que cumplan TODOS los criterios anteriores. Template base:

```
Editorial design composition, 1080x1920 vertical (9:16 reel format).
Dark charcoal background hex #0D1117.

Subject: [DESCRIPCIÓN DEL CONTENIDO DEL FRAME]

Typography: Inter Bold for headline reading exactly "[TEXTO DEL FRAME]" in pure white #FFFFFF.
Inter Black for the number "[CIFRA]" in golden #D4A574, sized prominently.
JetBrains Mono Regular for caption bottom-right reading "DINERO IA" in #A0A0B0.

Composition: subject in upper-third center, generous negative space (40-60% empty),
implicit movement direction [LEFT/RIGHT/UP/DOWN/CENTER].

Style: minimalist editorial, premium magazine aesthetic, no stock photos,
no human faces, no cartoons, no glitch effects, no particles.
Mood: serious financial education with AI tech accent.

Lighting: soft directional shadow from upper-left if any depth needed.
Avoid: warm white #FFFFFF backgrounds, magenta neon, green corporate,
multiple accent colors, busy compositions.
```

**A5 Visual Director llena los `[bracketed placeholders]` con contenido específico por keyframe.**

---

## 7. Subtitles / closed captions

**Obligatorio en todos los reels** — 85% de viewers IG/TikTok scrollean sin sonido.

| Aspecto | Detalle |
|---|---|
| Font | Inter Bold |
| Tamaño | 48-56pt |
| Color | `#FFFFFF` con outline negro `#000000` 4px |
| Posición | Centrado horizontal, 65% de altura desde arriba (no abajo — UI Instagram tapa) |
| Estilo | Una línea visible a la vez (max 6-8 palabras) |
| Highlight | Palabra hablada en ese instante en color `#D4A574` |
| Timing | Sync exacto con audio (no leadout, no delay >100ms) |

A8e Compositor genera subs automáticamente a partir del SSML de A6 + voice output de A8c.

---

## 8. Diferenciadores visuales únicos Dinero IA

Lo que NADIE en LATAM hace y debemos hacer:

1. **Screenshot REAL de Claude/ChatGPT** dando respuestas financieras concretas (en pesos, soles, USD según país)
2. **Dataviz simples animados** (barras de 2-3 valores, no charts complejos)
3. **Dark mode siempre** (LATAM finance creators usan white/verde — nos diferenciamos)
4. **Cifras grandes en dorado** + contexto país + fecha (estilo Bloomberg pero accesible)

---

## 9. Checklist visual para A9 Compliance

Antes de pasar al compositor, A9 verifica:

- [ ] Paleta cumple specs (dark + dorado + cyan máx 2 acentos)
- [ ] Tipografía cumple (Inter para texto + JetBrains Mono para captions)
- [ ] Wordmark "Dinero IA" presente en cada frame
- [ ] Safe area respetada (100px top, 200px bottom)
- [ ] No caras humanas reales
- [ ] Disclaimer presente si productos_mencionados.length > 0
- [ ] Subs en sync con audio
- [ ] Duración total 30-60s (sweet spot 35-55s)
