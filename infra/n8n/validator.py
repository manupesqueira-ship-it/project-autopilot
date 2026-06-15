# -*- coding: utf-8 -*-
"""
Validador del "director" de Dinero IA: logica PURA que rechaza guiones malos.

No renderiza ni llama a la voz: trabaja solo sobre el JSON del guion (y,
opcionalmente, el brief y el ledger). Se importa desde test_planner.py y desde
el workflow de n8n (via CLI). Es la FUENTE DE VERDAD de las reglas del director.

API:
    from validator import validate, is_valid
    res = validate(guion, brief=None, ledger=None, strict=False)
    # res = {"errors": [...], "warnings": [...]}
    is_valid(guion) -> bool   (True si no hay errores duros)

CLI:
    python validator.py guion_x.json [--brief brief.txt] [--ledger] [--strict]
    # exit 0 = PASS, exit 1 = FAIL (hay errores duros)

Reglas duras (errors) -> rechazan el guion:
  R1  ningun beat de aterrizaje estatico >2.5s sin sub-evento que cubra el final
  R2  <=2 beats del mismo tipo por video y NUNCA 2 iguales seguidos
  R3  >=1 visual "wow" (mapa/caricatura/3D/grafica espectaculo) por video
  R4  arco fijo: hook -> contexto -> 2-3 datos (visual distinto c/u) -> climax numero -> CTA
  R5  ultimo beat = BeatCta; entre MIN_BEATS y MAX_BEATS beats; slug valido
  R6  moneda explicita en la cifra protagonista (USD o MXN visible)
  R7  cada cue existe LITERAL en el `vo` de su beat
  R8  (heredadas de test_planner) tipos validos, grafica de datos obligatoria,
      caricatura dentro del roster, max 1 beat espectaculo, beat sin vo
  R9  (si hay ledger) tema NO repetido y combinacion visual NO repetida
  R10 (si hay ledger) recencia: ningun visual de FIRMA usado en los ultimos
      RECENCY_WINDOW videos (rota el medio dia a dia para no cansar al espectador)
  R11 (si hay ledger) rota las PUNTAS del arco (hook/climax/cierre) respecto al
      video anterior; un slot con <2 tipos validos se omite (se auto-activa luego)

Reglas blandas (warnings, no rechazan salvo --strict):
  W-num  cifra mostrada que no aparece en el brief (posible dato inventado)
  W-cur  cifras secundarias sin moneda explicita
"""
import colorsys
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
ASSEMBLER = HERE.parent / "assembler"
if str(ASSEMBLER) not in sys.path:
    sys.path.insert(0, str(ASSEMBLER))

# ------------------------------------------------------------------ constantes
# Timing (debe espejar build916.py: LEAD=0.25, TAIL=0.50, FPS=30).
LEAD, TAIL = 0.25, 0.50
# Tasa de habla del narrador (es-MX, tono serio/lento). Calibrada con
# el_salvador (7 beats ~= 81.5s, ~210 palabras -> ~2.6 palabras/seg).
SPEAKING_RATE_WPS = 2.6
STATIC_MAX_S = 2.5      # ningun tramo estatico puede durar mas que esto
LATE_FRAC = 0.5         # el sub-evento que "cubre el final" debe caer pasada
#                          esta fraccion de las palabras del vo
KINETIC_COVER = 0.5     # un hook kinetic debe revelar >= este % de su vo

MIN_BEATS, MAX_BEATS = 3, 7   # El Salvador aprobado tiene 7 beats

# R10 (recencia): a 3 videos/dia, no reusar un visual de FIRMA que ya salio en
# los ultimos N videos -> rota el medio para que el espectador diario no se
# canse (las puntas del arco -hook/climax/cierre- se excluyen de la firma en
# ledger.py, asi que rotan aparte). Ventana conservadora: con ~20+ visuales en
# el pool y ~3 datos por video, 3 deja amplio margen al proposer. Subir N = mas
# variedad, mas presion al planner. 0 desactiva la regla.
RECENCY_WINDOW = 3

# W-round: la NARRACION debe redondear cifras grandes ("alrededor de 200 M")
# mientras el VISUAL muestra la cifra exacta del brief.
ROUND_THRESHOLD = 1_000_000
HEDGE_WORDS = {
    "alrededor", "aproximadamente", "aprox", "cerca", "casi", "unos", "unas",
    "ronda", "rondando", "practicamente", "mas", "poco", "como",
    "aproximado", "redondeando", "redondo", "casi",
}

