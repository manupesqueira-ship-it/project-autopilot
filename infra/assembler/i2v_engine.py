# -*- coding: utf-8 -*-
"""
F3 — Wrapper del motor imagen->video (i2v), PROVIDER-ABSTRACTED, modo DRY-RUN.

Sirve a los arquetipos que CUESTAN del menu cerrado (SHOT_VOCABULARY.md):
  3 Objeto-heroe (lane hero_shot)  y  4 Caricatura-personaje.
Toma un STILL ya hecho (Seedream/Blender/gpt-image: el wrapper es agnostico de
como se genero) + una spec de movimiento, y produce el clip que SE MUEVE.

POR QUE EXISTE (PLAN_MOTOR_AI_v3): el objeto/personaje que se mueve es la unica
pieza de paga; el resto (logos vector real, mapas, charts, tipografia) es CODIGO $0.
Este wrapper aisla al proveedor (Kling/Seedance/PixVerse) detras de una interfaz
unica, para poder cambiarlo sin tocar el pipeline (desacople one-way del director).

CONGELAMIENTO DE GASTOS (Manuel): por DEFECTO no llama a NINGUN proveedor ni paga.
  - `plan()`  = DRY-RUN $0: valida la peticion, ESTIMA el costo, escribe un manifest
    y (opcional) renderiza un PLACEHOLDER local (push-in sobre el still) para poder
    cablear/probar F5 (candado anti-slideshow) y el ensamblador end-to-end sin pagar.
  - `submit()` = LIVE (paga): BLOQUEADO con doble candado (flag --live + env
    I2V_ALLOW_SPEND=1). Es la ruta de GATE 2; NO se corre hasta que Manuel lo apruebe.

Uso:
  python i2v_engine.py providers                 # lista rate-cards (verificar en vivo)
  python i2v_engine.py plan shots.json           # DRY-RUN: estima + manifest + placeholders
  python i2v_engine.py plan shots.json --no-placeholder
  # LIVE (NO correr sin OK de Manuel + GATE 2):
  #   $env:I2V_ALLOW_SPEND=1 ; python i2v_engine.py submit shots.json --live
"""
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
HERE = Path(__file__).parent
OUT_DRYRUN = HERE / "out" / "_i2v_dryrun"
EXPENSES = ROOT / "docs" / "EXPENSES.md"

sys.path.insert(0, str(ROOT / "infra" / "voz"))
from tts_timestamps import (  # noqa: E402
    RETRY_STATUS, RetryableError, load_env, with_retries)

# ffmpeg: mismo patron que build916.py (Gyan no esta en PATH -> FFMPEG_BIN o ruta).
FFMPEG = os.environ.get("FFMPEG_BIN") or (
    r"C:\Users\manup\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe")
if not os.path.exists(FFMPEG):
    FFMPEG = "ffmpeg"

FX_MXN = 17.4  # TC aprox USD->MXN (solo para mostrar; el cargo real es en USD)

# --------------------------------------------------------------------------
# Rate-cards de proveedores. OJO: precios/endpoints DECAEN -> `verificado=null`
# obliga a confirmar EN VIVO en fal antes de pasar a LIVE (memoria del stack).
# usd_per_s = costo por segundo de clip generado. El abstraction-layer expone
# build_request() por-proveedor; en DRY-RUN no se llama a ninguno.
# --------------------------------------------------------------------------
PROVIDERS = {
    "kling_v3_pro": {
        "fal_endpoint": "fal-ai/kling-video/v3/pro/image-to-video",
        "usd_per_s": 0.112,          # audio OFF (lo que usamos); on=0.168, voice=0.196
        "max_s": 15, "fps": 30, "min_s": 3,
        "supports_motion_brush": False,   # el endpoint v3 de fal NO expone motion_brush
        "verificado": "2026-06-24 (fal: start_image_url/generate_audio + $0.112/s audio-off)",
        "note": "premium 2026; aspecto = START IMAGE (padeamos a 9:16); audio = pipeline propio.",
    },
    "kling_v25_turbo_pro": {
        "fal_endpoint": "fal-ai/kling-video/v2.5-turbo/pro/image-to-video",
        "usd_per_s": 0.07,
        "max_s": 10, "fps": 30, "min_s": 3,
        "supports_motion_brush": False,
        "verificado": None,
        "note": "mas barato; balance precio/control (stack base ~$1.56/reel).",
    },
    "seedance_1_pro": {
        "fal_endpoint": "fal-ai/bytedance/seedance/v1/pro/image-to-video",
        "usd_per_s": 0.124,          # ~$0.62 / 5s
        "max_s": 12, "fps": 24, "min_s": 3,
        "supports_motion_brush": False,
        "verificado": None,
        "note": "clips largos (12s), hasta 9 refs; confirmar 1080p vertical.",
    },
    "pixverse_v45": {
        "fal_endpoint": "fal-ai/pixverse/v4.5/image-to-video",
        "usd_per_s": 0.045,
        "max_s": 8, "fps": 30, "min_s": 3,
        "supports_motion_brush": False,
        "verificado": None,
        "note": "anime-puro mas barato; alternativa a Kling para caricatura.",
    },
}
DEFAULT_PROVIDER = "kling_v3_pro"
VALID_ASPECTS = {"9:16"}            # el canal es vertical; nada mas se acepta


