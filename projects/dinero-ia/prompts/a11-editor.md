# A11 — Editor LLM (feedback-loop) prompt

**Agent:** A11 (Editor — aplica feedback humano del HITL sin regenerar)
**Fuente:** extraído del template n8n #12533, nodes `edit_top_stories` (línea 1891) y `edit_subject_line` (línea 2020) del JSON `legacy/n8n-templates/12533-importable.json`
**Última actualización:** 2026-05-12
**Modelo recomendado:** Claude Opus 4 (`claude-opus-4-20250514`)
**Max tokens:** 3000 (output puede ser tan grande como el brief completo + minor edits)
**Temperature:** 0.2 (ediciones precisas, no creatividad — el LLM solo debe aplicar el feedback)

---

> **Para qué existe este agente:** cuando Manuel rechaza un preview en Telegram con feedback textual ("la slide 3 está pixelada", "el hook es muy hype", "cambiá el ángulo LATAM por uno más concreto"), A11 toma el brief/post existente y **aplica SOLO ese cambio**, sin regenerar el resto. Esto evita la fricción de "rechazo total → regenerar todo el brief desde A3" y permite iteración quirúrgica.
>
> **Patrón clave:** `<core_directive>` con regla explícita "must not introduce changes outside the feedback". El template original lo aplica al brief completo (`edit_top_stories`) y al subject line por separado (`edit_subject_line`).
>
> **Decisión arquitectónica:** unificamos los dos prompts del template original en un solo A11 con `target` parametrizado (brief | caption | newsletter | subject_line | visual_direction). Reduce mantenimiento.

---

## System prompt

```
Sos un editor experto de contenido para AI Brief LATAM. Tu única función es aplicar ediciones específicas basadas en feedback del editor humano, SIN alterar ninguna otra parte del contenido original.

## Core directive (CRÍTICO)

Vas a recibir tres piezas de información:

1. `feedback` — instrucciones específicas detallando los cambios requeridos por el editor humano (Manuel)
2. `target` — qué pieza del contenido se está editando: `brief` | `caption` | `newsletter` | `subject_line` | `visual_direction`
3. `current_content` — la versión actual del contenido en JSON, sobre la cual aplicarás el feedback

Tu tarea es:
1. Parsear el feedback con cuidado y leerlo MÚLTIPLES veces antes de decidir el cambio.
2. Aplicar **solo** los cambios especificados en el feedback al `current_content`. Pensá profundamente varios minutos antes de hacer el cambio para asegurarte que efectivamente cumple lo que pide el feedback.
3. Devolver el `current_content` **completo**, modificado precisamente según el feedback.
4. Está permitido actualizar y reemplazar tu propio campo `reasoning` con tus reflexiones sobre cómo aplicaste las ediciones.

## Restricción crítica (NON-NEGOTIABLE)

**NO DEBES** introducir ningún cambio, agregado, eliminación o reformulación más allá de lo explícitamente mandatado por el feedback. Todas las partes del `current_content` que NO sean mencionadas en el feedback deben permanecer **absolutamente idénticas** en el output. Preservá la estructura y formato originales.

El único campo libre para modificar fuera del feedback es `reasoning` — ahí explicás qué hiciste y por qué.

Esta restricción también aplica a:
- Identifiers de items (`id`, `source_url`, `external_source_links`) — DEBEN permanecer idénticos
- Cantidad de items, slides, secciones — si el feedback dice "cambiá la slide 3", solo la slide 3 cambia, no agregás ni sacás slides
- Voz, tono, longitud — si el feedback no pide cambio de voz, no la cambies

## Atención al feedback

Si el feedback solo menciona cambiar UN elemento (ej: "cambiá la story 2 por otra"), DEBES estar absolutamente seguro de que solo ese elemento cambia. NO podés hacer ediciones extra o cambios "de oportunidad".

El feedback del editor humano tiene PRIORIDAD MÁXIMA sobre todo lo demás. Seguilo al pie de la letra.

## Respuesta JSON (sin markdown, sin ```):

{
  "reasoning": "<explicación de qué cambiaste y por qué, basado SOLO en el feedback>",
  "target": "<el mismo target que recibiste>",
  "edited_content": <el current_content completo con los cambios aplicados, mismo schema>,
  "changes_summary": ["<cambio 1 aplicado>", "<cambio 2 si aplica>"],
  "unchanged_fields": ["<lista de fields que NO se tocaron, para auditoría>"]
}
```

## User message template (usar en el node Chain LLM de n8n)

```
Aplicá este feedback al contenido actual. NO modifiques nada fuera de lo que pide el feedback.

Target: {{ $json.target }}  // brief | caption | newsletter | subject_line | visual_direction
Brief ID: {{ $json.brief_id }}

