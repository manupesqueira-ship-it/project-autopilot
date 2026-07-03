# -*- coding: utf-8 -*-
"""director.py — DIRECTOR unificado "writers-room" (P1.3 del plan maestro).

Fusiona ideación + producción en UN agente con contrato único:
  IDEA   -> por beat, 2-3 OPCIONES de sujeto/metáfora (cada una un `scene` listo del MENÚ
            CERRADO), con VO y el porqué. NO teclea números: los beats de dato llevan `bind`
            a una clave del ledger.
  ELIGE  -> Manuel elige la opción por beat (Compuerta 1). El LLM recomienda, no auto-decide.
  VERIFICA -> compile() aterriza las elecciones a reel_def (resolviendo binds desde el
            datasheet) y el gate de build_reels lo verifica ANTES de gastar.

Uso:
  python director.py "<tema>" datasheets/<slug>.json            # imprime el TRATAMIENTO (opciones)
  python director.py "<tema>" datasheets/<slug>.json --compile 0,1,0,2,0   # compila las elecciones -> reel_def.json
  (sin --compile usa las recomendadas del LLM)

Menú CERRADO de escenas: cover · mapzoom · bignum · compare · fallchart · payoff · plate · hero_i2v · close
Transiciones renderizables: corte · whoosh · flash · dip
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
HERE = Path(__file__).resolve().parent
MODEL = "claude-sonnet-5"

# clips i2v disponibles (reuso $0) — el director SOLO puede referenciar estos para plate/hero_i2v
I2V_MANIFEST = {
    "i2v/btc_coin.mp4": "moneda Bitcoin dorada cinematográfica girando (oscura, premium)",
    "i2v/oil_barril.mp4": "barril de petróleo con crudo desbordándose",
    "i2v/oil_surtidor.mp4": "surtidor de gasolina, dígitos en la noche",
    "i2v/oil_billete.mp4": "billete de 100 ardiendo en llamas",
}


def load_key():
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("ANTHROPIC_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("no key")


SYSTEM = r"""Eres el DIRECTOR de un canal premium de finanzas LATAM (reels 9:16, estilo EDITORIAL
papel-oxblood, ULTRA visual y en MOVIMIENTO CONSTANTE — nada estático). Un editor te da un tema,
un LEDGER de datos (claves + valores ya verificados) y una lista de clips i2v disponibles.

TU FILOSOFÍA:
- La creatividad es ELEGIR EL SUJETO/METÁFORA CORRECTO y MOSTRARLO en movimiento, no poner una
  gráfica genérica. País pequeño -> MAPA que hace zoom al país. Reserva -> la MONEDA i2v. Comparar
  -> barras que crecen. Cifra clímax -> conteo grande. Piensa en IMÁGENES que frenan el scroll.
- Cada beat debe MOVERSE. Prohibido lo estático.
- Para CADA beat propón 2-3 OPCIONES distintas (cada una un `scene` LISTO del menú), di el porqué,
  y marca cuál RECOMIENDAS (índice). El humano elige; tú no decides solo.

