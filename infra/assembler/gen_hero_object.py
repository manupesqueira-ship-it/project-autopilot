# -*- coding: utf-8 -*-
# Genera el STILL "objeto-heroe" (gpt-image-1) cacheado por OBJETO para el
# arquetipo 3 del menu cerrado (SHOT_VOCABULARY.md). Este still es el ANCLA:
# se usa tal cual como input del i2v (Kling lo MUEVE -> el clip de paga) y
# tambien podria flotar estatico en codigo. Una imagen por slug -> se reusa.
#
# ESTILO BLOQUEADO (PLAN_MOTOR_AI_v3 §Estilo): caricatura-fino, premium, NO
# foto-realista. Fondo de estudio oscuro que CASA con el theme (#0D1117) para
# componer full-bleed sin alfa (el MP4 de Kling no trae canal alfa). Sin
# wordmark ni logo HORNEADO en el objeto (los logos van como vector real, no IA).
#
# Mismo patron que gen_coin.py / gen_caricature.py (load_env -> images/
# generations, gpt-image-1 quality=high, cache por slug, log de gasto).
#
# Uso: python gen_hero_object.py <slug> [--force]
import base64
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
OBJ_DIR = ROOT / "infra" / "remotion-render" / "public" / "objects"
EXPENSES = ROOT / "docs" / "EXPENSES.md"

sys.path.insert(0, str(ROOT / "infra" / "voz"))
from tts_timestamps import load_env  # noqa: E402

# Look comun del objeto-heroe: caricatura-fino (premium estilizado, NO foto-real),
# un solo objeto heroico centrado, estudio cinematografico oscuro que casa con el
# theme, rim-light dramatico, glow de acento semantico (teal/verde = marca), aire
# negativo generoso para el encuadre vertical 9:16. Sin texto ni marcas horneadas.
STYLE = (
    "premium stylized 3D illustration, refined caricature look (clearly NOT "
    "photorealistic, no sensor noise, no photographic grain), bold clean forms "
    "with slightly heroic exaggerated proportions, cinematic dark studio "
    "background in deep charcoal navy (#0D1117), dramatic rim lighting from the "
    "upper left, teal and emerald accent glow, subtle volumetric haze, one single "
    "hero object floating centered with generous negative space around it, "
    "tall vertical 9:16 composition, high craft, sharp edges, no text, no numbers, "
    "no brand name, no logo, no wordmark, no watermark, no hands"
)

# registro: slug -> descripcion del objeto (sin marca; el wordmark va aparte en vector).
OBJECT_PROMPTS = {
    "chip_ia": (
        "a powerful AI accelerator processor chip: a large square silicon die with "
        "a brushed metallic heatspreader, a ring of golden contact pins around the "
        "edge, and glowing teal and emerald circuit traces running across its "
        "surface, sitting on a sleek green circuit board, energy pulsing through "
        "the traces, the single hero object of the shot"
    ),
}


def gen(slug: str, force: bool = False) -> Path:
    if slug not in OBJECT_PROMPTS:
        raise SystemExit(
            f"sin prompt para objeto '{slug}' en OBJECT_PROMPTS "
            f"(agrega el slug con su descripcion)")
    return _generate(slug, OBJECT_PROMPTS[slug], force)


def gen_inline(slug: str, object_desc: str, force: bool = False) -> Path:
    """Variante para el DIRECTOR-LLM: usa la descripcion de objeto que el director
    escribio en el guion (props.object del BeatHeroShot) en vez del registro
    hardcoded. El STYLE bloqueado se ANEXA SIEMPRE -> el director elige el QUE
    (que objeto), no el COMO se ve (eso lo gobierna el estilo de la marca)."""
    if not (object_desc or "").strip():
        raise SystemExit(f"objeto vacio para '{slug}' (props.object del BeatHeroShot)")
    return _generate(slug, object_desc.strip(), force)


def _generate(slug: str, object_desc: str, force: bool = False) -> Path:
    OBJ_DIR.mkdir(parents=True, exist_ok=True)
    out = OBJ_DIR / f"{slug}.png"
    if out.exists() and not force:
        print(f"OBJECT skip {slug} (cache) -> {out}")
        return out

    key = load_env()["OPENAI_API_KEY"]
    prompt = f"{object_desc}. {STYLE}"
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
    print(f"OBJECT gen {slug} (gpt-image-1, high, 1024x1536)...")
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    b64 = data["data"][0]["b64_json"]
    out.write_bytes(base64.b64decode(b64))
    print(f"OBJECT ok -> {out}")
    _log_expense(slug)
    return out


def _log_expense(slug: str):
    from datetime import datetime
    line = (f"\n- {datetime.now().date()} · OpenAI gpt-image-1 (high 1024x1536) · "
            f"objeto-heroe '{slug}' · ~$0.19 USD · Dinero IA arquetipo 3 (still i2v, cacheada)")
    try:
        with EXPENSES.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print("EXPENSE log warn:", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("uso: python gen_hero_object.py <slug> [--force]")
    gen(sys.argv[1], force="--force" in sys.argv)
