#!/usr/bin/env python3
"""
telegram_bot.py - Gate humano via Telegram para Dinero LATAM.

QUE HACE: manda el video ya producido a tu Telegram con dos botones
[OK Publicar] / [Basura], espera tu tap desde el celular (sin PC) y devuelve la
decision. Asi el gate humano deja de atarte a la compu. $0, stdlib (urllib).

Lee TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID del .env RAIZ del repo. NUNCA imprime
el token (ni en logs ni en errores).

USO:
  python telegram_bot.py --ping
      -> verifica el bot (getMe) y te manda un mensaje con UN boton de prueba;
         confirma el viaje redondo (mandar + recibir tu tap).

  python telegram_bot.py --video <URL_publica> --caption-file cap.txt [--timeout 7200]
      -> manda el video con los 2 botones y ESPERA tu decision.
         Sale por stdout: APPROVED | REJECTED | TIMEOUT  (y exit code 0/2/3).

Tambien se importa como modulo desde el orquestador (producir.py):
  from telegram_bot import send_for_approval, wait_for_decision
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT_ENV = Path(r"C:\Users\manup\projects\project-autopilot\.env")
API = "https://api.telegram.org/bot{token}/{method}"
LONGPOLL_S = 30  # long-poll del lado del server: eficiente, no busy-wait


def load_env(path: Path) -> dict:
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _creds() -> tuple[str, str]:
    env = load_env(ROOT_ENV)
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat = env.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en el .env raiz.")
    return token, chat


def _call(token: str, method: str, params=None, data=None, timeout=70, retries=6) -> dict:
    url = API.format(token=token, method=method)
    if data is not None:
        body = urllib.parse.urlencode(data).encode("utf-8")
    else:
        body = None
        if params:
            url += "?" + urllib.parse.urlencode(params)
    last = ""
    for attempt in range(retries + 1):
        req = (urllib.request.Request(url, data=body, method="POST")
               if body is not None else urllib.request.Request(url, method="GET"))
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            # El cuerpo de error de Telegram NO incluye el token (el token va en la
            # URL, que no se imprime). Es seguro mostrar el 'description'.
            try:
                err = json.loads(e.read().decode("utf-8"))
                desc = err.get("description", str(err))
                retry_after = (err.get("parameters") or {}).get("retry_after")
            except Exception:
                desc, retry_after = f"HTTP {e.code}", None
            last = desc
            # 429 (rate-limit) y 5xx (server) son transitorios: el gate hace un
            # long-poll de horas y un blip NO debe matarlo. Respeta retry_after.
            if (e.code == 429 or 500 <= e.code < 600) and attempt < retries:
                wait = retry_after if isinstance(retry_after, (int, float)) else 5
                print(f"[tg] {method}: {e.code} {desc} -> reintento en {wait}s "
                      f"({attempt + 1}/{retries})", flush=True)
                time.sleep(wait + 1)
                continue
            raise SystemExit(f"ERROR Telegram ({method}): {desc}")
        except OSError as e:
            # Blip de red en el long-poll: reintenta, no tires el gate. Atrapa
            # OSError (no solo URLError) porque el read-timeout del long-poll y el
            # conn-reset (WinError 10054) escapan dentro de getresponse() como
            # TimeoutError/ConnectionError pelones, que urllib NO envuelve en URLError.
            last = str(getattr(e, "reason", e))
            if attempt < retries:
                print(f"[tg] {method}: red/{last} -> reintento en 3s "
                      f"({attempt + 1}/{retries})", flush=True)
                time.sleep(3)
                continue
            raise SystemExit(f"ERROR Telegram ({method}): red/{last}")
    raise SystemExit(f"ERROR Telegram ({method}): agotados {retries} reintentos ({last})")


def _kbd(tag: str, approve="OK Publicar", reject="Basura") -> str:
    return json.dumps({"inline_keyboard": [[
        {"text": "✅ " + approve, "callback_data": f"approve:{tag}"},
        {"text": "❌ " + reject, "callback_data": f"reject:{tag}"},
    ]]})


# Encabezado/boton por TIPO de pieza, para que en el celular sea OBVIO que estas
# aprobando: POST del feed (permanente) vs STORY teaser (24h, jala al post).
_KINDS = {
    "post":  {"head": "\U0001f3ac POST · reel del feed\nRevisa y decide:\n\n",
              "approve": "OK Publicar"},
    "story": {"head": "\U0001f4f2 STORY · teaser 24h (jala al post)\nRevisa y decide:\n\n",
              "approve": "Publicar Story"},
}


def send_for_approval(token: str, chat: str, video_url: str, caption: str, tag: str,
                      kind: str = "post") -> int:
    """Manda el video (por URL publica) con los 2 botones. Devuelve message_id.

    kind = 'post' | 'story' -> cambia encabezado/emoji y el texto del boton OK para
    que en Telegram distingas QUE estas aprobando (no publicar una Story creyendo
    que es el reel, ni al reves).
    """
    k = _KINDS.get(kind, _KINDS["post"])
    r = _call(token, "sendVideo", data={
        "chat_id": chat,
        "video": video_url,
        "caption": (k["head"] + caption)[:1024],  # limite de caption de media en Telegram
        "reply_markup": _kbd(tag, approve=k["approve"]),
    })
    return r["result"]["message_id"]


def wait_for_decision(token: str, chat: str, tag: str, timeout: int = 7200) -> str:
    """Espera el tap. Devuelve 'approved' | 'rejected' | 'timeout'.

    Hace deleteWebhook primero: si la era vieja dejo un webhook puesto,
    getUpdates devuelve 409 Conflict y nunca veriamos el tap.
    """
    _call(token, "deleteWebhook", data={"drop_pending_updates": "false"})
    deadline = time.time() + timeout
    offset = None
    while time.time() < deadline:
        params = {"timeout": LONGPOLL_S}
        if offset is not None:
            params["offset"] = offset
        resp = _call(token, "getUpdates", params=params, timeout=LONGPOLL_S + 15)
        for upd in resp.get("result", []):
            offset = upd["update_id"] + 1
            cq = upd.get("callback_query")
            if not cq:
                continue
            data = cq.get("data", "")
            if not (data.endswith(":" + tag)):
                continue  # tap de OTRO video; ignorar
            _call(token, "answerCallbackQuery", data={"callback_query_id": cq["id"]})
            approved = data.startswith("approve:")
            msg = cq.get("message", {})
            if msg:
                nota = "✅ APROBADO — entra a publicarse." if approved \
                    else "\U0001f5d1️ DESCARTADO — no se publica."
                _call(token, "editMessageReplyMarkup", data={
                    "chat_id": chat, "message_id": msg["message_id"],
                    "reply_markup": json.dumps({"inline_keyboard": []}),
                })
                _call(token, "sendMessage", data={"chat_id": chat, "text": nota,
                                                  "reply_to_message_id": msg["message_id"]})
            return "approved" if approved else "rejected"
    return "timeout"


def _ping():
    token, chat = _creds()
    me = _call(token, "getMe")
    uname = me.get("result", {}).get("username", "?")
    print(f"[tg] bot OK: @{uname}")
    _call(token, "deleteWebhook", data={"drop_pending_updates": "false"})
    tag = f"ping{int(time.time())}"
    try:
        r = _call(token, "sendMessage", data={
            "chat_id": chat,
            "text": "\U0001f916 Bot de Dinero LATAM vivo. Tocame el boton para "
                    "confirmar que recibo tus taps:",
            "reply_markup": _kbd(tag, approve="Funciona", reject="Probar otro"),
        })
    except SystemExit as e:
        print(e)
        print(f"[tg] Si dijo 'chat not found': abre @{uname} en Telegram y dale Start.")
        raise
    print(f"[tg] mensaje enviado (msg_id={r['result']['message_id']}). Esperando tu tap (120s)...")
    d = wait_for_decision(token, chat, tag, timeout=120)
    print(f"[tg] RESULTADO DEL VIAJE REDONDO: {d}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--ping", action="store_true")
    ap.add_argument("--video", help="URL publica del MP4")
    ap.add_argument("--caption-file")
    ap.add_argument("--caption")
    ap.add_argument("--tag", default=None, help="id corto del video (para casar el tap)")
    ap.add_argument("--timeout", type=int, default=7200)
    args = ap.parse_args()

    if args.ping:
        _ping()
        return

    if not args.video:
        raise SystemExit("Falta --video <URL> (o usa --ping)")
    if args.caption_file:
        caption = Path(args.caption_file).read_text(encoding="utf-8").strip()
    elif args.caption:
        caption = args.caption
    else:
        raise SystemExit("Falta --caption o --caption-file")

    token, chat = _creds()
    tag = args.tag or f"v{int(time.time())}"
    send_for_approval(token, chat, args.video, caption, tag)
    print(f"[tg] video enviado a Telegram, esperando tu decision (timeout {args.timeout}s)...")
    d = wait_for_decision(token, chat, tag, timeout=args.timeout)
    print(d.upper())
    sys.exit({"approved": 0, "rejected": 2, "timeout": 3}[d])


if __name__ == "__main__":
    main()
