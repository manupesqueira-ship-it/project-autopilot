# -*- coding: utf-8 -*-
"""
chart3d.py  --  Graficas 3D con VOLUMEN real (Dinero IA, Track A4).

Barras con cuerpo 3D de verdad (no el slab 2.5D de BarsValue.tsx): cubos
biselados, altura proporcional al dato, materiales PBR de la paleta SEMANTICA,
sobre el template premium (studio_premium.py) -> HDRI + DoF + motion blur. Las
barras CRECEN en el render (animacion de escala escalonada), igual que la grafica
Remotion, para que la toma no sea estatica.

Por que propio y no el addon BlenderDataVis: el sistema es 100% nuestro y $0, sin
dependencias externas que instalar/mantener; estas barras heredan EXACTO el look
del resto de beats 3D (mismo studio_premium). El addon queda como referencia, no
como dependencia.

Datos: misma forma que BarsValue.tsx -> {label, value, highlight?, color?}. Se
pasa un JSON con --data; si no, usa un demo. Las etiquetas (valor arriba,
categoria abajo) se HORNEAN como texto 3D extruido: Blender dibuja glifos exactos
de la fuente (a diferencia de gpt-image, que escribe mal las cifras), asi que la
toma es legible por si sola para el juicio de R1. Con --no-labels se apagan y el
dato lo pone Remotion en overlay (arquitectura objeto-3D + datos-encima).

Paleta SEMANTICA (Style Bible §3, locked): verde sube/marca, rojo SOLO perdida,
teal neutral, oro dinero. sRGB -> linear para que el color pegue en Cycles.

NO renderiza ahora; se ESCRIBE. Render en el lote final (R1):
    cd infra/blender
    blender --background --python chart3d.py -- --out out_chart --prefix bar_ [--data c.json]
    python encode_host.py     # (ajustar glob a bar_*.png)

Salida: out_chart/bar_#####.png (RGBA transparente, 70 frames @30fps).
"""
import json
import math
import os
import sys

import bpy  # noqa: E402  (solo dentro de Blender)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import studio_premium as sp  # noqa: E402

FRAMES = 70  # ~2.3s @30fps: arranque + crecimiento escalonado + asiento


# --------------------------------------------------------- color (sRGB->linear)
def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h, a=1.0):
    """'#00D9A5' -> (r,g,b,a) en espacio LINEAL (lo que espera el Principled)."""
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (_srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b), a)


# paleta semantica locked (Style Bible §3 / theme.ts / CLAUDE.md)
PALETTE = {
    "green": "#00D9A5",   # sube / seguro / marca
    "red": "#FF6B6B",     # SOLO perdida
    "teal": "#5BC0BE",    # neutral
    "gold": "#D4A574",    # dinero
}


def _bar_material(name, color_key, highlight):
    """Barra destacada = emisiva (brilla, atrae el ojo); resto = metal de paleta."""
    col = hex_lin(PALETTE.get(color_key, PALETTE["teal"]))
    if highlight:
        return sp.pbr_emission(name, col, strength=3.2)
    return sp.pbr_metal(name, col, rough=0.30, coat=0.5)


