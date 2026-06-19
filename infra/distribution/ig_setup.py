#!/usr/bin/env python3
"""
ig_setup.py - Termina el setup de Meta (flujo "Instagram login", SIN Facebook/Pagina).

Hace 2 cosas tediosas por ti, SIN imprimir secretos:
  1) Cambia tu token CORTO (el del boton "Generate token" / "Add account") por uno
     LARGO (~60 dias) via graph.instagram.com.
  2) Resuelve tu IG_USER_ID (id numerico de la cuenta) via /me.
Y escribe ambos (IG_ACCESS_TOKEN largo + IG_USER_ID) de vuelta en .env.

------------------------------------------------------------------------------------
ANTES de correrlo, pon estos 2 en infra/distribution/.env (yo nunca los imprimo):
    IG_APP_SECRET=<Instagram app secret>   (app de Meta -> use case Instagram -> "API setup
                                            with Instagram login" -> Instagram app secret / Show)
    IG_SHORT_TOKEN=<token que genera "Add account">   (loguear con @dinerolatam)
Requisito previo: la app tiene el permiso instagram_business_content_publish, y @dinerolatam
es cuenta Professional (Business o Creator).

USO:   python ig_setup.py
Luego: python publish_ig.py --video-url <URL_publica> --caption-file caption_dinerolatam.txt
------------------------------------------------------------------------------------
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GRAPH = "https://graph.instagram.com"
ENV_PATH = Path(__file__).with_name(".env")


def load_env(env_path: Path) -> dict:
    env = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _get(url: str, soft: bool = False):
    """GET JSON. soft=True devuelve None en error (en vez de abortar)."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="GET"), timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8"))
            msg = err.get("error", {}).get("message", str(err))
        except Exception:
            msg = f"HTTP {e.code}"
        if soft:
            print(f"[meta] aviso: {msg}")
            return None
        raise SystemExit(f"ERROR Instagram API: {msg}")


def set_env_keys(env_path: Path, updates: dict):
    """Reescribe .env actualizando/insertando KEY=VALUE. Preserva el resto. No imprime valores."""
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    seen = set()
    out = []
    for line in lines:
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            k = stripped.split("=", 1)[0].strip()
            if k in updates:
                out.append(f"{k}={updates[k]}")
                seen.add(k)
                continue
        out.append(line)
    for k, v in updates.items():
        if k not in seen:
            out.append(f"{k}={v}")
    env_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    env = load_env(ENV_PATH)
    app_secret = env.get("IG_APP_SECRET") or env.get("FB_APP_SECRET")  # acepta cualquiera de los 2 nombres
    short = env.get("IG_SHORT_TOKEN")
    missing = [k for k, v in [("IG_APP_SECRET/FB_APP_SECRET", app_secret), ("IG_SHORT_TOKEN", short)] if not v]
    if missing:
        raise SystemExit(
            "Falta en .env: " + ", ".join(missing) +
            "\n(ver la cabecera de ig_setup.py para que es cada uno)."
        )

    # 1) token corto -> largo (~60 dias). Si ya viene largo, el exchange puede fallar:
    #    en ese caso seguimos con el token tal cual.
    q = urllib.parse.urlencode({
        "grant_type": "ig_exchange_token",
        "client_secret": app_secret,
        "access_token": short,
    })
    res = _get(f"{GRAPH}/access_token?{q}", soft=True)
    if res and res.get("access_token"):
        token = res["access_token"]
        days = res.get("expires_in", 0) // 86400
        print(f"[meta] token largo OK (~{days} dias de vigencia)")
    else:
        token = short
        print("[meta] uso el token tal cual (no se pudo intercambiar; puede que ya sea largo)")

    # 2) resolver IG_USER_ID
    me = _get(f"{GRAPH}/me?fields=user_id,username&"
              + urllib.parse.urlencode({"access_token": token}))
    ig_id = me.get("user_id") or me.get("id")
    username = me.get("username", "")
    if not ig_id:
        raise SystemExit("No se pudo resolver el IG_USER_ID (revisa el token / permisos).")
    print(f"[meta] cuenta = @{username}   IG_USER_ID = {ig_id}")

    # 3) escribir de vuelta (token no se imprime; ig_id no es secreto)
    set_env_keys(ENV_PATH, {"IG_ACCESS_TOKEN": token, "IG_USER_ID": ig_id})
    print("[meta] .env actualizado: IG_ACCESS_TOKEN (largo) + IG_USER_ID. Listo para publish_ig.py")


if __name__ == "__main__":
    main()
