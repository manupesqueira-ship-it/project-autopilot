-- ─────────────────────────────────────────────────────────────────────
-- Dinero IA — Initial Supabase schema (v2 post-ADR-017)
-- ─────────────────────────────────────────────────────────────────────
-- Migration: 001_initial.sql
-- Created: 2026-05-12 (v1) / 2026-05-30 (v2 Dinero IA pivot)
-- Purpose: schema para Fase 1+ (Fase 0 NO necesita esto — corre con
--          Manual Trigger y sin persistencia). Aplicable cuando Manuel
--          cree la cuenta Supabase y haga el primer link n8n ↔ Supabase.
--
-- Tablas core:
--   dedup_history    — items procesados (anti-duplicación 30 días)
--   briefs_pending   — TODOS los briefs generados (incluye HITL state)
--   posts_published  — qué publicamos, dónde, cuándo, con métricas
--   compliance_log   — toda invocación de A9 (audit trail regulatorio)
--   costs_log        — tokens consumidos por agent (analytics + budget)
--   metrics_daily    — agregados cross-platform (engagement diario)
--   outreach_log     — Inflection Lever Track (5 outreaches/sem)
--   audit_log        — event sourcing genérico para eventos del workflow
--
-- Storage bucket (creado aparte via dashboard o API):
--   assets — imágenes de Blotato/gpt-image-2, videos Seedance, audio ElevenLabs
--
-- Convenciones:
--   - PRIMARY KEY = UUID (gen_random_uuid()) en todas las tablas
--   - URLs únicas para dedup vía UNIQUE constraint
--   - JSONB para campos con schema variable (brief_content, metrics, payload)
--   - timestamptz con DEFAULT now() para todos los timestamps
--   - Índices en columnas usadas por queries del workflow
--   - RLS deshabilitado (Fase 1 single-user; activar si multi-user en Fase 5+)
-- ─────────────────────────────────────────────────────────────────────

-- Habilitar extensión para uuid v4
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: dedup_history
-- ─────────────────────────────────────────────────────────────────────
-- Función: evitar procesar el mismo item RSS dos veces.
-- El workflow hace UPSERT por url_hash; si ya existe, descarta el item.
-- Retención: 30 días (cron cleanup recomendado).
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE dedup_history (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  url            TEXT NOT NULL UNIQUE,
  url_hash       TEXT NOT NULL UNIQUE,
  title          TEXT,
  source_name    TEXT NOT NULL,
  processed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  outcome        TEXT NOT NULL DEFAULT 'pending'
                 CHECK (outcome IN ('pending', 'scored', 'briefed', 'approved', 'published', 'rejected', 'failed'))
);

CREATE INDEX idx_dedup_url_hash ON dedup_history(url_hash);
CREATE INDEX idx_dedup_processed_at ON dedup_history(processed_at);
CREATE INDEX idx_dedup_outcome ON dedup_history(outcome);

COMMENT ON TABLE dedup_history IS 'Anti-duplicación: cada URL procesada queda registrada 30d para no re-procesar';
COMMENT ON COLUMN dedup_history.url_hash IS 'SHA-256 de URL normalizada (lowercased, sin trailing slash, sin query params irrelevantes)';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: briefs_pending
-- ─────────────────────────────────────────────────────────────────────
-- Función: persistencia de TODOS los briefs generados + HITL state.
-- El A11 Editor lee de acá para aplicar feedback sin re-generar A3.
-- El callback handler de Telegram lee/escribe acá según user actions.
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE briefs_pending (
  id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_dedup_id          UUID REFERENCES dedup_history(id) ON DELETE SET NULL,
  source_url               TEXT NOT NULL,
  source_name              TEXT NOT NULL,
  title                    TEXT NOT NULL,
  signal_score             NUMERIC(5,2),
  classification           TEXT CHECK (classification IN ('strong', 'consider', 'discard', 'shortlist')),

  -- Sub-categoría finanzas (post-ADR-017)
  sub_categoria            TEXT CHECK (sub_categoria IN (
    'inversiones', 'presupuesto', 'inflacion', 'impuestos',
    'comparativas', 'retiro', 'crypto', 'bancos', 'seguros', 'otros'
  )),

  -- Contenidos generados (cada uno JSONB para flex schema)
  brief_content            JSONB NOT NULL,
  fact_check_result        JSONB,
  carousel_content         JSONB,
  newsletter_content       JSONB,
  reel_script              JSONB,
  compliance_result        JSONB,

  -- Compliance específicos (denormalizados para queries rápidos)
  disclaimer_requerido     BOOLEAN DEFAULT false,
  disclaimer_texto         TEXT,
  productos_mencionados    TEXT[],
  compliance_verdict       TEXT CHECK (compliance_verdict IN ('approved', 'approved_with_warnings', 'blocked')),

  -- HITL tracking
  telegram_message_id      BIGINT,
  telegram_chat_id         BIGINT,
  approval_status          TEXT NOT NULL DEFAULT 'pending'
                           CHECK (approval_status IN (
                             'pending', 'approved', 'rejected', 'edited',
                             'regenerated', 'published', 'failed_publish',
                             'auto_rejected_timeout'
                           )),
  manuel_feedback          TEXT,
  edit_iterations          INTEGER NOT NULL DEFAULT 0,

  -- Timestamps
  created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
  approved_at              TIMESTAMPTZ,
  published_at             TIMESTAMPTZ,
  expires_at               TIMESTAMPTZ DEFAULT (now() + INTERVAL '8 hours')
);