# R-color: el ROJO solo puede codificar una PERDIDA (regla semantica locked).
# filter_a NO puede atraparlo (el rojo es un tono permitido a nivel de pixel);
# se valida AQUI, sobre el dato. Un item categorico en rojo (una "categoria mas"
# pintada de rojo: Gastos, Deudas...) es decoracion, no perdida -> se marca.
# Palabras que SI justifican el rojo (la cifra ES una perdida/caida). Tight a
# proposito: no incluye "deuda"/"gasto"/"baja" (ambiguas) para no excusar rojos
# decorativos. Senal numerica de perdida = valor o delta NEGATIVO.
LOSS_WORDS = {
    "perdida", "perdidas", "caida", "caidas", "desplome", "desplomo",
    "derrumbe", "retroceso", "quiebra", "colapso", "hundimiento",
    "cayo", "cayeron", "perdio", "perdieron", "deficit", "negativo",
    "negativa", "minusvalia", "minusvalias", "numeros rojos",
}
COLOR_KEYS = ("color", "fill", "stroke", "accentColor", "barColor", "lineColor")

# --- Catalogo de tipos: la VERDAD viva esta en Root.tsx (crece seguido).
#     Se lee dinamicamente; este set es solo el fallback si no se halla.
CORE_TYPES = {
    "BeatKinetic", "BeatBigNumber", "BeatPictogram", "BeatBars",
    "BeatLineChart", "BeatAssetCard", "BeatTrendBreak", "BeatVersus",
    "BeatBarRace", "BeatTimeline", "BeatCta", "BeatMapZoom",
    "BeatCharacter", "BeatRecovery",
    "BeatDonut", "BeatWaterfall", "BeatBubble", "BeatCandlestick",
}
ROOT_TSX = HERE.parent / "remotion-render" / "src" / "Root.tsx"


def registered_beat_types(root_tsx=ROOT_TSX):
    """Lee los ids de Composition registrados en Root.tsx (fuente viva)."""
    try:
        txt = Path(root_tsx).read_text(encoding="utf-8")
    except OSError:
        return set()
    return set(re.findall(r'id="(Beat[A-Za-z0-9]+)"', txt))


TYPES = registered_beat_types() | CORE_TYPES

# Graficas de datos / visualizaciones de cantidad (al menos una obligatoria).
CHARTS = {
    "BeatLineChart", "BeatRecovery", "BeatTrendBreak", "BeatBarRace",
    "BeatBars", "BeatDonut", "BeatWaterfall", "BeatBubble", "BeatCandlestick",
    "BeatStackedArea", "BeatDialGauge", "BeatSlope", "BeatProgressRing",
    "BeatLollipop", "BeatFunnel", "BeatHistogram", "BeatHeatmap",
    "BeatTreemap", "BeatRadar", "BeatSankey", "BeatScaledIcon", "BeatTickerTape",
}
# Beats "espectaculo": maximo 1 por video (animacion pesada / cinematica).
SPECT = {"BeatTrendBreak", "BeatBarRace", "BeatTimeline", "BeatRecovery"}

# Visuales "wow" (>=1 por video). El subconjunto literal mapa/caricatura/3D es
# {BeatMapZoom, BeatCharacter, BeatMultiMap, BeatDebate}; se amplia con las
# graficas de alta produccion para que SIEMPRE haya al menos un visual potente.
WOW = {
    "BeatMapZoom", "BeatCharacter", "BeatMultiMap", "BeatDebate",
    "BeatNewsCard", "BeatHeroCoin", "BeatLogoWall",
    "BeatTrendBreak", "BeatBarRace", "BeatRecovery", "BeatTimeline",
    "BeatCandlestick", "BeatWaterfall", "BeatBubble", "BeatDonut",
    "BeatSankey", "BeatTreemap", "BeatHeatmap", "BeatRadar",
    "BeatStackedArea", "BeatTickerTape",
}

