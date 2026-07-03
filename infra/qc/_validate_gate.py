# -*- coding: utf-8 -*-
"""Valida text_overlap_check.analyze_frame en stills reales.
BAD debe dar empalme=True; los FIX deben dar empalme=False."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from text_overlap_check import analyze_frame, PROC_W, PROC_H

CASES = [
    ("BAD  badhook_late", r"C:\Users\manup\projects\project-autopilot\infra\qc\_badhook_late.png", True),
    ("FIX  fix_f200", r"C:\Users\manup\projects\project-autopilot\infra\remotion-render\_hookgate\fix_f200.png", False),
    ("FIX  fix_f355", r"C:\Users\manup\projects\project-autopilot\infra\remotion-render\_hookgate\fix_f355.png", False),
]

ok = True
for name, path, want_empalme in CASES:
    img = Image.open(path).convert("L").resize((PROC_W, PROC_H), Image.BILINEAR)
    gray = np.asarray(img)
    emp, lns = analyze_frame(gray)
    verdict = "PASS" if emp == want_empalme else "**WRONG**"
    if emp != want_empalme:
        ok = False
    print(f"[{verdict}] {name}: empalme={emp} (esperado {want_empalme})")
    for l in lns:
        print(f"        line y={l['y']} x={l['x']} glyphs={l['glyphs']} "
              f"hero_in={l['hero_in']} ha={l.get('ha')} hb={l.get('hb')} "
              f"bg_frac={l['bg_frac']} bg_p85={l['bg_p85']} bad={l['bad']}")
print("\n=> GATE", "CALIBRADO OK" if ok else "MAL CALIBRADO")
sys.exit(0 if ok else 1)
