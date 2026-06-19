# -*- coding: utf-8 -*-
# Ensamblador Dinero IA v2 (Remotion nativo 9:16):
#   guion.json -> VO ElevenLabs con timestamps -> beats Remotion (duracion atada a la voz)
#   -> concat -> subs ASS -> mezcla (musica ducked + VO loudnorm + SFX) -> master
#   -> Filtro C (filter_c_prepare.py) se corre aparte sobre el master.
# Uso: python build916.py guion_X.json [vo|render|assemble|all]
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import cache
from post_finish import finish_chain  # acabado filmico opcional (A5); no-op sin "finish"

HERE = Path(__file__).parent
ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
REMOTION_DIR = ROOT / "infra" / "remotion-render"
MUSIC = str(ROOT / "music_floating_cities.mp3")
SFX_DIR = ROOT / "projects" / "dinero-ia" / "infra" / "ae-pipeline" / "templates" / "modern_counter" / "sfx"
# Packs Envato (M11): si existen, tienen prioridad; si no, fallback a lo de arriba
ENVATO_AUDIO = Path(r"C:\Users\manup\envato_audio")
ENVATO_MUSIC_DIR = ENVATO_AUDIO / "music"
ENVATO_SFX_DIR = ENVATO_AUDIO / "sfx"


# track default del pack Envato (mood dark/tension para finanzas); se puede
# sobreescribir por guion con "music": "music_xxx.mp3". Loopea + trim al total.
ENVATO_MUSIC_DEFAULT = "music_minimaltechno_01.mp3"


def pick_music(guion):
    # el guion puede pedir track especifico: "music": "music_dark_01.mp3"
    req = guion.get("music")
    if req:
        for d in (ENVATO_MUSIC_DIR, ROOT):
            cand = d / req
            if cand.exists():
                return str(cand)
        print(f"MUSIC WARN: '{req}' no existe, uso default")
    dft = ENVATO_MUSIC_DIR / ENVATO_MUSIC_DEFAULT
    if dft.exists():
        return str(dft)
    return MUSIC


def pick_sfx(name):
    # sfx del guion puede traer extension o no; busca primero en pack Envato.
    # nombres genericos del guion (whoosh/tick/impact) -> match por prefijo
    # (whoosh -> whoosh_01.wav), evitando variantes "_dramatic".
    if ENVATO_SFX_DIR.exists():
        for fname in (name + ".wav", name + ".mp3", name):
            cand = ENVATO_SFX_DIR / fname
            if cand.exists():
                return cand
        hits = sorted(p for p in ENVATO_SFX_DIR.glob(f"{name}_*")
                      if "dramatic" not in p.stem)
        if hits:
            return hits[0]
    for fname in (name + ".wav", name + ".mp3", name):
        cand = SFX_DIR / fname
        if cand.exists():
            return cand
    return SFX_DIR / (name + ".wav")

sys.path.insert(0, str(ROOT / "infra" / "voz"))
from tts_timestamps import DEFAULT_VOICE, load_env, tts_beat  # noqa: E402

LEAD, TAIL = 0.25, 1.10  # cola larga: el hueco audible entre voces = LEAD+TAIL-XFADE = 1.0s
XFADE = 0.35             # disolvencia visual; el respiro real lo da el DIP de musica
FPS = 30

ELEVEN_MODEL = "eleven_v3"  # entra al key de cache del VO; cambiarlo lo invalida


def run(args, cwd=None):
    p = subprocess.run(args, capture_output=True, text=True, cwd=cwd, shell=False)
    if p.returncode != 0:
        print("CMD ERR:", " ".join(str(a) for a in args))
        print((p.stderr or p.stdout)[-3000:])
        raise SystemExit(1)
    return p


def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