class ShotError(Exception):
    """Peticion de shot invalida (still ausente, aspect/duracion/proveedor malos)."""


def _provider(name: str) -> dict:
    if name not in PROVIDERS:
        raise ShotError(f"proveedor '{name}' desconocido; usa uno de {sorted(PROVIDERS)}")
    return PROVIDERS[name]


def _resolve_still(p: str) -> Path:
    """Acepta ruta absoluta o relativa a la raiz del repo o a infra/assembler."""
    cand = Path(p)
    for base in (cand, ROOT / p, HERE / p):
        if base.is_file():
            return base
    raise ShotError(f"still no encontrado: {p}")


def validate(shot: dict) -> dict:
    """Normaliza + valida un shot; lanza ShotError si algo no cumple. $0."""
    sid = shot.get("shot_id") or shot.get("id")
    if not sid:
        raise ShotError("shot sin 'shot_id'")
    prov_name = shot.get("provider", DEFAULT_PROVIDER)
    prov = _provider(prov_name)
    still = _resolve_still(shot["still"]) if shot.get("still") else None
    if still is None:
        raise ShotError(f"[{sid}] falta 'still' (imagen de entrada)")
    aspect = shot.get("aspect", "9:16")
    if aspect not in VALID_ASPECTS:
        raise ShotError(f"[{sid}] aspect '{aspect}' invalido (el canal es 9:16)")
    dur = float(shot.get("duration_s", 5))
    if not (prov["min_s"] <= dur <= prov["max_s"]):
        raise ShotError(
            f"[{sid}] duration_s={dur} fuera de rango del proveedor "
            f"{prov_name} ({prov['min_s']}-{prov['max_s']}s)")
    if shot.get("motion_brush") and not prov["supports_motion_brush"]:
        raise ShotError(f"[{sid}] {prov_name} no soporta motion_brush")
    if not (shot.get("motion") or "").strip():
        raise ShotError(f"[{sid}] falta 'motion' (descripcion del movimiento)")
    return {
        "shot_id": sid,
        "provider": prov_name,
        "still": str(still),
        "aspect": aspect,
        "duration_s": dur,
        "fps": int(shot.get("fps", prov["fps"])),
        "motion": shot["motion"].strip(),
        "motion_brush": shot.get("motion_brush"),
    }


def estimate_cost(shot: dict) -> float:
    """USD estimado para un shot (proveedor usd_per_s x duracion). $0 de ejecutar."""
    v = shot if "provider" in shot and "duration_s" in shot else validate(shot)
    return round(PROVIDERS[v["provider"]]["usd_per_s"] * float(v["duration_s"]), 4)


THEME_BG = (13, 17, 23)   # #0D1117 — piso del theme (para padear el still a 9:16)


