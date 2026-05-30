# Runbook — Onboarding técnico Dinero IA

**Fecha:** 2026-05-30
**Status:** ready-to-execute paso a paso
**Audiencia:** Manuel (solo founder, no requiere experiencia n8n previa)
**Tiempo total estimado:** 90-120 min secuencial (puede partirse en 2-3 sesiones)

> **Importante:** este runbook se ejecuta **DESPUÉS de Fase -1 validada** (5-10 piezas manuales que pegaron). Si Fase -1 todavía no fue ejecutada, NO hacer este onboarding — es plata + tiempo invertido prematuramente.

---

## Pre-checklist (10 min)

Antes de arrancar, confirmar:

- [ ] Fase -1 ejecutada: ≥5 piezas publicadas manualmente
- [ ] Engagement promedio Fase -1 ≥2% (saves+comments/views)
- [ ] ≥1 sub-categoría con engagement claramente superior (la que vamos a doblar)
- [ ] Inflection Lever Track activo (≥10 outreaches enviados)
- [ ] Decisión: ¿arrancamos Fase 0 (smoke) o saltamos directo a Fase 1 (publish)?

**Recomendación fuerte:** arrancar siempre con Fase 0 (smoke, ~$10 testing) antes de comprometer SaaS ($48/mo recurrente).

---

## Bloque 1 — Telegram Bot (5 min)

Necesario para Fase 0 y Fase 1.

1. **Abrir Telegram** y buscar `@BotFather`
2. Mensaje: `/newbot`
3. BotFather pregunta nombre: responder **"Dinero IA Bot"**
4. BotFather pregunta username: responder **`dinero_ia_bot`** (o `@dineroia_bot` si tomado)
5. **Guardar el TOKEN** que devuelve (algo tipo `7891234567:AAFxxx...`). NO compartir. Es la API key del bot.
6. **Obtener tu chat_id:**
   - Buscar `@userinfobot` en Telegram
   - Escribirle `/start`
   - Te devuelve tu `id` (número de 9-10 dígitos). **Anotalo.**
7. **Iniciar conversación con tu bot:** buscar `@dinero_ia_bot` en Telegram y enviar `/start`. (Si no haces esto, el bot no puede mandarte mensajes — Telegram bloquea bots que escriben primero.)

**Output esperado:** tenés guardados `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`.

---

## Bloque 2 — Anthropic API (10 min)

