"""news_director.py — AGENTE DIRECTOR v2: noticia -> tratamiento listo para assemble_news.py.

Toma una NOTICIA (titular + hechos/datos verificados) y DISEÑA el reel completo:
reescribe el hook (reglas de escritura es-MX minadas), arma el arco beat por beat
eligiendo del MENÚ CERRADO v2 (beats2 + gráficas ECharts), elige transición por
relación narrativa, ancla la cifra a la PALABRA del VO (target_word) y escribe la
narración. El output ES el treatment que consume assemble_news.py sin tocar nada:
    python news_director.py brief.json          -> out/_treatments/news_treatment.json
    python assemble_news.py <treatment> <slug>  -> reel FINAL con gates

Brief: {"headline","facts":{clave:{value,unit,source?,as_of?}},"why_matters"}
v2 (2026-07-03): menú = NewsReel MAP real (12 tipos, props exactas de beats2);
schema por beat {type, vo, props, target_word?, trans?, min_s?}; reglas de
escritura es-MX de docs/standards/MINED_KNOWLEDGE_2026-07-03.md en el system.
"""
import json, sys, urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
MODEL = "claude-sonnet-5"


def load_key():
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("ANTHROPIC_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("no ANTHROPIC key")


# MENÚ CERRADO v3 = MASTERS congelados (kit2, mundo de la página; MastersReel MAP).
# El movimiento NO existe en este schema: solo DATOS. Props EXACTAS.
CATALOG = r"""
- hook    : titular que frena el scroll, palabra por palabra (grotesca fina MAYÚS; las palabras
            accent REPOSAN en esmeralda — máx 2). props {kicker:"MAYÚS 2-4 palabras",
            words:[{t,accent?:true}...], tease:"remate corto"}
            ⚠ target_word = LA palabra del VO donde entra la primera palabra accent.
- cifra   : CIFRA HÉROE con odómetro que asienta de izquierda a derecha.
            props {kicker, value:"$96,209" (string exacto YA formateado), unit:"MXN"|"%"|"",
            sub:"frase de contexto", foot?:"FUENTE · FECHA"}
            ⚠ OBLIGATORIO target_word = palabra del VO donde aterriza la cifra.
- linea   : línea héroe que se TRAZA completa (curva sin overshoot) con punto esmeralda en la
            cabeza; el endTag aterriza al final. props {kicker, points:[números... serie completa],
            xLabels:["2020","2022",...], endTag:"×3.4"|"+622%", sub, foot?}
            ⚠ target_word = palabra del VO donde aterriza el endTag.
- barras  : comparación horizontal estilo keynote (2-4 barras; protagonista esmeralda crece AL
            FINAL y su valor cuenta; referencias en azules). props {kicker,
            bars:[{label:"MAYÚS", value:número, display:"7.2%"}...], accentIndex, sub, foot?}
            ⚠ target_word = palabra del VO donde aterriza el valor del protagonista.
- carrera : carrera de barras entre periodos (valores deslizan continuo, 2.5s por periodo; el
            protagonista esmeralda). props {kicker, steps:[{period:"2020",values:{"BTC":n,...}}...
            (3-5 periodos, 4-6 nombres)], accentName, prefix:"$", suffix:" mil M", sub, foot?}
- cierre  : cierre corto que reconecta con el hook (mismo lenguaje kinético). props {kicker,
            words:[{t,accent?}...] (la frase citable, corta), tease:"el imperativo/CTA"}
"""

RULEBOOK = r"""
REGLAS DE DIRECCIÓN (docs/standards/DIRECTION_RULEBOOK.md — cítalas por beat):
- Cifra que impacta -> cifra (el odómetro aterriza CON la voz). Tendencia/crecimiento -> linea.
  A vs B (2-4 cosas hoy) -> barras (protagonista esmeralda, resto azules). Evolución de ranking en
  el tiempo -> carrera. El gancho y el cierre -> hook/cierre (kinético).
- Von Restorff: UN protagonista esmeralda por escena; todo lo demás reposa en hueso/azules.
  Peak-end: clímax al ~80% y cierre que reconecta con el hook (Zeigarnik: el loop se CIERRA ahí).
- Transiciones del mundo (sobrias): "cut" = continuidad · "dip" = respiro/cambio de capítulo
  (fade por negro). Campo trans del beat = transición HACIA el siguiente. Nada más existe.
- EL MOVIMIENTO NO SE DIRIGE: vive congelado en los masters. Tú NO puedes emitir duraciones,
  curvas ni efectos — solo elegir master, llenar datos y anclar target_word.
- TIMING legible: min_s por beat si el VO es corto (default 4.0s); el sistema sostiene solo.
"""

WRITING = r"""
REGLAS DE ESCRITURA es-MX (obligatorias, minadas y verificadas):
- HOOK = pérdida/impacto PERSONAL en 2ª persona con cifra o plazo concreto, ≤20 palabras. PROHIBIDO
  abrir con institución/fecha/contexto. Traduce sujeto institucional→persona ("Banxico subió su tasa"→
  "Tu tarjeta acaba de subir de precio"). Moldes: nadie-te-cuenta / te-cuesta-$X-al-mes /
  si-tienes-X-deja-de-hacer-scroll / el-dinero-real-está-en / estás-pagando-sin-darte-cuenta.
- PRESUPUESTO: 45-60s = 120-150 palabras TOTALES de VO. Hook ≤20 + promesa 10-15 + desarrollo 80-100
  en 2-3 beats + payoff 20-25. Máximo 3 ideas. Guarda UNA revelación para los últimos 10-15s.
- OPEN LOOPS cada 12-18 palabras ("Pero eso no es lo raro..." / "Y aquí viene la parte que te toca a
  ti." / "Guárdate ese número, porque ahorita regresa."). TODO loop se cierra dentro del video. Máx 1
  loop abierto simultáneo además del principal.
- CONECTORES solo de CONFLICTO ("pero", "el problema es") o CONSECUENCIA ("entonces", "por eso",
  "resultado:"). PROHIBIDO "y luego"/"además"/"y también" (>30% aditivos = lista, no historia).
- CIFRAS: el VISUAL muestra la cifra exacta (props); el VO dice la redondeada comparable ("alrededor
  de tres billones y medio"). En VO los números van CON PALABRAS. En el hook SIEMPRE cifra o plazo.
- ANALOGÍA FÍSICA obligatoria para toda cifra >1 millón, en UNA frase mexicana ("un Tren Maya completo,
  y sobra"). Máximo 2 por video.
- OÍDO + TTS: frases ≤15 palabras, sujeto-verbo-complemento. LISTA NEGRA: "cabe destacar", "en el
  marco de", "asimismo", voz pasiva, siglas sin explicar. LISTA BLANCA: "lana", "quincena", "te sale
  más caro", "ojo con esto". Marcado: "..." antes de cada revelación, "—" para giros, MAYÚS en solo
  UNA palabra de todo el guion. Test: si suena a noticiero de los 90, reescribe.
- REFRAME "No es X... es Y" como beat 2 o hook alterno, solo si la Y es demostrable con el dato.
- GATE DE CIERRE: ¿el cuerpo responde LITERAL lo que el hook promete? ¿loops cerrados? ¿revelación
  final en los últimos 15s? ¿el "entonces qué hago yo" en una frase imperativa? PROHIBIDO "sígueme
  para más", resúmenes y despedidas. La última frase debe poder citarse sola.

RETRO DEL FUNDADOR 2026-07-07 (obligatorias, costaron un rechazo):
- CERO REPETICIÓN: una cifra se DICE una sola vez en todo el reel. Si el hook la adelanta, el beat
  que la desarrolla aporta contexto/consecuencia NUEVA, jamás la re-enuncia ("ya me perdiste, se ve
  hecho con AI"). Hay un QC automático que rechaza el guion si repites un 5-grama.
- FUENTES DESCONOCIDAS fuera del VO: Nvidia/Apple/Banxico se dicen; Concanaco/Canaco/organismos
  gremiales NO se nombran en la voz (nadie los conoce) — se describen ("las cámaras de comercio
  estiman...") y la sigla vive solo en el foot de pantalla.
- ARCO DE LUZ: el reel ABRE oscuro pero NO se queda oscuro; el mundo se enriquece hacia el clímax.
  Escríbelo en la visión y elige heroes/beats que suban la luz (el fundador: "demasiado oscuro TODO
  el video" = rechazo).
- HERO CON INTENCIÓN DE CÁMARA: al describir un hero visual, pide un movimiento NARRATIVO (ej.
  establecer amplio → zoom dramático a los miles de fans), no un push-in genérico. La creatividad
  del encuadre es tu trabajo.
- SUJETOS RECONOCIBLES: si el tema tiene un objeto icónico (la Copa del Mundo, el Ángel), el hero
  muestra ESE objeto reconocible, no una versión genérica.
- ESTILO DE VOZ "D" (audición 07-07, elegido por el fundador): el VO se escribe CONVERSACIONAL, como
  si le contaras a un amigo — preguntas directas al viewer ("¿Sabes cuánto…?"), giros hablados ("Pero
  aquí viene lo bueno—"), repetición natural de énfasis ("Esa… esa es la historia"), contracciones
  mexicanas. PROHIBIDO el tono locutor/boletín. Los "…" y "—" son pausas reales del TTS: úsalos.
"""

SYSTEM = f"""Eres el DIRECTOR de un canal premium de finanzas/noticias LATAM (reels 9:16, look A:
negro profundo, tipografía bold, un acento de color, movimiento constante, minimalista serio).
Te dan una NOTICIA con hechos verificados y DISEÑAS el reel completo para el pipeline real.

{RULEBOOK}
{WRITING}

MENÚ CERRADO de beats (usa EXACTAMENTE estos tipos y estas props):{CATALOG}

Devuelve SOLO un JSON con el schema EXACTO de assemble_masters.py:
{{
 "topic": "...",
 "hook_text": "el gancho reescrito",
 "vision": "el ángulo en una línea",
 "beats": [
   {{"type":"hook","vo":"narración es-MX de este beat","props":{{...}},
     "target_word":"país","trans":"dip","technique":"regla del rulebook que aplicas"}},
   {{"type":"cifra","vo":"...la cifra dicha con palabras...","props":{{...}},
     "target_word":"billones","trans":"dip","technique":"..."}},
   ... 4 a 6 beats, arco: hook -> desarrollo (cifra/linea/barras/carrera) -> clímax (~80%) -> cierre ...
 ]
}}
Reglas duras:
- target_word OBLIGATORIO en cifra/linea/barras y en hook/cierre (la palabra accent): la palabra
  EXACTA del VO de ese beat donde aterriza (una palabra que el TTS pronuncia, sin signos).
- Todo kicker va en MAYÚSCULAS, 2-4 palabras ("EL DATO", "LA CARRERA").
- Datos SOLO del brief (exactos, con moneda explícita). NO inventes cifras ni series: si un master
  necesita puntos que el brief no tiene, elige otro master.
- El campo trans del ÚLTIMO beat se omite. La VO de todos los beats leída seguida = historia completa.
- No repitas el mismo master 2 veces seguidas; máximo 2 usos del mismo master por reel (hook/cierre
  cuentan aparte)."""


def direct(brief):
    facts = brief.get("facts", {})
    # VISIÓN CREATIVA del agente creativo (creative_director.py) — si existe, el
    # mecánico la EJECUTA: la creatividad ya está decidida desde el gusto del
    # fundador; aquí solo se llena el tratamiento técnico dentro del schema.
    creative_txt = ""
    cs = ROOT / "infra" / "assembler" / "out" / "_treatments" / "creative_spec.json"
    if cs.exists():
        creative_txt = (
            "\n\nVISIÓN CREATIVA (OBLIGATORIA — la diseñó el director creativo desde el "
            "TASTE LEDGER del fundador; tu trabajo es EJECUTARLA, no reinventarla):\n"
            + cs.read_text(encoding="utf-8")
            + "\n\nMapa de trans_intent→trans (menú aprobado hoy): continuidad→cut · "
              "capitulo→dip · energia→cut · firma→dip. Los heroes de la visión van como "
              "bgClip en el beat correspondiente (nombre de archivo lo asigna el pipeline; "
              "escribe props.bgClip = 'heroes/<slug_descriptivo>.mp4' según la escena).")
    user = (f"NOTICIA (titular): {brief.get('headline','')}\n\n"
            f"HECHOS VERIFICADOS (usa estos valores exactos):\n{json.dumps(facts, ensure_ascii=False, indent=2)}\n\n"
            f"POR QUÉ IMPORTA / ángulo LATAM: {brief.get('why_matters','')}"
            f"{creative_txt}\n\n"
            "Diseña el TRATAMIENTO del reel (JSON del schema exacto).")
    body = json.dumps({"model": MODEL, "max_tokens": 16000, "system": SYSTEM,
                       "messages": [{"role": "user", "content": user}]}).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST")
    req.add_header("x-api-key", load_key()); req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=240) as r:
        resp = json.loads(r.read())
    txt = "".join(b.get("text", "") for b in resp.get("content", []))
    out = ROOT / "infra" / "assembler" / "out" / "_treatments"
    out.mkdir(parents=True, exist_ok=True)
    (out / "_news_raw.txt").write_text(txt, encoding="utf-8")
    start = txt.find("{")
    obj, _ = json.JSONDecoder().raw_decode(txt[start:])
    return obj


