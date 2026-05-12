-- ─────────────────────────────────────────────────────────────────────
-- AI Brief LATAM — Initial Supabase schema
-- ─────────────────────────────────────────────────────────────────────
-- Migration: 001_initial.sql
-- Created: 2026-05-12
-- Purpose: schema para Fase 1 (Fase 0 NO necesita esto — corre con
--          Manual Trigger y sin persistencia). Aplicable cuando Manuel
--          cree la cuenta Supabase y haga el primer link.
--
-- Tablas:
--   dedup_history    — items procesados (anti-duplicación 30 días)
--   briefs           — todos los briefs generados (aprobados + rechazados)
--   posts_published  — qué publicamos, dónde, cuándo, con métricas
--   costs            — tokens consumidos por agent (analytics + budget)
--   compliance_log   — toda invocación de A9 (audit trail + analytics)
--
-- Storage bucket (creado aparte via dashboard o API):
--   assets — imágenes de gpt-image-2, videos de Seedance, audio ElevenLabs
--
-- Convenciones:
--   - PRIMARY KEY = UUID (gen_random_uuid()) en todas las tablas
--   - URLs únicas para dedup vía UNIQUE constraint
--   - JSONB para campos con schema variable (brief_content, metrics)
--   - timestamptz con DEFAULT now() para todos los timestamps
--   - Índices en columnas usadas por queries del workflow
-- ─────────────────────────────────────────────────────────────────────

-- Habilitar extensión para uuid v4 si no está
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: dedup_history
-- ─────────────────────────────────────────────────────────────────────
-- Función: evitar procesar el mismo item RSS dos veces.
-- El workflow hace UPSERT por url_hash; si ya existe, descarta el item.
-- Retención: 30 días (cron job o manual cleanup).
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE dedup_history (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  url            TEXT NOT NULL UNIQUE,
  url_hash       TEXT NOT NULL UNIQUE,  -- SHA-256 de url normalizada, indexada
  title          TEXT,
  source_name    TEXT NOT NULL,  -- ej: "OpenAI Blog", "TechCrunch AI"
  processed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  outcome        TEXT NOT NULL DEFAULT 'pending'
                 CHECK (outcome IN ('pending', 'scored', 'briefed', 'published', 'rejected', 'failed'))
);

CREATE INDEX idx_dedup_url_hash ON dedup_history(url_hash);
CREATE INDEX idx_dedup_processed_at ON dedup_history(processed_at);
CREATE INDEX idx_dedup_outcome ON dedup_history(outcome);

COMMENT ON TABLE dedup_history IS 'Anti-duplicación: cada URL procesada queda registrada 30d para no re-procesar';
COMMENT ON COLUMN dedup_history.url_hash IS 'SHA-256 de URL normalizada (lowercased, sin trailing slash, sin query params irrelevantes)';
COMMENT ON COLUMN dedup_history.outcome IS 'Estado final del item: pending=acabamos de verlo, scored=A2 corrió, briefed=A3 corrió, published=A10 OK, rejected=descartado, failed=error técnico';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: briefs
-- ─────────────────────────────────────────────────────────────────────
-- Función: persistencia de TODOS los briefs generados (aprobados +
-- rechazados). Audit trail completo. El A11 Editor lee de acá para
-- aplicar feedback sin re-generar.
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE briefs (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_dedup_id      UUID REFERENCES dedup_history(id) ON DELETE SET NULL,
  source_url           TEXT NOT NULL,
  source_name          TEXT NOT NULL,
  title                TEXT NOT NULL,
  signal_score         NUMERIC(5,2),  -- ej: 78.50, sumatoria de A2
  classification       TEXT CHECK (classification IN ('strong', 'consider', 'discard', 'shortlist')),

  -- Contenidos generados (cada uno es JSONB para flex schema)
  brief_content        JSONB NOT NULL,   -- output de A3 Editorial completo
  fact_check_result    JSONB,            -- output de A4 (puede ser NULL si no llegó a fact-check)
  carousel_content     JSONB,            -- output de A7 (carousel + caption + alternates)
  newsletter_content   JSONB,            -- output de A8d (Intro + Top + Quick Hits + Subject)
  reel_script          JSONB,            -- output de A7 (reel_script — Fase 2)
  compliance_result    JSONB,            -- último output de A9 compliance

  -- HITL tracking
  telegram_message_id  BIGINT,           -- ID del mensaje preview enviado a Telegram
  approval_status      TEXT NOT NULL DEFAULT 'pending'
                       CHECK (approval_status IN ('pending', 'approved', 'rejected', 'edited')),
  manuel_feedback      TEXT,             -- texto libre del feedback humano
  edit_iterations      INTEGER NOT NULL DEFAULT 0,  -- cuántas veces pasó por A11

  -- Timestamps
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  approved_at          TIMESTAMPTZ,
  published_at         TIMESTAMPTZ
);

