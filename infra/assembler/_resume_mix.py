"""Reanuda un ensamble de masters: usa VO (mp3+words.json) y visual YA existentes,
solo re-corre timeline → mezcla → gates. Uso: python _resume_mix.py treatment.json slug"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from assemble_masters import (FPS, JCUT, LEAD0, MUSIC, QC, ROOT, SFX, TAIL,
                              TRANS_F_DEFAULT, ffprobe_dur, find_word)

tr = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
slug = sys.argv[2]
out = ROOT / "infra" / "assembler" / "out" / slug
beats = tr["beats"]
words_all = json.loads((out / "vo" / "words.json").read_text(encoding="utf-8-sig"))
vo_meta = [{"mp3": out / "vo" / f"b{m['i']}.mp3", "words": m["words"], "dur": m["dur"]} for m in words_all]

specs = []
for i, (b, m) in enumerate(zip(beats, vo_meta)):
    lead = LEAD0 if i == 0 else 0.0
    vis_dur = max(b.get("min_s", 4.0), lead + m["dur"] - (0 if i == 0 else JCUT) + b.get("tail_s", TAIL))
    specs.append({"type": b["type"], "durF": round(vis_dur * FPS),
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
        if w is not None:
            lands_abs[i] = vo_at[i] + w

visual = out / f"{slug}_visual.mp4"
total = ffprobe_dur(visual)
print(f"visual {total:.2f}s · {len(lands_abs)} anclas")

close_start = starts[-1]
inputs = ["-i", str(visual)]
for m in vo_meta:
    inputs += ["-i", str(m["mp3"])]
inputs += ["-i", str(MUSIC)]
mus_idx = len(vo_meta) + 1
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
        d = int(max(0.0, land_t - use) * 1000)
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
    print(r.stderr[-500:]); raise SystemExit("mezcla falló")
print(f"FINAL {ffprobe_dur(final):.2f}s → {final}")

ok = True
for gate in ["filter_motion.py", "text_overlap_check.py"]:
    g = subprocess.run([sys.executable, str(QC / gate), str(final)], capture_output=True, text=True)
    line = (g.stdout or g.stderr).strip().splitlines()[-1] if (g.stdout or g.stderr) else "?"
    print(f"  {gate}: {line}")
    ok = ok and g.returncode == 0 and "[FAIL]" not in line
g = subprocess.run([sys.executable, str(QC / "filter_d.py"), str(final), sys.argv[1], str(out)],
                   capture_output=True, text=True)
line = (g.stdout or g.stderr).strip().splitlines()[-1] if (g.stdout or g.stderr) else "?"
print(f"  filter_d.py: {line}")
ok = ok and g.returncode == 0 and "[FAIL]" not in line
sys.exit(0 if ok else 1)
