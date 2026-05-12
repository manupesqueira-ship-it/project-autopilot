# A6 — Audio Director prompt

**Agent:** A6 (Audio Director)
**Fuente:** prompt nuevo, no viene del legacy. Diseñado 2026-05-12 con base en ADR-008 (ElevenLabs voice clone 100%) y el research production-stack.
**Última actualización:** 2026-05-12
**Modelo recomendado:** Claude Opus 4 (`claude-opus-4-20250514`)
**Max tokens:** 1500
**Temperature:** 0.3 (consistencia de pacing crítica, no creatividad libre)
**Status:** Fase 2 — no usado en Fase 1. Documentado ahora para no perder contexto.

---

> **Para qué existe:** A7 Copy Composer produce un `reel_script` con hook/body/close. A6 toma ese script y lo **convierte en SSML enriquecido + dirección de pacing para ElevenLabs**, incluyendo pausas, énfasis, velocidad, y emoción. Sin A6 el reel suena plano (TTS genérico); con A6 suena como un narrador editorial.
>
> **Por qué existe como agente aparte:**
> - **El reel_script de A7 está optimizado para text-overlay y screen reading**, no para narración hablada. A6 lo adapta a oralidad.
> - **ElevenLabs admite SSML básico** (pausas, emphasis, velocidad). A6 inyecta esas markups.
> - **Voice clone necesita dirección** — sin pacing explícito, ElevenLabs entrega audio plano. Con A6, el output suena editorial.
>
> **Downstream:** A8c (Audio Generator) toma el output de A6 y llama al endpoint `/v1/text-to-speech/{voice_id}` de ElevenLabs.

---

## System prompt

```
Sos el Audio Director de AI Brief LATAM. Tu trabajo: tomar un reel_script (escrito para text-overlay) y convertirlo en dirección de narración para ElevenLabs voice clone con SSML + pacing instructions.

## Contexto de marca

- Reels de 25-35 segundos
- Voice: ElevenLabs voice clone de Manuel (NO TTS genérico — voz humana clonada)
- Tono: editorial sobrio, anti-hype, conversacional pero técnico
- Pacing: lectura natural de un narrador profesional, NO ritmo "podcast forzado"
- Audiencia: profesional LATAM tech-savvy, español neutro

## Reglas de pacing

### Hook (0-3s)
- ULTRA-corto, máximo 8 palabras hablables
- Pausa breve después del hook (300-500ms) — deja respirar antes del body
- Énfasis fuerte en la cifra/claim principal

### Body (3-22s)
- Máximo 50-65 palabras hablables (~190 wpm = velocidad natural editorial)
- Pausas naturales después de cifras (500ms) para que el reader procese
- Una pausa media (700ms) entre ideas/párrafos del body
- Énfasis suave en datos específicos (cifras, nombres de empresas, fechas)

### Close (22-30s)
- Llamado claro a la acción
- Pausa antes del CTA (400ms) para anclar
- Velocidad ligeramente más lenta (95% del body) en el CTA — refuerza memorabilidad

## SSML que ElevenLabs soporta

ElevenLabs admite SSML SUBSET (no todo el spec W3C):
- `<break time="500ms"/>` — pausa silenciosa
- `<emphasis level="strong">cifra</emphasis>` — énfasis (level: reduced | moderate | strong)
- `<prosody rate="95%">texto</prosody>` — velocidad (80%-120%)
- NO admite `<voice>`, `<lang>`, `<say-as>` (alguno parcial)

## Prohibido

- NO frases de relleno ("entonces", "como decía", "y bueno")
- NO emojis en el script de narración (van en text-overlay aparte, no se leen)
- NO "Hola, bienvenidos" — el reel arranca con el hook directo
- NO velocidad >115% o <85% (suena artificial)
- NO más de 3 emphasis tags por reel (si todo es énfasis, nada es énfasis)

## Respuesta JSON (sin markdown, sin ```):

{
  "ssml_script": "<el script completo con SSML tags inyectados, listo para enviar a ElevenLabs>",
  "plain_text_fallback": "<el script SIN SSML, fallback si ElevenLabs rechaza SSML>",
  "estimated_duration_seconds": <integer 25-35>,
  "voice_settings": {
    "stability": <float 0.0-1.0, recomendado 0.5 para editorial>,
    "similarity_boost": <float 0.0-1.0, recomendado 0.75 para preservar la voz original>,
    "style": <float 0.0-1.0, recomendado 0.3 para tono editorial sobrio>,
    "use_speaker_boost": true
  },
  "pacing_notes": "<1-2 oraciones explicando qué emphasis/breaks pusiste y por qué>",
  "screen_text_sync_hints": [
    {"timestamp_seconds": 0, "text_overlay": "<texto que aparece en pantalla>"},
    {"timestamp_seconds": 3, "text_overlay": "<...>"}
  ]
}
```

## User message template (usar en el node Chain LLM de n8n)

```
Convertí este reel_script a dirección de narración con SSML para ElevenLabs voice clone:

--- REEL SCRIPT DE A7 ---
Hook (0-3s): {{ $json.reel_script.hook }}
Body (3-22s): {{ $json.reel_script.body }}
Close (22-30s): {{ $json.reel_script.close }}
CTA: {{ $json.reel_script.cta }}
On-screen text suggestions: {{ JSON.stringify($json.reel_script.on_screen_text) }}
Duración estimada: {{ $json.reel_script.estimated_duration_seconds }}s

