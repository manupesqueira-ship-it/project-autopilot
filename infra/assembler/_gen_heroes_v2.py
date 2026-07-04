"""Heroes del Mundial v2: 3 seeds (gpt-image, regla fotos=OpenAI) → 3 clips Kling v3 Pro (fal).

Motor oficial post-A/B-ciego 2026-07-04 (empate → gana el barato): Kling v3 Pro $0.56/clip.
El 4º hero (estadio) = clipA del A/B, ya pagado.
"""
import base64
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
HERE = ROOT / "infra" / "assembler"
OUT = HERE / "out" / "_i2v"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra" / "voz"))
from i2v_engine import _still_to_data_uri  # noqa: E402
from _ab_kling_seedance import call_fal  # noqa: E402
from tts_timestamps import load_env  # noqa: E402

WORLD = ("cinematic dark editorial photography, matte black moody atmosphere, volumetric light, "
         "restrained palette of deep blacks and warm white light, no text, no logos, no faces")

HEROES = [
    {
        "tag": "hero_multitud_angel",
        "seed_prompt": (
            "Aerial night photograph of an immense sea of people flooding a grand city avenue "
            "around a tall victory column monument with a golden winged statue on top, hundreds of "
            "thousands of tiny phone lights twinkling like stars in the crowd, light haze, "
            f"{WORLD}"),
        "motion": ("Slow majestic aerial rise revealing the endless crowd stretching down the "
                   "avenue, phone lights twinkling, gentle drift, crowd subtly alive, cinematic, "
                   "dark atmosphere preserved"),
    },
    {
        "tag": "hero_billetes_mxn",
        "seed_prompt": (
            "Macro cinematic photograph of paper banknotes suspended mid-air in pure darkness, "
            "dramatic warm rim light catching their edges, shallow depth of field, floating dust "
            f"particles, {WORLD}"),
        "motion": ("Banknotes falling in extreme slow motion through darkness, gently tumbling and "
                   "rotating, rim light glinting on edges, dust particles drifting, camera slowly "
                   "pushing in, cinematic"),
    },
    {
        "tag": "hero_trofeo",
        "seed_prompt": (
            "A gleaming golden sports trophy silhouette on a dark pedestal in a black void studio, "
            "single dramatic spotlight from above, volumetric haze, reflections on polished gold, "
            f"generic trophy shape not any real trademark trophy, {WORLD}"),
        "motion": ("Extremely slow orbital camera move around the golden trophy, spotlight beams "
                   "shifting through haze, dust particles floating in the light, reflections "
                   "sliding across the gold, cinematic, dark"),
    },
]

KLING = "fal-ai/kling-video/v3/pro/image-to-video"


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
    env = load_env()
    okey, fkey = env["OPENAI_API_KEY"], env["FAL_KEY"]
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0.0
    for h in HEROES:
        seed = OUT / f"seed_{h['tag']}.png"
        clip = OUT / f"{h['tag']}.mp4"
        if not seed.exists():
            print(f"[{h['tag']}] seed gpt-image …")
            gen_seed(okey, h["seed_prompt"], seed)
            total += 0.17
        if not clip.exists():
            print(f"[{h['tag']}] Kling v3 Pro ~$0.56 …")
            data = call_fal(fkey, KLING, {
                "start_image_url": _still_to_data_uri(str(seed)),
                "prompt": h["motion"], "duration": "5", "generate_audio": False,
            })
            url = (data.get("video") or {}).get("url") or data.get("url")
            with urllib.request.urlopen(url, timeout=600) as r:
                clip.write_bytes(r.read())
            total += 0.56
            print(f"  ok -> {clip.name} ({clip.stat().st_size/1e6:.1f} MB)")
    with (ROOT / "docs" / "EXPENSES.md").open("a", encoding="utf-8") as f:
        f.write(f"\n- {datetime.now().date()} · heroes Mundial v2 · 3 seeds gpt-image + 3 clips "
                f"Kling v3 Pro (fal) · ~${total:.2f} USD · motor oficial post A/B (empate→barato)")
    print(f"HEROES listos · ~${total:.2f} USD registrados")
