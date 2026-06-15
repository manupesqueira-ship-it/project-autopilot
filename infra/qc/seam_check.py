"""Tira visual de las costuras de un video: 8 frames alrededor de cada
tiempo dado (fila = costura). Uso:
    python seam_check.py video.mp4 salida.jpg t1 t2 t3 ...
"""

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

OFFSETS = [-0.20, -0.13, -0.07, -0.02, 0.02, 0.07, 0.13, 0.20]
W, H = 135, 240


def main():
    video, out = sys.argv[1], sys.argv[2]
    times = [float(t) for t in sys.argv[3:]]
    sheet = Image.new("RGB", (W * len(OFFSETS) + 64, H * len(times)),
                      (8, 8, 12))
    d = ImageDraw.Draw(sheet)
    tmp = Path(out).with_suffix(".tmp.png")
    for r, t in enumerate(times):
        d.text((4, r * H + H // 2 - 6), f"{t:5.1f}s", fill=(230, 230, 230))
        for c, off in enumerate(OFFSETS):
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error",
                 "-ss", f"{max(t + off, 0):.3f}", "-i", video,
                 "-frames:v", "1", "-vf", f"scale={W}:{H}", str(tmp)],
                check=True)
            sheet.paste(Image.open(tmp), (64 + c * W, r * H))
    tmp.unlink(missing_ok=True)
    sheet.save(out, quality=90)
    print("WROTE", out)


if __name__ == "__main__":
    main()
