"""veo_engine.py — Google Veo 3.1 vía Gemini API (motor alterno oficial, 2026-07-04).

Por qué existe: fal rechazó la tarjeta de Manuel; la facturación de Google sí
funciona. Veo 3.1 Fast 1080p = $0.12/s (~$0.72 clip 6s) CON audio nativo.
Uso:  python veo_engine.py <seed.png> "<motion prompt>" <out.mp4> [fast|standard|lite] [4|6|8]
"""
import base64
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
sys.path.insert(0, str(ROOT / "infra" / "voz"))
from tts_timestamps import load_env  # noqa: E402

MODELS = {
    "fast": ("veo-3.1-fast-generate-preview", 0.12),
    "standard": ("veo-3.1-generate-preview", 0.40),
    "lite": ("veo-3.1-lite-generate-preview", 0.08),
}
BASE = "https://generativelanguage.googleapis.com/v1beta"


def pad916_b64(path: str) -> str:
    """Padea el seed a 1080x1920 sobre negro del mundo y regresa base64 JPEG."""
    im = Image.open(path).convert("RGB")
    tw, th = 1080, 1920
    w, h = im.size
    nh = max(1, round(h * tw / w))
    im = im.resize((tw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", (tw, th), (7, 7, 7))
    if nh <= th:
        canvas.paste(im, (0, (th - nh) // 2))
    else:
        top = (nh - th) // 2
        canvas.paste(im.crop((0, top, tw, top + th)), (0, 0))
    buf = BytesIO()
    canvas.save(buf, format="JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _req(url: str, key: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if body is not None else "GET")
    req.add_header("x-goog-api-key", key)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Veo HTTP {e.code}: {e.read()[:400]}")


def generate(seed: str, prompt: str, out: Path, tier: str = "fast", dur: int = 6) -> Path:
    key = load_env()["GEMINI_API_KEY"]
    model, usd_s = MODELS[tier]
    body = {
        "instances": [{
            "prompt": prompt,
            "image": {"bytesBase64Encoded": pad916_b64(seed), "mimeType": "image/jpeg"},
        }],
        "parameters": {"aspectRatio": "9:16", "resolution": "1080p", "durationSeconds": dur},
    }
    print(f"Veo {tier} ({model}) {dur}s ~${usd_s * dur:.2f} …")
    op = _req(f"{BASE}/models/{model}:predictLongRunning", key, body)
    name = op.get("name")
    if not name:
        raise SystemExit(f"sin operation name: {str(op)[:300]}")
    for _ in range(120):
        time.sleep(10)
        st = _req(f"{BASE}/{name}", key)
        if st.get("done"):
            if "error" in st:
                raise SystemExit(f"Veo error: {json.dumps(st['error'])[:400]}")
            resp = st.get("response", {})
            gv = resp.get("generateVideoResponse") or resp
            samples = gv.get("generatedSamples") or gv.get("videos") or []
            if not samples:
                raise SystemExit(f"sin samples: {json.dumps(resp)[:400]}")
            s0 = samples[0]
            uri = (s0.get("video") or {}).get("uri") or s0.get("uri") or (s0.get("video") or {}).get("url")
            if not uri:
                raise SystemExit(f"sin uri: {json.dumps(s0)[:400]}")
            dreq = urllib.request.Request(uri)
            dreq.add_header("x-goog-api-key", key)
            with urllib.request.urlopen(dreq, timeout=600) as r:
                out.write_bytes(r.read())
            cost = usd_s * dur
            with (ROOT / "docs" / "EXPENSES.md").open("a", encoding="utf-8") as f:
                f.write(f"\n- {datetime.now().date()} · Google Veo 3.1 {tier} (Gemini API) · "
                        f"clip {dur}s 1080p 9:16 '{out.stem}' · ~${cost:.2f} USD · motor alterno (fal bloqueado)")
            print(f"ok -> {out} ({out.stat().st_size/1e6:.1f} MB) · ~${cost:.2f} logueado")
            return out
    raise SystemExit("timeout esperando la operación de Veo")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    seed, prompt, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    tier = sys.argv[4] if len(sys.argv) > 4 else "fast"
    dur = int(sys.argv[5]) if len(sys.argv) > 5 else 6
    generate(seed, prompt, out, tier, dur)