# ---------- etapa 1: voz con timestamps ----------
def gen_vo(guion, out_dir: Path):
    vo_dir = out_dir / "vo"
    vo_dir.mkdir(parents=True, exist_ok=True)
    key = load_env()["ELEVENLABS_API_KEY"]
    voice = guion.get("voice", DEFAULT_VOICE)
    for b in guion["beats"]:
        mp3 = vo_dir / f"{b['id']}.mp3"
        wjson = vo_dir / f"{b['id']}.words.json"
        # cache content-addressed: el VO depende de voz + modelo + TEXTO. Editar
        # b["vo"] cambia el key y re-graba (y aguas abajo wav/render). adopt=True:
        # VO preexistente sin sidecar se ADOPTA (no re-pagar ElevenLabs al migrar).
        ck = cache.key("tts.v1", ELEVEN_MODEL, voice, b["vo"])
        if (mp3.exists() and wjson.exists()
                and not cache.need_build(mp3, ck, "tts.v1", adopt=True)):
            print("VO skip", b["id"])
            continue
        words = tts_beat(key, voice, b["vo"], mp3)
        wjson.write_text(json.dumps(words, indent=2, ensure_ascii=False),
                         encoding="utf-8")
        cache.stamp(mp3, ck, "tts.v1")
        print(f"VO ok {b['id']}  {len(words)} palabras  {words[-1]['end']:.2f}s")


# ---------- etapa 2: render Remotion por beat ----------
def _norm_word(w):
    return re.sub(r"[^\wáéíóúüñ]", "", w.lower())


