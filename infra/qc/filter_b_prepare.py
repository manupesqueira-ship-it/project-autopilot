"""Filtro B (preparacion) — arma los paneles candidato|referencia para el juez visual.

Uso:
    python filter_b_prepare.py candidato.mp4 referencia.png salida_dir [--pcts 30,60,85]

Genera en salida_dir:
    panel_XX.png   side-by-side (candidato al XX% de duracion | referencia), misma altura
    rubric.md      rubrica 1-10 que el juez (LLM con vision) aplica a cada panel

El juez aprueba con promedio >= 8 y ninguna dimension < 6.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

RUBRIC = """# Rubrica Filtro B — juez visual (1-10 por dimension)

Compara el lado IZQUIERDO (candidato) contra el DERECHO (referencia 0x100x).
No se exige identidad: se exige el MISMO nivel de oficio.

1. **Composicion / espacio negativo** — un sujeto dominante, aire alrededor,
   nada flotando sin proposito, safe areas respetadas.
2. **Jerarquia tipografica** — dato protagonista claramente mayor; caption
   secundario discreto; pesos correctos (cifras Black, soporte Medium).
3. **Paleta y semantica** — solo tokens del theme; verde=ganancia, rojo=perdida,
   oro=dinero; fondo #0D1117/gradiente, nunca negro vacio ni colores nuevos.
4. **Iluminacion / profundidad** — glow con nucleo caliente, spotlight de
   estudio, sensacion de escenario; no flat, no plano de PowerPoint.
5. **Acabado premium** — bordes limpios, gradientes suaves sin banding,
   nada pixelado, detalle fino (reflejos, grano sutil).

**Veredicto**: PASS si promedio >= 8 y ninguna dimension < 6.
Si FAIL: lista las correcciones concretas (que cambiar, donde, cuanto).
"""


def duration_of(video: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate")
    ap.add_argument("reference")
    ap.add_argument("outdir")
    ap.add_argument("--pcts", default="30,60,85")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    dur = duration_of(args.candidate)
    ref = Image.open(args.reference).convert("RGB")

    panels = []
    for pct in [int(p) for p in args.pcts.split(",")]:
        ts = dur * pct / 100
        frame_path = outdir / f"cand_{pct:02d}.png"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ts:.3f}",
             "-i", args.candidate, "-frames:v", "1", str(frame_path)],
            check=True,
        )
        cand = Image.open(frame_path).convert("RGB")

        h = 960
        cw = int(cand.width * h / cand.height)
        rw = int(ref.width * h / ref.height)
        panel = Image.new("RGB", (cw + rw + 16, h), (20, 20, 20))
        panel.paste(cand.resize((cw, h)), (0, 0))
        panel.paste(ref.resize((rw, h)), (cw + 16, 0))
        panel_path = outdir / f"panel_{pct:02d}.png"
        panel.save(panel_path)
        frame_path.unlink()
        panels.append(str(panel_path))

    (outdir / "rubric.md").write_text(RUBRIC, encoding="utf-8")
    print(json.dumps({"panels": panels, "rubric": str(outdir / "rubric.md")},
                     indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
