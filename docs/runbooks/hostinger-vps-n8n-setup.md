# Runbook — Hostinger VPS + n8n setup

**Fuente:** ADR-015 (Hostinger VPS KVM2 self-hosted, 2026-05-12)
**Tiempo estimado total:** 60-90 minutos
**Recurrencia:** una vez (setup inicial). Mantenimiento posterior ~30 min/mes.
**Pre-requisitos:** tarjeta de crédito, email aibrieflatam.media@gmail.com, dominio opcional.

---

## Por qué este runbook

ADR-015 lockeó Hostinger VPS KVM2 como host de n8n self-hosted. Este documento es la guía paso a paso para que cuando Manuel decida ejecutarlo, no haya fricción operativa. Cualquiera (incluso yo desde este chat asistiéndote) puede seguirlo.

---

## Paso 1 — Crear cuenta Hostinger (~5 min)

1. Ir a https://www.hostinger.com/
2. Click "Sign Up" → email aibrieflatam.media@gmail.com
3. Confirmar email
4. **NO comprar todavía** — primero elegir el plan correcto

## Paso 2 — Comprar VPS KVM2 con plantilla n8n (~10 min)

1. Ir a https://www.hostinger.com/self-hosted-n8n
2. Seleccionar plan **KVM 2** (NO el KVM 1 — n8n recomienda 2 vCPU + 4 GB mínimo)
   - 2 vCPU cores
   - 8 GB RAM
   - 100 GB NVMe SSD
   - 8 TB bandwidth
3. Elegir duración:
   - **24 meses** ($6.49/mo facturado de una): mejor precio
   - **12 meses** ($7.99/mo): mejor balance compromiso/precio
   - **1 mes** ($14.99/mo): test rápido (no recomendado para producción)
4. Datacenter location:
   - **Brasil (São Paulo)** — mejor latencia para LATAM
   - Alternative: USA East (Virginia) si Brasil no disponible
5. Hostname: `aibrief-prod-01` (o similar — para distinguirlo si agregás más VPS después)
6. **Antes de checkout:**
   - Verificá que la opción "OS template: n8n" está seleccionada (NO Ubuntu base — querés la plantilla pre-instalada)
   - Si te ofrece "Hostinger AI Domain" gratis, **rechazar** — la plantilla se accede por IP inicialmente
7. Checkout con tarjeta
8. Esperar ~5 min mientras Hostinger provisiona

## Paso 3 — Acceso inicial a n8n (~10 min)

1. En el dashboard Hostinger → VPS → tu nuevo servidor → "Manage"
2. Ver el **IP público** (formato `123.45.67.89`)
3. Ver el **panel n8n** — Hostinger pre-provisiona la URL: `https://[IP]:5678` o `https://n8n.[IP].sslip.io`
4. Primer login:
   - **Username:** crear admin user en primer boot (Hostinger te muestra el setup wizard)
   - **Password:** generar fuerte, guardar en password manager
   - **Owner email:** aibrieflatam.media@gmail.com
5. Activar n8n license:
   - n8n self-hosted tiene 2 modos:
     - **Community Edition** — gratis, todo lo que necesitamos para Fase 1
     - **Enterprise** — features extra (RBAC, audit logs, LDAP) — no necesarios
   - Saltear Enterprise license. Usar Community Edition.

## Paso 4 — Configurar dominio (opcional, recomendado) (~15 min)

**Por qué hacerlo:** acceder a n8n via `https://n8n.aibrieflatam.media` es más profesional que via IP. También necesario si querés que Telegram webhook llegue a n8n (Telegram exige HTTPS válido).

1. **Comprar dominio** — sugerencias:
   - `aibrieflatam.com` (canonical, más cara)
   - `aibrief.media` (corta, premium)
   - `aibrieflatam.media` (matchea el Gmail business)
   - Usar Hostinger Domain ($9-12/year) o Namecheap ($10-15/year)
2. **Configurar DNS:**
   - En el panel del registrador, crear A record:
     - Host: `n8n` (subdominio)
     - Value: IP del VPS (de Paso 3)
     - TTL: 3600
   - Esperar propagación 5-30 min
3. **Configurar SSL:**
   - SSH al VPS (Hostinger te da Web SSH gratis desde el panel)
   - Hostinger n8n template incluye script para Let's Encrypt:
     ```bash
     sudo /opt/n8n/setup-ssl.sh n8n.aibrieflatam.media
     ```
   - Confirmar que el cert se renueva automático (cron job ya configurado por la plantilla)
