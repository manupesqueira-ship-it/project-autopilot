# -*- coding: utf-8 -*-
# LOOK TEST (no el colchon): explora el LOOK nuevo que Manuel pidio 2026-06-26
# tras el slice v2 ("pequeno paso adelante, ahora mejorar drasticamente").
# Direccion ELEGIDA por Manuel: "Motion-graphics premium" = 0x100x madurado
# (personaje estilizado pero mas pulido/adulto, navy + verde/dorado vivos,
# graficos cineticos bold, acabado premium, NADA infantil).
#
# 2026-06-26: Manuel eligio la flavor B (dimensional soft-3D) = "la mas
# profesional". Pidio 5 variaciones MAS refinando B para que se vea aun mas
# premium/profesional ("ingeniatelas"). De ahi el B-SET (look_premiumB_1..5),
# cada una empuja el acabado por una palanca distinta (luz, profundidad,
# pedestal, energia, minimalismo) manteniendo el MISMO personaje (consistencia).
#
# El concepto/metafora NO se decide aqui (eso es el director); esto fija el LOOK.
# Sigue siendo el FRAME DE ARRANQUE; el movimiento lo daria i2v despues, SOLO
# cuando el look pase la barra de Manuel.
#
# Uso:
#   python gen_look.py            # las 3 flavors base a|b|c (cache)
#   python gen_look.py bset       # las 5 variaciones refinadas de B
#   python gen_look.py bset --force
import base64
import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
OUT_DIR = ROOT / "infra" / "remotion-render" / "public" / "scenes"
EXPENSES = ROOT / "docs" / "EXPENSES.md"

sys.path.insert(0, str(ROOT / "infra" / "voz"))
from tts_timestamps import (  # noqa: E402
    RETRY_STATUS, RetryableError, load_env, with_retries)

import urllib.error  # noqa: E402
import urllib.request  # noqa: E402

# --- Set base A|B|C ----------------------------------------------------------
STYLE_PREMIUM = (
    "Premium fintech motion-graphics key art, MATURE and professional: NOT "
    "childish, NOT chibi, NOT infantile, refined adult design. Deep near-black "
    "navy background hex 0D1117 with vivid emerald-green and warm gold accent "
    "lighting, calm cinematic depth and a subtle studio glow. Tall vertical 9:16 "
    "composition with generous empty negative space reserved for data added "
    "later. Absolutely no text, no numbers, no letters, no logos, no watermark, "
    "no UI elements."
)
CHAR_PREMIUM = (
    "a confident stylized adult everyperson with warm light-brown skin, short "
    "tidy dark hair, refined modern adult proportions and an expressive but "
    "composed pose, wearing smart-casual modern attire with a subtle teal-green "
    "accent, polished premium character design"
)
SCENE_BASE = (
    f"{CHAR_PREMIUM} stands assured on a sleek minimal platform inside a deep "
    "navy premium financial world, gesturing toward a large open area with a "
    "clear sense of upward momentum and growth. Keep the upper-right as empty "
    "navy negative space for a bold animated chart."
)
FLAVORS = {
    "look_premium_a": (
        "Rendered as clean FLAT bold vector motion-graphics: crisp flat shapes, "
        "premium smooth gradients, strong graphic silhouettes, high-energy "
        "editorial motion-design key art. Bold, dynamic, polished and adult."
    ),
    "look_premium_b": (
        "Rendered with soft DIMENSIONAL depth: gentle 3D-like soft shading, "
        "cinematic studio lighting and shallow depth of field, premium glossy "
        "finish, refined adult character modeling. Sophisticated and cinematic."
    ),
    "look_premium_c": (
        "Rendered as a premium EDITORIAL-MOTION hybrid: flat vector base with "
        "subtle fine film grain and texture, elegant gold rim-light glow, "
        "sophisticated upscale editorial finish. Mature, serious, premium."
    ),
}

