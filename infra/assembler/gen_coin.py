# -*- coding: utf-8 -*-
# Genera la moneda "hero" (gpt-image) cacheada por MONEDA para el beat
# BeatHeroCoin de Dinero IA. Una imagen por slug (btc, usd, mxn, eth...) ->
# se reusa en todos los videos de esa moneda. Fondo transparente para componer
# limpio sobre el StudioScene; el giro/brillo lo pone Remotion (2.5D).
#
# Mismo patron que gen_caricature.py (load_env -> images/generations,
# gpt-image-1, transparent, cache por slug, log de gasto).
#
# Uso: python gen_coin.py <slug> [--force]
import base64
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
COIN_DIR = ROOT / "infra" / "remotion-render" / "public" / "coins"
EXPENSES = ROOT / "docs" / "EXPENSES.md"

sys.path.insert(0, str(ROOT / "infra" / "voz"))
from tts_timestamps import load_env  # noqa: E402

# Look comun: moneda fisica premium, oro pulido (dorado = dinero en la paleta),
# render 3D foto-real, luz de estudio, una sola moneda, fondo transparente.
STYLE = (
    "a single premium physical coin, polished gold metal with warm amber "
    "reflections, photorealistic 3D product render, dramatic studio rim "
    "lighting from the upper left, subtle milled reeded edge, slight top-down "
    "three-quarter angle, floating centered, soft contact shadow, high detail "
    "sharp focus, fully transparent background, no text label, no watermark, "
    "no hands, exactly one coin"
)

# registro: slug -> que va EMBOSSED en la cara de la moneda.
COIN_PROMPTS = {
    "btc": (
        "the Bitcoin logo (a capital letter B with two vertical strokes through "
        "it) deeply embossed and centered on the coin face"
    ),
    "eth": (
        "the Ethereum diamond logo (two stacked triangles forming a faceted "
        "diamond) deeply embossed and centered on the coin face"
    ),
    "usd": (
        "a US dollar sign ($) deeply embossed and centered on the coin face"
    ),
    "mxn": (
        "a peso sign ($) deeply embossed and centered on the coin face, with a "
        "small MXN engraving below it"
    ),
}


def gen(slug: str, force: bool = False) -> Path:
    COIN_DIR.mkdir(parents=True, exist_ok=True)
    out = COIN_DIR / f"{slug}.png"
    if out.exists() and not force:
        print(f"COIN skip {slug} (cache)")
        return out
    if slug not in COIN_PROMPTS:
        raise SystemExit(
            f"sin prompt para moneda '{slug}' en COIN_PROMPTS "
            f"(agrega el slug con su simbolo)")

    key = load_env()["OPENAI_API_KEY"]
    prompt = f"{COIN_PROMPTS[slug]}. {STYLE}"
    body = json.dumps({
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1024",
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
    print(f"COIN gen {slug} (gpt-image-1, high, 1024x1024)...")
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    b64 = data["data"][0]["b64_json"]
    out.write_bytes(base64.b64decode(b64))
    print(f"COIN ok -> {out}")
    _log_expense(slug)
    return out


def _log_expense(slug: str):
    line = (f"\n- 2026-06-15 · OpenAI gpt-image-1 (high 1024x1024) · moneda hero "
            f"'{slug}' · ~$0.12 USD · Dinero IA BeatHeroCoin (cacheada)")
    try:
        with EXPENSES.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print("EXPENSE log warn:", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("uso: python gen_coin.py <slug> [--force]")
    gen(sys.argv[1], force="--force" in sys.argv)
