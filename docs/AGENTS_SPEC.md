# Agents Spec — AI Brief LATAM (v2, 2026-05-10)

Especificación técnica de los 11 agentes del sistema multi-agente orquestado por n8n.

---

## A1 — Source Monitor

**Function:** Monitorea continuamente fuentes RSS, APIs de noticias tech y feeds especializados en AI para detectar noticias nuevas. Deduplica contra un historial de 7 días almacenado en n8n (o base de datos simple) usando hash de título + URL. Aplica un filtro preliminar por keywords relevantes (AI, LLM, machine learning, automation, robotics, etc.) para descartar ruido antes de pasar señales al scorer. Ejecuta cada 2 horas en horario activo.

- **Inputs:** RSS feeds (TechCrunch, The Verge, Ars Technica, MIT Tech Review, ArXiv, VentureBeat, etc.), APIs de noticias
- **Outputs:** Lista JSON de señales candidatas: `{ title, url, summary, source, timestamp, keywords[], raw_content }`
- **LLM:** Ninguno (procesamiento determinístico)
- **Tools:** n8n RSS Read node, n8n HTTP Request node, n8n Function node (deduplicación + keyword filter), n8n Google Sheets / SQLite (historial de deduplicación)
- **Prompt:** `/prompts/a1-source-monitor.md` (configuración de feeds y keywords)

---

## A2 — Signal Scorer

**Function:** Evalúa cada señal candidata usando la rúbrica de 8 categorías heredada del Anexo B del sistema anterior. Las categorías incluyen: novedad, impacto en LATAM, relevancia para audiencia target, calidad de fuente, potencial viral, profundidad técnica, implicaciones de negocio, y timing. Asigna un score compuesto de 0-10. Solo señales con score >6.5 avanzan al pipeline editorial. El agente procesa en batch las señales de cada ciclo de A1.

- **Inputs:** Lista de señales candidatas de A1 (JSON array)
- **Outputs:** Señales rankeadas: `{ ...signal, score, category, justification, latam_relevance_note }`
- **LLM:** Claude Sonnet (costo-eficiente para evaluación batch; Opus sería excesivo para scoring)
- **Tools:** n8n AI Agent node, Anthropic API (Claude Sonnet), n8n Function node (filtering por umbral)
- **Prompt:** `/prompts/a2-signal-scorer.md` (rúbrica completa de 8 categorías + ejemplos calibrados)

---

## A3 — Editorial

**Function:** Toma las señales top-scored y genera un brief editorial estructurado en formato Smart Brevity. Cada brief incluye: hook (1 línea impactante), "why it matters" (contexto para profesional LATAM), dato clave (número o hecho verificable), y ángulo regional (implicaciones específicas para Latinoamérica). El brief es la pieza central que alimenta a todos los agentes downstream (visual, copy, audio, newsletter).

- **Inputs:** Top 3-5 señales scored de A2, con URLs de fuentes originales
- **Outputs:** Brief editorial: `{ hook, why_it_matters, key_data_point, latam_angle, sources[], tone_notes }`
- **LLM:** Claude Opus 4 (calidad editorial máxima, tono preciso)
- **Tools:** n8n AI Agent node, Anthropic API (Claude Opus 4)
- **Prompt:** `/prompts/a3-editorial.md` (Smart Brevity format + brand voice + LATAM angle guidelines)

---

## A4 — Fact-Checker

**Function:** Verifica cada claim del brief editorial contra las fuentes originales citadas. Accede a las URLs para confirmar que los datos, cifras, atribuciones y contextos son correctos. Identifica exageraciones, datos desactualizados o claims sin soporte. Asigna un veredicto por claim y un veredicto global: PASS (todo verificado), FLAG (minor issues corregibles), REJECT (error material que requiere re-editorial). Si FLAG, sugiere correcciones específicas.

- **Inputs:** Brief editorial de A3 + lista de URLs de fuentes originales
- **Outputs:** `{ verdict: PASS|FLAG|REJECT, claims_verified: [{claim, source, status, correction?}], notes }`
- **LLM:** Claude Opus 4 (razonamiento profundo para verificación)
- **Tools:** n8n AI Agent node, Anthropic API (Claude Opus 4), n8n HTTP Request node (acceso a fuentes para re-verificación)
- **Prompt:** `/prompts/a4-fact-checker.md` (protocolo de verificación + estándares de evidencia)

---

## A5 — Visual Director

**Function:** Decide la dirección visual completa de cada pieza de contenido. Define el estilo del carousel (tech-minimal, data-viz, editorial-magazine, breaking-news), la paleta de colores para cada slide, el layout (texto-sobre-fondo, split-screen, infográfico), los elementos gráficos complementarios, y el texto exacto que aparecerá en cada slide. Genera un visual brief detallado que A8a usará como instrucción para gpt-image-2. En Fase 1, la dirección visual se simplifica y se integra parcialmente en A8a.

- **Inputs:** Brief editorial verificado de A4 (post fact-check PASS)
- **Outputs:** Visual brief: `{ style, color_palette, slides: [{ layout, text, visual_elements, gpt_image_prompt }] }`
- **LLM:** Claude Opus 4
- **Tools:** n8n AI Agent node, Anthropic API (Claude Opus 4)
- **Prompt:** `/prompts/a5-visual-director.md` (brand visual guidelines + carousel templates + gpt-image-2 prompt engineering)