VALID_TYPES = {"hook", "cifra", "linea", "barras", "carrera", "cierre"}
VALID_TRANS = {"cut", "dip"}
MOTION_FIELDS = {"land", "durF", "easing", "duration", "curve", "stagger", "speed"}


def validate(t):
    """Contrato v3 (masters): tipos del menú, target_word obligatorio, CERO motion en props."""
    errs = []
    beats = t.get("beats", [])
    if not beats:
        return ["sin beats"]
    if beats[0].get("type") != "hook":
        errs.append("el beat 1 debe ser hook")
    if beats[-1].get("type") != "cierre":
        errs.append("el último beat debe ser cierre")
    for i, b in enumerate(beats):
        ty = b.get("type")
        if ty not in VALID_TYPES:
            errs.append(f"b{i}: tipo '{ty}' fuera del menú")
        if b.get("trans") and b["trans"] not in VALID_TRANS:
            errs.append(f"b{i}: trans '{b['trans']}' inválida (solo cut|dip)")
        if ty in ("cifra", "linea", "barras") and not b.get("target_word"):
            errs.append(f"b{i} ({ty}): falta target_word")
        if not b.get("vo"):
            errs.append(f"b{i}: falta vo")
        # el director NO puede emitir motion — se valida por SCHEMA, no por prompt
        leaked = MOTION_FIELDS & set(b.get("props", {}).keys())
        if leaked:
            errs.append(f"b{i}: props de motion prohibidas {sorted(leaked)}")
    total_words = sum(len(b.get("vo", "").split()) for b in beats)
    if total_words > 175:
        errs.append(f"VO total {total_words} palabras (presupuesto ≤150+margen)")
    return errs


