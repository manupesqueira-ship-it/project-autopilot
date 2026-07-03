# -*- coding: utf-8 -*-
"""Dinero IA — AUDIO MASTER (cadena de masterizacion de audio, modulo aislado).

================================================================================
CONTEXTO: cadena de audio ACTUAL de build916.py (lo que YA funciona; NO tocar)
================================================================================
build916.assemble() arma el audio asi, hoy:

  VOZ
    - Cada beat trae su mp3 ElevenLabs (Asgard eleven_v3) + words.json (timestamps).
    - norm_vo(): loudnorm DOS-PASADAS por-beat (I=-16:TP=-1.5:LRA=11, linear=true)
      -> vn_<id>.wav 48k. Cache content-addressed por sha(mp3).
    - Cada VO se adelanta con adelay a vo_start*1000 ms, se amix (normalize=0),
      apad=whole_dur=total. Ese stream se asplit en 3: [vo_mix] al mix final,
      [vo_sc] como key del sidechain, [vo_stem] que se exporta a {slug}.vo_stem.wav
      (PCM 48k, mono) para el QC de entrega.

  MUSICA
    - pick_music(): track Envato (guion["music"] o default music_minimaltechno_01).
    - [0:a]aloop=-1, atrim=0:total, volume=0.30, DIP super-gaussiano
      volume='1-0.93*(bumps)' centrado en los HUECOS audibles reales
      (midpoint entre aud_end[m] y aud_start[m+1]), afade out al final.
    - Ducking: sidechaincompress=threshold=0.03:ratio=6:attack=5:release=260
      keyado por [vo_sc].

  SFX
    - Por beat con "sfx": pick_sfx() resuelve el archivo (Envato prioritario),
      se coloca en s["start"] (frontera de beat) con adelay, volume=0.45.

  MASTER
    - amix([ducked]+[vo_mix]+sfx, normalize=0) -> [mix].
    - [mix]loudnorm=I=-16:TP=-1.5:LRA=11  <-- UNA SOLA PASADA (online/dinamico).
    - encode AAC 192k 48k -> audio.m4a. Mux final: -c:v copy -c:a copy -t total.

  GOTCHAS heredados (respetados aqui):
    - loudnorm 2-pasadas + encode UNICO + mux -c:a copy (re-encodear AAC despues
      del loudnorm re-mete true-peaks > -1 dBTP).
    - Cuidar el TAIL: apad=whole_dur=total / -shortest pueden cortar el cierre.
    - ffmpeg (Gyan) NO en PATH -> FFMPEG_BIN / ruta completa.
    - XFADE=0.35 es de VIDEO; el respiro real de audio lo da el DIP de musica.

================================================================================
QUE MEJORA ESTE MODULO (vs la cadena de arriba)
================================================================================
  1. VOZ con cadena de presencia broadcast: highpass ~80 Hz (quita retumbe) ->
     de-esser ligero -> EQ de presencia suave (~4.5 kHz) -> compresion suave
     (presencia sin bombeo). Hoy la voz solo se loudnorm-ea.
  2. MUSICA con bed LUFS-RELATIVO (se mide la voz y la musica, el bed se sienta
     ~8 dB bajo la voz) en vez del volume=0.30 magico. Conserva el DIP
     super-gaussiano y el sidechain validados.
  3. MASTER con loudnorm DOS-PASADAS (medir -> aplicar con measured_*+linear=true)
     en vez de la pasada unica de hoy -> integrado mas exacto, sin pumping +
     limitador de seguridad. Encode UNICO -> el mux sigue siendo -c:a copy.

Todo $0 (ffmpeg local). NO regenera voz (reusa el VO ya producido).

================================================================================
CONTRATO (lo que el integrador llama)
================================================================================
  master_audio(vo_path, vo_timestamps, music_path, sfx_cues, total_duration,
               out_path, ...) -> out_path

Ver la firma exacta + el unico punto de llamada en build916.py al FINAL del
archivo (seccion "NOTA DE INTEGRACION").
"""

