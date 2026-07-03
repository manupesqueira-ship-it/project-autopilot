# -*- coding: utf-8 -*-
"""
QC OFFLINE del validador y del ledger. No llama a ninguna API ni renderiza.
Usa guiones-fixture INVENTADOS (buenos y malos), NO los 6 guiones reales.

    python test_validator.py
    # imprime PASS/FAIL por caso; exit 0 si todos pasan.
"""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "assembler"))

from validator import validate, is_valid          # noqa: E402
from ledger import Ledger                          # noqa: E402


# --------------------------------------------------------------- fixtures
def _kinetic_hook(vo, words=None):
    """Hook kinetic cuyas stanzas cubren todo el vo (no congelado)."""
    toks = (words or vo).split()
    line = [{"text": w} for w in toks]
    return {"id": "b1_hook", "type": "BeatKinetic", "vo": vo, "sfx": "impact",
            "trans": "scrollUp", "props": {"lines": [line]}}


def _cta(vo="Cierra aqui y protege tu dinero hoy mismo amigo"):
    return {"id": "b9_cta", "type": "BeatCta", "vo": vo, "sfx": "whoosh",
            "props": {"text": "Cuida tu dinero", "boldWord": "dinero",
                      "sub": "manana: el siguiente tema"}}


def GOOD():
    """Guion valido: hook -> mapa(wow) -> bars -> versus -> bignumber -> cta."""
    return {
        "slug": "test_bueno",
        "title": "Inventado prueba alfa zeta",
        "beats": [
            _kinetic_hook("Una decision cambio todo para siempre en el mundo entero"),
            {"id": "b2_map", "type": "BeatMapZoom", "sfx": "whoosh", "trans": "zoomPunch",
             "vo": "Esto pasa en un pais lejano que nadie esperaba ver crecer asi.",
             "props": {"countryName": "Chile", "iso2": "CL", "caption": "2024",
                       "label": "Chile", "sublabel": "prueba"}},
            {"id": "b3_bars", "type": "BeatBars", "sfx": "tick", "trans": "scrollUp",
             "vo": "Tres montos muy distintos: cien, luego quinientos y al final mil dolares.",
             "cues": {"growWords": ["cien", "quinientos", "mil"]},
             "props": {"caption": "montos", "prefix": "$", "suffix": " USD",
                       "bars": [{"label": "A", "value": 100}, {"label": "B", "value": 500},
                                {"label": "C", "value": 1000}]}},
            {"id": "b4_vs", "type": "BeatVersus", "sfx": "whoosh", "trans": "flashWhite",
             "vo": "El primero llego a mil dolares y el segundo a tres mil dolares hoy.",
             "cues": {"leftEndWord": "dolares", "rightEndWord": "dolares:2"},
             "props": {"caption": "duelo USD", "prefix": "$", "winner": "right",
                       "left": {"name": "Uno", "ticker": "USD", "value": 1000},
                       "right": {"name": "Dos", "ticker": "USD", "value": 3000}}},
            {"id": "b5_big", "type": "BeatBigNumber", "sfx": "impact", "trans": "flashWhite",
             "vo": "La ganancia final fue de doscientos mil dolares limpios para ellos.",
             "cues": {"countEndWord": "dolares"},
             "props": {"value": 200000, "prefix": "$", "suffix": " USD",
                       "caption": "ganancia", "subline": "neto", "color": "#00D9A5"}},
            _cta(),
        ],
    }


def _mut(fn):
    g = GOOD()
    fn(g)
    return g


CASES = []  # (nombre, guion, codigo_de_error_esperado o None)


def case(name, code, guion):
    CASES.append((name, guion, code))


case("bueno", None, GOOD())

# R5
case("muy pocos beats", "R5", {"slug": "x", "title": "t uno dos", "beats": [_kinetic_hook("hola mundo cruel"), _cta()]})
case("ultimo no es cta", "R5", _mut(lambda g: g["beats"].append(
    {"id": "bz", "type": "BeatBigNumber", "vo": "extra mil dolares aqui", "props": {"value": 1000, "suffix": " USD"}})))
case("slug malo", "R5", _mut(lambda g: g.update(slug="Mal Slug!")))

