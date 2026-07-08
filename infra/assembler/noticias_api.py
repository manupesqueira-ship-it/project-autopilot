# -*- coding: utf-8 -*-
"""noticias_api.py — SCOUT + VERIFICADOR de noticias vía API (autonomía del motor).

Antes la investigación corría dentro de la sesión de Claude Code; esto la porta
a la API de Anthropic con la herramienta server-side de BÚSQUEDA WEB, para que
el motor diario pueda despertar solo (cron) sin sesión abierta.

Flujo:  scout (candidatas frescas) → editor_jefe decide → verify (≥2 fuentes
por cifra) → brief listo para producir_reel.

Uso:  python noticias_api.py scout            → out/_treatments/candidatas.json
      python noticias_api.py verify "<titular elegido>"
                                              → out/_treatments/brief_hoy.json
Costo aprox: scout ~$0.15 · verify ~$0.20 (tokens + búsquedas $10/1000).
"""
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

from agent_api import ROOT, load_key, MODEL

OUT = ROOT / "infra" / "assembler" / "out" / "_treatments"


def ask_with_search(system: str, user: str, max_searches: int = 12,
                    max_tokens: int = 12000) -> str:
    body = json.dumps({
        "model": MODEL, "max_tokens": max_tokens, "system": system,
        "tools": [{"type": "web_search_20250305", "name": "web_search",
                   "max_uses": max_searches}],
        "messages": [{"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST")
    req.add_header("x-api-key", load_key())
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            resp = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Anthropic HTTP {e.code}: {e.read()[:400]}")
    return "".join(b.get("text", "") for b in resp.get("content", [])
                   if b.get("type") == "text")


def _json_from(txt: str) -> dict:
    obj, _ = json.JSONDecoder().raw_decode(txt[txt.find("{"):])
    return obj


SCOUT_SYS = """Eres el SCOUT de noticias de un canal de reels financieros para México/LATAM.
Buscas en la web noticias FRESCAS (últimas 24-72h) de finanzas/economía/cripto/empresas con:
(a) UN dato que obliga a parar el pulgar, (b) un hero VISUAL filmable (lugar/objeto/escena),
(c) impacto en la cartera del viewer mexicano o asombro dimensionable.
Prioriza México/LATAM > global con ángulo LATAM. NADA de temas cuyo pico ya pasó.
Devuelve SOLO JSON: {"candidates": [{"headline": "...", "why_hook": "...", "key_figures":
["cifra + fuente URL", ...], "hero_visual": "...", "freshness": "...", "universe": "tema-universo
en 2 palabras"}, ...]} — las 3-4 mejores."""

VERIFY_SYS = """Eres el VERIFICADOR de datos de un canal de noticias financieras. Tu regla es DURA:
cada cifra que se publica debe estar confirmada en ≥2 fuentes (ideal 1 primaria), con fecha de
corte y URL. Si una cifra no se confirma, se marca verified:false y NO se usa. Verifica también
conversiones (FX del día vía Banxico si aplica) y agrega guardarrailes editoriales si el tema los
pide (estimaciones gremiales se atribuyen, listados de reventa se dicen 'llegó a listarse', etc.).
Devuelve SOLO JSON: {"headline": "...", "why_matters": "...", "facts": {"slug": {"value": "...",
"as_of": "...", "source": "fuentes + URLs"}, ...}, "guardrails": ["..."]}"""


def scout() -> dict:
    txt = ask_with_search(
        SCOUT_SYS,
        f"HOY es {date.today().isoformat()}. Busca las mejores noticias para el reel de hoy "
        f"(varias búsquedas: México economía, Banxico/peso, cripto, empresas/IA, consumo). "
        f"Devuelve el JSON.")
    obj = _json_from(txt)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "candidatas.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    return obj


def verify(headline: str) -> dict:
    txt = ask_with_search(
        VERIFY_SYS,
        f"HOY es {date.today().isoformat()}. NOTICIA ELEGIDA: {headline}\n\n"
        f"Verifica cada cifra clave en ≥2 fuentes y arma el brief. Devuelve el JSON.",
        max_searches=15)
    obj = _json_from(txt)
    (OUT / "brief_hoy.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    return obj


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scout"
    if cmd == "scout":
        r = scout()
        for c in r.get("candidates", []):
            print(f"  · {c['headline']}  [{c.get('freshness','')}]")
        print(f"SCOUT OK · {len(r.get('candidates', []))} candidatas → out/_treatments/candidatas.json")
    elif cmd == "verify":
        r = verify(sys.argv[2])
        ok = sum(1 for f in r.get("facts", {}).values() if "false" not in str(f).lower())
        print(f"VERIFY OK · {len(r.get('facts', {}))} facts → out/_treatments/brief_hoy.json")
    else:
        raise SystemExit("uso: noticias_api.py scout | verify '<titular>'")
