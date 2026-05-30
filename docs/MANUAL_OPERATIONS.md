# Manual Operations — AI Brief LATAM

**Status:** activo mientras el pipeline n8n no esté corriendo. Documenta cómo Manuel produce contenido a mano usando los mismos prompts que el pipeline eventualmente automatizará.
**Última actualización:** 2026-05-12
**Frecuencia objetivo:** 1 pieza por día mientras se construye Fase 0 (no se exige cumplimiento estricto; el objetivo es generar 5-10 piezas seed para alimentar el few-shot de A3).

---

## Por qué existe este documento

El pipeline n8n está en diseño/Fase 0. Mientras tanto, Manuel puede (debe?) seguir produciendo piezas a mano. Esto cumple 3 propósitos:

1. **No pausar momentum** — la marca necesita una cadencia de posts aunque sea manual.
2. **Generar seeds para A3 few-shot** — el prompt A3 Editorial mejora cuando se le pasan 2-3 briefs aprobados anteriores como ejemplos. Esos seeds salen de este flujo manual.
3. **Validar voz/format antes de automatizar** — si un brief manual no convence, el problema está en la voz, no en n8n. Mejor descubrirlo ahora.

---

## Flujo manual diario (~45 min)

### Paso 1 — Discovery (~10 min)

Manuel escanea las fuentes:

| Fuente | URL | Para qué |
|---|---|---|
| OpenAI Blog | https://openai.com/blog | Anuncios oficiales |
| Anthropic | https://www.anthropic.com/news | Anuncios oficiales |
| TechCrunch AI | https://techcrunch.com/category/artificial-intelligence/ | Movimientos industria |
| Hacker News | https://news.ycombinator.com/ | Pulso técnico + comentarios señalados |
| Latent Space | https://www.latent.space/ | Análisis profundo IA |
| Contxto | https://contxto.com/en/ | LATAM startup news |
| LatamList | https://latamlist.com/ | LATAM ecosystem digest |
| La Nación Tecnología | https://www.lanacion.com.ar/tecnologia/ | LATAM tech AR |

**Output:** elegir 3-5 candidatos del día. No más. La fricción de elegir entre 20 cosa es lo que mata la cadencia.

### Paso 2 — Scoring rápido (~5 min)

Para cada candidato, aplicar la rúbrica de A2 a ojo (no necesita Claude para esto en modo manual):

| Categoría | Pregunta rápida | Score |
|---|---|---|
| relevancia_latam | ¿Esto le importa a un founder/manager LATAM o es solo USA? | 0-20 |
| novedad | ¿Es de las últimas 24-48h o ya circuló? | 0-15 |
| credibilidad_fuente | ¿La fuente es primary o un blogger random? | 0-15 |
| potencial_educativo | ¿Aprendés algo concreto leyendo esto? | 0-10 |
| fit_marca | ¿Es sobrio o es hype? | 0-10 |

**Output:** pick 1. El de score más alto. Si empate, el más "raro" (que ninguna otra newsletter está cubriendo) gana.

### Paso 3 — Brief con Claude (~10 min)

Abrir Claude (claude.ai), nuevo chat. Pegar el system prompt completo de `projects/dinero-ia/prompts/a3-editorial.md` (sección "## System prompt") **una vez**. Después, por cada brief:

```
Generá un brief editorial completo para este item:

Título: <título>
Fuente: <fuente>
URL: <url>
Snippet: <párrafo del artículo o tu resumen de 2-3 frases>
Signal Score: <score que le pusiste a ojo>
Ángulo sugerido: <tu intuición editorial>
Risk flags: <[] si nada raro>
```

Claude devuelve JSON con el brief estructurado.

**Validación rápida:**
- ¿`hook_tentativo` cumple los 3 requisitos (atención + tensión + promesa)?
- ¿`angulo_latam` es concreto o genérico?
- ¿`datos_clave` tiene cifras con contexto?

