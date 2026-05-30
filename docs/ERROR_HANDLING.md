# Error Handling Spec — Dinero IA

**Fecha:** 2026-05-30
**Status:** diseño para Fase 0-1.
**Principio:** **degradación controlada > fallar silencioso o full-stop**. El sistema sigue funcionando aunque algo falle, pero Manuel se entera siempre.

---

## Principios

1. **Nada se publica sin compliance pass.** Si A9 dice `blocked`, NO publica — punto.
2. **Nada se publica sin HITL approval.** Si Manuel no toca un botón, no se ejecuta el fanout.
3. **Cada falla deja log auditable.** En n8n execution log (siempre) + Supabase `audit_log` (Fase 1+).
4. **Manuel se entera de errores antes que de éxitos.** Notificación Telegram para failures críticos; éxitos solo en daily report.
5. **Retry SIEMPRE antes de fallar.** Backoff exponencial. 3 intentos máximo en operaciones idempotentes, 1 intento en operaciones con side effects.

---

## Failure modes Fase 0

### F0-1 — RSS feed devuelve vacío o 4xx/5xx

**Causa típica:** fuente cambió URL, está caída, o no hay items nuevos hoy.

**Comportamiento n8n:**
- Si vacío (0 items): **OK**, no es error — solo no hay nada que procesar hoy. Workflow termina sin errores. No notifica Manuel.
- Si 4xx/5xx: **retry 2× con 30s y 90s backoff**. Si sigue fallando: notifica Telegram a Manuel con mensaje:
  > ⚠️ Dinero IA — RSS Bloomberg Línea devolvió 503 (3 intentos). Workflow saltado hoy. Revisá el feed manual o cambiá a fuente backup.

### F0-2 — Anthropic API rate limit (429)

**Causa típica:** Tier 1 (50 req/min) saturado en testing intensivo.

**Comportamiento n8n:**
- `retryOnFail: true` + `waitBetweenTries: 5000` ya configurado en los nodos LLM
- 3 retries con 5s, 15s, 45s backoff
- Si todos fallan: marca el item como `discarded` con razón `anthropic_rate_limit` y sigue al próximo item

### F0-3 — Anthropic devuelve JSON malformado (output parser falla)

**Causa típica:** modelo "alucinó" estructura, temperatura muy alta, o prompt ambiguo.

**Comportamiento n8n:**
- Output Parser detecta el fail → workflow se rompe en ese nodo
- n8n retry automático (configurado): 3 intentos
- Si los 3 fallan: el item se loguea en `Log Discarded` con razón `parser_failed` + raw output
- Notifica Telegram:
  > ⚠️ A3 Editorial — output parser falló 3× para item "{título}". Brief no generado. Ver logs n8n.

**Fix recomendado:** bajar `temperature` del nodo Anthropic afectado (0.4 → 0.2) o reforzar prompt con ejemplo de output válido.

### F0-4 — Compliance bloquea pieza

**No es error.** Es comportamiento esperado.

**Comportamiento n8n:**
- A9 verdict = `blocked` → workflow NO sigue al Telegram preview de approval
- Telegram recibe en su lugar:
  > 🚫 Dinero IA — pieza rechazada por compliance
  > Título: {título}
  > Verdict: blocked
  > Blocks: {lista de issues}
  > Razón: {summary}
  > Item descartado. Revisar prompt A3 si esto pasa con frecuencia.

**Tasa de bloqueo esperada normal:** 10-20% de items. Si sube de 30%, el prompt A3 necesita ajuste (probablemente está generando recomendaciones directas o sin disclaimer).

### F0-5 — Telegram bot bloqueado o token inválido

**Causa típica:** Manuel borró conversación con bot, o regeneró el token y no actualizó credentials.

**Comportamiento n8n:**
- Telegram API devuelve 401 / 403
- n8n marca workflow como **failed**
- n8n cloud manda **email automático** a Manuel (configurable en Settings → Notifications) — esto es lo único que no depende de Telegram

**Fix:** abrir Telegram → `/start` al bot → si token fue regenerado, actualizar en n8n credentials.

---

## Failure modes Fase 1

### F1-1 — Manuel no responde al HITL en 4 horas

**Causa típica:** Manuel ocupado, dormido, sin señal.

**Comportamiento n8n:**
- Workflow `dinero-ia-fase1-hitl.json` tiene un **Wait node** con 4h timeout
- Si no hay callback en 4h:
  - Notifica recordatorio Telegram: *"⏰ Pieza esperando review hace 4h — {título}"*
- Si no hay callback en 8h:
  - Marca como `auto_rejected` en Supabase
  - NO publica
  - Notifica Telegram: *"⛔ Pieza descartada por timeout — {título}. Si querés rescatar: re-correr workflow."*