# R2
def _two_same(g):
    g["beats"].insert(3, {"id": "b3b", "type": "BeatBars", "sfx": "tick",
                          "vo": "Otra vez tres barras: dos, cuatro y seis dolares contados.",
                          "cues": {"growWords": ["dos", "cuatro", "seis"]},
                          "props": {"caption": "x", "prefix": "$", "suffix": " USD",
                                    "bars": [{"label": "a", "value": 2}, {"label": "b", "value": 4},
                                             {"label": "c", "value": 6}]}})
case("dos bars seguidos", "R2", _mut(_two_same))

# R3 (sin wow: cambia el mapa por un pictograma que no es wow, y bars/versus tampoco)
def _no_wow(g):
    g["beats"][1] = {"id": "b2_pic", "type": "BeatPictogram", "sfx": "tick",
                     "vo": "Veintiuno de cada cien personas no llegan a fin de mes nunca.",
                     "props": {"total": 100, "highlight": 21, "caption": "21 de 100"}}
case("sin visual wow", "R3", _mut(_no_wow))

# R4 hook
case("primer beat no es hook", "R4", _mut(lambda g: g["beats"].__setitem__(0,
     {"id": "b1", "type": "BeatBigNumber", "vo": "mil dolares de entrada directa aqui",
      "cues": {"countEndWord": "aqui"}, "props": {"value": 1000, "suffix": " USD"}})))

# R4 pocos datos distintos (solo bars en la media -> 1 tipo de dato)
def _one_data(g):
    g2 = {"slug": "test_unodato", "title": "otro tema gamma delta",
          "beats": [_kinetic_hook("una frase larga que cubre el hook completo del video"),
                    {"id": "b2", "type": "BeatCharacter", "sfx": "tick",
                     "vo": "Aqui aparece el protagonista del relato que todos conocen ya.",
                     "props": {"imageSlug": "bukele", "name": "X", "role": "Y"}},
                    {"id": "b3", "type": "BeatBigNumber", "sfx": "impact",
                     "vo": "El total final asciende a quinientos mil dolares para todos.",
                     "cues": {"countEndWord": "dolares"},
                     "props": {"value": 500000, "suffix": " USD"}},
                    _cta()]}
    g.clear(); g.update(g2)
case("menos de 2 datos distintos", "R4", _mut(_one_data))

# R1 hook congelado: vo larguisimo pero revela 2 palabras
def _frozen_hook(g):
    g["beats"][0] = {"id": "b1_hook", "type": "BeatKinetic", "sfx": "impact",
                     "vo": ("Esta es una introduccion larguisima que dura muchos segundos "
                            "en pantalla pero las palabras reveladas son pocas y se congela todo"),
                     "props": {"lines": [[{"text": "Dinero"}, {"text": "facil"}]]}}
case("hook congelado", "R1", _mut(_frozen_hook))

# R1 bignumber largo que aterriza temprano (countEndWord al inicio)
def _early_land(g):
    g["beats"][4] = {"id": "b5_big", "type": "BeatBigNumber", "sfx": "impact",
                     "vo": ("Doscientos mil dolares fue la cifra y despues el narrador "
                            "siguio hablando mucho tiempo mas sin que nada cambie en pantalla nunca jamas"),
                     "cues": {"countEndWord": "dolares"},
                     "props": {"value": 200000, "prefix": "$", "suffix": " USD"}}
case("bignumber aterriza temprano", "R1", _mut(_early_land))

# R6 cifra protagonista sin moneda
def _no_currency(g):
    g["beats"][4]["props"] = {"value": 200000, "prefix": "$", "caption": "ganancia",
                              "subline": "neto", "color": "#00D9A5"}
    g["beats"][4]["vo"] = "La ganancia final fue de doscientos mil limpios para ellos hoy."
    g["beats"][4]["cues"] = {"countEndWord": "limpios"}
case("bignumber sin moneda", "R6", _mut(_no_currency))

# R7 cue inexistente
case("cue inexistente", "R7", _mut(lambda g: g["beats"][2]["cues"].__setitem__("growWords", ["cien", "noexiste", "mil"])))