if __name__ == "__main__":
    # consola Windows cp1252: no morir por un carácter de adorno
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    brief = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
    t = direct(brief)
    errs = validate(t)
    if errs:
        print("⚠ contrato v2, reintento 1x:", "; ".join(errs))
        t = direct(brief)          # un reintento limpio
        errs = validate(t)
        if errs:
            raise SystemExit("tratamiento inválido: " + "; ".join(errs))
    out = ROOT / "infra" / "assembler" / "out" / "_treatments" / "news_treatment.json"
    out.write_text(json.dumps(t, ensure_ascii=False, indent=2), encoding="utf-8")
    print("═" * 70)
    print("HOOK:", t.get("hook_text"))
    print("VISIÓN:", t.get("vision"))
    print("─" * 70)
    for i, b in enumerate(t.get("beats", [])):
        tw = f"  land→'{b['target_word']}'" if b.get("target_word") else ""
        print(f"[b{i}] {b.get('type').upper():9s} trans:{b.get('trans','—'):5s}{tw}  ·  {b.get('technique','')}")
        print(f"     VO: {b.get('vo','')}")
    print("═" * 70)
    print(f"VO total: {sum(len(b.get('vo','').split()) for b in t.get('beats',[]))} palabras")
    print("guardado en", out, "\nsiguiente:  python assemble_masters.py", out, "<slug>")
