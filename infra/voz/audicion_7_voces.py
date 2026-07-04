"""audicion_7_voces.py — genera 7 opciones de voz de ElevenLabs y las manda a Telegram.

Busca en la librería de voces compartidas (idioma es, caso narrativo), elige 7
DIVERSAS (mezcla hombre/mujer, edades), sintetiza LA MISMA línea de reel con cada
una (modelo eleven_v3, mismo que Asgard) y manda cada muestra a Telegram numerada
para que Manuel elija. Corre en cuanto ELEVENLABS_API_KEY esté viva:

    python audicion_7_voces.py
"""
import json
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
OUT = ROOT / "infra" / "voz" / "audicion"
DIST = ROOT / "infra" / "distribution"
sys.path.insert(0, str(DIST))
from telegram_bot import API, load_env, ROOT_ENV  # noqa: E402

SAMPLE = ("El Mundial ya dejó cuarenta y cinco mil millones de pesos en México... "
          "en solo veinte días. Y lo que viene el domingo... puede romper todos los récords.")
MODEL = "eleven_v3"


def get_key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("ELEVENLABS_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("no hay ELEVENLABS_API_KEY en .env")


def api(path: str, key: str, params: dict | None = None) -> dict:
    url = f"https://api.elevenlabs.io{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("xi-api-key", key)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def tts(key: str, voice_id: str, text: str, mp3: Path):
    body = json.dumps({"text": text, "model_id": MODEL,
                       "voice_settings": {"stability": 0.45, "similarity_boost": 0.8}}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
        data=body, method="POST")
    req.add_header("xi-api-key", key)
    req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        mp3.write_bytes(r.read())


def send_audio(path: Path, caption: str) -> int:
    env = load_env(ROOT_ENV)
    token, chat = env["TELEGRAM_BOT_TOKEN"], env["TELEGRAM_CHAT_ID"]
    boundary = "----dineroia" + uuid.uuid4().hex
    body = b""
    for k, v in {"chat_id": chat, "caption": caption[:1024]}.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"{path.name}\"\r\n"
             f"Content-Type: audio/mpeg\r\n\r\n").encode()
    body += path.read_bytes() + b"\r\n" + f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(API.format(token=token, method="sendAudio"), data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req, timeout=120) as r:
        res = json.loads(r.read())
    if not res.get("ok"):
        raise SystemExit(f"sendAudio falló: {res.get('description', res)}")
    return res["result"]["message_id"]


def pick_voices(key: str) -> list[dict]:
    """7 voces DIVERSAS de la librería compartida en español (narrativo primero)."""
    seen, picks = set(), []
    combos = [
        {"language": "es", "use_cases": "narrative_story", "sort": "cloned_by_count", "page_size": 30},
        {"language": "es", "use_cases": "informative_educational", "sort": "cloned_by_count", "page_size": 30},
        {"language": "es", "sort": "cloned_by_count", "page_size": 30},
    ]
    males, females = [], []
    for params in combos:
        try:
            data = api("/v1/shared-voices", key, params)
        except Exception:
            continue
        for v in data.get("voices", []):
            vid = v.get("voice_id")
            if not vid or vid in seen:
                continue
            seen.add(vid)
            (males if v.get("gender") == "male" else females).append(v)
    # 5 masculinas + 2 femeninas (canal narrado por voz masculina hoy; contraste para elegir)
    picks = males[:5] + females[:2]
    if len(picks) < 7:
        picks += (males[5:] + females[2:])[: 7 - len(picks)]
    return picks[:7]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    key = get_key()
    try:
        sub = api("/v1/user/subscription", key)
        print(f"key viva · tier {sub.get('tier')} · {sub.get('character_count')}/{sub.get('character_limit')} chars")
    except Exception:
        print("key scoped (sin permiso de subscription) — seguimos: TTS y voces sí responden")
    OUT.mkdir(parents=True, exist_ok=True)
    voices = pick_voices(key)
    if not voices:
        raise SystemExit("la librería no devolvió voces es — revisar filtros")
    print(f"{len(voices)} voces elegidas")
    for i, v in enumerate(voices, 1):
        vid, name = v["voice_id"], v.get("name", "?")
        gender = v.get("gender", "?")
        acc = v.get("accent", "?")
        mp3 = OUT / f"voz{i}_{name[:16].replace(' ', '_')}.mp3"
        # red intermitente (WinError 10054): reintentos en TTS y en el envío
        for attempt in range(4):
            try:
                if not mp3.exists() or mp3.stat().st_size < 20000:
                    tts(key, vid, SAMPLE, mp3)
                cap = (f"VOZ {i}/7 · {name} ({gender}, {acc})\nvoice_id: {vid}\n\n"
                       "Misma línea en todas. Contesta con el número de las que SÍ.")
                mid = send_audio(mp3, cap)
                print(f"  {i}/7 {name} -> msg {mid}")
                break
            except Exception as e:
                print(f"  {i}/7 intento {attempt + 1}: {type(e).__name__}")
                time.sleep(4 * (attempt + 1))
        time.sleep(2)
    print("AUDICIÓN ENVIADA — Manuel elige por número")
