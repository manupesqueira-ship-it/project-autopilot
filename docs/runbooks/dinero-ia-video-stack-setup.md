# Runbook — Setup Video Stack Dinero IA (ElevenLabs + Seedance + Supabase Storage)

**Fecha:** 2026-06-01
**Status:** ready-to-execute paso a paso
**Audiencia:** Manuel
**Tiempo total estimado:** 60-90 min secuencial (se puede partir en 2 sesiones)
**Pre-requisito:** Fase 0 smoke test funcionando + onboarding técnico base completo (Anthropic + Telegram + n8n cloud)

> Este runbook activa el stack para el pipeline video v2 (workflows `produce-v2` + `fanout-v2`). NO arranca producción todavía — solo deja todo configurado para que cuando hagamos el smoke test video end-to-end, funcione.

---

## Pre-checklist

Antes de arrancar, confirmar:

- [ ] Fase 0 smoke test corrió OK con preview en Telegram (commit `a5d7bec` confirmó funcionamiento)
- [ ] Decidiste el rango de costo aceptado (~$270-440/mo Fase 1 producción)
- [ ] Estás OK con voice library al inicio (no esperás a grabar tu voz primero)

---

## Bloque 1 — Supabase Free (15 min)

Necesario para storage de assets (keyframes, voice, music, video final).

### 1.1 Crear cuenta

