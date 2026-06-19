# -*- coding: utf-8 -*-
"""
producir.py - ORQUESTADOR de Dinero LATAM (reemplaza el cascaron de n8n).

Hace el video de punta a punta y lo deja LISTO para que la NUBE lo publique sin
tu PC. Encadena las piezas que ya existen y estan probadas:

  1) cola.py         elige el SIGUIENTE tema producible (carril news primero,
                     si no, evergreen). El tema YA debe tener un guion autorado.
  2) build916.py all voz ElevenLabs (costo ~centavos, ya presupuestado) + render
                     Remotion ($0) + ensamblado FFmpeg ($0) + QC de ENTREGA DURO
                     (filter_delivery: si las voces se enciman o el loudness/dur
                     fallan, build916 sale !=0 y AQUI nos detenemos).
  3) caption.py      caption + hashtags desde el guion ($0, sin API).
  4) upload_supabase sube el MP4 a Storage publico ($0) -> URL publica (la usan
                     Telegram para el preview Y la nube para publicar).
  5) telegram_bot    GATE HUMANO: te manda el video con [OK]/[Basura] y espera tu
                     tap desde el celular. Nada se publica sin tu OK.
  6) enqueue.py      al aprobar, encola en Supabase (lane = carril del tema). El
                     cron de la nube (publish-due, ~8pm CDMX) lo postea SIN PC.
  7) aprobar.py      cierra el loop: ledger (no repetir) + marca el tema producido.

COSTO / CONGELAMIENTO: NO llama a ninguna API de planner. EXIGE que el guion
`guion_<slug>.json` YA exista (lo escribo yo en sesion = $0). Si no existe, se
detiene y te dice como autorarlo. El unico costo por corrida es la voz de
ElevenLabs (centavos), que ya estaba presupuestada.

"PRENDER LA COMPU Y YA": con un guion autorado en la cola, esto corre solo de
punta a punta; tu unica intervencion es el tap de Telegram. Apagas la compu y la
nube publica a su hora.

USO:
  python producir.py                      # siguiente tema producible de la cola
  python producir.py --slug edu_efecto_latte_latam
  python producir.py --carril evergreen   # fuerza un carril
  python producir.py --dry-run            # planifica + caption, SIN gastar ni publicar
  python producir.py --skip-build         # reusa el MP4 ya renderizado (reintentos)
  python producir.py --timeout 7200 --ttl-hours 36
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent                       # infra/n8n
INFRA = HERE.parent                                # infra
ASSEMBLER = INFRA / "assembler"
DISTRIBUTION = INFRA / "distribution"
BUILD916 = ASSEMBLER / "build916.py"
UPLOAD = DISTRIBUTION / "upload_supabase.py"

for _p in (str(HERE), str(DISTRIBUTION), str(ASSEMBLER)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cola            # noqa: E402  (selector de la cola, lane-aware)
import caption         # noqa: E402  (caption/hashtags desde el guion)
import enqueue         # noqa: E402  (encolar en Supabase, idempotente)
import aprobar         # noqa: E402  (ledger + marcar producido)
import telegram_bot    # noqa: E402  (gate humano)
import build_story     # noqa: E402  (render del Story-teaser, $0)


def _log(step, msg):
    print(f"[producir] {step}  {msg}", flush=True)


def _guion_path(slug):
    return ASSEMBLER / f"guion_{slug}.json"


def _load_guion(slug):
    return json.loads(_guion_path(slug).read_text(encoding="utf-8-sig"))


# ---------------------------------------------------------------- 1) tema
def pick_topic(args):
    """Devuelve (slug, carril). Fuentes: --slug, o el siguiente de la cola."""
    if args.slug:
        slug = args.slug
        # carril: del --carril, o del propio guion si lo declara, o evergreen
        carril = args.carril
        if not carril and _guion_path(slug).exists():
            carril = (_load_guion(slug).get("carril") or "").lower() or None
        return slug, (carril or "evergreen")

    data = cola.load(args.cola)
    t = cola.siguiente(data, carril_filtro=args.carril)
    if t is None:
        raise SystemExit(
            "[producir] No hay tema PRODUCIBLE en la cola"
            + (f" (carril={args.carril})" if args.carril else "")
            + ". Llena las cifras de un tema (quita <<verificar>>) o pasa --slug. "
            "Ver: python cola.py list")
    brief = cola._brief(t)
    _log("1/7 tema", f"slug={brief['slug']} carril={brief['carril']} — {t.get('tema','')[:70]}")
    return brief["slug"], brief["carril"]


# ---------------------------------------------------------------- 2) build
def ensure_guion(slug):
    p = _guion_path(slug)
    if not p.exists():
        raise SystemExit(
            f"[producir] No existe {p.name}. El guion se AUTORA en sesion (yo lo "
            f"escribo, $0) o con el planner (API, costo — NO se llama solo por el "
            f"congelamiento). Crea {p.name} y reintenta.")
    return p


def build(slug, guion_file, skip_build):
    final = ASSEMBLER / "out" / slug / f"{slug}_FINAL_916.mp4"
    if skip_build and final.exists():
        _log("2/7 build", f"--skip-build: reuso {final.name} ({final.stat().st_size/1_048_576:.1f} MB)")
        return final
    _log("2/7 build", "build916.py all (voz ElevenLabs ~centavos + render $0 + QC duro)…")
    r = subprocess.run([sys.executable, str(BUILD916), str(guion_file), "all"],
                       cwd=str(ASSEMBLER))
    if r.returncode != 0:
        raise SystemExit(f"[producir] build916/QC fallo (rc={r.returncode}). "
                         f"Revisa {slug}_delivery_qc.json. NO se publica.")
    if not final.exists():
        raise SystemExit(f"[producir] build916 termino pero no encuentro {final}")
    _log("2/7 build", f"OK -> {final.name} ({final.stat().st_size/1_048_576:.1f} MB)")
    return final


# ------------------------------------------------------------- 3) caption
def make_caption(slug):
    g = _load_guion(slug)
    paths = caption.write_caption_files(g)  # out_caption_ig.txt + _tiktok.txt
    ig = caption.build_caption(g, "instagram")
    _log("3/7 caption", f"IG {len(ig)} chars -> {paths['instagram'].name} (+ tiktok)")
    return ig


# -------------------------------------------------------------- 4) upload
def _content_tag(path, n=10):
    """sha256 corto del MP4. Mismo contenido -> mismo nombre (idempotente);
    contenido distinto -> nombre/URL distinta -> Telegram y el CDN NO sirven la
    copia vieja cacheada (el re-render se VE de verdad)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def upload(slug, final):
    obj_name = f"{slug}-{_content_tag(final)}.mp4"  # cache-bust por contenido
    _log("4/7 upload", f"subiendo MP4 a Supabase Storage (publico, $0) -> {obj_name}…")
    r = subprocess.run([sys.executable, str(UPLOAD), str(final), "--name", obj_name],
                       cwd=str(DISTRIBUTION), capture_output=True, text=True)
    if r.stdout:
        print(r.stdout, end="")
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        raise SystemExit("[producir] upload_supabase fallo.")
    urls = [ln.strip() for ln in r.stdout.splitlines() if ln.strip().startswith("http")]
    if not urls:
        raise SystemExit("[producir] upload no devolvio URL publica.")
    _log("4/7 upload", f"URL publica lista ({urls[-1].split('/')[-1]})")
    return urls[-1]


