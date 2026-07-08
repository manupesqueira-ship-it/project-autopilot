"""Audición de SETTINGS para Alberto (retro 07-07: 'la voz sigue siendo obvio que es AI').

Mismo texto, 4 configuraciones → Telegram etiquetadas A-D. Manuel elige de oído.
A = baseline de la audición original · B = retuneada (menos plana) · C = expresiva
al límite · D = B + guion reescrito conversacional (la naturalidad también es TEXTO).
"""
import sys
import time
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
sys.path.insert(0, str(ROOT / "infra" / "voz"))
sys.path.insert(0, str(ROOT / "infra" / "distribution"))
import tts_timestamps as tts  # noqa: E402
from tts_timestamps import load_env, tts_beat  # noqa: E402

ALBERTO = "l1zE9xgNpUTaQCZzpNJa"
OUT = ROOT / "infra" / "voz" / "out_settings_alberto"

TEXTO = ("Alguien pagó más de dos millones de pesos... por un boleto. "
         "Y ojo — no fue para ver ganar a México. "
         "Pero mientras el estadio se quedaba callado... la ciudad hizo su agosto. "
         "Casi ochenta veces más que el premio del equipo. Ahí está la verdadera historia.")

TEXTO_D = ("¿Sabes cuánto pagó alguien por UN boleto? Más de dos millones de pesos... "
           "y ni siquiera vio ganar a México. "
           "Pero aquí viene lo bueno — mientras el estadio se quedaba mudo, "
           "la ciudad hizo su agosto... casi ochenta veces el premio del equipo. "
           "Esa... esa es la historia.")

VARIANTES = [
    ("A", {"stability": 0.45, "similarity_boost": 0.80, "style": 0.25, "use_speaker_boost": True}, TEXTO,
     "A — la de la audición original (tu referencia)"),
    ("B", {"stability": 0.30, "similarity_boost": 0.80, "style": 0.40, "use_speaker_boost": True}, TEXTO,
     "B — retuneada: menos plana, más intención"),
    ("C", {"stability": 0.20, "similarity_boost": 0.75, "style": 0.55, "use_speaker_boost": True}, TEXTO,
     "C — expresiva al límite (riesgo: menos consistente entre beats)"),
    ("D", {"stability": 0.30, "similarity_boost": 0.80, "style": 0.40, "use_speaker_boost": True}, TEXTO_D,
     "D — misma voz que B pero GUION reescrito conversacional (pregunta directa, muletillas naturales)"),
]


def send_audio(path: Path, caption: str, tries: int = 5):
    import urllib.request
    env = load_env()
    token, chat = env["TELEGRAM_BOT_TOKEN"], env["TELEGRAM_CHAT_ID"]
    boundary = "----albertoaudition"
    data = path.read_bytes()
    parts = []
    for k, v in (("chat_id", chat), ("caption", caption)):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"audio\"; "
                 f"filename=\"{path.name}\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode())
    body = b"".join(parts) + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendAudio", data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                r.read()
            return True
        except Exception as e:  # noqa: BLE001
            print(f"  tg intento {a + 1}: {type(e).__name__}")
            time.sleep(6 * (a + 1))
    return False


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    key = load_env()["ELEVENLABS_API_KEY"]
    OUT.mkdir(parents=True, exist_ok=True)
    for tag, settings, texto, caption in VARIANTES:
        mp3 = OUT / f"alberto_{tag}.mp3"
        if not mp3.exists():
            tts.VOICE_SETTINGS = settings
            words = tts_beat(key, ALBERTO, texto, mp3)
            print(f"{tag}: {words[-1]['end']:.1f}s")
        ok = send_audio(mp3, f"🎙️ PRUEBA DE VOZ {caption}")
        print(f"{tag}: {'enviada' if ok else 'FALLÓ envío'}")
        time.sleep(2)
    print("Listo — contesta con la letra que suene menos AI.")
