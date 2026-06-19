# -*- coding: utf-8 -*-
"""
caption.py - Arma el CAPTION + hashtags de un guion, listo para Instagram/TikTok.

QUE HACE: dado `guion_<slug>.json`, produce el texto de descripcion (caption) que
acompana al reel, siguiendo el estandar VIVO de la marca
(projects/dinero-ia/templates/caption_template.md): hook < ~100 chars, valor con
la cifra EXACTA y moneda explicita, CTA + open-loop + pregunta de engagement,
6-7 hashtags y la linea de disclaimer. $0, solo stdlib, SIN llamar a ninguna API.

DOS FUENTES (en orden):
  1) BLOQUE AUTORADO: si el guion trae un objeto top-level `caption` (lo escribo yo
     en sesion al autorar el guion), se usa ese copy pulido.
  2) FALLBACK desde los beats: si no hay bloque, se deriva del propio guion
     (hook = 1a frase del beat hook; valor = beat climax; CTA + open-loop = BeatCta).
     Asi el pipeline NUNCA se traba por falta de caption; el gate humano (Telegram)
     atrapa lo que no convenza.

REGLA DE MARCA (dura): la cuenta se llama "Dinero LATAM" y NUNCA dice "IA"/"AI" en
el caption (resta confianza en finanzas). Si el texto contiene 'IA'/'AI' como
palabra suelta o 'inteligencia artificial', se AVISA por stderr (no se bloquea:
hay temas que hablan del boom de chips sin nombrar 'IA').

USO (CLI):
  python caption.py ..\\assembler\\guion_edu_interes_compuesto.json
  python caption.py <guion.json> --platform tiktok
  python caption.py <guion.json> --out ..\\assembler\\out\\<slug>\\out_caption_ig.txt
  python caption.py <guion.json> --both        # imprime IG y TikTok separados

Tambien se importa desde el orquestador (producir.py):
  from caption import build_caption, write_caption_files
"""
import argparse
import json
import re
import sys
from pathlib import Path

# --- Banco de hashtags (del estandar vivo; rotar para no spamear) ------------
AMPLIOS = ["finanzaspersonales", "inversiones", "dinero", "educacionfinanciera"]
NICHO = ["libertadfinanciera", "invertir", "ahorro", "finanzas", "interescompuesto"]
GEO = {
    "mexico": ["mexico", "finanzasmexico", "pesos"],
    "argentina": ["argentina", "finanzasargentina"],
    "colombia": ["colombia"],
    "latam": ["latam", "finanzaslatam"],
}

DISCLAIMER = "Contenido educativo, no es asesoría financiera."
MONEY_EMOJI = ["\U0001f4b8", "\U0001f4c8", "\U0001f4b0"]  # 💸 📈 💰
CTA_EMOJI = "\U0001f449"  # 👉

# 'IA'/'AI' como palabra suelta (no como substring de 'financiera', 'dia', etc.).
_BRAND_IA = re.compile(r"(?<![A-Za-z])(IA|AI)(?![A-Za-z])")
_IA_FRASE = re.compile(r"inteligencia artificial", re.IGNORECASE)

# Palabras-clave -> hashtag de nicho que conviene forzar si el tema lo toca.
_TOPICAL = [
    (("interes compuesto", "interés compuesto", "compuesto"), "interescompuesto"),
    (("invertir", "inversion", "inversión", "invierte"), "invertir"),
    (("ahorro", "ahorrar", "ahorra"), "ahorro"),
    (("libertad financiera", "retiro", "jubil"), "libertadfinanciera"),
]


# ----------------------------------------------------------------- utilidades
def _load_guion(guion):
    if isinstance(guion, (str, Path)):
        return json.loads(Path(guion).read_text(encoding="utf-8-sig"))
    return guion


def _det_index(seed: str, n: int) -> int:
    """Indice 0..n-1 determinista por slug (rota estable entre videos, sin azar)."""
    return (sum(ord(c) for c in seed) % n) if n else 0


def _sentences(text: str):
    text = (text or "").strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?…])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _clip(text: str, limit: int) -> str:
    """Recorta a <= limit en frontera de palabra, agregando '…' si hace falta."""
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(" ,;:.") + "…"


def _has_brand_ia(text: str) -> bool:
    return bool(_BRAND_IA.search(text or "")) or bool(_IA_FRASE.search(text or ""))


def _blob(guion: dict) -> str:
    """Texto plano del guion (title + vo + valores de props) para detectar geo/topico.
    Incluye props porque la MONEDA vive ahi (props.suffix = ' MXN' / ' USD')."""
    bits = [guion.get("title", "")]
    for b in guion.get("beats", []):
        bits.append(b.get("vo", ""))
        for v in (b.get("props") or {}).values():
            if isinstance(v, str):
                bits.append(v)
    return " ".join(bits).lower()


