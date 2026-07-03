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
from director import direct  # noqa: E402  (triage de set-pieces; one-way: director NO importa proposer)

FILL = "<<rellenar"  # marca de hueco para Manuel / el planner

# CONGELAMIENTO DEL KIT (A1 del fork del freeze, 2026-06-19, decidido por Manuel):
# el proposer auto-selecciona SOLO del kit-10 (evergreen) + mini-set de noticia. El
# resto del catalogo (Donut/Waterfall/Bubble/BarRace/...) sigue REGISTRADO y se puede
# renderear a mano o desde un guion ya escrito; simplemente NO entra al muestreo
# automatico. "Archivar" = sacar del auto-pick, NO desregistrar. Para ensanchar el
# kit (opcion B), agrega tipos aqui.
#
# DOS sutilezas del kit frozen (verificadas contra el codigo, no obvias):
#   - Bars/Versus son LANDING (animan-y-se-quedan): validos en el kit, pero el
#     auto-pick del MEDIO los OMITE (solo el climax aterriza -R1-, ver pools abajo).
#     Quedan para guiones a mano / del planner. El auto-pick de datos efectivo es
#     {LineChart, Pictogram, Timeline}.
#   - Los hooks de SET-PIECE del director (BeatNapkin 'listo'; newspaper/phone/
#     chalkboard/ticket 'planeado') NO van en este set: los castea director.py por
#     TRIGGER de tema (no el auto-pick aleatorio). Un video de formula PUEDE traer
#     BeatNapkin fuera de FROZEN a proposito (carril deliberado, no fuga del freeze).
FROZEN = {
    # --- kit-10 evergreen ---
    "BeatKinetic", "BeatStatCallout",                            # hooks
    "BeatLineChart", "BeatBars", "BeatPictogram", "BeatVersus",  # datos
    "BeatMapZoom",                                               # wow
    "BeatBigNumber", "BeatHeroCoin",                             # climax
    "BeatCta",                                                   # cierre
    # --- mini-set de noticia (carril actualidad) ---
    "BeatNewsCard", "BeatTimeline", "BeatMultiMap",
}

# Pools derivados de los sets VIVOS del validador, ACOTADOS al kit frozen. Se
# adaptan si crece Root.tsx Y el tipo esta en FROZEN. Excluimos LANDING de wow/data
# para no pelear con R1 (solo el climax aterriza).
WOW_POOL = sorted((WOW & TYPES & FROZEN) - LANDING - {"BeatCharacter"})
DATA_POOL = sorted((DATA_VISUAL & TYPES & FROZEN) - LANDING)
CHART_POOL = sorted((CHARTS & TYPES & FROZEN) - LANDING - SPECT)  # graficas "seguras"
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
# OJO: este pool es el DEFECTO ALEATORIO; NO incluye los hooks de set-piece (p.ej.
# la servilleta), que NO deben salir al azar en un tema cualquiera -> solo los
# emite el director cuando el tema dispara sus triggers (ver _SETPIECE_HOOK_BUILDERS).
_HOOK_BUILDERS = {"BeatKinetic": _hook_kinetic, "BeatStatCallout": _hook_stat}


def _hook(tema, rng):
    kinds = [k for k in sorted(HOOK_TYPES) if k in _HOOK_BUILDERS] or ["BeatKinetic"]
    return _HOOK_BUILDERS.get(rng.choice(kinds), _hook_kinetic)(tema, rng)


# ----------------------------------------------------- hooks de SET-PIECE (director)
# Estos NO se castean al azar: el director (director.py) decide el carril y SOLO si
# el tema dispara los triggers del set-piece (p.ej. "regla del 72" -> servilleta)
# pasa su cast aqui. Los slots de copy/dato quedan '<<rellenar>>' -> Manuel/planner.
def _hook_napkin(tema, rng, cast):
    """Hook 'servilleta': una FORMULA/regla que cabe en una servilleta (BeatNapkin).
    Construido desde el cast del director (asset + slots promise/formula)."""
    napkin = Path(cast.get("asset", "setpieces/napkin_2.png")).stem  # -> "napkin_2"
    slots = cast.get("slots", {})
    vo = "Esta regla cabe en una servilleta y te dice que hacer con tu dinero hoy"
    return {"id": "b1_hook", "type": "BeatNapkin", "sfx": "impact",
            "trans": rng.choice(_TRANS), "vo": vo,
            "props": {"napkin": napkin,
                      "promise": slots.get("promise", f"{FILL}: la promesa que el numero responde>>"),
                      "formula": slots.get("formula", f"{FILL}: la formula EXACTA escrita a mano>>"),
                      "_fill": f"{FILL}: hook de servilleta para el tema '{tema}'>>"}}


