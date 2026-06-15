# -*- coding: utf-8 -*-
# Genera caricaturas (gpt-image) cacheadas por personaje para los beats de
# personaje de Dinero IA. Una imagen por slug -> se reusa en todos los videos.
# Fondo transparente para componer limpio sobre el StudioScene.
#
# Politica OpenAI: NO nombrar figuras publicas reales (lo rechaza). Por eso el
# registro describe el "look" iconico del personaje sin nombrarlo. La voz del
# video si lo nombra; la caricatura evoca, no retrata 1:1.
#
# Uso: python gen_caricature.py <slug>
import base64
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
CHAR_DIR = ROOT / "infra" / "remotion-render" / "public" / "characters"
EXPENSES = ROOT / "docs" / "EXPENSES.md"

sys.path.insert(0, str(ROOT / "infra" / "voz"))
from tts_timestamps import load_env  # noqa: E402

STYLE = (
    "flat vector editorial caricature, bold clean outlines, slightly exaggerated "
    "friendly proportions, big expressive head, modern fintech illustration style, "
    "teal and gold accents, soft studio lighting, centered bust portrait facing "
    "the viewer, fully transparent background, no text, no logos, no flag"
)

# registro: slug -> descripcion del look (sin nombrar a la persona real)
CHARACTER_PROMPTS = {
    "bukele": (
        "a charismatic young Latin American president in his early 40s, neat short "
        "dark hair, well groomed short dark beard, wearing a dark navy blazer over "
        "a white shirt with no tie and a backwards black baseball cap, confident "
        "calm half-smile, arms crossed"
    ),
    # opositor generico (NO una persona real): economista/banquero esceptico
    "economista": (
        "a skeptical middle-aged economist, graying hair combed back, rectangular "
        "glasses, neatly trimmed gray beard, wearing a charcoal gray suit with a "
        "deep red tie, one eyebrow raised in doubt, slight frown, arms crossed in a "
        "guarded posture, serious analytical expression"
    ),
}


def gen(slug: str, force: bool = False) -> Path:
    CHAR_DIR.mkdir(parents=True, exist_ok=True)
    out = CHAR_DIR / f"{slug}.png"
    if out.exists() and not force:
        print(f"CARICATURE skip {slug} (cache)")
        return out
    if slug not in CHARACTER_PROMPTS:
        raise SystemExit(f"sin prompt para slug '{slug}' en CHARACTER_PROMPTS")

    key = load_env()["OPENAI_API_KEY"]
    prompt = f"{CHARACTER_PROMPTS[slug]}. {STYLE}"
    body = json.dumps({
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1536",
        "quality": "high",
        "background": "transparent",
        "n": 1,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    print(f"CARICATURE gen {slug} (gpt-image-1, high, 1024x1536)...")
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    b64 = data["data"][0]["b64_json"]
    out.write_bytes(base64.b64decode(b64))
    print(f"CARICATURE ok -> {out}")
    _log_expense(slug)
    return out


def _log_expense(slug: str):
    line = (f"\n- 2026-06-13 · OpenAI gpt-image-1 (high 1024x1536) · caricatura "
            f"'{slug}' · ~$0.17 USD · Dinero IA beats de personaje (cacheada)")
    try:
        with EXPENSES.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print("EXPENSE log warn:", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("uso: python gen_caricature.py <slug> [--force]")
    gen(sys.argv[1], force="--force" in sys.argv)
