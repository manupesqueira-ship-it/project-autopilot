# -*- coding: utf-8 -*-
"""
Lector de la COLA de temas (banco de material) para Dinero IA.

Fuente de verdad en Python (sirve con o sin n8n). Lee `temas_cola.json` y le
entrega al pipeline el SIGUIENTE tema producible, mapeado 1:1 a los campos del
nodo Brief del workflow: tema / open_loop / datos (+ slug = id del tema, para
que el slug del guion sea el id corto de la cola y el ledger lo pueda cerrar).

REGLA DE ORO (la que protege la calidad): un tema NO es producible mientras su
`datos` conserve marcadores '<<verificar' o '<<rellenar' (cifras sin confirmar).
El planner SOLO debe recibir datos verificados; este lector se NIEGA a emitir un
tema con huecos -> nunca se renderiza un guion con cifras placeholder.

Ciclo de un tema:
  propuesto --(gate de Manuel)--> aprobado --(llenar cifras y quitar <<verificar>>)
            --> producible --(produccion + gate humano)--> producido

Uso CLI:
  python cola.py next  [--cola ruta.json]   imprime el JSON del brief (stdout) o sale !=0
  python cola.py list  [--cola ruta.json]   estado de toda la cola (a stderr)
Salidas: 0 = emitio un tema ; 3 = no hay temas producibles ; 2 = error de uso.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
DEFAULT_COLA = HERE / "temas_cola.json"

MARCADORES = ("<<verificar", "<<rellenar")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def faltan_cifras(datos):
    """True si `datos` aun tiene cifras sin verificar (marcadores)."""
    d = datos or ""
    return any(m in d for m in MARCADORES)


def producible(t):
    """Un tema se puede producir si Manuel lo aprobo Y sus datos estan verificados."""
    return t.get("estado") == "aprobado" and not faltan_cifras(t.get("datos", ""))


def siguiente(data):
    """Primer tema producible en orden de la cola, o None."""
    for t in data.get("temas", []):
        if producible(t):
            return t
    return None


def _brief(t):
    """Los 3 campos que consume el nodo Brief + el slug = id del tema."""
    return {
        "slug": t["id"],
        "tema": t["tema"],
        "open_loop": t.get("open_loop", ""),
        "datos": t["datos"],
    }


def _cli(argv):
    if not argv or argv[0] not in ("next", "list"):
        print(__doc__)
        return 2
    cmd = argv[0]
    cola = DEFAULT_COLA
    if "--cola" in argv:
        cola = Path(argv[argv.index("--cola") + 1])
    data = load(cola)
    temas = data.get("temas", [])

    if cmd == "list":
        print(f"=== cola: {cola.name} ({len(temas)} temas) ===", file=sys.stderr)
        for t in temas:
            if t.get("estado") == "producido":
                marca = "producido"
            elif producible(t):
                marca = "LISTO p/producir"
            elif t.get("estado") == "aprobado":
                marca = "aprobado (faltan cifras)"
            else:
                marca = t.get("estado", "?")
            print(f"  [{marca:24}] {t.get('id')}", file=sys.stderr)
        listos = sum(1 for t in temas if producible(t))
        print(f"  -> {listos} listo(s) para producir", file=sys.stderr)
        return 0

    # next: emite SOLO JSON a stdout (lo parsea el nodo Brief de n8n)
    t = siguiente(data)
    if t is None:
        aprob = sum(1 for x in temas if x.get("estado") == "aprobado")
        print(
            f"NO HAY TEMAS PRODUCIBLES: {aprob} aprobado(s) pero todos con cifras "
            f"sin verificar (<<verificar>>). Llena las cifras de uno y quita los "
            f"marcadores antes de producir.",
            file=sys.stderr,
        )
        return 3
    print(json.dumps(_brief(t), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