# Puntas del arco (R4/R5). Cada slot (hook / climax / cierre) tiene un SET de
# tipos validos; R11 obliga a ROTAR la punta respecto al video anterior
# (variedad en secuencia: que no todo abra/cierre igual). Un slot con un solo
# tipo no se puede rotar -> R11 lo OMITE hasta que gane un 2o tipo (auto-activo).
# OJO: estos tres sets deben espejar SIGNATURE_EXCLUDE de ledger.py (las puntas
# se gobiernan con R11, NO con la firma/recencia R9-R10).
HOOK_TYPES = {"BeatKinetic", "BeatStatCallout"}    # hook (beat 0): kinetic o cifra-shock
CLIMAX_TYPES = {"BeatBigNumber", "BeatHeroCoin"}   # clima: cifra protagonista (numero o moneda 3D)
CTA_TYPES = {"BeatCta"}                             # cierre (ultimo beat); 2o cierre pendiente
# "datos": beats de visualizacion que sostienen la parte media del arco.
DATA_VISUAL = CHARTS | {"BeatPictogram", "BeatVersus", "BeatAssetCard",
                        "BeatTimeline", "BeatScoreboard"}

# Beats que ANIMAN-Y-SE-QUEDAN (riesgo de tramo estatico si el vo es largo y
# la animacion aterriza temprano). El resto anima de forma continua (graficas
# que barren, mapa que hace zoom, kinetic que revela, pictograma que llena,
# CTA con bookmark pulsante) o es un visual "wow" con micro-motion propio.
LANDING = {"BeatBigNumber", "BeatAssetCard", "BeatVersus", "BeatBars",
           "BeatHeroCoin"}

ROSTER = {"bukele"}   # caricaturas ya generadas (sincronizar con public/characters)

_CUR_TOKENS = ("usd", "mxn", "dolares", "pesos", "dolar", "peso", "us$", "$mxn")