---

## A6 — Audio Director

**Function:** Evalúa si la pieza de contenido se beneficiaría de un componente de audio/video (reel con voiceover) o si es mejor como carousel estático. Si decide que sí, escribe el guion de voiceover optimizado para la voz clonada de Manuel, con marcas de timing, énfasis y pausas. También define las instrucciones de dirección para el reel (transiciones, pacing, call-to-action). Inactivo en Fase 1.

- **Inputs:** Brief editorial verificado de A4
- **Outputs:** `{ needs_audio: bool, needs_video: bool, voiceover_script, direction_notes, estimated_duration }`
- **LLM:** Claude Opus 4
- **Tools:** n8n AI Agent node, Anthropic API (Claude Opus 4)
- **Prompt:** `/prompts/a6-audio-director.md` (guion guidelines + voice clone constraints + reel best practices)

---

## A7 — Copy Composer

**Function:** Genera todo el texto que acompaña al contenido visual/audiovisual. Produce el caption de Instagram (optimizado para engagement, con hook en primera línea pre-fold), 15-20 hashtags rankeados por relevancia, caption adaptado para TikTok, y el texto extendido para newsletter. Mantiene consistencia de tono Smart Brevity + Morning Brew casual en español neutro LATAM. Evita patrones prohibidos (clickbait, hype sin datos, anglicismos innecesarios).

- **Inputs:** Brief editorial verificado de A4
- **Outputs:** `{ caption_ig, hashtags[], caption_tiktok, newsletter_text, cta }`
- **LLM:** Claude Opus 4
- **Tools:** n8n AI Agent node, Anthropic API (Claude Opus 4)
- **Prompt:** `/prompts/a7-copy-composer.md` (copy guidelines + hashtag strategy + brand voice rules + forbidden patterns)

---

## A8 — Content Generator

Agente paraguas que coordina 4 sub-agentes especializados en generación de assets multimedia. En Fase 1, solo A8a está activo.

### A8a — Visual Generator

**Function:** Genera las imágenes del carousel usando gpt-image-2 de OpenAI. Cada carousel tiene 4-8 slides de 1080x1080px. Sigue las instrucciones del visual brief de A5 (o instrucciones simplificadas en Fase 1). Aplica el branding consistente de AI Brief LATAM (logo watermark, tipografía, paleta). Valida que las imágenes generadas cumplan con las especificaciones antes de pasar a compliance.

- **Inputs:** Visual brief de A5 (o brief editorial de A4 en Fase 1 simplificada)
- **Outputs:** Array de imágenes PNG 1080x1080, metadata: `{ slides: [{ image_url, alt_text, slide_number }] }`
- **LLM:** gpt-image-2 (OpenAI Images API)
- **Tools:** n8n HTTP Request node (OpenAI API endpoint `/v1/images/generations`), n8n Function node (validación de dimensiones)
- **Prompt:** `/prompts/a8a-visual-generator.md` (gpt-image-2 prompt templates + brand visual constraints)

### A8b — Video Generator

**Function:** Genera reels cortos (15-30 segundos, formato 9:16) a partir de imágenes del carousel + guion de voiceover usando Seedance 2.0. Aplica transiciones, timing sincronizado con audio, y call-to-action final. Activo desde Fase 2.

- **Inputs:** Imágenes de A8a + guion de A6 + audio de A8c
- **Outputs:** Video MP4 (9:16, 1080x1920, 15-30s): `{ video_url, duration, format }`
- **LLM:** Seedance 2.0
- **Tools:** n8n HTTP Request node (Seedance API)
- **Prompt:** `/prompts/a8b-video-generator.md` (video generation parameters + transition styles)

### A8c — Audio Generator

**Function:** Genera voiceover usando la voz clonada de Manuel via ElevenLabs API. En Fase 2, produce audio para reels (15-30s). En Fase 4, produce episodios completos de podcast (5-10 min). Aplica las marcas de timing y énfasis del guion de A6.

- **Inputs:** Guion de voiceover de A6 (con marcas de timing)
- **Outputs:** Audio MP3: `{ audio_url, duration, format, voice_id }`
- **LLM:** ElevenLabs TTS (voice clone)
- **Tools:** n8n HTTP Request node (ElevenLabs API `/v1/text-to-speech`), n8n Function node (validación de duración)
- **Prompt:** `/prompts/a8c-audio-generator.md` (voice settings + SSML markup guidelines)

### A8d — Newsletter Generator

**Function:** Genera el brief extendido formateado para distribución por email via Beehiiv. Toma las 3 noticias del día, el texto extendido de A7, y las imágenes clave de A8a para componer una newsletter cohesiva con secciones claras, CTAs, y branding consistente. Activo desde Fase 3.