CREATE INDEX idx_briefs_source_url ON briefs(source_url);
CREATE INDEX idx_briefs_classification ON briefs(classification);
CREATE INDEX idx_briefs_approval_status ON briefs(approval_status);
CREATE INDEX idx_briefs_created_at ON briefs(created_at DESC);
CREATE INDEX idx_briefs_brief_content_gin ON briefs USING GIN (brief_content);

COMMENT ON TABLE briefs IS 'Todos los briefs generados — aprobados y rechazados, audit trail completo';
COMMENT ON COLUMN briefs.brief_content IS 'JSON de A3 Editorial: title, que_paso, por_que_importa, angulo_latam, hook_tentativo, datos_clave, fuentes, etc.';
COMMENT ON COLUMN briefs.edit_iterations IS 'Counter de cuántas veces A11 editó este brief antes de aprobar/rechazar. Max=3 antes de descarte.';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: posts_published
-- ─────────────────────────────────────────────────────────────────────
-- Función: tracking de qué publicamos, en qué plataforma, con qué
-- métricas. Una fila por (brief_id, platform) — un brief puede generar
-- 3 posts (IG carousel + TikTok + newsletter section).
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE posts_published (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id       UUID NOT NULL REFERENCES briefs(id) ON DELETE CASCADE,
  platform       TEXT NOT NULL CHECK (platform IN ('instagram', 'tiktok', 'newsletter', 'linkedin')),
  post_url       TEXT,                  -- URL pública del post
  external_id    TEXT,                  -- ID del post en la plataforma (IG media_id, TikTok video_id)
  content_type   TEXT CHECK (content_type IN ('carousel', 'reel', 'static', 'newsletter')),

  -- Métricas (poblado por cron job posterior, no por workflow de publish)
  metrics        JSONB,                 -- {likes, comments, shares, saves, reach, impressions, ctr}
  metrics_fetched_at TIMESTAMPTZ,

  -- Publicación
  publisher_used TEXT,                  -- 'blotato' | 'upload-post' | 'buffer' | 'meta-graph' | 'manual'
  publisher_response JSONB,             -- raw response del publisher API para debug
  published_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Constraint: un brief no publica 2 veces a la misma plataforma
  UNIQUE (brief_id, platform)
);

CREATE INDEX idx_posts_brief_id ON posts_published(brief_id);
CREATE INDEX idx_posts_platform ON posts_published(platform);
CREATE INDEX idx_posts_published_at ON posts_published(published_at DESC);

COMMENT ON TABLE posts_published IS 'Una fila por (brief, plataforma) — 1 brief típicamente genera 3 posts (IG + TikTok + newsletter)';
COMMENT ON COLUMN posts_published.metrics IS 'JSON: likes, comments, shares, saves, reach, impressions, ctr — poblado por cron analytics, no por publish workflow';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: costs
-- ─────────────────────────────────────────────────────────────────────
-- Función: monitorear costo por agent y por modelo. Útil para alertar
-- si el costo mensual supera el budget proyectado.
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE costs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id      UUID REFERENCES briefs(id) ON DELETE SET NULL,
  agent_name    TEXT NOT NULL,         -- 'A2', 'A3', 'A4', 'A7', 'A9', 'A11', 'A8a-gpt-image-2', 'A6-ElevenLabs', ...
  provider      TEXT NOT NULL CHECK (provider IN ('anthropic', 'openai', 'elevenlabs', 'seedance', 'tavily', 'perplexity')),
  model         TEXT NOT NULL,         -- 'claude-opus-4', 'claude-sonnet-4-5', 'gpt-image-2', 'voice-clone-v2', ...

  -- Tokens / units consumidos
  input_tokens   INTEGER,
  output_tokens  INTEGER,
  images_generated INTEGER,            -- para gpt-image-2 / Seedance
  audio_seconds  INTEGER,              -- para ElevenLabs
  web_searches   INTEGER,              -- para Claude web_search tool

  -- Costo en USD (calculado en el workflow node Code antes de insertar)
  cost_usd      NUMERIC(10,6) NOT NULL,

  -- Timestamps
  timestamp     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_costs_brief_id ON costs(brief_id);