# ------------------------------------------------------------------ utilidades
def _norm(w):
    w = unicodedata.normalize("NFD", str(w).lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")  # quita acentos
    return re.sub(r"[^a-z0-9_]", "", w)


def _vo_words(vo):
    return [_norm(w) for w in str(vo).split() if _norm(w)]


def _est_seconds(vo):
    n = len([w for w in str(vo).split() if w.strip()])
    return LEAD + (n / SPEAKING_RATE_WPS) + TAIL


def _cue_word_index(cue, words):
    """Indice (0-based) de la palabra del cue en `words`.

    Soporta el sufijo de ocurrencia 'palabra:N'. Devuelve None si no aparece.
    """
    base, _, occ = str(cue).partition(":")
    target = _norm(base)
    occ = int(occ) if occ.isdigit() else 1
    seen = 0
    for i, w in enumerate(words):
        if w == target:
            seen += 1
            if seen == occ:
                return i
    return None


def _kinetic_revealed_words(props):
    """Cuenta palabras reveladas por un BeatKinetic (stanzas o lines)."""
    count = 0
    blocks = []
    if isinstance(props.get("stanzas"), list):
        for stanza in props["stanzas"]:
            for line in stanza:
                blocks.append(line)
    elif isinstance(props.get("lines"), list):
        for line in props["lines"]:
            blocks.append(line)
    for line in blocks:
        if isinstance(line, list):
            count += sum(1 for tok in line if isinstance(tok, dict)
                         and str(tok.get("text", "")).strip())
    return count


def _strings_in_props(props):
    """Aplana todos los strings visibles de los props (recursivo)."""
    out = []

    def walk(x):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(props)
    return out


def _has_currency(beat):
    blob = " ".join(_strings_in_props(beat.get("props", {})) + [beat.get("vo", "")])
    blob = blob.lower()
    return any(tok in blob for tok in _CUR_TOKENS)


def _has_dollar(beat):
    props = beat.get("props", {})
    return any("$" in s for s in _strings_in_props(props)) or \
        str(props.get("prefix", "")).strip() == "$"


# ----- chequeo de cifras vs brief (best-effort, genera warnings) -----
def _sig_digits(num_str):
    """Digitos significativos: quita separadores y ceros a la derecha.

    270000000 -> '27' ; 44,739 -> '44739' ; 209 millones->'209'.
    Permite casar la forma escalada del guion con la forma corta del brief.
    """
    d = re.sub(r"[^\d]", "", str(num_str))
    d = d.rstrip("0") or d
    return d


def _full_digits(num_str):
    return re.sub(r"[^\d]", "", str(num_str))


def _brief_number_sigs(brief_text):
    """(digitos_completos, digitos_significativos) presentes en el brief."""
    full, sig = set(), set()
    for m in re.findall(r"\d[\d,\.]*", brief_text):
        d = _full_digits(m)
        if d:
            full.add(d)
            sig.add(_sig_digits(m))
    return full, sig


def _displayed_numbers(beat):
    """Magnitudes que el video MUESTRA en pantalla para este beat."""
    p = beat.get("props", {})
    nums = []

    def add(v):
        if isinstance(v, (int, float)) and abs(v) >= 100:
            nums.append(v)
        elif isinstance(v, str):
            for m in re.findall(r"\d[\d,\.]*", v):
                digits = re.sub(r"[^\d]", "", m)
                if len(digits) < 3:
                    continue
                if len(digits) == 4 and 1900 <= int(digits) <= 2099:
                    continue  # es un anio, no un monto
                nums.append(m)

    for key in ("value", "price", "countFrom", "countTo"):
        if key in p:
            add(p[key])
    for side in ("left", "right"):
        if isinstance(p.get(side), dict):
            add(p[side].get("value"))
    # Solo etiquetas de VALOR de graficas (no caption/subline descriptivos).
    for key in ("troughLabel", "endLabel", "peakLabel"):
        if key in p:
            add(p[key])
    if isinstance(p.get("bars"), list):
        for b in p["bars"]:
            if isinstance(b, dict):
                add(b.get("value"))
    if isinstance(p.get("labels"), list):
        for lb in p["labels"]:
            if isinstance(lb, dict):
                add(lb.get("text"))
    return nums


def _max_magnitude(beat):
    """Mayor magnitud numerica que el beat MUESTRA en pantalla (0 si ninguna)."""
    best = 0
    for n in _displayed_numbers(beat):
        d = _full_digits(n)
        if d:
            best = max(best, int(d))
    return best


def _vo_has_hedge(vo):
    """True si el vo incluye una palabra de redondeo ('alrededor', 'unos'...)."""
    return any(w in HEDGE_WORDS for w in _vo_words(vo))


# ----- R-color: rojo = SOLO perdida (chequeo semantico, no de pixel) -----
def _is_red(v):
    """True si el valor de color es ROJO (hex saturado en hue ~0, o token rojo)."""
    if not isinstance(v, str):
        return False
    s = v.strip().lower()
    if s in ("red", "rojo"):
        return True
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})", s)
    if not m:
        return False
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    h = h[:6]  # ignora alpha
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    hh, ss, vv = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if ss < 0.35 or vv < 0.45:
        return False  # gris/oscuro, no es "rojo" categorico
    deg = hh * 360
    return deg <= 12 or deg >= 348


def _vo_has_loss(vo):
    """True si la NARRACION del beat habla de una perdida/caida. Si el beat es
    tematicamente de perdida, su rojo es legitimo (p.ej. BeatRecovery: el tramo
    de la caida va en rojo y el vo dice 'cayo'/'se desplomo')."""
    t = "".join(_norm(w) for w in str(vo).split())
    return any(w.replace(" ", "") in t for w in LOSS_WORDS)


def _item_is_loss(d):
    """True si el item trae senal de perdida: valor/delta negativo o palabra clave."""
    for k in ("value", "deltaPct", "delta", "change", "pct", "value2", "to", "end"):
        x = d.get(k)
        if isinstance(x, (int, float)) and x < 0:
            return True
    for s in _strings_in_props(d):
        norm = " ".join(_norm(w) for w in str(s).split())
        if any(w.replace(" ", "") in norm.replace(" ", "") for w in LOSS_WORDS):
            return True
    return False


def _red_decor_items(beat):
    """Etiquetas de items CATEGORICOS (dentro de una lista) pintados de rojo SIN
    senal de perdida. Solo mira items de listas: ahi vive el rojo-decorativo
    ('una categoria mas' en rojo). Un accentColor rojo a nivel beat se respeta
    (suele ser un clima de perdida intencional)."""
    bad = []

    def walk(node, in_list):
        if isinstance(node, dict):
            if in_list and any(_is_red(node.get(k)) for k in COLOR_KEYS) and not _item_is_loss(node):
                lbl = node.get("label") or node.get("name") or node.get("title")
                bad.append(str(lbl) if lbl else "(item sin etiqueta)")
            for v in node.values():
                walk(v, False)
        elif isinstance(node, list):
            for v in node:
                walk(v, True)

    walk(beat.get("props", {}), False)
    return bad


