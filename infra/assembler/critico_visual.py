# -*- coding: utf-8 -*-
"""critico_visual.py — CRÍTICO CON OJOS (gate previo al Telegram de Manuel).

Extrae frames reales del MP4 final y los JUZGA contra el TASTE_LEDGER con visión.
Objetivo: que los rechazos obvios mueran AQUÍ y no gasten la atención del
fundador. R1-compliant: juzga PÍXELES, no metadata.

Uso:  python critico_visual.py <final.mp4>   → exit 0 PASS · 1 FAIL
      (escribe <final>.critica.json)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from agent_api import ask_json, img_block, load_taste

FFMPEG = (r"C:\Users\manup\AppData\Local\Microsoft\WinGet\Packages"
          r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
          r"\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe")

SYSTEM_TMPL = """Eres el CRÍTICO VISUAL de un canal premium. Recibes frames reales del reel terminado
y los juzgas contra el gusto DEL FUNDADOR (su ledger completo abajo). Tu trabajo: matar aquí lo que
él rechazaría, ANTES de que le llegue.

{taste}

CHECKLIST DURO sobre los frames (todo se juzga en PÍXELES):
1. ¿Algún texto CORTADO/fuera de pantalla o encimado sobre zona ocupada del hero?
2. ¿El mundo se sostiene (negro mate, jerarquía por luz) SIN quedarse plano-oscuro todo el reel?
   (busca el ARCO: debe haber frames más ricos hacia el clímax)
3. ¿Los heroes se VEN premium (composición, luz) o genéricos/cliché?
4. ¿Identidad real donde el tema la pide (logos/banderas reconocibles)?
5. ¿Los datos se leen completos (cifras, unidades, pies de fuente)?
6. ¿Algún frame se ve "hecho con AI barato" (artefactos, deformidades, texto fantasma horneado)?

Sé el abogado del diablo: si dudas de un frame, señálalo. FAIL si CUALQUIER cosa de la checklist
falla claramente.

Devuelve SOLO JSON:
{{"pass": true|false, "score": 0-10,
  "fails": [{{"frame": "t=Ns", "problema": "...", "regla_violada": "..."}}],
  "highlights": ["lo que SÍ está a la barra"],
  "verdict_one_line": "..."}}"""


def review(mp4: Path, n_frames: int = 8) -> dict:
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
        capture_output=True, text=True).stdout.strip())
    tmp = Path(tempfile.mkdtemp(prefix="critico_"))
    blocks = []
    times = [dur * (i + 0.5) / n_frames for i in range(n_frames)]
    for i, t in enumerate(times):
        f = tmp / f"f{i}.png"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(mp4),
                        "-vframes", "1", "-vf", "scale=540:960", str(f)], check=True)
        blocks.append({"type": "text", "text": f"frame t={t:.1f}s:"})
        blocks.append(img_block(f))
    blocks.append({"type": "text", "text": "Tu veredicto (JSON del schema)."})
    return ask_json(SYSTEM_TMPL.format(taste=load_taste()), blocks, temperature=0.5)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    mp4 = Path(sys.argv[1])
    r = review(mp4)
    out = mp4.with_suffix(".critica.json")
    out.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"CRÍTICO VISUAL · score {r.get('score')}/10 · {'PASS' if r.get('pass') else 'FAIL'}")
    print(f"  «{r.get('verdict_one_line', '')}»")
    for f in r.get("fails", []):
        print(f"  {f.get('frame')}: {f.get('problema')}")
    sys.exit(0 if r.get("pass") else 1)
