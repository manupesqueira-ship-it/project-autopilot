# -*- coding: utf-8 -*-
"""build_reels.py — arma reels editoriales COMPLETOS (voz + música + SFX + video).

Pipeline por reel: guion -> tts_timestamps (voz Asgard + timing) -> props del
EditorialReel (duración de cada escena = voz + colchón) -> render Remotion (video
mudo) -> audio (voz + música duckeada + SFX) -> mux -> mp4 final en el Desktop.

Uso: python build_reels.py [slug1 slug2 ...]   (sin args = los 3)
"""
import copy
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from datasheet import Datasheet, verify_reel  # P1.1b: gate de datos

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
DATASHEETS = Path(__file__).resolve().parent / "datasheets"
REMOTION = ROOT / "infra" / "remotion-render"
VOZ = ROOT / "infra" / "voz" / "tts_timestamps.py"
AUDIO = Path(r"C:\Users\manup\envato_audio")
OUTDIR = Path(r"C:\Users\manup\Desktop\DINERO_IA_reels")
WORK = ROOT / "infra" / "assembler" / "out" / "_editorial_reels"
FPS = 30
LEAD = 0.35
TAIL = 0.9
MUSIC = "music_minimal_04.mp3"


def run(cmd, cwd=None, shell=False):
    print(">", cmd if isinstance(cmd, str) else " ".join(str(c) for c in cmd))
    subprocess.run(cmd, cwd=cwd, shell=shell, check=True)


def ff(args):
    run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *[str(a) for a in args]])


def _apply_binds(rd, binds):
    """Aplica el mapa _binds del datasheet ("b3.left.value" -> clave) a las escenas del reel."""
    by_id = {b["id"]: b["scene"] for b in rd["beats"]}
    for path, key in (binds or {}).items():
        parts = path.split(".")
        sc = by_id.get(parts[0])
        if not sc:
            continue
        rest = parts[1:]
        if rest == ["value"]:
            sc["bind"] = key
        elif len(rest) == 2 and rest[0] in ("left", "right") and rest[1] == "value":
            sc.setdefault(rest[0], {})["bind"] = key
        elif rest and rest[0] in ("from", "to", "delta"):
            sc[f"bind_{rest[0]}"] = key


def gate(rd):
    """GATE VERIFY (P1.1b): corre ANTES de gastar (voz/render). Aborta si un dato no cuadra.
    Usa datasheets/{slug}.json si existe; si no, corre el lint ligero (<<verify>> + temporal)."""
    slug = rd["slug"]
    ds_path = DATASHEETS / f"{slug}.json"
    rd_check = copy.deepcopy(rd)
    ds = None
    if ds_path.exists():
        raw = json.loads(ds_path.read_text(encoding="utf-8"))
        ds = Datasheet(raw["figures"], raw.get("lane", "evergreen"))
        _apply_binds(rd_check, raw.get("_binds"))
    elif rd.get("lane"):
        ds = Datasheet({}, rd["lane"])  # sin ledger pero con carril (para el lint temporal)
    ok, errors = verify_reel(rd_check, ds)
    for e in errors:
        print(("  x " if e.startswith("BLOQUEA") else "  . ") + e)
    if not ok:
        raise SystemExit(f"[GATE] '{slug}' NO pasa verify — build abortado ANTES de gastar (voz/render).")
    tag = "" if ds and ds.figures else " [lint ligero: sin datasheet]"
    print(f"  gate VERIFY OK ({slug}){tag}")


