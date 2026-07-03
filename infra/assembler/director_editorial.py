# -*- coding: utf-8 -*-
"""director_editorial.py — el DIRECTOR (agente Claude) del sistema editorial.

Lee un TEMA + DATOS VERIFICADOS y emite un reel_def (elige escenas del MENÚ +
redacta el guion/VO + define el arco). La creatividad = elección inteligente +
redacción, NO inventar arte de cero ni cifras.

Salida: un dict compatible con reels_defs / build_reels.build().

Uso:
    python director_editorial.py brief.json            # brief con tema + datos
    python director_editorial.py brief.json --build     # además construye el reel
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
MODEL = "claude-sonnet-5"


def load_key():
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("ANTHROPIC_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("no ANTHROPIC_API_KEY")


SYSTEM = r"""Eres el DIRECTOR VISUAL de "Dinero IA": reels verticales 9:16 de finanzas
personales LATAM en español, estilo EDITORIAL premium (papel hueso, tinta, un acento
oxblood, tipografía fuerte). Tu trabajo: convertir TEMA + DATOS VERIFICADOS en un reel
completo, eligiendo escenas del MENÚ CERRADO y ESCRIBIENDO el guion (VO). La creatividad
es ELEGIR la escena correcta para cada hecho y CÓMO decirlo.

REGLAS NO NEGOCIABLES:
- DATOS EXACTOS: usa SOLO cifras de los datos dados. Si falta una, escribe "<<verify>>". NUNCA inventes números.
- La VO redondea en palabras ("alrededor de doscientos millones"); el VISUAL muestra la cifra exacta.
- Moneda SIEMPRE explícita (USD o MXN).
- MOVIMIENTO CONSTANTE: cada escena del menú ya se mueve; tú eliges bien y no repites el mismo tipo dos veces seguidas.
- Color semántico lo maneja cada escena (verde=sube, rojo=pérdida, oxblood=acento).
- Arco: hook -> escala de datos distintos -> cifra clímax -> cierre con CTA. 4 a 6 escenas.
- La PRIMERA escena es "cover" (hook). La ÚLTIMA es "close" (CTA). Al menos una escena de dato dinámico.
- Elige con criterio: si el tema es un PAÍS/geografía -> usa "mapzoom". Una CAÍDA de valor -> "fallchart".
  Un A vs B -> "compare". Una cifra titular/clímax -> "bignum" o "payoff". No fuerces escenas.

MENÚ DE ESCENAS (usa exactamente estos tipos y campos):
1. cover:    {"type":"cover","kicker":"TEXTO CORTO MAYUS","lines":[{"text":"máx ~12 chars"},{"text":"..."},{"text":"...","accent":true}],"foot":"frase de apoyo"}
2. mapzoom:  {"type":"mapzoom","countryName":"NombreEN(inglés, ej 'El Salvador','Mexico','Argentina')","iso2":"SV","label":"NOMBRE EN MAYÚS","region":["vecinos en inglés"],"kicker":"opcional"}
3. bignum:   {"type":"bignum","label":"contexto","prefix":"$","value":123456,"suffix":"opcional ej 'M USD'","sublabel":"opcional","accent":false}
4. fallchart:{"type":"fallchart","kicker":"opcional","fromLabel":"antes","from":100000,"toLabel":"después","to":96209,"delta":3791,"prefix":"$","axisRight":"−X% · N MESES","note":"opcional"}
5. compare:  {"type":"compare","kicker":"opcional","left":{"tag":"corto","value":45000},"right":{"tag":"corto","value":61900},"prefix":"$","winner":"right","note":"opcional"}
6. payoff:   {"type":"payoff","kicker":"MAYÚS","prefix":"$","value":6033,"suffix":"opcional","deltaText":"frase corta","body":"opcional"}
7. close:    {"type":"close","headline":[{"text":"corto"},{"text":"corto"},{"text":"corto","accent":true}],"sub":"disclaimer/loop","cta":"Guarda esto"}

(NO uses i2v/placa: eso se agrega aparte a mano cuando hace falta un objeto/persona.)

SALIDA: SOLO un JSON válido (sin markdown, sin explicación) con esta forma exacta:
{"slug":"snake_case","edition":"INFORME · TEMA AÑO","source":"Fuente: ... · corte ...","beats":[
  {"id":"b1","vo":"...","scene":{...}}, ... ]}
Los value son NÚMEROS (sin comas ni $). Escribe la VO natural, con gancho, en español LATAM."""


def call_claude(brief: dict) -> dict:
    user = ("TEMA: " + brief.get("tema", "") + "\n\nDATOS VERIFICADOS (con fuente/fecha):\n"
            + json.dumps(brief.get("datos", {}), ensure_ascii=False, indent=2)
            + "\n\nFuente para el pie: " + brief.get("fuente", "") + "\n\nDame el reel_def JSON.")
    body = json.dumps({
        "model": MODEL, "max_tokens": 3000, "system": SYSTEM,
        "messages": [{"role": "user", "content": user}],
    }).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST")
    req.add_header("x-api-key", load_key())
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    txt = "".join(b.get("text", "") for b in resp.get("content", []))
    m = re.search(r"\{.*\}", txt, re.DOTALL)
    if not m:
        raise SystemExit("el director no devolvió JSON:\n" + txt[:500])
    return json.loads(m.group(0))


VALID = {"cover", "mapzoom", "bignum", "fallchart", "compare", "payoff", "close", "plate"}


def validate(rd: dict):
    errs = []
    for k in ("slug", "edition", "source", "beats"):
        if k not in rd:
            errs.append(f"falta '{k}'")
    beats = rd.get("beats", [])
    if not beats or beats[0]["scene"]["type"] != "cover":
        errs.append("la 1a escena debe ser cover")
    if beats and beats[-1]["scene"]["type"] != "close":
        errs.append("la última escena debe ser close")
    for i, b in enumerate(beats):
        t = b.get("scene", {}).get("type")
        if t not in VALID:
            errs.append(f"beat {i}: tipo inválido '{t}'")
        if not b.get("vo"):
            errs.append(f"beat {i}: sin vo")
    return errs


if __name__ == "__main__":
    brief_path = Path(sys.argv[1])
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    rd = call_claude(brief)
    errs = validate(rd)
    if errs:
        print("[director] reintento por errores:", errs)
        rd = call_claude({**brief, "correccion": "Corrige: " + "; ".join(errs)})
        errs = validate(rd)
    out = ROOT / "infra" / "assembler" / "out" / "_editorial_reels" / rd["slug"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "reel_def.json").write_text(json.dumps(rd, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SLUG:", rd["slug"], "| escenas:", [b["scene"]["type"] for b in rd["beats"]], "| errs:", errs)
    print("Guardado:", out / "reel_def.json")
    if "--build" in sys.argv:
        sys.path.insert(0, str(ROOT / "infra" / "assembler"))
        from build_reels import build
        build(rd)
