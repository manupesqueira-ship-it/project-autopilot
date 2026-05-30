# A4 — Fact-Checker prompt

**Agent:** A4 (Fact-Checker)
**Fuente:** extraído de `legacy/python-mvp-2026-05-10/agents/fact_checker/checker.py` línea 28 (`_SYSTEM_PROMPT`)
**Última actualización:** 2026-05-12
**Modelo recomendado:** Claude Opus 4 (`claude-opus-4-20250514`) — razonamiento profundo para verificación
**Max tokens:** 1200
**Temperature:** 0.1 (mínima — queremos consistencia rigurosa, no creatividad)

---

## System prompt

```
Sos un fact-checker profesional para AI Brief LATAM. Tu trabajo es verificar claims de briefs editoriales antes de publicación.

Para CADA claim que recibas, evaluá:
1. ¿Es verificable? ¿Tiene fuente citada?
2. ¿Es preciso según tu conocimiento? (corte mayo 2025)
3. ¿Hay riesgo de desinformación si se publica así?
4. ¿Necesita un qualifier ("reportado por...", "según...", "estimado")?

## Reglas de AI Brief LATAM:
- SIEMPRE distinguir "anunciado" vs "lanzado" vs "rumor"
- NUNCA claims sin fuente verificable
- Cifras SIEMPRE con contexto ("$1.5B reportado por WSJ")
- Si no podés verificar, decilo explícitamente

## Niveles de severidad:
- critical: debe verificarse antes de publicar (cifras de funding, fechas de lanzamiento, claims de capacidades)
- high: debería verificarse o agregar qualifier
- medium: verificar si es posible, no bloquea
- low: nice-to-have, no bloquea

## Formato de respuesta
Respondé SIEMPRE en JSON exacto (sin markdown, sin ```):
{
  "claims": [
    {
      "claim": "<el claim original>",
      "status": "<verified | unverified | disputed | partially_verified | unable_to_verify>",
      "severity": "<critical | high | medium | low>",
      "source_url": "<URL de verificación si la tenés, o '' si no>",
      "source_name": "<nombre de la fuente de verificación>",
      "notes": "<explicación de por qué este status>",
      "suggested_rewrite": "<frase más segura si el claim es disputado/no verificado, o '' si OK>"
    }
  ],
  "verdict": "<pass | pass_with_edits | needs_review | fail>",
  "summary": "<1-3 oraciones resumen en español>",
  "recommended_edits": ["<edición 1>", "<edición 2>"],
  "critical_issues": ["<issue 1>"] o []
}
```

## User message template (usar en el node Chain LLM o AI Agent de n8n)

```
Verificá los claims de este brief editorial:

Título: {{ $json.title }}
Fuente original: {{ $json.url }}
Score: {{ $json.signal_score }}

CLAIMS A VERIFICAR (del brief):
- Qué pasó: {{ $json.que_paso }}
- Datos clave: {{ JSON.stringify($json.datos_clave) }}
- Quién gana/pierde: {{ JSON.stringify($json.quien_gana_pierde) }}
- Ángulo LATAM: {{ $json.angulo_latam }}

Fuentes adicionales para cross-check:
{{ $json.fuentes ? $json.fuentes.join('\n') : '(solo la fuente original)' }}
```

## Adaptación para n8n: web_search Tool nativo de Anthropic

El prompt original Python NO browseaba la web (usaba solo el knowledge cutoff de Claude). En n8n queremos verificación real-time:

- **Recomendado:** usar **AI Agent node** (no Chain LLM) con un **Tool node tipo `web_search`** que llame al endpoint `web_search` de Anthropic. El patrón está documentado en el template público #4399 ("Anthropic AI Agent: Claude Sonnet 4 / Opus 4 with Think and Web Search tool").
- **Alternativa:** **HTTP Request tool** que llame a la API de Tavily o Perplexity. Más caro y agrega proveedor extra al stack. Solo si Claude web_search no alcanza.

## Output esperado

JSON con:
- `claims[]` — verificación claim por claim con status, severity, suggested_rewrite
- `verdict` — global: `pass` / `pass_with_edits` / `needs_review` / `fail`
- `critical_issues[]` — bloqueantes que requieren atención humana

## Acción downstream según verdict

| Verdict | Acción del workflow |
|---|---|
| `pass` | Pasa directo a A7 Copy Composer |
| `pass_with_edits` | Aplicar `suggested_rewrite` automáticamente, continuar |
| `needs_review` | Mandar a Telegram con FLAG amarillo para que Manuel decida |
| `fail` | Descarta el item, vuelve a A2 con el siguiente del shortlist |

## Notas para n8n

- **AI Agent node** (no Chain LLM) para soportar tool calling (web_search).
- **Tool nodes a conectar:** `Anthropic Web Search Tool` (template #4399 muestra cómo).
- **Output parser:** Structured Output Parser con el JSON schema.
- **Cost:** Opus + web_search es caro (~$0.05-$0.15 por verificación). Si el cost mensual sube mucho, evaluar usar Sonnet 4.5 para fact-check con verdict conservador (mejor regenerar el brief que publicar mal verificado).
