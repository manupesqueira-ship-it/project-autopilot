# -*- coding: utf-8 -*-
"""Termina un reel (audio + mux) reusando voz/props/video ya generados.
Uso: python finish_reel_audio.py <slug>"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
AUDIO = Path(r"C:\Users\manup\envato_audio")
OUTDIR = Path(r"C:\Users\manup\Desktop\DINERO_IA_reels")
WORK = ROOT / "infra" / "assembler" / "out" / "_editorial_reels"
FPS, LEAD, MUSIC = 30, 0.35, "music_minimal_04.mp3"

def ff(a): subprocess.run(["ffmpeg","-nostdin","-loglevel","error","-y",*[str(x) for x in a]], check=True)

slug = sys.argv[1]
work = WORK / slug
props = json.loads((work / "props.json").read_text(encoding="utf-8"))
scenes = props["scenes"]
ids = [f"b{i+1}" for i in range(len(scenes))]
durs = [(ids[i], s["durF"], s["durF"]/FPS, s["scene"].get("type")) for i, s in enumerate(scenes)]
total_s = sum(d for _,_,d,_ in durs)

segs = []
for idx, (bid, durF, dur_s, _t) in enumerate(durs):
    seg = work / f"{bid}_seg.wav"
    lead = 0.10 if idx == 0 else LEAD  # P0.3: mata el silencio inicial en b1 (freno de scroll)
    ff(["-i", work/"vo"/f"{bid}.mp3", "-af",
        f"aformat=channel_layouts=stereo,adelay={int(lead*1000)}|{int(lead*1000)},apad",
        "-t", f"{dur_s:.3f}", "-ar","48000","-ac","2","-c:a","pcm_s16le", seg])
    segs.append(seg)
lst = work/"vo_list.txt"
lst.write_text("".join(f"file '{s.as_posix()}'\n" for s in segs), encoding="utf-8")
ff(["-f","concat","-safe","0","-i",lst,"-c","copy", work/"vo_full.wav"])

ff(["-stream_loop","-1","-i",AUDIO/"music"/MUSIC,"-i",work/"vo_full.wav","-filter_complex",
    f"[0:a]aformat=channel_layouts=stereo,atrim=0:{total_s:.3f},volume=0.13[m];"
    f"[m][1:a]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[o]",
    "-map","[o]","-ar","48000","-ac","2", work/"music_ducked.wav"])

starts, acc = [], 0
for (_,durF,_,_) in durs: starts.append(acc/FPS); acc += durF
ins, filt, k = [], [], 0
for idx,(st,(_,_,_,typ)) in enumerate(zip(starts,durs)):
    if idx==0:  # P0.3: golpe suave en t=0 = arranque con presencia (freno de scroll)
        ins += ["-i", AUDIO/"sfx"/"impact_02.wav"]
        filt.append(f"[{k}:a]aformat=channel_layouts=stereo,volume=0.3[s{k}]"); k+=1
    if idx>0:
        ins += ["-i", AUDIO/"sfx"/"whoosh_02.wav"]
        filt.append(f"[{k}:a]aformat=channel_layouts=stereo,adelay={int(st*1000)}|{int(st*1000)},volume=0.32[s{k}]"); k+=1
    if typ=="payoff":
        ins += ["-i", AUDIO/"sfx"/"impact_02.wav"]
        filt.append(f"[{k}:a]aformat=channel_layouts=stereo,adelay={int(st*1000)}|{int(st*1000)},volume=0.4[s{k}]"); k+=1
mix = work/"mix.wav"
if k>0:
    mixins="".join(f"[s{j}]" for j in range(k))
    ff([*ins,"-filter_complex", ";".join(filt)+f";{mixins}amix=inputs={k}:normalize=0,apad,atrim=0:{total_s:.3f}[o]",
        "-map","[o]","-ar","48000","-ac","2", work/"sfx_full.wav"])
    ff(["-i",work/"vo_full.wav","-i",work/"music_ducked.wav","-i",work/"sfx_full.wav","-filter_complex",
        "[0:a][1:a][2:a]amix=inputs=3:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[o]","-map","[o]","-ar","48000","-ac","2", mix])
else:
    ff(["-i",work/"vo_full.wav","-i",work/"music_ducked.wav","-filter_complex",
        "[0:a][1:a]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[o]","-map","[o]", mix])

OUTDIR.mkdir(parents=True, exist_ok=True)
final = OUTDIR/f"{slug}.mp4"
ff(["-i",work/"video.mp4","-i",mix,"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-shortest", final])
print("LISTO", final, f"{total_s:.1f}s")
