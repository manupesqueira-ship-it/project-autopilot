# -*- coding: utf-8 -*-
"""
logo_fetch.py — consigue IDENTIDAD VISUAL REAL para los masters (gate 07-08:
"pudiste haber puesto el logo de la FIFA, la bandera de Méx y el logo de la
selección... ese debe ser trabajo del director creativo").

Fuentes (assets reales, no IA — regla logos=vector real):
  flag:XX      → flagcdn.com (banderas oficiales, dominio público)
  wiki:Título  → imagen principal del artículo de Wikipedia (logos/escudos
                 oficiales; uso editorial estándar de medios)

Descarga a infra/remotion-render/public/logos/<slug>.png y lo registra en el
banco compartido C:/Users/manup/assets_ia/manifest.json (type=brand, reusable).
SIEMPRE verificar en PÍXELES tras descargar (regla brand_safe: mirar el asset).

Uso:  python logo_fetch.py fifa=wiki:FIFA mx=flag:mx seleccion_mx="wiki:Mexico national football team"
"""
import json
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
LOGOS = ROOT / "infra" / "remotion-render" / "public" / "logos"
BANK = Path(r"C:\Users\manup\assets_ia\manifest.json")
UA = {"User-Agent": "DineroIA-editorial/1.0 (contacto: manupesqueira@gmail.com)"}


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def fetch_flag(iso2: str) -> bytes:
    return _get(f"https://flagcdn.com/w320/{iso2.lower()}.png")


def fetch_wiki(title: str) -> bytes:
    q = urllib.parse.urlencode({
        "action": "query", "titles": title, "prop": "pageimages",
        "pithumbsize": 512, "format": "json", "redirects": 1,
    })
    data = json.loads(_get(f"https://en.wikipedia.org/w/api.php?{q}"))
    pages = data.get("query", {}).get("pages", {})
    for p in pages.values():
        thumb = (p.get("thumbnail") or {}).get("source")
        if thumb:
            return _get(thumb)
    raise SystemExit(f"wiki:{title} sin imagen principal")


def register(slug: str, spec: str, path: Path):
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    entry = {
        "file": str(path).replace("\\", "/"),
        "subject": f"logo/identidad: {slug} ({spec})",
        "world": "n/a (asset de identidad)",
        "engine": "asset real (flagcdn/wikipedia editorial)",
        "type": "brand",
        "used_in": [],
        "date": str(date.today()),
        "note": "REUSABLE; verificar en píxeles antes de cada uso",
    }
    bank["assets"] = [a for a in bank["assets"] if a["file"] != entry["file"]] + [entry]
    BANK.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    LOGOS.mkdir(parents=True, exist_ok=True)
    for arg in sys.argv[1:]:
        slug, spec = arg.split("=", 1)
        kind, _, val = spec.partition(":")
        data = fetch_flag(val) if kind == "flag" else fetch_wiki(val)
        dst = LOGOS / f"{slug}.png"
        dst.write_bytes(data)
        register(slug, spec, dst)
        print(f"{slug}: {spec} -> logos/{slug}.png ({len(data)/1024:.0f} KB) · registrado en banco")