import json
import os
import re
import subprocess
from pathlib import Path

# ffmpeg/ffprobe (Gyan) NO estan en PATH (ver CLAUDE.md) -> FFMPEG_BIN o ruta
# completa. Mismo patron que build916.py / post_finish.py.
_DEFAULT_FF = (r"C:\Users\manup\AppData\Local\Microsoft\WinGet\Packages"
               r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
               r"\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe")
FFMPEG = os.environ.get("FFMPEG_BIN") or _DEFAULT_FF
if not os.path.exists(FFMPEG):
    FFMPEG = "ffmpeg"
FFPROBE = os.environ.get("FFPROBE_BIN") or str(Path(FFMPEG).with_name("ffprobe.exe"))
if not os.path.exists(FFPROBE):
    FFPROBE = "ffprobe"

# --- parametros de la cadena (tuneables; conservadores por default) ---
HP_HZ = 80.0              # high-pass voz: quita retumbe sub-80
DEESS_I = 0.15            # de-esser ligero (0..1); alto = mas agresivo
PRES_HZ, PRES_Q, PRES_G = 4500.0, 2.0, 2.0   # EQ presencia suave (+2 dB ~4.5k)
COMP = "threshold=-20dB:ratio=2.5:attack=8:release=180:makeup=2"  # comp suave voz

BED_BELOW_VOICE_DB = 8.0  # la musica se sienta ~8 dB bajo la voz (bed)
DIP_DEPTH = 0.93          # profundidad del dip en el hueco (= build916)
DIP_WIDTH = 1.05          # ancho super-gaussiano del dip (= build916)
MUSIC_VOL_FLOOR_DB = -40.0
MUSIC_VOL_CEIL_DB = 6.0

SIDECHAIN = "threshold=0.03:ratio=6:attack=5:release=260"  # = build916 (validado)

SFX_DEFAULT_GAIN_DB = -7.0   # ~volume=0.45 de build916

# master
LN_I, LN_TP, LN_LRA = -16.0, -1.5, 11.0
LIMIT_LINEAR = 0.85          # ~-1.4 dB: red de seguridad sobre el TP de loudnorm
MUSIC_TAIL_FADE = 0.8        # afade out de la musica al final


def _run(args):
    p = subprocess.run(args, capture_output=True, text=True, shell=False)
    if p.returncode != 0:
        print("CMD ERR:", " ".join(str(a) for a in args))
        print((p.stderr or p.stdout)[-3000:])
        raise SystemExit(1)
    return p


