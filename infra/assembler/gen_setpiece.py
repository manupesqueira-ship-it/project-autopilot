# -*- coding: utf-8 -*-
# Genera el OBJETO/ESCENA de un set-piece de hook (servilleta, cohete, periodico,
# pizarron, ticket, ...) como imagen foto-real con gpt-image-1. Mismo patron
# aprobado que gen_coin.py / gen_caricature.py.
#
# ARQUITECTURA (decidida 2026-06-19): el OBJETO lo genera la IA (un tiro, sin
# tallar Blender a mano); los DATOS/numeros/formula van ENCIMA en capa controlada
# (Remotion), porque la IA escribe las cifras MAL. Por eso el objeto se pide
# SIEMPRE en blanco, con espacio negativo para el overlay exacto.
#
# Uso:
#   python gen_setpiece.py napkin            # 2 variantes para elegir
#   python gen_setpiece.py napkin --n 3 --force
import base64
import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
OUT_DIR = ROOT / "infra" / "remotion-render" / "public" / "setpieces"
EXPENSES = ROOT / "docs" / "EXPENSES.md"

sys.path.insert(0, str(ROOT / "infra" / "voz"))
from tts_timestamps import load_env  # noqa: E402

import urllib.request  # noqa: E402

# Look comun de marca: foto-real, premium, fondo oscuro (paleta #0D1117), DoF
# poco profundo, luz de estudio, y SIEMPRE espacio en blanco para el overlay.
STYLE = (
    "photorealistic product photography, premium cinematic look, dark moody "
    "charcoal background that matches a near-black brand palette, shallow depth "
    "of field with the hero object in sharp focus and the background softly "
    "blurred, soft warm key light with a cool rim light from the upper left, "
    "gentle realistic contact shadow, high detail, 8k, vertical 9:16 "
    "composition. The hero surface is COMPLETELY BLANK with generous empty "
    "negative space in the center for text added later: absolutely no text, no "
    "handwriting, no letters, no numbers, no print, no logo, no watermark"
)

SETPIECES = {
    "napkin": (
        "A single clean white paper cafe napkin resting flat on a dark table, "
        "one corner naturally folded over, soft realistic fabric creases and "
        "subtle wrinkles, a slim black ballpoint pen resting diagonally beside "
        "it as if someone is about to write on it, shot from a slight top-down "
        "three-quarter angle"
    ),
}


def gen(slug: str, n: int = 2, force: bool = False):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if slug not in SETPIECES:
        raise SystemExit(f"sin prompt para set-piece '{slug}' en SETPIECES")
    existing = sorted(OUT_DIR.glob(f"{slug}_*.png"))
    if existing and not force:
        print(f"SETPIECE skip {slug} (cache: {len(existing)} variantes)")
        return existing

    key = load_env()["OPENAI_API_KEY"]
    prompt = f"{SETPIECES[slug]}. {STYLE}"
    body = json.dumps({
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1536",   # portrait 9:16-ish
        "quality": "high",
        "n": n,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    print(f"SETPIECE gen {slug} x{n} (gpt-image-1, high, 1024x1536)...")
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read().decode("utf-8"))
    outs = []
    for i, item in enumerate(data["data"], 1):
        out = OUT_DIR / f"{slug}_{i}.png"
        out.write_bytes(base64.b64decode(item["b64_json"]))
        outs.append(out)
        print(f"SETPIECE ok -> {out}")
    _log_expense(slug, n)
    return outs


def _log_expense(slug: str, n: int):
    line = (f"\n- 2026-06-19 · OpenAI gpt-image-1 (high 1024x1536) x{n} · "
            f"set-piece '{slug}' · ~${0.19 * n:.2f} USD · Dinero IA hook object")
    try:
        with EXPENSES.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print("EXPENSE log warn:", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("uso: python gen_setpiece.py <slug> [--n N] [--force]")
    slug = sys.argv[1]
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 2
    gen(slug, n=n, force="--force" in sys.argv)