# ------------------------------------------------------------------ validacion
def validate(guion, brief=None, ledger=None, strict=False):
    """Valida un guion. Devuelve {"errors": [...], "warnings": [...]}.

    `brief`  : texto del brief (opcional) para chequear cifras inventadas.
    `ledger` : instancia de Ledger (opcional) para bloquear repeticiones.
    `strict` : si True, los warnings tambien cuentan como errores.
    """
    errors, warnings = [], []
    beats = guion.get("beats", []) if isinstance(guion, dict) else []
    types = [b.get("type") for b in beats]

    # ---- R5: estructura basica ----
    slug = guion.get("slug", "") if isinstance(guion, dict) else ""
    if not re.fullmatch(r"[a-z0-9_]+", slug or ""):
        errors.append("R5 slug invalido o ausente")
    if not (MIN_BEATS <= len(beats) <= MAX_BEATS):
        errors.append(f"R5 numero de beats={len(beats)} (debe ser {MIN_BEATS}-{MAX_BEATS})")
    if beats and types[-1] not in CTA_TYPES:
        errors.append(f"R5 el ultimo beat debe ser un cierre {sorted(CTA_TYPES)}")
    if any(t in CTA_TYPES for t in types[:-1]):
        errors.append("R5 el cierre (CTA) solo puede ir al final")

    # ---- R8: tipos validos, vo presente, roster, espectaculo ----
    spect = 0
    for i, b in enumerate(beats):
        t = b.get("type")
        if t not in TYPES:
            errors.append(f"R8 tipo desconocido '{t}' (beat {b.get('id', i)})")
        if t in SPECT:
            spect += 1
        if not str(b.get("vo", "")).strip():
            errors.append(f"R8 beat {b.get('id', i)} sin vo")
        if t == "BeatCharacter":
            sl = b.get("props", {}).get("imageSlug")
            if sl not in ROSTER:
                errors.append(f"R8 caricatura '{sl}' fuera del roster {sorted(ROSTER)}")
    if spect > 1:
        errors.append(f"R8 {spect} beats espectaculo (maximo 1)")
    if beats and not any(t in CHARTS for t in types):
        errors.append("R8 falta al menos una grafica de datos")

    # ---- R2: <=2 del mismo tipo y nunca 2 iguales seguidos ----
    for i in range(1, len(types)):
        if types[i] and types[i] == types[i - 1]:
            errors.append(f"R2 dos '{types[i]}' seguidos (pos {i})")
    counts = {}
    for t in types:
        counts[t] = counts.get(t, 0) + 1
    for t, c in counts.items():
        # Kinetic/Cta de texto pueden repetir poco; aun asi cap a 2 como pide la regla.
        if c > 2:
            errors.append(f"R2 '{t}' aparece {c} veces (maximo 2 por video)")

    # ---- R3: >=1 visual wow ----
    if beats and not any(t in WOW for t in types):
        errors.append("R3 falta un visual 'wow' (mapa/caricatura/grafica espectaculo)")

    # ---- R4: arco hook -> contexto -> 2-3 datos distintos -> climax -> CTA ----
    if beats:
        if types[0] not in HOOK_TYPES:
            errors.append(f"R4 el primer beat debe ser hook {sorted(HOOK_TYPES)} (es '{types[0]}')")
        # datos en la parte media (excluye hook[0], climax-final y CTA)
        middle = types[1:-1]  # quita hook y CTA
        data_types = [t for t in middle if t in DATA_VISUAL]
        distinct_data = set(data_types)
        if len(distinct_data) < 2:
            errors.append(f"R4 se necesitan >=2 datos visuales DISTINTOS en la parte media (hay {len(distinct_data)})")
        if len(distinct_data) > 3:
            warnings.append(f"R4 hay {len(distinct_data)} tipos de dato en la parte media (el arco pide 2-3)")
        # climax numero: debe existir un BeatBigNumber despues de algun dato
        bignum_idx = [i for i, t in enumerate(types) if t in CLIMAX_TYPES]
        first_data_idx = next((i for i, t in enumerate(types) if t in DATA_VISUAL), None)
        if not bignum_idx:
            errors.append("R4 falta el climax: un BeatBigNumber con la cifra protagonista")
        elif first_data_idx is not None and max(bignum_idx) < first_data_idx:
            errors.append("R4 el climax (BeatBigNumber) debe ir DESPUES de los datos")

    # ---- R1: tramos estaticos ----
    for i, b in enumerate(beats):
        t = b.get("type")
        dur = _est_seconds(b.get("vo", ""))
        if t == "BeatKinetic":
            vo_n = len(_vo_words(b.get("vo", "")))
            rev = _kinetic_revealed_words(b.get("props", {}))
            if dur > STATIC_MAX_S and vo_n and (rev / vo_n) < KINETIC_COVER:
                errors.append(
                    f"R1 hook '{b.get('id', i)}' revela {rev}/{vo_n} palabras "
                    f"(~{dur:.1f}s); cubre <{int(KINETIC_COVER*100)}% del vo -> congelado")
            continue
        if t not in LANDING:
            continue
        if dur <= STATIC_MAX_S:
            continue
        # beat de aterrizaje largo: necesita un sub-evento que caiga tarde
        words = _vo_words(b.get("vo", ""))
        cues = b.get("cues", {}) or {}
        anchors = []
        for k in ("countEndWord", "breakWord", "leftEndWord", "rightEndWord"):
            if cues.get(k):
                anchors.append(cues[k])
        for k in ("growWords", "pulseWords"):
            if isinstance(cues.get(k), list) and cues[k]:
                anchors.append(cues[k][-1])  # el ultimo, que es el mas tardio
        late = False
        for a in anchors:
            idx = _cue_word_index(a, words)
            if idx is not None and len(words) > 1 and idx >= LATE_FRAC * (len(words) - 1):
                late = True
                break
        if not late:
            errors.append(
                f"R1 beat '{b.get('id', i)}' (~{dur:.1f}s, tipo {t}) aterriza temprano "
                f"y se queda estatico; agrega un cue (countEndWord/growWords) que caiga "
                f"en la 2a mitad del vo")

    # ---- R7: cada cue existe literal en el vo de su beat ----
    for i, b in enumerate(beats):
        words = _vo_words(b.get("vo", ""))
        cues = b.get("cues", {}) or {}
        allc = []
        for k in ("growWords", "pulseWords"):
            if isinstance(cues.get(k), list):
                allc += cues[k]
        for k in ("countEndWord", "breakWord", "leftEndWord", "rightEndWord"):
            if cues.get(k):
                allc.append(cues[k])
        for c in allc:
            if _cue_word_index(c, words) is None:
                errors.append(f"R7 cue '{c}' no esta en el vo de {b.get('id', i)}")

    # ---- R6: moneda explicita en la cifra protagonista ----
    for i, b in enumerate(beats):
        if b.get("type") in CLIMAX_TYPES and _has_dollar(b):
            if not _has_currency(b):
                errors.append(f"R6 la cifra protagonista '{b.get('id', i)}' no muestra moneda (USD/MXN)")
        elif b.get("type") in ("BeatAssetCard", "BeatVersus", "BeatBars") and _has_dollar(b):
            if not _has_currency(b):
                warnings.append(f"W-cur '{b.get('id', i)}' muestra '$' sin moneda explicita (USD/MXN)")

    # ---- R-color: rojo = SOLO perdida (decorativo prohibido) ----
    for i, b in enumerate(beats):
        if _vo_has_loss(b.get("vo", "")):
            continue  # beat con narrativa de perdida -> su rojo es tematico
        for lbl in _red_decor_items(b):
            warnings.append(
                f"R-color beat '{b.get('id', i)}': ROJO en el item '{lbl}' sin "
                f"senal de perdida (regla locked: rojo = SOLO perdida). Usa "
                f"neutro/oro/verde, o marca el dato como perdida (valor/deltaPct "
                f"negativo o etiqueta 'perdida/caida').")

    # ---- W-num: cifras que no estan en el brief ----
    if brief:
        brief_full, brief_sig = _brief_number_sigs(brief)
        for i, b in enumerate(beats):
            for n in _displayed_numbers(b):
                full = _full_digits(n)
                if len(full) < 3:
                    continue
                if full in brief_full or _sig_digits(n) in brief_sig:
                    continue
                warnings.append(
                    f"W-num beat '{b.get('id', i)}' muestra {n!r} que no aparece en el brief (verifica que no sea inventada)")

    # ---- W-round: el visual muestra cifra exacta grande; la voz deberia redondear ----
    for i, b in enumerate(beats):
        mag = _max_magnitude(b)
        if mag >= ROUND_THRESHOLD and not _vo_has_hedge(b.get("vo", "")):
            warnings.append(
                f"W-round beat '{b.get('id', i)}' muestra {mag:,} exacto pero el vo no "
                f"redondea (usa 'alrededor de'/'unos'/'casi' en la narracion; el numero "
                f"en pantalla queda exacto)")

    # ---- R9/R10: ledger (tema, combo y recencia) ----
    if ledger is not None and isinstance(guion, dict):
        from ledger import signature_types  # mismo set de exclusion que el ledger
        tema = guion.get("title", "") or slug
        rep_t, slug_t, sim = ledger.is_tema_repeated(tema)
        if rep_t:
            errors.append(f"R9 tema repetido (sim {sim}) vs video '{slug_t}'")
        rep_c, slug_c = ledger.is_combo_repeated(beats)
        if rep_c:
            errors.append(f"R9 combinacion visual de beats repetida vs video '{slug_c}'")
        if ledger.has_slug(slug):
            errors.append(f"R9 slug '{slug}' ya existe en el ledger")

        # R10: no reusar un visual de FIRMA usado en los ultimos N videos.
        recent = ledger.recent_beats(RECENCY_WINDOW)
        for t in sorted(set(signature_types(beats)) & recent):
            errors.append(
                f"R10 '{t}' se uso en los ultimos {RECENCY_WINDOW} videos; rota a "
                f"otro visual para no cansar al espectador (variedad en secuencia)")

        # R11: rotar las PUNTAS del arco (hook/climax/cierre) respecto al video
        # anterior, para que no todo abra/cierre igual (variedad en secuencia).
        # Ventana = 1 (solo el inmediato anterior): con >=2 opciones por slot la
        # alternancia siempre es posible; una ventana mayor podria bloquear el
        # slot. Un slot con un solo tipo (hoy el cierre) se OMITE -> la regla se
        # auto-activa el dia que ese slot gane un 2o tipo.
        if ledger.videos:
            prev = ledger.videos[-1].get("beats_usados", [])
            prev_slug = ledger.videos[-1].get("slug")
            cur_climax = next((t for t in types if t in CLIMAX_TYPES), None)
            pre_climax = next((t for t in prev if t in CLIMAX_TYPES), None)
            slots = (
                ("hook", HOOK_TYPES, types[0] if types else None, prev[0] if prev else None),
                ("climax", CLIMAX_TYPES, cur_climax, pre_climax),
                ("cierre", CTA_TYPES, types[-1] if types else None, prev[-1] if prev else None),
            )
            for label, pool, cur, pre in slots:
                if len(pool) >= 2 and cur and cur == pre:
                    errors.append(
                        f"R11 el {label} '{cur}' es igual al del video anterior "
                        f"'{prev_slug}'; rota la punta (variedad en secuencia)")

    if strict:
        errors = errors + [w for w in warnings]
        warnings = []
    return {"errors": errors, "warnings": warnings}


def is_valid(guion, **kw):
    return not validate(guion, **kw)["errors"]


# ----------------------------------------------------------------------- CLI
def _cli(argv):
    if not argv:
        print(__doc__)
        return 2
    path = argv[0]
    guion = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    brief = None
    if "--brief" in argv:
        bp = argv[argv.index("--brief") + 1]
        brief = Path(bp).read_text(encoding="utf-8-sig")
    ledger = None
    if "--ledger" in argv:
        from ledger import Ledger
        ledger = Ledger()
    strict = "--strict" in argv

    res = validate(guion, brief=brief, ledger=ledger, strict=strict)
    for w in res["warnings"]:
        print("  WARN:", w)
    if res["errors"]:
        print("VALIDADOR: FAIL")
        for e in res["errors"]:
            print("  -", e)
        return 1
    print("VALIDADOR: PASS" + (f" ({len(res['warnings'])} warnings)" if res["warnings"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