**Por qué este timeout matters:** si publicamos sin HITL aunque sea por timeout, se pierde el control editorial. Mejor saltar un día que publicar mal.

### F1-2 — Blotato falla generando carousel

**Causa típica:** credits agotados, template inválido, API temporarily down.

**Comportamiento n8n:**
- **Retry 2× con 30s, 90s backoff**
- Si falla las 2:
  - Trigger workflow alternativo `dinero-ia-fallback-images.json` que usa OpenAI gpt-image-2 directamente
  - Si fallback también falla: notifica Telegram con preview del brief + URLs originales
    > ⚠️ Blotato + gpt-image-2 fallaron. Brief listo, falta visual. Generá manual en ChatGPT y subí a IG.

### F1-3 — ContentStudio rechaza el post

**Causas típicas:**
- Caption excede límite IG (2,200 chars)
- Hashtags > 30
- Media URL ya expirada
- IG cuenta deslinked

**Comportamiento n8n:**
- Catch error del POST a ContentStudio
- **Si caption issue:** llamar nodo "Trim caption" que recorta a 2,100 chars + reintenta
- **Si hashtags issue:** trim a 25 hashtags + reintenta
- **Si media expired:** re-llamar Blotato para regenerar URLs + reintentar
- **Si cuenta deslinked:** NO reintentar — notificar Telegram inmediatamente:
  > 🔴 ContentStudio — cuenta IG deslinked. Re-conectá vía OAuth en contentstudio.io ANTES de próxima publish.

### F1-4 — Beehiiv rechaza el newsletter send

**Causas típicas:**
- Schedule_at en el pasado
- API key revoked
- Lista de subs muy chica para acción (early stage)

**Comportamiento n8n:**
- Catch error del POST a Beehiiv
- **Si schedule pasado:** ajustar a +5 min from now + reintenta
- **Si API key revoked:** notificar Telegram + dejar post en draft (Manuel puede publicar manual desde Beehiiv UI)
- **Si otra causa:** dejar en draft + notificar Telegram

### F1-5 — IG/TikTok algoritmo flag temporario

**Causa típica:** post fue marcado como "spam" por algoritmo Meta/ByteDance (raro pero pasa con contenido nuevo).

**Comportamiento:**
- ContentStudio reporta el status via webhook (configurable)
- n8n recibe webhook → log + notifica Telegram:
  > ⚠️ IG/TikTok flag temporario en post "{título}". Reach reducido probable. Ver detalles en {plataforma}.

**Acción manual:** ninguna. El flag suele resolverse solo en 24-48h. NO eliminar el post (eso empeora reputation).

### F1-6 — Costo Anthropic excede presupuesto diario

**Causa típica:** loop infinito (raro), muchas regeneraciones, o spike en items procesados.

**Comportamiento:**
- Anthropic Billing tiene **alert configurable** ($50/día sugerido en runbook)
- Si Manuel recibe alert: pausar workflow en n8n manualmente + investigar
- En workflow: agregar **Code node "Cost Check"** que cuenta tokens/día y aborta si excede límite (Fase 1 v2 mejora)

---

## Logging & audit trail

### Niveles de log

| Nivel | Qué se loguea | Dónde |
|---|---|---|
| **Workflow execution** | Cada run completo de n8n (input, output por nodo, errores) | n8n cloud (built-in, 7 días retention en tier Starter) |
| **Compliance decisions** | Cada A9 verdict + checks + brief_id | Supabase `compliance_log` (Fase 1) |
| **HITL decisions** | Cada button press de Manuel: approve/edit/reject + timestamp + brief_id | Supabase `briefs_pending.decided_at` (Fase 1) |
| **Publishing results** | Status de cada post IG/TT/LI/NL (success/failed + reason) | Supabase `publish_log` (Fase 1) |
| **Cost tracking** | Tokens consumidos + costo por agent por día | Supabase `costs_daily` (Fase 1) |

### Retención

- n8n cloud Starter: **7 días** execution log. Si necesitás más: upgrade a Pro o export semanal a Supabase.
- Supabase Free: **500 MB DB total**. Suficiente para 6+ meses de operación 1 pieza/día.

### Compliance audit (regulatory)

Si CNV/CNBV/SFC pregunta cómo Dinero IA evita ser "asesoría no autorizada", la tabla `compliance_log` muestra:

- Cada pieza pasó por A9 antes de publicar
- Verdict por pieza: approved / approved_with_warnings / blocked
- Reglas 16-18 (financieras) explícitamente chequeadas
- Disclaimer presente en todas las piezas con productos
- Audit trail timestamped + immutable