4. Acceder: https://n8n.aibrieflatam.media → login → debería mostrar dashboard n8n con cert válido

## Paso 5 — Instalar community node de Upload-Post (~5 min)

n8n self-hosted permite community nodes sin restricciones. Para A10 Publisher:

1. n8n UI → Settings (icono engranaje arriba-derecha) → Community Nodes
2. Click "Install"
3. Package name: `n8n-nodes-upload-post`
4. Click "Install" — espera 30-60 segundos
5. Refrescar n8n → buscar "Upload-Post" en el panel de nodes — debería aparecer
6. **Repetir para otros community nodes** que necesitemos en Fase 1+:
   - `n8n-nodes-blotato` (Plan B publisher, ADR-014)
   - `n8n-nodes-supabase` (opcional — el Supabase oficial viene incluido)

## Paso 6 — Importar fase0.json (~5 min)

1. Descargar `infra/n8n/fase0.json` del repo:
   ```bash
   wget https://raw.githubusercontent.com/<tu-repo>/project-autopilot/main/infra/n8n/fase0.json
   ```
   O simplemente copy-paste el contenido desde GitHub UI.
2. En n8n UI: click **"+"** arriba → "Import from File" → seleccionar `fase0.json`
3. n8n importa el workflow → te advierte que las credentials están con placeholders `REPLACE_ME`

## Paso 7 — Configurar credentials (~15 min)

### Anthropic API

1. Settings → Credentials → "Add Credential"
2. Type: **Anthropic API**
3. API Key: pegá la key de https://console.anthropic.com/settings/keys
4. Name: "Anthropic API"
5. Save
6. Vuelve al workflow `fase0` → click en cualquier node Anthropic Chat Model → "Credential to connect with" → seleccionar la recién creada

### Telegram Bot

1. Crear el bot:
   - Abrir Telegram → buscar `@BotFather` → `/newbot`
   - Nombre: "AI Brief LATAM Preview"
   - Username: `@aibrief_latam_bot` (o similar disponible)
   - BotFather te devuelve el **token** (formato `1234567890:AABBccDD...`)
2. Obtener tu chat_id:
   - Mandale CUALQUIER mensaje al bot (necesario para que `getUpdates` funcione)
   - En el navegador: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   - Buscar `"chat":{"id": <NUMERO>}` — ese es tu chat_id
3. n8n → Settings → Credentials → "Add Credential" → "Telegram"
4. Access Token: pegá el bot token
5. Name: "Telegram Bot AI Brief LATAM"
6. Save
7. En el node "Telegram — Send Preview" del workflow:
   - Credential: seleccionar la recién creada
   - Chat ID: pegá tu chat_id (reemplazar `REPLACE_ME_CHAT_ID`)

## Paso 8 — Ejecutar Fase 0 smoke test (~5 min)

1. En el workflow `fase0`, click "Execute Workflow" (botón abajo)
2. Esperar 30-90 segundos (RSS fetch + 2 LLM calls + Telegram send)
3. Si todo OK: deberías recibir un brief en Telegram con el formato del POST_STANDARD
4. Si error en algún node: click el node con el ícono rojo → ver error detallado

### Troubleshooting común

| Error | Causa | Fix |
|---|---|---|
| `RSS Read failed` | OpenAI Blog feed temporalmente caído | Reintentar; o cambiar URL a backup en el Set node |
| `Anthropic 401` | API key mal copiada | Re-verificar la key en Anthropic console |
| `Anthropic insufficient_quota` | Sin crédito en cuenta Anthropic | Agregar $10-20 USD en https://console.anthropic.com/settings/billing |
| `Structured Output Parser failed` | El LLM devolvió markdown wrapping | Agregar Output Parser Autofixing — n8n lo hace en 2 clicks |
| `Telegram chat_id invalid` | Chat ID mal copiado o el bot no escribió primero | Mandar de nuevo un msg al bot, refrescar getUpdates |

## Paso 9 — Backup automático (~10 min)

Sin esto, si el VPS muere, perdemos todo. Setup obligatorio.

1. SSH al VPS (Web SSH desde Hostinger panel)
2. Crear directorio backup:
   ```bash
   mkdir -p /opt/backups/n8n
   ```