# R8 tipo desconocido
case("tipo desconocido", "R8", _mut(lambda g: g["beats"][2].__setitem__("type", "BeatFoo")))

# R8 sin grafica de datos (reemplaza bars por pictograma, versus queda, no charts)
def _no_chart(g):
    g["beats"][2] = {"id": "b3", "type": "BeatPictogram", "sfx": "tick",
                     "vo": "Treinta de cada cien personas pierden su dinero cada ano completo.",
                     "props": {"total": 100, "highlight": 30, "caption": "30 de 100"}}
    # ahora media = MapZoom? no, mapa esta en 1. media tiene pictogram+versus -> 2 datos distintos OK
case("sin grafica de datos", "R8", _mut(_no_chart))

# R8 roster desde registro: un personaje REGISTRADO pero con en_roster=false
# (economista, fondo horneado) NO se puede castear -> R8. Bloquea el drift que
# motivo character_roster.json (la fuente de verdad del roster en F4).
def _offroster(g):
    g["beats"][1] = {"id": "b2_char", "type": "BeatCharacter", "sfx": "tick",
                     "vo": "Aqui aparece el analista que explica la cifra a todos ustedes.",
                     "props": {"imageSlug": "economista", "name": "X", "role": "Y"}}
case("personaje fuera del roster (en_roster=false)", "R8", _mut(_offroster))


# --------------------------------------------------------------- runner
def run_cases():
    ok = 0
    for name, guion, code in CASES:
        res = validate(guion)
        errs = res["errors"]
        if code is None:
            passed = (len(errs) == 0)
            detail = "" if passed else " | inesperado: " + " ; ".join(errs)
        else:
            passed = any(e.startswith(code) for e in errs)
            detail = "" if passed else f" | esperaba {code}, obtuvo: " + (" ; ".join(errs) or "(ninguno)")
        ok += passed
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}{detail}")
    return ok, len(CASES)


def run_brief():
    print("\n-- chequeo de cifras vs brief (warnings) --")
    g = GOOD()
    brief_bueno = "El monto fue de 100, 500 y 1,000 dolares; total 200,000 y duelo 3,000."
    r1 = validate(g, brief=brief_bueno)
    print(f"  [{'PASS' if not any(w.startswith('W-num') for w in r1['warnings']) else 'FAIL'}] brief con todas las cifras -> sin W-num")
    brief_pobre = "Un video sobre algo sin numeros relevantes aqui."
    r2 = validate(g, brief=brief_pobre)
    print(f"  [{'PASS' if any(w.startswith('W-num') for w in r2['warnings']) else 'FAIL'}] brief vacio de cifras -> hay W-num")
    # strict convierte warnings en errores
    r3 = validate(g, brief=brief_pobre, strict=True)
    print(f"  [{'PASS' if r3['errors'] and not is_valid(g, brief=brief_pobre, strict=True) else 'FAIL'}] --strict promueve W-num a error")


def run_round():
    print("\n-- W-round (narracion redondea / visual exacto) --")
    # cifra grande exacta en pantalla, vo SIN redondeo -> W-round
    g1 = _mut(lambda g: g["beats"][4].update(
        vo="La perdida total fue de cuarenta y dos millones setecientos mil dolares exactos hoy",
        cues={"countEndWord": "dolares"},
        props={"value": 42700000, "prefix": "$", "suffix": " USD", "caption": "x"}))
    r1 = validate(g1)
    print(f"  [{'PASS' if any(w.startswith('W-round') for w in r1['warnings']) else 'FAIL'}] cifra >=1M sin redondeo en la voz -> W-round")
    print(f"  [{'PASS' if not r1['errors'] else 'FAIL'}] W-round es warning, no rechaza")
    # misma cifra pero la voz redondea -> sin W-round
    g2 = _mut(lambda g: g["beats"][4].update(
        vo="La perdida total fue de alrededor de cuarenta y dos millones de dolares hoy",
        cues={"countEndWord": "dolares"},
        props={"value": 42700000, "prefix": "$", "suffix": " USD", "caption": "x"}))
    r2 = validate(g2)
    print(f"  [{'PASS' if not any(w.startswith('W-round') for w in r2['warnings']) else 'FAIL'}] voz con 'alrededor de' -> sin W-round")