def apply_cues(b, props, out_dir: Path, frames: int):
    """Sincroniza la animacion del beat con los timestamps de la voz."""
    words = json.loads((out_dir / "vo" / f"{b['id']}.words.json")
                       .read_text(encoding="utf-8"))

    def word_frame(target, which):
        # "palabra:N" = N-esima ocurrencia (default 1)
        tgt, _, occ = target.partition(":")
        occ = int(occ) if occ else 1
        tgt = _norm_word(tgt)
        seen = 0
        for w in words:
            if _norm_word(w["word"]) == tgt:
                seen += 1
                if seen == occ:
                    return int(round((LEAD + w[which]) * FPS))
        print(f"CUE WARN: '{target}' no esta en la voz de {b['id']}")
        return None

    cues = b.get("cues", {})
    if cues.get("growWords"):
        gf = [word_frame(w, "start") for w in cues["growWords"]]
        if all(f is not None for f in gf):
            props["growFrames"] = gf
    if cues.get("pulseWords"):
        pf = [word_frame(w, "start") for w in cues["pulseWords"]]
        if all(f is not None for f in pf):
            props["pulseFrames"] = pf
    if cues.get("countEndWord"):
        f = word_frame(cues["countEndWord"], "end")
        if f is not None:
            props["countEndFrame"] = f
    if cues.get("breakWord"):
        f = word_frame(cues["breakWord"], "start")
        if f is not None:
            props["breakFrame"] = f
    if cues.get("leftEndWord"):
        f = word_frame(cues["leftEndWord"], "end")
        if f is not None:
            props["leftEndFrame"] = f
    if cues.get("rightEndWord"):
        f = word_frame(cues["rightEndWord"], "end")
        if f is not None:
            props["rightEndFrame"] = f
    if b["type"] == "BeatKinetic":
        # estrofas (orden global estrofa->linea->palabra) o lines legacy
        if "stanzas" in b["props"]:
            toks = [w for st in b["props"]["stanzas"] for line in st for w in line]
        else:
            toks = [w for line in b["props"]["lines"] for w in line]
        speech_end = int(round((LEAD + words[-1]["end"]) * FPS))
        props["startFrame"] = int(LEAD * FPS) + 2
        props["wordSpacing"] = max(
            3, (speech_end - props["startFrame"]) // max(len(toks), 1))
        # sync real: cada token kinetico se revela en el timestamp de SU palabra
        # en la voz (match secuencial normalizado). Si todos casan, se usa.
        wf, wi = [], 0
        for tk in toks:
            tgt = _norm_word(tk["text"])
            found = None
            j = wi
            while j < len(words):
                if _norm_word(words[j]["word"]) == tgt:
                    found = int(round((LEAD + words[j]["start"]) * FPS))
                    wi = j + 1
                    break
                j += 1
            wf.append(found)
        if all(f is not None for f in wf):
            props["wordFrames"] = wf
        else:
            print(f"KINETIC WARN: tokens sin match en voz de {b['id']}, "
                  "uso espaciado parejo")
    return props


def ensure_caricatures(guion):
    # beats de personaje necesitan su PNG cacheado; lo generamos (gpt-image)
    # una sola vez por slug antes de renderizar.
    slugs = {b["props"]["imageSlug"] for b in guion["beats"]
             if b["type"] == "BeatCharacter" and b.get("props", {}).get("imageSlug")}
    if not slugs:
        return
    from gen_caricature import gen
    for s in sorted(slugs):
        gen(s)


def render_beats(guion, out_dir: Path):
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    ensure_caricatures(guion)
    beats = guion["beats"]
    # sha del arbol de fuentes Remotion (una vez por corrida): si se edita
    # CUALQUIER componente/theme/StudioScene, el key de TODO render cambia y se
    # re-renderiza. Cierra el bug de "edite el .tsx pero salio el mp4 viejo".
    src_sha = cache.tree_sha(REMOTION_DIR / "src")
    for i, b in enumerate(beats):
        dst = raw_dir / f"{b['id']}.mp4"
        vo_d = dur(out_dir / "vo" / f"{b['id']}.mp3")
        frames = int(round((LEAD + vo_d + TAIL) * FPS))
        props = apply_cues(b, dict(b["props"], durationInFrames=frames),
                           out_dir, frames)
        # Whips de costura DESACTIVADOS: las transiciones ahora son xfade real
        # en assemble() (disolvencia + dip de musica). Hornear los whips peleaba
        # con la disolvencia. b["trans"] queda en el guion pero se ignora.
        props_json = json.dumps(props, ensure_ascii=False)
        props_file = raw_dir / f"{b['id']}.props.json"
        props_file.write_text(props_json, encoding="utf-8")
        # cache content-addressed: el render depende de type + props (frames
        # atados a la voz + cues de words.json) + scale/crf + CODIGO FUENTE
        # (src_sha). Si se re-graba la voz, frames/cues cambian; si se edita el
        # componente, src_sha cambia -> se re-renderiza (antes el mp4 viejo se
        # reusaba y props.json / el .tsx divergian en silencio). Recipe v2 = se
        # agrego src_sha al key (invalida los renders viejos una vez).
        ck = cache.key("remo.v2", b["type"], props_json,
                       cache.file_sha(out_dir / "vo" / f"{b['id']}.words.json"),
                       src_sha, "scale2", "crf16", LEAD, TAIL, FPS)
        # adopt=False en renders: si NO hay sidecar (migracion / git clean / 1a
        # vez con el cache nuevo) NO se adopta el mp4 viejo a ciegas -> se
        # RE-RENDERIZA. El render es $0 (CPU local) y reproducible, asi la
        # garantia "edite el .tsx -> sale el render nuevo" es hermetica incluso
        # sin baseline. (El VO sigue adopt=True porque cuesta $; el render no.)
        # Con adopt=True aqui, un render sin sidecar se "bendecia" como vigente y
        # servia el mp4 viejo = el bug de artefacto-viejo que P0 mata.
        if dst.exists() and not cache.need_build(dst, ck, "remo.v2", adopt=False):
            print("RENDER skip", b["id"])
            continue
        # --scale=2: supersampling 2x (2160x3840). El downscale a 1080x1920
        # con lanczos en el concat da anti-aliasing real en texto y graficas
        # (sin esto los bordes "shimmer" y se ven baratos = el "no es HD").
        # --timeout=600000: a 2x (4x pixeles/frame) la CPU se satura y en algun
        # tab el callback de carga de la fuente se queda sin turno (starvation),
        # no por cuelgue real. Con timeout amplio ese tab resuelve la fuente en
        # cuanto los otros terminan y liberan CPU. 180s reventaba en beats largos.
        run(["npx.cmd", "remotion", "render", b["type"], str(dst),
             f"--props={props_file}", "--concurrency=4", "--crf=16",
             "--scale=2", "--timeout=600000"],
            cwd=str(REMOTION_DIR))
        cache.stamp(dst, ck, "remo.v2")
        print(f"RENDER ok {b['id']}  {frames}f ({frames / FPS:.2f}s)")


# ---------- etapa 3: ensamblado (mezcla validada de build.py) ----------
def norm_vo(src, dst, I=-16.0, TP=-1.5, LRA=11.0):
    p = subprocess.run(["ffmpeg", "-i", str(src), "-af",
                        f"loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[\s\S]*?\}", p.stderr)
    d = json.loads(m.group(0))
    af = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={d['input_i']}"
          f":measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
          f":measured_thresh={d['input_thresh']}"
          f":offset={d['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-i", str(src), "-af", af, "-ar", "48000", str(dst)])