Si algo no convence → pedir regenerar parte específica ("regenerá solo `hook_tentativo`, más sobrio"). Esto es el comportamiento de A11 Editor que eventualmente automatizamos.

### Paso 4 — Copy con Claude (~10 min)

Mismo chat. Pegar el system prompt de `prompts/a7-copy-composer.md`. Decir:

```
Generá el carousel (5 slides) + caption IG + caption TikTok + newsletter section + reel script para este brief verificado:

<pegar el JSON del brief de A3>
```

Claude devuelve JSON con `carousel`, `newsletter`, `reel_script`, `tiktok`.

### Paso 5 — Compliance check manual (~3 min)

Aplicar checklist de `prompts/a9-compliance.md` a ojo:

| # | Regla |
|---|---|
| 1 | ¿Caption sin claims financieros sin disclaimer? |
| 2 | ¿No hay copia textual de otra fuente? |
| 3 | ¿Hashtags < 30 y relevantes? |
| 4 | ¿No se prometen resultados? |
| 8 | ¿Sin hype injustificado? |
| 9 | ¿Sin predicciones irresponsables? |
| 11 | ¿Max 1 emoji por frase? |
| 12 | ¿Español neutro LATAM? |
| 13 | ¿Cifras con contexto y fuente? |

Si falla algo → editar la sección específica con Claude ("rewrite slide 3 para no prometer resultados"). Iterar máximo 2 veces; si después de 2 sigue mal, descartar.

### Paso 6 — Visual con DALL-E playground (~5 min)

Por ahora **NO** gpt-image-2 vía API (eso espera Fase 1). En modo manual, ChatGPT Plus tiene generación de imágenes incluida en la suscripción ($20/mo). Para cada slide:

1. Abrir ChatGPT (con DALL-E 3 / gpt-image-2 según versión).
2. Prompt template:
   ```
   Editorial design composition, dark charcoal background #0F0F10. Big headline text in white Inter Bold reading "<hook tentativo de la slide>". Mint green #00D9A0 accent on key numbers. Generous negative space. JetBrains Mono caption bottom-right: "AI BRIEF LATAM". Minimalist editorial style, no stock photography, no faces, no cartoons, square 1024x1024.
   ```
3. Generar. Descargar.
4. Si la tipografía sale fea (común), repetir 2-3 veces hasta tener algo aceptable. **Esto es trabajo manual real** — el pipeline lo automatiza pero la manualidad ahora cuesta tiempo.

**Atajo alternativo:** generar fondos limpios con DALL-E, después agregar tipografía en Canva con Inter + JetBrains Mono (free en Canva). Más control de tipografía, menos magia.

### Paso 7 — Archivo (~2 min)

Guardar el resultado en `projects/dinero-ia/manual-mvp/pieces/YYYY-MM-DD_slug.md`:

```markdown
# <Título>

**Fecha:** YYYY-MM-DD
**Fuente:** <URL>
**Score (manual):** XX/100
**Aprobado para publicar:** sí | no

## Brief (output de A3)

<JSON o markdown del brief>

## Carousel (output de A7)

<JSON o slides en markdown>

## Caption IG

<caption>

## Hashtags

<#hashtags>

## Newsletter section

<sección>

## Reel script (Fase 2 — guardar igual aunque no se grabe)

<script>

## Decisiones manuales

- Hook elegido: <cuál>
- Por qué este ángulo: <1-2 frases>
- Edits aplicados: <qué cambiaste vs lo que generó Claude>
```

### Paso 8 — Publicación (~5 min)

**IG carousel:**
1. Buffer o IG nativo. Subir 5-7 imágenes en orden.
2. Pegar caption del archivo.
3. Pegar hashtags.
4. Schedule a la hora del día que mejor performe (testing inicial: 8:00 AM CDMX y 6:00 PM CDMX, comparar).

**TikTok caption:**
- Usar el `tiktok.caption` del archivo, no el de IG.
- Sin imagen — eso es Fase 2 con Seedance.

