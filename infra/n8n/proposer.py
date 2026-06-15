# -*- coding: utf-8 -*-
"""
Proposer del "director" de Dinero IA: arma un ESQUELETO de guion.

Dado un tema (+ brief opcional) genera la ESTRUCTURA de un guion: solo los
tipos de beat + huecos ("<<rellenar: ...>>") para copy y datos, muestreando del
catalogo VIVO de beats (lo que esta registrado en Root.tsx, leido por
validator.registered_beat_types()). El esqueleto SIEMPRE pasa el validador
(R1-R9): genera la estructura, corre validate() y reintenta hasta que no haya
errores. Es $0 y offline: NO llama a la API del planner.

El planner real (Claude) sigue siendo quien escribe el copy y mete las cifras
EXACTAS del brief. El proposer solo le da la cancha: que tipos de beat usar y en
que orden para cumplir el arco, sin repetir combos del ledger.

API:
    from proposer import propose
    guion = propose(tema, brief=None, ledger=None, n_data=2, seed=None)

CLI:
    python proposer.py "Tema del video" [--brief b.txt] [--ledger] [--seed N] [--out g.json]
"""
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "assembler"))

from validator import (  # noqa: E402
    validate, _norm,
    TYPES, CHARTS, SPECT, WOW, DATA_VISUAL, CLIMAX_TYPES, LANDING, HOOK_TYPES,
)

FILL = "<<rellenar"  # marca de hueco para Manuel / el planner

# Pools derivados de los sets VIVOS del validador (se adaptan si crece Root.tsx).
# Excluimos LANDING de wow/data para no pelear con R1 (solo el climax aterriza).
WOW_POOL = sorted((WOW & TYPES) - LANDING - {"BeatCharacter"})
DATA_POOL = sorted((DATA_VISUAL & TYPES) - LANDING)
CHART_POOL = sorted((CHARTS & TYPES) - LANDING - SPECT)  # graficas "seguras"
# wow que NO son data_visual (sirven de contexto sin sumar al conteo de datos)
WOW_CONTEXT = sorted(t for t in WOW_POOL if t not in DATA_VISUAL)

_SFX = ["whoosh", "tick", "impact"]
_TRANS = ["scrollUp", "zoomPunch", "flashWhite"]


def _slugify(tema):
    words = [_norm(w) for w in str(tema).split() if _norm(w)]
    slug = "_".join(words[:4]) or "video"
    return slug[:40]


def _short(t):
    return _norm(t.replace("Beat", "")) or "beat"


# ---------------------------------------------------------------- scaffolders
def _hook_kinetic(tema, rng):
    vo = "Nadie te conto esto y por eso hoy lo vas a entender de golpe"
    words = vo.split()
    lines = []
    for k in range(0, len(words), 3):
        chunk = words[k:k + 3]
        lines.append([
            {"text": w, **({"accent": True} if idx == 0 else {})}
            for idx, w in enumerate(chunk)
        ])
    return {"id": "b1_hook", "type": "BeatKinetic", "sfx": "impact",
            "trans": rng.choice(_TRANS), "vo": vo,
            "props": {"lines": lines,
                      "_fill": f"{FILL}: reescribe el hook con la tension del tema '{tema}'>>"}}


def _hook_stat(tema, rng):
    # Hook alterno: una cifra-shock POP de apertura (NO word-by-word). Distinto
    # ritmo que el kinetic -> rota la apertura sin componente nuevo.
    vo = "Esta sola cifra deberia bastar para que cambies como ves tu dinero hoy"
    return {"id": "b1_hook", "type": "BeatStatCallout", "sfx": "impact",
            "trans": rng.choice(_TRANS), "vo": vo,
            "props": {"stat": f"{FILL}: cifra-shock EXACTA del brief>>",
                      "context": f"{FILL}: que significa esa cifra en una linea>>",
                      "_fill": f"{FILL}: hook de impacto para el tema '{tema}'>>"}}


# El proposer solo emite hooks que sabe construir, aunque HOOK_TYPES crezca.
_HOOK_BUILDERS = {"BeatKinetic": _hook_kinetic, "BeatStatCallout": _hook_stat}


def _hook(tema, rng):
    kinds = [k for k in sorted(HOOK_TYPES) if k in _HOOK_BUILDERS] or ["BeatKinetic"]
    return _HOOK_BUILDERS.get(rng.choice(kinds), _hook_kinetic)(tema, rng)


def _placeholder_props(t):
    note = f"{FILL}: datos EXACTOS del brief para {t}>>"
    base = {"caption": f"{FILL}: titulo corto>>", "_fill": note}
    if t in CHARTS:
        base["points"] = []          # serie cruda a llenar
        base["label"] = f"{FILL}: etiqueta>>"
    if t == "BeatPictogram":
        base.update({"total": 100, "highlight": None})
    if t == "BeatTimeline":
        base["nodes"] = []
    if t == "BeatMapZoom":
        base.update({"countryName": f"{FILL}: pais en ingles>>",
                     "iso2": "XX", "label": f"{FILL}: pais>>",
                     "sublabel": f"{FILL}: dato del pais>>"})
    if t == "BeatScoreboard":
        base["rows"] = []
    return base


def _generic(t, pos, rng):
    vo = ("Aqui va el bloque que explica con datos el punto clave de la "
          "historia para que la audiencia lo sienta de verdad.")
    return {"id": f"b{pos}_{_short(t)}", "type": t, "sfx": rng.choice(_SFX),
            "trans": rng.choice(_TRANS), "vo": vo, "props": _placeholder_props(t)}


