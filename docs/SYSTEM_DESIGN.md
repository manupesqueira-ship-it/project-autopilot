# System Design — AI Brief LATAM (v2, 2026-05-10)

## Resumen ejecutivo

AI Brief LATAM es un sistema multi-agente orquestado por n8n Cloud que produce y publica 3 piezas diarias de contenido sobre inteligencia artificial para profesionales en Latinoamérica. El sistema reemplaza el MVP anterior basado en Python CLI (9 agentes, 98 tests) con una arquitectura de 11 agentes conectados mediante workflows de n8n, utilizando Claude Opus 4 para decisiones editoriales, gpt-image-2 para generación visual, ElevenLabs para audio y Buffer/Beehiiv para distribución. En Fase 1, un humano aprueba cada pieza vía Telegram antes de publicación; después de 14 días sin errores, el sistema pasa a auto-publish con alertas solo para casos borderline.

## Diagrama del sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        n8n Cloud Orchestrator                          │
│                                                                        │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │    A1     │──▶│    A2     │──▶│    A3     │──▶│    A4     │           │
│  │  Source   │   │  Signal   │   │Editorial │   │  Fact-   │           │
│  │ Monitor  │   │  Scorer   │   │          │   │ Checker  │           │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘            │
│                                                      │                 │
│                                                      ▼                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │    A5     │◀──│          │   │    A7     │◀──│          │            │
│  │  Visual   │   │          │   │   Copy    │   │          │            │
│  │ Director │   │          │   │ Composer  │   │          │            │
│  └──────────┘   │          │   └──────────┘   │          │            │
│       │         │          │        │          │          │            │
│       ▼         │          │        ▼          │          │            │
│  ┌──────────┐   │          │   ┌──────────────────────────┐            │
│  │    A6     │   │          │   │         A8              │            │
│  │  Audio    │   │          │   │   Content Generator     │            │
│  │ Director │   │          │   │ ┌─────┬─────┬─────┬───┐ │            │
│  └──────────┘   │          │   │ │A8a  │A8b  │A8c  │A8d│ │            │
│       │         │          │   │ │Vis. │Vid. │Aud. │NL │ │            │
│       │         │          │   │ │gpt  │Seed.│11L  │Bee│ │            │
│       │         │          │   │ └─────┴─────┴─────┴───┘ │            │
│       │         │          │   └──────────────────────────┘            │
│       │         │          │               │                           │
│       └─────────┘          │               ▼                           │
│                            │        ┌──────────┐                       │
│                            │        │    A9     │                       │
│                            │        │Compliance│                       │
│                            │        └──────────┘                       │
│                            │               │                           │
│                            │     ┌─────────▼──────────┐                │
│                            │     │  TELEGRAM APPROVAL  │  ◀── Human    │
│                            │     │   (Fase 1: 14 días) │               │
│                            │     └─────────┬──────────┘                │
│                            │               │                           │
│                            │               ▼                           │
│                            │        ┌──────────┐                       │
│                            │        │   A10     │                       │
│                            │        │Publisher  │──▶ IG + TikTok       │
│                            │        │          │──▶ Newsletter          │
│                            │        └──────────┘                       │
│                            │               │                           │
│                            │               ▼                           │
│                            │        ┌──────────┐                       │
│                            │        │   A11     │                       │
│                            │        │Analytics │──▶ Weekly report       │
│                            │        └──────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘

Flujo de datos:
RSS/APIs ──▶ A1 ──▶ A2 ──▶ A3 ──▶ A4 ──▶ A5/A6/A7 ──▶ A8 ──▶ A9 ──▶ [Telegram] ──▶ A10 ──▶ A11
```

## Los 11 agentes

### A1 — Source Monitor

**Rol:** Monitorea fuentes RSS, APIs de noticias y feeds relevantes para detectar noticias nuevas sobre AI. Deduplica contra un historial de 7 días y aplica un filtro preliminar por keywords para descartar ruido antes de pasar señales al scorer.

- **Inputs:** RSS feeds, APIs de noticias (TechCrunch, The Verge, ArXiv, etc.)
- **Outputs:** Lista de señales candidatas con título, URL, resumen, timestamp, source
- **LLM:** Ninguno (determinístico)
- **Tools:** n8n RSS node, HTTP Request node, deduplication via n8n Function node

### A2 — Signal Scorer

**Rol:** Evalúa cada señal candidata usando una rúbrica de 8 categorías (Anexo B del sistema anterior) para asignar un score compuesto. Solo las señales que superan el umbral (>6.5/10) avanzan al pipeline editorial.

- **Inputs:** Lista de señales candidatas de A1
- **Outputs:** Señales rankeadas con score, categoría, justificación
- **LLM:** Claude Sonnet (costo-eficiente para scoring)
- **Tools:** n8n AI Agent node, Anthropic API

### A3 — Editorial

**Rol:** Toma las señales top-scored y genera un brief editorial en formato Smart Brevity con ángulo LATAM. Define el hook, el "why it matters", el dato clave y el contexto regional. Este brief es la base para todo el contenido downstream.

- **Inputs:** Señales top-scored de A2 con fuentes originales
- **Outputs:** Brief editorial estructurado (hook, body, LATAM angle, key data point)
- **LLM:** Claude Opus 4
- **Tools:** n8n AI Agent node, Anthropic API

### A4 — Fact-Checker

**Rol:** Verifica cada claim del brief editorial contra las fuentes originales. Busca inconsistencias, datos incorrectos o exageraciones. Asigna un veredicto (PASS/FLAG/REJECT) y notas de corrección si aplica.

- **Inputs:** Brief editorial de A3 + URLs de fuentes originales
- **Outputs:** Veredicto (PASS/FLAG/REJECT), claims verificados, correcciones sugeridas
- **LLM:** Claude Opus 4
- **Tools:** n8n AI Agent node, HTTP Request node (para re-verificar fuentes)

### A5 — Visual Director

**Rol:** Decide la dirección visual de la pieza: estilo del carousel, paleta de colores, layout de slides, elementos gráficos. Genera un visual brief que A8a usará para crear las imágenes.

- **Inputs:** Brief editorial verificado de A4
- **Outputs:** Visual brief (estilo, layout por slide, texto por slide, instrucciones para gpt-image-2)
- **LLM:** Claude Opus 4
- **Tools:** n8n AI Agent node

### A6 — Audio Director

**Rol:** Decide si la pieza necesita componente de audio/video (Fase 2+). Si aplica, escribe el guion para voiceover y las instrucciones de dirección para el reel. En Fase 1, este agente está inactivo.

- **Inputs:** Brief editorial verificado de A4
- **Outputs:** Decisión audio/video (sí/no), guion de voiceover, instrucciones de dirección
- **LLM:** Claude Opus 4
- **Tools:** n8n AI Agent node

### A7 — Copy Composer

**Rol:** Genera el caption para Instagram/TikTok, los hashtags optimizados, y el texto extendido para newsletter. Mantiene el tono Smart Brevity + Morning Brew casual en español neutro LATAM.

- **Inputs:** Brief editorial verificado de A4
- **Outputs:** Caption IG, hashtags (15-20), caption TikTok, texto newsletter extendido
- **LLM:** Claude Opus 4
- **Tools:** n8n AI Agent node

### A8 — Content Generator

Agente paraguas con 4 sub-agentes especializados en generación de assets:

#### A8a — Visual Generator

**Rol:** Genera carousel slides (1080x1080) usando gpt-image-2 siguiendo las instrucciones del Visual Director.

- **Inputs:** Visual brief de A5
- **Outputs:** 4-8 imágenes PNG 1080x1080 para carousel
- **LLM:** gpt-image-2 (OpenAI)
- **Tools:** n8n HTTP Request node (OpenAI Images API)

#### A8b — Video Generator

**Rol:** Genera reels cortos a partir de imágenes + guion usando Seedance 2.0. Activo desde Fase 2.

- **Inputs:** Imágenes de A8a + guion de A6
- **Outputs:** Video MP4 (9:16, 15-30s)
- **LLM:** Seedance 2.0
- **Tools:** n8n HTTP Request node (Seedance API)

#### A8c — Audio Generator

**Rol:** Genera voiceover usando voz clonada de Manuel via ElevenLabs. Activo desde Fase 2.

- **Inputs:** Guion de A6
- **Outputs:** Audio MP3 para reel o podcast
- **LLM:** ElevenLabs TTS
- **Tools:** n8n HTTP Request node (ElevenLabs API)

#### A8d — Newsletter Generator

**Rol:** Genera el brief extendido formateado para email via Beehiiv API. Activo desde Fase 3.

- **Inputs:** Texto newsletter de A7 + imágenes de A8a
- **Outputs:** Newsletter draft en Beehiiv
- **LLM:** Ninguno (templating)
- **Tools:** n8n HTTP Request node (Beehiiv API)

### A9 — Compliance

**Rol:** Revisa todo el contenido generado contra las reglas de Meta (IG/TikTok), lineamientos de brand voice, y patrones prohibidos (clickbait, claims sin fuente, lenguaje ofensivo). Asigna PASS/FLAG/REJECT.

- **Inputs:** Todo el output de A7 + A8 (caption, imágenes, video, audio)
- **Outputs:** Veredicto compliance (PASS/FLAG/REJECT), notas específicas
- **LLM:** Claude Opus 4
- **Tools:** n8n AI Agent node

### A10 — Publisher

**Rol:** Publica el contenido aprobado en los canales correspondientes. En Fase 1, solo publica carousels en IG y crosspost a TikTok via Buffer. En fases posteriores, agrega newsletter via Beehiiv y podcast via Spotify.

- **Inputs:** Contenido aprobado (post-compliance, post-Telegram approval)
- **Outputs:** Posts publicados, IDs de publicación, timestamps
- **LLM:** Ninguno (determinístico)
- **Tools:** n8n HTTP Request node (Buffer API, Beehiiv API)

### A11 — Analytics

**Rol:** Recolecta métricas de engagement de IG/TikTok, suscriptores de newsletter, y costos de API. Genera reportes semanales y alertas si métricas caen bajo umbrales.

- **Inputs:** IDs de publicación de A10, APIs de plataformas
- **Outputs:** Reporte semanal (engagement, followers, costs), alertas
- **LLM:** Ninguno (determinístico)
- **Tools:** n8n HTTP Request node (IG Graph API, Buffer API, Beehiiv API)

## Human-in-the-loop

### Fase 1 (primeros 14 días): Aprobación obligatoria

El sistema se detiene después de A9 (Compliance) y envía un resumen al bot de Telegram con:

- Preview del carousel (imágenes)
- Caption propuesto
- Score de la señal original
- Veredicto de fact-check y compliance
- Botones: APROBAR / EDITAR / RECHAZAR

El humano (Manuel) revisa y aprueba antes de que A10 publique. Esto permite:
1. Calibrar la calidad del output
2. Detectar errores que los agentes no captaron
3. Construir confianza en el sistema antes de automatizar

### Post Fase 1 (día 15+): Auto-publish con alertas

Si el sistema acumula 14 días sin errores de fact-check ni rechazos de compliance:
- Contenido con score >8 y compliance PASS se auto-publica
- Contenido con score 6.5-8 o compliance FLAG se envía a Telegram para revisión
- Contenido con compliance REJECT se descarta automáticamente

## Estado del proyecto

### Implementado
- Prompts extraídos del MVP Python y documentados en `/prompts/`
- Brand voice, rúbricas de scoring y lógica editorial preservados
- Documentación de arquitectura (este documento)
- Cuentas creadas: @breiflatam (IG), @ai.brief.latam (TikTok), aibrieflatam@gmail.com

### Pendiente (próximo)
- Configurar n8n Cloud o self-hosted en Hostinger
- Construir workflow de A1 (RSS + deduplicación)
- Implementar A2 (Signal Scorer) con Claude Sonnet
- Implementar A3-A4 (Editorial + Fact-Check) con Claude Opus 4
- Implementar A7 + A8a (Copy + Visual) para Fase 1
- Implementar A9 (Compliance) con Claude Opus 4
- Configurar Telegram Bot para aprobación
- Conectar Buffer para publicación
- Primer carousel de prueba end-to-end

## Cambios respecto al sistema anterior

### Descartado
- **Python custom CLI** (`autopilot.py`, `main.py`): Reemplazado por n8n workflows. La orquestación ya no vive en código Python sino en nodos visuales de n8n.
- **Pillow/PIL para visuals**: Las imágenes generadas con Python + Pillow se reemplazan por gpt-image-2, que produce calidad significativamente superior sin código de renderizado.
- **98 tests unitarios**: No aplican al nuevo sistema. La validación se hace via monitoring en n8n y métricas de A11.
- **9 agentes monolíticos**: Reestructurados en 11 agentes con responsabilidades más granulares (separación Visual/Audio Director, sub-agentes en A8).
- **Ejecución local**: El sistema anterior corría en la máquina local. El nuevo corre en n8n Cloud.

### Rescatado
- **Prompts editoriales**: Los prompts de Smart Brevity, fact-checking y compliance se extrajeron y adaptaron para el nuevo sistema.
- **Brand voice guidelines**: Tono, vocabulario, patrones prohibidos se mantienen intactos.
- **Rúbrica de scoring (Anexo B)**: Las 8 categorías de evaluación de señales se preservan en A2.
- **Lógica de scoring**: Los umbrales y pesos del Signal Scorer se mantienen.
- **Research de audiencia y competencia**: Todo el análisis de mercado LATAM se preserva.
- **Formato Smart Brevity**: La estructura hook → why it matters → dato clave → contexto se mantiene.

### Código legacy
El MVP Python completo se preserva en `legacy/python-mvp-2026-05-10/` como referencia para los prompts y la lógica de negocio.
