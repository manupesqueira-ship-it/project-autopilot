"""assemble_masters.py — pipeline noticia→reel en el MUNDO DE LA PÁGINA (masters kit2).

Idéntica plomería probada de assemble_news.py (VO con timestamps por palabra →
timeline con land anclado a LA PALABRA → UN render → mezcla dirigida → gates QC
exit 1) pero renderiza la composición MastersReel (masters congelados, tokens
kit2). El movimiento NO se toca aquí: solo datos, duraciones desde la voz, y el
frame exacto donde cada cifra/palabra-acento aterriza.

Uso:  python assemble_masters.py treatment.json <slug>
Treatment beat: {type: hook|cifra|linea|barras|carrera|cierre, vo, props,
                 target_word?, trans?: cut|dip, transF?, min_s?, tail_s?}
Voz: ElevenLabs con timestamps por palabra — ALBERTO RODRÍGUEZ (serio narrativo,
voz 2 de la audición, elegida por Manuel 2026-07-04). Reusa la plomería probada
de infra/voz/tts_timestamps.py (with-timestamps + retries).
"""
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
REMOTION = ROOT / "infra" / "remotion-render"
QC = ROOT / "infra" / "qc"
SFX = Path(r"C:\Users\manup\envato_audio\sfx")
# Gate 07-08: rotación aprobada por Manuel — M1 "me encantan" + M2 "muy buena";
# M3/minimal_04/minimaltechno_01 RECHAZADAS. "No siempre lo mismo en cada reel"
# → rotación determinista por slug. La elección fina la puede pedir el creativo.
MUSIC_POOL = [
    Path(r"C:\Users\manup\envato_audio\music\music_tension_03.mp3"),      # M1 dramático
    Path(r"C:\Users\manup\envato_audio\music\music_techabstract_02.mp3"),  # M2 neutro-premium
]
FPS = 30
COMP = "MastersReel"
# LA VOZ DEL CANAL (audición msgs 138-144, Manuel eligió la 2): Alberto Rodríguez
VOICE_ID = "l1zE9xgNpUTaQCZzpNJa"
# RETRO 07-07 ("interrumpiste… ni medio segundo entre palabras"): el J-cut de
# 0.40s encimaba la voz del beat siguiente sobre la cola del anterior. FUERA
# J-cut: cada VO entra CON su visual; siempre queda TAIL de aire tras la última
# palabra, y un check DURO aborta el reel si el gap real baja de MIN_VO_GAP.
JCUT = 0.0
LEAD0 = 0.30
TAIL = 0.80
MIN_VO_GAP = 0.50
TRANS_F_DEFAULT = 14
# duraciones default por transición — misma fuente que el render (kit2)
TRANS_DEFAULTS = {
    k: v for k, v in json.loads(
        (REMOTION / "src" / "kit2" / "trans_defaults.json").read_text(encoding="utf-8")
    ).items() if isinstance(v, int)
}


def trans_frames(b: dict) -> int:
    """Frames de la transición SALIENTE de un beat (0 si es cut)."""
    t = b.get("trans", "cut")
    if t == "cut":
        return 0
    return int(b.get("transF", TRANS_DEFAULTS.get(t, TRANS_F_DEFAULT)))

sys.path.insert(0, str(ROOT / "infra" / "voz"))
import tts_timestamps as _tts  # noqa: E402
from tts_timestamps import load_env as _load_env, tts_beat  # noqa: E402

# RETRO 07-07 ("la voz sigue siendo obvio que es AI"): tuning para Alberto —
# stability más baja (más expresivo/menos parejo) + style para intención. El
# cache por texto invalida solo cuando cambia el TEXTO; si cambias settings,
# borra out/<slug>/vo/ para re-generar con la voz nueva.
_tts.VOICE_SETTINGS = {
    "stability": 0.30,
    "similarity_boost": 0.8,
    "style": 0.40,
    "use_speaker_boost": True,
}


def ffprobe_dur(p: Path) -> float:
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True).stdout.strip())


def norm(w: str) -> str:
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9ñ]", "", w)


def tts_words(text: str, mp3: Path):
    """ElevenLabs with-timestamps (voz Alberto) → [{word,start,end}]. CACHE: si el
    mp3 y words ya existen para el MISMO texto, no re-cobra (idempotencia de voz)."""
    wjson = mp3.with_suffix(".words.json")
    tjson = mp3.with_suffix(".text.txt")
    if mp3.exists() and wjson.exists() and tjson.exists() and tjson.read_text(encoding="utf-8") == text:
        return json.loads(wjson.read_text(encoding="utf-8"))
    key = _load_env()["ELEVENLABS_API_KEY"]
    words = tts_beat(key, VOICE_ID, text, mp3)
    wjson.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    tjson.write_text(text, encoding="utf-8")
    return words


