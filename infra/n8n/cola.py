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

DOS CARRILES (campo `carril` de cada tema):
  - 'news'      PERECEDERO (noticia / cifra viva). El selector lo PRIORIZA y al
                producir se encola con TTL (caduca si no se publico a tiempo).
                Campo opcional 'vence' (YYYY-MM-DD): tras esa fecha deja de ser
                producible (cifra atada a un evento con fecha).
  - 'evergreen' SIN caducidad (educativo / habito). Rellena los dias sin noticia.
El selector entrega PRIMERO el news producible mas urgente (vence mas proximo),
y si no hay ninguno, el primer evergreen. Asi una noticia no se "envejece" en la
cola detras de un evergreen.

NOTA (seleccion de noticias EN VIVO): elegir el tema-noticia del dia desde fuentes
en tiempo real (auto) NO se hace aqui: requiere o bien que Claude escriba en sesion
un tema-news con cifras verificadas, o una API (costo recurrente -> avisar antes de
cablear). Este lector solo PRIORIZA y CADUCA por carril; el material lo alimenta el
gate editorial.

Ciclo de un tema:
  propuesto --(gate de Manuel)--> aprobado --(llenar cifras y quitar <<verificar>>)
            --> producible --(produccion + gate humano)--> producido

Uso CLI:
  python cola.py next  [--cola ruta.json] [--carril news|evergreen]
        imprime el JSON del brief (stdout) o sale !=0
  python cola.py list  [--cola ruta.json]   estado de toda la cola (a stderr)
Salidas: 0 = emitio un tema ; 3 = no hay temas producibles ; 2 = error de uso.
"""
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
DEFAULT_COLA = HERE / "temas_cola.json"

MARCADORES = ("<<verificar", "<<rellenar")
CARRIL_DEFAULT = "evergreen"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def faltan_cifras(datos):
    """True si `datos` aun tiene cifras sin verificar (marcadores)."""
    d = datos or ""
    return any(m in d for m in MARCADORES)


def carril(t):
    return (t.get("carril") or CARRIL_DEFAULT).lower()


def vencido(t, hoy=None):
    """True si es un tema-news con 'vence' ya pasada (cifra atada a una fecha)."""
    v = t.get("vence")
    if not v:
        return False
    try:
        return date.fromisoformat(str(v)[:10]) < (hoy or date.today())
    except ValueError:
        return False  # fecha mal escrita: no la usamos para descartar


def producible(t, hoy=None):
    """Producible = aprobado Y datos verificados Y (si news) no vencido."""
    return (t.get("estado") == "aprobado"
            and not faltan_cifras(t.get("datos", ""))
            and not vencido(t, hoy))


def siguiente(data, carril_filtro=None, hoy=None):
    """Siguiente tema a producir respetando carriles.

    Orden: PRIMERO news producibles (los de 'vence' mas proximo van antes; los sin
    'vence' van al final del bloque news, en orden de la cola), LUEGO evergreen en
    orden de la cola. `carril_filtro` ('news'|'evergreen') limita a ese carril.
    """
    temas = [t for t in data.get("temas", []) if producible(t, hoy)]
    if carril_filtro:
        temas = [t for t in temas if carril(t) == carril_filtro.lower()]

    news = [t for t in temas if carril(t) == "news"]
    ever = [t for t in temas if carril(t) != "news"]
    # news: por 'vence' ascendente; sin vence al final (clave = fecha-maxima)
    news.sort(key=lambda t: str(t.get("vence") or "9999-12-31")[:10])
    ordered = news + ever
    return ordered[0] if ordered else None


def _brief(t):
    """Los campos que consume el Brief + el slug (= id) + el carril (para encolar)."""
    return {
        "slug": t["id"],
        "tema": t["tema"],
        "open_loop": t.get("open_loop", ""),
        "datos": t["datos"],
        "carril": carril(t),
    }


def _cli(argv):
    if not argv or argv[0] not in ("next", "list"):
        print(__doc__)
        return 2
    cmd = argv[0]
    cola = DEFAULT_COLA
    if "--cola" in argv:
        cola = Path(argv[argv.index("--cola") + 1])
    carril_filtro = None
    if "--carril" in argv:
        carril_filtro = argv[argv.index("--carril") + 1]
    data = load(cola)
    temas = data.get("temas", [])

    if cmd == "list":
        print(f"=== cola: {cola.name} ({len(temas)} temas) ===", file=sys.stderr)
        for t in temas:
            if t.get("estado") == "producido":
                marca = "producido"
            elif producible(t):
                marca = "LISTO p/producir"
            elif vencido(t):
                marca = "vencido (news)"
            elif t.get("estado") == "aprobado":
                marca = "aprobado (faltan cifras)"
            else:
                marca = t.get("estado", "?")
            cstr = carril(t)
            vstr = f" vence={t['vence']}" if t.get("vence") else ""
            print(f"  [{marca:24}] {cstr:9} {t.get('id')}{vstr}", file=sys.stderr)
        listos = sum(1 for t in temas if producible(t))
        ln = sum(1 for t in temas if producible(t) and carril(t) == "news")
        print(f"  -> {listos} listo(s): {ln} news + {listos - ln} evergreen",
              file=sys.stderr)
        return 0

    # next: emite SOLO JSON a stdout (lo parsea el orquestador / nodo Brief)
    t = siguiente(data, carril_filtro=carril_filtro)
    if t is None:
        aprob = sum(1 for x in temas if x.get("estado") == "aprobado")
        extra = f" (carril={carril_filtro})" if carril_filtro else ""
        print(
            f"NO HAY TEMAS PRODUCIBLES{extra}: {aprob} aprobado(s) pero con cifras "
            f"sin verificar (<<verificar>>) o vencidos. Llena las cifras de uno y "
            f"quita los marcadores antes de producir.",
            file=sys.stderr,
        )
        return 3
    print(json.dumps(_brief(t), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
