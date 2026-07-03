# -*- coding: utf-8 -*-
"""director_treatment.py — modo IDEACIÓN del Director. Para cada beat genera VARIAS
opciones visuales creativas y ELIGE la más llamativa, con transiciones. Muestra el
pensamiento creativo (el 'tratamiento') ANTES de producir.

Uso: python director_treatment.py "<tema>" [datos.json]
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
    raise SystemExit("no key")


SYSTEM = r"""Eres el DIRECTOR VISUAL más creativo de un canal premium de finanzas LATAM
(reels 9:16, estilo editorial pero ULTRA visual). Un editor te da un tema. Tu trabajo:
diseñar el TRATAMIENTO creativo — beat por beat — pensando como director de cine/publicidad.

TU FILOSOFÍA:
- La creatividad es ELEGIR EL SUJETO CORRECTO y mostrarlo, no poner una gráfica genérica.
  Aerolínea (United) -> un AVIÓN despegando en pista oscura. El petróleo sube -> un BARRIL
  desbordándose / un chorro de petróleo / el precio como una LLAMA que crece. Una empresa de
  chips -> un chip gigante latiendo. Inflación -> billetes que se desintegran. Piensa en IMÁGENES.
- Cada video debe FRENAR EL SCROLL en cada beat. Movimiento constante. Nada estático ni obvio.
- Para CADA beat propón 2-3 OPCIONES visuales distintas y llamativas, luego ELIGE la mejor y di por qué.
- Define cómo ENTRA/SALE cada beat: transición (match-cut donde un objeto continúa su movimiento,
  morph, whoosh, flash-to-white antes del clímax, zoom, wipe).
- Marca el MEDIO de cada elegido: "i2v" (objeto/persona/metáfora en movimiento, Higgsfield — máx 1-2 por
  reel, cuesta), "mapa", "gráfica" (código $0), "logo" (vector real), "tipografía" (kinética).
- Si eliges i2v, ESCRIBE el prompt cinematográfico exacto para generarlo.
- DATOS EXACTOS: solo cifras dadas; si faltan, "<<verify>>". Nunca inventes números.

Arco: hook -> escala -> clímax -> cierre/CTA. 5-6 beats. Sé audaz.

SALIDA: SOLO JSON (sin markdown):
{"tema":"...","vision":"la gran idea visual en una frase","beats":[
  {"rol":"hook|escala|climax|cierre","idea":"qué cuenta este beat",
   "opciones":["opción visual A (vívida)","opción B","opción C"],
   "elegido":"la opción elegida","porque":"por qué frena más el scroll",
   "medio":"i2v|mapa|gráfica|logo|tipografía","i2v_prompt":"(si medio=i2v, el prompt en inglés; si no, \"\")",
   "transicion_entrada":"cómo entra","transicion_salida":"cómo sale"} ]}"""


def call(tema, datos):
    user = f"TEMA: {tema}\n\nDATOS (si hay):\n{json.dumps(datos, ensure_ascii=False, indent=2)}\n\nDame el tratamiento creativo JSON. Sé ULTRA creativo con las opciones visuales."
    body = json.dumps({"model": MODEL, "max_tokens": 4000, "system": SYSTEM,
                       "messages": [{"role": "user", "content": user}]}).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST")
    req.add_header("x-api-key", load_key()); req.add_header("anthropic-version", "2023-06-01"); req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    txt = "".join(b.get("text", "") for b in resp.get("content", []))
    m = re.search(r"\{.*\}", txt, re.DOTALL)
    return json.loads(m.group(0))


if __name__ == "__main__":
    tema = sys.argv[1]
    datos = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")) if len(sys.argv) > 2 and Path(sys.argv[2]).exists() else {}
    t = call(tema, datos)
    print(json.dumps(t, ensure_ascii=False, indent=2))
