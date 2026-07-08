# -*- coding: utf-8 -*-
"""critico_guion.py — SCRIPT DOCTOR (el viewer escéptico).

Lee el guion completo como un viewer de 24 años haciendo scroll a la 1am y lo
califica SIN piedad. Si suena a AI, a locutor, a lista de datos o aburre en
cualquier beat → FAIL con issues accionables (el guionista corrige con ellas).

Uso:  python critico_guion.py <treatment.json>   → exit 0 PASS · exit 1 FAIL
      (escribe out/_treatments/critica_guion.json con el detalle)
"""
import json
import sys
from pathlib import Path

from agent_api import ROOT, ask_json

SYSTEM = """Eres el SCRIPT DOCTOR de un canal de reels financieros — y tu personaje es EL VIEWER:
24 años, mexicano, scrolleando a la 1am, cero paciencia, alergia a todo lo que huela a AI o a
noticiero. Te pagan por MATAR guiones débiles antes de que gasten producción.

Lee el guion completo (la voz de todos los beats, seguida) y evalúa:
1. ¿El hook te detiene el pulgar EN 2 SEGUNDOS? (si abre con contexto/institución = muerte)
2. ¿Suena a PERSONA o a máquina/locutor? (uniformidad de ritmo = máquina; muletillas naturales = persona)
3. ¿Cada beat AVANZA la historia o repite/rellena? (repetir una cifra ya dicha = muerte)
4. ¿Hay UNA revelación guardada para el final o se gasta todo al inicio?
5. ¿La última frase se puede citar sola / da ganas de comentar?
6. ¿Dice algo que un viewer NO sabía? (obviedades = muerte)

Sé DURO: un guion "correcto" que no emociona = FAIL. Solo pasa lo que TÚ verías completo.

Devuelve SOLO JSON:
{"pass": true|false, "score": 0-10,
 "kill_reasons": ["..."],                      // vacío si pass
 "must_fix": [{"beat": N, "problema": "...", "sugerencia": "..."}],
 "best_line": "la mejor frase del guion",
 "verdict_one_line": "tu veredicto en una frase de viewer"}"""


def review(treatment: dict) -> dict:
    script = "\n\n".join(f"[beat {i} · {b['type']}]\n{b['vo']}"
                         for i, b in enumerate(treatment["beats"]))
    return ask_json(SYSTEM, f"EL GUION COMPLETO:\n\n{script}", temperature=0.7)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    treatment = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
    r = review(treatment)
    out = ROOT / "infra" / "assembler" / "out" / "_treatments" / "critica_guion.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"SCRIPT DOCTOR · score {r.get('score')}/10 · {'PASS' if r.get('pass') else 'FAIL'}")
    print(f"  «{r.get('verdict_one_line', '')}»")
    for m in r.get("must_fix", []):
        print(f"  b{m.get('beat')}: {m.get('problema')}")
    sys.exit(0 if r.get("pass") else 1)
