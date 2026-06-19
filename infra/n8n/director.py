# -*- coding: utf-8 -*-
"""
Director VISUAL de Dinero LATAM: el nodo que decide QUE PASA en cada video.

Manuel no puede guiar la creatividad de cada video a mano. Este nodo lo hace por
el, pero CON BARANDALES: NUNCA inventa de un prompt en blanco. Castea SOLO del
vocabulario CERRADO de `setpiece_catalog.json` (set-pieces foto-reales + motions
$0 mapeadas a beats REALES). Asi se evita el "cambio no pedido" (caso divide-72):
la creatividad es casting, no invencion.

Que hace, dado un tema/brief:
  1. arma el texto buscable (tema + open_loop + datos + categoria),
  2. puntua cada set-piece 'listo' por cuantos de sus triggers aparecen,
  3. decide el CARRIL (lane):
       - set_piece -> un objeto del catalogo calza con el tema (castea hook),
       - default   -> nada calza -> hook por defecto del proposer (kinetic/stat),
       (hero_shot es bespoke/planeado -> se SUGIERE a Manuel, no se auto-castea),
  4. emite un PLAN DE TOMA (shot plan) con comp + motion + slots '<<rellenar>>'.

El director PROPONE; Manuel aprueba/edita en el gate ANTES de producir. El copy
exacto de los slots queda '<<rellenar>>' -> lo decide Manuel / el planner, NUNCA
el director. $0 y offline (no llama a ninguna API). Compone con proposer.py: si
el lane es set_piece, el hook del director REEMPLAZA el hook por defecto del
proposer; el resto del arco (wow/datos/climax/cta) lo sigue armando el proposer.

API:
    from director import direct
    plan = direct(brief)          # brief = dict tema de temas_cola.json o {"tema": ...}

CLI:
    python director.py <id-de-tema>            # busca el id en temas_cola.json
    python director.py --tema "texto libre"    # castea sobre texto suelto
    python director.py edu_regla_72 --out plan.json
"""
import json
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
CATALOG = HERE / "setpiece_catalog.json"
TEMAS = HERE / "temas_cola.json"

FILL = "<<rellenar"  # misma marca de hueco que proposer.py / el planner