# ---------------------------------------------------------------- 5) gate
def human_gate(slug, url, ig_caption, timeout, kind="post", tag=None):
    """Gate humano por Telegram. kind='post'|'story' cambia el encabezado/emoji y el
    boton (📲 STORY vs 🎬 POST) para que sepas QUE estas aprobando. tag casa tu tap con
    ESTE video; la Story usa tag=f'{slug}:story' para no chocar con el del post."""
    token, chat = telegram_bot._creds()
    tag = tag or slug
    label = "STORY" if kind == "story" else "POST"
    _log("5/7 gate", f"enviando {label} a Telegram, esperando tu tap [OK]/[Basura]…")
    telegram_bot.send_for_approval(token, chat, url, ig_caption, tag, kind=kind)
    decision = telegram_bot.wait_for_decision(token, chat, tag, timeout=timeout)
    _log("5/7 gate", f"decision {label} = {decision.upper()}")
    return decision


# ------------------------------------------------------- 6) encolar / 7) cerrar
def queue_and_close(slug, url, ig_caption, carril, final, ttl_hours):
    _log("6/7 cola", f"encolando en Supabase (lane={carril})…")
    res = enqueue.enqueue(slug, url, ig_caption, lane=carril, platform="instagram",
                          video_file=str(final), ttl_hours=ttl_hours)
    if res.get("skipped"):
        _log("6/7 cola", "ya estaba encolado/publicado (idempotente): no re-encolo.")
    _log("7/7 cierre", "ledger + marcar producido…")
    aprobar.aprobar(slug, fecha=date.today().isoformat())


