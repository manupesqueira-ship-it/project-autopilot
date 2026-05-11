# Content Strategy — AI Brief LATAM

## Angulo editorial: AI Brief LATAM generalista

### Audiencia target
Founders, operators, consultores, y profesionales en Latinoamérica que necesitan mantenerse al día con AI sin perder horas leyendo fuentes en inglés. Nivel de conocimiento: intermedio (saben qué es un LLM, usan herramientas AI, pero no son researchers ni ML engineers).

### Tono y voz
- **Framework:** Smart Brevity (Axios) + Morning Brew casual
- **Idioma:** Español neutro LATAM (evitar regionalismos fuertes de un solo país)
- **Postura:** Anti-hype. Datos > opiniones. Nunca "esto va a cambiar el mundo". Siempre "esto es lo que pasó, esto es lo que significa para ti"
- **Personalidad:** Inteligente pero accesible, como un amigo informado que te resume las noticias en el café
- **Formato de escritura:** Hook directo, contexto breve, dato clave, ángulo LATAM

### Lo que cubrimos
- Lanzamientos de modelos y herramientas AI (OpenAI, Anthropic, Google, Meta, Mistral, etc.)
- Aplicaciones prácticas de AI en negocios, especialmente relevantes para LATAM
- Regulación y governance de AI (global + LATAM)
- Funding y M&A en el espacio AI
- Investigación académica con implicaciones prácticas
- Adopción de AI en empresas y gobiernos de LATAM
- Herramientas y workflows para profesionales

### Lo que NO cubrimos
- Crypto/blockchain (salvo intersección directa con AI)
- Hardware reviews sin ángulo de AI
- Tutoriales paso-a-paso (no somos un curso)
- Opiniones editoriales fuertes (somos curación, no opinión)
- Rumores sin fuente verificable
- Contenido hype/sensacionalista ("AGI is here", "X job is dead")

---

## Volumen y frecuencia

| Métrica | Valor |
|---------|-------|
| Piezas por día | 3 |
| Piezas por semana | 21 |
| Piezas por mes | ~84 |
| Días activos | Lunes a domingo (AI news no para) |

### Mix de formatos por fase

| Fase | Carousels/día | Reels/día | Newsletter | Podcast |
|------|---------------|-----------|------------|---------|
| Fase 1 | 3 | 0 | No | No |
| Fase 2 | 2 | 1 | No | No |
| Fase 3 | 2 | 1 | 1/día | No |
| Fase 4 | 2 | 1 | 1/día | 1-2/semana |

El mix carousel/reel se ajustará según datos de engagement después de las primeras 2 semanas de Fase 2.

---

## Scheduling

### Horarios de publicación (CDMX / UTC-6)

| Slot | Hora CDMX | Hora Argentina (UTC-3) | Hora Colombia (UTC-5) | Rationale |
|------|-----------|------------------------|----------------------|-----------|
| Mañana | 8:00 AM | 11:00 AM | 9:00 AM | Commute / inicio de jornada |
| Mediodía | 1:00 PM | 4:00 PM | 2:00 PM | Lunch break / pausa laboral |
| Noche | 7:00 PM | 10:00 PM | 8:00 PM | Post-trabajo / scroll nocturno |

### Revisión de horarios
Después de los primeros 30 posts, revisar Instagram Insights para:
- Confirmar o ajustar horarios según actividad real de audiencia
- Identificar si algún slot tiene consistentemente menor engagement
- Evaluar si fines de semana necesitan horarios diferentes

---

## Formatos por fase

### Fase 1: Carousels (semana 1-2)
- **Formato:** Carousel Instagram 1080x1080, 4-8 slides
- **Slide 1:** Hook visual (texto grande + visual impactante)
- **Slide 2-6:** Contenido (Smart Brevity: why it matters, key data, LATAM angle)
- **Slide 7-8:** CTA (follow + share + guardar)
- **Generación:** gpt-image-2 via OpenAI API
- **Crosspost:** TikTok (carousel nativo) via Buffer

### Fase 2: +Reels (semana 3-4)
- **Formato:** Reel 1080x1920, 15-30 segundos
- **Estructura:** Hook visual (3s) → Contexto (10-15s) → Dato clave (5s) → CTA (3s)
- **Audio:** Voiceover con voz clonada de Manuel (ElevenLabs)
- **Video:** Generado con Seedance 2.0 (imágenes + transiciones)
- **Subtítulos:** Automáticos, estilo bold keyword

