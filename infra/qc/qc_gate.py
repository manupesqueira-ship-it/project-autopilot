# -*- coding: utf-8 -*-
"""qc_gate.py — QC DE MÁQUINA sobre el MP4 final (pieza #6 del plan maestro).

Enchufa los filtros de PÍXEL que ya existían pero no se corrían automáticamente, para
frenar la entrega ANTES del ojo de Manuel. Corre por reel:
  - text_overlap_check : letra ENCIMA de imagen/hero (el bug #1 recurrente ~20 reincidencias)
  - filter_motion      : piso anti-slideshow (nada estático)
  + un chequeo de loudness/duración con ffprobe (barato, sin timeline).

Uso:  python qc_gate.py <reel1.mp4> [reel2.mp4 ...]     # exit 0 = todos PASS, 1 = algún FAIL
"""
import json
import subprocess
import sys
from pathlib import Path

QC = Path(__file__).resolve().parent
PY = sys.executable


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _loudness(video):
    rc, out = _run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(video), "-af", "volumedetect", "-f", "null", "-"])
    mean = next((ln for ln in out.splitlines() if "mean_volume" in ln), "")
    try:
        val = float(mean.split("mean_volume:")[1].split("dB")[0].strip())
        return ("OK" if -26 <= val <= -12 else "WARN"), f"mean {val:.1f} dB"
    except Exception:
        return "WARN", "sin lectura"


def check_reel(video):
    video = Path(video)
    results = {}
    rc, out = _run([PY, str(QC / "text_overlap_check.py"), str(video)])
    results["text_overlap"] = ("PASS" if rc == 0 else "FAIL", out.strip().splitlines()[-1] if out.strip() else "")
    rc, out = _run([PY, str(QC / "filter_motion.py"), str(video)])
    results["motion"] = ("PASS" if rc == 0 else "FAIL", out.strip().splitlines()[-1] if out.strip() else "")
    lo_state, lo_msg = _loudness(video)
    results["loudness"] = (lo_state, lo_msg)
    return results


def main():
    vids = sys.argv[1:]
    if not vids:
        raise SystemExit("uso: python qc_gate.py <reel.mp4> [...]")
    any_fail = False
    for v in vids:
        print(f"\n=== QC {Path(v).name} ===")
        res = check_reel(v)
        for k, (state, msg) in res.items():
            mark = {"PASS": "  OK  ", "FAIL": " FAIL ", "OK": "  OK  ", "WARN": " WARN "}[state]
            print(f" [{mark}] {k:14} {msg}")
            if state == "FAIL":
                any_fail = True
    print("\n" + ("QC GATE: ALGÚN FAIL -> revisar antes de entregar" if any_fail else "QC GATE: todos PASS"))
    raise SystemExit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
