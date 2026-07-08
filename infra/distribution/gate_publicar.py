#!/usr/bin/env python3
"""
gate_publicar.py — El viaje completo del gate humano (pedido de Manuel 2026-07-07):

    MP4 final → Supabase (URL pública) → Telegram con [OK Publicar]/[Basura]
    → espera TU tap en el celular → si apruebas, PUBLICA el Reel en @dinerolatam
    → te confirma en Telegram con el resultado.

USO:
  python gate_publicar.py --video out/<slug>/<slug>_FINAL_916.mp4 \
                          --caption-file caption.txt --slug <slug> [--timeout 86400]
  python gate_publicar.py ... --dry-run   # todo el viaje SIN publicar (el tap solo confirma)

Reusa las piezas ya probadas: upload_supabase (host), telegram_bot (gate con
botones), publish_ig (Graph API Instagram-login). $0 extra, stdlib.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from telegram_bot import _call, _creds, send_for_approval, wait_for_decision  # noqa: E402
from upload_supabase import load_env  # noqa: E402

PY = sys.executable


def _run(script: str, args: list[str]) -> str:
    """Corre un script hermano y devuelve su stdout (falla ruidoso si exit != 0)."""
    r = subprocess.run([PY, str(HERE / script), *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"{script} fallo (exit {r.returncode}):\n{r.stdout}\n{r.stderr}")
    return r.stdout


def upload(video: Path, slug: str) -> str:
    """Sube el MP4 al bucket público y devuelve la URL (última línea con http)."""
    out = _run("upload_supabase.py", ["--video", str(video), "--name", f"{slug}.mp4"])
    urls = [l.strip() for l in out.splitlines() if l.strip().startswith("http")]
    if not urls:
        raise SystemExit(f"upload_supabase no devolvió URL:\n{out}")
    return urls[-1]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--caption-file")
    ap.add_argument("--caption")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--timeout", type=int, default=86400)  # 24h para el tap
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    video = Path(args.video)
    if not video.exists():
        raise SystemExit(f"no existe: {video}")
    if args.caption_file:
        caption = Path(args.caption_file).read_text(encoding="utf-8-sig").strip()
    elif args.caption:
        caption = args.caption
    else:
        raise SystemExit("falta --caption o --caption-file")

    print(f"[gate] 1/4 subiendo a Supabase: {video.name}")
    url = upload(video, args.slug)
    print(f"[gate] URL publica lista")

    token, chat = _creds()
    tag = f"{args.slug}-{int(time.time())}"
    print(f"[gate] 2/4 enviando a Telegram con botones (tag {tag})")
    send_for_approval(token, chat, url, caption, tag)

    print(f"[gate] 3/4 esperando tu tap (hasta {args.timeout // 3600}h)...")
    decision = wait_for_decision(token, chat, tag, timeout=args.timeout)
    print(f"[gate] decision: {decision.upper()}")
    if decision != "approved":
        return

    if args.dry_run:
        _call(token, "sendMessage", data={
            "chat_id": chat,
            "text": "🧪 DRY-RUN: aprobado, pero NO se publica (prueba del flujo)."})
        print("[gate] dry-run: no se publica")
        return

    print("[gate] 4/4 publicando Reel en @dinerolatam ...")
    pub_args = ["--video-url", url]
    if args.caption_file:
        pub_args += ["--caption-file", args.caption_file]
    else:
        pub_args += ["--caption", caption]
    out = _run("publish_ig.py", pub_args)
    print(out.strip().splitlines()[-1] if out.strip() else "[gate] publicado")
    _call(token, "sendMessage", data={
        "chat_id": chat,
        "text": f"🚀 PUBLICADO en @dinerolatam — reel '{args.slug}' ya está en el feed."})


if __name__ == "__main__":
    main()
