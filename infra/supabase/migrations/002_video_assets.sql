-- ─────────────────────────────────────────────────────────────────────
-- Dinero IA — Video Assets Schema (Fase 1 post-ADR-018/019)
-- ─────────────────────────────────────────────────────────────────────
-- Migration: 002_video_assets.sql
-- Created: 2026-06-01
-- Purpose: extensiones al schema base (001_initial.sql) para soportar:
--          - Pipeline video (A5-A8e): assets storage tracking
--          - Música licensing: music_usage_log para anti-repetición
--          - Topical dedup: topic_keywords para anti-canibalización
--          - Slot config: extender briefs_pending con slot info
--
-- Pre-requisito: 001_initial.sql ya aplicado en Supabase
-- ─────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────
-- ALTER: briefs_pending — agregar slot info
-- ─────────────────────────────────────────────────────────────────────

ALTER TABLE briefs_pending
  ADD COLUMN IF NOT EXISTS slot TEXT CHECK (slot IN ('morning', 'noon', 'evening')),
  ADD COLUMN IF NOT EXISTS slot_target_publish_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS topic_keywords TEXT[],
  ADD COLUMN IF NOT EXISTS production_status TEXT DEFAULT 'pending'
    CHECK (production_status IN (
      'pending', 'visual_directing', 'audio_directing', 'script_composing',
      'image_generating', 'video_generating', 'voice_generating',
      'music_selecting', 'compositing', 'uploading', 'ready_to_publish',
      'failed_production'
    )),
  ADD COLUMN IF NOT EXISTS production_started_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS production_completed_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS production_error TEXT;

CREATE INDEX IF NOT EXISTS idx_briefs_slot ON briefs_pending(slot);
CREATE INDEX IF NOT EXISTS idx_briefs_production_status ON briefs_pending(production_status);
CREATE INDEX IF NOT EXISTS idx_briefs_topic_keywords ON briefs_pending USING GIN (topic_keywords);

COMMENT ON COLUMN briefs_pending.slot IS 'morning=7am MX, noon=12:30 MX, evening=7pm MX';
COMMENT ON COLUMN briefs_pending.topic_keywords IS 'Keywords extraídas de que_paso para topical dedup (max 2 overlap 7 días)';
COMMENT ON COLUMN briefs_pending.production_status IS 'Pipeline state durante asset generation post-HITL approval';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: assets_storage
-- ─────────────────────────────────────────────────────────────────────
-- Función: tracking de TODOS los assets generados durante producción de
-- un reel. Una fila por (brief_id, asset_type, asset_index).
-- Asset URLs apuntan a Supabase Storage bucket `dinero-ia-assets`.
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS assets_storage (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id            UUID NOT NULL REFERENCES briefs_pending(id) ON DELETE CASCADE,
  asset_type          TEXT NOT NULL CHECK (asset_type IN (
    'keyframe', 'video_segment', 'voice_audio', 'music_track',
    'subtitle_srt', 'final_video', 'cover_image'
  )),
  asset_index         INTEGER NOT NULL DEFAULT 0,  -- 0,1,2... para keyframes/segments
  storage_path        TEXT NOT NULL,                -- path en bucket: e.g. carousels/{brief_id}/keyframe_0.png
  storage_url         TEXT,                         -- signed URL público temporal
  mime_type           TEXT,
  file_size_bytes     BIGINT,
  duration_seconds    NUMERIC(8,3),                 -- para audio/video
  width_px            INTEGER,
  height_px           INTEGER,

  -- Generación metadata
  generator_tool      TEXT NOT NULL CHECK (generator_tool IN (
    'gpt-image-2', 'seedance-2.0', 'elevenlabs-creator',
    'epidemic-sound', 'artlist', 'ffmpeg-compositor'
  )),
  generator_params    JSONB,                        -- prompts, voice_settings, music_id, etc.
  generation_cost_usd NUMERIC(10,6) DEFAULT 0,

  -- Status
  status              TEXT NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending', 'generating', 'ready', 'failed', 'archived')),
  error_message       TEXT,

  -- Timestamps
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  generated_at        TIMESTAMPTZ,
  expires_at          TIMESTAMPTZ DEFAULT (now() + INTERVAL '90 days')
);

