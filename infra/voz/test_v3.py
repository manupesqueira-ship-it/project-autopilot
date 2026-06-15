"""Sample A/B: mismo texto del hook con eleven_v3 (Asgard) para comparar
contra el b1 de multilingual_v2. Si v3 no soporta with-timestamps, cae al
endpoint normal (para A/B de calidad basta el audio)."""

import base64
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from tts_timestamps import DEFAULT_VOICE, load_env

TEXT = "Tu banco gana con tu dinero. Tú, no."
OUT = Path(r"C:\Users\manup\projects\project-autopilot\infra\assembler\out\dinero_dormido\voz_ab")
OUT.mkdir(parents=True, exist_ok=True)

key = load_env()["ELEVENLABS_API_KEY"]
headers = {"xi-api-key": key, "Content-Type": "application/json"}
body = {"text": TEXT, "model_id": "eleven_v3"}

r = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{DEFAULT_VOICE}/with-timestamps"
    "?output_format=mp3_44100_128", headers=headers, json=body, timeout=120)
if r.ok:
    (OUT / "b1_asgard_v3.mp3").write_bytes(
        base64.b64decode(r.json()["audio_base64"]))
    print("v3 with-timestamps OK -> b1_asgard_v3.mp3 (timestamps disponibles)")
else:
    print("with-timestamps v3 fallo:", r.status_code, r.text[:300])
    r2 = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{DEFAULT_VOICE}"
        "?output_format=mp3_44100_128", headers=headers, json=body, timeout=120)
    if r2.ok:
        (OUT / "b1_asgard_v3.mp3").write_bytes(r2.content)
        print("v3 endpoint normal OK -> b1_asgard_v3.mp3 (SIN timestamps)")
    else:
        print("v3 normal tambien fallo:", r2.status_code, r2.text[:300])
