#!/usr/bin/env python3
"""
upload_supabase.py - Sube un MP4 a un bucket PUBLICO de Supabase Storage y devuelve su URL publica.

POR QUE: Instagram Graph API NO recibe el archivo subido; DESCARGA el MP4 de una URL publica.
Este script pone el MP4 en Supabase Storage (bucket publico 'reels', free tier $0) y deja la
URL publica en la ultima linea de stdout para encadenarla con publish_ig.py --video-url.

Flujo: POST objeto via Storage REST API (auth = service_role key, bypassa RLS) -> URL publica.
Costo: $0 (Supabase free tier: 1GB storage; un reel pesa ~11MB). Sin dependencias (solo stdlib).

NOTA: los proyectos free de Supabase se PAUSAN tras ~7 dias sin actividad. Para la publicacion
no importa: IG solo descarga el MP4 una vez (en el momento de publicar, ~minutos) y luego lo
re-hostea en su CDN; la URL solo necesita estar viva durante ese rato. Subir 3x/dia mantiene el
proyecto activo. Si quedo pausado, reactivar es $0 (dashboard o restore).

------------------------------------------------------------------------------------
LO QUE MANUEL HACE UNA SOLA VEZ (es un secreto; Claude NUNCA lo lee/imprime):
  1. Dashboard de Supabase -> proyecto "manupesqueira@gmail.com's Project"
     -> Project Settings -> API -> copiar la "service_role" secret key (NO la anon/publishable).
  2. Guardar en  infra/distribution/.env  (gitignored, NUNCA commitear):
       SUPABASE_URL=https://raacvxndaveidgaqkznh.supabase.co
       SUPABASE_SERVICE_KEY=<service_role secret>
  El bucket publico "reels" ya lo creo Claude por SQL; no requiere accion.

USO:
  python upload_supabase.py "C:\\...\\edu_interes_compuesto_FINAL_916.mp4"
  python upload_supabase.py <ruta.mp4> --bucket reels --name edu_interes_compuesto.mp4
  python upload_supabase.py <ruta.mp4> --dry-run     # valida y muestra la URL sin subir
------------------------------------------------------------------------------------
"""
import argparse
import urllib.error
import urllib.request
from pathlib import Path


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", help="Ruta local del MP4 a subir")
    ap.add_argument("--bucket", default="reels", help="Bucket publico (default: reels)")
    ap.add_argument("--name", help="Nombre del objeto en el bucket (default: nombre del archivo)")
    ap.add_argument("--dry-run", action="store_true", help="Valida y muestra la URL sin subir")
    args = ap.parse_args()

    video = Path(args.video)
    if not video.exists():
        raise SystemExit(f"No existe el archivo: {video}")
    obj_name = args.name or video.name

    env = load_env(Path(__file__).with_name(".env"))
    base = env.get("SUPABASE_URL", "").rstrip("/")
    key = env.get("SUPABASE_SERVICE_KEY")
    if not base or not key:
        raise SystemExit(
            "Falta SUPABASE_URL o SUPABASE_SERVICE_KEY en infra/distribution/.env "
            "(ver cabecera del script para el setup de una sola vez)."
        )

    size_mb = video.stat().st_size / 1_048_576
    upload_url = f"{base}/storage/v1/object/{args.bucket}/{obj_name}"
    public_url = f"{base}/storage/v1/object/public/{args.bucket}/{obj_name}"
    print(f"[supabase] archivo={video.name} ({size_mb:.1f} MB) -> {args.bucket}/{obj_name}")

    if args.dry_run:
        print(f"[supabase] DRY-RUN: no se subio nada. URL seria:")
        print(public_url)
        return

    data = video.read_bytes()
    req = urllib.request.Request(upload_url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("apikey", key)
    req.add_header("Content-Type", "video/mp4")
    req.add_header("x-upsert", "true")  # re-subir sobreescribe (idempotente)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            r.read()
    except urllib.error.HTTPError as e:
        # El cuerpo de error de Storage NO incluye la key; es seguro mostrarlo.
        try:
            body = e.read().decode("utf-8")
        except Exception:
            body = f"HTTP {e.code}"
        raise SystemExit(f"ERROR Supabase Storage: {body}")

    print(f"[supabase] SUBIDO. URL publica:")
    print(public_url)  # ultima linea = solo la URL, para encadenar con publish_ig.py


if __name__ == "__main__":
    main()
