"""Filtro C (preparacion) — QC del video COMPLETO ensamblado, antes del gate Manuel.

Uso:
    python filter_c_prepare.py video_final.mp4 salida_dir

Genera:
    sheet_NN.png   contact sheets (2 fps, tiles 6x5) de todo el video
    audio.json     loudness integrado (EBU R128), true peak, rango
    rubric.md      rubrica del juez de video completo

Ademas corre los checks programaticos del Filtro A (con audio obligatorio).
PASS programatico + juez >= 8 => se muestra a Manuel. Si no, NO se muestra.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from filter_a import check_luminance, check_motion, check_palette, check_safe_areas, check_tech, extract_frames, ffprobe  # noqa: E402

import tempfile  # noqa: E402

RUBRIC = """# Rubrica Filtro C — juez de video completo (1-10 por dimension)

Se juzga el video ENTERO via contact sheets + audio.json. Es el ultimo filtro
antes del gate humano: si hay duda, FAIL.

1. **Hook (0-2s)** — primer frame ya plantea tension/curiosidad; no arranca
   con pantalla vacia ni logo.
2. **Variedad de beats** — minimo 3 tipos distintos (numero, chart, pictograma,
   texto...); nunca dos beats identicos seguidos.
3. **Consistencia de diseño** — mismo theme en TODOS los beats: mismo fondo,
   misma tipografia, misma logica de color. Cero cambios de estilo entre escenas.
4. **Datos exactos y legibles** — toda cifra narrada aparece en pantalla,
   correcta y dominante; charts muestran EXACTAMENTE el dato del guion.
5. **Ritmo** — ningun beat se siente eterno ni cortado; transiciones limpias;
   el video completo < 60s.
6. **Audio** (de audio.json) — loudness integrado entre -16 y -12 LUFS,
   true peak <= -1 dBTP; musica no tapa la voz.
7. **Cierre** — CTA claro con open-loop para el siguiente video.

**Veredicto**: PASS si promedio >= 8 y ninguna dimension < 7.
Si FAIL: lista de correcciones por beat (numero de sheet + posicion).
"""


def audio_stats(video: str) -> dict:
    out = subprocess.run(
        ["ffmpeg", "-i", video, "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    txt = out.stderr
    stats = {}
    # ebur128 imprime lineas de progreso y un Summary al final: usar el ULTIMO match
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt)
    if m:
        stats["integrated_lufs"] = float(m[-1])
    m = re.findall(r"LRA:\s+(-?[\d.]+) LU", txt)
    if m:
        stats["loudness_range_lu"] = float(m[-1])
    m = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", txt)
    if m:
        stats["true_peak_dbfs"] = float(m[-1])
    lufs = stats.get("integrated_lufs")
    peak = stats.get("true_peak_dbfs")
    issues = []
    if lufs is None:
        issues.append("sin audio medible")
    else:
        if not (-16.5 <= lufs <= -11.5):
            issues.append(f"loudness {lufs} LUFS fuera de [-16, -12]")
        if peak is not None and peak > -0.9:
            issues.append(f"true peak {peak} dBTP > -1")
    stats["pass"] = not issues
    stats["issues"] = issues
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("outdir")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", args.video,
         "-vf", "fps=2,scale=200:-1,tile=6x5",
         str(outdir / "sheet_%02d.png")],
        check=True,
    )

    meta = ffprobe(args.video)
    with tempfile.TemporaryDirectory() as tmp:
        frames = extract_frames(args.video, tmp)
    prog = {
        "tech": check_tech(meta, None, audio_required=True),
        "palette": check_palette(frames),
        "luminance": check_luminance(frames),
        "safe_areas": check_safe_areas(frames),
        "motion": check_motion(frames),
        "audio": audio_stats(args.video),
    }
    prog["overall_programmatic"] = (
        "PASS" if all(v["pass"] for v in prog.values() if isinstance(v, dict))
        else "FAIL"
    )

    (outdir / "audio.json").write_text(
        json.dumps(prog["audio"], indent=2, ensure_ascii=False), encoding="utf-8")
    (outdir / "rubric.md").write_text(RUBRIC, encoding="utf-8")
    (outdir / "programmatic.json").write_text(
        json.dumps(prog, indent=2, ensure_ascii=False), encoding="utf-8")

    sheets = sorted(str(p) for p in outdir.glob("sheet_*.png"))
    print(json.dumps({"sheets": sheets, "programmatic": prog}, indent=2,
                     ensure_ascii=False))
    return 0 if prog["overall_programmatic"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