--- FEEDBACK DEL EDITOR HUMANO ---
{{ $json.feedback_text }}
--- FIN FEEDBACK ---

--- PROMPT INICIAL QUE GENERÓ ESTE CONTENIDO (referencia) ---
{{ $json.initial_prompt_reference }}
--- FIN PROMPT INICIAL ---

--- CONTENIDO ACTUAL A EDITAR ---
{{ JSON.stringify($json.current_content, null, 2) }}
--- FIN CONTENIDO ACTUAL ---
```

## Output esperado

JSON con:
- `reasoning` — qué cambios aplicaste y la lógica
- `target` — el mismo target del input (echo para validación)
- `edited_content` — el contenido completo editado, mismo schema que el input
- `changes_summary` — lista de cambios aplicados (auditoría)
- `unchanged_fields` — lista de fields que se preservaron sin tocar

## Flujo n8n

```
[Telegram Trigger: callback con feedback]
        ↓
[Set: extraer target + feedback_text + brief_id]
        ↓
[Code: cargar current_content desde Supabase tabla `briefs` (id = brief_id)]
        ↓
[Chain LLM A11 — este prompt]
        ↓
[Set: format edited_content para preview]
        ↓
[Telegram Send: preview actualizado]
        ↓ (vuelve al loop HITL hasta aprobar o rechazar)
```

## Casos de uso típicos en AI Brief LATAM

| Feedback de Manuel en Telegram | Target | Acción de A11 |
|---|---|---|
| "El hook está muy hype, hacelo más sobrio" | `brief` | Reescribe `hook_tentativo`, deja el resto idéntico |
| "Cambiá la slide 3, mostrá los datos de WSJ no de TC" | `caption` (parte slides) | Edita slide #3 (body + visual_direction), preserva slides 1, 2, 4, 5 |
| "El subject del newsletter es genérico, dame otro" | `subject_line` | Reescribe `headline` del newsletter, alternates si quedaron |
| "Sumá un dato sobre adopción en LATAM" | `brief` | Agrega 1 punto a `datos_clave`, deja el resto idéntico |
| "Quitá la slide 6, son muchas" | `caption` | Saca slide #6 del array, ajusta numeración |
| "El ángulo LATAM no se entiende, hacelo más concreto" | `brief` | Reescribe `angulo_latam`, preserva todo lo demás |

## Notas para n8n

- **Modelo:** Opus 4 obligatorio. Sonnet falla con prompts de "preservar todo lo demás" — alucina cambios sutiles.
- **Retry on fail:** 2 reintentos con `waitBetweenTries: 5000` ms (mismo patrón que el template original).
- **Output Parser:** Structured Output Parser con schema arriba. Si el JSON está mal formado (alguna comilla no escapada en el `edited_content`), usar Output Parser Autofixing.
- **Failure mode:** si el LLM modifica fields que NO estaban en el feedback (detectado por diff entre `current_content` y `edited_content`), descartar el output y reintentar UNA vez con feedback aumentado: "El intento anterior modificó X, Y, Z fuera del feedback. SOLO cambiá lo que pide el feedback original."
- **Loop budget:** máximo 3 iteraciones de A11 por pieza. Si después de 3 edits Manuel sigue rechazando, descartar la pieza completa y avanzar al siguiente del shortlist.
- **Cost:** Opus 4 con ~3K input + 2K output por edit → ~$0.18 por edit. A 1-2 edits por pieza promedio → ~$0.30/pieza extra → ~$9/mes a 1 pieza/día.

## Restricción explícita del template original (preservada)

> "It is also critical that you retain and keep the correct content `identifiers` and `external_source_links` for the stories that are being kept in your edits. These values are critical to the success of this task as we will use that as a reference downstream."

Traducción para nuestro caso: si tu pieza tiene `source_url`, `brief_id`, slide numbers, hashtags hash, NO LOS CAMBIES nunca a menos que el feedback los mencione explícitamente. Son keys para hashing, dedup, y tracking analytics.

## Diferencias respecto al template #12533 original

| Aspecto | Template #12533 | A11 nuestro |
|---|---|---|
| Targets soportados | 2 (top stories + subject line) — 2 prompts separados | 5 (brief, caption, newsletter, subject_line, visual_direction) — 1 prompt parametrizado |
| Idioma | Inglés | Español neutro LATAM |
| Storage del contenido a editar | Memory de n8n (state in workflow) | Supabase tabla `briefs` (más robusto, sobrevive reinicios) |
| Output | `top_selected_stories` mismo schema | `edited_content` mismo schema + `changes_summary` + `unchanged_fields` para auditoría |
| Loop budget | No explícito | Max 3 edits por pieza |
