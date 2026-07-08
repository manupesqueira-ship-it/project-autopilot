"""Prueba E: guion conversacional (ganador D) + AUDIO TAGS de eleven_v3.
Los tags ([curious], [exhales]...) dirigen la ACTUACIÓN dentro del texto — es el
techo del motor actual antes del salto real (clonar la voz de Manuel)."""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
sys.path.insert(0, str(ROOT / "infra" / "voz"))
import tts_timestamps as tts  # noqa: E402
from tts_timestamps import load_env, tts_beat  # noqa: E402
from audicion_settings_alberto import ALBERTO, OUT, send_audio  # noqa: E402

TEXTO_E = ("[curious] ¿Sabes cuánto pagó alguien por UN boleto? "
           "[pause] Más de dos millones de pesos... y ni siquiera vio ganar a México. "
           "[exhales] Pero aquí viene lo bueno — mientras el estadio se quedaba mudo... "
           "la ciudad hizo su agosto. Casi ochenta veces el premio del equipo. "
           "[pause] Esa... esa es la historia.")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    key = load_env()["ELEVENLABS_API_KEY"]
    tts.VOICE_SETTINGS = {"stability": 0.30, "similarity_boost": 0.80,
                          "style": 0.40, "use_speaker_boost": True}
    mp3 = OUT / "alberto_E.mp3"
    words = tts_beat(key, ALBERTO, TEXTO_E, mp3)
    print(f"E: {words[-1]['end']:.1f}s")
    ok = send_audio(mp3, "🎙️ PRUEBA E — la D ganadora + AUDIO TAGS de eleven v3 "
                         "([curious]/[exhales]/[pause] dirigen la actuación dentro del guion). "
                         "Este es el TECHO del motor actual — el salto real es otra cosa (te explico en el chat).")
    print("enviada" if ok else "FALLÓ envío")