**Newsletter (cuando Beehiiv esté armado):**
- Sección del archivo va en el daily email.
- Por ahora archivado solamente.

---

## Métricas a trackear (manual, una hoja por semana)

Crear `manual-mvp/metrics/YYYY-WW.md` cada lunes:

```markdown
# Semana XX — métricas

| Día | Brief | IG Saves | IG Comments | IG Reach | TikTok Views | Notas |
|---|---|---:|---:|---:|---:|---|
| Lun | <slug> | X | X | X | X | <qué funcionó / qué no> |
...

## Observaciones de la semana
- Hooks que mejor performaron: <lista>
- Hooks que peor performaron: <lista>
- Hipótesis para la próxima: <1-2 cambios para testear>
```

Esto alimenta el feedback loop que eventualmente A2 score-ea automáticamente.

---

## Cuándo dejar de operar manual

Manuel pasa a Fase 0 (smoke test n8n) cuando:
1. Telegram bot + Anthropic API key estén cargados en n8n.
2. El `fase0.json` esté importado.
3. El primer run manual de n8n entregue un brief comparable a los manuales en calidad.

Manuel pasa a Fase 1 (pipeline completo) cuando:
1. Fase 0 entregó ≥3 briefs decentes en Telegram (≥1 al día por 3 días).
2. Decisión publisher confirmada (ADR-012 → ADR-014: Upload-Post).
3. Cuenta Supabase creada con el schema de `infra/supabase/migrations/001_initial.sql` aplicado.
4. Decisión sobre plan n8n (Starter / Pro / self-hosted) tomada.

**Hasta que Fase 1 corra estable, este documento SIGUE vigente como fallback.** Si el pipeline falla un día, Manuel vuelve al manual sin drama.

---

## Costos estimados modo manual

| Item | Costo/mes | Por qué |
|---|---:|---|
| ChatGPT Plus | $20 USD | Generación de imágenes DALL-E + Claude alt |
| Claude.ai Pro (opcional) | $20 USD | Si usás Claude principalmente, mejor que ChatGPT |
| Canva Pro (opcional) | $13 USD | Post-procesado de imágenes + brand kit |
| Buffer Essentials | $15 USD | Scheduling IG + TikTok |
| **Total mínimo** | **$35-40 USD/mes** | Claude.ai Pro + Buffer |
| **Total con Canva** | **$48-53 USD/mes** | + Canva Pro |

Comparado con Fase 1 automatizado (~$85-100/mes Anthropic + OpenAI + n8n Pro), el manual es **más barato** pero **mucho más lento**: 45 min/día × 30 días = 22 horas/mes de Manuel personalmente.

---

## Diferencias críticas vs pipeline automatizado

| Aspecto | Manual | Pipeline Fase 1 |
|---|---|---|
| Discovery | Manuel browsea 8 fuentes | RSS polling 12+ fuentes automático |
| Dedup | A ojo (memoria de Manuel) | Supabase hash 30d |
| Scoring | Heurístico, 5 categorías | A2 rúbrica 8 categorías con Sonnet 4.5 |
| Brief | Claude.ai chat manual | A3 Chain LLM con few-shot examples |
| Fact-check | A ojo | A4 con Claude web_search Tool |
| Copy | Claude.ai chat | A7 con 3-5 caption alternates |
| Visuals | DALL-E playground + Canva | A5 + A8a con gpt-image-2 API + estilo locked |
| Compliance | Checklist a ojo | A9 con 15 reglas + retry loop |
| HITL | Sin gate explícito (Manuel decide) | Telegram bidireccional con A11 Editor |
| Publishing | Buffer/IG nativo manual | A10 via Blotato/Upload-Post |
| Logging | Manuel commitea markdown | Auto a Supabase + GitHub backup |

El delta principal NO es velocidad (manual también puede hacer 1/día). Es **consistencia editorial** + **audit trail** + **escala** una vez que AI How-To LATAM esté validada y pueda crecer en volumen.
