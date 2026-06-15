# -*- coding: utf-8 -*-
"""Audicion de voces: genera la MISMA frase en varias voces/modelos para elegir.
Uso: python audition.py
Salida: infra/assembler/out/_voz_audicion/<n>_<slug>.mp3
"""
import base64
from pathlib import Path

import requests
from tts_timestamps import load_env

OUT = Path(r"C:\Users\manup\projects\project-autopilot\infra\assembler\out\_voz_audicion")
SAMPLE = ("Un pais entero apuesta todo al Bitcoin. El mundo dijo que estaban "
          "locos. Hoy ganan doscientos nueve millones de dolares.")

SETTINGS = {"stability": 0.38, "similarity_boost": 0.8, "style": 0.25,
            "use_speaker_boost": True}

# (slug, voice_id, model)
VARIANTS = [
    ("1_asgard_v3", "lJtjZw9ZjSbD9Zs9bOWq", "eleven_v3"),
    ("2_asgard_v2_ref", "lJtjZw9ZjSbD9Zs9bOWq", "eleven_multilingual_v2"),
    ("3_gerardo_becker_mx", "jDCIEoR6LooiuNW1UVeS", "eleven_multilingual_v2"),
    ("4_andres_deep", "DG7jA52oyooNEvdToTzA", "eleven_multilingual_v2"),
    ("5_zenas_doc", "0fizugdarib8ZOtvybTk", "eleven_multilingual_v2"),
]


def gen(key, slug, voice, model):
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
        params={"output_format": "mp3_44100_128"},
        headers={"xi-api-key": key},
        json={"text": SAMPLE, "model_id": model, "voice_settings": SETTINGS},
        timeout=120,
    )
    if r.status_code != 200:
        print(f"  FAIL {slug} [{model}] {r.status_code} {r.text[:160]}")
        return False
    (OUT / f"{slug}.mp3").write_bytes(r.content)
    print(f"  ok   {slug} [{model}]  {len(r.content)//1024} KB")
    return True


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    key = load_env()["ELEVENLABS_API_KEY"]
    print("Audicion ->", OUT)
    for slug, voice, model in VARIANTS:
        gen(key, slug, voice, model)


if __name__ == "__main__":
    main()
