# -*- coding: utf-8 -*-
"""agent_api.py — capa común de los AGENTES del estudio (API Anthropic).

Todos los agentes del pipeline (creativo, guionista, crítico, editor, heroes,
crítico visual) hablan por aquí: una key, un patrón, un ledger de costo.
"""
import base64
import json
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
MODEL = "claude-sonnet-5"


def load_key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no ANTHROPIC key")


def ask(system: str, user, max_tokens: int = 8000, temperature: float = 1.0,
        model: str = MODEL) -> str:
    """user = str o lista de content-blocks (para visión). Devuelve el texto."""
    content = user if isinstance(user, list) else [{"type": "text", "text": user}]
    # claude-sonnet-5 deprecó `temperature` (400 si se manda); el param queda en
    # la firma por compatibilidad pero NO viaja en el request.
    _ = temperature
    body = json.dumps({"model": model, "max_tokens": max_tokens, "system": system,
                       "messages": [{"role": "user", "content": content}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST")
    req.add_header("x-api-key", load_key())
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            resp = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Anthropic HTTP {e.code}: {e.read()[:400]}")
    return "".join(b.get("text", "") for b in resp.get("content", []))


def ask_json(system: str, user, **kw) -> dict:
    txt = ask(system, user, **kw)
    obj, _ = json.JSONDecoder().raw_decode(txt[txt.find("{"):])
    return obj


def img_block(path: Path) -> dict:
    """Content-block de imagen para agentes CON VISIÓN."""
    return {"type": "image", "source": {
        "type": "base64", "media_type": "image/png",
        "data": base64.b64encode(path.read_bytes()).decode("ascii")}}


def load_taste() -> str:
    return (ROOT / "docs" / "standards" / "TASTE_LEDGER.md").read_text(encoding="utf-8")
