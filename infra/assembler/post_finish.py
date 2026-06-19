# -*- coding: utf-8 -*-
"""
post_finish.py  --  Capa de ACABADO filmico (Track A5): bloom + grano + vineta.

$0 y SIN dependencia nueva: filtros NATIVOS de FFmpeg (ya es el ensamblador del
pipeline), NO Natron. Misma logica con la que A4 rechazo el addon BlenderDataVis:
cero herramienta extra que instalar/mantener, y el acabado se aplica UNA sola vez
sobre el master -> consistente en TODOS los beats y en las costuras de xfade (no
por-beat, donde cada toma quedaria con un grano/glow distinto). Si en R1 Manuel
quiere mas control, Natron queda como upgrade opcional, no como dependencia.

Dos formas de uso:

  1) Inyeccion (lo que hace build916): importar `finish_chain()` -> devuelve un
     string de filtros FFmpeg que se mete en el grafo de video ANTES del fade
     final. CERO pase extra de re-encode: son nodos mas en el mismo filter_complex
     que ya produce el master. Se activa SOLO si el guion trae un bloque "finish";
     sin el, el grafo queda IDENTICO al de hoy (no toca lo ya aprobado).

  2) Standalone (tuneo al ojo de Manuel en R1, A/B sin tocar el pipeline):
       python post_finish.py IN.mp4 OUT.mp4 [--bloom .18] [--grain 9]
              [--vignette .3] [--bloom-thr .62] [--bloom-sigma 16]
     re-encoda IN.mp4 con el acabado y copia el audio tal cual.

Filmico, NO videojuego: bloom sutil SOLO en altas luces (no halo global), grano
TEMPORAL fino (vida, no ruido fijo), vineta suave que centra el ojo en 9:16.
Defaults conservadores; Manuel sube/baja en R1.

NO renderiza al importarse; este archivo solo construye el grafo.
"""
import os
import subprocess
import sys

FFMPEG = os.environ.get("FFMPEG_BIN") or r"C:\Users\manup\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG):
    FFMPEG = "ffmpeg"

# Defaults conservadores (filmico, sutil). El guion los sobreescribe con su
# bloque "finish": {...}; el standalone con flags. 0 en bloom/grain/vignette
# APAGA esa etapa.
DEFAULTS = {
    "bloom": 0.18,      # opacidad del screen-blend del glow (0 = apagado)
    "bloom_thr": 0.62,  # umbral de altas luces (0..1) que brillan
    "bloom_sigma": 16,  # radio del desenfoque del glow (px @1080 de ancho)
    "grain": 9.0,       # amplitud del grano temporal (0 = apagado; ~6-14 filmico)
    "vignette": 0.30,   # fuerza de la vineta 0..1 (0 = apagada)
}

_STAGES = ("bloom", "vignette", "grain")  # orden de aplicacion (grano al final)


def _clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def finish_chain(src="[vin]", dst="[vout]", **kw):
    """Construye el sub-grafo de acabado de `src` a `dst`.

    Devuelve un string de filtros (segmentos separados por ';') listo para
    concatenar al filter_complex del master. Si todo viene apagado, es un
    passthrough (`null`). No ejecuta FFmpeg.
    """
    p = dict(DEFAULTS)
    for k, v in kw.items():
        if k in p and v is not None:
            p[k] = float(v)

    active = [s for s in _STAGES if p[s] > 0]
    if not active:
        return f"{src}null{dst}"

    segs, cur = [], src
    for i, stage in enumerate(active):
        out = dst if i == len(active) - 1 else f"[fx{i}]"
        if stage == "bloom":
            # aisla altas luces SOLO en luma (conserva el color del highlight),
            # las desenfoca y las screen-blendea de vuelta -> halacion sutil.
            thr = int(round(_clamp01(p["bloom_thr"]) * 255))
            segs.append(f"{cur}split[fxbb{i}][fxbh{i}]")
            segs.append(f"[fxbh{i}]lutyuv=y='if(gt(val,{thr}),val,0)',"
                        f"gblur=sigma={p['bloom_sigma']:g}[fxbg{i}]")
            segs.append(f"[fxbb{i}][fxbg{i}]blend=all_mode=screen:"
                        f"all_opacity={_clamp01(p['bloom']):.3f}{out}")
        elif stage == "vignette":
            # 0..1 -> angulo 0..1.4 rad; mas angulo = esquinas mas oscuras.
            ang = _clamp01(p["vignette"]) * 1.4
            segs.append(f"{cur}vignette=angle={ang:.4f}{out}")
        else:  # grain
            # temporal (allf=t): cambia cada frame -> se lee como grano de pelicula.
            segs.append(f"{cur}noise=alls={int(round(p['grain']))}:allf=t{out}")
        cur = out
    return ";".join(segs)


# ----------------------------------------------------------------- standalone
def main():
    pos, kw, it = [], {}, iter(sys.argv[1:])
    for tok in it:
        if tok.startswith("--"):
            kw[tok[2:].replace("-", "_")] = next(it, None)
        else:
            pos.append(tok)
    if len(pos) < 2:
        print("uso: python post_finish.py IN.mp4 OUT.mp4 "
              "[--bloom .18] [--grain 9] [--vignette .3] "
              "[--bloom-thr .62] [--bloom-sigma 16]")
        sys.exit(1)
    src, dst = pos[0], pos[1]
    fc = finish_chain("[0:v]", "[v]", **kw)
    cmd = [FFMPEG, "-y", "-i", src, "-filter_complex", fc,
           "-map", "[v]", "-map", "0:a?", "-c:a", "copy",
           "-c:v", "libx264", "-preset", "slow", "-crf", "15",
           "-pix_fmt", "yuv420p", dst]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG FAIL\n", (r.stderr or "")[-2000:]); sys.exit(1)
    print("[ok] acabado ->", dst)


if __name__ == "__main__":
    main()