def assemble(guion, out_dir: Path):
    tmp = out_dir / "_asm"
    tmp.mkdir(parents=True, exist_ok=True)
    # Solape de xfade DENTRO del silencio LEAD/TAIL: entre dos VOs queda
    # LEAD+TAIL-xf de silencio, asi la voz nunca se pisa. video y audio salen
    # del MISMO start[i] -> no se desfasan.
    beats = guion["beats"]
    n = len(beats)
    raw, cum = [], 0.0
    for b in beats:
        vd = dur(out_dir / "vo" / f"{b['id']}.mp3")
        sd = LEAD + vd + TAIL
        raw.append((b, vd, sd, cum))
        cum += sd
    xf = min(XFADE, min(r[2] for r in raw) * 0.4) if n > 1 else 0.0
    segs = []
    for i, (b, vd, sd, ns) in enumerate(raw):
        start = ns - i * xf
        # fin/inicio AUDIBLE de la voz (ultima/primera palabra), NO el borde del
        # mp3: las voces traen silencio de cola (b2_pais ~0.48s) y centrar el dip
        # en el borde del mp3 lo dejaba ~0.25s tarde -> la musica subia justo al
        # callar la voz (lo que Manuel oye como "encimada" en el seg 21).
        wj = out_dir / "vo" / f"{b['id']}.words.json"
        try:
            ww = json.loads(wj.read_text(encoding="utf-8"))
            a_first, a_last = float(ww[0]["start"]), float(ww[-1]["end"])
        except Exception:
            a_first, a_last = 0.0, vd
        segs.append(dict(b, vo_dur=vd, seg=sd, start=start,
                         vo_start=start + LEAD,
                         aud_start=start + LEAD + a_first,
                         aud_end=start + LEAD + a_last))
    total = cum - (n - 1) * xf
    print(f"TIMELINE {total:.2f}s / {n} beats  (xfade {xf:.2f}s)")
    # golden estructural: lo que el QC de ENTREGA usa para ubicar cada medicion
    # (aud_start/aud_end por beat = donde DEBE estar la voz en el master). Todo
    # esto ya se calculo arriba; aqui solo se vuelca como sidecar del entregable.
    timeline = {
        "slug": guion["slug"], "total": total, "xfade": xf, "fps": FPS,
        "lead": LEAD, "tail": TAIL, "n": n,
        "beats": [{"id": s["id"], "type": s["type"],
                   "start": round(s["start"], 4),
                   "vo_start": round(s["vo_start"], 4),
                   "aud_start": round(s["aud_start"], 4),
                   "aud_end": round(s["aud_end"], 4),
                   "seg": round(s["seg"], 4),
                   "vo_dur": round(s["vo_dur"], 4)} for s in segs],
    }
    timeline_path = out_dir / f"{guion['slug']}.timeline.json"
    timeline_path.write_text(json.dumps(timeline, indent=2, ensure_ascii=False),
                             encoding="utf-8")

    # concat FILTER (no demuxer): une frames decodificados exactos; el demuxer
    # suma duraciones de contenedor con redondeo y pierde/duplica frames.
    # Re-encode unico crf 15 (fuente Remotion crf 16).
    silent = tmp / "silent.mp4"
    vins = []
    for s in segs:
        vins += ["-i", str(out_dir / "raw" / (s["id"] + ".mp4"))]
    # raws 2160x3840 (supersampling 2x) -> downscale lanczos a 1080x1920 por
    # input, luego cadena de xfade=fade. offset[m] = Sum(seg[0..m]) - (m+1)*xf.
    seg = [s["seg"] for s in segs]
    # tpad clona el ultimo frame y trim fija cada input a EXACTAMENTE su seg: los
    # raws se renderizaron con TAIL viejo (0.50); aqui se rellenan a la cola nueva
    # (0.95) congelando el frame final -> mas silencio entre voces SIN re-render
    # (clave: las pestanas paralelas tocaron beats compartidos como VersusCards).
    # El freeze arranca en seg-XFADE, bajo la disolvencia -> imperceptible.
    pre = [f"[{i}:v]scale=1080:1920:flags=lanczos,format=yuv420p,setsar=1,"
           f"fps={FPS},tpad=stop_mode=clone:stop_duration=2,"
           f"trim=0:{seg[i]:.3f},setpts=PTS-STARTPTS[s{i}]" for i in range(n)]
    if n == 1:
        chain = pre + ["[s0]null[vbase]"]
    else:
        cur, steps = "[s0]", []
        for m in range(n - 1):
            off = sum(seg[: m + 1]) - (m + 1) * xf
            out = "[vbase]" if m == n - 2 else f"[vx{m}]"
            steps.append(f"{cur}[s{m + 1}]xfade=transition=fade:"
                         f"duration={xf:.3f}:offset={off:.3f}{out}")
            cur = out
        chain = pre + steps
    # apertura/cierre limpios desde/hacia negro. El xfade deja el video ~3-4
    # frames corto de `total` (cuantizacion de offsets/trim a frame), mientras el
    # audio se rellena a `total` EXACTO -> el track de video quedaba mas corto que
    # el de audio (av_match FAIL) y el fade-out (programado para cerrar en `total`)
    # se cortaba al ~75% sin llegar a negro. Se clona el ultimo frame y se recorta
    # a `total` ANTES del fade: el video casa con el audio y el fade cierra a negro.
    base = (f"[vbase]tpad=stop_mode=clone:stop_duration=1,"
            f"trim=0:{total:.3f},setpts=PTS-STARTPTS")
    fades = (f"fade=t=in:st=0:d=0.25,"
             f"fade=t=out:st={max(total - 0.5, 0):.3f}:d=0.5")
    # acabado filmico (A5) OPCIONAL: si el guion trae "finish": {bloom/grano/
    # vineta}, se inyecta entre el trim y el fade (el fade a negro queda ENCIMA,
    # asi apertura/cierre cierran limpios). Sin "finish" el grafo es IDENTICO al
    # de hoy -> no toca lo ya aprobado. Cero pase extra de re-encode.
    fin = guion.get("finish") or {}
    if fin:
        chain.append(f"{base}[vpre]")
        chain.append(finish_chain("[vpre]", "[vpost]", **fin))
        chain.append(f"[vpost]{fades}[v]")
    else:
        chain.append(f"{base},{fades}[v]")
    fc_v = ";".join(chain)
    run(["ffmpeg", "-y"] + vins + ["-filter_complex", fc_v, "-map", "[v]",
         "-c:v", "libx264", "-preset", "slow", "-crf", "15",
         "-pix_fmt", "yuv420p", str(silent)])

    norm = []
    for s in segs:
        npath = tmp / f"vn_{s['id']}.wav"
        src = out_dir / "vo" / f"{s['id']}.mp3"
        # Cache CONTENT-ADDRESSED: el wav loudnorm depende de los BYTES del mp3
        # (+ params I/TP/LRA). Si se re-graba la voz, sha(mp3) cambia -> el key no
        # matchea -> se reconstruye. Mata el bug de raiz: el wav viejo era
        # imposible de detectar por mtime (git checkout / pestanas paralelas /
        # re-toma de igual duracion lo dejaban pasar). adopt=False: el wav es
        # barato y es el epicentro -> se rehace y queda content-addressed de una.
        ck = cache.key("loud.v1", -16.0, -1.5, 11.0, cache.file_sha(src))
        if cache.need_build(npath, ck, "loud.v1", adopt=False):
            norm_vo(src, npath)
            cache.stamp(npath, ck, "loud.v1")
        # Guard RUIDOSO (cinturon-y-tirantes, independiente del cache): lo que
        # SUENA (wav) debe durar ~lo que se USO para colocar (dur del mp3). Si
        # divergen >0.25s, abortar antes de entregar voces encimadas en silencio.
        wv = dur(npath)
        if abs(wv - s["vo_dur"]) > 0.25:
            raise SystemExit(
                f"ABORT vn_{s['id']}: wav={wv:.2f}s vs mp3={s['vo_dur']:.2f}s "
                f"(dif {wv - s['vo_dur']:+.2f}s) -> voces encimadas. "
                f"Borra out/<slug>/_asm/vn_*.wav y re-ensambla.")
        norm.append(npath)

    inputs = ["-i", pick_music(guion)]
    for npth in norm:
        inputs += ["-i", str(npth)]
    sfx_inputs = []
    for s in segs:
        if s.get("sfx"):
            sfx_inputs.append((pick_sfx(s["sfx"]), s["start"]))
    for sf, _ in sfx_inputs:
        inputs += ["-i", str(sf)]

    # dip de musica (~-5 dB, ~0.4s) centrado en cada costura = respiro audible
    # (hoy el sidechain SUBE la musica en los huecos del VO; el dip lo compensa)
    # respiro: dip de musica centrado en el HUECO real entre voces (medio del
    # silencio [fin VO_m, inicio VO_{m+1}]), no en el centro del xfade de video.
    # respiro centrado en el HUECO AUDIBLE real (fin de la ultima palabra de m ->
    # inicio de la primera palabra de m+1), NO en el borde del mp3.
    breaths = [(segs[m]["aud_end"] + segs[m + 1]["aud_start"]) / 2
               for m in range(n - 1)]
    if breaths:
        # super-gaussiana exp(-u^8), u=(t-S)/1.05: fondo PLANO y ANCHO con paredes
        # casi verticales. El dip se aplica ANTES del sidechain (que solo REDUCE)
        # -> el dip es el TECHO de la musica en el hueco. El bottom plano cubre
        # TODO el hueco audible: ~-23 dB en +-0.5s (huecos de 1.0s) y aun ~-18 dB
        # en +-0.74s (el hueco ancho de 1.48s tras b2_pais). Las paredes recuperan
        # la musica ~0.6s DENTRO de la voz (ahi el sidechain la agacha). El SFX de
        # transicion cae en el hueco y puntua el respiro -> no un dropout muerto.
        def _sg(S):
            u = f"((t-{S:.3f})/1.05)"
            q = f"(({u}*{u})*({u}*{u}))"   # u^4
            return f"exp(-{q}*{q})"          # exp(-u^8)
        bumps = "+".join(_sg(S) for S in breaths)
        dip = f",volume=eval=frame:volume='1-0.93*({bumps})'"
    else:
        dip = ""
    fc = [f"[0:a]aloop=loop=-1:size=2e9,atrim=0:{total:.3f},volume=0.30{dip},"
          f"afade=t=out:st={total - 0.8:.3f}:d=0.8[mus]"]
    vo_labels = []
    for i, s in enumerate(segs):
        ms = int(s["vo_start"] * 1000)
        fc.append(f"[{i + 1}:a]adelay={ms}|{ms}[v{i}]")
        vo_labels.append(f"[v{i}]")
    # apad: sidechaincompress termina cuando se acaba el sidechain; sin pad
    # el audio queda corto (TAIL del ultimo beat) y el mux -t total dejaria un
    # tail mudo (video hasta total, audio cortado antes)
    fc.append("".join(vo_labels)
              + f"amix=inputs={len(vo_labels)}:normalize=0,"
              + f"apad=whole_dur={total:.3f}[vo]")
    fc.append("[vo]asplit=3[vo_mix][vo_sc][vo_stem]")
    fc.append("[mus][vo_sc]sidechaincompress=threshold=0.03:ratio=6:attack=5:release=260[ducked]")
    mix_in = ["[ducked]", "[vo_mix]"]
    for j, (_, st) in enumerate(sfx_inputs):
        idx = 1 + len(norm) + j
        ms = int(st * 1000)
        fc.append(f"[{idx}:a]volume=0.45,adelay={ms}|{ms}[s{j}]")
        mix_in.append(f"[s{j}]")
    fc.append("".join(mix_in) + f"amix=inputs={len(mix_in)}:normalize=0[mix]")
    # loudnorm hace limiting de TRUE-peak (inter-sample), no solo sample-peak
    # como alimiter: TP=-1.5 garantiza el <= -1 dBTP que exige el QC. I=-16 deja
    # el integrado en target sin pumpear (LRA del mix ya es bajo).
    fc.append("[mix]loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
    audio = tmp / "audio.m4a"
    vo_stem = out_dir / f"{guion['slug']}.vo_stem.wav"
    # 2 salidas en UNA corrida: el master de audio (AAC) + el vo_stem (SOLO voz,
    # PCM, antes de musica/sidechain) que el QC de entrega mide con silencedetect
    # para ver los huecos REALES entre voces sin la musica encima.
    run(["ffmpeg", "-y"] + inputs + ["-filter_complex", ";".join(fc),
         "-map", "[aout]", "-t", f"{total:.3f}", "-c:a", "aac", "-b:a", "192k",
         "-ar", "48000", str(audio),
         "-map", "[vo_stem]", "-t", f"{total:.3f}", "-c:a", "pcm_s16le",
         "-ar", "48000", str(vo_stem)])

    final = out_dir / f"{guion['slug']}_FINAL_916.mp4"
    # -c:a copy: audio.m4a ya es AAC 192k con el true-peak controlado por
    # loudnorm; re-encodear aqui re-introduce picos inter-sample > -1 dBTP.
    # -t total (NO -shortest): con -c:v copy, -shortest corta el ultimo GOP por
    # los B-frames (DTS!=PTS) y deja el video ~4 frames corto del audio
    # (av_match FAIL). Audio y video ya estan acotados a `total` por construccion
    # (apad whole_dur + tpad/trim), asi que -t total casa ambos sin truncar.
    run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
         "-c:a", "copy", "-dn", "-t", f"{total:.3f}", str(final)])
    print("WROTE", final, f"{dur(final):.2f}s")

    # QC de ENTREGA sobre el MP4 ENTREGADO (no un intermedio): mide los huecos
    # reales entre voces en el vo_stem + loudness/TP/duracion. exit!=0 BLOQUEA la
    # entrega. Esto es lo que habria atrapado el bug de seg 21/44 en el artefacto
    # final, las 4 veces (antes solo se validaba vn_*.wav intermedio).
    qc = subprocess.run(
        [sys.executable, str(ROOT / "infra" / "qc" / "filter_delivery.py"),
         str(final), str(timeline_path), str(vo_stem)])
    if qc.returncode != 0:
        raise SystemExit(
            f"ENTREGA BLOQUEADA por QC: ver {guion['slug']}_delivery_qc.json")
    return final


def main():
    guion_file = sys.argv[1]
    stage = sys.argv[2] if len(sys.argv) > 2 else "all"
    guion = json.loads(Path(guion_file).read_text(encoding="utf-8-sig"))
    out_dir = HERE / "out" / guion["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    if stage in ("vo", "all"):
        gen_vo(guion, out_dir)
    if stage in ("render", "all"):
        render_beats(guion, out_dir)
    if stage in ("assemble", "all"):
        assemble(guion, out_dir)


if __name__ == "__main__":
    main()