### Fase 3: +Newsletter (semana 5-6)
- **Formato:** Email diario via Beehiiv
- **Estructura:** 3 noticias del día, cada una en formato Smart Brevity expandido
- **Secciones:** Titular → Resumen → Why it matters → Dato clave → Link a fuente
- **Subject line:** Optimizada para open rate (A/B test si Beehiiv lo permite)
- **CTA:** Responde este email / Comparte con un colega

### Fase 4: +Podcast (mes 2+)
- **Formato:** Episodio semanal, 5-10 minutos
- **Estructura:** Intro (30s) → 3-5 noticias top de la semana → Cierre + CTA (30s)
- **Voz:** Clone de Manuel (ElevenLabs)
- **Distribución:** Spotify for Podcasters
- **Cross-promotion:** Clips de 30s como reels, mención en newsletter

---

## Distribución multi-canal

### Instagram (@breiflatam)
- Canal principal de crecimiento
- Carousels + Reels
- Stories para engagement (polls, preguntas, behind-the-scenes del sistema AI)
- Link en bio hacia newsletter landing

### TikTok (@ai.brief.latam)
- Crosspost de carousels y reels via Buffer
- Adaptar captions al estilo TikTok (más casual, más directo)
- Hashtags adaptados para TikTok (diferente ecosistema que IG)

### Newsletter (Beehiiv)
- Canal de audiencia propia (no dependiente de algoritmo)
- Brief diario extendido
- Fase 3+

### Landing page
- Captura de emails para newsletter
- Portfolio de mejores piezas
- Lovable.dev o alternativa
- Fase 3+

### Podcast (Spotify)
- Resumen semanal en audio
- Fase 4+

---

## Métricas

### 30 días (fin de Fase 1-2)

| Métrica | Target | Cómo medir |
|---------|--------|------------|
| Followers IG | 500 | Instagram Insights |
| Newsletter subs | 100 (si Fase 3 arranca) | Beehiiv dashboard |
| Piezas con >4% engagement | 5+ | Instagram Insights (likes+comments+saves+shares / reach) |
| Fact-check errors | 0 | Manual review + A4 logs |
| Costos mensuales | <$150 | API billing dashboards |

### 60 días (fin de Fase 3)

| Métrica | Target | Decisión asociada |
|---------|--------|-------------------|
| Followers IG | 1,500 | Si <500, revisar contenido y horarios |
| Newsletter subs | 300 | Si <100, revisar CTA y landing |
| Engagement consistente | >3% promedio | Si <2%, pivotar formato o tono |
| Verticalización | Decisión basada en datos | Analizar qué temas/formatos performan mejor |

### 90 días (sistema maduro)

| Métrica | Target | Decisión asociada |
|---------|--------|-------------------|
| Followers IG | 5,000 | Evaluar monetización |
| Newsletter subs | 800 | Evaluar sponsors |
| Revenue | Primer test | Sponsored post o newsletter ad |
| Podcast plays | 50+ | Evaluar si continuar o pivotar |

---

## Diferenciación vs competencia

### Competidores principales (en inglés)
- **The Rundown AI** — newsletter diaria, 500k+ subs, generalista, inglés
- **The Neuron** — newsletter + social, similar a Rundown, inglés
- **Superhuman AI** — newsletter, más técnico, inglés

### Nuestra diferenciación

| Factor | Competencia (EN) | AI Brief LATAM |
|--------|-------------------|----------------|
| Idioma | Inglés | Español neutro LATAM |
| Región | Global (US-centric) | Ángulo LATAM explícito |
| Formato | Newsletter-first | Social-first (IG/TikTok) + newsletter |
| Tono | Varía (algunos hype) | Anti-hype estricto, datos > opiniones |
| Frecuencia social | 1-2/día | 3/día |
| Visual | Templates estáticos | AI-generated (gpt-image-2) |
| Audio | Algunos | Voice clone personalizado |

### Competidores en español
- Pocos competidores directos en español con formato Smart Brevity + social-first
- Algunos newsletters en español existen pero sin presencia social fuerte
- Oportunidad clara en el gap idioma + formato + frecuencia

### Verticalización (decisión diferida a mes 2)
Opciones a evaluar basadas en datos de engagement de los primeros 60 días:
1. **AI para founders/startups LATAM** — funding, herramientas, casos de uso
2. **AI governance y regulación LATAM** — políticas públicas, compliance
3. **AI para middle-market** — adopción en empresas medianas de la región
4. **Mantenerse generalista** — si los datos muestran que la audiencia valora la amplitud

La decisión se tomará con datos, no con intuición. Métricas clave: engagement rate por tema, saves (indicador de valor percibido), DMs/comentarios pidiendo más de un tema específico.