# --- B-SET: 5 refinamientos de la flavor B (la que eligio Manuel) ------------
# Base dimensional ELEVADA: empuja material/luz/profundidad mas premium.
STYLE_PREMIUM_B = (
    "Premium dimensional 3D-style fintech key art, MATURE, professional and "
    "high-end: soft realistic 3D-like shading and modeling, cinematic studio "
    "lighting with a clean key light plus soft emerald rim light and gentle "
    "fill, shallow depth of field with tasteful bokeh, premium matte-and-"
    "specular materials, subtle volumetric glow, refined cinematic color grade. "
    "Deep near-black navy background hex 0D1117 with vivid emerald-green and "
    "warm gold accents. Tall vertical 9:16 composition, strong hero framing "
    "with generous empty negative space reserved for data added later. Clean "
    "well-formed hands, simple hand pose. Absolutely no text, no numbers, no "
    "letters, no logos, no watermark, no UI elements."
)
# Mismo personaje que gusto en B, elevado a "profesional pulido" (consistencia).
CHAR_B = (
    "the same recurring everyperson styled as a polished young professional: "
    "warm light-brown skin, short tidy dark hair, refined adult proportions, "
    "calm confident expression, wearing a sharp modern smart-casual outfit with "
    "a subtle teal-green accent and premium tailoring, high-end character design"
)
VARIATIONS_B = {
    # b1: angulo heroe bajo + reflejo glossy = autoridad/cine
    "look_premiumB_1": (
        f"{CHAR_B}, composed in a low hero camera angle looking slightly up at "
        "the professional standing tall and confident on a sleek dark platform; "
        "dramatic cinematic three-point lighting with a strong emerald rim "
        "light and a subtle glossy floor reflection beneath. Authoritative, "
        "premium, cinematic. Keep the upper-right as empty navy negative space."
    ),
    # b2: profundidad de campo + bokeh de luz = atmosfera premium
    "look_premiumB_2": (
        f"{CHAR_B}, standing relaxed and confident, rendered with rich shallow "
        "depth of field and soft floating bokeh particles of emerald-green and "
        "gold light in the deep navy background, volumetric studio glow "
        "wrapping the figure. Atmospheric, premium, cinematic. Keep the right "
        "side as empty navy negative space for data."
    ),
    # b3: pedestal reflectante tipo keynote = staging ultra-limpio
    "look_premiumB_3": (
        f"{CHAR_B}, standing on a sleek minimalist reflective pedestal with "
        "soft ambient occlusion and a clean subtle floor reflection, lit like a "
        "high-end Apple-keynote product render, ultra-clean premium staging and "
        "crisp specular highlights. Keep the upper area as empty navy negative "
        "space for a large data figure."
    ),
    # b4: pose dinamica + estela de luz = energia de motion-graphics
    "look_premiumB_4": (
        f"{CHAR_B}, in a confident dynamic pose gesturing upward, with elegant "
        "emerald light streaks and a soft glowing energy trail rising beside "
        "them suggesting upward growth and momentum, premium cinematic finish "
        "with the energy of high-end motion-graphics. Keep the upper-right as "
        "empty navy negative space for an animated chart."
    ),
    # b5: minimal/quiet-luxury = sobrio y serio
    "look_premiumB_5": (
        f"{CHAR_B}, in a restrained minimal and elegant composition: the "
        "professional stands calmly with a simple confident pose, subdued "
        "premium lighting and a soft single emerald accent, lots of clean "
        "negative space, sophisticated quiet-luxury mood, understated and "
        "serious. Keep most of the top and right as empty navy negative space."
    ),
}


def _generate(slug: str, prompt: str, key: str, force: bool) -> bool:
    out = OUT_DIR / f"{slug}_1.png"
    if out.exists() and not force:
        print(f"LOOK skip {slug} (cache)")
        return False
    body = json.dumps({
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1536",
        "quality": "high",
        "n": 1,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    print(f"LOOK gen {slug} (gpt-image-1, high, 1024x1536)...")

    def _call():
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in RETRY_STATUS:
                raise RetryableError(f"HTTP {e.code}")
            raise SystemExit(f"gpt-image HTTP {e.code}: {e.read()[:200]}")
        except (urllib.error.URLError, TimeoutError) as e:
            raise RetryableError(f"red/timeout: {e}")

    data = with_retries(_call, what=f"gpt-image[{slug}]")
    out.write_bytes(base64.b64decode(data["data"][0]["b64_json"]))
    print(f"LOOK ok -> {out}")
    return True


def gen(letters, force: bool = False):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    key = load_env()["OPENAI_API_KEY"]
    n = 0
    for letter in letters:
        slug = f"look_premium_{letter}"
        if slug not in FLAVORS:
            raise SystemExit(f"flavor '{letter}' invalida (a|b|c)")
        prompt = f"{SCENE_BASE} {FLAVORS[slug]} {STYLE_PREMIUM}"
        if _generate(slug, prompt, key, force):
            n += 1
    if n:
        _log_expense(n, "motion-graphics premium (set base a|b|c)")


def gen_bset(force: bool = False):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    key = load_env()["OPENAI_API_KEY"]
    n = 0
    for slug, scene in VARIATIONS_B.items():
        prompt = f"{scene} {STYLE_PREMIUM_B}"
        if _generate(slug, prompt, key, force):
            n += 1
    if n:
        _log_expense(n, "refinamiento flavor B (dimensional premium)")


def _log_expense(n: int, label: str):
    from datetime import datetime
    line = (f"\n- {datetime.now().date()} · OpenAI gpt-image-1 (high 1024x1536) "
            f"x{n} · look-test premium · {label} · ~${0.17 * n:.2f} USD "
            f"· Dinero IA still madurado (eleccion de look, post slice v2)")
    try:
        with EXPENSES.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print("EXPENSE log warn:", e)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    if args and args[0].lower() == "bset":
        gen_bset(force=force)
    else:
        gen(args if args else ["a", "b", "c"], force=force)
