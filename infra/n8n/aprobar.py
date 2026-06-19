# -*- coding: utf-8 -*-
"""
Cierra el loop tras el GATE HUMANO: registra un video que Manuel ya aprobo.

UNA sola accion idempotente (antes eran 2 pasos manuales sueltos):
  1) lo agrega al LEDGER (infra/assembler/ledger.py) -> bloquea ese tema y esa
     combinacion visual a futuro (no se repiten).
  2) marca el tema como 'producido' en infra/n8n/temas_cola.json (si vino de la
     cola; si fue un tema manual suelto, solo avisa y sigue).

El gate sigue siendo HUMANO a proposito: esto se corre SOLO cuando Manuel
aprobo el MP4 entregado. El slug del guion == id del tema en la cola (el
pipeline fuerza esa igualdad), asi que un solo <slug> cierra ambas cosas.

Uso:
  python aprobar.py <slug> [--fecha YYYY-MM-DD] [--dry-run] [--cola ruta.json]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ASSEMBLER = HERE.parent / "assembler"
DEFAULT_COLA = HERE / "temas_cola.json"

sys.path.insert(0, str(ASSEMBLER))
from ledger import Ledger  # noqa: E402  (fuente de verdad del ledger)


def _guion_path(slug):
    return ASSEMBLER / f"guion_{slug}.json"


def _load_guion(slug):
    p = _guion_path(slug)
    if not p.exists():
        raise FileNotFoundError(f"no existe el guion {p.name} en {ASSEMBLER}")
    return json.loads(p.read_text(encoding="utf-8-sig"))


def aprobar(slug, fecha=None, dry_run=False, cola=DEFAULT_COLA):
    g = _load_guion(slug)
    tema = g.get("title", "") or slug
    beats = g.get("beats", [])

    # 1) ledger (idempotente: no duplica si el slug ya esta)
    led = Ledger()
    if led.has_slug(slug):
        print(f"  ledger: '{slug}' ya estaba registrado (no se duplica)")
    else:
        if dry_run:
            print(f"  ledger: [dry-run] agregaria '{slug}' ({tema}) {len(beats)} beats")
        else:
            led.append_video(slug, tema, beats, fecha=fecha)
            print(f"  ledger: REGISTRADO '{slug}' ({tema}) {len(beats)} beats")

    # 2) marcar 'producido' en la cola (si el tema vino de ahi)
    cola = Path(cola)
    if cola.exists():
        data = json.loads(cola.read_text(encoding="utf-8-sig"))
        t = next((x for x in data.get("temas", []) if x.get("id") == slug), None)
        if t is None:
            print(f"  cola: '{slug}' no esta en la cola (ok si fue tema manual)")
        elif t.get("estado") == "producido":
            print(f"  cola: '{slug}' ya estaba marcado producido")
        else:
            if dry_run:
                print(f"  cola: [dry-run] marcaria '{slug}' como producido")
            else:
                t["estado"] = "producido"
                if fecha:
                    t["producido_fecha"] = fecha
                cola.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  cola: '{slug}' marcado como producido")
    else:
        print(f"  cola: no existe {cola} (se omite el marcado)")

    return 0


def rechazar(slug, fecha=None, cola=DEFAULT_COLA):
    """Tras un [Basura] en el gate humano: DESCARTA el tema de la cola para que la
    proxima corrida tome el SIGUIENTE producible (no se queda en bucle sobre el
    rechazado). Marca estado='rechazado' -> cola.producible() lo excluye solo.

    NO toca el ledger (no se publico nada que registrar) y NO borra el MP4 (queda
    en out/<slug>/ por si lo quieres revisar). Reversible: editar el estado a
    'aprobado' en la cola lo vuelve a poner en juego.
    """
    cola = Path(cola)
    if not cola.exists():
        print(f"  cola: no existe {cola} (nada que descartar)")
        return 0
    data = json.loads(cola.read_text(encoding="utf-8-sig"))
    t = next((x for x in data.get("temas", []) if x.get("id") == slug), None)
    if t is None:
        print(f"  cola: '{slug}' no esta en la cola (ok si fue tema manual suelto)")
        return 0
    if t.get("estado") == "rechazado":
        print(f"  cola: '{slug}' ya estaba rechazado")
        return 0
    if t.get("estado") == "producido":
        print(f"  cola: '{slug}' ya estaba producido; no lo toco")
        return 0
    t["estado"] = "rechazado"
    if fecha:
        t["rechazado_fecha"] = fecha
    cola.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  cola: '{slug}' marcado RECHAZADO (la proxima corrida salta al siguiente)")
    return 0


def _cli(argv):
    if not argv or argv[0].startswith("--"):
        print(__doc__)
        return 2
    slug = argv[0]
    fecha = argv[argv.index("--fecha") + 1] if "--fecha" in argv else None
    dry = "--dry-run" in argv
    cola = Path(argv[argv.index("--cola") + 1]) if "--cola" in argv else DEFAULT_COLA
    if "--rechazar" in argv:
        print(f"=== rechazar {slug} ===")
        return rechazar(slug, fecha=fecha, cola=cola)
    print(f"=== aprobar {slug}{' (dry-run)' if dry else ''} ===")
    try:
        return aprobar(slug, fecha=fecha, dry_run=dry, cola=cola)
    except FileNotFoundError as e:
        print(f"  ERROR: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
