"""Genera el still semilla del A/B con gpt-image (regla de Manuel: fotos = API OpenAI)."""
import base64
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
sys.path.insert(0, str(ROOT / "infra" / "voz"))
from tts_timestamps import load_env  # noqa: E402

PROMPT = ("Aerial cinematic night photograph of a colossal packed soccer stadium bowl glowing "
          "in darkness, 90,000 crowd as a shimmering texture of tiny lights, dramatic volumetric "
          "floodlights cutting through light haze, matte black moody atmosphere surrounding the "
          "stadium, dark editorial photography style, restrained color palette of deep blacks and "
          "warm white light, no text, no logos, no flags")

OUT = ROOT / "infra" / "assembler" / "out" / "_i2v" / "seed_estadio.png"

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    key = load_env()["OPENAI_API_KEY"]
    body = json.dumps({
        "model": "gpt-image-1",
        "prompt": PROMPT,
        "size": "1024x1536",
        "quality": "high",
        "n": 1,
    }).encode()
    req = urllib.request.Request("https://api.openai.com/v1/images/generations",
                                 data=body, method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read())
    b64 = data["data"][0]["b64_json"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(base64.b64decode(b64))
    print(f"seed -> {OUT}")