def run_color():
    """R-color: el ROJO solo puede codificar una PERDIDA. Un item categorico en
    rojo (Gastos/Deudas...) SIN senal de perdida es decoracion -> se marca. Estos
    casos cuentan para el total (un regreso aqui REPRUEBA la suite)."""
    print("\n-- R-color (rojo = SOLO perdida; decorativo prohibido) --")
    ok = total = 0

    def chk(cond, label):
        nonlocal ok, total
        total += 1
        ok += bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    # fixture: bars con un item 'Gastos' rojo; extra/vo configurables por caso.
    def red_gastos(extra=None, vo=None):
        def fn(g):
            bar = {"label": "Gastos", "value": 500, "color": "#FF6B6B"}
            if extra:
                bar.update(extra)
            g["beats"][2]["props"]["bars"] = [
                {"label": "Ingresos", "value": 100, "color": "#00D9A5"},
                bar,
                {"label": "Ahorro", "value": 1000, "color": "#D4A574"},
            ]
            if vo is not None:                 # vo nuevo -> suelta el cue viejo
                g["beats"][2]["vo"] = vo
                g["beats"][2].pop("cues", None)
        return _mut(fn)

    # 1) item categorico rojo, valor positivo, vo sin perdida -> dispara R-color
    g1 = red_gastos()
    r1 = validate(g1)
    fired = [w for w in r1["warnings"] if w.startswith("R-color")]
    chk(fired and "Gastos" in fired[0],
        "'Gastos' rojo (valor positivo, vo sin perdida) -> R-color senala 'Gastos'")
    # ...y es WARNING: no rechaza en modo normal
    chk(not any(e.startswith("R-color") for e in r1["errors"]),
        "R-color es warning (no rechaza sin --strict)")

    # 2) el MISMO item rojo pero con senal de perdida (deltaPct negativo) -> NO dispara
    r2 = validate(red_gastos(extra={"deltaPct": -8}))
    chk(not any(w.startswith("R-color") for w in r2["warnings"]),
        "rojo en item con deltaPct negativo (perdida real) -> sin R-color")

    # 3) la NARRACION del beat habla de una caida -> rojo tematico, NO dispara
    r3 = validate(red_gastos(vo="El gasto del hogar se desplomo y la familia perdio mucho dinero."))
    chk(not any(w.startswith("R-color") for w in r3["warnings"]),
        "vo narra una caida ('desplomo') -> sin R-color (rojo tematico)")

    # 4) --strict promueve R-color (warning) a error -> puede volverse gate duro
    r4 = validate(g1, strict=True)
    chk(any(e.startswith("R-color") for e in r4["errors"]),
        "--strict promueve R-color a error")

    return ok, total


def run_maxbeats():
    print("\n-- conteo de beats (MAX_BEATS=10, banda de retencion 7-10) --")
    # GOOD tiene 6 beats. +1 = 7 (valido, El Salvador aprobado tiene 7).
    _pic = {"id": "b2b_pic", "type": "BeatPictogram", "sfx": "tick", "trans": "scrollUp",
            "vo": "Veintiuno de cada cien no llegan a fin de mes nunca jamas.",
            "props": {"total": 100, "highlight": 21, "caption": "21 de 100"}}
    g7 = _mut(lambda g: g["beats"].insert(2, dict(_pic)))
    r = validate(g7)
    n = len(g7["beats"])
    print(f"  [{'PASS' if n == 7 and not r['errors'] else 'FAIL'}] guion de 7 beats valido -> PASS{'' if not r['errors'] else ' | ' + '; '.join(r['errors'])}")
    # 8 beats ahora DENTRO de la banda (antes disparaba R5): no debe haber error de CONTEO.
    g8 = _mut(lambda g: [g["beats"].insert(2, dict(_pic)) for _ in range(2)] and None)
    r8 = validate(g8)
    no_count_err = not any("numero de beats" in e for e in r8["errors"])
    print(f"  [{'PASS' if len(g8['beats']) == 8 and no_count_err else 'FAIL'}] guion de 8 beats dentro de banda -> sin R5 de conteo")
    # 11 beats -> excede MAX_BEATS=10 -> R5 de conteo (otras reglas pueden disparar tambien; solo exijo el conteo).
    g11 = _mut(lambda g: [g["beats"].insert(2, dict(_pic)) for _ in range(5)] and None)
    r11 = validate(g11)
    has_count_err = any("numero de beats" in e for e in r11["errors"])
    print(f"  [{'PASS' if len(g11['beats']) == 11 and has_count_err else 'FAIL'}] guion de 11 beats -> R5 de conteo")


