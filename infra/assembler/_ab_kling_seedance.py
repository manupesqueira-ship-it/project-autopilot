"""A/B CIEGO Kling v3 Pro vs Seedance 2.0 (fal): mismo still, mismo prompt de movimiento.

Responde la duda de Manuel 2026-07-04: '¿Kling v3 da la misma calidad que Seedance 2.0?'
— con evidencia en píxeles, no con leaderboards. Gasto: ~$0.56 + ~$3.40 ≈ $4 USD.
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
HERE = ROOT / "infra" / "assembler"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra" / "voz"))
from i2v_engine import _still_to_data_uri  # noqa: E402
from tts_timestamps import RETRY_STATUS, RetryableError, load_env, with_retries  # noqa: E402

SEED = HERE / "out" / "_i2v" / "seed_estadio.png"
OUT = HERE / "out" / "_i2v"
MOTION = ("Slow majestic aerial push-in toward the pitch, camera descending gently through light "
          "haze, floodlight beams shimmering volumetrically, the crowd texture subtly alive with "
          "tiny flickering phone lights, cinematic, dark moody atmosphere preserved, no text")

JOBS = [
    {"tag": "clipA_kling3pro", "endpoint": "fal-ai/kling-video/v3/pro/image-to-video",
     "input": {"start_image_url": None, "prompt": MOTION, "duration": "5", "generate_audio": False},
     "est_usd": 0.56},
    {"tag": "clipB_seedance20", "endpoint": "bytedance/seedance-2.0/image-to-video",
     "input": {"image_url": None, "prompt": MOTION, "resolution": "1080p", "duration": "5",
               "aspect_ratio": "9:16", "generate_audio": False},
     "est_usd": 3.40},
]


def call_fal(key: str, endpoint: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"https://fal.run/{endpoint}", data=data,
                                 headers={"Authorization": f"Key {key}",
                                          "Content-Type": "application/json"}, method="POST")
    def _c():
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in RETRY_STATUS:
                raise RetryableError(f"HTTP {e.code}")
            raise SystemExit(f"fal HTTP {e.code}: {e.read()[:300]}")
        except (urllib.error.URLError, TimeoutError) as e:
            raise RetryableError(f"red: {e}")
    return with_retries(_c, what=endpoint)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    key = load_env().get("FAL_KEY")
    if not key:
        raise SystemExit("falta FAL_KEY")
    uri = _still_to_data_uri(str(SEED))
    total = 0.0
    for j in JOBS:
        body = dict(j["input"])
        for f in ("start_image_url", "image_url"):
            if f in body:
                body[f] = uri
        print(f"[{j['tag']}] {j['endpoint']} ~${j['est_usd']:.2f} …")
        data = call_fal(key, j["endpoint"], body)
        url = (data.get("video") or {}).get("url") or data.get("url")
        if not url:
            raise SystemExit(f"sin video url: {str(data)[:300]}")
        dst = OUT / f"{j['tag']}.mp4"
        with urllib.request.urlopen(url, timeout=600) as r:
            dst.write_bytes(r.read())
        total += j["est_usd"]
        print(f"  ok -> {dst.name} ({dst.stat().st_size/1e6:.1f} MB)")
    with (ROOT / "docs" / "EXPENSES.md").open("a", encoding="utf-8") as f:
        f.write(f"\n- {datetime.now().date()} · fal.ai A/B ciego Kling v3 Pro (~$0.56) vs "
                f"Seedance 2.0 1080p (~$3.40) · mismo still estadio (gpt-image ~$0.17) · "
                f"~${total + 0.17:.2f} USD · decisión de motor de volumen Dinero IA")
    print(f"A/B listo · ~${total:.2f} USD registrados")
