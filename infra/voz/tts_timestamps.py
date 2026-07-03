"""Voz con timestamps por palabra (ElevenLabs with-timestamps).

Uso:
    python tts_timestamps.py guion.json out_dir [--voice VOICE_ID]

Para cada beat del guion genera:
    out_dir/vo/{id}.mp3
    out_dir/vo/{id}.words.json   [{"word","start","end"}] en segundos

y un resumen out_dir/vo/timing.json con duracion por beat (la duracion del
beat en el ensamblado = end de su ultima palabra + colchon).
"""

import argparse
import base64
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")

# Codigos HTTP que vale la pena REINTENTAR (transitorios del lado del server o
# rate-limit). Un 4xx "real" (401 auth, 422 body malo) NO entra: reintentarlo
# solo re-falla. Reintentar un transitorio NO re-cobra: una request fallida no
# es una generacion exitosa (las APIs de paga cobran por exito).
RETRY_STATUS = {429, 500, 502, 503, 504}


class RetryableError(Exception):
    """La marca un caller cuando detecta un fallo TRANSITORIO (red/timeout/5xx).
    `with_retries` la atrapa y reintenta; cualquier otra excepcion aborta ya."""


def with_retries(fn, *, tries=4, base_delay=2.0, what="API"):
    """Llama fn() con backoff exponencial ante RetryableError.

    fn() devuelve el resultado en exito y lanza RetryableError para reintentar.
    Tras agotar `tries`, aborta con SystemExit(1). Cualquier otra excepcion de
    fn() (p.ej. SystemExit por 401) sube intacta sin reintentar.
    """
    for attempt in range(1, tries + 1):
        try:
            return fn()
        except RetryableError as e:
            if attempt == tries:
                print(f"{what}: agotados {tries} intentos ({e})")
                raise SystemExit(1)
            delay = base_delay * (2 ** (attempt - 1))
            print(f"{what}: intento {attempt}/{tries} fallo ({e}); reintento en {delay:.0f}s")
            time.sleep(delay)

# Asgard — confirmado por Manuel 2026-06-11 (Norberto Falcon = RviUET0nhAzUw2NH93OJ)
# Para cambiar de voz: edita estas 2 lineas, borra los out/<slug>/vo/*.mp3 y
# *.words.json viejos (si no, los reusa) y regenera con build916 ... vo.
DEFAULT_VOICE = "lJtjZw9ZjSbD9Zs9bOWq"
MODEL = "eleven_v3"  # 2026-06-13 Manuel eligio audicion #1: misma Asgard, modelo v3 (mas real)
VOICE_SETTINGS = {
    "stability": 0.38,        # mas bajo = mas expresivo, menos robotico
    "similarity_boost": 0.8,
    "style": 0.25,
    "use_speaker_boost": True,
}


def load_env() -> dict:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v
    return env


def chars_to_words(alignment: dict) -> list[dict]:
    chars = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    ends = alignment["character_end_times_seconds"]
    words, cur, w_start = [], "", None
    for ch, s, e in zip(chars, starts, ends):
        if ch.isspace():
            if cur:
                words.append({"word": cur, "start": w_start, "end": prev_end})
                cur, w_start = "", None
        else:
            if not cur:
                w_start = s
            cur += ch
            prev_end = e
    if cur:
        words.append({"word": cur, "start": w_start, "end": prev_end})
    return words


def tts_beat(key: str, voice: str, text: str, mp3_path: Path) -> list[dict]:
    def _call() -> dict:
        try:
            r = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps"
                "?output_format=mp3_44100_128",
                headers={"xi-api-key": key},
                json={"text": text, "model_id": MODEL, "voice_settings": VOICE_SETTINGS},
                timeout=120,
            )
        except requests.exceptions.RequestException as e:
            raise RetryableError(f"red/timeout: {e}")
        if r.status_code in RETRY_STATUS:
            raise RetryableError(f"HTTP {r.status_code}: {r.text[:200]}")
        if r.status_code != 200:
            print("ELEVENLABS ERR", r.status_code, r.text[:300])
            raise SystemExit(1)
        return r.json()

    # solo la LLAMADA se reintenta; decodificar/escribir el mp3 ya con datos en
    # mano NO (un 200 ya se cobro -> no re-llamar por un fallo local).
    data = with_retries(_call, what=f"ElevenLabs[{mp3_path.stem}]")
    mp3_path.write_bytes(base64.b64decode(data["audio_base64"]))
    return chars_to_words(data["alignment"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("outdir")
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    args = ap.parse_args()

    env = load_env()
    key = env["ELEVENLABS_API_KEY"]
    guion = json.loads(Path(args.guion).read_text(encoding="utf-8-sig"))
    vo_dir = Path(args.outdir) / "vo"
    vo_dir.mkdir(parents=True, exist_ok=True)

    timing = {}
    for b in guion["beats"]:
        mp3 = vo_dir / f"{b['id']}.mp3"
        wjson = vo_dir / f"{b['id']}.words.json"
        if mp3.exists() and wjson.exists():
            words = json.loads(wjson.read_text(encoding="utf-8"))
            print("VO skip", b["id"])
        else:
            words = tts_beat(key, args.voice, b["vo"], mp3)
            wjson.write_text(json.dumps(words, indent=2, ensure_ascii=False),
                             encoding="utf-8")
            print(f"VO ok {b['id']}  {len(words)} palabras  "
                  f"{words[-1]['end']:.2f}s")
        timing[b["id"]] = {
            "words": len(words),
            "speech_end": words[-1]["end"] if words else 0,
        }

    (vo_dir / "timing.json").write_text(
        json.dumps(timing, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