CREATE INDEX idx_briefs_source_url ON briefs_pending(source_url);
CREATE INDEX idx_briefs_classification ON briefs_pending(classification);
CREATE INDEX idx_briefs_approval_status ON briefs_pending(approval_status);
CREATE INDEX idx_briefs_sub_categoria ON briefs_pending(sub_categoria);
CREATE INDEX idx_briefs_created_at ON briefs_pending(created_at DESC);
CREATE INDEX idx_briefs_expires_at ON briefs_pending(expires_at);
CREATE INDEX idx_briefs_brief_content_gin ON briefs_pending USING GIN (brief_content);

COMMENT ON TABLE briefs_pending IS 'Briefs en estado pending HITL + audit trail completo Dinero IA';
COMMENT ON COLUMN briefs_pending.disclaimer_requerido IS 'Denormalizado de brief_content.disclaimer_requerido para queries rápidos';
COMMENT ON COLUMN briefs_pending.productos_mencionados IS 'Array de productos financieros mencionados (Cocos, IOL, Bitso, etc.) para audit regulatorio';
COMMENT ON COLUMN briefs_pending.expires_at IS 'Timeout HITL: si no hay decisión en 8h, marcar auto_rejected_timeout';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: posts_published
-- ─────────────────────────────────────────────────────────────────────
-- Función: tracking de qué publicamos, en qué plataforma, con qué métricas.
-- Una fila por (brief_id, platform).
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE posts_published (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id            UUID NOT NULL REFERENCES briefs_pending(id) ON DELETE CASCADE,
  platform            TEXT NOT NULL CHECK (platform IN (
    'instagram', 'tiktok', 'newsletter', 'linkedin', 'x', 'threads', 'youtube_shorts'
  )),
  post_url            TEXT,
  external_id         TEXT,
  content_type        TEXT CHECK (content_type IN ('carousel', 'reel', 'static', 'newsletter', 'short_video')),

  -- Métricas (poblado por cron analytics posterior, no por publish workflow)
  metrics             JSONB,
  metrics_fetched_at  TIMESTAMPTZ,

  -- Publicación
  publisher_used      TEXT,
  publisher_response  JSONB,
  publish_status      TEXT NOT NULL DEFAULT 'scheduled'
                      CHECK (publish_status IN ('scheduled', 'published', 'failed', 'retry_pending', 'cancelled')),
  publish_error       TEXT,
  scheduled_at        TIMESTAMPTZ,
  published_at        TIMESTAMPTZ,

  UNIQUE (brief_id, platform)
);

CREATE INDEX idx_posts_brief_id ON posts_published(brief_id);
CREATE INDEX idx_posts_platform ON posts_published(platform);
CREATE INDEX idx_posts_published_at ON posts_published(published_at DESC);
CREATE INDEX idx_posts_publish_status ON posts_published(publish_status);