MENÚ CERRADO de `scene` (usa EXACTAMENTE estos tipos y campos):
- {"type":"cover","kicker":"...","lines":[{"text":".."},{"text":"..","accent":true}],"foot":".."}
- {"type":"mapzoom","countryName":"<nombre EN INGLÉS d3>","iso2":"XX","label":"<MAYÚS>","region":["Vecino1","Vecino2"],"kicker":".."}
- {"type":"bignum","label":"..","prefix":"$","suffix":"M USD"|"","bind":"<clave_ledger>"}
- {"type":"compare","kicker":"..","prefix":"$","left":{"tag":"..","bind":"<clave>"},"right":{"tag":"..","bind":"<clave>"},"winner":"left"|"right","note":".."}
- {"type":"fallchart","kicker":"..","fromLabel":"..","toLabel":"..","prefix":"$","bind_from":"<clave>","bind_to":"<clave>","bind_delta":"<clave>","axisRight":"..","note":".."}
- {"type":"payoff","kicker":"..","prefix":"$","suffix":"..","bind":"<clave>","deltaText":"..","body":".."}
- {"type":"pictogram","kicker":"..","label":"de cada 100 ...","total":100,"highlight":<n o "bind":"<clave>">,"color":"green"|"accent","note":".."}  (X de 100, muy dinámico)
- {"type":"proportion","kicker":"..","label":"¿a dónde va...?","segments":[{"tag":"..","pct":50,"color":"ink"},{"tag":"..","pct":30,"color":"accent"},{"tag":"..","pct":20,"color":"green"}],"note":".."}  (desglose, la suma de pct = 100)
- {"type":"level","kicker":"..","label":"..","fillPct":<n o "bind":"<clave>">,"color":"green"|"accent","note":".."}  (recipiente que se llena: metas/cobertura)
- {"type":"timeline","kicker":"..","label":"cómo llegamos aquí","events":[{"year":"2021","text":"..","accent":true},{"year":"2024","text":".."}],"note":".."}  (paso a paso, 3-5 eventos)
- {"type":"plate","kicker":"..","src":"<clip i2v del manifest>","caption":"..","logo":"logos/bitcoin.svg"(opcional),"note":".."}
- {"type":"hero_i2v","src":"<clip i2v>","kicker":"..","caption":"..","punch":".."}
- {"type":"close","headline":[{"text":".."},{"text":"..","accent":true}],"sub":"..","cta":"Guarda esto"}

REGLAS DURAS:
- DATOS: los beats que muestran una cifra NO llevan números crudos: llevan `bind`/`bind_from`/etc.
  a una CLAVE del ledger que te doy. Nunca inventes una cifra ni una clave que no exista.
- i2v: `src` SOLO de la lista de clips disponibles. Máx 1-2 beats i2v por reel.
- MAPAS/banderas = el tipo mapzoom (código, no i2v). countryName en INGLÉS (nombre d3, p.ej. "El Salvador").
- La VO redondea en palabras ("alrededor de..."); el visual muestra la cifra exacta (del ledger).
- Arco: 4-6 beats, hook -> ≥2 datos visuales DISTINTOS -> clímax -> cierre/CTA. No repitas type consecutivo.
- Empieza FUERTE y en movimiento (un mapzoom o un hero i2v como b1 frena el scroll mejor que texto).