def _find_beat(beats, *, idx=None, id_sub=None, types=None):
    if idx is not None and 0 <= idx < len(beats):
        return beats[idx]
    for b in beats:
        if id_sub and id_sub in (b.get("id") or ""):
            return b
        if types and b.get("type") in types:
            return b
    return None


# -------------------------------------------------- deteccion geo / hashtags
def _geo_for(slug: str, blob: str) -> str:
    s = (slug or "").lower()
    if s.startswith("mx_"):
        return "mexico"
    if s.startswith("ar_"):
        return "argentina"
    if s.startswith(("co_", "col_")):
        return "colombia"
    b = (blob or "").lower()
    if any(k in b for k in ("peso mexicano", "cetes", "banxico", "superpeso", "mxn", "mexic")):
        return "mexico"
    if any(k in b for k in ("dolar mep", "dólar mep", "blue", "argentin", "bcra", "indec")):
        return "argentina"
    if "colombia" in b:
        return "colombia"
    return "latam"


def _hashtags(guion: dict, n_total: int) -> list:
    """Selecciona hashtags: 2-3 amplios + 2-3 nicho + 1-2 geo, deterministas por slug.
    Fuerza tags topicales si el tema los toca; rota el resto estable por slug."""
    slug = guion.get("slug", "video")
    blob = _blob(guion)

    forced = [tag for kws, tag in _TOPICAL if any(k in blob for k in kws)]

    geo_key = _geo_for(slug, blob)
    geo_tags = GEO.get(geo_key, GEO["latam"])
    n_geo = 1 if n_total <= 5 else 2
    geo_sel = geo_tags[:n_geo]

    # cuantos amplios/nicho caben tras geo + forzados
    room = max(0, n_total - len(geo_sel))
    nicho_forced = [t for t in forced if t in NICHO]
    n_amp = 3 if room >= 6 else 2
    n_amp = min(n_amp, max(1, room - 2))

    off_a = _det_index(slug, len(AMPLIOS))
    amplios_sel = [AMPLIOS[(off_a + i) % len(AMPLIOS)] for i in range(n_amp)]

    out = []
    for t in nicho_forced + amplios_sel:  # nicho topical primero (mas relevante)
        if t not in out:
            out.append(t)
    # rellenar nicho rotado hasta dejar hueco para geo
    off_n = _det_index(slug, len(NICHO))
    i = 0
    while len(out) < (n_total - len(geo_sel)) and i < 2 * len(NICHO):
        cand = NICHO[(off_n + i) % len(NICHO)]
        if cand not in out:
            out.append(cand)
        i += 1
    out.extend(g for g in geo_sel if g not in out)
    return out[:n_total]


# ----------------------------------------------------- materiales del guion
def _materials(guion: dict) -> dict:
    """Reune {hook, valor, cta, open_loop, pregunta, emoji} del bloque autorado o,
    si no hay, derivado de los beats. Devuelve strings ya listos (sin hashtags)."""
    beats = guion.get("beats", [])
    authored = guion.get("caption") or {}

    hook_beat = _find_beat(beats, idx=0)
    cta_beat = _find_beat(beats, id_sub="cta", types={"BeatCta"}) or _find_beat(beats, idx=len(beats) - 1)
    climax_beat = (_find_beat(beats, id_sub="climax",
                              types={"BeatBigNumber", "BeatHeroCoin"})
                   or _find_beat(beats, idx=max(0, len(beats) - 2)))

    # HOOK
    hook = authored.get("hook")
    if not hook:
        hs = _sentences(hook_beat.get("vo", "") if hook_beat else "")
        hook = hs[0] if hs else (guion.get("title", "") or "")
        if len(hook) > 100 and len(hs) and "." in hook:  # no partir cifras a la mitad
            hook = hs[0]
    hook = _clip(hook, 100)

    # VALOR (cifra exacta): bloque autorado, o el vo del climax (lleva el payoff)
    valor = authored.get("valor") or authored.get("cuerpo")
    if not valor and climax_beat:
        vs = _sentences(climax_beat.get("vo", ""))
        valor = " ".join(vs[:2]) if vs else ""
    valor = (valor or "").strip()

    # CTA + open-loop + pregunta
    cta = authored.get("cta")
    open_loop = authored.get("open_loop")
    if cta_beat:
        props = cta_beat.get("props", {})
        cta = cta or props.get("text") or ""
        open_loop = open_loop or props.get("sub") or ""
    cta = (cta or "").strip()
    open_loop = (open_loop or "").strip()
    if open_loop and not re.match(r"(?i)\s*mañana", open_loop):
        open_loop = "Mañana: " + open_loop
    pregunta = (authored.get("pregunta") or "").strip()

    emoji = authored.get("emoji") or MONEY_EMOJI[_det_index(guion.get("slug", "x"), len(MONEY_EMOJI))]
    return {"hook": hook, "valor": valor, "cta": cta,
            "open_loop": open_loop, "pregunta": pregunta, "emoji": emoji}