COMMENT ON TABLE posts_published IS 'Una fila por (brief, plataforma) — un brief típicamente genera 4 posts (IG + TikTok + LinkedIn + newsletter)';
COMMENT ON COLUMN posts_published.metrics IS 'JSON: likes, comments, shares, saves, reach, impressions, watch_time, ctr — poblado por cron analytics diario';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: compliance_log
-- ─────────────────────────────────────────────────────────────────────
-- Función: audit trail de TODA invocación de A9 Compliance (18 reglas
-- post-ADR-017). Cada regla evaluada queda registrada. Útil si CNV/CNBV/
-- SFC pregunta cómo evitamos ser "asesoría no autorizada".
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE compliance_log (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id        UUID NOT NULL REFERENCES briefs_pending(id) ON DELETE CASCADE,
  content_type    TEXT NOT NULL CHECK (content_type IN (
    'brief_editorial', 'carousel_caption', 'newsletter', 'reel_script', 'tiktok_caption', 'ig_caption', 'linkedin_caption'
  )),
  rule            TEXT NOT NULL,
  rule_number     INTEGER CHECK (rule_number BETWEEN 1 AND 18),
  rule_category   TEXT CHECK (rule_category IN (
    'platform_meta_tiktok', 'brand_voice', 'financial_compliance'
  )),
  passed          BOOLEAN NOT NULL,
  severity        TEXT NOT NULL CHECK (severity IN ('block', 'warning', 'info')),
  detail          TEXT,
  suggested_fix   TEXT,
  verdict_global  TEXT NOT NULL CHECK (verdict_global IN ('approved', 'approved_with_warnings', 'blocked')),
  timestamp       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_compliance_brief_id ON compliance_log(brief_id);
CREATE INDEX idx_compliance_rule ON compliance_log(rule);
CREATE INDEX idx_compliance_rule_number ON compliance_log(rule_number);
CREATE INDEX idx_compliance_passed ON compliance_log(passed);
CREATE INDEX idx_compliance_verdict ON compliance_log(verdict_global);
CREATE INDEX idx_compliance_rule_category ON compliance_log(rule_category);
CREATE INDEX idx_compliance_timestamp ON compliance_log(timestamp DESC);

COMMENT ON TABLE compliance_log IS 'Audit trail regulatorio: cada brief paso por las 18 reglas A9. Reglas 16-18 son financieras post-ADR-017.';
COMMENT ON COLUMN compliance_log.rule_category IS 'platform_meta_tiktok=1-7, brand_voice=8-15, financial_compliance=16-18';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: costs_log
-- ─────────────────────────────────────────────────────────────────────
-- Función: monitorear costo por agent y por modelo. Alerta si costo
-- mensual supera budget proyectado (Anthropic ~$25-42/mo Fase 1).
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE costs_log (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id          UUID REFERENCES briefs_pending(id) ON DELETE SET NULL,
  agent_name        TEXT NOT NULL,
  provider          TEXT NOT NULL CHECK (provider IN (
    'anthropic', 'openai', 'elevenlabs', 'seedance', 'tavily', 'perplexity',
    'contentstudio', 'blotato', 'beehiiv'
  )),
  model             TEXT NOT NULL,

  -- Units consumidos
  input_tokens      INTEGER,
  output_tokens     INTEGER,
  images_generated  INTEGER,
  audio_seconds     INTEGER,
  web_searches      INTEGER,
  api_calls         INTEGER DEFAULT 1,

  -- Costo USD
  cost_usd          NUMERIC(10,6) NOT NULL,

  -- Timestamps
  timestamp         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_costs_brief_id ON costs_log(brief_id);
CREATE INDEX idx_costs_agent_name ON costs_log(agent_name);
CREATE INDEX idx_costs_provider ON costs_log(provider);
CREATE INDEX idx_costs_timestamp ON costs_log(timestamp DESC);

COMMENT ON TABLE costs_log IS 'Costo por invocación de agent (LLM) o per-call SaaS — analytics mensual + alertas budget';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: metrics_daily
-- ─────────────────────────────────────────────────────────────────────
-- Función: agregados cross-platform por día. Populado por cron 11pm que
-- consulta ContentStudio + Beehiiv + n8n + costs_log.
-- Used by Telegram daily report 9am del día siguiente.
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE metrics_daily (
  id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  day                      DATE NOT NULL UNIQUE,

  -- Pipeline metrics
  briefs_generated         INTEGER DEFAULT 0,
  briefs_approved          INTEGER DEFAULT 0,
  briefs_rejected          INTEGER DEFAULT 0,
  briefs_blocked_compliance INTEGER DEFAULT 0,
  avg_signal_score         NUMERIC(5,2),

  -- Publishing metrics
  posts_published_ig       INTEGER DEFAULT 0,
  posts_published_tiktok   INTEGER DEFAULT 0,
  posts_published_linkedin INTEGER DEFAULT 0,
  posts_published_newsletter INTEGER DEFAULT 0,
  posts_failed             INTEGER DEFAULT 0,

  -- Engagement metrics (snapshot)
  total_ig_reach           BIGINT DEFAULT 0,
  total_ig_engagement      BIGINT DEFAULT 0,
  total_tiktok_views       BIGINT DEFAULT 0,
  total_tiktok_engagement  BIGINT DEFAULT 0,
  total_linkedin_impressions BIGINT DEFAULT 0,
  newsletter_subs_total    INTEGER DEFAULT 0,
  newsletter_subs_added    INTEGER DEFAULT 0,
  newsletter_open_rate     NUMERIC(5,2),
  newsletter_click_rate    NUMERIC(5,2),

  -- Inflection Lever Track
  outreaches_sent          INTEGER DEFAULT 0,
  outreaches_responses     INTEGER DEFAULT 0,

  -- Cost metrics
  cost_anthropic_usd       NUMERIC(10,4) DEFAULT 0,
  cost_openai_usd          NUMERIC(10,4) DEFAULT 0,
  cost_other_usd           NUMERIC(10,4) DEFAULT 0,
  cost_total_usd           NUMERIC(10,4) DEFAULT 0,

  -- Generated at
  generated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_metrics_daily_day ON metrics_daily(day DESC);

COMMENT ON TABLE metrics_daily IS 'Aggregate diario cross-platform. Populado por cron 11pm. Source para Telegram daily report y dashboards.';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: outreach_log
-- ─────────────────────────────────────────────────────────────────────
-- Función: tracking del Inflection Lever Track. Cada outreach enviado
-- + su status (sent / replied / scheduled / closed / no-response).
-- Si Manuel quiere visibilidad cross-temporal del lever track.
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE outreach_log (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prospect_name      TEXT NOT NULL,
  prospect_handle    TEXT,
  prospect_category  TEXT CHECK (prospect_category IN (
    'creator_finanzas', 'newsletter', 'podcast', 'broker_fintech',
    'founder', 'media', 'newsletter_ia', 'other'
  )),
  channel            TEXT CHECK (channel IN ('dm_ig', 'dm_tiktok', 'dm_linkedin', 'email', 'dm_x', 'other')),
  template_used      TEXT,
  message_text       TEXT,
  sent_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  status             TEXT NOT NULL DEFAULT 'sent'
                     CHECK (status IN ('sent', 'read', 'replied', 'scheduled', 'closed_win', 'closed_lose', 'no_response')),
  response_summary   TEXT,
  followup_count     INTEGER DEFAULT 0,
  last_followup_at   TIMESTAMPTZ,
  closed_at          TIMESTAMPTZ,
  notes              TEXT
);

CREATE INDEX idx_outreach_prospect_name ON outreach_log(prospect_name);
CREATE INDEX idx_outreach_status ON outreach_log(status);
CREATE INDEX idx_outreach_sent_at ON outreach_log(sent_at DESC);
CREATE INDEX idx_outreach_category ON outreach_log(prospect_category);

COMMENT ON TABLE outreach_log IS 'Inflection Lever Track — cada outreach + status. Source para weekly review del track.';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: audit_log
-- ─────────────────────────────────────────────────────────────────────
-- Función: event sourcing genérico. Cada acción importante del workflow
-- (brief_created, hitl_decision, publish_attempt, error) deja entrada.
-- Útil para debugging + analytics histórico.
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE audit_log (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type  TEXT NOT NULL,
  brief_id    UUID REFERENCES briefs_pending(id) ON DELETE SET NULL,
  actor       TEXT,
  payload     JSONB,
  timestamp   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_event_type ON audit_log(event_type);
CREATE INDEX idx_audit_brief_id ON audit_log(brief_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_payload_gin ON audit_log USING GIN (payload);

COMMENT ON TABLE audit_log IS 'Event sourcing genérico: brief_created, hitl_decided, publish_attempted, error_caught, etc.';

-- ─────────────────────────────────────────────────────────────────────
-- Views convenience
-- ─────────────────────────────────────────────────────────────────────

-- Vista: stats diarios de pipeline
CREATE OR REPLACE VIEW daily_pipeline_stats AS
SELECT
  DATE(b.created_at) AS day,
  COUNT(*) FILTER (WHERE b.approval_status = 'pending')          AS pending,
  COUNT(*) FILTER (WHERE b.approval_status = 'approved')         AS approved,
  COUNT(*) FILTER (WHERE b.approval_status = 'rejected')         AS rejected,
  COUNT(*) FILTER (WHERE b.approval_status = 'edited')           AS edited,
  COUNT(*) FILTER (WHERE b.approval_status = 'published')        AS published,
  COUNT(*) FILTER (WHERE b.approval_status = 'auto_rejected_timeout') AS timeout_rejected,
  COUNT(*) FILTER (WHERE b.compliance_verdict = 'blocked')       AS compliance_blocked,
  AVG(b.signal_score)                                             AS avg_score,
  AVG(b.edit_iterations)                                          AS avg_edits_per_brief
FROM briefs_pending b
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
FROM costs_log
GROUP BY DATE_TRUNC('month', timestamp), provider
ORDER BY month DESC, total_cost_usd DESC;

-- Vista: compliance violations top — qué reglas fallan más
CREATE OR REPLACE VIEW compliance_violations_top AS
SELECT
  rule,
  rule_number,
  rule_category,
  COUNT(*) FILTER (WHERE NOT passed)                AS failures_count,
  COUNT(*) FILTER (WHERE NOT passed AND severity = 'block') AS blocks_count,
  COUNT(*)                                          AS total_evaluations,
  ROUND(COUNT(*) FILTER (WHERE NOT passed) * 100.0 / COUNT(*), 2) AS failure_rate_pct
FROM compliance_log
GROUP BY rule, rule_number, rule_category
HAVING COUNT(*) > 0
ORDER BY failures_count DESC;

-- Vista: outreach funnel
CREATE OR REPLACE VIEW outreach_funnel AS
SELECT
  prospect_category,
  COUNT(*)                                          AS total_sent,
  COUNT(*) FILTER (WHERE status IN ('replied', 'scheduled', 'closed_win', 'closed_lose')) AS responded,
  COUNT(*) FILTER (WHERE status IN ('scheduled', 'closed_win'))                            AS advanced,
  COUNT(*) FILTER (WHERE status = 'closed_win')                                            AS won,
  ROUND(COUNT(*) FILTER (WHERE status IN ('replied', 'scheduled', 'closed_win', 'closed_lose')) * 100.0 / NULLIF(COUNT(*), 0), 2) AS response_rate_pct
FROM outreach_log
GROUP BY prospect_category
ORDER BY won DESC, advanced DESC;

-- ─────────────────────────────────────────────────────────────────────
-- Helper functions
-- ─────────────────────────────────────────────────────────────────────

-- Función: cleanup dedup_history > 30 días
CREATE OR REPLACE FUNCTION cleanup_old_dedup() RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM dedup_history WHERE processed_at < (now() - INTERVAL '30 days');
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_dedup IS 'Llamar via cron n8n diario 2am — limpia entradas dedup > 30 días';

-- Función: marcar briefs expirados como auto_rejected_timeout
CREATE OR REPLACE FUNCTION expire_pending_briefs() RETURNS INTEGER AS $$
DECLARE
  expired_count INTEGER;
BEGIN
  UPDATE briefs_pending
  SET approval_status = 'auto_rejected_timeout',
      approved_at = now()
  WHERE approval_status = 'pending'
    AND expires_at < now();
  GET DIAGNOSTICS expired_count = ROW_COUNT;
  RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION expire_pending_briefs IS 'Llamar via cron n8n cada hora — marca briefs sin HITL decision como timeout';

-- ─────────────────────────────────────────────────────────────────────
-- Storage bucket (NO se crea por SQL — se crea via Supabase Dashboard
-- o API. Documentación para Manuel:)
-- ─────────────────────────────────────────────────────────────────────
-- Bucket name: dinero-ia-assets
-- Privacy: private (signed URLs para publishing externo)
-- Public CDN: NO (control de acceso)
-- Folder structure propuesta:
--   /carousels/{brief_id}/slide_{n}.png   — slides Blotato/gpt-image-2
--   /carousels/{brief_id}/full.pdf        — carousel full PDF
--   /audio/{brief_id}/reel.mp3            — ElevenLabs Fase 2
--   /video/{brief_id}/reel.mp4            — Seedance Fase 2
--   /exports/{brief_id}/{platform}.zip    — bundle final
-- Lifecycle policy: borrar carousels > 90 días para ahorrar storage
-- ─────────────────────────────────────────────────────────────────────