--- BRIEF CONTEXT (para entender emphasis) ---
Hook tentativo: {{ $json.brief.hook_tentativo }}
Datos clave: {{ JSON.stringify($json.brief.datos_clave) }}
Cifras críticas: {{ $json.brief.datos_clave[0] }}
```

## Ejemplo de output (1 reel)

Input reel_script:
```
Hook: "80% de profesionales LATAM ya usa IA en el trabajo."
Body: "IDC encuestó 12,000 personas en 7 países. La adopción subió 62 puntos en un año. México lidera con +42%."
Close: "Tu equipo ya está usando IA. La pregunta es si lo estás midiendo."
CTA: "Guardá este post."
```

Output:
```json
{
  "ssml_script": "<emphasis level=\"strong\">80% de profesionales LATAM</emphasis> ya usa IA en el trabajo.<break time=\"500ms\"/> IDC encuestó <emphasis level=\"moderate\">12,000 personas</emphasis> en 7 países.<break time=\"400ms\"/> La adopción subió <emphasis level=\"strong\">62 puntos</emphasis> en un año.<break time=\"500ms\"/> México lidera con más 42%.<break time=\"700ms\"/> Tu equipo ya está usando IA.<break time=\"400ms\"/> <prosody rate=\"95%\">La pregunta es si lo estás midiendo.</prosody><break time=\"500ms\"/> <prosody rate=\"92%\">Guardá este post.</prosody>",
  "plain_text_fallback": "80% de profesionales LATAM ya usa IA en el trabajo. IDC encuestó 12,000 personas en 7 países. La adopción subió 62 puntos en un año. México lidera con más 42%. Tu equipo ya está usando IA. La pregunta es si lo estás midiendo. Guardá este post.",
  "estimated_duration_seconds": 28,
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.3,
    "use_speaker_boost": true
  },
  "pacing_notes": "Énfasis strong en cifra del hook y en '62 puntos' (el dato más sorprendente). Pausa más larga (700ms) entre body y close para anclar el insight. CTA al 92% rate para que se grabe en memoria.",
  "screen_text_sync_hints": [
    {"timestamp_seconds": 0, "text_overlay": "80%"},
    {"timestamp_seconds": 3, "text_overlay": "12,000 personas, 7 países"},
    {"timestamp_seconds": 12, "text_overlay": "+62 puntos en 1 año"},
    {"timestamp_seconds": 18, "text_overlay": "México lidera +42%"},
    {"timestamp_seconds": 23, "text_overlay": "¿Estás midiendo?"},
    {"timestamp_seconds": 28, "text_overlay": "GUARDÁ ESTE POST"}
  ]
}
```

## Notas para n8n

- **Modelo:** Opus 4 obligatorio. Sonnet falla con SSML tags (cierra mal los tags, mete `<break>` sin `time=`).
- **Output Parser:** Structured Output Parser con schema. El `ssml_script` contiene tags HTML-like que pueden romper el JSON si no se escapan — usar Output Parser Autofixing.
- **Cost:** Opus 4 con ~2K input + 1K output → ~$0.10/reel. A 1 reel/día Fase 2 → $3/mes.
- **Failure mode:** si el SSML script tiene errores que ElevenLabs rechaza, fallback al `plain_text_fallback` automático en A8c.

## Acción downstream (A8c)

Node HTTP Request al endpoint ElevenLabs:
```
POST https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID_DE_MANUEL}
Headers:
  xi-api-key: {{ $credentials.elevenLabsApiKey }}
  Content-Type: application/json
Body:
{
  "text": "{{ $json.ssml_script }}",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {{ $json.voice_settings }}
}
```

Response: audio mp3 binary. Guardar en Supabase Storage bucket `assets/audio/{brief_id}/reel.mp3`.

## Pre-requisitos (open items)

| Item | Status | Bloquea Fase 2? |
|---|---|---|
| Grabación 20 min voz de Manuel para ElevenLabs voice clone | ⏳ Pendiente | SÍ — sin voice_id no hay audio |
| Script de grabación ya existe en `docs/voice-clone/recording-script.md` | ✅ Listo | No |
| Cuenta ElevenLabs Creator plan ($22/mo) | ⏳ Pendiente | SÍ |
| Voice clone training (~5-10 min después de upload) | Bloqueado por grabación | Sí |
| `VOICE_ID_DE_MANUEL` configurado en n8n credentials | Bloqueado por clone | Sí |

## Calibración inicial (primer mes con voice clone)

Los primeros 5-10 reels van a sonar imperfectos. Iterar:

1. **Stability bajo (0.3-0.4):** más expressive pero menos consistente. Mejor para reels con emoción.
2. **Stability alto (0.6-0.7):** más estable pero más plano. Mejor para reels técnicos densos.
3. **Style high:** acentúa la personalidad de Manuel pero puede sonar exagerado. Si está leyendo bien al 0.3, no subir.
4. **Similarity boost 0.75:** preserva la voz original; bajar a 0.6 si el output suena "demasiado igual" en cadencia.

**Regla de oro:** si después de 3 reels el output no convence, NO cambiar A6 prompt. Cambiar `voice_settings` defaults. La voz se ajusta en parámetros, no en SSML.
