# -*- coding: utf-8 -*-
"""Filtro D — el gate "el render ES el tratamiento" (auditoría 2026-07-03, salto #8).

La auditoría encontró que el clímax de un tratamiento se TIRÓ en el render y nadie
lo atrapó (arco roto), que una cifra se spoileaba 3-4s antes de la voz (land muerto)
y reels que abrían en un frame casi vacío. Este gate compara el MP4 FINAL contra el
TRATAMIENTO del director de forma DETERMINISTA (sin LLM) y truena el pipeline si el
render no cuenta la historia que el director diseñó.

Checks (exit 1 = NO entregar):
  D1 arco       : mismos beats, mismo orden, mismos tipos (tratamiento vs reel_props).
  D2 duración   : dur(MP4) == timeline compilado (sum durF - overlaps) ± TOL_S.
  D3 anclas     : todo beat con target_word tiene land y 0<=land<durF (la cifra
                  aterriza DENTRO de su beat, con la voz — no spoiler, no fuera).
  D4 frame0     : el primer frame está VIVO (stddev de luminancia > piso, no abre
                  en negro/vacío).
  D5 voz        : hay VO generada para CADA beat del tratamiento (words.json).

Uso:  python filter_d.py <final.mp4> <treatment.json> <out_dir>
      (out_dir = carpeta del slug con reel_props.json y vo/words.json)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

FPS = 30
TOL_S = 0.75            # tolerancia mux/encode sobre la duración esperada
# D4 calibrado contra el golden nvidia_v2 (2026-07-03): f0 std=5.6 (bg+masthead),
# t=0.9s std=19.6 (hook en pantalla). Negro plano ~0-2. Piso con margen:
MIN_F0_STD = 3.0        # frame 0: no abre en negro absoluto
MIN_HOOK_STD = 10.0     # t=0.9s: el hook YA debe estar en pantalla
HOOK_T = 0.9
MIN_LAND = 8            # un land antes de esto = la cifra ya estaba spoileada


def _ff(bin_name: str) -> str:
    import os
    env = os.environ.get(f"{bin_name.upper()}_BIN")
    if env and os.path.exists(env):
        return env
    guess = (r"C:\Users\manup\AppData\Local\Microsoft\WinGet\Packages"
             r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
             rf"\ffmpeg-8.1.1-full_build\bin\{bin_name}.exe")
    return guess if os.path.exists(guess) else bin_name


FFMPEG = _ff("ffmpeg")
FFPROBE = _ff("ffprobe")


def _duration(path: str) -> float:
    out = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", path],
        capture_output=True, text=True, check=True)
    return float(json.loads(out.stdout)["format"]["duration"])


def _frame_std(path: str, at_s: float = 0.0) -> float:
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "f.png"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{at_s:.2f}", "-i", path,
                        "-vf", "scale=270:480", "-vframes", "1", str(png)],
                       check=True)
        arr = np.asarray(Image.open(png).convert("L"), dtype=np.float32)
    return float(arr.std())


def gate(final: Path, treatment: Path, out_dir: Path) -> dict:
    issues = []
    tr = json.loads(treatment.read_text(encoding="utf-8-sig"))
    t_beats = tr["beats"]

    props_p = out_dir / "reel_props.json"
    words_p = out_dir / "vo" / "words.json"
    if not props_p.exists():
        return {"pass": False, "issues": [f"falta {props_p.name} (¿pipeline viejo?)"]}
    specs = json.loads(props_p.read_text(encoding="utf-8-sig"))["beats"]

    # D1 — arco completo: ningún beat del tratamiento se tira ni se reordena
    if len(specs) != len(t_beats):
        issues.append(f"D1 arco: tratamiento tiene {len(t_beats)} beats, render {len(specs)} — se PERDIÓ parte de la historia")
    else:
        for i, (tb, sp) in enumerate(zip(t_beats, specs)):
            if tb["type"] != sp["type"]:
                issues.append(f"D1 arco: b{i} tratamiento={tb['type']} vs render={sp['type']}")

    # D2 — duración del MP4 == timeline compilado
    total_f = 0.0
    for i, sp in enumerate(specs):
        total_f += sp["durF"]
        if i < len(specs) - 1 and sp.get("trans", "cut") != "cut":
            total_f -= sp.get("transF", 10)
    expected = total_f / FPS
    actual = _duration(str(final))
    if abs(actual - expected) > TOL_S:
        issues.append(f"D2 duración: esperado {expected:.2f}s vs MP4 {actual:.2f}s (±{TOL_S}) — render truncado o timeline roto")

    # D3 — anclas: la cifra aterriza dentro de su beat y no antes de tiempo
    for i, (tb, sp) in enumerate(zip(t_beats, specs)):
        if tb.get("target_word"):
            land = sp.get("props", {}).get("land")
            if land is None:
                issues.append(f"D3 ancla: b{i} ({tb['type']}) tiene target_word '{tb['target_word']}' pero el render no lleva land")
            elif not (MIN_LAND <= land < sp["durF"]):
                issues.append(f"D3 ancla: b{i} land={land} fuera de [{MIN_LAND},{sp['durF']}) — cifra spoileada o fuera del beat")

    # D4 — apertura viva: frame 0 no-negro + hook en pantalla a los 0.9s
    std0 = _frame_std(str(final), 0.0)
    if std0 < MIN_F0_STD:
        issues.append(f"D4 frame0: stddev {std0:.1f} < {MIN_F0_STD} — el reel abre en un cuadro vacío/negro")
    std_hook = _frame_std(str(final), HOOK_T)
    if std_hook < MIN_HOOK_STD:
        issues.append(f"D4 hook: stddev {std_hook:.1f} < {MIN_HOOK_STD} a t={HOOK_T}s — el hook no está en pantalla")

    # D5 — VO por beat
    if words_p.exists():
        vo = json.loads(words_p.read_text(encoding="utf-8-sig"))
        if len(vo) != len(t_beats):
            issues.append(f"D5 voz: {len(vo)} segmentos de VO para {len(t_beats)} beats")
        else:
            for seg in vo:
                if seg.get("dur", 0) < 0.4:
                    issues.append(f"D5 voz: segmento b{seg.get('i')} dura {seg.get('dur')}s (muerto)")
    else:
        issues.append("D5 voz: falta vo/words.json")

    return {"pass": not issues, "issues": issues,
            "expected_s": round(expected, 2), "actual_s": round(actual, 2),
            "frame0_std": round(std0, 1), "hook_std": round(std_hook, 1), "beats": len(t_beats)}


def main() -> int:
    if len(sys.argv) != 4:
        print("uso: python filter_d.py <final.mp4> <treatment.json> <out_dir>")
        return 2
    final, treatment, out_dir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    r = gate(final, treatment, out_dir)
    tag = "PASS" if r["pass"] else "FAIL"
    extra = "" if r["pass"] else " | " + "; ".join(r["issues"])
    print(f"[{tag}] filter_d {final.name} (beats={r.get('beats')}, "
          f"dur {r.get('actual_s')}s/{r.get('expected_s')}s, f0std={r.get('frame0_std')}){extra}")
    return 0 if r["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