CREATE INDEX IF NOT EXISTS idx_assets_brief_id ON assets_storage(brief_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets_storage(asset_type);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets_storage(status);
CREATE INDEX IF NOT EXISTS idx_assets_generator ON assets_storage(generator_tool);
CREATE INDEX IF NOT EXISTS idx_assets_expires_at ON assets_storage(expires_at);

COMMENT ON TABLE assets_storage IS 'Todos los assets generados durante video production (keyframes, voice, music, final MP4)';
COMMENT ON COLUMN assets_storage.expires_at IS 'Cleanup automático después de 90 días — final_video se mantiene más tiempo (lifecycle policy aparte en bucket)';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: music_usage_log
-- ─────────────────────────────────────────────────────────────────────
-- Función: anti-repetición de tracks musicales. Cada vez que A8d
-- selecciona un track, queda registrado. A8d filtra tracks usados en
-- últimos 14 días para evitar "ya escuché esto".
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS music_usage_log (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id        UUID NOT NULL REFERENCES briefs_pending(id) ON DELETE CASCADE,
  track_id        TEXT NOT NULL,                    -- ID del track en Epidemic/Artlist/local
  track_name      TEXT NOT NULL,
  track_artist    TEXT,
  source          TEXT NOT NULL CHECK (source IN ('epidemic_sound', 'artlist', 'youtube_audio_lib', 'pixabay', 'custom')),
  mood_tag        TEXT NOT NULL,                    -- e.g. "calm_confident", "tech_curious"
  bpm             INTEGER,
  duration_sec    INTEGER,
  used_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_music_usage_track_id ON music_usage_log(track_id);
CREATE INDEX IF NOT EXISTS idx_music_usage_used_at ON music_usage_log(used_at DESC);
CREATE INDEX IF NOT EXISTS idx_music_usage_mood ON music_usage_log(mood_tag);

COMMENT ON TABLE music_usage_log IS 'Tracking de música para anti-repetición — A8d query últimos 14 días para evitar reuso';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: topic_keywords_recent
-- ─────────────────────────────────────────────────────────────────────
-- Función: vista materializada de keywords usados últimos 7 días.
-- A1.5 Binary Filter consulta esto para topical dedup (max 2 overlap).
-- ─────────────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW topic_keywords_recent AS
SELECT
  unnest(topic_keywords) AS keyword,
  COUNT(*) AS usage_count,
  MAX(created_at) AS last_used_at
FROM briefs_pending
WHERE created_at > (now() - INTERVAL '7 days')
  AND approval_status IN ('approved', 'published')
  AND topic_keywords IS NOT NULL
GROUP BY unnest(topic_keywords)
ORDER BY usage_count DESC, last_used_at DESC;

COMMENT ON VIEW topic_keywords_recent IS 'Keywords usadas en últimos 7 días — A1.5 filter usa para anti-canibalización topical';

-- ─────────────────────────────────────────────────────────────────────
-- Tabla: voice_clone_versions
-- ─────────────────────────────────────────────────────────────────────
-- Función: tracking de qué voice ID se usa cuándo. Permite ver Fase 1.0
-- (voice library) vs Fase 1.1 (clone Manuel) en cualquier brief histórico.
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS voice_clone_versions (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  voice_id          TEXT NOT NULL,                  -- ElevenLabs voice ID
  voice_name        TEXT NOT NULL,                  -- e.g. "Adam (library)", "Manuel Pesqueira clone v1"
  is_clone_owner    BOOLEAN NOT NULL DEFAULT false, -- true si es clone Manuel
  voice_provider    TEXT NOT NULL DEFAULT 'elevenlabs' CHECK (voice_provider IN ('elevenlabs', 'openai_tts', 'fish_audio')),
  active            BOOLEAN NOT NULL DEFAULT false, -- solo 1 voice activa a la vez
  voice_settings    JSONB NOT NULL,                 -- stability, similarity_boost, style, etc.
  notes             TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  activated_at      TIMESTAMPTZ,
  deactivated_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_voice_clone_active ON voice_clone_versions(active);
CREATE INDEX IF NOT EXISTS idx_voice_clone_voice_id ON voice_clone_versions(voice_id);

-- Solo 1 voice puede estar active a la vez
CREATE UNIQUE INDEX IF NOT EXISTS idx_voice_clone_only_one_active
  ON voice_clone_versions(active) WHERE active = true;

COMMENT ON TABLE voice_clone_versions IS 'Tracking de voice IDs usados — Fase 1.0 voice library → Fase 1.1 clone Manuel swap';

-- ─────────────────────────────────────────────────────────────────────
-- Funciones helper
-- ─────────────────────────────────────────────────────────────────────

-- Función: get_current_voice_id() — devuelve el voice_id activo
CREATE OR REPLACE FUNCTION get_current_voice_id() RETURNS TEXT AS $$
DECLARE
  current_id TEXT;
BEGIN
  SELECT voice_id INTO current_id
  FROM voice_clone_versions
  WHERE active = true
  LIMIT 1;
  RETURN COALESCE(current_id, 'fallback_default_voice');
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_current_voice_id IS 'A8c Voice Gen lo llama para obtener voice_id current — soporta swap Fase 1.0 → 1.1 sin tocar workflows';

-- Función: cleanup_expired_assets() — limpia assets > 90 días (excepto final_video)
CREATE OR REPLACE FUNCTION cleanup_expired_assets() RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  UPDATE assets_storage
  SET status = 'archived',
      storage_url = NULL  -- URLs firmadas expiran, dejar storage_path para referencia
  WHERE expires_at < now()
    AND status = 'ready'
    AND asset_type != 'final_video';  -- mantener final videos como referencia histórica
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_assets IS 'Cron diario 3am — archiva assets intermedios > 90 días, preserva final_video';

-- Función: keyword_overlap_count(text[]) — cuenta cuántos keywords ya están en los últimos 7 días
CREATE OR REPLACE FUNCTION keyword_overlap_count(new_keywords TEXT[]) RETURNS INTEGER AS $$
DECLARE
  overlap_count INTEGER;
BEGIN
  SELECT COUNT(DISTINCT keyword) INTO overlap_count
  FROM topic_keywords_recent
  WHERE keyword = ANY(new_keywords);
  RETURN COALESCE(overlap_count, 0);
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION keyword_overlap_count IS 'A1.5 Binary Filter usa para topical dedup — si return > 2, descartar item';

-- ─────────────────────────────────────────────────────────────────────
-- Seed data: voice clone Fase 1.0 (library default)
-- ─────────────────────────────────────────────────────────────────────

INSERT INTO voice_clone_versions (
  voice_id, voice_name, is_clone_owner, voice_provider, active, voice_settings, notes
) VALUES (
  'pNInz6obpgDQGcFmaJgB',   -- Adam (multilingual ElevenLabs library) — placeholder ID
  'Adam (ElevenLabs library) - Fase 1.0 default',
  false,
  'elevenlabs',
  true,
  '{
    "stability": 0.55,
    "similarity_boost": 0.75,
    "style": 0.35,
    "use_speaker_boost": true,
    "model_id": "eleven_multilingual_v2"
  }'::jsonb,
  'Voice library default mientras Manuel no graba. Swap a clone Manuel cuando Fase 1.1 active.'
)
ON CONFLICT DO NOTHING;

-- ─────────────────────────────────────────────────────────────────────
-- Storage bucket setup (documentación — crear vía Supabase Dashboard o API)
-- ─────────────────────────────────────────────────────────────────────
-- Bucket name: dinero-ia-assets
-- Privacy: private
-- Folder structure:
--   /keyframes/{brief_id}/{index}.png   (gpt-image-2 outputs)
--   /video_segments/{brief_id}/{index}.mp4  (Seedance outputs por keyframe)
--   /voice/{brief_id}/narration.mp3     (ElevenLabs output)
--   /music/{brief_id}/track.mp3         (Epidemic/Artlist selected)
--   /subtitles/{brief_id}/subs.srt      (auto-generated)
--   /final/{brief_id}/reel.mp4          (FFmpeg compositor output)
--   /covers/{brief_id}/cover.jpg        (K1 keyframe = cover)
--   /music-library/{mood_tag}/{track_id}.mp3  (catálogo curado pre-pulled)
--
-- Lifecycle policies:
--   - keyframes, video_segments, voice, music: 90 días retention
--   - final_video, cover: 365 días retention
--   - music-library: sin expiración (curado)
-- ─────────────────────────────────────────────────────────────────────