def _ffprobe_dur(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    out = r.stdout.strip()
    if r.returncode != 0 or not out:
        raise SystemExit(f"FFPROBE ERR dur: {path}")
    return float(out)


def measure_lufs(path, ffmpeg=None):
    """LUFS integrado (input_i) de un archivo, via loudnorm de medicion.

    Devuelve float (LUFS) o None si no se pudo medir.
    """
    ff = ffmpeg or FFMPEG
    p = subprocess.run([ff, "-i", str(path), "-af",
                        "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[\s\S]*?\}", p.stderr)
    if not m:
        return None
    try:
        return float(json.loads(m.group(0))["input_i"])
    except Exception:
        return None


def _breaths_from_timeline(tl):
    """Midpoints de los huecos audibles reales entre voces (= build916)."""
    beats = tl.get("beats", [])
    return [(beats[m]["aud_end"] + beats[m + 1]["aud_start"]) / 2.0
            for m in range(len(beats) - 1)
            if "aud_end" in beats[m] and "aud_start" in beats[m + 1]]


def _breaths_from_silencedetect(vo_path, total, ffmpeg=None):
    """Fallback: deriva los huecos del vo con silencedetect (midpoint de cada
    silencio interior). Se usa cuando no hay timeline.json."""
    ff = ffmpeg or FFMPEG
    p = subprocess.run([ff, "-i", str(vo_path), "-af",
                        "silencedetect=noise=-40dB:d=0.4", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", p.stderr)]
    breaths = []
    for s, e in zip(starts, ends):
        if 0.2 < s and e < total - 0.2:   # ignora el silencio de cabeza/cola
            breaths.append((s + e) / 2.0)
    return breaths


def _dip_expr(breaths):
    """Automatizacion de volumen super-gaussiana (techo de la musica en los
    huecos). exp(-u^8), u=(t-S)/WIDTH. Identica a build916."""
    if not breaths:
        return ""
    def _sg(S):
        u = f"((t-{S:.3f})/{DIP_WIDTH})"
        q = f"(({u}*{u})*({u}*{u}))"      # u^4
        return f"exp(-{q}*{q})"             # exp(-u^8)
    bumps = "+".join(_sg(S) for S in breaths)
    return f",volume=eval=frame:volume='1-{DIP_DEPTH}*({bumps})'"


def _norm_sfx_cues(sfx_cues):
    """Acepta tuplas (file, t[, gain_db]) o dicts {file,t,gain_db}. Normaliza a
    lista de dicts ordenada por t."""
    out = []
    for c in (sfx_cues or []):
        if isinstance(c, dict):
            f, t = c["file"], float(c["t"])
            g = float(c.get("gain_db", SFX_DEFAULT_GAIN_DB))
        else:
            f, t = c[0], float(c[1])
            g = float(c[2]) if len(c) > 2 else SFX_DEFAULT_GAIN_DB
        if f and os.path.exists(str(f)):
            out.append({"file": str(f), "t": t, "gain_db": g})
        else:
            print(f"SFX WARN: no existe '{f}' (cue t={t}) -> omitido")
    return sorted(out, key=lambda d: d["t"])


def master_audio(vo_path, vo_timestamps, music_path, sfx_cues, total_duration,
                 out_path, work_dir=None, ffmpeg=None, ffprobe=None,
                 verbose=True):
    """Produce el master de audio estereo terminado (calidad broadcast).

    Parametros
    ----------
    vo_path : str|Path
        Stem de VOZ ya colocado en la linea de tiempo (lo que build916 exporta
        como {slug}.vo_stem.wav). PCM/wav, mono o estereo, a la duracion total.
        NO se re-genera voz aqui (reuso $0).
    vo_timestamps : str|Path|dict|None
        timeline.json (o dict) con beats[].aud_start/aud_end -> de ahi salen los
        huecos para el DIP de musica. Si es None, se derivan con silencedetect
        sobre vo_path.
    music_path : str|Path
        Track de musica (se loopea + recorta al total). Bed LUFS-relativo.
    sfx_cues : list
        Cues de SFX [{"file","t","gain_db"?}] o tuplas (file, t[, gain_db]).
        El que coloca CUAL sfx y DONDE es el caller (director/guion); este modulo
        solo los mezcla. t en segundos (frontera de beat).
    total_duration : float
        Duracion total del video (s). Acota atrim/apad/afade. Incluye el TAIL.
    out_path : str|Path
        Salida. .m4a/.aac -> AAC 192k (drop-in para mux -c:a copy). .wav -> PCM.
    work_dir : str|Path|None
        Carpeta para intermedios (premaster). Default: junto a out_path.

    Devuelve
    -------
    out_path (str) del master escrito.
    """
    ff = ffmpeg or FFMPEG
    fp = ffprobe or FFPROBE
    vo_path, music_path, out_path = str(vo_path), str(music_path), str(out_path)
    total = float(total_duration)
    work = Path(work_dir) if work_dir else Path(out_path).parent
    work.mkdir(parents=True, exist_ok=True)

    # --- breaths para el dip ---
    tl = None
    if isinstance(vo_timestamps, dict):
        tl = vo_timestamps
    elif vo_timestamps and os.path.exists(str(vo_timestamps)):
        tl = json.loads(Path(vo_timestamps).read_text(encoding="utf-8-sig"))
    breaths = _breaths_from_timeline(tl) if tl else \
        _breaths_from_silencedetect(vo_path, total, ff)
    if verbose:
        src = "timeline" if tl else "silencedetect"
        print(f"AUDIO: {len(breaths)} huecos ({src}) para el dip de musica")

    # --- niveles relativos voz/musica ---
    lv = measure_lufs(vo_path, ff)
    lm = measure_lufs(music_path, ff)
    if lv is not None and lm is not None:
        music_gain_db = (lv - BED_BELOW_VOICE_DB) - lm
    else:
        music_gain_db = -10.0  # ~volume 0.30; fallback si la medicion falla
        print("AUDIO WARN: no se pudo medir LUFS voz/musica -> bed fallback")
    music_gain_db = max(MUSIC_VOL_FLOOR_DB, min(MUSIC_VOL_CEIL_DB, music_gain_db))
    if verbose:
        print(f"AUDIO: voz={lv} LUFS  musica={lm} LUFS  "
              f"-> bed gain {music_gain_db:+.1f} dB (bed ~{(lv or 0)-BED_BELOW_VOICE_DB:.1f} LUFS)")

    cues = _norm_sfx_cues(sfx_cues)

    # ---------------- inputs ----------------
    # [0]=voz  [1]=musica  [2..]=sfx
    inputs = ["-i", vo_path, "-i", music_path]
    for c in cues:
        inputs += ["-i", c["file"]]

    fc = []
    # VOZ: presencia broadcast. mono->procesa->estereo. asplit (mix + key sidechain)
    fc.append(
        f"[0:a]aresample=48000,aformat=channel_layouts=mono,"
        f"highpass=f={HP_HZ},deesser=i={DEESS_I},"
        f"equalizer=f={PRES_HZ}:t=q:w={PRES_Q}:g={PRES_G},"
        f"acompressor={COMP},"
        f"aformat=channel_layouts=stereo[voc]")
    fc.append("[voc]asplit=2[vo_mix][vo_key]")

    # MUSICA: loop+trim, bed LUFS-relativo, DIP super-gaussiano, fade out.
    dip = _dip_expr(breaths)
    fc.append(
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"aloop=loop=-1:size=2e9,atrim=0:{total:.3f},"
        f"volume={music_gain_db:.2f}dB{dip},"
        f"afade=t=out:st={max(total - MUSIC_TAIL_FADE, 0):.3f}:d={MUSIC_TAIL_FADE}[mus]")

    # DUCKING sidechain (musica keyada por la voz).
    fc.append(f"[mus][vo_key]sidechaincompress={SIDECHAIN}[ducked]")

    # SFX: cada cue adelayado a su t.
    mix_in = ["[ducked]", "[vo_mix]"]
    for j, c in enumerate(cues):
        idx = 2 + j
        ms = int(round(c["t"] * 1000))
        fc.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
                  f"volume={c['gain_db']:.2f}dB,adelay={ms}|{ms}[sfx{j}]")
        mix_in.append(f"[sfx{j}]")

    # MIX -> apad al total EXACTO (no -shortest: protege el TAIL del cierre).
    fc.append("".join(mix_in)
              + f"amix=inputs={len(mix_in)}:normalize=0,"
              + f"apad=whole_dur={total:.3f}[premix]")

    # --- premaster PCM (insumo de las 2 pasadas de loudnorm) ---
    premaster = work / "_premaster.wav"
    _run([ff, "-y"] + inputs + ["-filter_complex", ";".join(fc),
          "-map", "[premix]", "-t", f"{total:.3f}",
          "-c:a", "pcm_s16le", "-ar", "48000", str(premaster)])

    # ---------------- master: loudnorm 2 pasadas ----------------
    # PASO 1: medir el premaster.
    p = subprocess.run([ff, "-i", str(premaster), "-af",
                        f"loudnorm=I={LN_I}:TP={LN_TP}:LRA={LN_LRA}:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[\s\S]*?\}", p.stderr)
    if not m:
        print("LOUDNORM ERR: no se pudo medir el premaster")
        print((p.stderr or p.stdout)[-2000:])
        raise SystemExit(1)
    d = json.loads(m.group(0))
    af = (f"loudnorm=I={LN_I}:TP={LN_TP}:LRA={LN_LRA}"
          f":measured_I={d['input_i']}:measured_TP={d['input_tp']}"
          f":measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}"
          f":offset={d['target_offset']}:linear=true,"
          f"alimiter=limit={LIMIT_LINEAR}:level=disabled")

    # PASO 2: aplicar measured_* + limitador de seguridad, encode UNICO.
    ext = Path(out_path).suffix.lower()
    if ext in (".wav",):
        codec = ["-c:a", "pcm_s16le"]
    else:  # .m4a / .aac / default -> AAC drop-in para mux -c:a copy
        codec = ["-c:a", "aac", "-b:a", "192k"]
    _run([ff, "-y", "-i", str(premaster), "-af", af, "-ar", "48000"]
         + codec + ["-t", f"{total:.3f}", out_path])

    if verbose:
        print(f"AUDIO MASTER -> {out_path}  ({_ffprobe_dur(out_path):.2f}s, "
              f"target I={LN_I} TP={LN_TP})")
    return out_path


# ==============================================================================
# NOTA DE INTEGRACION (para el integrador, dueno de build916.py)
# ==============================================================================
#
# FIRMA EXACTA:
#   from audio_master import master_audio
#   master_audio(vo_path, vo_timestamps, music_path, sfx_cues,
#                total_duration, out_path) -> out_path
#
# DONDE LLAMARLA en build916.py -> assemble():
#   build916 ya calcula TODO lo que este modulo necesita. El bloque a reemplazar
#   es el de la mezcla final de audio: desde `inputs = ["-i", pick_music(guion)]`
#   (~linea 462) hasta el run que escribe `audio.m4a` (~linea 531). El vo_stem
#   (PCM, voz colocada en timeline) ya se produce en ese mismo bloque hoy via
#   `[vo_stem]`; para usar este modulo, exportalo PRIMERO (una corrida ffmpeg
#   barata que ya existe), y luego una sola llamada produce el master:
#
#       # build916 ya tiene: segs, total, timeline_path, guion
#       vo_stem = out_dir / f"{guion['slug']}.vo_stem.wav"   # YA se genera hoy
#       sfx_cues = [{"file": str(pick_sfx(s["sfx"])), "t": s["start"]}
#                   for s in segs if s.get("sfx")]
#       audio = tmp / "audio.m4a"
#       master_audio(vo_stem, timeline_path, pick_music(guion),
#                    sfx_cues, total, audio)
#
#   El resto de build916 NO cambia: el mux final sigue siendo
#       -i silent.mp4 -i audio.m4a -c:v copy -c:a copy -t total
#   (audio.m4a sale AAC 192k con el true-peak ya controlado por loudnorm 2-pasadas
#    -> -c:a copy NO re-introduce picos > -1 dBTP).
#
# INPUTS que pasa build916 (ya disponibles en assemble()):
#   - vo_stem      : out_dir/f"{slug}.vo_stem.wav"  (voz colocada, PCM 48k)
#   - timeline_path: out_dir/f"{slug}.timeline.json" (tiene aud_start/aud_end)
#   - music        : pick_music(guion)
#   - sfx_cues     : [(pick_sfx(s["sfx"]), s["start"]) ...]  (tuplas tambien valen)
#   - total        : el total del timeline
#   - out_path     : tmp/"audio.m4a"
#
# CONTRATO ESTABLE: inputs/outputs de master_audio no cambian -> el integrador
# conecta una sola linea y el contrato aguanta. Solo se crean archivos NUEVOS
# (este modulo + el sandbox) -> sin colision de merge con build916.