# --------------------------------------------------------------- ensamblado
def build_caption(guion, platform: str = "instagram") -> str:
    """Devuelve el caption final (string) para 'instagram' o 'tiktok'."""
    g = _load_guion(guion)
    m = _materials(g)
    tiktok = platform.lower() == "tiktok"
    n_tags = 5 if tiktok else 7
    authored_tags = (g.get("caption") or {}).get("hashtags")
    if authored_tags:
        tags = [h.lstrip("#") for h in authored_tags][:n_tags]
    else:
        tags = _hashtags(g, n_tags)
    tagline = " ".join("#" + t for t in tags)

    hook = f"{m['hook']} {m['emoji']}".strip()

    # Cierre: CTA + open-loop + pregunta
    cierre_bits = []
    if m["cta"]:
        cierre_bits.append(f"{m['cta']} {CTA_EMOJI}")
    if m["open_loop"]:
        cierre_bits.append(m["open_loop"])
    if m["pregunta"]:
        cierre_bits.append(m["pregunta"])
    cierre = "\n".join(cierre_bits)

    if tiktok:
        # mas corto: hook + 1a frase de valor + cierre compacto
        valor = _sentences(m["valor"])
        valor = valor[0] if valor else m["valor"]
        bloques = [hook]
        if valor:
            bloques.append(valor)
        if cierre:
            bloques.append(cierre)
        bloques.append(tagline)
        bloques.append(DISCLAIMER)
    else:
        bloques = [hook]
        if m["valor"]:
            bloques.append(m["valor"])
        if cierre:
            bloques.append(cierre)
        bloques.append(tagline)
        bloques.append(DISCLAIMER)

    text = "\n\n".join(b for b in bloques[:-2] if b)
    text += "\n\n" + bloques[-2] + "\n" + bloques[-1]

    if _has_brand_ia(text):
        print("[caption] OJO: el texto contiene 'IA'/'AI'/'inteligencia artificial'. "
              "La marca NO debe nombrar IA en el caption — revisa antes de publicar.",
              file=sys.stderr)
    if len(text) > 2200:  # limite duro de Instagram
        print(f"[caption] OJO: caption de {len(text)} chars > 2200 (limite IG).",
              file=sys.stderr)
    return text


def write_caption_files(guion, outdir=None) -> dict:
    """Escribe out_caption_ig.txt (caption CRUDO de IG, el que consume enqueue) y
    out_caption_tiktok.txt. Devuelve {'instagram': ruta, 'tiktok': ruta}."""
    g = _load_guion(guion)
    if outdir is None:
        slug = g.get("slug", "video")
        outdir = Path(__file__).resolve().parents[1] / "assembler" / "out" / slug
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for plat, fname in (("instagram", "out_caption_ig.txt"),
                        ("tiktok", "out_caption_tiktok.txt")):
        p = outdir / fname
        p.write_text(build_caption(g, platform=plat) + "\n", encoding="utf-8")
        paths[plat] = p
    return paths


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("guion", help="ruta a guion_<slug>.json")
    ap.add_argument("--platform", choices=["instagram", "tiktok"], default="instagram")
    ap.add_argument("--both", action="store_true", help="imprime IG y TikTok")
    ap.add_argument("--out", help="escribe el caption (de --platform) a este archivo")
    ap.add_argument("--write-files", action="store_true",
                    help="escribe out_caption_ig.txt + out_caption_tiktok.txt en out/<slug>/")
    args = ap.parse_args()

    g = _load_guion(args.guion)
    if args.write_files:
        paths = write_caption_files(g)
        for plat, p in paths.items():
            print(f"[caption] {plat}: {p}")
        return

    if args.both:
        print("==================== INSTAGRAM ====================")
        print(build_caption(g, "instagram"))
        print("\n==================== TIKTOK ====================")
        print(build_caption(g, "tiktok"))
    else:
        text = build_caption(g, args.platform)
        if args.out:
            Path(args.out).write_text(text + "\n", encoding="utf-8")
            print(f"[caption] escrito: {args.out}")
        else:
            print(text)


if __name__ == "__main__":
    main()
