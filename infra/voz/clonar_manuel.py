# -*- coding: utf-8 -*-
"""clonar_manuel.py — Instant Voice Clone de Manuel desde sus 6 bloques grabados.

1) Normaliza los .m4a (mono, loudnorm suave, MP3 192k) → out_clone/
2) Crea el IVC vía API ElevenLabs (POST /v1/voices/add)
3) Genera una línea de prueba estilo D con el clon y la manda a Telegram
   junto a la MISMA línea con Alberto (A/B directo)

Nota: IVC = prueba inmediata. El clon PROFESSIONAL (calidad definitiva) se hace
en la web con verificación de identidad y conviene con 30+ min de material.
"""
import json
import subprocess
import sys
import time
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
sys.path.insert(0, str(ROOT / "infra" / "voz"))
import tts_timestamps as tts  # noqa: E402
from tts_timestamps import load_env, tts_beat  # noqa: E402
from audicion_settings_alberto import ALBERTO, send_audio  # noqa: E402

FF = (r"C:\Users\manup\AppData\Local\Microsoft\WinGet\Packages"
      r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
      r"\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe")
SRC = Path(r"C:\Users\manup\OneDrive\Desktop\Grabaciones de voz Manuel")
OUT = ROOT / "infra" / "voz" / "out_clone"

TEXTO = ("¿Sabes cuánto pagó alguien por UN boleto? Más de dos millones de pesos... "
         "y ni siquiera vio ganar a México. Pero aquí viene lo bueno — mientras el estadio "
         "se quedaba mudo, la ciudad hizo su agosto... casi ochenta veces el premio del "
         "equipo. Esa... esa es la historia.")


def prep() -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    files = []
    for f in sorted(SRC.glob("*.m4a.mp4")):
        dst = OUT / (f.stem.replace(" ", "_").replace(".m4a", "") + ".mp3")
        if not dst.exists():
            subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(f),
                            "-ac", "1", "-af", "loudnorm=I=-20:TP=-3",
                            "-c:a", "libmp3lame", "-b:a", "192k", str(dst)], check=True)
        files.append(dst)
        print(f"  prep {dst.name} ({dst.stat().st_size/1e6:.1f} MB)")
    return files


def create_ivc(key: str, files: list[Path]) -> str:
    boundary = f"----clone{uuid.uuid4().hex[:12]}"
    parts = [f"--{boundary}\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\nManuel (canal)\r\n".encode()]
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"description\"\r\n\r\n"
                 f"Voz real de Manuel, 6 bloques (educativo/hook/cifras/confesional/cierres/variedad)\r\n".encode())
    for p in files:
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"files\"; "
                     f"filename=\"{p.name}\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode())
        parts.append(p.read_bytes())
        parts.append(b"\r\n")
    body = b"".join(parts) + f"--{boundary}--\r\n".encode()
    req = urllib.request.Request("https://api.elevenlabs.io/v1/voices/add",
                                 data=body, method="POST")
    req.add_header("xi-api-key", key)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ElevenLabs voices/add HTTP {e.code}: {e.read()[:300]}")
    vid = data.get("voice_id")
    if not vid:
        raise SystemExit(f"sin voice_id: {data}")
    return vid


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    key = load_env()["ELEVENLABS_API_KEY"]
    print("── 1/3 preparando bloques")
    files = prep()
    print("── 2/3 creando Instant Voice Clone")
    vid_file = OUT / "voice_id.txt"
    if vid_file.exists():
        vid = vid_file.read_text().strip()
        print(f"  clon ya existía: {vid}")
    else:
        vid = create_ivc(key, files)
        vid_file.write_text(vid)
        print(f"  ✓ clon creado: {vid}")
    print("── 3/3 prueba A/B a Telegram")
    tts.VOICE_SETTINGS = {"stability": 0.30, "similarity_boost": 0.85,
                          "style": 0.35, "use_speaker_boost": True}
    mp3_clone = OUT / "test_clon_manuel.mp3"
    if not mp3_clone.exists():
        tts_beat(key, vid, TEXTO, mp3_clone)
    send_audio(mp3_clone, "🎙️ TU CLON (instantáneo, con tus 9 min) — misma línea de prueba de siempre. "
                          "¿Se parece a ti? ¿Suena menos AI que Alberto?")
    time.sleep(2)
    mp3_alb = OUT / "test_alberto_ref.mp3"
    if not mp3_alb.exists():
        tts_beat(key, ALBERTO, TEXTO, mp3_alb)
    send_audio(mp3_alb, "🎙️ ALBERTO D (referencia) — la misma línea, para comparar de oído.")
    print("listo — A/B en tu Telegram")
