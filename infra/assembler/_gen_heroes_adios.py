"""Heroes del reel 'adiós mundialista': seeds gpt-image → Veo 3.1 (regla de tiers de Manuel:
LITE primero como preliminar; al aprobar composición en píxeles, FAST para la versión del reel).

Uso:  python _gen_heroes_adios.py lite|fast
"""
import base64
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
HERE = ROOT / "infra" / "assembler"
OUT = HERE / "out" / "_i2v"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra" / "voz"))
from veo_engine import generate  # noqa: E402
from tts_timestamps import load_env  # noqa: E402

WORLD = ("cinematic dark editorial photography, matte black moody atmosphere, volumetric light, "
         "restrained palette of deep blacks and warm light, no text, no logos, no people, no faces")

HEROES = [
    {
        "tag": "hero_boleto",
        "seed_prompt": (
            "A single golden paper event ticket floating in pure darkness, its edges glowing like "
            "cooling embers turning to gray ash, thin wisps of smoke rising, dramatic warm rim "
            f"light, shallow depth of field, {WORLD}"),
        "motion": ("The golden ticket drifts and rotates extremely slowly in darkness, its ember "
                   "edges cooling from orange glow to gray ash, ash particles and smoke wisps "
                   "floating away, rim light glinting, camera pushing in very slowly, cinematic, "
                   "dark atmosphere preserved"),
    },
    {
        "tag": "hero_azteca",
        "seed_prompt": (
            "Low aerial night photograph of a colossal empty concrete stadium exterior, brutalist "
            "monumental architecture, stadium lights dimming into darkness, light haze around the "
            f"structure, deserted surroundings, melancholic mood, {WORLD}"),
        "motion": ("Extremely slow aerial drift toward the dark silent stadium, its lights "
                   "flickering and dimming one by one, haze moving softly, melancholic and "
                   "monumental, cinematic, dark atmosphere preserved"),
    },
]


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


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tier = sys.argv[1] if len(sys.argv) > 1 else "lite"
    okey = load_env()["OPENAI_API_KEY"]
    OUT.mkdir(parents=True, exist_ok=True)
    for h in HEROES:
        seed = OUT / f"seed_{h['tag']}.png"
        clip = OUT / f"{h['tag']}_{tier}.mp4"
        if not seed.exists():
            print(f"[{h['tag']}] seed gpt-image …")
            gen_seed(okey, h["seed_prompt"], seed)
        if not clip.exists():
            generate(str(seed), h["motion"], clip, tier, 8)
    print("listo")