# --------------------------------------------------------------- construccion
def build_chart(spec, labels=True):
    bars = spec.get("bars", [])
    if not bars:
        raise SystemExit("chart3d: spec sin 'bars'")
    prefix = spec.get("prefix", "")
    suffix = spec.get("suffix", "")
    vmax = max((b.get("value", 0) for b in bars), default=1) or 1

    n = len(bars)
    step = 1.55
    width, depth = step * 0.58, step * 0.58
    max_h, stub = 3.2, 0.06
    x0 = -(n - 1) * step / 2.0

    dark = sp.pbr_plastic("Floor", (0.02, 0.025, 0.03, 1.0), rough=0.12, coat=0.6)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    bpy.context.active_object.data.materials.append(dark)

    grow_span = 10  # frames que tarda en crecer cada barra
    for i, b in enumerate(bars):
        val = b.get("value", 0)
        hl = bool(b.get("highlight"))
        color_key = b.get("color") or ("green" if hl else "teal")
        h = max(val / vmax * max_h, stub)
        x = x0 + i * step

        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0))
        bar = bpy.context.active_object
        bar.name = f"bar_{i}"
        bar.scale = (width, depth, 1.0)
        bev = bar.modifiers.new("Bevel", "BEVEL")
        bev.width = 0.02
        bev.segments = 3
        bpy.ops.object.shade_smooth()
        bar.data.materials.append(_bar_material(f"BarMat_{i}", color_key, hl))

        # crece desde el piso: escala Z 0->h y sube z de 0->h/2 en sincronia,
        # escalonado por barra (mismo gesto que el grow de BarsValue).
        start = 8 + i * 6
        end = start + grow_span
        for f, sz in ((start, 0.001), (end, h)):
            bar.scale.z = sz
            bar.location.z = sz / 2.0
            bar.keyframe_insert("scale", index=2, frame=f)
            bar.keyframe_insert("location", index=2, frame=f)

        if labels:
            white = sp.pbr_plastic(f"Lbl_{i}", (0.9, 0.93, 0.95, 1.0), rough=0.4)
            txt = f"{prefix}{val:,}{suffix}" if isinstance(val, (int, float)) else str(val)
            lbl = sp.extruded_text(
                txt, size=0.34, extrude=0.04, bevel=0.006, material=white,
                location=(x, 0, h + 0.45), rotation=(math.radians(90), 0, 0),
                name=f"val_{i}")
            # la etiqueta aparece cuando la barra termina de crecer
            lbl.keyframe_insert("scale", frame=1)
            lbl.scale = (0.001, 0.001, 0.001)
            lbl.keyframe_insert("scale", frame=end)
            lbl.scale = (1, 1, 1)
            lbl.keyframe_insert("scale", frame=end + 6)

            cat = sp.pbr_plastic(f"Cat_{i}", (0.62, 0.66, 0.72, 1.0), rough=0.5)
            sp.extruded_text(
                b.get("label", ""), size=0.24, extrude=0.02, bevel=0.004,
                material=cat, location=(x, 0, -0.55),
                rotation=(math.radians(90), 0, 0), name=f"cat_{i}")

    return n, max_h


# ----------------------------------------------------------------------- main
def _load_spec():
    argv = sys.argv
    args = argv[argv.index("--") + 1:] if "--" in argv else []
    if "--data" in args:
        path = args[args.index("--data") + 1]
        return json.loads(open(path, encoding="utf-8-sig").read()), ("--no-labels" not in args)
    # demo (capacidad nueva, no el beat CETES quemado): tasas reales de cuentas
    demo = {
        "caption": "rendimiento anual", "prefix": "", "suffix": "%",
        "bars": [
            {"label": "banco", "value": 1},
            {"label": "pagares", "value": 7},
            {"label": "CETES", "value": 10},
            {"label": "este fondo", "value": 14, "highlight": True},
        ],
    }
    return demo, ("--no-labels" not in args)


def main():
    spec, labels = _load_spec()
    scene = sp.fresh_scene()
    sp.setup_render(scene, res=1080, samples=180, fps=30, motion_blur=True)
    sp.world_studio(scene, strength=1.0)
    out_dir, prefix = sp.parse_out_arg("out_chart", "bar_")
    sp.set_output(scene, out_dir, prefix, frame_start=1, frame_end=FRAMES)

    n, max_h = build_chart(spec, labels=labels)

    # camara 3/4 que abarca la fila; enfoca el centro (DoF suaviza extremos)
    span = max(n * 1.7, 4.0)
    sp.add_camera(scene, location=(span * 0.55, -span * 1.15, max_h * 1.25),
                  look_at=(0, 0, max_h * 0.4), lens=62, dof=True, fstop=3.2)
    sp.studio_lights(scene, target_loc=(0, 0, max_h * 0.4))
    sp.render(scene, animation=True)


if __name__ == "__main__":
    main()