SALIDA: SOLO JSON (sin markdown):
{"tema":"..","vision":"la gran idea en una frase","lane":"noticia"|"evergreen","beats":[
  {"id":"b1","rol":"hook|dato|climax|cierre","idea":"qué cuenta",
   "opciones":[{"titulo":"nombre corto de la opción","por_que":"por qué frena el scroll",
                "vo":"narración del beat","scene":{..menú..}}, ...2-3..],
   "recomendado":0} ]}"""


def call_claude(user, max_tokens=8000):
    body = json.dumps({"model": MODEL, "max_tokens": max_tokens, "system": SYSTEM,
                       "messages": [{"role": "user", "content": user}]}).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST")
    req.add_header("x-api-key", load_key())
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=240) as r:
        resp = json.loads(r.read())
    txt = "".join(b.get("text", "") for b in resp.get("content", []))
    stop = resp.get("stop_reason")
    (HERE / "out" / "_treatments").mkdir(parents=True, exist_ok=True)
    (HERE / "out" / "_treatments" / "_raw.txt").write_text(txt, encoding="utf-8")
    start = txt.find("{")
    if start < 0:
        raise SystemExit(f"el director no devolvió JSON (stop_reason={stop})")
    try:
        obj, _ = json.JSONDecoder().raw_decode(txt[start:])  # 1er objeto válido, ignora lo que siga
        return obj
    except json.JSONDecodeError as e:
        raise SystemExit(f"JSON inválido (stop_reason={stop}, {e}); crudo en out/_treatments/_raw.txt")


def ideate(tema, ds_raw):
    keys = {k: v.get("value", "(computed)") for k, v in ds_raw.get("figures", {}).items()}
    user = (f"TEMA: {tema}\n\nLEDGER (claves disponibles para bind):\n{json.dumps(keys, ensure_ascii=False, indent=2)}\n\n"
            f"CLIPS i2v DISPONIBLES:\n{json.dumps(I2V_MANIFEST, ensure_ascii=False, indent=2)}\n\n"
            f"CARRIL: {ds_raw.get('lane','evergreen')}\n\n"
            "Dame el TRATAMIENTO con 2-3 opciones por beat. Sé ULTRA creativo y en movimiento constante.")
    return call_claude(user)


def compile_treatment(tr, choices, ds_raw):
    """Aterriza las elecciones (índice por beat) a un reel_def, resolviendo binds desde el ledger."""
    from datasheet import Datasheet
    vals = Datasheet(ds_raw["figures"], ds_raw.get("lane", "evergreen")).resolve()

    def resolve_num(bind, suffix=""):
        v = vals[bind]
        return round(v / 1e6) if str(suffix).strip().upper().startswith("M") else round(v)

    beats = []
    for i, b in enumerate(tr["beats"]):
        opt = b["opciones"][choices[i] if i < len(choices) else b.get("recomendado", 0)]
        sc = json.loads(json.dumps(opt["scene"]))  # copia
        t = sc.get("type")
        # resolver binds -> valores (el director no teclea números)
        if t in ("bignum", "payoff") and "bind" in sc:
            sc["value"] = resolve_num(sc.pop("bind"), sc.get("suffix", ""))
        if t == "compare":
            for side in ("left", "right"):
                if side in sc and "bind" in sc[side]:
                    sc[side]["value"] = resolve_num(sc[side].pop("bind"), sc.get("suffix", ""))
        if t == "fallchart":
            for f in ("from", "to", "delta"):
                bk = sc.pop(f"bind_{f}", None)
                if bk:
                    sc[f] = resolve_num(bk, sc.get("suffix", ""))
        if t == "pictogram" and "bind" in sc:
            sc["highlight"] = resolve_num(sc.pop("bind"))
        if t == "level" and "bind" in sc:
            sc["fillPct"] = resolve_num(sc.pop("bind"))
        beats.append({"id": b.get("id", f"b{i+1}"), "vo": opt["vo"], "scene": sc})
    return {"slug": ds_raw["slug"], "edition": tr.get("edition", "INFORME 2026"),
            "source": ds_raw.get("_source_line", "Fuente: ver ledger"),
            "lane": ds_raw.get("lane", "evergreen"), "beats": beats}


def print_treatment(tr):
    print(f"\n╔═ TRATAMIENTO: {tr.get('tema')}")
    print(f"║  visión: {tr.get('vision')}  ·  carril: {tr.get('lane')}\n")
    for i, b in enumerate(tr["beats"]):
        print(f"── beat {i} [{b.get('rol')}] — {b.get('idea')}")
        for j, o in enumerate(b["opciones"]):
            star = " ★REC" if j == b.get("recomendado", 0) else "     "
            print(f"  {star} [{j}] {o['titulo']}  ({o['scene'].get('type')})")
            print(f"         {o['por_que']}")
        print()


if __name__ == "__main__":
    tema = sys.argv[1]
    ds_raw = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    compile_arg = next((a for a in sys.argv if a.startswith("--compile")), None)
    tr = ideate(tema, ds_raw)
    (HERE / "out" / "_treatments").mkdir(parents=True, exist_ok=True)
    (HERE / "out" / "_treatments" / f"{ds_raw['slug']}.json").write_text(json.dumps(tr, ensure_ascii=False, indent=2), encoding="utf-8")
    print_treatment(tr)
    if compile_arg is not None:
        rest = compile_arg.split("=", 1)
        choices = [int(x) for x in rest[1].split(",")] if len(rest) > 1 and rest[1] else [b.get("recomendado", 0) for b in tr["beats"]]
        reel = compile_treatment(tr, choices, ds_raw)
        out = HERE / "out" / "_treatments" / f"{ds_raw['slug']}_reeldef.json"
        out.write_text(json.dumps(reel, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✓ reel_def compilado -> {out}")
