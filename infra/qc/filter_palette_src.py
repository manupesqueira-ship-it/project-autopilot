"""filter_palette_src.py — linter de paleta a NIVEL DE FUENTE.

filter_a.py atrapa color fuera de paleta en PIXELES del render final, pero solo
si el color llega a ser visualmente prominente en el frame muestreado. Un color
categorico mal puesto (azul/morado) en un slot poco visible se le escapa: asi
nacio el falso "25/25 PASS" (un #5B8DEF en una tarjeta chica nunca disparo
filter_a). Este linter lee el CODIGO de los beats y reprueba cualquier hex
CROMATICO cuyo tono caiga fuera de las bandas permitidas, ANTES de renderizar.
Mismos thresholds que filter_a (SAT_MIN / VAL_MIN / ALLOWED_HUES).

El ROJO es un tono PERMITIDO aqui, igual que en filter_a (hue ~0). La regla
"rojo = SOLO perdida" es SEMANTICA y la valida validator.py (R-color): un linter
de color no puede saber si un rojo codifica una perdida o es decorativo.

Escapes (para color intencional, p.ej. el color REAL de una marca):
  - `// palette-ok: <razon>`        en la MISMA linea -> ignora esa linea
  - `// palette-ok-start` / `-end`  envuelve un bloque (p.ej. un logo SVG)
  - `// palette-ok-file`            en cualquier parte -> ignora el archivo entero

Uso:   python filter_palette_src.py [dir]   (default: ../remotion-render/src)
Exit:  0 = limpio, 1 = hay color fuera de paleta, 2 = dir invalido.
"""

import colorsys
import re
import sys
from pathlib import Path

# espejo EXACTO de filter_a.py
SAT_MIN = 0.35
VAL_MIN = 0.45
ALLOWED_HUES = [(148, 195), (20, 48), (348, 360), (0, 12)]

HEX_RE = re.compile(r"#([0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")
OK_MARK = "palette-ok"


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    h = h[:6]  # ignora el alpha de un hex de 8 digitos
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def hue_allowed(deg: float) -> bool:
    return any(lo <= deg <= hi for lo, hi in ALLOWED_HUES)


def offenders_in_line(line: str):
    out = []
    for m in HEX_RE.finditer(line):
        r, g, b = hex_to_rgb(m.group(1))
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s < SAT_MIN or v < VAL_MIN:
            continue  # gris / estructural / oscuro -> no es color categorico
        if hue_allowed(h * 360):
            continue
        out.append((m.group(0), round(h * 360)))
    return out


def scan(root: Path):
    violations = []
    for f in sorted(root.rglob("*.tsx")):
        text = f.read_text(encoding="utf-8")
        if "palette-ok-file" in text:
            continue
        in_block = False
        for n, line in enumerate(text.splitlines(), 1):
            if "palette-ok-start" in line:
                in_block = True
                continue
            if "palette-ok-end" in line:
                in_block = False
                continue
            if in_block or OK_MARK in line:
                continue
            for hexv, deg in offenders_in_line(line):
                violations.append((f, n, hexv, deg, line.strip()))
    return violations


def main(argv) -> int:
    root = (
        Path(argv[0])
        if argv
        else Path(__file__).resolve().parents[1] / "remotion-render" / "src"
    )
    if not root.exists():
        print(f"no existe: {root}")
        return 2
    viols = scan(root)
    for f, n, hexv, deg, src in viols:
        print(f"[FAIL] {f.name}:{n}  {hexv} (hue {deg}deg fuera de paleta) — {src}")
    if viols:
        print(
            f"\n{len(viols)} color(es) fuera de paleta. Bandas: verde-teal 148-195, "
            f"oro 20-48, rojo 348-12 (el rojo solo-perdida lo valida validator.py)."
        )
        return 1
    print("paleta OK — ningun hex cromatico fuera de banda en el catalogo.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