**Esto es nuestro escudo legal.** No es opcional.

---

## Notificaciones a Manuel (lo que SÍ recibe vs NO)

### SÍ recibe (Telegram)

- ✅ Preview de cada brief listo para HITL (con verdict compliance + inline keyboard)
- ⚠️ Cualquier failure que requiera acción suya (cuenta deslinked, fuente caída, costos sobre presupuesto)
- ⛔ Pieza rechazada por compliance (con razón)
- ⏰ Recordatorio HITL después de 4h sin respuesta
- 📊 Daily report 9pm: 1 mensaje con resumen del día (pieza publicada, engagement preliminar, costo, outreaches pendientes)

### NO recibe

- ❌ Cada item descartado por low score (sería ruido — 80% de items se descartan)
- ❌ Logs internos de n8n (van al dashboard n8n, no a Telegram)
- ❌ Métricas detalladas IG/TikTok (van a ContentStudio dashboard)
- ❌ Subs nuevos uno por uno (Beehiiv dashboard suficiente)

**Filosofía:** Manuel se entera de lo que requiere DECISIÓN suya. Lo demás vive en dashboards consultables.

---

## Circuit breakers

Hard stops automáticos que pausan todo el workflow si algo grave pasa:

| Trigger | Acción | Quién resetea |
|---|---|---|
| 5 compliance blocks consecutivos | Pausar workflow + notificar Manuel + sugerir revisar prompt A3 | Manuel manual desde n8n UI |
| Costo Anthropic >$10/día | Pausar workflow + notificar | Manuel manual + ajustar pricing |
| 3 HITL timeouts (sin respuesta 8h) en 7 días | Pausar workflow + sugerir "tomate descanso" | Manuel manual |
| Anthropic devuelve `safety: refusal` para 3 piezas seguidas | Pausar + notificar | Manuel manual + revisar fuentes (¿estamos pidiendo contenido sensitivo?) |
| n8n cloud quota >80% | Notificar (sin pausar) | Manuel decide si upgrade plan |

---

## Recovery procedures

### Recovery 1 — Workflow pausado por circuit breaker

1. Manuel revisa razón del breaker en n8n UI → Executions → último run
2. Aplica fix (ajuste prompt / ajuste budget / aumentar quota)
3. n8n UI → Workflow → toggle Active ON
4. Manual execute para confirmar que funciona
5. Si funciona: dejar Active. Si NO: iterar.

### Recovery 2 — Pérdida de Supabase data

Solo aplica a Fase 1+. Backup strategy:

- **Daily export:** cron n8n a las 11pm exporta `briefs_pending` + `compliance_log` + `publish_log` a JSON en GitHub privado o S3
- **Si Supabase se cae:** restaurar último backup → tiempo perdido máximo 24h
- **Si pérdida total Supabase:** workflow degrada a "no tracking" — sigue funcionando para publish, pero sin audit trail. Manuel decide pausar o continuar.

### Recovery 3 — Cuenta SaaS bloqueada/cancelada

- **ContentStudio bloqueado:** plan B = Blotato standalone publishing (community node n8n) + manual review
- **Blotato bloqueado:** plan B = OpenAI gpt-image-2 directo + manual upload a ContentStudio
- **Beehiiv bloqueado:** plan B = export subscribers + migrar a Substack o ConvertKit (formato compatible)

Todos los planes B requieren ~30 min de switchover.

---

## Testing del error handling

Antes de Fase 1 production, **simular cada failure mode** manualmente:

| Test | Cómo simular | Expected behavior |
|---|---|---|
| F0-1 RSS down | Cambiar URL RSS a inexistente | Workflow falla con retry + notifica Telegram |
| F0-2 Rate limit | Trigger 60 executions seguidas | n8n retry automático, eventualmente OK |
| F0-3 JSON malformed | Subir temperature A3 a 1.0 + setear prompt vago | Output parser falla, retry, eventualmente OK o notifica |
| F0-4 Compliance block | Crear item de test con texto "comprá Bitso AHORA, vas a ganar 50% garantizado" | A9 bloquea, NO llega a preview |
| F0-5 Telegram inválido | Borrar credentials Telegram temporal | Workflow falla, n8n cloud manda email |
| F1-1 HITL timeout | Aprobar pieza pero NO tocar botón | Workflow espera, después 4h + 8h marca rejected |
| F1-2 Blotato fail | Pausar credenciales Blotato | Fallback a OpenAI gpt-image-2 |
| F1-3 CS rechaza | Mandar caption con 3000 chars | n8n trim + reintenta |

**Tiempo para testear todos los failure modes:** 60-90 min. Una vez por semana en Fase 1, una vez al mes después.