# ------------------------------------------------------- pata opcional: STORY
def story_leg(slug, carril, args):
    """Tras aprobar el POST: arma + gatea + encola el STORY-TEASER del MISMO tema.

    El Story es CORTO (~6s, $0, sin voz) y SEPARADO del reel: te llega un 2o Telegram
    marcado 📲 STORY para que sepas que apruebas un teaser de 24h (no el reel). Si lo
    apruebas, se encola con media_type='story' y la nube lo sube junto al reel (mismo
    tick del cron de prime-time). Si lo rechazas o falla, el POST igual va — la Story
    es solo un anzuelo que jala trafico al post del dia, no un bloqueante.
    """
    guion_file = _guion_path(slug)
    try:
        _log("story", "render del teaser (StoryHook, $0, sin voz)…")
        story_mp4 = build_story.build_story(guion_file)
    except Exception as e:  # noqa: BLE001 — un fallo del teaser NUNCA tumba el post
        _log("story", f"no se pudo construir el Story ({e}). El post sigue; hoy sin teaser.")
        return
    _log("story", f"OK -> {story_mp4.name} ({story_mp4.stat().st_size/1_048_576:.1f} MB)")
    surl = upload(f"{slug}-story", story_mp4)
    decision = human_gate(slug, surl, "", args.timeout, kind="story", tag=f"{slug}:story")
    if decision != "approved":
        _log("story", f"Story {decision.upper()}: no se encola. El POST no se afecta.")
        return
    enqueue.enqueue(slug, surl, "", lane=carril, platform="instagram",
                    video_file=str(story_mp4), ttl_hours=args.ttl_hours, media_type="story")
    _log("story", "Story encolada (media_type=story). La nube la sube junto al reel.")


def run(args):
    slug, carril = pick_topic(args)
    guion_file = ensure_guion(slug)

    if args.dry_run:
        ig = make_caption(slug)
        _log("dry-run", "no se construye/sube/publica. Caption IG de muestra:")
        print("\n" + ig + "\n")
        _log("dry-run", f"LISTO: produciria slug={slug} carril={carril}. Quita --dry-run para correr.")
        return 0

    final = build(slug, guion_file, args.skip_build)
    ig = make_caption(slug)
    url = upload(slug, final)
    decision = human_gate(slug, url, ig, args.timeout)

    if decision != "approved":
        if decision == "rejected":
            aprobar.rechazar(slug, fecha=date.today().isoformat())
            _log("fin", f"RECHAZADO ❌. No se publica. Descartado de la cola: la "
                        f"PROXIMA corrida toma el SIGUIENTE tema. El MP4 quedo en "
                        f"out/{slug}/ por si lo quieres ver.")
        else:  # timeout: no hubo tap; NO se descarta (reintenta este tema luego)
            _log("fin", f"Sin decision (timeout). No se descarta: la proxima corrida "
                        f"REINTENTA este tema. El MP4 quedo en out/{slug}/.")
        return 2 if decision == "rejected" else 3

    queue_and_close(slug, url, ig, carril, final, args.ttl_hours)
    if args.story:
        story_leg(slug, carril, args)
    _log("fin", f"LISTO ✅  '{slug}' encolado y aprobado. La NUBE lo publica a su "
                f"hora (~8pm CDMX) SIN tu PC. Puedes apagar la compu.")
    return 0


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", help="produce este tema (default: siguiente de la cola)")
    ap.add_argument("--carril", choices=["news", "evergreen"],
                    help="fuerza el carril del selector / de la cola")
    ap.add_argument("--cola", default=str(cola.DEFAULT_COLA), help="ruta de temas_cola.json")
    ap.add_argument("--ttl-hours", type=int, default=36, help="TTL del lane news (default 36)")
    ap.add_argument("--timeout", type=int, default=7200, help="espera del tap de Telegram (s)")
    ap.add_argument("--skip-build", action="store_true", help="reusa el MP4 ya renderizado")
    ap.add_argument("--story", action=argparse.BooleanOptionalAction, default=True,
                    help="tras aprobar el post, arma+gatea+encola tambien el Story-teaser "
                         "(default: si). Usa --no-story para saltarlo.")
    ap.add_argument("--dry-run", action="store_true", help="planifica + caption, sin gastar ni publicar")
    args = ap.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
