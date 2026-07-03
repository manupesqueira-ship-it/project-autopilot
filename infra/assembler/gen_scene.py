# -*- coding: utf-8 -*-
# Genera la ESCENA caricatura-fino de un beat (still de arranque para i2v) con
# gpt-image-1. Mismo patron aprobado que gen_setpiece.py / gen_caricature.py.
#
# ARQUITECTURA (rechazo 2026-06-26 de Manuel): el reel debe ser UN solo mundo
# IA en MOVIMIENTO con la data exacta COMPUESTA encima en codigo. Por eso la
# escena se pide caricatura-fino, navy del theme, con ESPACIO NEGATIVO y CERO
# texto/numeros (la IA escribe las cifras mal -> el dato va en Remotion encima).
# Este still es el FRAME DE ARRANQUE; el movimiento lo da Kling (i2v_engine).
#
# Personaje recurrente COMPARTIDO entre escenas (CHAR) para ADN unico; en el
# slice de prueba se acepta varianza, se endurece (refs/edit) tras OK de Manuel.
#
# Uso:
#   python gen_scene.py colchon_b5            # 1 variante (cache)
#   python gen_scene.py colchon_b3 --n 2 --force
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

# Look de marca en CARICATURA-FINO (no foto-real): vector editorial limpio,
# navy #0D1117, glow de estudio, espacio negativo, SIN texto. premium != realista.
STYLE = (
    "flat vector editorial illustration, caricatura-fino style: bold clean "
    "outlines, smooth subtle gradients, slightly exaggerated friendly "
    "proportions, modern premium fintech illustration, minimal. Deep near-black "
    "navy background (hex 0D1117) with a soft cool studio glow and gentle warm "
    "gold rim light, calm cinematic depth. Tall vertical 9:16 composition with "
    "generous empty negative space reserved for data added later. Absolutely no "
    "text, no numbers, no letters, no logos, no watermark, no UI elements"
)

# Personaje recurrente (mismo en todas las escenas -> ADN unico / consistencia).
CHAR = (
    "the same recurring everyperson character: a friendly young adult with warm "
    "light-brown skin, short tidy dark hair, simple rounded cartoon facial "
    "features, wearing a clean teal hoodie and dark slim trousers, flat minimal "
    "shading"
)

# Mundo del colchon (concepto C aprobado por Manuel 2026-06-26): mundo VERTICAL,
# cornisa arriba, abajo el colchon mint-green que amortigua la caida. El still es
# el FRAME DE ARRANQUE de cada beat; el motion (caida/rebote/crecer) lo da i2v.
SCENES = {
    # b3 build: colchon chico empezando a inflarse (motion i2v: se infla/crece)
    "colchon_b3": (
        f"{CHAR}, standing confidently on a small high narrow ledge at the very "
        "top of a tall vertical scene. Far below them floats a soft rounded "
        "mint-green cushion that is still small and just starting to inflate. "
        "The character looks down toward it with hope. Keep the right third as "
        "empty navy negative space for data"
    ),
    # b4 timeline: colchon ya ancho y mullido (motion i2v: se ensancha, leve bob)
    "colchon_b4": (
        f"{CHAR}, on the same high ledge looking down calm and confident; far "
        "below, the soft rounded mint-green cushion is now wide, plump and "
        "bouncy, clearly bigger than before, soft and inviting with a faint warm "
        "glow. Keep the upper third as empty navy negative space for a timeline"
    ),
    # b5 climax: arranque de la CAIDA hacia el colchon grande (motion i2v: cae+rebota)
    "colchon_b5": (
        f"{CHAR}, at the very edge of the high ledge beginning to fall forward "
        "into a dive, body tilting downward with a clear sense of downward "
        "motion. Far below waits a big plump soft mint-green cushion ready to "
        "catch them. Keep the upper area as empty navy negative space for a "
        "large number"
    ),
}


def gen(slug: str, n: int = 1, force: bool = False):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if slug not in SCENES:
        raise SystemExit(f"sin prompt para escena '{slug}' en SCENES "
                         f"(disponibles: {sorted(SCENES)})")
    existing = sorted(OUT_DIR.glob(f"{slug}_*.png"))
    if existing and not force:
        print(f"SCENE skip {slug} (cache: {len(existing)} variantes)")
        return existing

    key = load_env()["OPENAI_API_KEY"]
    prompt = f"{SCENES[slug]}. {STYLE}"
    body = json.dumps({
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1536",   # portrait (el mas alto de gpt-image-1; i2v lo padea a 9:16)
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
    print(f"SCENE gen {slug} x{n} (gpt-image-1, high, 1024x1536)...")

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
    outs = []
    for i, item in enumerate(data["data"], 1):
        out = OUT_DIR / f"{slug}_{i}.png"
        out.write_bytes(base64.b64decode(item["b64_json"]))
        outs.append(out)
        print(f"SCENE ok -> {out}")
    _log_expense(slug, n)
    return outs


def _log_expense(slug: str, n: int):
    from datetime import datetime
    line = (f"\n- {datetime.now().date()} · OpenAI gpt-image-1 (high 1024x1536) "
            f"x{n} · escena '{slug}' · ~${0.17 * n:.2f} USD · Dinero IA "
            f"still caricatura-fino (arranque i2v, concepto colchon)")
    try:
        with EXPENSES.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print("EXPENSE log warn:", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("uso: python gen_scene.py <slug> [--n N] [--force]")
    slug = sys.argv[1]
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 1
    gen(slug, n=n, force="--force" in sys.argv)
