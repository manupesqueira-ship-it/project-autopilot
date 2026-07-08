# -*- coding: utf-8 -*-
"""gen_heroes.py — GENERADOR GENÉRICO de heroes desde heroes_plan.json.

Cierra el ciclo: creative_director → hero_director (prompts) → ESTE script
(genera) → normaliza → public/heroes/ + registro en el banco compartido.

Tiers según la regla de Manuel: lite = borrador (revisar píxeles), fast =
versión de reel. El seed va por gpt-image (regla: fotos = API OpenAI).

Uso:  python gen_heroes.py lite|fast [heroes_plan.json]
"""
import base64
import json
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
HERE = ROOT / "infra" / "assembler"
OUT = HERE / "out" / "_i2v"
PUB = ROOT / "infra" / "remotion-render" / "public" / "heroes"
BANK = Path(r"C:\Users\manup\assets_ia\manifest.json")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra" / "voz"))
from veo_engine import generate  # noqa: E402
from tts_timestamps import load_env  # noqa: E402

FF = (r"C:\Users\manup\AppData\Local\Microsoft\WinGet\Packages"
      r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
      r"\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe")


def gen_seed(key: str, prompt: str, dst: Path):
    body = json.dumps({"model": "gpt-image-1", "prompt": prompt,
                       "size": "1024x1536", "quality": "high", "n": 1}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/images/generations",
                                 data=body, method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read())
    dst.write_bytes(base64.b64decode(data["data"][0]["b64_json"]))


def register(tag: str, clip: Path, why: str, used_in: str):
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    entry = {"file": str(clip).replace("\\", "/"), "subject": why,
             "world": "página (negro mate)", "engine": "veo_3_1",
             "type": "subject", "used_in": [used_in], "date": str(date.today())}
    bank["assets"] = [a for a in bank["assets"] if a["file"] != entry["file"]] + [entry]
    BANK.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tier = sys.argv[1] if len(sys.argv) > 1 else "lite"
    plan_path = Path(sys.argv[2]) if len(sys.argv) > 2 else \
        HERE / "out" / "_treatments" / "heroes_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    okey = load_env()["OPENAI_API_KEY"]
    OUT.mkdir(parents=True, exist_ok=True)
    PUB.mkdir(parents=True, exist_ok=True)
    for h in plan["heroes"]:
        tag = h["tag"]
        seed = OUT / f"seed_{tag}.png"
        raw = OUT / f"{tag}_{tier}.mp4"
        if not seed.exists():
            print(f"[{tag}] seed gpt-image …")
            gen_seed(okey, h["seed_prompt"], seed)
        if not raw.exists():
            generate(str(seed), h["motion_prompt"], raw, tier, int(h.get("duration_s", 8)))
        if tier == "fast":
            # normaliza (Veo trae AAC que cuelga Remotion) y publica para bgClip
            dst = PUB / f"{tag}.mp4"
            subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(raw), "-an",
                            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-preset", "fast", str(dst)], check=True)
            register(tag, dst, h.get("why", ""), plan_path.stem)
            print(f"  publicado heroes/{tag}.mp4 + registrado en banco")
    print(f"HEROES {tier} listos · revisar PÍXELES antes de pasar a fast/ensamblar")