- **Inputs:** Texto newsletter de A7 + imágenes seleccionadas de A8a + metadata del día
- **Outputs:** Newsletter draft en Beehiiv: `{ draft_id, subject_line, preview_text, html_content }`
- **LLM:** Ninguno (templating determinístico con datos de upstream agents)
- **Tools:** n8n HTTP Request node (Beehiiv API), n8n Function node (template rendering)
- **Prompt:** `/prompts/a8d-newsletter-generator.md` (email template + Beehiiv API reference)

---

## A9 — Compliance

**Function:** Revisa todo el contenido generado (captions, imágenes, video, audio) contra tres conjuntos de reglas: (1) Políticas de Meta/TikTok (contenido prohibido, límites de texto en imágenes, música con copyright, etc.), (2) lineamientos de brand voice de AI Brief LATAM (tono, vocabulario, patrones prohibidos), y (3) estándares de calidad internos (no clickbait, no claims sin fuente, no lenguaje ofensivo, no sesgos). Asigna veredicto PASS/FLAG/REJECT con notas específicas por issue encontrado.

- **Inputs:** Todo el output de A7 (captions, hashtags) + A8 (imágenes, video, audio)
- **Outputs:** `{ verdict: PASS|FLAG|REJECT, issues: [{ type, severity, description, suggestion }], confidence_score }`
- **LLM:** Claude Opus 4 (juicio editorial + conocimiento de políticas de plataformas)
- **Tools:** n8n AI Agent node, Anthropic API (Claude Opus 4)
- **Prompt:** `/prompts/a9-compliance.md` (Meta policies checklist + brand voice rules + forbidden patterns + quality standards)

---

## A10 — Publisher

**Function:** Publica el contenido aprobado (post-compliance, post-Telegram approval en Fase 1) en los canales correspondientes. En Fase 1, publica carousels en Instagram y crosspost a TikTok via Buffer API, respetando los horarios programados (8 AM, 1 PM, 7 PM CDMX). En fases posteriores, agrega publicación de newsletter via Beehiiv y podcast via Spotify. Registra IDs de publicación y timestamps para tracking de A11.

- **Inputs:** Contenido aprobado (imágenes, caption, hashtags) + horario de publicación
- **Outputs:** `{ post_id, platform, published_at, url }`
- **LLM:** Ninguno (determinístico)
- **Tools:** n8n HTTP Request node (Buffer API `/v1/updates`), n8n HTTP Request node (Beehiiv API, Fase 3), n8n Schedule Trigger node
- **Prompt:** `/prompts/a10-publisher.md` (publicación workflow + scheduling rules + error handling)

---

## A11 — Analytics

**Function:** Recolecta métricas de engagement de todas las plataformas (IG via Graph API, TikTok via Buffer, newsletter via Beehiiv), costos de API (Anthropic, OpenAI, ElevenLabs), y estadísticas de pipeline (señales procesadas, tasa de aprobación, errores). Genera reportes semanales automáticos enviados via Telegram. Alerta si métricas caen bajo umbrales definidos (engagement <2%, costos >$200/mo, fact-check error detectado).

- **Inputs:** Post IDs de A10, APIs de plataformas, logs de costos de n8n
- **Outputs:** `{ weekly_report: { followers, engagement_rate, top_posts[], costs_breakdown, pipeline_stats }, alerts[] }`
- **LLM:** Ninguno (determinístico, cálculos y agregación)
- **Tools:** n8n HTTP Request node (Instagram Graph API, Buffer API, Beehiiv API), n8n Function node (cálculos), n8n Telegram node (envío de reportes)
- **Prompt:** `/prompts/a11-analytics.md` (métricas definitions + alert thresholds + report template)

---

## Mapa de dependencias

```
A1 ──▶ A2 ──▶ A3 ──▶ A4 ──┬──▶ A5 ──▶ A8a ──┐
                           ├──▶ A6 ──▶ A8b ──┤
                           │         └──▶ A8c ──┤
                           ├──▶ A7 ──▶ A8d ──┤
                           │                  │
                           │                  ▼
                           │                 A9 ──▶ [Telegram] ──▶ A10 ──▶ A11
```

## Resumen de LLMs por agente

| Agente | LLM | Justificación |
|--------|-----|---------------|
| A1 Source Monitor | Ninguno | Determinístico (RSS + dedup) |
| A2 Signal Scorer | Claude Sonnet | Costo-eficiente para scoring batch |
| A3 Editorial | Claude Opus 4 | Calidad editorial máxima |
| A4 Fact-Checker | Claude Opus 4 | Razonamiento profundo para verificación |
| A5 Visual Director | Claude Opus 4 | Dirección creativa requiere juicio |
| A6 Audio Director | Claude Opus 4 | Dirección creativa requiere juicio |
| A7 Copy Composer | Claude Opus 4 | Brand voice preciso |
| A8a Visual Generator | gpt-image-2 | Generación de imágenes |
| A8b Video Generator | Seedance 2.0 | Generación de video |
| A8c Audio Generator | ElevenLabs TTS | Generación de audio |
| A8d Newsletter Generator | Ninguno | Templating determinístico |
| A9 Compliance | Claude Opus 4 | Juicio editorial + políticas |
| A10 Publisher | Ninguno | Determinístico (API calls) |
| A11 Analytics | Ninguno | Determinístico (cálculos) |
