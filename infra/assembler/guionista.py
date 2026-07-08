# -*- coding: utf-8 -*-
"""guionista.py — AGENTE DE ESCRITURA (aprobado por Manuel 2026-07-08).

Recibe el tratamiento del director mecánico y reescribe SOLO los "vo" al estilo
D (elegido por Manuel en la audición: conversacional, pregunta directa, giros
hablados, énfasis con repetición natural). Mantiene los DATOS intactos y emite
target_word coherente con el texto nuevo. Puede recibir la crítica del
critico_guion para una segunda pasada.

Uso:  python guionista.py <treatment.json> <brief.json> [critica.json]
      → sobreescribe el treatment con los VO pulidos
"""
import json
import sys
from pathlib import Path

from agent_api import ask_json

SYSTEM = """Eres el GUIONISTA de un canal de noticias financieras LATAM (reels de ~60s, es-MX).
Recibes un tratamiento con el VO de cada beat ya redactado por otro agente. Tu ÚNICO trabajo:
reescribir cada "vo" para que suene a UNA PERSONA REAL contándole algo jugoso a un amigo — jamás
a locutor, jamás a boletín, jamás a AI.

ESTILO D (elegido por el fundador — obligatorio):
- Pregunta directa al viewer cuando abre ("¿Sabes cuánto…?").
- Giros hablados: "Pero aquí viene lo bueno—", "Y ojo…", "el detalle está en…".
- Énfasis con repetición natural: "Esa… esa es la historia."
- Frases ≤15 palabras, sujeto-verbo-complemento. Contracciones mexicanas naturales.
- "…" y "—" son pausas REALES del TTS: úsalos para respirar y para revelar.
- MAYÚSCULAS solo en UNA palabra de todo el guion (el énfasis nuclear).

REGLAS DURAS (violarlas = rechazo):
- Los DATOS no se tocan: mismas cifras, mismas fuentes, mismos hechos. Números EN PALABRAS en el VO.
- Una cifra se dice UNA sola vez en todo el reel (hay QC automático de 5-gramas repetidos).
- Nada de "cabe destacar", "en el marco de", "asimismo", voz pasiva, siglas sin explicar.
- Organismos desconocidos (cámaras/gremios) NO se nombran en el VO — descríbelos.
- Presupuesto total: 120-150 palabras. La última frase debe poder citarse sola.
- Por beat emite "target_word": la palabra EXACTA de tu texto nuevo donde debe aterrizar el visual
  (una palabra que el TTS pronuncia, sin signos; para cifras = la palabra clave del número).

Devuelve SOLO JSON: {"beats": [{"n": 0, "vo": "...", "target_word": "..."}, ...]} — un objeto por
beat, en el MISMO orden que recibiste."""


def polish(treatment: dict, brief: dict, critica: dict | None = None) -> dict:
    user = (f"TRATAMIENTO ACTUAL (beats con vo a reescribir):\n"
            f"{json.dumps([{'n': i, 'type': b['type'], 'vo': b['vo'], 'target_word': b.get('target_word')} for i, b in enumerate(treatment['beats'])], ensure_ascii=False, indent=2)}\n\n"
            f"HECHOS DEL BRIEF (los datos NO se tocan):\n"
            f"{json.dumps(brief.get('facts', {}), ensure_ascii=False, indent=2)}")
    if critica:
        user += ("\n\nCRÍTICA DEL SCRIPT DOCTOR (corrige TODO esto en tu reescritura):\n"
                 + json.dumps(critica, ensure_ascii=False, indent=2))
    out = ask_json(SYSTEM, user, temperature=1.0)
    by_n = {b["n"]: b for b in out.get("beats", [])}
    for i, b in enumerate(treatment["beats"]):
        nb = by_n.get(i)
        if not nb or not nb.get("vo"):
            raise SystemExit(f"guionista no devolvió el beat {i}")
        b["vo"] = nb["vo"]
        if nb.get("target_word"):
            b["target_word"] = nb["target_word"]
    return treatment


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tpath = Path(sys.argv[1])
    treatment = json.loads(tpath.read_text(encoding="utf-8-sig"))
    brief = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8-sig"))
    critica = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8-sig")) if len(sys.argv) > 3 else None
    treatment = polish(treatment, brief, critica)
    tpath.write_text(json.dumps(treatment, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(b["vo"].split()) for b in treatment["beats"])
    print(f"GUIONISTA OK · {total} palabras de VO · {tpath}")