def find_word(words, target: str) -> float | None:
    tgt = norm(target)
    for w in words:
        if tgt and tgt in norm(w["word"]):
            return w["start"]
    return None


def main():
    tr = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
    slug = sys.argv[2]
    out = ROOT / "infra" / "assembler" / "out" / slug
    (out / "vo").mkdir(parents=True, exist_ok=True)
    beats = tr["beats"]

    print("── VO (ElevenLabs Alberto, word timestamps)")
    vo_meta = []
    for i, b in enumerate(beats):
        mp3 = out / "vo" / f"b{i}.mp3"
        words = tts_words(b["vo"], mp3)
        dur = ffprobe_dur(mp3)
        vo_meta.append({"mp3": mp3, "words": words, "dur": dur})
        print(f"  b{i} {dur:5.2f}s  {b['vo'][:46]}…")
    (out / "vo" / "words.json").write_text(
        json.dumps([{"i": i, "dur": m["dur"], "words": m["words"]} for i, m in enumerate(vo_meta)],
                   ensure_ascii=False), encoding="utf-8")

    print("── compilar timeline")
    specs = []
    for i, (b, m) in enumerate(zip(beats, vo_meta)):
        lead = LEAD0 if i == 0 else 0.0
        # TODA transición no-cut encima el visual siguiente ~transF/FPS: se lo
        # devolvemos al tail para que el AIRE DE VOZ sea constante siempre
        ov_own = trans_frames(b) / FPS
        vis_dur = max(b.get("min_s", 4.0), lead + m["dur"] - (0 if i == 0 else JCUT) + b.get("tail_s", TAIL) + ov_own)
        durF = round(vis_dur * FPS)
        specs.append({"type": b["type"], "props": dict(b.get("props", {})), "durF": durF,
                      "trans": b.get("trans", "cut"), "transF": trans_frames(b) or TRANS_F_DEFAULT})
    starts = [0.0]
    for i in range(1, len(specs)):
        ov = trans_frames(beats[i - 1]) / FPS
        starts.append(round(starts[-1] + specs[i - 1]["durF"] / FPS - ov, 3))
    vo_at = [max(0.0, starts[i] - JCUT) if i > 0 else LEAD0 for i in range(len(specs))]

    # D6 (retro 07-07): NUNCA una voz pisa a la anterior — gap real >= MIN_VO_GAP.
    for i in range(1, len(specs)):
        gap = vo_at[i] - (vo_at[i - 1] + vo_meta[i - 1]["dur"])
        if gap < MIN_VO_GAP:
            raise SystemExit(f"D6 FAIL: gap de VO b{i-1}→b{i} = {gap:.2f}s < {MIN_VO_GAP}s "
                             f"(sube tail_s del beat {i-1} en el treatment)")

    lands_abs = {}
    for i, (b, m) in enumerate(zip(beats, vo_meta)):
        if b.get("target_word"):
            w = find_word(m["words"], b["target_word"])
            if w is None:
                print(f"  ⚠ b{i}: palabra '{b['target_word']}' no encontrada; land default")
            else:
                land_local = round((vo_at[i] + w - starts[i]) * FPS)
                specs[i]["props"]["land"] = max(20, land_local)
                lands_abs[i] = vo_at[i] + w
                print(f"  b{i} land: '{b['target_word']}' @ {w:.2f}s → frame {specs[i]['props']['land']}")

    props_path = out / "reel_props.json"
    props_path.write_text(json.dumps({"beats": specs}, ensure_ascii=False), encoding="utf-8")

    print(f"── render {COMP} (una pieza)")
    visual = out / f"{slug}_visual.mp4"
    # concurrency=1: la máquina de Manuel vive con ~30+ procesos de Chrome; a 2
    # tabs el delayRender de fuentes se muere de hambre (colgado 10 min, 2026-07-03).
    # El cuelgue de "Loading font InterVar" es INTERMITENTE (~50%) → hasta 3 intentos.
    for attempt in range(3):
        r = subprocess.run(["npx", "remotion", "render", COMP, str(visual),
                            f"--props={props_path}", "--crf=17", "--concurrency=1",
                            "--timeout=600000", "--log=error"], cwd=str(REMOTION), shell=True)
        if r.returncode == 0:
            break
        print(f"  ⚠ render intento {attempt + 1} falló (¿cuelgue de fuente?); reintento…")
    else:
        raise SystemExit("render falló 3 veces")
    total = ffprobe_dur(visual)
    print(f"  visual {total:.2f}s")

    print("── audio dirigido")
    close_start = starts[-1]
    music = MUSIC_POOL[sum(ord(c) for c in slug) % len(MUSIC_POOL)]  # rotación por slug
    print(f"  música: {music.name}")
    inputs = ["-i", str(visual)]
    for m in vo_meta:
        inputs += ["-i", str(m["mp3"])]
    inputs += ["-i", str(music)]
    n_vo = len(vo_meta)
    mus_idx = n_vo + 1
    # Gate 07-04 "no vi ningún SFX": volúmenes con PRESENCIA real
    sfx_list = []
    for i in range(1, len(specs)):
        sfx_list.append((SFX / "whoosh_02.wav", starts[i] - 0.10, 0.55))
    for i, t in lands_abs.items():
        sfx_list.append((SFX / "riser_02.wav", None, 0.50, t))
        sfx_list.append((SFX / "impact_02.wav", t - 0.02, 0.75))
    sfx_list.append((SFX / "impact_04.wav", close_start + 0.55, 0.60))

    fc, labels = "", []
    for i, m in enumerate(vo_meta):
        d = int(vo_at[i] * 1000)
        fc += f"[{i + 1}:a]adelay={d}|{d},volume=1.0[vo{i}];"
        labels.append(f"vo{i}")
    # Gate 07-08 ("que no obstruya a la persona que habla"): DUCKING determinista
    # desde el timeline de VO — cama a 0.045 mientras Alberto habla (con colchón
    # 0.15s), 0.13 en los huecos/cierre; dip extra suave en cada aterrizaje.
    speech = "".join(
        f"*if(between(t,{vo_at[i] - 0.15:.2f},{vo_at[i] + m['dur'] + 0.15:.2f}),0.35,1)"
        for i, m in enumerate(vo_meta))
    dips = "".join(f"*if(between(t,{t - 0.55:.2f},{t + 0.12:.2f}),0.5,1)" for t in lands_abs.values())
    vol_expr = f"(0.13){speech}{dips}"
    fc += f"[{mus_idx}:a]atrim=0:{total:.2f},volume='{vol_expr}':eval=frame,afade=t=in:d=0.8,afade=t=out:st={total - 1.4:.2f}:d=1.3[mus];"
    labels.append("mus")
    base = mus_idx + 1
    for j, s in enumerate(sfx_list):
        if len(s) == 4:
            path, _, vol, land_t = s
            rdur = ffprobe_dur(path)
            use = min(rdur, 1.6)
            start_t = max(0.0, land_t - use)
            d = int(start_t * 1000)
            fc += f"[{base + j}:a]atrim={rdur - use:.2f}:{rdur:.2f},adelay={d}|{d},volume={vol}[s{j}];"
        else:
            path, at, vol = s
            d = max(0, int(at * 1000))
            fc += f"[{base + j}:a]adelay={d}|{d},volume={vol}[s{j}];"
        inputs += ["-i", str(path)]
        labels.append(f"s{j}")
    fc += "".join(f"[{l}]" for l in labels)
    fc += f"amix=inputs={len(labels)}:normalize=0[mx];[mx]alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11[a]"

    final = out / f"{slug}_FINAL_916.mp4"
    r = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *inputs,
                        "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.2f}", str(final)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-600:]); raise SystemExit("mezcla falló")
    print(f"  FINAL {ffprobe_dur(final):.2f}s → {final}")

    print("── gates QC")
    ok = True
    for gate in ["filter_motion.py", "text_overlap_check.py"]:
        g = subprocess.run([sys.executable, str(QC / gate), str(final)], capture_output=True, text=True)
        line = (g.stdout or g.stderr).strip().splitlines()[-1] if (g.stdout or g.stderr) else "?"
        print(f"  {gate}: {line}")
        if g.returncode != 0 or "[FAIL]" in line:
            ok = False
    g = subprocess.run([sys.executable, str(QC / "filter_d.py"), str(final), sys.argv[1], str(out)],
                       capture_output=True, text=True)
    line = (g.stdout or g.stderr).strip().splitlines()[-1] if (g.stdout or g.stderr) else "?"
    print(f"  filter_d.py: {line}")
    if g.returncode != 0 or "[FAIL]" in line:
        ok = False
    if not ok:
        raise SystemExit("GATE FAIL — el reel NO pasa la barra; no entregar")
    print("✔ todos los gates pasan")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