3. Crear script de backup:
   ```bash
   cat > /opt/backups/backup.sh <<'EOF'
   #!/bin/bash
   DATE=$(date +%Y-%m-%d_%H%M%S)
   BACKUP_DIR="/opt/backups/n8n"

   # Backup de la base de datos SQLite de n8n
   docker exec n8n cp /home/node/.n8n/database.sqlite /tmp/db_backup.sqlite
   docker cp n8n:/tmp/db_backup.sqlite "$BACKUP_DIR/n8n_db_$DATE.sqlite"

   # Backup de los workflows exportados como JSON
   docker exec n8n n8n export:workflow --all --output=/tmp/workflows.json
   docker cp n8n:/tmp/workflows.json "$BACKUP_DIR/workflows_$DATE.json"

   # Retención: mantener últimos 30 días
   find "$BACKUP_DIR" -type f -mtime +30 -delete

   echo "Backup completado: $DATE"
   EOF
   chmod +x /opt/backups/backup.sh
   ```
4. Programar cron diario a las 4 AM:
   ```bash
   (crontab -l 2>/dev/null; echo "0 4 * * * /opt/backups/backup.sh >> /var/log/n8n-backup.log 2>&1") | crontab -
   ```
5. **Adicional opcional pero recomendado:** rsync diario de `/opt/backups/n8n/` a un bucket S3 o Backblaze B2 (~$0.005/GB/mo). Si Hostinger entero muere, el backup vive afuera.

## Paso 10 — Configurar monitoreo básico (~5 min)

1. En el panel Hostinger → tu VPS → "Monitoring" — activar default monitoring (gratis):
   - CPU usage alerts >85%
   - RAM usage alerts >90%
   - Disk usage alerts >80%
   - Uptime monitor
2. Notificaciones por email a aibrieflatam.media@gmail.com
3. Opcional avanzado: integrar Uptime Robot (free tier 50 monitors / 5min interval) apuntando a `https://n8n.aibrieflatam.media/healthz`

## Mantenimiento mensual (~30 min/mes)

| Tarea | Frecuencia | Cómo |
|---|---|---|
| Update n8n a última versión | ~mensual | SSH → `cd /opt/n8n && docker-compose pull && docker-compose up -d` |
| Verificar backups | semanal | SSH → `ls -lh /opt/backups/n8n/` — debería tener 1 archivo nuevo por día |
| Update OS packages | trimestral | SSH → `sudo apt update && sudo apt upgrade -y` (con cuidado, después de backup) |
| Renovar dominio | anual | Hostinger/Namecheap email recordatorio |
| Renovar SSL | automático | Let's Encrypt renew automático via cron |
| Review costos | mensual | Hostinger dashboard → billing |

## Plan de recuperación de desastre

Si el VPS muere completamente:

1. **Provisionar VPS nuevo** (Hostinger u otro proveedor): 15 min.
2. **Aplicar template n8n** o instalar Docker + docker-compose manual: 15 min.
3. **Restaurar backup desde S3/B2:**
   ```bash
   wget https://s3.../n8n_db_<latest>.sqlite
   docker cp n8n_db_<latest>.sqlite n8n:/home/node/.n8n/database.sqlite
   docker restart n8n
   ```
4. **Re-configurar credenciales** (Anthropic, Telegram, Upload-Post — los tokens viven encriptados en la DB, pero require master key reset si la DB cambió de servidor).
5. **Apuntar DNS** del subdominio al IP nuevo: 5-30 min propagación.

**Tiempo total worst-case:** 60-90 min de downtime. Aceptable para una media property de bootstrap.

## Costos resumen

| Item | Costo | Frecuencia |
|---|---:|---|
| Hostinger KVM2 (24-mo plan) | $6.49 | mensual |
| Dominio (Namecheap/Hostinger) | ~$12 | anual ($1/mo amortizado) |
| Backup externo S3/B2 (opcional) | ~$0.50 | mensual (10 GB) |
| **Total infraestructura** | **~$8/mo** | |

vs n8n cloud Pro $60/mo = ahorro **$52/mo** = **$624/año**.

## Open items

- **Manuel:** confirmar ADR-015 antes de ejecutar este runbook.
- **Domain decision:** ¿cuál registrar? (OPEN_QUESTIONS L).
- **Backup externo S3 vs B2:** decidir solo si el S3 free tier (5 GB) no alcanza. Para Fase 1 alcanza.