def run_proposer():
    print("\n-- proposer (esqueleto -> validador) --")
    from proposer import propose
    okc = 0
    for seed in range(12):
        g = propose("Tema novedoso unico variante " + str(seed), seed=seed, n_data=2)
        r = validate(g)
        ok = (g is not None and not r["errors"])
        okc += ok
        if not ok:
            print(f"  [FAIL] seed {seed}: " + "; ".join(r["errors"]))
    print(f"  [{'PASS' if okc == 12 else 'FAIL'}] 12 esqueletos n_data=2 (6 beats) pasan el validador ({okc}/12)")
    okc3 = 0
    for seed in range(12):
        g = propose("Otro tema distinto numero " + str(seed), seed=seed, n_data=3)
        r = validate(g)
        ok = (g is not None and not r["errors"] and len(g["beats"]) == 7)
        okc3 += ok
        if not ok:
            print(f"  [FAIL] seed {seed} (n_data=3): " + ("; ".join(r["errors"]) or f"beats={len(g['beats'])}"))
    print(f"  [{'PASS' if okc3 == 12 else 'FAIL'}] 12 esqueletos n_data=3 (7 beats) pasan el validador ({okc3}/12)")
    # con ledger: el combo del primer esqueleto queda registrado y el proposer evita repetirlo
    tmp = Path(tempfile.gettempdir()) / "ledger_proposer_test.json"
    tmp.unlink(missing_ok=True)
    led = Ledger(path=tmp)
    g_a = propose("Tema ledger alpha beta gamma", seed=1)
    led.append_video(g_a["slug"], g_a["title"], g_a["beats"], fecha="2026-06-13")
    g_b = propose("Otro tema delta epsilon zeta", ledger=led, seed=1)
    r_b = validate(g_b, ledger=led)
    print(f"  [{'PASS' if not r_b['errors'] else 'FAIL'}] proposer con ledger genera combo NO repetido ({'; '.join(r_b['errors']) or 'ok'})")
    tmp.unlink(missing_ok=True)


def run_ledger():
    print("\n-- ledger --")
    tmp = Path(tempfile.gettempdir()) / "ledger_test_dineroia.json"
    if tmp.exists():
        tmp.unlink()
    led = Ledger(path=tmp)
    print(f"  [{'PASS' if led.videos == [] else 'FAIL'}] empieza vacio")

    g = GOOD()
    led.append_video(g["slug"], g["title"], g["beats"], fecha="2026-06-13")
    print(f"  [{'PASS' if len(led.videos) == 1 else 'FAIL'}] append registra 1 video")

    # mismo tema -> repetido
    rep_t, slug_t, sim = led.is_tema_repeated("Inventado prueba alfa zeta")
    print(f"  [{'PASS' if rep_t else 'FAIL'}] detecta tema repetido (sim {sim} vs {slug_t})")
    # tema nuevo -> no repetido
    rep_t2, _, _ = led.is_tema_repeated("Petroleo Venezuela colapso hiperinflacion bolivar")
    print(f"  [{'PASS' if not rep_t2 else 'FAIL'}] tema distinto NO se marca repetido")
    # mismo combo visual -> repetido
    rep_c, slug_c = led.is_combo_repeated(g["beats"])
    print(f"  [{'PASS' if rep_c else 'FAIL'}] detecta combinacion visual repetida (vs {slug_c})")
    # combo distinto
    rep_c2, _ = led.is_combo_repeated(["BeatKinetic", "BeatDonut", "BeatCta"])
    print(f"  [{'PASS' if not rep_c2 else 'FAIL'}] combinacion visual distinta NO se marca repetida")

    # validate con ledger -> bloquea el mismo guion
    res = validate(g, ledger=led)
    blocked = any(e.startswith("R9") for e in res["errors"])
    print(f"  [{'PASS' if blocked else 'FAIL'}] validate(ledger) bloquea tema+combo+slug repetidos")
    tmp.unlink(missing_ok=True)