def _climax_bignumber(tema, rng):
    vo = ("La cifra que lo resume todo y que tienes que recordar es una "
          "cantidad que cambia la conversacion por completo en dolares")
    return {"id": "b_climax", "type": "BeatBigNumber", "sfx": "impact",
            "trans": rng.choice(_TRANS), "vo": vo,
            "cues": {"countEndWord": "dolares"},
            "props": {"value": None, "prefix": "$", "suffix": " USD",
                      "caption": f"{FILL}: que representa la cifra>>",
                      "subline": f"{FILL}: contexto>>", "color": "#00D9A5",
                      "_fill": f"{FILL}: value = cifra EXACTA del brief; la voz puede redondearla>>"}}


def _climax_herocoin(tema, rng):
    # Climax alterno: la cifra protagonista sobre la moneda 3D (Blender). Misma
    # funcion narrativa que el BigNumber pero otro acabado -> rota el clima.
    vo = ("La cifra que lo resume todo y que tienes que recordar es una "
          "cantidad enorme medida en dolares")
    return {"id": "b_climax", "type": "BeatHeroCoin", "sfx": "impact",
            "trans": rng.choice(_TRANS), "vo": vo,
            "cues": {"countEndWord": "dolares"},
            "props": {"value": None, "prefix": "$", "suffix": " USD",
                      "caption": f"{FILL}: que representa la cifra>>",
                      "subline": f"{FILL}: contexto>>", "accentColor": "#D4A574",
                      "_fill": f"{FILL}: value = cifra EXACTA del brief; la voz puede redondearla>>"}}


# El proposer solo emite climax que sabe construir, aunque CLIMAX_TYPES crezca.
_CLIMAX_BUILDERS = {"BeatBigNumber": _climax_bignumber, "BeatHeroCoin": _climax_herocoin}


def _climax(tema, rng):
    kinds = [k for k in sorted(CLIMAX_TYPES) if k in _CLIMAX_BUILDERS] or ["BeatBigNumber"]
    return _CLIMAX_BUILDERS.get(rng.choice(kinds), _climax_bignumber)(tema, rng)


def _cta(tema):
    return {"id": "b_cta", "type": "BeatCta", "sfx": "whoosh",
            "vo": "Sigueme para no perderte lo que viene manana sobre tu dinero",
            "props": {"text": f"{FILL}: CTA>>", "boldWord": "dinero",
                      "sub": f"{FILL}: manana <<open loop del siguiente video>>>>"}}


# ------------------------------------------------------------------- draft
def _draft(tema, rng, n_data):
    # Para 3+ datos, el wow va de CONTEXTO (no suma al conteo de datos) y asi no
    # se rebasan los 3 tipos de dato del arco (R4 avisa si hay >3).
    wow_pool = WOW_CONTEXT if (n_data >= 3 and WOW_CONTEXT) else WOW_POOL
    wow = rng.choice(wow_pool)

    pool = [t for t in DATA_POOL if t != wow]
    data = rng.sample(pool, k=min(n_data, len(pool)))

    # R8: garantizar >=1 grafica de datos entre wow + datos.
    if wow not in CHARTS and not any(t in CHARTS for t in data):
        choices = [t for t in CHART_POOL if t != wow and t not in data]
        if choices:
            data[0] = rng.choice(choices)

    middle = [wow] + data
    rng.shuffle(middle)

    beats = [_hook(tema, rng)]
    for j, t in enumerate(middle):
        beats.append(_generic(t, j + 2, rng))
    beats.append(_climax(tema, rng))
    beats.append(_cta(tema))
    return {"slug": _slugify(tema), "title": tema, "beats": beats}


def propose(tema, brief=None, ledger=None, n_data=2, seed=None, max_tries=500):
    """Devuelve un esqueleto de guion que pasa el validador (errors == []).

    n_data = cuantos beats de dato en la parte media (2 -> 6 beats, 3 -> 7).
    Si se pasa `ledger`, reintenta hasta hallar un combo visual NO repetido.
    Si el tema mismo esta repetido en el ledger, NINGUN reintento lo salva: se
    devuelve el mejor esqueleto y el llamador vera el error R9 de tema.
    """
    rng = random.Random(seed)
    best = None
    for _ in range(max_tries):
        guion = _draft(tema, rng, n_data)
        res = validate(guion, brief=brief, ledger=ledger)
        if not res["errors"]:
            return guion
        if best is None:
            best = guion
    return best


# --------------------------------------------------------------------- CLI
def _cli(argv):
    if not argv or argv[0].startswith("--"):
        print(__doc__)
        return 2
    tema = argv[0]
    brief = None
    if "--brief" in argv:
        brief = Path(argv[argv.index("--brief") + 1]).read_text(encoding="utf-8-sig")
    ledger = None
    if "--ledger" in argv:
        from ledger import Ledger
        ledger = Ledger()
    seed = None
    if "--seed" in argv:
        seed = int(argv[argv.index("--seed") + 1])
    n_data = 2
    if "--ndata" in argv:
        n_data = int(argv[argv.index("--ndata") + 1])

    guion = propose(tema, brief=brief, ledger=ledger, n_data=n_data, seed=seed)
    out = json.dumps(guion, ensure_ascii=False, indent=2)
    if "--out" in argv:
        Path(argv[argv.index("--out") + 1]).write_text(out, encoding="utf-8")
    print(out)
    res = validate(guion, brief=brief, ledger=ledger)
    print("\n-- validador --", file=sys.stderr)
    for w in res["warnings"]:
        print("  WARN:", w, file=sys.stderr)
    print("  " + ("PASS" if not res["errors"] else "FAIL: " + "; ".join(res["errors"])),
          file=sys.stderr)
    return 0 if not res["errors"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