def _still_to_data_uri(still_path: str) -> str:
    """Prepara el still para fal (LIVE) y lo devuelve como data-URI JPEG.

    9:16: el endpoint Kling v3 toma el aspecto de la START IMAGE (no hay param de
    aspecto), asi que padeamos el still a 1080x1920 sobre el piso del theme (NO se
    recorta el objeto: fit-width + barras arriba/abajo). Sin esto, un still 2:3
    saldria 2:3, no vertical.
    data-URI: fal acepta base64 data-URI como file input (verificado 2026-06-24),
    evita host publico y un 2o round-trip a fal storage. JPEG q92 (el still no usa
    alfa: el fondo va horneado) para no inflar el payload."""
    im = Image.open(still_path).convert("RGB")
    tw, th = 1080, 1920
    w, h = im.size
    nh = max(1, round(h * tw / w))
    im = im.resize((tw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", (tw, th), THEME_BG)
    if nh <= th:
        canvas.paste(im, (0, (th - nh) // 2))          # fit-width, padea vertical
    else:
        top = (nh - th) // 2                            # still muy alto: recorta-centro
        canvas.paste(im.crop((0, top, tw, top + th)), (0, 0))
    buf = BytesIO()
    canvas.save(buf, format="JPEG", quality=92)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def build_request(shot: dict) -> dict:
    """Cuerpo que se ENVIARIA a fal en LIVE, segun el schema VERIFICADO (2026-06-24)
    del endpoint Kling v3 Pro i2v. Aisla el formato del proveedor; NO llama a nada.
      - `start_image_url`: la imagen de arranque (file:// placeholder; submit() lo
        reemplaza por el data-URI 9:16 real).
      - `duration`: STRING de segundos ("3".."15"), no numero.
      - `generate_audio`: en fal DEFAULTEA a True -> lo forzamos a False (el audio
        del reel lo pone NUESTRO pipeline; ademas baja el costo a $0.112/s).
      - aspecto: lo define la START IMAGE (no hay param) -> el padding 9:16 va en
        submit(). NO hay motion_brush/fps en este endpoint -> no se mandan."""
    v = validate(shot)
    body = {
        "start_image_url": f"file://{v['still']}",   # submit() lo reemplaza por data-URI
        "prompt": v["motion"],
        "duration": str(int(round(v["duration_s"]))),
        "generate_audio": False,
    }
    neg = (shot.get("negative_prompt") or "").strip()
    if neg:
        body["negative_prompt"] = neg
    return {"endpoint": PROVIDERS[v["provider"]]["fal_endpoint"], "input": body}


def _placeholder_clip(v: dict, out_dir: Path) -> Path | None:
    """DRY-RUN $0: clip placeholder = push-in lento sobre el still (representa
    'este slot SE MUEVE') para cablear F5/ensamblador sin pagar. Procedencia por
    nombre (_DRYRUN) + manifest; si zoompan falla, cae a un hold (sigue marcado)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{v['shot_id']}_DRYRUN.mp4"
    fps, dur = v["fps"], v["duration_s"]
    nframes = max(int(round(fps * dur)), 1)
    # Placeholder = push-in lento sobre el still (representa "este slot SE MUEVE").
    # Es un STAND-IN de dry-run, no el clip final (ese lo da Kling en GATE 2), a
    # resolucion nativa. OJO ffmpeg: `-loop 1` da frames infinitas y zoompan d=N
    # repite CADA frame de entrada N veces -> hay que ALIMENTAR una sola y CAPAR la
    # SALIDA con `-frames:v N` (si ademas pones `-t dur` en la entrada metes dur*fps
    # frames de entrada * N = clip N veces mas largo: el bug de los 750s).
    vf_zoom = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"zoompan=z='min(zoom+0.0010,1.14)':d={nframes}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
    )
    base = [FFMPEG, "-y", "-loop", "1", "-i", v["still"]]
    enc = ["-frames:v", str(nframes), "-c:v", "libx264", "-preset", "veryfast",
           "-pix_fmt", "yuv420p", "-r", str(fps), str(out)]
    r = subprocess.run(base + ["-vf", vf_zoom] + enc,
                       capture_output=True, text=True)
    if r.returncode != 0:
        # fallback robusto: hold estatico (placeholder igual, sin movimiento)
        vf_hold = ("scale=1080:1920:force_original_aspect_ratio=increase,"
                   "crop=1080:1920")
        r2 = subprocess.run(base + ["-vf", vf_hold] + enc,
                            capture_output=True, text=True)
        if r2.returncode != 0:
            print(f"  PLACEHOLDER warn [{v['shot_id']}]: ffmpeg fallo "
                  f"({r2.stderr.strip()[:160]})")
            return None
        print(f"  PLACEHOLDER [{v['shot_id']}] (hold, sin zoom) -> {out.name}")
        return out
    print(f"  PLACEHOLDER [{v['shot_id']}] (push-in) -> {out.name}")
    return out


def plan(shots: list[dict], out_dir: Path = OUT_DRYRUN,
         render_placeholder: bool = True) -> dict:
    """DRY-RUN $0: valida todos los shots, estima costo total, escribe manifest y
    (opcional) placeholders. NO llama a ningun proveedor. NO registra gasto."""
    rows, total = [], 0.0
    for s in shots:
        v = validate(s)
        cost = estimate_cost(v)
        total += cost
        ph = _placeholder_clip(v, out_dir) if render_placeholder else None
        rows.append({**v, "est_cost_usd": cost,
                     "placeholder": str(ph) if ph else None})
    manifest = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": "dry_run",
        "fx_rate_mxn": FX_MXN,
        "shots": rows,
        "total_cost_usd": round(total, 4),
        "total_cost_mxn": round(total * FX_MXN, 2),
        "note": ("DRY-RUN: no se llamo a ningun proveedor; $0. Producir de verdad "
                 "= GATE 2 + OK de Manuel + I2V_ALLOW_SPEND=1 + --live."),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    mpath = out_dir / "i2v_plan.json"
    tmp = mpath.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, mpath)  # escritura atomica (mismo patron que ledger/cola)
    print(f"\nPLAN dry-run: {len(rows)} shots · est ${total:.2f} USD "
          f"(~${total*FX_MXN:.0f} MXN) · manifest -> {mpath}")
    return manifest


def submit(shots: list[dict], live: bool = False) -> list[Path]:
    """LIVE (PAGA). Doble candado: live=True Y env I2V_ALLOW_SPEND=1. Es GATE 2;
    NO correr sin OK explicito de Manuel. Sin los dos candados, aborta a DRY-RUN."""
    if not live or os.environ.get("I2V_ALLOW_SPEND") != "1":
        raise SystemExit(
            "BLOQUEADO: submit() paga. Requiere --live Y env I2V_ALLOW_SPEND=1. "
            "Esto es GATE 2 (primer render de paga) -> necesita OK de Manuel. "
            "Para probar sin pagar usa `plan` (dry-run, $0).")
    key = load_env().get("FAL_KEY") or load_env().get("FAL_API_KEY")
    if not key:
        raise SystemExit("falta FAL_KEY en .env para LIVE")
    outs = []
    for s in shots:
        req = build_request(s)
        v = validate(s)
        cost = estimate_cost(v)
        # En LIVE el still local se padea a 9:16 y se empaqueta como data-URI
        # (fal no puede leer file://; el aspecto del clip = el de esta imagen).
        req["input"]["start_image_url"] = _still_to_data_uri(v["still"])
        body = json.dumps(req["input"]).encode("utf-8")
        url = f"https://fal.run/{req['endpoint']}"
        http = urllib.request.Request(
            url, data=body,
            headers={"Authorization": f"Key {key}",
                     "Content-Type": "application/json"}, method="POST")

        def _call():
            try:
                with urllib.request.urlopen(http, timeout=600) as r:
                    return json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code in RETRY_STATUS:
                    raise RetryableError(f"HTTP {e.code}")
                raise SystemExit(f"fal HTTP {e.code}: {e.read()[:200]}")
            except (urllib.error.URLError, TimeoutError) as e:
                raise RetryableError(f"red/timeout: {e}")

        print(f"LIVE i2v [{v['shot_id']}] {v['provider']} {v['duration_s']}s "
              f"~${cost:.2f} USD ...")
        data = with_retries(_call, what=f"fal[{v['shot_id']}]")
        video_url = (data.get("video") or {}).get("url") or data.get("url")
        if not video_url:
            raise SystemExit(f"respuesta fal sin video url: {str(data)[:200]}")
        OUT_DRYRUN.parent.mkdir(parents=True, exist_ok=True)
        dst = HERE / "out" / "_i2v" / f"{v['shot_id']}.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(video_url, timeout=600) as r:
            dst.write_bytes(r.read())
        _log_expense(v, cost)
        print(f"LIVE ok -> {dst}")
        outs.append(dst)
    return outs


def _log_expense(v: dict, cost: float):
    line = (f"\n- {datetime.now().date()} · fal {v['provider']} i2v · "
            f"shot '{v['shot_id']}' {v['duration_s']}s · ~${cost:.2f} USD · "
            f"Dinero IA objeto/personaje en movimiento")
    try:
        with EXPENSES.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print("EXPENSE log warn:", e)


def _load_shots(path: str) -> list[dict]:
    raw = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return raw["shots"] if isinstance(raw, dict) and "shots" in raw else raw


def _print_providers():
    print("Rate-cards i2v (VERIFICAR en vivo antes de LIVE; precios decaen):\n")
    for name, p in PROVIDERS.items():
        star = " (default)" if name == DEFAULT_PROVIDER else ""
        ver = p["verificado"] or "SIN VERIFICAR"
        print(f"  {name}{star}")
        print(f"    ${p['usd_per_s']}/s · {p['min_s']}-{p['max_s']}s @ {p['fps']}fps"
              f" · motion_brush={p['supports_motion_brush']} · {ver}")
        print(f"    endpoint: {p['fal_endpoint']}")
        print(f"    {p['note']}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cmd = sys.argv[1]
    if cmd == "providers":
        _print_providers()
    elif cmd == "plan":
        if len(sys.argv) < 3:
            raise SystemExit("uso: python i2v_engine.py plan <shots.json> [--no-placeholder]")
        shots = _load_shots(sys.argv[2])
        plan(shots, render_placeholder="--no-placeholder" not in sys.argv)
    elif cmd == "submit":
        if len(sys.argv) < 3:
            raise SystemExit("uso: python i2v_engine.py submit <shots.json> --live")
        shots = _load_shots(sys.argv[2])
        submit(shots, live="--live" in sys.argv)
    else:
        raise SystemExit(f"comando desconocido '{cmd}' (providers|plan|submit)")
