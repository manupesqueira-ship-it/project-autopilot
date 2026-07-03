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


# MENÚ CERRADO v2 = NewsReel MAP (beats2/NewsBeats2 + beats2/ChartBeats2). Props EXACTAS.
CATALOG = r"""
- hook     : titular kinético palabra-por-palabra. props {kicker, words:[{t,accent?:true}...], tease}
             (words = el hook partido en palabras; accent SOLO en la palabra clave)
- reveal   : revela el sujeto (empresa/activo), tipográfico gigante con glow.
             props {name, tagline, color:"#hex de la marca"}
- shock    : CIFRA HÉROE con odómetro + punch en la sílaba. props {value:"$3.5 billones" (string
             YA formateado, unidad inline), kicker, caption, valence:"gain"|"loss"|"gold"}
             ⚠ OBLIGATORIO target_word = la palabra del VO donde aterriza la cifra.
- scale    : zoom-OUT de escala (chico gris vs gigante oro, focus+context).
             props {smallLabel, smallValue, bigLabel, bigValue}
- trend    : línea SVG con glow y cabeza viva (tendencia simple). props {kicker, label,
             points:[números...], caption, endTag:"+35%"}
- bars     : comparación de barras ECharts, UN acento en el sujeto. props {kicker, label,
             cats:["A","B","C"], values:[n,n,n], accentIndex, valence, prefix:"$", suffix:" mil M", caption}
- trendpro : línea héroe ECharts con área y UMBRAL semántico (rojo debajo / verde arriba —
             precio de compra, meta, break-even). props {kicker, label, points:[...],
             xLabels:["2020"...], threshold:número, valence, endTag, caption}
- lines    : hasta 3 series con nombre+valor al final + línea de meta punteada (carrera entre
             países/activos). props {kicker, label, series:[{name,data:[...]},...(máx 3, [0]=protagonista)],
             xLabels, threshold?, thresholdLabel?:"meta Banxico 3%", valence, suffix:"%", caption}
- gauge    : UN porcentaje protagonista en arco fino. props {kicker, label, value:68, suffix:"%",
             valence, caption}   ⚠ target_word = palabra donde aterriza el número.
- donut    : proporción ultrafina con cifra central. props {kicker, label,
             parts:[{name,value}...([0]=protagonista)], centerValue:"42%", centerLabel, valence, caption}
             ⚠ target_word recomendado.
- race     : carrera de barras entre periodos (quién sube/quién cae). props {kicker, label,
             steps:[{period:"2020",values:{"A":n,"B":n,...}},...], accentName, prefix, suffix, caption}
- close    : cierre corto que reconecta con el hook. props {line1, punch, cta}
"""

RULEBOOK = r"""
REGLAS DE DIRECCIÓN (docs/standards/DIRECTION_RULEBOOK.md — cítalas por beat):
- Cifra shock -> shock (odómetro + punch + color en el aterrizaje del VO). Magnitud a dimensionar ->
  scale (zoom-out focus+context). A vs B -> bars (sujeto en color, resto gris = Von Restorff).
  Tendencia c/historia de pérdida->ganancia -> trendpro con threshold. Carrera entre 2-3 -> lines o race.
  UN porcentaje que duele -> gauge. Proporción del todo -> donut. Figura pública -> NO hay beat aún en
  este menú: usa reveal con su nombre (NUNCA cara generada por IA).
- Von Restorff: UN solo acento de color por cuadro. Peak-end: clímax al ~80% y cierre que reconecta
  con el hook (Zeigarnik: el loop del hook se CIERRA ahí).
- zoom-IN=urgencia/detalle · zoom-OUT=revelación de contexto · whip=contraste o cambio de sujeto ·
  dip=respiro antes del clímax · cut=continuidad. Campo trans del beat = transición HACIA el siguiente:
  "cut"|"zoom"|"whip"|"whipL"|"dip". Similares->suave (cut/zoom), contraste->whip, antes del clímax->dip.
- TIMING legible: revelar temprano y SOSTENER. min_s por beat si el VO es corto (default 3.2s).
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
"""

