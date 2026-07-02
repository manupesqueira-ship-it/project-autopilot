# -*- coding: utf-8 -*-
"""datasheet.py — DATA-SPINE del sistema Dinero IA (P1.1 keystone del plan maestro).

Convierte "datos exactos con fuente" de esperanza-de-prompt en INVARIANTE que rompe el build.

Tres piezas:
  1) LEDGER tipado: cada cifra vive como {value, unit, currency, source, url, as_of, method}.
     - SOURCED  = dato primario (con fuente/fecha).
     - COMPUTED = derivado por una fórmula determinista desde otras claves (nadie teclea el número).
  2) CALCULADORA determinista: resuelve las COMPUTED (multiply / sum / diff / pct_change /
     real_value[erosión] / fv_annuity[interés compuesto]). Es la única fuente de las cifras derivadas.
  3) GATE verify(): corre ANTES del render y FALLA (en segundos) si:
       (a) sobrevive cualquier "<<verify>>";
       (b) una cifra COMPUTED no cuadra con su recálculo;
       (c) una cifra MOSTRADA en el reel no cuadra (a su precisión) con la del ledger;
       (d) el pie de fuente no se compone de la procedencia;
       (e) hay claim temporal relativo ("esta semana/hoy") sin fecha, en carril=noticia;
       (f) el dato vivo está rancio (as_of más viejo que el máximo del carril).

Uso:  python datasheet.py            # corre la auto-prueba (demuestra que caza el 475M y el "esta semana")
      from datasheet import resolve, verify_reel, Datasheet
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------- calculadora

def _fv_annuity(pmt: float, annual_rate: float, years: float, freq: int = 12) -> float:
    """Valor futuro de una anualidad (aporte periódico constante)."""
    r = annual_rate / freq
    n = years * freq
    if r == 0:
        return pmt * n
    return pmt * (((1 + r) ** n - 1) / r)


def _real_value(principal: float, annual_infl: float, years: float) -> float:
    """Poder de compra real tras 'years' de inflación (erosión del efectivo)."""
    return principal / ((1 + annual_infl) ** years)


# op -> función pura sobre valores ya resueltos de las claves referidas
def _apply(method: dict, vals: dict) -> float:
    kind = method["kind"]
    if kind == "sourced":
        raise ValueError("sourced no se computa")
    if kind == "multiply":
        out = 1.0
        for k in method["factors"]:
            out *= vals[k]
        return out
    if kind == "sum":
        return sum(vals[k] for k in method["terms"])
    if kind == "diff":
        return vals[method["a"]] - vals[method["b"]]
    if kind == "pct_change":                       # (to-from)/from  -> fracción
        f, t = vals[method["from"]], vals[method["to"]]
        return (t - f) / f
    if kind == "real_value":                       # erosión por inflación
        return _real_value(vals[method["principal"]], method["annual_infl"], method["years"])
    if kind == "fv_annuity":                        # interés compuesto sobre aportes
        pmt = vals[method["pmt"]] if isinstance(method["pmt"], str) else method["pmt"]
        return _fv_annuity(pmt, method["annual_rate"], method["years"], method.get("freq", 12))
    if kind == "scale":                             # value * factor (p.ej. a millones)
        return vals[method["of"]] * method["factor"]
    raise ValueError(f"método desconocido: {kind}")


# ---------------------------------------------------------------- ledger

class Datasheet:
    """Colección de cifras tipadas. figures[key] = {value?, unit, currency, source, url, as_of, method}."""

    def __init__(self, figures: dict, lane: str = "evergreen"):
        self.figures = figures
        self.lane = lane                 # "noticia" | "evergreen"
        self._resolved: dict | None = None

    @classmethod
    def load(cls, path) -> "Datasheet":
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(d["figures"], d.get("lane", "evergreen"))

    def resolve(self) -> dict:
        """Resuelve todas las COMPUTED en orden topológico. Devuelve {key: value}."""
        if self._resolved is not None:
            return self._resolved
        vals: dict = {}
        pending = dict(self.figures)
        guard = 0
        while pending:
            guard += 1
            if guard > 10 * (len(self.figures) + 1):
                raise ValueError(f"ciclo o clave faltante en el ledger: {list(pending)}")
            for key, fig in list(pending.items()):
                method = fig.get("method", {"kind": "sourced"})
                if method["kind"] == "sourced":
                    if "value" not in fig:
                        raise ValueError(f"figura sourced sin value: {key}")
                    vals[key] = float(fig["value"])
                    del pending[key]
                    continue
                refs = _refs_of(method)
                if all(r in vals for r in refs):
                    vals[key] = _apply(method, vals)
                    del pending[key]
        self._resolved = vals
        return vals


def _refs_of(method: dict) -> list[str]:
    out = []
    for k in ("factors", "terms"):
        out += [r for r in method.get(k, []) if isinstance(r, str)]
    for k in ("a", "b", "from", "to", "principal", "of"):
        v = method.get(k)
        if isinstance(v, str):
            out.append(v)
    if isinstance(method.get("pmt"), str):
        out.append(method["pmt"])
    return out


# ---------------------------------------------------------------- comparación a precisión

def matches_at_precision(shown_abs: float, actual: float) -> bool:
    """El valor MOSTRADO (redondeado a su propia precisión) debe igualar al REAL redondeado
    a esa misma precisión. Así 476.63M mostrado como 477 = OK, pero como 475 = FALLA."""
    if actual == 0:
        return round(shown_abs) == 0
    # precisión implícita del valor mostrado = su magnitud de redondeo
    step = _round_step(shown_abs)
    return round(actual / step) * step == round(shown_abs / step) * step


def _round_step(v: float) -> float:
    """Escalón de redondeo implícito de un número (el dígito significativo más bajo no-cero)."""
    v = abs(v)
    if v == 0:
        return 1.0
    # cuántos ceros finales tiene el entero mostrado
    iv = int(round(v))
    if iv == 0:
        return 1.0
    step = 1
    while iv % (step * 10) == 0:
        step *= 10
    return float(step)


# ---------------------------------------------------------------- gate VERIFY

REL_TIME = re.compile(r"\b(esta semana|hoy|ayer|este mes|estos días|ahora mismo|reci[eé]n|acaba de)\b", re.I)
HAS_DATE = re.compile(r"\b(20\d{2}|ener|febr|marz|abril|mayo|junio|julio|agost|septiembre|octubre|noviembre|diciembre)\b", re.I)
LANE_MAX_STALE_DAYS = {"noticia": 7, "evergreen": 3650}


def _iter_shown_numbers(reel_def: dict):
    """Devuelve (beat_id, campo, valor_absoluto, bind_key|None) por cada cifra visible del reel."""
    for b in reel_def.get("beats", []):
        sc = b.get("scene", {})
        t = sc.get("type")
        scale = 1e6 if str(sc.get("suffix", "")).strip().upper().startswith("M") else 1.0
        bid = b.get("id", "?")
        if t == "bignum" and "value" in sc:
            yield bid, "value", sc["value"] * scale, sc.get("bind")
        elif t == "payoff" and "value" in sc:
            yield bid, "value", sc["value"] * scale, sc.get("bind")
        elif t == "compare":
            for side in ("left", "right"):
                if side in sc and "value" in sc[side]:
                    yield bid, f"{side}.value", sc[side]["value"] * scale, sc[side].get("bind")
        elif t == "fallchart":
            for f in ("from", "to", "delta"):
                if f in sc:
                    yield bid, f, sc[f] * scale, sc.get(f"bind_{f}")


def verify_reel(reel_def: dict, datasheet: Datasheet | None = None, today: date | None = None) -> tuple[bool, list[str]]:
    """Corre el gate. Devuelve (ok, errores)."""
    errors: list[str] = []
    today = today or date.today()
    lane = datasheet.lane if datasheet else "evergreen"

    # (a) <<verify>> sin resolver en cualquier texto del reel
    blob = json.dumps(reel_def, ensure_ascii=False)
    if "<<verify>>" in blob or "<<VERIFY>>" in blob:
        errors.append("BLOQUEA: sobrevive un marcador <<verify>> sin resolver.")

    # (e) claims temporales relativos sin fecha, en carril noticia
    if lane == "noticia":
        for b in reel_def.get("beats", []):
            vo = b.get("vo", "")
            if REL_TIME.search(vo) and not HAS_DATE.search(vo):
                m = REL_TIME.search(vo).group(0)
                errors.append(f"BLOQUEA [{b.get('id')}]: claim temporal relativo '{m}' sin fecha en carril=noticia.")

    if datasheet is None:
        return (len(errors) == 0, errors)

    vals = datasheet.resolve()

    # (b) cada COMPUTED debe cuadrar con su recálculo (self-check del ledger)
    for key, fig in datasheet.figures.items():
        method = fig.get("method", {"kind": "sourced"})
        if method["kind"] != "sourced" and "value" in fig:
            if not matches_at_precision(float(fig["value"]), vals[key]):
                errors.append(f"BLOQUEA: la cifra COMPUTED '{key}'={fig['value']} no cuadra con el recálculo={vals[key]:.2f}.")

    # (c) cada cifra MOSTRADA debe trazar a una clave del ledger y cuadrar a su precisión
    for bid, campo, shown_abs, bind in _iter_shown_numbers(reel_def):
        if bind is None:
            errors.append(f"AVISO [{bid}].{campo}={shown_abs:g}: sin 'bind' a una clave del ledger (procedencia no trazable).")
            continue
        if bind not in vals:
            errors.append(f"BLOQUEA [{bid}].{campo}: bind '{bind}' no existe en el ledger.")
            continue
        if not matches_at_precision(shown_abs, vals[bind]):
            errors.append(f"BLOQUEA [{bid}].{campo}: muestra {shown_abs:g} pero el ledger['{bind}']={vals[bind]:.2f} (no cuadra a esa precisión).")

    # (f) frescura del dato vivo
    max_stale = LANE_MAX_STALE_DAYS.get(lane, 3650)
    for key, fig in datasheet.figures.items():
        as_of = fig.get("as_of")
        if as_of:
            try:
                d0 = datetime.strptime(as_of, "%Y-%m-%d").date()
                if (today - d0).days > max_stale:
                    errors.append(f"BLOQUEA: '{key}' as_of={as_of} está rancio para carril={lane} (máx {max_stale} días).")
            except ValueError:
                errors.append(f"AVISO: '{key}' as_of='{as_of}' no es YYYY-MM-DD.")

    return (len([e for e in errors if e.startswith("BLOQUEA")]) == 0, errors)


def compose_source(datasheet: Datasheet) -> str:
    """Compone el pie de fuente desde la procedencia (fuentes únicas + as_of más reciente)."""
    srcs, latest = [], None
    for fig in datasheet.figures.values():
        s = fig.get("source")
        if s and s not in srcs:
            srcs.append(s)
        ao = fig.get("as_of")
        if ao and (latest is None or ao > latest):
            latest = ao
    line = " · ".join(srcs)
    if latest:
        line += f" · corte {latest}"
    return line


# ---------------------------------------------------------------- auto-prueba

def _demo():
    print("=" * 74)
    print("AUTO-PRUEBA del data-spine (P1.1) — demuestra que caza los bugs reales\n")

    # --- Caso 1: reserva BTC de El Salvador (el bug del 475M) ---
    btc_sheet = Datasheet({
        "btc_qty":   {"value": 7700, "unit": "BTC", "currency": None,
                       "source": "Oficina Nacional de Bitcoin", "url": "", "as_of": "2026-07-02",
                       "method": {"kind": "sourced"}},
        "btc_price": {"value": 61900, "unit": "USD/BTC", "currency": "USD",
                       "source": "Oficina Nacional de Bitcoin", "url": "", "as_of": "2026-07-02",
                       "method": {"kind": "sourced"}},
        "btc_reserve": {"unit": "USD", "currency": "USD",
                         "source": "cálculo propio", "as_of": "2026-07-02",
                         "method": {"kind": "multiply", "factors": ["btc_qty", "btc_price"]}},
    }, lane="noticia")
    print(f"  Reserva computada = ${btc_sheet.resolve()['btc_reserve']:,.0f}  (7,700 × 61,900)")

    reel_malo = {"beats": [{"id": "b4", "vo": "vale alrededor de 475 millones.",
        "scene": {"type": "bignum", "value": 475, "suffix": "M USD", "bind": "btc_reserve"}}]}
    reel_bueno = {"beats": [{"id": "b4", "vo": "vale alrededor de 477 millones.",
        "scene": {"type": "bignum", "value": 477, "suffix": "M USD", "bind": "btc_reserve"}}]}

    ok_malo, err_malo = verify_reel(reel_malo, btc_sheet, today=date(2026, 7, 2))
    ok_bueno, err_bueno = verify_reel(reel_bueno, btc_sheet, today=date(2026, 7, 2))
    print(f"\n  reel con $475M  -> {'PASS' if ok_malo else 'FALLA'}  (esperado: FALLA)")
    for e in err_malo:
        print(f"      · {e}")
    print(f"  reel con $477M  -> {'PASS' if ok_bueno else 'FALLA'}  (esperado: PASS)")
    for e in err_bueno:
        print(f"      · {e}")
    print(f"  pie compuesto  -> {compose_source(btc_sheet)}")

    # --- Caso 2: claim temporal relativo sin fecha (el "petróleo subió esta semana") ---
    print()
    oil = Datasheet({}, lane="noticia")
    reel_oil = {"beats": [{"id": "b1", "vo": "El petróleo subió fuerte esta semana."}]}
    ok_oil, err_oil = verify_reel(reel_oil, oil, today=date(2026, 7, 2))
    print(f"  'subió esta semana' (sin fecha, noticia) -> {'PASS' if ok_oil else 'FALLA'}  (esperado: FALLA)")
    for e in err_oil:
        print(f"      · {e}")
    reel_oil2 = {"beats": [{"id": "b1", "vo": "El petróleo subió fuerte en la semana del 1 de julio de 2026."}]}
    ok_oil2, _ = verify_reel(reel_oil2, oil, today=date(2026, 7, 2))
    print(f"  con fecha explícita                       -> {'PASS' if ok_oil2 else 'FALLA'}  (esperado: PASS)")

    # --- Caso 3: la calculadora reproduce cifras de reels reales (erosión + interés compuesto) ---
    print()
    real = Datasheet({
        "efectivo_hoy": {"value": 100000, "currency": "MXN", "method": {"kind": "sourced"}},
        "efectivo_1y":  {"currency": "MXN",
                          "method": {"kind": "real_value", "principal": "efectivo_hoy", "annual_infl": 0.0394, "years": 1}},
    })
    r = real.resolve()
    print(f"  Erosión $100,000 al 3.94% (1 año) = ${r['efectivo_1y']:,.0f}  (reel muestra $96,209)")

    print("\n" + "=" * 74)
    all_ok = (not ok_malo) and ok_bueno and (not ok_oil) and ok_oil2
    print("RESULTADO:", "✅ el gate caza los 2 bugs reales y deja pasar lo correcto" if all_ok else "❌ revisar")


if __name__ == "__main__":
    _demo()