def _sp_slug(cast):
    """Slug del asset foto-real del set-piece, o '' si aun NO hay foto concreta
    (asset 'por generar' / glob -> el componente cae a su fallback PROCEDURAL $0).
    Asi el set-piece rinde $0 sin la foto: el gasto gpt-image queda gateado hasta
    que Manuel genere+apruebe el asset y ponga el path real en el catalogo."""
    asset = str(cast.get("asset", ""))
    if not asset or "*" in asset or "por generar" in asset:
        return ""
    return Path(asset).stem


def _hook_newspaper(tema, rng, cast):
    """Hook 'periodico': un TITULAR de actualidad (BeatNewspaper, headline_set)."""
    slots = cast.get("slots", {})
    vo = "El titular de esta semana cambia por completo como deberias ver tu dinero ahora"
    return {"id": "b1_hook", "type": "BeatNewspaper", "sfx": "impact",
            "trans": rng.choice(_TRANS), "vo": vo,
            "props": {"paper": _sp_slug(cast),
                      "headline": slots.get("headline", f"{FILL}: titular EXACTO del brief>>"),
                      "stat": slots.get("stat", f"{FILL}: cifra resaltada del titular>>"),
                      "_fill": f"{FILL}: hook de periodico para el tema '{tema}'>>"}}


def _hook_phone(tema, rng, cast):
    """Hook 'telefono': una NOTIFICACION/app/saldo (BeatPhone, notification_in)."""
    slots = cast.get("slots", {})
    vo = "Mira la notificacion que le llego al telefono y lo que significa de verdad para ti"
    return {"id": "b1_hook", "type": "BeatPhone", "sfx": "impact",
            "trans": rng.choice(_TRANS), "vo": vo,
            "props": {"phone": _sp_slug(cast),
                      "screenLabel": slots.get("screen_label", f"{FILL}: que muestra la pantalla>>"),
                      "amount": slots.get("amount", f"{FILL}: monto/cifra EXACTA del brief>>"),
                      "_fill": f"{FILL}: hook de telefono para el tema '{tema}'>>"}}


def _hook_chalkboard(tema, rng, cast):
    """Hook 'pizarron': una LECCION paso a paso (BeatChalkboard, write_on multilinea)."""
    slots = cast.get("slots", {})
    vo = "Te lo explico en el pizarron paso a paso para que no te quede ninguna duda hoy"
    return {"id": "b1_hook", "type": "BeatChalkboard", "sfx": "impact",
            "trans": rng.choice(_TRANS), "vo": vo,
            "props": {"board": _sp_slug(cast),
                      "title": slots.get("title", f"{FILL}: titulo de la leccion>>"),
                      "steps": [f"{FILL}: paso 1>>", f"{FILL}: paso 2>>", f"{FILL}: resultado>>"],
                      "_fill": f"{FILL}: hook de pizarron para '{tema}'; steps = pasos EXACTOS del brief>>"}}


def _hook_ticket(tema, rng, cast):
    """Hook 'ticket': un PRECIO/recibo/gasto hormiga (BeatTicket, print_out)."""
    slots = cast.get("slots", {})
    vo = "Este ticket que parece inofensivo te esta costando mucho mas dinero de lo que crees"
    return {"id": "b1_hook", "type": "BeatTicket", "sfx": "impact",
            "trans": rng.choice(_TRANS), "vo": vo,
            "props": {"ticket": _sp_slug(cast),
                      "items": [{"label": f"{FILL}: concepto>>", "price": f"{FILL}: $>>"},
                                {"label": f"{FILL}: concepto>>", "price": f"{FILL}: $>>"}],
                      "total": slots.get("total", f"{FILL}: total resaltado EXACTO del brief>>"),
                      "_fill": f"{FILL}: hook de ticket para '{tema}'; items = conceptos EXACTOS del brief>>"}}


# Registro por COMPONENTE (el director da el comp del set-piece). Solo entran los
# que ya tienen componente construido; si crece el catalogo, se agrega aqui.
_SETPIECE_HOOK_BUILDERS = {
    "BeatNapkin": _hook_napkin,
    "BeatNewspaper": _hook_newspaper,
    "BeatPhone": _hook_phone,
    "BeatChalkboard": _hook_chalkboard,
    "BeatTicket": _hook_ticket,
}