def run_recency():
    """R10: no reusar un visual de FIRMA (= espectaculo wow, ledger.SIGNATURE_WOW)
    usado en los ultimos RECENCY_WINDOW videos (rota el wow del dia). Opcion A del
    freeze: la firma EXENTA las graficas/datos (lenguaje constante del canal) y las
    puntas del arco (esas las rota R11). Cuenta al total."""
    print("\n-- R10 recencia + firma wow-only (Opcion A del freeze) --")
    from validator import RECENCY_WINDOW
    from ledger import signature_types
    ok = total = 0

    def chk(cond, label):
        nonlocal ok, total
        total += 1
        ok += bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    # firma = SOLO el espectaculo wow; graficas/datos y puntas del arco quedan FUERA.
    sig = signature_types(["BeatKinetic", "BeatMapZoom", "BeatBars",
                           "BeatPictogram", "BeatBigNumber", "BeatCta"])
    chk(set(sig) == {"BeatMapZoom"},
        "firma = solo wow (MapZoom); excluye graficas (Bars/Pictogram) y puntas (Kinetic/BigNumber/Cta)")
    # un video cuyo unico 'visual' son graficas constantes -> firma VACIA: invisible
    # a R9-combo/R10 (la linea verde->rojo sale a diario A PROPOSITO, no es repeticion).
    chk(signature_types(["BeatKinetic", "BeatLineChart", "BeatPictogram", "BeatCta"]) == [],
        "video sin espectaculo wow -> firma vacia (la grafica constante no cuenta)")

    tmp = Path(tempfile.gettempdir()) / "ledger_recency_test.json"
    tmp.unlink(missing_ok=True)
    led = Ledger(path=tmp)
    # video reciente cuyo wow es BeatMapZoom (el wow de GOOD), con tema y combo
    # DISTINTOS de GOOD para aislar R10 de R9.
    led.append_video("otro_video_reciente",
                     "Petroleo Venezuela colapso bolivar hiperinflacion",
                     ["BeatKinetic", "BeatMapZoom", "BeatLineChart", "BeatCta"], fecha="2026-06-13")
    chk(led.recent_beats(RECENCY_WINDOW) == {"BeatMapZoom"},
        "recent_beats() = solo el espectaculo wow del video reciente (BeatMapZoom)")
    chk(led.recent_beats(0) == set(), "recent_beats(0) desactiva la recencia")

    # GOOD (wow: BeatMapZoom) reusa el MapZoom recien usado -> R10, y SOLO R10
    # (tema/combo/slug son novedosos, no debe saltar R9).
    r = validate(GOOD(), ledger=led)
    fired = [e for e in r["errors"] if e.startswith("R10")]
    chk(fired and all("BeatMapZoom" in e for e in fired)
        and not any(e.startswith("R9") for e in r["errors"]),
        "GOOD reusa BeatMapZoom en ventana -> R10 (solo BeatMapZoom; sin R9 falso)")

    # empuja BeatMapZoom fuera de la ventana con N videos cuyo wow es OTRO (MultiMap)
    for k in range(RECENCY_WINDOW):
        led.append_video(f"filler_{k}", f"relleno aislado numero {k} omega",
                         ["BeatKinetic", "BeatMultiMap", "BeatLineChart", "BeatCta"],
                         fecha="2026-06-13", save=False)
    r2 = validate(GOOD(), ledger=led)
    chk(not any(e.startswith("R10") for e in r2["errors"]),
        "BeatMapZoom fuera de la ventana (N videos despues) -> sin R10")
    tmp.unlink(missing_ok=True)
    return ok, total


