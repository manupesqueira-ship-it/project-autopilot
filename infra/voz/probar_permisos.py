"""Sonda de permisos de la key ElevenLabs: qué puede y qué no (sin imprimir la key)."""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
sys.path.insert(0, str(ROOT / "infra" / "voz"))
from tts_timestamps import load_env  # noqa: E402


def probe(key: str, path: str) -> tuple[int, str]:
    req = urllib.request.Request(f"https://api.elevenlabs.io{path}")
    req.add_header("xi-api-key", key)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:200]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    key = load_env()["ELEVENLABS_API_KEY"]
    print(f"key instalada: …{key[-6:]} ({len(key)} chars)")
    for name, path in [("user", "/v1/user"),
                       ("subscription", "/v1/user/subscription"),
                       ("voices (read)", "/v1/voices?page_size=1")]:
        code, body = probe(key, path)
        if name == "subscription" and code == 200:
            d = json.loads(body) if body.startswith("{") else {}
            print(f"  {name}: {code} → tier={d.get('tier')} · chars={d.get('character_count')}/{d.get('character_limit')} · can_use_ivc={d.get('can_use_instant_voice_cloning')} · can_use_pvc={d.get('can_use_professional_voice_cloning')}")
        else:
            ok = "OK" if code == 200 else body
            print(f"  {name}: {code} {ok if code != 200 else ''}")
