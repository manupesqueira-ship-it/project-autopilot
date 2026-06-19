#!/usr/bin/env python3
"""
publish_ig.py - Publica un Reel en Instagram via Graph API (Dinero LATAM @dinerolatam).

QUE HACE: toma un MP4 que YA esta en una URL PUBLICA + un caption, y lo publica como
Reel. Flujo oficial Graph API en 3 pasos: crear contenedor -> esperar FINISHED -> publicar.
Costo: $0 (API oficial). Sin dependencias (solo stdlib).

------------------------------------------------------------------------------------
FLUJO "Instagram login" (graph.instagram.com): SIN Facebook, SIN Pagina de FB.
LO QUE MANUEL HACE UNA SOLA VEZ (es identidad/OAuth; Claude no puede hacerlo):
  1. @dinerolatam = cuenta Professional (Business o Creator).
  2. App en developers.facebook.com -> use case "Instagram" -> "API setup with Instagram login".
     Permisos: instagram_business_basic + instagram_business_content_publish.
  3. "Generate access tokens" -> "Add account" -> loguear con @dinerolatam -> copiar el token.
  4. Poner en .env: IG_APP_SECRET + IG_SHORT_TOKEN, y correr `python ig_setup.py`
     (cambia el token a largo ~60d y resuelve IG_USER_ID; deja IG_ACCESS_TOKEN+IG_USER_ID en .env).
  Nota: self-post a TU PROPIA cuenta NO requiere el App Review de 2-4 semanas.

USO:
  python publish_ig.py --video-url "https://HOST/edu_interes_compuesto_FINAL_916.mp4" \
                       --caption-file out_caption_ig.txt
  python publish_ig.py --video-url "https://..." --caption "texto del caption..."
  python publish_ig.py ... --dry-run     # valida todo SIN publicar

El MP4 necesita estar en una URL publica porque Meta lo DESCARGA (no se sube el archivo).
Host $0 a decidir aparte (bucket publico de Supabase free / static host).
------------------------------------------------------------------------------------
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

GRAPH_VERSION = "v21.0"  # Meta bumpea ~trimestral; subir aqui si caduca.
GRAPH = f"https://graph.instagram.com/{GRAPH_VERSION}"  # flujo "Instagram login" (sin Facebook/Pagina)
POLL_TIMEOUT_S = 300      # el procesamiento del video puede tardar minutos
POLL_EVERY_S = 5


def load_env(env_path: Path) -> dict:
    """Lee KEY=VALUE de .env. No imprime valores (secretos)."""
    env = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _post(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    return _send(req)


def _get(url: str) -> dict:
    return _send(urllib.request.Request(url, method="GET"))


def _send(req) -> dict:
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # El cuerpo de error de Graph NO incluye el token; es seguro mostrarlo.
        try:
            err = json.loads(e.read().decode("utf-8"))
            msg = err.get("error", {}).get("message", str(err))
        except Exception:
            msg = f"HTTP {e.code}"
        raise SystemExit(f"ERROR Graph API: {msg}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows: la consola cp1252 truena con emojis del caption
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--video-url", required=True, help="URL PUBLICA del MP4")
    ap.add_argument("--caption", help="Texto del caption")
    ap.add_argument("--caption-file", help="Archivo con SOLO el caption (utf-8)")
    ap.add_argument("--dry-run", action="store_true", help="Valida sin publicar")
    args = ap.parse_args()

    if args.caption_file:
        caption = Path(args.caption_file).read_text(encoding="utf-8").strip()
    elif args.caption:
        caption = args.caption
    else:
        raise SystemExit("Falta --caption o --caption-file")

    env = load_env(Path(__file__).with_name(".env"))
    ig_id = env.get("IG_USER_ID")
    token = env.get("IG_ACCESS_TOKEN")
    if not ig_id or not token:
        raise SystemExit(
            "Falta IG_USER_ID o IG_ACCESS_TOKEN en infra/distribution/.env "
            "(ver cabecera del script para el setup de una sola vez)."
        )

    print(f"[ig] cuenta={ig_id}  video={args.video_url}")
    print(f"[ig] caption ({len(caption)} chars):\n{caption}\n")
    if args.dry_run:
        print("[ig] DRY-RUN: todo listo, no se publico nada.")
        return

    # 1) crear contenedor (Meta descarga el video de la URL publica)
    cont = _post(f"{GRAPH}/{ig_id}/media", {
        "media_type": "REELS",
        "video_url": args.video_url,
        "caption": caption,
        "access_token": token,
    })
    cid = cont["id"]
    print(f"[ig] contenedor creado: {cid}")

    # 2) esperar a que el contenedor termine de procesar
    deadline = time.time() + POLL_TIMEOUT_S
    while True:
        st = _get(f"{GRAPH}/{cid}?fields=status_code,status&"
                  + urllib.parse.urlencode({"access_token": token}))
        code = st.get("status_code")
        print(f"[ig] estado: {code}")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            raise SystemExit(f"Contenedor fallo: {st.get('status')}")
        if time.time() > deadline:
            raise SystemExit("Timeout esperando el procesamiento del video.")
        time.sleep(POLL_EVERY_S)

    # 3) publicar
    pub = _post(f"{GRAPH}/{ig_id}/media_publish", {
        "creation_id": cid,
        "access_token": token,
    })
    media_id = pub["id"]
    link = _get(f"{GRAPH}/{media_id}?fields=permalink&"
                + urllib.parse.urlencode({"access_token": token}))
    print(f"[ig] PUBLICADO  media_id={media_id}  {link.get('permalink', '')}")


if __name__ == "__main__":
    main()