def run_bookend():
    """R11: las PUNTAS del arco (hook/cierre) ROTAN respecto al video anterior
    (variedad en secuencia). El climax NO se rota (BeatHeroCoin es solo-cripto, su
    default es BeatBigNumber). Un slot con un solo tipo (hoy el cierre) se OMITE.
    Tambien prueba que BeatStatCallout es un hook valido y que, como punta, queda
    FUERA de la firma (lo gobierna R11, no la recencia). Cuenta al total."""
    print("\n-- R11 rotacion de puntas (hook/cierre) --")
    from validator import HOOK_TYPES
    from ledger import signature_types
    ok = total = 0

    def chk(cond, label):
        nonlocal ok, total
        total += 1
        ok += bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    chk("BeatStatCallout" in HOOK_TYPES, "BeatStatCallout esta en HOOK_TYPES (hook alterno)")

    # StatCallout como primer beat = hook valido (R4 no se queja del arco)
    g_stat = _mut(lambda g: g["beats"].__setitem__(0,
        {"id": "b1_hook", "type": "BeatStatCallout", "sfx": "impact", "trans": "scrollUp",
         "vo": "Esta sola cifra deberia bastar para que cambies como ves tu dinero hoy",
         "props": {"stat": "8 de cada 10", "context": "no llegan a fin de mes"}}))
    r_stat = validate(g_stat)
    chk(not r_stat["errors"], f"BeatStatCallout como hook -> guion valido ({'; '.join(r_stat['errors']) or 'ok'})")

    # punta -> fuera de la firma (no suma a R9/R10)
    chk("BeatStatCallout" not in signature_types(
        ["BeatStatCallout", "BeatBars", "BeatBigNumber", "BeatCta"]),
        "BeatStatCallout excluido de la firma (es punta -> lo rota R11)")

    # video previo: hook=Kinetic, climax=BigNumber, medio Donut+Waterfall
    tmp = Path(tempfile.gettempdir()) / "ledger_bookend_test.json"
    tmp.unlink(missing_ok=True)
    led = Ledger(path=tmp)
    led.append_video("previo_uno", "Petroleo Venezuela colapso bolivar hiperinflacion",
                     ["BeatKinetic", "BeatDonut", "BeatWaterfall", "BeatBigNumber", "BeatCta"],
                     fecha="2026-06-13")

    def _arg_video(slug, hook, climax):
        # tema/medio DISTINTOS del previo para aislar R11 de R9/R10.
        return {"slug": slug, "title": "Argentina peso dolar blue brecha cambiaria",
                "beats": [
                    hook,
                    {"id": "b2", "type": "BeatBubble", "sfx": "tick", "trans": "scrollUp",
                     "vo": "Tres burbujas muestran tamanos muy distintos de cada economia analizada hoy.",
                     "props": {"caption": "x", "points": [], "label": "y"}},
                    {"id": "b3", "type": "BeatRadar", "sfx": "tick", "trans": "scrollUp",
                     "vo": "El radar compara cinco ejes distintos entre los dos paises vecinos ahora.",
                     "props": {"caption": "x", "points": [], "label": "y"}},
                    climax,
                    _cta(),
                ]}

    big = {"id": "b4_big", "type": "BeatBigNumber", "sfx": "impact", "trans": "flashWhite",
           "vo": "El numero final llega a trescientos mil dolares para cerrar la idea.",
           "cues": {"countEndWord": "dolares"},
           "props": {"value": 300000, "prefix": "$", "suffix": " USD", "caption": "x"}}
    coin = {"id": "b4_coin", "type": "BeatHeroCoin", "sfx": "impact", "trans": "flashWhite",
            "vo": "El numero final llega a trescientos mil dolares para cerrar la idea.",
            "cues": {"countEndWord": "dolares"},
            "props": {"value": 300000, "prefix": "$", "suffix": " USD", "caption": "x"}}
    kin = _kinetic_hook("Una historia distinta arranca aqui con toda la fuerza posible hoy")
    stat = {"id": "b1_hook", "type": "BeatStatCallout", "sfx": "impact", "trans": "scrollUp",
            "vo": "Esta sola cifra deberia bastar para que cambies como ves tu dinero hoy",
            "props": {"stat": "200%", "context": "de inflacion anual"}}

    # REPITE hook(Kinetic)+climax(BigNumber) del anterior -> R11 SOLO en el hook
    # (el climax no se rota: BeatBigNumber repetido es valido).
    r_rep = validate(_arg_video("repite_puntas", kin, big), ledger=led)
    fired = [e for e in r_rep["errors"] if e.startswith("R11")]
    chk(any("hook" in e for e in fired) and not any("climax" in e for e in fired),
        "repetir hook(Kinetic) dispara R11; el climax (BigNumber) repetido NO")
    chk(not any("cierre" in e for e in fired),
        "el cierre NO dispara R11 (un solo tipo de CTA -> slot omitido)")

    # ROTA el hook (->StatCallout) y usa climax HeroCoin (permitido) -> sin R11
    r_rot = validate(_arg_video("rota_puntas", stat, coin), ledger=led)
    chk(not any(e.startswith("R11") for e in r_rot["errors"]),
        "rotar hook->StatCallout (climax HeroCoin permitido) -> sin R11")
    chk(not r_rot["errors"], f"video con puntas rotadas es totalmente valido ({'; '.join(r_rot['errors']) or 'ok'})")
    tmp.unlink(missing_ok=True)
    return ok, total


