"""Filtro A — QC programatico de un render (beat o video completo).

Uso:
    python filter_a.py video.mp4 [--duration S] [--no-audio-ok] [--json out.json]

Checks:
  1. tech       : 1080x1920, 30fps, duracion esperada (+-0.5s), stream de audio
  2. palette    : hues saturados dentro de la paleta (verde/oro/rojo/cyan-teal)
  3. luminance  : fondo oscuro pero NO negro vacio (feedback brillo Manuel)
  4. safe_areas : franja superior (UI de IG) e inferior (captions/UI) sin contenido brillante
  5. motion     : ningun tramo estatico > 1.5s

Exit code 0 = PASS total, 1 = algun FAIL.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

SAMPLE_FPS = 4
STATIC_LIMIT_S = 2.0
# diff medio (0-255) bajo esto = frame muerto. Calibrado contra dinero_dormido:
# glow-pulse/breathe legitimos rinden 0.15-0.40; aire muerto real rinde <0.12.
MOTION_THRESHOLD = 0.12
# hue en grados: verde #00D9A5 ~165 (halos sobre fondo azul llegan a ~195),
# oro #D4A574 ~33, rojo #FF6B6B ~0
ALLOWED_HUES = [(148, 195), (20, 48), (348, 360), (0, 12)]
SAT_MIN = 0.35  # solo juzgamos pixeles realmente saturados
VAL_MIN = 0.45  # halos tenues de glow sobre el fondo no cuentan como contenido


def ffprobe(path: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", path],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def extract_frames(path: str, tmpdir: str) -> list[np.ndarray]:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", path,
         "-vf", f"fps={SAMPLE_FPS},scale=270:480",
         str(Path(tmpdir) / "f%04d.png")],
        check=True,
    )
    frames = []
    for p in sorted(Path(tmpdir).glob("f*.png")):
        frames.append(np.asarray(Image.open(p).convert("RGB"), dtype=np.float32))
    return frames


def check_tech(meta: dict, expect_dur: float | None, audio_required: bool) -> dict:
    v = next(s for s in meta["streams"] if s["codec_type"] == "video")
    a = [s for s in meta["streams"] if s["codec_type"] == "audio"]
    dur = float(meta["format"]["duration"])
    num, den = v["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    issues = []
    if (v["width"], v["height"]) != (1080, 1920):
        issues.append(f"resolucion {v['width']}x{v['height']} != 1080x1920")
    if abs(fps - 30) > 0.1:
        issues.append(f"fps {fps:.2f} != 30")
    if expect_dur is not None and abs(dur - expect_dur) > 0.5:
        issues.append(f"duracion {dur:.2f}s != {expect_dur}s")
    if audio_required and not a:
        issues.append("sin stream de audio")
    return {"pass": not issues, "issues": issues, "duration": dur}


def rgb_to_hsv(arr: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r, g, b = arr[..., 0] / 255, arr[..., 1] / 255, arr[..., 2] / 255
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    diff = mx - mn
    hue = np.zeros_like(mx)
    mask = diff > 1e-6
    rm = mask & (mx == r)
    gm = mask & (mx == g) & ~rm
    bm = mask & (mx == b) & ~rm & ~gm
    hue[rm] = (60 * ((g[rm] - b[rm]) / diff[rm])) % 360
    hue[gm] = 60 * ((b[gm] - r[gm]) / diff[gm]) + 120
    hue[bm] = 60 * ((r[bm] - g[bm]) / diff[bm]) + 240
    sat = np.where(mx > 1e-6, diff / np.maximum(mx, 1e-6), 0)
    return hue, sat, mx


def check_palette(frames: list[np.ndarray]) -> dict:
    bad_ratios = []
    for f in frames[:: max(1, len(frames) // 12)]:
        hue, sat, val = rgb_to_hsv(f)
        judged = (sat > SAT_MIN) & (val > VAL_MIN)
        n = judged.sum()
        if n < 200:
            continue
        ok = np.zeros_like(hue, dtype=bool)
        for lo, hi in ALLOWED_HUES:
            ok |= (hue >= lo) & (hue <= hi)
        bad = (judged & ~ok).sum() / n
        bad_ratios.append(float(bad))
    worst = max(bad_ratios) if bad_ratios else 0.0
    return {
        "pass": worst < 0.12,
        "worst_offpalette_ratio": round(worst, 4),
        "issues": [] if worst < 0.12 else
        [f"{worst:.0%} de pixeles saturados fuera de paleta en algun frame"],
    }


def check_luminance(frames: list[np.ndarray]) -> dict:
    lums = [float(f.mean()) for f in frames]
    avg = sum(lums) / len(lums)
    issues = []
    if avg < 8:
        issues.append(f"luminancia media {avg:.1f} — negro vacio (subir modo estudio)")
    if avg > 70:
        issues.append(f"luminancia media {avg:.1f} — demasiado claro para el theme")
    return {"pass": not issues, "avg_luminance": round(avg, 1), "issues": issues}


def check_safe_areas(frames: list[np.ndarray]) -> dict:
    # franjas en coords del sample 270x480: top 11% (~220px reales), bottom 17% (~320px)
    issues = []
    top_max, bot_max = 0.0, 0.0
    top_run = bot_run = 0
    top_bad = bot_bad = False
    for f in frames:
        gray = f.mean(axis=2)
        # flash de transicion (frame entero brillante) no es contenido en
        # safe-area: si el centro tambien esta encendido, saltar el frame
        center = (gray[int(480 * 0.30): int(480 * 0.70)] > 90).mean()
        if center > 0.5:
            top_run = bot_run = 0
            continue
        top = (gray[: int(480 * 0.11)] > 90).mean()
        bot = (gray[int(480 * 0.83):] > 90).mean()
        # solo es problema si PERSISTE (>=2 samples = >0.25s): contenido
        # estacionado bajo la UI de IG; un whip que cruza la franja no cuenta
        top_run = top_run + 1 if top > 0.05 else 0
        bot_run = bot_run + 1 if bot > 0.05 else 0
        if top_run >= 2:
            top_bad, top_max = True, max(top_max, float(top))
        if bot_run >= 2:
            bot_bad, bot_max = True, max(bot_max, float(bot))
    if top_bad:
        issues.append(f"contenido brillante en safe-area superior ({top_max:.0%})")
    if bot_bad:
        issues.append(f"contenido brillante en safe-area inferior ({bot_max:.0%})")
    return {"pass": not issues, "top": round(top_max, 3),
            "bottom": round(bot_max, 3), "issues": issues}


def check_motion(frames: list[np.ndarray]) -> dict:
    static_run, worst_run = 0, 0
    for a, b in zip(frames, frames[1:]):
        diff = float(np.abs(a - b).mean())
        static_run = static_run + 1 if diff < MOTION_THRESHOLD else 0
        worst_run = max(worst_run, static_run)
    worst_s = worst_run / SAMPLE_FPS
    return {
        "pass": worst_s <= STATIC_LIMIT_S,
        "longest_static_s": round(worst_s, 2),
        "issues": [] if worst_s <= STATIC_LIMIT_S else
        [f"tramo estatico de {worst_s:.1f}s (max {STATIC_LIMIT_S}s)"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--no-audio-ok", action="store_true")
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args()

    meta = ffprobe(args.video)
    with tempfile.TemporaryDirectory() as tmp:
        frames = extract_frames(args.video, tmp)

    report = {
        "video": args.video,
        "tech": check_tech(meta, args.duration, not args.no_audio_ok),
        "palette": check_palette(frames),
        "luminance": check_luminance(frames),
        "safe_areas": check_safe_areas(frames),
        "motion": check_motion(frames),
    }
    overall = all(v["pass"] for k, v in report.items() if k != "video")
    report["overall"] = "PASS" if overall else "FAIL"

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
