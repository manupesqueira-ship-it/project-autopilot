"""Filtro A aplicado a STILLS (PNG) de beats sueltos.

filter_a.py ingiere VIDEO (necesita format.duration + motion entre frames). Un
still no tiene duracion ni movimiento, asi que aqui reusamos EXACTAMENTE los
checks estaticos de filter_a (misma logica y thresholds) sobre cada PNG:
  - palette    : hues saturados dentro de paleta verde/oro/rojo/cyan
  - luminance  : fondo oscuro pero no negro vacio
  - safe_areas : franja superior (11%) e inferior (17%) sin contenido brillante

El check de motion NO aplica a un frame estatico (cada beat lleva micro-motion
sin() por diseno; eso se valida con filter_a.py sobre el video ensamblado).

Uso:
    python filter_a_stills.py <dir_o_pngs...> [--json out.json]
Exit 0 = todos PASS, 1 = algun FAIL.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# reusar la logica exacta de filter_a (mismos thresholds)
from filter_a import check_palette, check_luminance, check_safe_areas

# Beats cuyo color saturado lo dominan ASSETS DEL MUNDO REAL: logos de marca
# (simple-icons via BrandLogo: el azul/verde/amarillo de Microsoft, el azul de
# Visa/PayPal...) y banderas nacionales (country-flag-icons: el azul cobalto de
# la bandera de El Salvador). Su paleta NO se "corrige": recolorear el logo de
# Microsoft o una bandera seria incorrecto y rompe el reconocimiento. Para estos
# beats el check de paleta se REPORTA (queda visible el ratio) pero NO bloquea;
# safe-areas y luminance siguen aplicando normal.
PALETTE_EXEMPT = {"BeatLogoWall", "BeatMapZoom"}


def load_frame(png: Path) -> np.ndarray:
    # filter_a samplea a 270x480; replicamos esa escala para que las coords de
    # safe-area (gray[:int(480*0.11)] etc.) coincidan.
    img = Image.open(png).convert("RGB").resize((270, 480), Image.BILINEAR)
    return np.asarray(img, dtype=np.float32)


def run_one(png: Path) -> dict:
    # check_safe_areas exige que el contenido brillante PERSISTA >=2 frames
    # (top_run>=2) para no marcar un whip de transicion. Un still es 1 frame, asi
    # que SIN duplicar el run nunca llega a 2 -> safe_areas SIEMPRE pasaba (no-op).
    # Un still = un frame "sostenido"; duplicarlo simula esa persistencia real.
    # No afecta palette/luminance (2 frames identicos dan el mismo veredicto).
    f = load_frame(png)
    frames = [f, f]
    palette = check_palette(frames)
    exempt = png.stem in PALETTE_EXEMPT
    palette["exempt"] = exempt
    report = {
        "still": png.name,
        "palette": palette,
        "luminance": check_luminance(frames),
        "safe_areas": check_safe_areas(frames),
    }
    # un beat exento (logos/banderas reales) no falla por paleta, pero SI sigue
    # sujeto a safe-areas y luminance.
    checks = ["luminance", "safe_areas"] + ([] if exempt else ["palette"])
    report["overall"] = "PASS" if all(report[k]["pass"] for k in checks) else "FAIL"
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args()

    pngs: list[Path] = []
    for p in args.paths:
        pp = Path(p)
        if pp.is_dir():
            pngs.extend(sorted(pp.glob("*.png")))
        elif pp.suffix.lower() == ".png":
            pngs.append(pp)

    reports = [run_one(p) for p in pngs if not p.name.startswith("_")]
    all_pass = all(r["overall"] == "PASS" for r in reports)

    for r in reports:
        flag = "PASS" if r["overall"] == "PASS" else "FAIL"
        extra = []
        for k in ("palette", "luminance", "safe_areas"):
            if k == "palette" and r[k].get("exempt"):
                ratio = r[k].get("worst_offpalette_ratio", 0.0)
                extra.append(
                    f"paleta exenta: imagen real (logo/bandera), {ratio:.0%} off-palette"
                )
                continue
            extra.extend(r[k].get("issues", []))
        detail = (" — " + "; ".join(extra)) if extra else ""
        print(f"[{flag}] {r['still']}{detail}")

    print(f"\n{sum(r['overall']=='PASS' for r in reports)}/{len(reports)} PASS")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