SYSTEM = f"""Eres el DIRECTOR de un canal premium de finanzas/noticias LATAM (reels 9:16, look A:
negro profundo, tipografía bold, un acento de color, movimiento constante, minimalista serio).
Te dan una NOTICIA con hechos verificados y DISEÑAS el reel completo para el pipeline real.

{RULEBOOK}
{WRITING}

MENÚ CERRADO de beats (usa EXACTAMENTE estos tipos y estas props):{CATALOG}

Devuelve SOLO un JSON con el schema EXACTO de assemble_news.py:
{{
 "topic": "...",
 "hook_text": "el gancho reescrito",
 "vision": "el ángulo en una línea",
 "beats": [
   {{"type":"hook","vo":"narración es-MX de este beat","props":{{...}},
     "trans":"zoom","technique":"regla del rulebook que aplicas"}},
   {{"type":"shock","vo":"...la cifra dicha con palabras...","props":{{...}},
     "target_word":"billones","trans":"dip","technique":"..."}},
   ... 5 a 7 beats, arco: hook -> reveal/desarrollo -> clímax (~80%) -> close ...
 ]
}}
Reglas duras:
- target_word OBLIGATORIO en shock/gauge (y recomendado en donut): la palabra EXACTA del VO de ese
  beat donde la cifra debe aterrizar (una palabra que el TTS pronuncia, sin signos).
- Datos SOLO del brief (exactos, con moneda explícita). NO inventes cifras ni series: si una gráfica
  necesita puntos que el brief no tiene, elige otro beat.
- El campo trans del ÚLTIMO beat se omite. La VO de todos los beats leída seguida = historia completa.
- Varía el menú: no repitas el mismo tipo de gráfica 2 veces en un reel."""


def direct(brief):
    facts = brief.get("facts", {})
    user = (f"NOTICIA (titular): {brief.get('headline','')}\n\n"
            f"HECHOS VERIFICADOS (usa estos valores exactos):\n{json.dumps(facts, ensure_ascii=False, indent=2)}\n\n"
            f"POR QUÉ IMPORTA / ángulo LATAM: {brief.get('why_matters','')}\n\n"
            "Diseña el TRATAMIENTO del reel (JSON). Sé ultra creativo en el hook y en la elección "
            "de beat + transición por relación narrativa.")
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


VALID_TYPES = {"hook", "reveal", "shock", "scale", "trend", "close",
               "bars", "trendpro", "lines", "gauge", "donut", "race"}
VALID_TRANS = {"cut", "zoom", "whip", "whipL", "dip"}


def validate(t):
    """Contrato v2: tipos del menú, target_word donde es obligatorio, arco hook->close."""
    errs = []
    beats = t.get("beats", [])
    if not beats:
        return ["sin beats"]
    if beats[0].get("type") != "hook":
        errs.append("el beat 1 debe ser hook")
    if beats[-1].get("type") != "close":
        errs.append("el último beat debe ser close")
    for i, b in enumerate(beats):
        ty = b.get("type")
        if ty not in VALID_TYPES:
            errs.append(f"b{i}: tipo '{ty}' fuera del menú")
        if b.get("trans") and b["trans"] not in VALID_TRANS:
            errs.append(f"b{i}: trans '{b['trans']}' inválida")
        if ty in ("shock", "gauge") and not b.get("target_word"):
            errs.append(f"b{i} ({ty}): falta target_word")
        if not b.get("vo"):
            errs.append(f"b{i}: falta vo")
    total_words = sum(len(b.get("vo", "").split()) for b in beats)
    if total_words > 175:
        errs.append(f"VO total {total_words} palabras (presupuesto ≤150+margen)")
    return errs


if __name__ == "__main__":
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
    print("guardado en", out, "\nsiguiente:  python assemble_news.py", out, "<slug>")
