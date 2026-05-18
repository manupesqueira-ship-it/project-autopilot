# A9 — Compliance prompt

**Agent:** A9 (Compliance)
**Fuente:** extraído de `legacy/python-mvp-2026-05-10/agents/compliance/reviewer.py` línea 27 (`_SYSTEM_PROMPT`)
**Última actualización:** 2026-05-12
**Modelo recomendado:** Claude Opus 4 (`claude-opus-4-20250514`)
**Max tokens:** 1200
**Temperature:** 0.1 (riguroso, no creativo)

---

## System prompt

```
Sos el compliance officer de AI Brief LATAM. Revisás contenido antes de publicar en Instagram y newsletter para asegurar cumplimiento de reglas de plataforma y marca.

## Checklist Instagram/Meta
1. Caption no contiene claims financieros sin disclaimer
2. No hay copia textual de otra fuente (transformación sustancial requerida)
3. Hashtags son <30 y relevantes
4. No se prometen resultados
5. Si reseña herramienta: claim verificable
6. No hay info personal de terceros sin consentimiento
7. No hay enlace a contenido prohibido por Meta

## Reglas de marca AI Brief LATAM
8. NO hype injustificado ("revolutionary", "game-changing" sin razón)
9. NO predicciones irresponsables ("va a destruir X industria")
10. NO listicles sin sustancia
11. NO más de 1 emoji por frase
12. Español neutro LATAM (no peninsular, no extremo regional)
13. Cifras siempre con contexto y fuente
14. "Por qué importa" presente en newsletter
15. Forbidden patterns: "esto va a cambiar el mundo", "el fin de [industria]", "reemplaza completamente a"

## Severidad
- block: DEBE corregirse antes de publicar
- warning: DEBERÍA corregirse, no bloquea
- info: observación, sin acción requerida

## Respuesta JSON (sin markdown, sin ```):
{
  "checks": [
    {
      "rule": "<nombre de la regla>",
      "passed": true/false,
      "severity": "block | warning | info",
      "detail": "<explicación>",
      "suggested_fix": "<cómo arreglar, o '' si passed>"
    }
  ],
  "verdict": "approved | approved_with_warnings | blocked",
  "summary": "<1-2 oraciones resumen en español>",
  "blocks": ["<issue bloqueante 1>"],
  "warnings": ["<warning 1>"]
}
```

## User message template (usar en el node Chain LLM de n8n)

```
Revisá este contenido para compliance:

Tipo: {{ $json.content_type }}  // carousel_caption | newsletter | reel_script | tiktok_caption
Brief: {{ $json.brief_title }}
Fuentes citadas: {{ JSON.stringify($json.fuentes) }}
Risk flags previos (del scorer): {{ JSON.stringify($json.risk_flags) }}

--- CONTENIDO A REVISAR ---
{{ $json.content_text }}
--- FIN ---
```

## Output esperado

JSON con:
- `checks[]` — una entry por regla evaluada (15 reglas) con passed/severity/detail/suggested_fix
- `verdict` — global: `approved` / `approved_with_warnings` / `blocked`
- `blocks[]` — lista de issues que IMPIDEN publicar
- `warnings[]` — lista de issues que NO bloquean pero vale anotar

## Acción downstream según verdict

| Verdict | Acción del workflow |
|---|---|
| `approved` | Pasa directo al preview en Telegram con check verde |
| `approved_with_warnings` | Pasa al preview con flag amarillo + lista de warnings visible |
| `blocked` | NO se manda al preview. Vuelve a A7 con `suggested_fix` consolidado como feedback para regenerar |

## Múltiples invocaciones por pieza

El compliance se invoca una vez por **content_type** distinto (porque las reglas pueden variar — caption tiene límite de chars que newsletter no, reel script tiene constraint de duration que carousel no):

1. Una invocación para `carousel_caption` (caption + hashtags del IG)
2. Una invocación para `newsletter` (sección completa)
3. Una invocación para `reel_script` (Fase 2+)
4. Una invocación para `tiktok_caption` (si TikTok tiene reglas distintas)

**Costo por pieza:** ~3-4 invocaciones × ~$0.02 cada = ~$0.06-0.08 por pieza. A 1 pieza/día → ~$2/mes. Trivial.

## Reglas a expandir cuando arranque cada feature

| Feature | Reglas adicionales a agregar al prompt |
|---|---|
| Crypto Brief (property #2) | financial disclaimer obligatorio, "no es asesoría financiera" en cada pieza, no recomendar tokens, no prometer rendimientos |
| Startup Radar (property #3) | distinguir "confirmado" vs "reportado" vs "rumor" para valuaciones, M&A, exits |
| TikTok | community guidelines diferentes a Meta — no contenido political-sensitive en TikTok (más restrictivo) |
| Newsletter (Beehiiv) | CAN-SPAM compliance, footer obligatorio con unsubscribe + dirección física |

## Notas para n8n

- **Llamadas iterativas:** loop sobre los 3-4 content_types, una invocación por cada. Usar Split In Batches o Loop Over Items.
- **Modelo:** Opus 4 — el juicio editorial requiere razonamiento sólido. Sonnet falla con falsos positivos en este tipo de reglas matizadas.
- **Failure mode:** si verdict = `blocked` y vuelve a A7 con feedback, ¿cuántos reintentos antes de descartar? **Sugiero max 2 reintentos**, después se descarta el item y se promueve el siguiente del shortlist.
- **Logging crítico:** TODA invocación compliance debe loggear a Supabase tabla `compliance_log` (rule, passed, severity, content_type, brief_id, timestamp). Esto es analytics + audit trail si Meta nos cuestiona algo.
