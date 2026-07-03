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

# Estilo de ALTO DETALLE para caricaturas de figuras publicas TOPICAS (b-roll).
# Manuel 2026-06-26: para una figura real, ultra-realista "se ve que es AI";
# mejor una caricatura MUY detallada y bien hecha -> lee como CRAFT, no como AI
# fallido. Mas pictorica/detallada que el STYLE plano de las mascotas recurrentes.
STYLE_DETAILED = (
    "premium highly-detailed editorial caricature illustration, richly rendered "
    "with painterly detail and fine texture, slightly exaggerated characterful "
    "features with a larger expressive head, dramatic studio lighting with a "
    "subtle emerald-green rim light and a warm gold key light, set against a deep "
    "near-black navy studio background hex 0D1117 with soft cinematic depth, "
    "high-end illustration craft, NOT photorealistic and NOT flat vector, "
    "characterful three-quarter bust composition with some empty navy negative "
    "space beside the figure, full-bleed image filling the entire frame edge to "
    "edge, no decorative border, no matte frame, no paper margin, no canvas edge, "
    "no text, no numbers, no letters, no logos, no flag, no watermark"
)

# Override de estilo por slug (default = STYLE plano de mascota).
CHARACTER_STYLE = {
    "milei": STYLE_DETAILED,
    "bukele_cine": STYLE_DETAILED,
}

# registro: slug -> descripcion del look (sin nombrar a la persona real)
CHARACTER_PROMPTS = {
    "bukele": (
        "a charismatic young Latin American president in his early 40s, neat short "
        "dark hair, well groomed short dark beard, wearing a dark navy blazer over "
        "a white shirt with no tie and a backwards black baseball cap, confident "
        "calm half-smile, arms crossed"
    ),
    # b-roll cinematografico (arq 4 que SE MUEVE via i2v): version resuelta/seria
    # del MISMO look iconico para el reel El Salvador (tension FMI, $16k, conviccion).
    # Usa STYLE_DETAILED (pictorica, navy 0D1117 + rim esmeralda) = nuestro mundo.
    "bukele_cine": (
        "a charismatic young Latin American president in his early 40s, neat short "
        "dark hair, well groomed short dark beard, wearing a dark navy blazer over "
        "a black shirt and a backwards black baseball cap, serious resolute "
        "determined expression gazing off into the distance, mouth closed, NOT "
        "smiling, calm and composed under pressure, quiet unshakeable conviction"
    ),
    # opositor generico (NO una persona real): economista/banquero esceptico
    "economista": (
        "a skeptical middle-aged economist, graying hair combed back, rectangular "
        "glasses, neatly trimmed gray beard, wearing a charcoal gray suit with a "
        "deep red tie, one eyebrow raised in doubt, slight frown, arms crossed in a "
        "guarded posture, serious analytical expression"
    ),
    # figura topica (NO nombrada al generador): el look iconico de un libertario
    # argentino de la motosierra. La VOZ lo nombra; la caricatura lo evoca.
    "milei": (
        "a fiery Argentine libertarian firebrand politician in his mid-fifties, "
        "with a very distinctive wild unkempt tousled mane of dark brown hair and "
        "long prominent bushy mutton-chop sideburns, clean-shaven, intense "
        "charismatic wide-eyed impassioned expression as if mid-speech, wearing a "
        "black leather jacket over a dark shirt, energetic dynamic posture"
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
    prompt = f"{CHARACTER_PROMPTS[slug]}. {CHARACTER_STYLE.get(slug, STYLE)}"
    # Figuras de alto detalle (CHARACTER_STYLE) hornean su fondo navy de marca
    # -> opaco; las mascotas planas van transparentes para componer sobre escena.
    bg = "opaque" if slug in CHARACTER_STYLE else "transparent"
    body = json.dumps({
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1536",
        "quality": "high",
        "background": bg,
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
    from datetime import datetime
    line = (f"\n- {datetime.now().date()} · OpenAI gpt-image-1 (high 1024x1536) · caricatura "
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