1. Ir a [supabase.com](https://supabase.com)
2. **Sign up** con `aibrieflatam.media@gmail.com`
3. Confirmar email
4. **Create new project** → name: `dinero-ia` → región: **US East (North Virginia)** (más cerca de Anthropic + OpenAI) → plan: **Free**
5. **Database password:** generá uno largo (32+ chars) y guardalo en password manager — lo vas a usar para SQL admin

### 1.2 Aplicar migrations

1. En Supabase Dashboard → sidebar **SQL Editor**
2. **+ New query**
3. Pegá el contenido de `infra/supabase/migrations/001_initial.sql` → **Run**
4. Verificá que dice "Success" sin errores
5. **+ New query** otra vez
6. Pegá el contenido de `infra/supabase/migrations/002_video_assets.sql` → **Run**
7. Verificá Success

### 1.3 Verificar tablas creadas

En sidebar **Table Editor** vas a ver:
- `dedup_history`
- `briefs_pending`
- `posts_published`
- `compliance_log`
- `costs_log`
- `metrics_daily`
- `outreach_log`
- `audit_log`
- `assets_storage` (de migration 002)
- `music_usage_log`
- `voice_clone_versions` (con 1 row seed)

### 1.4 Crear Storage bucket

1. Sidebar **Storage** → **Create bucket**
2. Name: `dinero-ia-assets`
3. **Privacy:** Private (NO public)
4. **Click Create**
5. Dentro del bucket, **New folder** → crear: `keyframes`, `video_segments`, `voice`, `music`, `subtitles`, `final`, `covers`, `music-library`

### 1.5 Guardar credentials

Sidebar **Settings → API**:
- Copiá **URL** (formato: `https://xxxx.supabase.co`)
- Copiá **service_role key** (la SECRET, no la anon)

Agregá al `.env`:
```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJxxxxx...
```

---

## Bloque 2 — ElevenLabs Creator (15 min)

### 2.1 Crear cuenta

1. Ir a [elevenlabs.io](https://elevenlabs.io)
2. **Sign up** con `aibrieflatam.media@gmail.com`
3. Plan: **Creator** ($22/mo) — primer mes 50% off ($11) si aplica deal
4. Confirmar email

### 2.2 Seleccionar voz library (Fase 1.0)

1. En el dashboard → **Voices**
2. Buscar **"Adam"** o **"Antoni"** o **"Drew"** (multilingual masculine)
3. **Test** cada uno con este texto:
   ```
   Subí mi extracto a Claude. Encontró cuatro suscripciones fantasma por cuarenta mil pesos mexicanos.
   ```
4. Comparar pronunciación de "Claude" (debe sonar "klod"), pausas, energía
5. Elegir el que más se acerca al tone Dinero IA (profesor cálido + autoridad pausada)
6. **Copiá el Voice ID** del seleccionado (lo ves en la URL o panel del voice)
7. Anotalo

### 2.3 Update voice_clone_versions en Supabase

En Supabase SQL Editor:
```sql
UPDATE voice_clone_versions
SET voice_id = 'TU_VOICE_ID_REAL_AQUI',
    voice_name = 'Adam (o Antoni o Drew) - ElevenLabs library Fase 1.0'
WHERE active = true;
```

### 2.4 Generar API key

1. **Settings → API Keys**
2. **+ New Key**
3. Name: `dinero-ia-n8n`
4. Permissions: **Speech Synthesis + Voice Library** (no necesitás Audio Native)
5. **Create** → copiá la key

Agregá al `.env`:
```
ELEVENLABS_API_KEY=sk_xxxxx
```

---

## Bloque 3 — Seedance 2.0 (15 min)

> **Nota:** Seedance 2.0 está cambiando. Si el flujo de API difiere de lo descrito, ajustar en el workflow `produce-v2.json` node "A8b Video Gen".

### 3.1 Crear cuenta

1. Ir a [seedance.com](https://seedance.com) (verificar URL actual)
2. **Sign up** con `aibrieflatam.media@gmail.com`
3. Plan: **Creator** (~$30-50/mo dependiendo del modelo de pricing actual)
4. Si pricing es per-video: cargar **$50 USD initial credits** (cubre ~30-35 videos a $1.50)

### 3.2 Verificar acceso API

1. **Settings → API**
2. Generar API key
3. Verificar docs en `docs.seedance.com` (URL exacta puede variar) para confirmar endpoint:
   - Endpoint esperado: `POST https://api.seedance.com/v1/generations` (puede variar)
   - Auth: `Authorization: Bearer SEEDANCE_API_KEY`
4. Algunos providers tienen polling de status — verificar si Seedance devuelve URL directa o requiere polling

### 3.3 Test rápido

Test directo en su playground (no via API todavía):
1. Subí una imagen 1080×1920 dark mode con texto
2. Prompt: "subtle scale-in animation, editorial style"
3. Duration: 3 segundos
4. Generate
5. Si el output cumple specs VISUAL.md §5 (animación sutil, no glitch) → OK
6. Si no rinde → considerar alternativas: Runway Gen-3, Kling, Luma

### 3.4 Guardar credentials

Agregá al `.env`:
```
SEEDANCE_API_KEY=sk_xxxxx
```

---

## Bloque 4 — Music stack (15 min)

### 4.1 Epidemic Sound (recomendado)

1. Ir a [epidemicsound.com](https://epidemicsound.com)
2. **Try free** → 30 días free trial
3. **Personal Subscription** ($9-13/mo después del trial)
4. Crear cuenta con `aibrieflatam.media@gmail.com`

### 4.2 Curar playlist "Dinero IA — Lo-Fi"

1. En el dashboard, **Browse → Filter**:
   - **Genres:** Lo-Fi, Chillhop, Cinematic Electronic
   - **Moods:** Calm, Focused, Confident, Hopeful, Curious
   - **Tempo:** 70-85 BPM
   - **Vocals:** No vocals (filtro estricto)
   - **Length:** 60-180 seconds
2. Escuchá tracks y favoritea 30-40 que cumplan VISUAL.md §3 (lo-fi cálido, no EDM, no reggaeton)
3. Organizar en colecciones por mood:
   - **calm_confident** (10-12 tracks)
   - **optimistic_warm** (8-10 tracks)
   - **tech_curious** (5-7 tracks)
   - **steady_focus** (5-7 tracks)
   - **other moods** según necesidad

### 4.3 Descargar curated library a Supabase Storage

Por cada track:
1. Download MP3 desde Epidemic
2. Subir a Supabase Storage bucket: `dinero-ia-assets/music-library/{mood_tag}/{track_id}.mp3`
3. Registrar en una nota: track_id, mood, BPM (para query interno)

**Alternativa:** crear función custom `select_music_track(mood_tag, min_bpm, max_bpm)` en Supabase que el workflow A8d query. Si querés que arme esa función SQL, decímelo y la agrego a migration 003.

---

## Bloque 5 — Webhook URLs en n8n cloud (10 min)

Los workflows `produce-v2` y `fanout-v2` se comunican via webhooks. Necesitamos las URLs activas.

### 5.1 Importar workflows nuevos

1. En n8n cloud → **Workflows → + Add workflow → Import from file**
2. Importar en orden:
   - `infra/n8n/dinero-ia-fase1-produce-v2.json`
   - `infra/n8n/dinero-ia-fase1-fanout.json` (el existente, lo modificamos en próxima sesión para video)
3. NO activar todavía (toggle OFF)

### 5.2 Obtener webhook URLs

Para cada workflow:
1. Abrir el workflow
2. Click en el nodo **"Webhook trigger"**
3. Copiar la **Production URL** (NO test URL)
4. Anotar:
   - `N8N_PRODUCE_WEBHOOK_URL`
   - `N8N_FANOUT_WEBHOOK_URL`

### 5.3 Generar webhook secret

```bash
openssl rand -base64 32
```

(o cualquier string random largo de 32+ chars)

### 5.4 Cargar env vars en n8n cloud

En n8n cloud → **Settings → Variables** (o **Environment Variables** en algunas versions):

Agregá todas las variables del `.env` actualizado:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `ANTHROPIC_API_KEY` (ya está en credential, pero también como env var)
- `OPENAI_API_KEY`
- `ELEVENLABS_API_KEY`
- `SEEDANCE_API_KEY`
- `TELEGRAM_CHAT_ID`
- `N8N_PRODUCE_WEBHOOK_URL`
- `N8N_FANOUT_WEBHOOK_URL`
- `N8N_WEBHOOK_SECRET`
- `BEEHIIV_API_KEY` (Fase 1 cuando actives Beehiiv)
- `BEEHIIV_PUBLICATION_ID`
- `CONTENT_STUDIO_API_KEY` (Fase 1 cuando actives)
- `BLOTATO_API_KEY` (opcional, Fase 1)

### 5.5 Asignar credentials a nodos nuevos

En el workflow `produce-v2`:
- Cada nodo Anthropic → asignar **Anthropic Account** credential
- Nodos HTTP que usan env vars no necesitan credential explícita (usan env vars)

---

## Bloque 6 — Smoke test video pipeline end-to-end (próxima sesión)

**NO ejecutar este bloque ahora.** Se hace en sesión separada cuando todo lo anterior esté listo.

Cuando hagamos el smoke test:
1. Trigger manual del workflow `publish-v2` (que vamos a crear próxima sesión modificando el actual `publish.json`)
2. Verificar que pasa por: RSS → scoring → A3 brief → A4 fact-check → A9 compliance → Telegram HITL preview con 4 botones
3. Aprobar en Telegram → trigger `produce-v2`
4. Verificar A7 script → A5 visual → A6 audio → A8a image gen → A8b video gen → A8c voice → A8d music → A8e compositor plan
5. Verificar todos los assets en Supabase Storage
6. Revisar quality output → iterar prompts si necesario

---

## Resumen — credentials que vas a tener al final

En `.env` local:
```
ANTHROPIC_API_KEY=sk-ant-...        ✅ ya tenés
TELEGRAM_BOT_TOKEN=...              ✅ ya tenés
TELEGRAM_CHAT_ID=...                ✅ ya tenés
SUPABASE_URL=https://xxx.supabase.co   ← bloque 1
SUPABASE_SERVICE_KEY=eyJ...         ← bloque 1
OPENAI_API_KEY=sk-proj-...          ← bloque 2 si activas
ELEVENLABS_API_KEY=sk_...           ← bloque 2
SEEDANCE_API_KEY=sk_...             ← bloque 3
N8N_PRODUCE_WEBHOOK_URL=https://... ← bloque 5
N8N_FANOUT_WEBHOOK_URL=https://...  ← bloque 5
N8N_WEBHOOK_SECRET=random_string    ← bloque 5
BEEHIIV_API_KEY=...                 ← Fase 1 (cuando actives Beehiiv para newsletter)
BEEHIIV_PUBLICATION_ID=...
CONTENT_STUDIO_API_KEY=...          ← Fase 1
BLOTATO_API_KEY=...                 ← Fase 1 opcional (carousels alternativos)
```

En n8n cloud Credentials:
- `Anthropic Account` ✅ ya tenés
- `Telegram - Dinero IA` ✅ ya tenés

(Los nuevos servicios — ElevenLabs, Seedance, Supabase — los usamos via env vars + HTTP Request nodes, no via credentials nativas porque n8n cloud no tiene credentials específicas de esos services todavía)

---

## Costos mensuales (estimados al activar todo)

| Servicio | $/mes | Cuándo se activa |
|---|---|---|
| Anthropic API (más volumen 2-3/día con A5+A6+A7) | $80-130 | Ya |
| OpenAI gpt-image-2 (60-90 piezas × 5-8 keyframes) | $15-25 | Bloque 2 |
| ElevenLabs Creator | $11-22 (1er mes deal) | Bloque 2 |
| Seedance 2.0 (60-90 videos × $1.50) | $90-135 | Bloque 3 |
| Epidemic Sound | $9-13 | Bloque 4 |
| Supabase Free | $0 (hasta limits) | Bloque 1 |
| n8n cloud (probable upgrade Starter post-trial) | $0-30 | Cuando trial acabe |
| **Total al activar todo** | **$205-355/mo** | (sin Beehiiv ni ContentStudio todavía) |

Cuando sumes Beehiiv ($0-43) + ContentStudio ($19) + Blotato opcional ($29) = **~$270-440/mo** rango total Fase 1.

---

## Si algo no funciona — escalation

| Problema | Acción inicial | Siguiente paso |
|---|---|---|
| Supabase migration falla | Copiar el error exacto, revisar sintaxis | Pedirme el debug |
| ElevenLabs voice library no encuentra voces ES neutro | Probar alternativas: Spanish voices section | Considerar fish.audio como alternativa |
| Seedance no animación dec calidad | Probar otros prompts | Considerar alternativas (Runway, Kling, Luma) |
| Epidemic Sound no tiene catálogo lo-fi LATAM-friendly | Probar Artlist | Music library local con Pixabay Music free |
| n8n cloud env vars no se reconocen en workflow | Restart workflow después de agregar vars | Verificar sintaxis `{{ $env.VAR_NAME }}` |
| Webhook URLs no funcionan entre workflows | Verificar production URL vs test URL | Verificar X-Webhook-Secret coincide |

---

## Tiempo total esperado

| Bloque | Tiempo |
|---|---|
| 1 — Supabase | 15 min |
| 2 — ElevenLabs | 15 min |
| 3 — Seedance | 15 min |
| 4 — Music stack + curated library | 15-30 min (depende de cuántos tracks favoriteás) |
| 5 — n8n webhooks + env vars | 10 min |
| **Total** | **70-85 min** |

Podés hacerlo en una sola sesión o partido en 2-3 sentadas (cada bloque es independiente, podés hacer Supabase un día y ElevenLabs otro).
