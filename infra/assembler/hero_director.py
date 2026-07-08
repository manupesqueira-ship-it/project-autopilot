# -*- coding: utf-8 -*-
"""hero_director.py — DIRECTOR DE HEROES (visión creativa → prompts i2v de calidad).

Toma las escenas con hero del creative_spec y escribe los prompts REALES:
seed (gpt-image, el still) + motion (Veo, el movimiento narrativo), con las
constantes del mundo horneadas y las lecciones minadas de prompting i2v.
Emite un plan ejecutable con tiers según la regla de Manuel (lite=borrador,
fast=versión de reel).

Uso:  python hero_director.py [creative_spec.json]  → out/_treatments/heroes_plan.json
"""
import json
import sys
from pathlib import Path

from agent_api import ROOT, ask_json

SYSTEM = """Eres el DIRECTOR DE HEROES: conviertes la visión de un director creativo en PROMPTS
ejecutables de generación (still + video) con calidad cinematográfica.

CONSTANTES DEL MUNDO (van horneadas en TODO seed): cinematic dark editorial photography, matte
black moody atmosphere, volumetric light, restrained palette of deep blacks and warm light,
no text, no logos, no people faces.

LECCIONES DE PROMPTING (minadas de nuestros clips validados):
- SEED (gpt-image): describe UNA composición fotográfica concreta (sujeto + encuadre + luz +
  atmósfera + profundidad de campo). Los seeds ricos en LUZ direccional salen mejor que los planos.
- MOTION (Veo i2v): describe el MOVIMIENTO como narración de cámara ("slow aerial rise revealing…",
  "camera descending through the haze toward…") + vida interna de la escena (partículas, luces
  titilando, tela moviéndose). SIEMPRE cerrar con "cinematic, dark atmosphere preserved".
- La cámara debe REVELAR algo (la regla del fundador: empezar amplio → zoom con propósito).
- El ARCO DE LUZ del creative_spec manda: escenas tempranas más oscuras, clímax más rico en luz.
- Personas: solo multitudes/siluetas lejanas, NUNCA caras cercanas.
- Sujetos icónicos reconocibles cuando el tema los pide (estadios reales, monumentos, La Copa).

Devuelve SOLO JSON:
{"heroes": [
  {"tag": "hero_<slug_corto>", "scene_n": N,
   "seed_prompt": "prompt gpt-image completo en inglés",
   "motion_prompt": "prompt Veo completo en inglés",
   "duration_s": 8,
   "why": "qué revela este hero en una línea"}
]}"""


def plan(spec: dict) -> dict:
    scenes = [s for s in spec.get("scenes", []) if s.get("hero")]
    user = (f"ARCO DE LUZ DEL REEL: {spec.get('light_arc', '')}\n\n"
            f"MOMENTO WOW: {spec.get('wow_moment', '')}\n\n"
            f"ESCENAS CON HERO:\n{json.dumps(scenes, ensure_ascii=False, indent=2)}")
    return ask_json(SYSTEM, user, temperature=0.9)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        ROOT / "infra" / "assembler" / "out" / "_treatments" / "creative_spec.json"
    spec = json.loads(src.read_text(encoding="utf-8-sig"))
    r = plan(spec)
    if not r.get("heroes"):
        raise SystemExit("hero_director no devolvió heroes")
    out = ROOT / "infra" / "assembler" / "out" / "_treatments" / "heroes_plan.json"
    out.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    for h in r["heroes"]:
        print(f"  {h['tag']} (escena {h['scene_n']}): {h['why']}")
    print(f"HEROES PLAN OK · {len(r['heroes'])} heroes → {out}")
