# -*- coding: utf-8 -*-
# Replica el nodo "Planner (Claude)" + "Validar guion" del workflow n8n,
# para probar el cerebro sin depender de la UI de n8n.
# La validacion la hace el modulo compartido validator.py (fuente de verdad);
# este script ya NO duplica las reglas.
# OJO: ESTE script SI llama a la API de Anthropic (~$0.03-0.05 USD por guion).
#      No correr sin OK de Manuel. Para probar SOLO reglas/ledger usa
#      test_validator.py (offline, $0).
# Uso: python test_planner.py
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

# --- mismo Brief que el nodo Set del workflow ---
wf = json.loads((HERE / "workflow_dinero_ia.json").read_text(encoding="utf-8"))
brief = {a["name"]: a["value"] for n in wf["nodes"] if n["name"] == "Brief"
         for a in n["parameters"]["assignments"]["assignments"]}

user_msg = (f"TEMA: {brief['tema']}\n"
            f"OPEN LOOP DEL SIGUIENTE VIDEO (para el sub del CTA): {brief['open_loop']}\n"
            f"DATOS VERIFICADOS:\n{brief['datos']}")

body = json.dumps({
    "model": "claude-sonnet-4-6",
    "max_tokens": 4000,
    "system": SYSTEM,
    "messages": [{"role": "user", "content": user_msg}],
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages", data=body,
    headers={"x-api-key": KEY, "anthropic-version": "2023-06-01",
             "content-type": "application/json"})
print("Llamando al planner (Claude sonnet-4-6)...")
resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
txt = resp["content"][0]["text"].strip()
txt = re.sub(r"^```(json)?\s*", "", txt)
txt = re.sub(r"```\s*$", "", txt).strip()
g = json.loads(txt)
usage = resp.get("usage", {})
print(f"tokens in={usage.get('input_tokens')} out={usage.get('output_tokens')}")

# --- validacion via modulo compartido (fuente de verdad) + ledger ---
beats = g.get("beats", [])
brief_text = (f"{brief['tema']}\n{brief['datos']}")
ledger = Ledger()
res = validate(g, brief=brief_text, ledger=ledger)

out = ASSEMBLER / f"guion_{g['slug']}.json"
out.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nGUION -> {out.name}  ({len(beats)} beats)")
for b in beats:
    print(f"  {b['id']:14s} {b['type']:14s} | {b['vo'][:60]}...")

for w in res["warnings"]:
    print("  WARN:", w)
if res["errors"]:
    print("\nVALIDADOR: FAIL")
    for e in res["errors"]:
        print("  -", e)
    sys.exit(1)
print("\nVALIDADOR: PASS")
print("Para registrar este video en el ledger tras aprobarlo:")
print(f"  python ../assembler/ledger.py append {out.name}")