CREATE INDEX idx_costs_agent_name ON costs(agent_name);
CREATE INDEX idx_costs_provider ON costs(provider);
CREATE INDEX idx_costs_timestamp ON costs(timestamp DESC);

COMMENT ON TABLE costs IS 'Costo por invocación de agent — para analytics mensual y alertas de budget';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: compliance_log
-- ─────────────────────────────────────────────────────────────────────
-- Función: audit trail de TODA invocación de A9 Compliance. Cada regla
-- evaluada queda registrada. Útil si Meta cuestiona algo y necesitamos
-- demostrar que hicimos due diligence.
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE compliance_log (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id       UUID NOT NULL REFERENCES briefs(id) ON DELETE CASCADE,
  content_type   TEXT NOT NULL CHECK (content_type IN ('carousel_caption', 'newsletter', 'reel_script', 'tiktok_caption')),
  rule           TEXT NOT NULL,         -- nombre de la regla (ej: "no_financial_claims_without_disclaimer")
  rule_number    INTEGER,               -- 1-15 según Anexo D + brand rules
  passed         BOOLEAN NOT NULL,
  severity       TEXT NOT NULL CHECK (severity IN ('block', 'warning', 'info')),
  detail         TEXT,                  -- explicación del check
  suggested_fix  TEXT,                  -- si falló, qué cambio sugerir
  verdict_global TEXT NOT NULL CHECK (verdict_global IN ('approved', 'approved_with_warnings', 'blocked')),
  timestamp      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_compliance_brief_id ON compliance_log(brief_id);
CREATE INDEX idx_compliance_rule ON compliance_log(rule);
CREATE INDEX idx_compliance_passed ON compliance_log(passed);
CREATE INDEX idx_compliance_verdict ON compliance_log(verdict_global);
CREATE INDEX idx_compliance_timestamp ON compliance_log(timestamp DESC);

COMMENT ON TABLE compliance_log IS 'Audit trail de A9 — una fila por (brief, content_type, rule). Si Meta nos cuestiona, esto demuestra due diligence';

-- ─────────────────────────────────────────────────────────────────────
-- Views convenience (analytics queries comunes)
-- ─────────────────────────────────────────────────────────────────────

-- Vista: stats diarios de pipeline
CREATE OR REPLACE VIEW daily_pipeline_stats AS
SELECT
  DATE(b.created_at) AS day,
  COUNT(*) FILTER (WHERE b.approval_status = 'pending')   AS pending,
  COUNT(*) FILTER (WHERE b.approval_status = 'approved')  AS approved,
  COUNT(*) FILTER (WHERE b.approval_status = 'rejected')  AS rejected,
  COUNT(*) FILTER (WHERE b.approval_status = 'edited')    AS edited,
  AVG(b.signal_score)                                      AS avg_score,
  AVG(b.edit_iterations)                                   AS avg_edits_per_brief
FROM briefs b
GROUP BY DATE(b.created_at)
ORDER BY day DESC;

-- Vista: costo mensual por provider
CREATE OR REPLACE VIEW monthly_costs_by_provider AS
SELECT
  DATE_TRUNC('month', timestamp)::DATE AS month,
  provider,
  COUNT(*)                              AS invocations,
  SUM(cost_usd)                         AS total_cost_usd,
  AVG(cost_usd)                         AS avg_cost_per_invocation
FROM costs
GROUP BY DATE_TRUNC('month', timestamp), provider
ORDER BY month DESC, total_cost_usd DESC;

-- ─────────────────────────────────────────────────────────────────────
-- Storage bucket (NO se crea por SQL — se crea via Supabase Dashboard
-- o API. Documentación para Manuel:)
-- ─────────────────────────────────────────────────────────────────────
-- Bucket name: assets
-- Privacy: private (signed URLs cuando publishing externo lo necesite)
-- Public CDN: NO (queremos control de acceso)
-- Folder structure propuesta:
--   /images/{brief_id}/slide_{n}.png      -- 5-7 slides de gpt-image-2
--   /images/{brief_id}/cover.png          -- cover hero
--   /audio/{brief_id}/reel.mp3            -- ElevenLabs voice clone output (Fase 2)
--   /video/{brief_id}/reel.mp4            -- Seedance output (Fase 2)
--   /exports/{brief_id}/instagram.zip     -- bundle final para Buffer/Blotato
-- ─────────────────────────────────────────────────────────────────────
