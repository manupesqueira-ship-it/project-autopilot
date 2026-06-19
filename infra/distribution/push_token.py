#!/usr/bin/env python3
"""
push_token.py - Sube tu token de Instagram (largo) del .env LOCAL a la nube.

QUE HACE: copia IG_ACCESS_TOKEN + IG_USER_ID de infra/distribution/.env a la fila
`dinero_ig_credentials` (id=1) de Supabase, para que el publicador en la nube
(Edge Function `publish-due`) pueda postear SIN tu PC. De ahi en adelante la
funcion lo AUTO-REFRESCA sola (~cada 50 dias). Corre esto UNA vez (o cuando
regeneres el token a mano). $0, solo stdlib.

NUNCA imprime el token (solo su longitud, para confirmar que viajo).

USO:
  python push_token.py
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENV = Path(__file__).with_name(".env")


def load_env(path: Path) -> dict:
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

    env = load_env(ENV)
    url = env.get("SUPABASE_URL", "").rstrip("/")
    key = env.get("SUPABASE_SERVICE_KEY")
    token = env.get("IG_ACCESS_TOKEN")
    ig_id = env.get("IG_USER_ID")
    missing = [k for k, v in {
        "SUPABASE_URL": url, "SUPABASE_SERVICE_KEY": key,
        "IG_ACCESS_TOKEN": token, "IG_USER_ID": ig_id,
    }.items() if not v]
    if missing:
        raise SystemExit(f"Falta en infra/distribution/.env: {', '.join(missing)}")

    body = json.dumps({
        "access_token": token,
        "ig_user_id": ig_id,
        "token_updated_at": datetime.now(timezone.utc).isoformat(),
        "last_refreshed_at": None,
        "note": "token subido desde .env local via push_token.py; la Edge Function lo auto-refresca",
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{url}/rest/v1/dinero_ig_credentials?id=eq.1",
        data=body, method="PATCH",
        headers={
            "apikey": key, "Authorization": f"Bearer {key}",
            "Content-Type": "application/json", "Prefer": "return=representation",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode("utf-8")).get("message", f"HTTP {e.code}")
        except Exception:
            msg = f"HTTP {e.code}"
        raise SystemExit(f"ERROR Supabase: {msg}")

    if not res:
        raise SystemExit("No se actualizo la fila id=1 (¿existe dinero_ig_credentials?).")
    print(f"[token] OK: token IG (len={len(token)}) + ig_user_id={ig_id} subidos a la nube.")
    print("[token] El publicador ya puede postear sin tu PC. Se auto-refresca solo.")


if __name__ == "__main__":
    main()
