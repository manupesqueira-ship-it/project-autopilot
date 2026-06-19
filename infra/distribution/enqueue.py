#!/usr/bin/env python3
"""
enqueue.py - Mete un video YA APROBADO en la cola de publicacion (Supabase).

QUE HACE: despues del OK humano (Telegram), inserta una fila en
`dinero_publish_queue`. El publicador en la nube (cron prime-time, SIN PC) la
toma a su hora y la sube. $0, solo stdlib (urllib).

POR QUE una cola en la nube y no publicar al toque:
  - El posteo ocurre a HORA ESTRATEGICA (~8pm MX), no cuando aprietas el boton.
  - La cola es TAMBIEN el registro de "ya subido": si (slug, platform) ya esta
    queued/publishing/posted, NO se re-encola -> no hay doble post ni re-gasto.

CARRILES (lane):
  - 'news'      perecedero. Caduca en --ttl-hours (default 36). Si no se publico
                antes de expires_at, el publicador lo marca 'expired' y NO lo sube
                (noticia vieja = pierde credibilidad la cuenta).
  - 'evergreen' sin caducidad. Rellena dias sin noticia.

INTEGRIDAD: guarda video_sha256 (hash del CONTENIDO del MP4 local) para casar el
archivo aprobado con lo que se publico.

Lee SUPABASE_URL + SUPABASE_SERVICE_KEY de infra/distribution/.env. NUNCA imprime
la llave (va en headers, no en la URL ni en logs).

USO (CLI):
  python enqueue.py --slug edu_interes_compuesto \
      --video-url "https://HOST/edu_interes_compuesto_FINAL_916.mp4" \
      --caption-file out_caption_ig.txt --lane evergreen \
      --video-file "C:\\...\\edu_interes_compuesto_FINAL_916.mp4"

  python enqueue.py ... --lane news --ttl-hours 36     # noticia: expira en 36h

Tambien se importa desde el orquestador (producir.py):
  from enqueue import enqueue
"""
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
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


def _creds() -> tuple[str, str]:
    env = load_env(ENV)
    url = env.get("SUPABASE_URL")
    key = env.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise SystemExit("Falta SUPABASE_URL o SUPABASE_SERVICE_KEY en infra/distribution/.env")
    return url.rstrip("/"), key


def _headers(key: str, extra=None) -> dict:
    h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if extra:
        h.update(extra)
    return h


def _req(method: str, url: str, key: str, body=None, extra_headers=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers=_headers(key, extra_headers))
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        # El cuerpo de error de PostgREST NO incluye la llave (va en headers).
        try:
            err = json.loads(e.read().decode("utf-8"))
            msg = err.get("message") or err.get("hint") or str(err)
        except Exception:
            msg = f"HTTP {e.code}"
        raise SystemExit(f"ERROR Supabase ({method} /{url.split('/rest/')[-1]}): {msg}")


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def already_in_queue(url: str, key: str, slug: str, platform: str,
                     media_type: str = "reel"):
    """Fila activa (queued|publishing|posted) para ese slug+plataforma+media_type, o None.

    media_type entra a la llave de dedup: un mismo tema tiene DOS piezas (el reel del
    feed y su Story-teaser), ambas con platform='instagram' y el mismo slug. Sin el
    media_type, encolar la Story se veria como duplicado del reel y se saltaria.
    """
    q = urllib.parse.urlencode({
        "slug": f"eq.{slug}",
        "platform": f"eq.{platform}",
        "media_type": f"eq.{media_type}",
        "status": "in.(queued,publishing,posted)",
        "select": "id,status,scheduled_for,permalink",
    })
    rows = _req("GET", f"{url}/rest/v1/dinero_publish_queue?{q}", key)
    return rows[0] if rows else None


def enqueue(slug: str, video_url: str, caption: str, lane: str = "evergreen",
            platform: str = "instagram", video_file: str = None,
            ttl_hours: int = 36, scheduled_for: str = None,
            media_type: str = "reel") -> dict:
    """Encola un video aprobado. Idempotente por (slug, platform, media_type)."""
    url, key = _creds()

    dup = already_in_queue(url, key, slug, platform, media_type)
    if dup:
        print(f"[cola] '{slug}' ({media_type}) ya esta en la cola (status={dup['status']}). No re-encolo.")
        return {"skipped": True, "existing": dup}

    now = datetime.now(timezone.utc)
    sched = scheduled_for or now.isoformat()
    expires = (now + timedelta(hours=ttl_hours)).isoformat() if lane == "news" else None
    sha = _sha256_file(video_file) if video_file else None

    row = {
        "slug": slug, "platform": platform, "lane": lane, "media_type": media_type,
        "video_url": video_url, "caption": caption, "video_sha256": sha,
        "status": "queued", "scheduled_for": sched, "expires_at": expires,
    }
    res = _req("POST", f"{url}/rest/v1/dinero_publish_queue", key, body=row,
               extra_headers={"Prefer": "return=representation"})
    new = res[0] if isinstance(res, list) else res
    tail = f" expires_at={expires}" if expires else ""
    print(f"[cola] encolado id={new['id']} lane={lane} scheduled_for={sched}{tail}")
    return {"skipped": False, "row": new}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--video-url", required=True, help="URL PUBLICA del MP4")
    ap.add_argument("--caption")
    ap.add_argument("--caption-file")
    ap.add_argument("--lane", choices=["news", "evergreen"], default="evergreen")
    ap.add_argument("--platform", default="instagram")
    ap.add_argument("--media-type", choices=["reel", "story"], default="reel",
                    help="reel = post del feed (default) · story = teaser 24h")
    ap.add_argument("--video-file", help="MP4 local (para el sha256 de integridad)")
    ap.add_argument("--ttl-hours", type=int, default=36, help="solo para lane=news")
    ap.add_argument("--scheduled-for", help="ISO8601; default = ahora")
    args = ap.parse_args()

    # una Story no lleva caption (la Graph API no acepta caption en STORIES)
    if args.media_type == "story":
        caption = ""
    elif args.caption_file:
        caption = Path(args.caption_file).read_text(encoding="utf-8").strip()
    elif args.caption:
        caption = args.caption
    else:
        raise SystemExit("Falta --caption o --caption-file")

    enqueue(args.slug, args.video_url, caption, lane=args.lane,
            platform=args.platform, video_file=args.video_file,
            ttl_hours=args.ttl_hours, scheduled_for=args.scheduled_for,
            media_type=args.media_type)


if __name__ == "__main__":
    main()