def run_freeze_deadlock():
    """REGRESION del deadlock R8/R10 (sesion 2026-06-19). Al congelar el catalogo al
    kit-10, R8 forzaba la unica grafica frozen (LineChart) en cada video y la firma
    'todo el medio' + window=3 la bloqueaba al 2o dia -> 9/10 deadlocks. La Opcion A
    (firma wow-only + RECENCY_WINDOW=2 + R9-combo solo si firma>=2) lo rompe.

    Esta sim corre N videos CONSECUTIVOS contra un ledger VIVO (maxima presion: cada
    video aprobado entra y aprieta al siguiente) y exige 0 deadlocks (= validate con
    errores DESPUES de que el proposer agoto sus reintentos). Temas 100% unicos por
    video (Jaccard 0) -> aisla el deadlock REAL (R10/R9-combo) de un falso R9-tema.
    La sim multi-video es la AUTORIDAD de la libertad de deadlock; los unit tests de
    arriba cubren casos puntuales, esto cubre la DINAMICA dia-a-dia."""
    print("\n-- freeze: 0 deadlocks en N videos consecutivos (Opcion A) --")
    from proposer import propose
    ok = total = 0

    def chk(cond, label):
        nonlocal ok, total
        total += 1
        ok += bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    def sim(n_videos, n_data):
        tmp = Path(tempfile.gettempdir()) / f"ledger_freeze_dl_{n_data}.json"
        tmp.unlink(missing_ok=True)
        led = Ledger(path=tmp)
        deadlocks = []
        for i in range(n_videos):
            tema = f"alfa{i} beta{i} gamma{i} delta{i}"   # tokens unicos -> Jaccard 0
            g = propose(tema, ledger=led, n_data=n_data, seed=1000 + i)
            errs = validate(g, ledger=led)["errors"]
            if errs:
                deadlocks.append((i, errs))
            led.append_video(g["slug"], g["title"], g["beats"], fecha="2026-06-19")
        tmp.unlink(missing_ok=True)
        return deadlocks

    for n_data in (2, 3):
        dl = sim(20, n_data)
        detail = "ok" if not dl else f"v{dl[0][0]}: {'; '.join(dl[0][1])}"
        chk(not dl, f"20 videos consecutivos n_data={n_data} -> 0 deadlocks ({detail})")
    return ok, total


if __name__ == "__main__":
    print("== casos de validacion (fixtures buenos/malos) ==")
    ok, total = run_cases()
    run_brief()
    run_round()
    okc, totc = run_color()
    ok += okc
    total += totc
    run_maxbeats()
    run_proposer()
    run_ledger()
    okr, totr = run_recency()
    ok += okr
    total += totr
    okb, totb = run_bookend()
    ok += okb
    total += totb
    okd, totd = run_freeze_deadlock()
    ok += okd
    total += totd
    print(f"\nRESULTADO casos duros: {ok}/{total}")
    sys.exit(0 if ok == total else 1)
