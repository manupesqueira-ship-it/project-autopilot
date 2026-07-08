# -*- coding: utf-8 -*-
"""
creative_director.py — EL AGENTE DE CREATIVIDAD (pedido de Manuel 2026-07-07:
"hay que crear un agente y conectarlo a una API para que te diga creativamente
qué crear en cada escena. No debe ser muy caro").

QUÉ HACE: entre el brief verificado y el director mecánico, este agente piensa
SOLO la CREATIVIDAD: el ángulo visual del reel, la metáfora/hero de cada escena
(con cámara narrativa y luz), el momento wow, el arco de luz. NO toca datos ni
motion — eso lo blindan el QC y el schema del director mecánico.

POR QUÉ FUNCIONA (garantía de calidad): no inventa en el vacío — piensa DESDE
docs/standards/TASTE_LEDGER.md (todo lo que Manuel aprobó/rechazó, actualizado
tras cada gate). La creatividad MEJORA con cada retro porque el ledger crece.

COSTO: 1 llamada claude-sonnet-5 (~$0.05 USD/reel).

Uso:  python creative_director.py <brief.json>   → out/_treatments/creative_spec.json
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
MODEL = "claude-sonnet-5"


def load_key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no ANTHROPIC key")


def load_taste() -> str:
    p = ROOT / "docs" / "standards" / "TASTE_LEDGER.md"
    return p.read_text(encoding="utf-8")


SYSTEM_TMPL = """Eres el DIRECTOR CREATIVO de un canal premium de noticias financieras LATAM
(reels 9:16). Tu ÚNICO trabajo es la CREATIVIDAD: qué se VE en cada escena para que un viewer
que hace scroll se detenga, sienta y entienda. Otro agente (el director mecánico) convertirá tu
visión en el tratamiento técnico — tú NO escribes VO final, ni datos, ni parámetros de motion.

TU GUSTO NO ES EL TUYO — ES EL DEL FUNDADOR. Este es su ledger completo (aprobaciones, rechazos
y principios; violarlo = rechazo seguro):

{taste}

REGLAS DE TU OUTPUT:
- Por CADA escena propones: la IDEA visual (metáfora/símbolo, no descripción plana), el HERO si
  aplica (sujeto + movimiento de cámara NARRATIVO + luz/mood + qué revela el movimiento), o el
  TIPO de gráfica y qué la hace memorable (logos reales, crecimiento dramático, escala brutal).
- Piensas el ARCO DE LUZ del reel completo (dónde abre oscuro, dónde se enriquece, el pico).
- Nombras EL MOMENTO WOW del reel (uno solo, específico) y por qué frena el scroll.
- intent de transición por escena: continuidad | capitulo | energia | firma (el mecánico mapea).
- 4-6 escenas. Sé ESPECÍFICO y visual ("la multitud como marea de luces que la cámara descubre al
  elevarse sobre el Ángel"), nunca genérico ("un video del tema").
- El barrido de ideas: da 2 CONCEPTOS de reel distintos primero, elige el mejor y justifica en una
  línea (el descartado queda registrado).

Devuelve SOLO JSON:
{{
 "concepts_considered": [{{"name": "...", "premise": "..."}}, {{"name": "...", "premise": "..."}}],
 "chosen": "nombre del elegido + por qué en una línea",
 "wow_moment": "escena N: descripción específica",
 "light_arc": "cómo evoluciona la luz del reel",
 "scenes": [
   {{"n": 1, "role": "hook|desarrollo|climax|cierre",
     "idea": "la metáfora/idea visual específica",
     "hero": {{"subject": "...", "camera": "movimiento narrativo y qué revela", "light": "..."}} | null,
     "chart": {{"kind": "cifra|linea|barras|carrera|leaderboard", "twist": "qué la hace memorable"}} | null,
     "text_breathing": "cuándo respira el hero sin texto encima",
     "trans_intent": "continuidad|capitulo|energia|firma"}}
 ]
}}"""


def create(brief: dict) -> dict:
    system = SYSTEM_TMPL.format(taste=load_taste())
    user = (f"NOTICIA: {brief.get('headline', '')}\n\n"
            f"HECHOS VERIFICADOS:\n{json.dumps(brief.get('facts', {}), ensure_ascii=False, indent=2)}\n\n"
            f"POR QUÉ IMPORTA: {brief.get('why_matters', '')}\n\n"
            "Diseña la CREATIVIDAD del reel (JSON del schema).")
    body = json.dumps({"model": MODEL, "max_tokens": 8000, "temperature": 1,
                       "system": system,
                       "messages": [{"role": "user", "content": user}]}).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST")
    req.add_header("x-api-key", load_key())
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=240) as r:
        resp = json.loads(r.read())
    txt = "".join(b.get("text", "") for b in resp.get("content", []))
    out = ROOT / "infra" / "assembler" / "out" / "_treatments"
    out.mkdir(parents=True, exist_ok=True)
    (out / "_creative_raw.txt").write_text(txt, encoding="utf-8")
    obj, _ = json.JSONDecoder().raw_decode(txt[txt.find("{"):])
    return obj


def validate(spec: dict) -> list[str]:
    errs = []
    scenes = spec.get("scenes", [])
    if not (4 <= len(scenes) <= 6):
        errs.append(f"{len(scenes)} escenas (deben ser 4-6)")
    if not spec.get("wow_moment"):
        errs.append("falta wow_moment")
    if not spec.get("light_arc"):
        errs.append("falta light_arc")
    heroes = sum(1 for s in scenes if s.get("hero"))
    if heroes == 0:
        errs.append("cero heroes (alternancia mundo↔dato exige al menos 1-2)")
    for s in scenes:
        if not s.get("idea"):
            errs.append(f"escena {s.get('n')}: sin idea")
        if s.get("trans_intent") not in ("continuidad", "capitulo", "energia", "firma", None):
            errs.append(f"escena {s.get('n')}: trans_intent inválido")
    return errs


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    brief = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
    spec = create(brief)
    errs = validate(spec)
    if errs:
        print("CREATIVE INVALID:", "; ".join(errs))
        raise SystemExit(1)
    dst = ROOT / "infra" / "assembler" / "out" / "_treatments" / "creative_spec.json"
    dst.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"CREATIVE OK · {len(spec['scenes'])} escenas · wow: {spec['wow_moment'][:70]}…")
    print(f"→ {dst}")