1. Ir a [console.anthropic.com](https://console.anthropic.com)
2. **Crear cuenta** con `aibrieflatam.media@gmail.com` (el email del proyecto)
3. Sección **Billing** → agregar tarjeta de crédito → cargar **$20-30 USD initial** (suficiente para Fase 0 + 1 semana Fase 1)
4. Sección **API Keys** → crear nueva key con label `dinero-ia-n8n`
5. **Guardar la API key** (algo tipo `sk-ant-api03-xxx...`). NO compartir.
6. Sección **Limits** → confirmar:
   - Tier 1 default (50 req/min Sonnet, 50 req/min Opus). Suficiente para Fase 0.
   - Si necesitás más tier: solicitar Tier 2 después de gastar $20 (automatic upgrade ~7 días)

**Output:** `ANTHROPIC_API_KEY` guardada.

---

## Bloque 3 — OpenAI API (5 min) [opcional Fase 0, recomendado Fase 1]

Solo necesario si querés usar gpt-image-2 como backup de visual cuando Blotato no rinda. **Diferible** hasta que Fase 1 esté armada.

1. Ir a [platform.openai.com](https://platform.openai.com)
2. Crear cuenta con `aibrieflatam.media@gmail.com`
3. Billing → cargar **$10-15 USD initial** (cubre 200-300 imágenes a $0.04/u)
4. API Keys → crear key `dinero-ia-n8n`
5. **Guardar**: `OPENAI_API_KEY`

---

## Bloque 4 — n8n cloud trial (10 min)

1. Ir a [n8n.io](https://n8n.io) → **Get started free**
2. Registro con `aibrieflatam.media@gmail.com`
3. Elegir region: **US East** (más cerca de Anthropic + OpenAI = menor latencia)
4. Confirmar email
5. **NO importar nada todavía** — primero configurar credentials

### Configurar credentials (5 min)

En n8n UI → **Credentials** (sidebar izq) → **Create new credential**

#### Anthropic API
- **Credential type:** "Anthropic API"
- **API Key:** pegar `ANTHROPIC_API_KEY` del Bloque 2
- **Name:** `Anthropic API — Dinero IA`
- **Save**

#### Telegram API
- **Credential type:** "Telegram Bot API"
- **Access Token:** pegar `TELEGRAM_BOT_TOKEN` del Bloque 1
- **Name:** `Telegram Bot — Dinero IA`
- **Save**

(OpenAI y otros se configuran cuando se necesiten en Fase 1.)

---

## Bloque 5 — Importar workflow Fase 0 (5 min)

1. **Descargar** el archivo `infra/n8n/fase0.json` del repo (clone o raw download desde GitHub)
2. En n8n UI → **Workflows** → **+ New** → **Import from file**
3. Subir `fase0.json`
4. Verás 19 nodos en el canvas con líneas de conexión

### Reemplazar credentials placeholder

Buscar nodos con `"REPLACE_ME_..."`:

1. Click en **"Anthropic Sonnet 4.5 — A2"** → field `Credential to connect with` → seleccionar `Anthropic API — Dinero IA`
2. Repetir para **"Anthropic Opus 4 — A3"** y **"Anthropic Opus 4 — A9"** (3 nodos Anthropic en total)
3. Click en **"Telegram — Send Preview"** → field `Credential to connect with` → seleccionar `Telegram Bot — Dinero IA`
4. Mismo nodo → field `Chat ID` → reemplazar `REPLACE_ME_CHAT_ID` con tu `TELEGRAM_CHAT_ID` del Bloque 1

### Save

**Save** (Ctrl+S). El workflow debería mostrar **0 errores** (chequear el ícono ⚠️ al lado de cada node).

---

## Bloque 6 — Primer test Fase 0 (5 min)

1. Click en **"Manual Trigger"** (nodo izquierdo)
2. Click en **"Execute workflow"** (botón arriba derecha)
3. Esperar 30-90 segundos mientras se ejecuta
4. Verás los nodos cambiar de gris a verde uno por uno
5. **Si todo OK:** debería llegar un mensaje a tu Telegram con el preview del brief generado

### Posibles errores y cómo resolverlos

| Error | Causa | Fix |
|---|---|---|
| `Anthropic 401` | API key inválida o sin billing | Revisar credentials + Billing en console.anthropic.com |
| `Telegram chat not found` | chat_id incorrecto o no iniciaste conversación con bot | Mandar `/start` al bot + verificar chat_id con @userinfobot |
| `RSS feed empty` | Bloomberg Línea cambió URL o feed down | Probar el feed en browser: `https://www.bloomberglinea.com/arc/outboundfeeds/rss/?outputType=xml` |
| `Output parser failed` | Anthropic devolvió JSON malformado (raro pero pasa) | Re-ejecutar. Si pasa 3+ veces seguidas: revisar el prompt en el nodo A2/A3/A9 |
| `Rate limit` Anthropic | Más de 50 req/min en tier 1 | Esperar 1 min, re-ejecutar |

### Definition of Done Fase 0

Después de **3-5 ejecuciones exitosas**:
- [ ] Los briefs llegan a Telegram con voz "Dinero IA" reconocible (no genérica AI brief)
- [ ] El compliance verdict aparece (approved / blocked)
- [ ] El score promedio de los items Bloomberg Línea es ≥60 (sino, fuente débil — testear más fuentes)
- [ ] Tiempo total por ejecución <90 segundos
- [ ] Costo total testing <$5 Anthropic

**Si todo OK:** podés pasar a Bloque 7. Si NO: iterar prompts (A2/A3/A9) en n8n hasta calibrar.

---

## Bloque 7 — Cuentas SaaS Fase 1 (45-60 min)

Solo después de Fase 0 estable. Estas cuentas cuestan $48/mo recurrente.

### 7.1 ContentStudio Standard ($19/mo, 5 min)

1. Ir a [contentstudio.io](https://contentstudio.io)
2. Crear cuenta con `aibrieflatam.media@gmail.com`
3. Plan **Standard** ($19/mo billed monthly first, anual después si rinde)
4. **Conectar cuentas sociales** vía OAuth:
   - Instagram (cuenta de Dinero IA cuando esté registrada — o cuenta personal de Manuel para Fase -1 test)
   - TikTok
   - LinkedIn
   - (Opcional) X, Threads
5. En ContentStudio → **API & Webhooks** → crear API key con scope `posts:write`
6. **Guardar:** `CONTENT_STUDIO_API_KEY`

### 7.2 Blotato Starter ($29/mo, 15 min)

1. Ir a [blotato.com](https://blotato.com)
2. Crear cuenta con `aibrieflatam.media@gmail.com`
3. Plan **Starter** ($29/mo)
4. **Crear template `dinero-ia-dark-editorial`:**
   - Dimensiones: 1080×1080 (square IG carousel)
   - Background color: `#0F0F10`
   - Primary font: **Inter Bold** (size 64-80 para hooks, 32-40 para body)
   - Secondary font: **JetBrains Mono** (size 16-20 para captions/sources)
   - Accent color: `#00D9A0` (mint green para cifras destacadas)
   - 5-7 slides default:
     1. **Hook slide** — texto grande centrado + accent
     2. **Context slide** — "¿Por qué importa?"
     3. **Data slide 1** — cifra grande con fuente
     4. **Step 1 slide** — paso del prompt
     5. **Step 2 slide** — paso del prompt
     6. **Result slide** — resultado/aprendizaje + caveat
     7. **Disclaimer slide** — disclaimer + branding "Dinero IA"
5. **Save template** con name `dinero-ia-dark-editorial`
6. API key: **Settings → API** → crear con scope `carousels:generate`
7. **Guardar:** `BLOTATO_API_KEY`

### 7.3 Beehiiv Launch (gratis, 15 min)

1. Ir a [beehiiv.com](https://beehiiv.com)
2. Crear cuenta con `aibrieflatam.media@gmail.com`
3. Plan **Launch** (free hasta 2,500 subs)
4. **Crear publicación:**
   - Nombre: **Dinero IA**
   - Descripción: "IA aplicada a tus finanzas personales LATAM. Educativo, no asesoría. 5 min al día."
   - URL: `dineroia.beehiiv.com` (subdomain inicial) o `dineroia.com` si ya compraste dominio
   - From address: `hola@dineroia.com` (configurar email después si tenés dominio)
5. **Welcome sequence** (3 emails — diseñar despacio):
   - Email 1: intro + qué esperar
   - Email 2: top 5 piezas históricas (después de Fase 1 estable)
   - Email 3: encuesta sub-nicho favorito
6. **Footer obligatorio:**
   - Unsubscribe link (Beehiiv lo agrega automático)
   - Disclaimer financiero fijo: "Dinero IA es contenido educativo, no asesoría financiera. Antes de tomar decisiones con tu plata, consultá con un profesional matriculado."
   - Dirección física (CAN-SPAM compliance) — puede ser apartado postal
7. API key: **Settings → Integrations → API** → crear
8. **Guardar:** `BEEHIIV_API_KEY` + `BEEHIIV_PUBLICATION_ID`

### 7.4 Cargar credentials nuevas en n8n (5 min)

En n8n → Credentials → New:

- **ContentStudio API** (HTTP Header Auth, header `Authorization: Bearer {{ CONTENT_STUDIO_API_KEY }}`)
- **Blotato API** (HTTP Header Auth, header `X-API-Key: {{ BLOTATO_API_KEY }}`)
- **Beehiiv API** (HTTP Header Auth, header `Authorization: Bearer {{ BEEHIIV_API_KEY }}`)

(Workflow Fase 1 va a usar estas credentials cuando se importe.)

---

## Bloque 8 — Importar workflow Fase 1 (próxima entrega)

> **Pendiente:** el archivo `infra/n8n/dinero-ia-fase1-publish.json` aún no está hecho. Se entrega después de que Fase 0 corra estable 5+ veces.

Por ahora: el spec completo de Fase 1 webhooks está en `docs/PHASE1_INTEGRATION_SPEC.md`.

---

## Bloque 9 — Monitoreo continuo

### Daily check (5 min Manuel cada mañana)

1. Abrir Telegram → ¿llegó el preview? Si sí, decidir (Aprobar/Editar/Rechazar).
2. Si no llegó: abrir n8n cloud → **Executions** → ver último run → debugear error.

### Weekly check (15 min Manuel cada domingo)

1. n8n executions: ¿tasa de éxito >95%?
2. ContentStudio analytics: ¿engagement promedio >2%?
3. Beehiiv analytics: ¿open rate >25%? ¿subs crecen?
4. Anthropic billing: ¿costo dentro de presupuesto ($25-42/mo)?
5. Si algo se sale de banda: actualizar `manual-mvp/metrics/YYYY-WW.md` con notas + ajustar.

### Alerts opcionales

- n8n cloud manda email automático si workflow falla 3 veces seguidas (configurable en Settings → Notifications)
- Anthropic alerta si gastás >$50/día (configurable en Billing → Usage limits)
- ContentStudio alerta si un post falla publicar (notificación en UI + email)

---

## Si algo sale mal — escalation

| Síntoma | Primera acción | Segunda acción |
|---|---|---|
| Telegram no recibe nada | Re-execute workflow manual desde n8n → ver logs | Si falla: revisar credentials Telegram + Anthropic |
| Compliance bloquea 3 piezas seguidas | Revisar el contenido — quizás Bloomberg Línea está dando piezas con productos sin disclaimer | Ajustar prompt A3 para que SIEMPRE sugiera disclaimer si productos_mencionados.length > 0 |
| Scoring promedio <50 (todas descartadas) | Bloomberg Línea no está dando piezas Dinero IA-aplicables | Probar otra fuente RSS (Cenital, Pequeño Cerdo Capitalista) — editar URL en nodo RSS |
| Costos Anthropic >$60/mo (sobre presupuesto) | Verificar volumen real vs proyectado | Bajar temperature de A3 (0.4 → 0.3) + max_tokens (2000 → 1500) |
| ContentStudio rechaza un post | Probable: media URL inválida o caption muy largo | Verificar Blotato carousel_id válido + caption <2200 chars IG |
| Blotato carousel falla | API down o credits agotados | Manual upload visual a ContentStudio + reportar a Blotato support |

---

## Resumen — credentials que Manuel termina con

Al final de este runbook, Manuel tiene en n8n cloud configurado:

1. `Anthropic API — Dinero IA` (Fase 0 ✅)
2. `Telegram Bot — Dinero IA` (Fase 0 ✅)
3. `OpenAI API — Dinero IA` (Fase 1, backup visual)
4. `ContentStudio API — Dinero IA` (Fase 1)
5. `Blotato API — Dinero IA` (Fase 1)
6. `Beehiiv API — Dinero IA` (Fase 1)

Y en el repo (NO en variables — son referencias):

- Workflow `infra/n8n/fase0.json` (importable a n8n cloud)
- Workflow `infra/n8n/dinero-ia-fase1-publish.json` (pendiente — próxima sesión)
- Spec `docs/PHASE1_INTEGRATION_SPEC.md`
- Este runbook

**Tiempo total desde "no tengo nada" a "Fase 0 corriendo en Telegram":** ~35-45 min secuencial.
**Tiempo total a "Fase 1 publicando IG+TikTok+LinkedIn+Newsletter":** +60-90 min adicional (cuentas SaaS + import workflow Fase 1 cuando esté).