def _setpiece_hook(tema, rng, cast):
    """Construye el hook de set-piece desde el cast del director, o None si su
    componente aun no existe (entonces el proposer cae al hook por defecto)."""
    builder = _SETPIECE_HOOK_BUILDERS.get(cast.get("comp"))
    return builder(tema, rng, cast) if builder else None


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
def _draft(tema, rng, n_data, cast_hook=None):
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

    # hook: set-piece del director si calza y tiene componente; si no, el de defecto.
    hook = (cast_hook and _setpiece_hook(tema, rng, cast_hook)) or _hook(tema, rng)
    beats = [hook]
    for j, t in enumerate(middle):
        beats.append(_generic(t, j + 2, rng))
    beats.append(_climax(tema, rng))
    beats.append(_cta(tema))
    return {"slug": _slugify(tema), "title": tema, "beats": beats}


def _director_brief(tema, brief):
    """Brief dict para el director (castea triggers): tema + texto libre del brief."""
    d = {"tema": tema}
    if isinstance(brief, str) and brief.strip():
        d["datos"] = brief  # mas superficie de triggers (open_loop/cifras del brief)
    return d


def _tag(guion, plan, lane):
    """Adjunta el plan del director al guion (visible en el gate de Manuel)."""
    if guion is None:
        return None
    hook = plan.get("hook") or {}
    guion["_director"] = {
        "lane": lane,  # carril EFECTIVO (set_piece solo si su hook entro de verdad)
        "hook_setpiece": hook.get("set_piece") if lane == "set_piece" else None,
        "hero_shot_posible": plan.get("hero_shot_posible"),
        "nota": "El director PROPONE; Manuel aprueba/edita en el gate antes de producir.",
    }
    return guion


def propose(tema, brief=None, ledger=None, n_data=2, seed=None, max_tries=500):
    """Devuelve un esqueleto de guion que pasa el validador (errors == []).

    n_data = cuantos beats de dato en la parte media (2 -> 6 beats, 3 -> 7).
    Si se pasa `ledger`, reintenta hasta hallar un combo visual NO repetido.
    Si el tema mismo esta repetido en el ledger, NINGUN reintento lo salva: se
    devuelve el mejor esqueleto y el llamador vera el error R9 de tema.

    TRIAGE (B4): consulta al director (director.py). Si el tema dispara un
    set-piece 'listo' con componente construido (p.ej. "regla del 72" ->
    servilleta) el hook del set-piece REEMPLAZA al de defecto. Si ese hook no
    logra pasar el validador (p.ej. R11 lo choca con el hook del video anterior),
    cae limpio al hook por defecto (kinetic/stat). hero_shot se SUGIERE en la
    metadata `_director`, nunca se auto-castea.
    """
    rng = random.Random(seed)
    plan = direct(_director_brief(tema, brief))
    cast_hook = plan.get("hook") if plan.get("lane") == "set_piece" else None
    if cast_hook and cast_hook.get("comp") not in _SETPIECE_HOOK_BUILDERS:
        cast_hook = None  # set-piece sin componente construido -> hook por defecto

    best = None
    # fase 1: hook del set-piece (preferente)
    if cast_hook:
        for _ in range(max_tries):
            guion = _draft(tema, rng, n_data, cast_hook=cast_hook)
            if not validate(guion, brief=brief, ledger=ledger)["errors"]:
                return _tag(guion, plan, "set_piece")
            if best is None:
                best = guion
    # fase 2: hooks por defecto (si no hubo set-piece o no paso -> rota la punta)
    for _ in range(max_tries):
        guion = _draft(tema, rng, n_data)
        if not validate(guion, brief=brief, ledger=ledger)["errors"]:
            return _tag(guion, plan, "default")
        if best is None:
            best = guion
    return _tag(best, plan, "default")


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
    d = (guion or {}).get("_director", {})
    print("\n-- director --", file=sys.stderr)
    print(f"  lane: {d.get('lane')}"
          + (f"  ->  hook set-piece: {d.get('hook_setpiece')}" if d.get("hook_setpiece") else ""),
          file=sys.stderr)
    res = validate(guion, brief=brief, ledger=ledger)
    print("\n-- validador --", file=sys.stderr)
    for w in res["warnings"]:
        print("  WARN:", w, file=sys.stderr)
    print("  " + ("PASS" if not res["errors"] else "FAIL: " + "; ".join(res["errors"])),
          file=sys.stderr)
    return 0 if not res["errors"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
