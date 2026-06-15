const express = require("express");
const path = require("path");
const fs = require("fs");
const os = require("os");
const crypto = require("crypto");
const { bundle } = require("@remotion/bundler");
const { renderMedia, selectComposition } = require("@remotion/renderer");

const PORT = process.env.PORT || 3000;
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const SUPABASE_BUCKET = process.env.SUPABASE_BUCKET || "dinero-ai-assets";

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
  console.warn("[warn] SUPABASE_URL or SUPABASE_SERVICE_KEY missing — uploads will fail");
}

async function uploadToSupabase(storageKey, fileBuf, contentType) {
  const url = `${SUPABASE_URL}/storage/v1/object/${SUPABASE_BUCKET}/${storageKey}`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
      apikey: SUPABASE_SERVICE_KEY,
      "Content-Type": contentType,
      "x-upsert": "true",
    },
    body: fileBuf,
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`supabase upload ${res.status}: ${txt}`);
  }
  return await res.json();
}

async function getSignedUrl(storageKey, expiresInSec = 60 * 60 * 24 * 7) {
  const url = `${SUPABASE_URL}/storage/v1/object/sign/${SUPABASE_BUCKET}/${storageKey}`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
      apikey: SUPABASE_SERVICE_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ expiresIn: expiresInSec }),
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`supabase sign ${res.status}: ${txt}`);
  }
  const data = await res.json();
  const signedPath = data.signedURL || data.signedUrl;
  return `${SUPABASE_URL}/storage/v1${signedPath.startsWith("/") ? signedPath : "/" + signedPath}`;
}

const app = express();
app.use(express.json({ limit: "5mb" }));

let cachedBundle = null;
let bundlePromise = null;
async function getBundle() {
  if (cachedBundle) return cachedBundle;
  if (bundlePromise) return bundlePromise;
  bundlePromise = (async () => {
    console.log("[bundle] building Remotion bundle...");
    const t = Date.now();
    cachedBundle = await bundle({
      entryPoint: path.resolve(__dirname, "src/index.ts"),
      webpackOverride: (cfg) => cfg,
    });
    console.log(`[bundle] done in ${Date.now() - t}ms`);
    return cachedBundle;
  })();
  return bundlePromise;
}

app.get("/health", (_, res) => {
  res.json({
    ok: true,
    service: "dinero-ia-remotion",
    uptime: process.uptime(),
    bundle_ready: !!cachedBundle,
  });
});

app.post("/render", async (req, res) => {
  const reqId = crypto.randomBytes(4).toString("hex");
  const t0 = Date.now();
  console.log(`[${reqId}] /render start`);

  try {
    const {
      title,
      script_beats,
      voice_audio_url,
      music_audio_url,
      accent_color,
      duration_seconds,
      brief_id,
    } = req.body;

    if (!title || !Array.isArray(script_beats) || !voice_audio_url) {
      return res.status(400).json({
        error: "missing required fields: title, script_beats, voice_audio_url",
      });
    }

    const fps = 30;
    const seconds = Math.min(Math.max(duration_seconds || 50, 10), 90);
    const durationInFrames = Math.round(seconds * fps);

    const serveUrl = await getBundle();
    console.log(`[${reqId}] bundle ready`);

    const inputProps = {
      title,
      script_beats,
      voice_audio_url,
      music_audio_url: music_audio_url || null,
      accent_color: accent_color || "#00D9A5",
    };

    const composition = await selectComposition({
      serveUrl,
      id: "DineroIAReel",
      inputProps,
    });

    const outputDir = path.join(os.tmpdir(), `remotion-${reqId}`);
    fs.mkdirSync(outputDir, { recursive: true });
    const outputLocation = path.join(outputDir, "out.mp4");

    console.log(`[${reqId}] rendering ${durationInFrames} frames @ ${fps}fps...`);
    const renderStart = Date.now();
    await renderMedia({
      composition: { ...composition, durationInFrames, fps },
      serveUrl,
      codec: "h264",
      outputLocation,
      inputProps,
      chromiumOptions: { headless: true },
    });
    console.log(`[${reqId}] render done in ${Date.now() - renderStart}ms`);

    if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
      return res.status(500).json({
        error: "supabase not configured",
        local_path: outputLocation,
      });
    }

    const fileBuf = fs.readFileSync(outputLocation);
    const storageKey = `videos/${brief_id || reqId}/${Date.now()}.mp4`;

    await uploadToSupabase(storageKey, fileBuf, "video/mp4");
    const videoUrl = await getSignedUrl(storageKey);

    fs.rmSync(outputDir, { recursive: true, force: true });

    const totalMs = Date.now() - t0;
    console.log(`[${reqId}] success in ${totalMs}ms — ${storageKey}`);

    res.json({
      ok: true,
      video_url: videoUrl,
      storage_key: storageKey,
      duration_seconds: seconds,
      render_ms: totalMs,
      brief_id: brief_id || null,
    });
  } catch (err) {
    console.error(`[${reqId}] error`, err);
    res.status(500).json({ error: String(err?.message || err) });
  }
});

app.listen(PORT, () => {
  console.log(`[boot] dinero-ia-remotion listening on :${PORT}`);
  getBundle().catch((e) => console.error("[bundle] preload failed", e));
});
