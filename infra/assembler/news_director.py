"""news_director.py — AGENTE DIRECTOR de noticias -> reel 9:16.

Toma una NOTICIA (titular + hechos/datos verificados) y DISEÑA el reel:
reescribe la noticia en un HOOK que frena el scroll, arma la historia beat por beat,
elige el tipo de escena y la TÉCNICA (zoom/color/transición) según el DIRECTION_RULEBOOK,
y escribe la narración (VO) natural es-MX. Devuelve un TRATAMIENTO en JSON.

Uso: python news_director.py brief.json   (brief = {"headline","facts":{clave:{value,unit}},"why_matters"})
El humano revisa el tratamiento; el render lo implementa desde el catálogo CERRADO de beats reales.
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


# catálogo CERRADO de beats que el motor sabe renderizar (props exactas)
CATALOG = r"""
- hook      : gancho que frena el scroll. props {kicker, question, tease}  (curiosity gap: nombra que existe un resultado y NO lo reveles)
- reveal    : revela el sujeto (empresa/activo). props {name, tagline, logo?}  (logo = vector real, NUNCA IA)
- shocknumber: cifra héroe con count-up + punch-in + color. props {target(number), prefix, suffix, decimals, valence:"loss"|"gain", kicker, caption}
- scalereveal: zoom-OUT de escala (algo se ve enorme -> queda diminuto junto a algo gigante). props {smallLabel, smallValue, bigLabel, bigValue}
- comparebars: dos barras. props {title, a:{label,display,value,sub?,color:"green"|"red"|"gray"}, b:{...}}
- trendline : línea que sube/baja en el tiempo (bolsa, inflación). props {kicker, label, points:[num...], caption, up:bool}
- photohero : figura pública REAL. props {who, headline, sub}   (motor: foto DOMINIO PÚBLICO + Ken Burns; NUNCA generar su cara con IA)
- close     : cierre/CTA con loop. props {line1, punch, cta}
"""

RULEBOOK = r"""
REGLAS DE DIRECCIÓN (cítalas):
- HOOK (0-2s): abre con el RESULTADO/impacto, no el setup. Curiosity gap: nombra que existe algo asombroso y tápalo hasta el clímax. Especifica cifra+moneda.
- Cifra shock -> shocknumber (punch-in + vira a rojo=pérdida/verde=ganancia). Magnitud enorme a dimensionar -> scalereveal (zoom-out focus+context). Comparar A vs B -> comparebars (ganador en color, resto gris). Tendencia en el tiempo -> trendline. Figura pública real -> photohero (foto PD, jamás IA).
- Von Restorff: un solo acento de color por cuadro. Peak-end: pon el clímax al ~80% y cierra reconectando con el hook (loop).
- Zeigarnik: abre un loop en el hook y ciérralo al final. Aversión a la pérdida: framing en 2a persona ("TU").
- Datos SIEMPRE exactos del brief. Moneda explícita. VO redondea ("más de 3 billones"); el visual muestra la cifra.
- TIMING: cada beat debe poder LEERSE (revelar temprano, sostener). VO natural, conversacional, es-MX, frases cortas.
"""

SYSTEM = f"""Eres el DIRECTOR de un canal premium de finanzas/noticias LATAM (reels verticales 9:16, look
editorial oscuro, movimiento constante, minimalista). Te dan una NOTICIA con hechos verificados y
DISEÑAS el reel: reescribes la noticia en un HOOK potente, armas la historia, y para CADA beat eliges
un tipo del CATÁLOGO CERRADO + la TÉCNICA del rulebook + escribes la narración (VO).

{RULEBOOK}

CATÁLOGO CERRADO de beats (usa EXACTAMENTE estos tipos y props):{CATALOG}

Devuelve SOLO un JSON:
{{
 "topic": "...",
 "hook_text": "el gancho reescrito (una frase que frena el scroll)",
 "vision": "en una línea, el ángulo/porqué importa",
 "beats": [
   {{"id":"b1","type":"hook","vo":"narración es-MX de este beat","props":{{...}},"technique":"regla del rulebook que aplicas","why":"por qué aquí"}},
   ... 6 a 8 beats, arco completo: hook -> reveal -> desarrollo (shock/scale/compare/trend) -> clímax -> cierre ...
 ]
}}
Reglas: 6-8 beats. La VO de todos los beats, leída seguida, debe contar la historia completa y fluida.
Empieza fuerte, cierra con loop al hook. Usa los datos exactos del brief en las props."""


def direct(brief):
    facts = brief.get("facts", {})
    user = (f"NOTICIA (titular): {brief.get('headline','')}\n\n"
            f"HECHOS VERIFICADOS (usa estos valores exactos):\n{json.dumps(facts, ensure_ascii=False, indent=2)}\n\n"
            f"POR QUÉ IMPORTA / ángulo LATAM: {brief.get('why_matters','')}\n\n"
            "Diseña el TRATAMIENTO del reel (JSON). Sé ultra creativo en el hook y en la elección de técnica por beat.")
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


if __name__ == "__main__":
    brief = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    t = direct(brief)
    out = ROOT / "infra" / "assembler" / "out" / "_treatments" / "news_treatment.json"
    out.write_text(json.dumps(t, ensure_ascii=False, indent=2), encoding="utf-8")
    print("═" * 70)
    print("HOOK:", t.get("hook_text"))
    print("VISIÓN:", t.get("vision"))
    print("─" * 70)
    for b in t.get("beats", []):
        print(f"[{b.get('id')}] {b.get('type').upper()}  ·  técnica: {b.get('technique','')}")
        print(f"   VO: {b.get('vo','')}")
        print(f"   props: {json.dumps(b.get('props',{}), ensure_ascii=False)}")
    print("═" * 70, "\nguardado en", out)