def build(rd):
    slug = rd["slug"]
    print(f"=== gate {slug} ===")
    gate(rd)                       # P1.1b: falla en segundos si un dato no cuadra
    work = WORK / slug
    work.mkdir(parents=True, exist_ok=True)

    # 1) guion + 2) voz
    guion = {"slug": slug, "title": slug, "beats": [{"id": b["id"], "vo": b["vo"]} for b in rd["beats"]]}
    (work / "guion.json").write_text(json.dumps(guion, ensure_ascii=False), encoding="utf-8")
    run([sys.executable, str(VOZ), str(work / "guion.json"), str(work)])
    timing = json.loads((work / "vo" / "timing.json").read_text(encoding="utf-8"))

    # 3) props (duración escena = lead + voz + tail)
    scenes, durs = [], []
    for b in rd["beats"]:
        se = float(timing[b["id"]]["speech_end"])
        dur_s = LEAD + se + TAIL
        durF = round(dur_s * FPS)
        durs.append((b["id"], durF, durF / FPS, b["scene"].get("type")))
        scenes.append({"durF": durF, "scene": b["scene"]})
    props = {"edition": rd["edition"], "source": rd["source"], "scenes": scenes}
    (work / "props.json").write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    total_s = sum(d for _, _, d, _ in durs)

    # 4) render video mudo
    video = work / "video.mp4"
    run(f'npx remotion render EditorialReel "{video}" --props="{work / "props.json"}" '
        f'--crf=16 --concurrency=2 --timeout=600000 --log=error', cwd=str(REMOTION), shell=True)

    # 5) audio — segmentos de voz con lead + pad a la duración exacta de su escena
    segs = []
    for idx, (bid, durF, dur_s, _t) in enumerate(durs):
        seg = work / f"{bid}_seg.wav"
        lead = 0.10 if idx == 0 else LEAD  # P0.3: mata el silencio inicial en b1
        ff(["-i", work / "vo" / f"{bid}.mp3",
            "-af", f"aformat=channel_layouts=stereo,adelay={int(lead*1000)}|{int(lead*1000)},apad",
            "-t", f"{dur_s:.3f}", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", seg])
        segs.append(seg)
    lst = work / "vo_list.txt"
    lst.write_text("".join(f"file '{s.as_posix()}'\n" for s in segs), encoding="utf-8")
    vo_full = work / "vo_full.wav"
    ff(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vo_full])

    # música: loop -> volumen bajo -> ducking bajo la voz
    ducked = work / "music_ducked.wav"
    ff(["-stream_loop", "-1", "-i", AUDIO / "music" / MUSIC, "-i", vo_full,
        "-filter_complex",
        f"[0:a]aformat=channel_layouts=stereo,atrim=0:{total_s:.3f},volume=0.13[m];"
        f"[m][1:a]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[o]",
        "-map", "[o]", "-ar", "48000", "-ac", "2", ducked])

    # SFX: whoosh en cada transición + impact suave al inicio de un 'payoff'
    starts, acc = [], 0
    for (_, durF, _, _) in durs:
        starts.append(acc / FPS)
        acc += durF
    ins, filt, k = [], [], 0
    for idx, (st, (_, _, _, typ)) in enumerate(zip(starts, durs)):
        if idx == 0:  # P0.3: golpe suave en t=0 = arranque con presencia
            ins += ["-i", AUDIO / "sfx" / "impact_02.wav"]
            filt.append(f"[{k}:a]aformat=channel_layouts=stereo,volume=0.3[s{k}]")
            k += 1
        if idx > 0:  # SFX suave que acompaña el dip-a-papel (P2.2), no un whoosh que compite
            ins += ["-i", AUDIO / "sfx" / "whoosh_02.wav"]
            filt.append(f"[{k}:a]aformat=channel_layouts=stereo,adelay={int(st*1000)}|{int(st*1000)},volume=0.18[s{k}]")
            k += 1
        if typ == "payoff":
            ins += ["-i", AUDIO / "sfx" / "impact_02.wav"]
            filt.append(f"[{k}:a]aformat=channel_layouts=stereo,adelay={int(st*1000)}|{int(st*1000)},volume=0.4[s{k}]")
            k += 1
    mix = work / "mix.wav"
    if k > 0:
        sfx_full = work / "sfx_full.wav"
        mixins = "".join(f"[s{j}]" for j in range(k))
        ff([*sum([[a, b] for a, b in zip(ins[::2], ins[1::2])], []),
            "-filter_complex",
            ";".join(filt) + f";{mixins}amix=inputs={k}:normalize=0,apad,atrim=0:{total_s:.3f}[o]",
            "-map", "[o]", "-ar", "48000", "-ac", "2", sfx_full])
        ff(["-i", vo_full, "-i", ducked, "-i", sfx_full, "-filter_complex",
            "[0:a][1:a][2:a]amix=inputs=3:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[o]",
            "-map", "[o]", "-ar", "48000", "-ac", "2", mix])
    else:
        ff(["-i", vo_full, "-i", ducked, "-filter_complex",
            "[0:a][1:a]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[o]",
            "-map", "[o]", "-ar", "48000", "-ac", "2", mix])

    # 6) mux final
    OUTDIR.mkdir(parents=True, exist_ok=True)
    final = OUTDIR / f"{slug}.mp4"
    ff(["-i", video, "-i", mix, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final])
    print(f"\n=== LISTO: {final}  ({total_s:.1f}s) ===\n")


# ------------------------------------------------------------------ definiciones
from reels_defs import REELS  # noqa: E402

if __name__ == "__main__":
    want = sys.argv[1:] or [r["slug"] for r in REELS]
    for rd in REELS:
        if rd["slug"] in want:
            print(f"\n########## {rd['slug']} ##########")
            build(rd)
