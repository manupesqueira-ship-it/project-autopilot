# -*- coding: utf-8 -*-
"""QC OFFLINE de filter_a_stills: prueba que el fix del no-op de safe_areas
realmente ATRAPA contenido brillante en las franjas seguras.

check_safe_areas solo marca cuando la franja brillante PERSISTE (run>=2 frames).
Un still es 1 frame, asi que sin duplicarlo nunca llegaba a 2 y safe_areas pasaba
SIEMPRE (el falso "25/25 PASS"). El fix en filter_a_stills.run_one duplica el
still a [f, f]. Aqui medimos exactamente esa diferencia: 1 frame PASA (reproduce
el bug) y 2 frames REPRUEBAN (confirma el fix). Si alguien revierte el [f, f],
estos casos fallan.

    python test_filter_a_stills.py
No renderiza ni llama a ninguna API; genera stills sinteticos en memoria/temp.
"""
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from filter_a import check_safe_areas          # noqa: E402
from filter_a_stills import run_one             # noqa: E402

DARK = 17.0  # ~ luminancia del fondo del theme (#0D1117)


def _sampled(top=False, bot=False):
    """Frame ya en coords del sample de filter_a (270x480) con banda opcional."""
    f = np.full((480, 270, 3), DARK, dtype=np.float32)
    if top:
        f[: int(480 * 0.11), :, :] = 230.0   # franja superior 11%
    if bot:
        f[int(480 * 0.83):, :, :] = 230.0    # franja inferior 17%
    return f


def _png(path, top_band=False):
    """PNG a resolucion real (1080x1920): fondo dark + banda superior opcional."""
    img = np.full((1920, 1080, 3), (13, 17, 23), dtype=np.uint8)
    if top_band:
        img[:211, :, :] = (230, 230, 230)    # top 11% = 211px brillante
    Image.fromarray(img, "RGB").save(path)


ok = total = 0


def chk(cond, label):
    global ok, total
    total += 1
    ok += bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


print("== filter_a_stills: no-op de safe_areas corregido ==")

# --- el corazon del fix: 1 frame (bug) vs 2 frames (fix) ---
top = _sampled(top=True)
chk(check_safe_areas([top])["pass"],
    "1 frame con banda SUPERIOR brillante PASA (reproduce el no-op historico)")
chk(not check_safe_areas([top, top])["pass"],
    "2 frames [f, f] REPRUEBAN esa banda superior -> el fix la atrapa")

bot = _sampled(bot=True)
chk(check_safe_areas([bot])["pass"],
    "1 frame con banda INFERIOR brillante PASA (no-op)")
chk(not check_safe_areas([bot, bot])["pass"],
    "2 frames [f, f] REPRUEBAN la banda inferior")

# control: un still limpio (oscuro) debe PASAR con [f, f] (no reprueba todo)
clean = _sampled()
chk(check_safe_areas([clean, clean])["pass"],
    "still limpio (oscuro) PASA safe_areas con [f, f]")

# --- integracion real: run_one sobre PNG a resolucion real (incluye resize) ---
with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    _png(d / "bright_top.png", top_band=True)
    _png(d / "dark_clean.png", top_band=False)
    r_bad = run_one(d / "bright_top.png")
    r_ok = run_one(d / "dark_clean.png")

chk(not r_bad["safe_areas"]["pass"] and r_bad["overall"] == "FAIL",
    "run_one(PNG banda-superior) -> safe_areas FAIL, overall FAIL")
chk(r_ok["safe_areas"]["pass"] and r_ok["overall"] == "PASS",
    "run_one(PNG oscuro limpio) -> safe_areas PASS, overall PASS")

print(f"\nRESULTADO: {ok}/{total}")
sys.exit(0 if ok == total else 1)
