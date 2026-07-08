# -*- coding: utf-8 -*-
"""editor_jefe.py — EL EDITOR EN JEFE (qué enseñar y cuándo).

Recibe las candidatas del scout + el historial de temas publicados/producidos
y decide: cuál noticia gana HOY, con qué ángulo, y en qué ventana publicar.
Mantiene la VARIEDAD del canal (no repetir tema/universo/master dominante) y
mata lo tibio (mejor no publicar que publicar relleno).

Uso:  python editor_jefe.py <candidatas.json>   → out/_treatments/decision_editorial.json
      (candidatas.json = lista de candidatas del scout, formato libre)
"""
import json
import sys
from datetime import date
from pathlib import Path

from agent_api import ROOT, ask_json

HISTORY = ROOT / "infra" / "assembler" / "out" / "_treatments" / "topics_history.json"

SYSTEM = """Eres el EDITOR EN JEFE de un canal de reels financieros LATAM (@dinerolatam). Decides
QUÉ se produce hoy y CUÁNDO se publica. Tu criterio:

1. FRESCURA dura: la noticia vive 24-72h. Un tema cuyo pico ya pasó = muerto (ej.: un partido de
   hace 3 días ya no es noticia aunque tenga ángulo nuevo).
2. VARIEDAD del canal: mira el historial — no repetir universo temático de los últimos 3-4 reels
   (si hubo 2 de Mundial, el tercero NO es Mundial aunque sea buena nota).
3. SCROLL-STOP: ¿la nota tiene UN dato que obliga a parar el pulgar + UN hero visual filmable?
4. RELEVANCIA cartera: ¿le toca el dinero al viewer mexicano/LATAM o al menos lo asombra en grande?
5. Mejor NO producir que producir tibio: si ninguna candidata pasa 3 y 4, dilo.

VENTANA de publicación (IG MX): mañana 7-9am (commute) · mediodía 12-14h · noche 19-21h (pico).
Elige según la naturaleza de la nota (mercados=mañana; consumo/cultura=noche).

Devuelve SOLO JSON:
{"decision": "producir"|"no_producir",
 "elegida": "titular de la candidata elegida (o null)",
 "por_que": "una línea",
 "angulo": "el ángulo específico que la hace NUESTRA (financiero, no genérico)",
 "publicar": "hoy 19-21h" | "...",
 "descartadas": [{"titular": "...", "razon": "..."}]}"""


def decide(candidatas: list) -> dict:
    hist = []
    if HISTORY.exists():
        hist = json.loads(HISTORY.read_text(encoding="utf-8"))
    user = (f"HOY: {date.today().isoformat()}\n\n"
            f"HISTORIAL RECIENTE del canal (producido/publicado):\n"
            f"{json.dumps(hist[-8:], ensure_ascii=False, indent=2)}\n\n"
            f"CANDIDATAS DEL SCOUT:\n{json.dumps(candidatas, ensure_ascii=False, indent=2)}")
    return ask_json(SYSTEM, user, temperature=0.6)


def log_topic(topic: str, universe: str):
    hist = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
    hist.append({"date": date.today().isoformat(), "topic": topic, "universe": universe})
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cands = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
    r = decide(cands if isinstance(cands, list) else cands.get("candidates", []))
    out = ROOT / "infra" / "assembler" / "out" / "_treatments" / "decision_editorial.json"
    out.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"EDITOR · {r.get('decision')} · {r.get('elegida')}")
    print(f"  ángulo: {r.get('angulo')}")
    print(f"  publicar: {r.get('publicar')}")