def _norm(s):
    """minusculas + sin acentos, para casar triggers contra el texto del brief."""
    s = unicodedata.normalize("NFKD", str(s).lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _brief_text(brief):
    """texto buscable del brief: tema + open_loop + datos + categoria."""
    parts = [brief.get(k, "") for k in ("tema", "open_loop", "datos", "categoria")]
    return _norm(" \n ".join(p for p in parts if p))


def _hits(triggers, text):
    """los triggers (en orden de catalogo) que aparecen en el texto del brief."""
    return [t for t in triggers if _norm(t) in text]


def _cast(catalog, rol, text):
    """mejor set-piece 'listo' de ese rol por # de triggers que casan (>=1)."""
    best = None
    for sp in catalog["set_pieces"]:
        if sp.get("estado") != "listo" or sp.get("rol") != rol:
            continue
        hits = _hits(sp.get("triggers", []), text)
        if hits and (best is None or len(hits) > len(best[1])):
            best = (sp, hits)
    return best


def _motion(catalog, motion_id):
    return next((m for m in catalog.get("motions", []) if m["id"] == motion_id), {})


def _toma(catalog, cast):
    """convierte un cast (set_piece, hits) en un bloque de plan de toma."""
    sp, hits = cast
    md = _motion(catalog, sp.get("motion"))
    return {
        "set_piece": sp["id"],
        "rol": sp.get("rol"),
        "comp": sp["comp"],
        "asset": sp["asset"],
        "motion": sp.get("motion"),
        "motion_detalle": md.get("para"),
        "costo": md.get("costo", "$0 Remotion"),
        "slots": {k: f"{FILL}: {v}>>" for k, v in sp.get("slots", {}).items()},
        "match": {"score": len(hits), "triggers": hits},
    }


def direct(brief, catalog=None):
    """Plan de toma para un brief. PROPONE (no decide); Manuel aprueba en gate."""
    catalog = catalog or _load(CATALOG)
    text = _brief_text(brief)
    como = catalog.get("como_se_usa", {})

    hook = _cast(catalog, "hook", text)
    climax = _cast(catalog, "climax", text)

    if hook:
        lane = "set_piece"
    else:
        lane = "default"

    plan = {
        "tema_id": brief.get("id"),
        "lane": lane,
        "hook": _toma(catalog, hook) if hook
        else {"set_piece": None,
              "nota": "ningun set-piece 'listo' calza -> hook por DEFECTO del "
                      "proposer (BeatKinetic / BeatStatCallout), ya mejorado por "
                      "el motor visual."},
        "climax_alterno": _toma(catalog, climax) if climax else None,
        "hero_shot_posible": _heroshot_nota(catalog, brief) if lane == "default" else None,
        "compone_con_proposer": (
            "lane=set_piece -> el hook del director REEMPLAZA el hook por defecto "
            "del proposer; el resto del arco (wow/datos/climax/cta) lo arma el "
            "proposer. lane=default -> el proposer arma el video completo."),
        "guardrail": como.get("guardrail"),
        "gate": como.get("gate"),
        "nota_copy": "Los slots quedan '<<rellenar>>': el copy/dato EXACTO lo "
                     "decide Manuel / el planner, NUNCA el director.",
    }
    return plan


def _heroshot_nota(catalog, brief):
    """hero_shot es bespoke/planeado: se SUGIERE a Manuel, no se auto-castea."""
    hs = catalog.get("hero_shot", {})
    if hs.get("estado") != "planeado":
        return None
    return {
        "estado": hs.get("estado"),
        "sugerencia": "si el tema tiene un objeto/evento ICONICO unico (no en el "
                      "catalogo de set-pieces), considera el lane bespoke hero_shot "
                      "(imagen IA / 3D libre + camara $0; img2vid de paga gateado). "
                      "Decision de Manuel.",
        "ejemplos": hs.get("ejemplos", []),
    }


def _find_tema(tema_id):
    for t in _load(TEMAS).get("temas", []):
        if t.get("id") == tema_id:
            return t
    return None


# --------------------------------------------------------------------- CLI
def _cli(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2

    if argv[0] == "--tema":
        brief = {"tema": argv[argv.index("--tema") + 1]}
    else:
        brief = _find_tema(argv[0])
        if brief is None:
            print(f"sin tema con id '{argv[0]}' en temas_cola.json; usa "
                  f"--tema \"texto\" para castear texto suelto", file=sys.stderr)
            return 2

    plan = direct(brief)
    out = json.dumps(plan, ensure_ascii=False, indent=2)
    if "--out" in argv:
        Path(argv[argv.index("--out") + 1]).write_text(out, encoding="utf-8")
    print(out)

    # resumen legible (como proposer imprime el resultado del validador)
    print("\n-- director --", file=sys.stderr)
    print(f"  lane: {plan['lane']}", file=sys.stderr)
    h = plan["hook"]
    if h.get("set_piece"):
        m = h["match"]
        print(f"  hook: {h['set_piece']} -> {h['comp']} (motion {h['motion']}, "
              f"{h['costo']})", file=sys.stderr)
        print(f"  match: {m['score']} triggers {m['triggers']}", file=sys.stderr)
    else:
        print("  hook: DEFECTO (proposer kinetic/stat)", file=sys.stderr)
    if plan.get("climax_alterno"):
        c = plan["climax_alterno"]
        print(f"  climax alterno: {c['set_piece']} -> {c['comp']} "
              f"({c['match']['score']} triggers)", file=sys.stderr)
    print("  PROPONE -> gate de Manuel antes de producir", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
