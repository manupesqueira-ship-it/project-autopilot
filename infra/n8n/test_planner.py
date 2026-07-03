# -*- coding: utf-8 -*-
# Replica el nodo "Planner (Claude)" + "Validar guion" del workflow n8n,
# para probar el cerebro sin depender de la UI de n8n.
# La validacion la hace el modulo compartido validator.py (fuente de verdad);
# este script ya NO duplica las reglas.
# OJO: ESTE script SI llama a la API de Anthropic (~$0.03-0.05 USD por guion).
#      No correr sin OK de Manuel. Para probar SOLO reglas/ledger usa
#      test_validator.py (offline, $0).
# Uso: python test_planner.py [id_tema_de_la_cola]   (sin id -> cola.siguiente())
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
ASSEMBLER = ROOT / "infra" / "assembler"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ASSEMBLER))
from validator import validate          # noqa: E402
from ledger import Ledger               # noqa: E402

# --- carga API key del .env del proyecto (sin duplicarla) ---
KEY = None
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if line.startswith("ANTHROPIC_API_KEY="):
        KEY = line.split("=", 1)[1].strip()
assert KEY, "ANTHROPIC_API_KEY no encontrada en .env"

SYSTEM = (HERE / "planner_system_prompt.txt").read_text(encoding="utf-8")

# --- brief del SIGUIENTE tema producible de la cola (banco de material) ---
# Reemplaza el viejo Brief hardcoded del nodo n8n. Pasa un id de tema como
# argumento para forzarlo (p.ej. `python test_planner.py edu_fondo_emergencia`);
# sin argumento usa cola.siguiente() (news urgente primero, luego evergreen).
import cola  # noqa: E402
slug_arg = next((a for a in sys.argv[1:] if not a.startswith("-")), None)
cola_data = cola.load(cola.DEFAULT_COLA)
if slug_arg:
    t = next((x for x in cola_data.get("temas", []) if x.get("id") == slug_arg), None)
    if t is None:
        sys.exit(f"tema '{slug_arg}' no esta en la cola")
    if not cola.producible(t):
        sys.exit(f"tema '{slug_arg}' no es producible (faltan cifras <<verificar>> o vencido)")
    brief = cola._brief(t)
else:
    t = cola.siguiente(cola_data)
    if t is None:
        sys.exit("no hay temas producibles en la cola")
    brief = cola._brief(t)
print(f"TEMA de la cola: {brief['slug']} ({brief['carril']})")

user_msg = (f"TEMA: {brief['tema']}\n"
            f"OPEN LOOP DEL SIGUIENTE VIDEO (para el sub del CTA): {brief['open_loop']}\n"
            f"DATOS VERIFICADOS:\n{brief['datos']}")

def _call(messages):
    """Una llamada al planner; devuelve (guion_dict, texto_crudo, usage)."""
    body = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 4000,
        "system": SYSTEM,
        "messages": messages,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"x-api-key": KEY, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
    raw = resp["content"][0]["text"].strip()
    t = re.sub(r"^```(json)?\s*", "", raw)
    t = re.sub(r"```\s*$", "", t).strip()
    return json.loads(t), raw, resp.get("usage", {})


# --- LAZO DIRECTOR <-> VALIDADOR (auto-correccion) ---
# El director propone; si el validador (fuente de verdad) lo rechaza, le devolvemos
# los errores EXACTOS y el director arregla su PROPIO guion. Acotado (no re-tirar a
# ciegas): 1 intento + hasta 2 reparaciones. Cada llamada ~$0.03-0.05 USD.
MAX_ROUNDS = 3
brief_text = f"{brief['tema']}\n{brief['datos']}"
ledger = Ledger()
messages = [{"role": "user", "content": user_msg}]
g = res = None
for rnd in range(1, MAX_ROUNDS + 1):
    etiqueta = ("Llamando al planner" if rnd == 1
                else f"Reparacion {rnd - 1} (el director corrige sus propios errores)")
    print(f"{etiqueta} (Claude sonnet-4-6)...")
    g, raw, usage = _call(messages)
    g["slug"] = brief["slug"]   # slug del guion = id de la cola (para que el ledger lo cierre)
    print(f"  tokens in={usage.get('input_tokens')} out={usage.get('output_tokens')}")
    res = validate(g, brief=brief_text, ledger=ledger)
    if not res["errors"]:
        break
    print("  VALIDADOR: FAIL ->")
    for e in res["errors"]:
        print("   ", e)
    if rnd < MAX_ROUNDS:
        errores = "\n".join(f"- {e}" for e in res["errors"])
        messages.append({"role": "assistant", "content": raw})
        messages.append({"role": "user", "content": (
            "El validador automatico RECHAZO ese guion por estos errores:\n"
            f"{errores}\n\n"
            "Corrige UNICAMENTE lo necesario para que pasen TODAS las reglas, "
            "manteniendo el mismo tema, el arco y el BeatHeroShot de movimiento. "
            "Recuerda: minimo 2 beats de datos DISTINTOS en la parte media; un hook "
            "BeatKinetic debe revelar la mayoria de las palabras de su vo; y todo "
            "beat de aterrizaje largo (BigNumber/HeroCoin/AssetCard/Versus/Bars) "
            "necesita un cue (countEndWord/growWords/leftEndWord) que caiga en la "
            "SEGUNDA MITAD de su vo. Devuelve SOLO el objeto JSON corregido completo.")})

# --- validacion via modulo compartido (fuente de verdad) + ledger ---
beats = g.get("beats", [])
out = ASSEMBLER / f"guion_{g['slug']}.json"
out.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nGUION -> {out.name}  ({len(beats)} beats)")
for b in beats:
    print(f"  {b['id']:14s} {b['type']:14s} | {b['vo'][:60]}...")

for w in res["warnings"]:
    print("  WARN:", w)
if res["errors"]:
    print(f"\nVALIDADOR: FAIL (tras {MAX_ROUNDS - 1} reparacion(es))")
    for e in res["errors"]:
        print("  -", e)
    sys.exit(1)
print("\nVALIDADOR: PASS")
print("Para registrar este video en el ledger tras aprobarlo:")
print(f"  python ../assembler/ledger.py append {out.name}")
