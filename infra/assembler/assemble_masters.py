"""assemble_masters.py — pipeline noticia→reel en el MUNDO DE LA PÁGINA (masters kit2).

Idéntica plomería probada de assemble_news.py (VO con timestamps por palabra →
timeline con land anclado a LA PALABRA → UN render → mezcla dirigida → gates QC
exit 1) pero renderiza la composición MastersReel (masters congelados, tokens
kit2). El movimiento NO se toca aquí: solo datos, duraciones desde la voz, y el
frame exacto donde cada cifra/palabra-acento aterriza.

Uso:  python assemble_masters.py treatment.json <slug>
Treatment beat: {type: hook|cifra|linea|barras|carrera|cierre, vo, props,
                 target_word?, trans?: cut|dip, transF?, min_s?, tail_s?}
Voz: edge-tts es-MX placeholder mientras ELEVENLABS_API_KEY siga vencida.
"""
import asyncio
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
MUSIC = Path(r"C:\Users\manup\envato_audio\music\music_minimal_04.mp3")
FPS = 30
COMP = "MastersReel"
VOICE = "es-MX-JorgeNeural"
JCUT = 0.40
LEAD0 = 0.30
TAIL = 0.70
TRANS_F_DEFAULT = 14


def ffprobe_dur(p: Path) -> float:
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True).stdout.strip())


def norm(w: str) -> str:
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9ñ]", "", w)


async def tts_words(text: str, mp3: Path, tries: int = 6):
    import edge_tts
    for a in range(tries):
        try:
            com = edge_tts.Communicate(text, VOICE, rate="-4%", boundary="WordBoundary")
            audio = bytearray()
            words = []
            async for chunk in com.stream():
                if chunk["type"] == "audio":
                    audio.extend(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    s = chunk["offset"] / 1e7
                    words.append({"word": chunk["text"], "start": round(s, 3),
                                  "end": round(s + chunk["duration"] / 1e7, 3)})
            if len(audio) > 1000:
                mp3.write_bytes(bytes(audio))
                return words
        except Exception as e:
            print(f"  tts retry {a}: {type(e).__name__}")
            await asyncio.sleep(2 * (a + 1))
    raise SystemExit(f"TTS falló: {text[:40]}")


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

    print("── VO (edge-tts, word boundaries)")
    vo_meta = []
    for i, b in enumerate(beats):
        mp3 = out / "vo" / f"b{i}.mp3"
        words = asyncio.run(tts_words(b["vo"], mp3))
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
        vis_dur = max(b.get("min_s", 4.0), lead + m["dur"] - (0 if i == 0 else JCUT) + b.get("tail_s", TAIL))
        durF = round(vis_dur * FPS)
        specs.append({"type": b["type"], "props": dict(b.get("props", {})), "durF": durF,
                      "trans": b.get("trans", "cut"), "transF": b.get("transF", TRANS_F_DEFAULT)})
    starts = [0.0]
    for i in range(1, len(specs)):
        ov = (specs[i - 1]["transF"] / FPS) if specs[i - 1]["trans"] == "dip" else 0.0
        starts.append(round(starts[-1] + specs[i - 1]["durF"] / FPS - ov, 3))
    vo_at = [max(0.0, starts[i] - JCUT) if i > 0 else LEAD0 for i in range(len(specs))]

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
    r = subprocess.run(["npx", "remotion", "render", COMP, str(visual),
                        f"--props={props_path}", "--crf=17", "--concurrency=2",
                        "--timeout=600000", "--log=error"], cwd=str(REMOTION), shell=True)
    if r.returncode != 0:
        raise SystemExit("render falló")
    total = ffprobe_dur(visual)
    print(f"  visual {total:.2f}s")

    print("── audio dirigido")
    close_start = starts[-1]
    inputs = ["-i", str(visual)]
    for m in vo_meta:
        inputs += ["-i", str(m["mp3"])]
    inputs += ["-i", str(MUSIC)]
    n_vo = len(vo_meta)
    mus_idx = n_vo + 1
    sfx_list = []
    for i in range(1, len(specs)):
        sfx_list.append((SFX / "whoosh_02.wav", starts[i] - 0.10, 0.26))
    for i, t in lands_abs.items():
        sfx_list.append((SFX / "riser_02.wav", None, 0.26, t))
        sfx_list.append((SFX / "impact_02.wav", t - 0.02, 0.48))
    sfx_list.append((SFX / "impact_04.wav", close_start + 0.55, 0.36))

    fc, labels = "", []
    for i, m in enumerate(vo_meta):
        d = int(vo_at[i] * 1000)
        fc += f"[{i + 1}:a]adelay={d}|{d},volume=1.0[vo{i}];"
        labels.append(f"vo{i}")
    dips = "".join(f"*if(between(t,{t - 0.55:.2f},{t + 0.12:.2f}),0.28,1)" for t in lands_abs.values())
    vol_expr = f"(if(lt(t,{starts[1] if len(starts) > 1 else 3}),0.15,if(lt(t,{close_start}),0.10,0.035))){dips}"
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
