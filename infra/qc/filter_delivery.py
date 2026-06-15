# -*- coding: utf-8 -*-
"""
Filtro de ENTREGA (P0): valida el MP4 ENTREGADO + sus sidecars, NO un
intermedio.

Por que existe: el bug de voces encimadas (seg 21/44) escapo 4 veces porque se
validaba un intermedio (vn_*.wav vs mp3 dentro de build916), nunca el master
entregado. Este filtro corre sobre el entregable real y mide la senal que
FALLARIA si el bug siguiera ahi (silencio real en cada costura del vo_stem).
Encaja con la regla del proyecto: "verificar el ARTEFACTO, no afirmar desde el
modelo".

Insumos (los emite build916.assemble):
  - <final>.mp4          el master entregado
  - <slug>.timeline.json el golden estructural (start/aud_start/aud_end/seg/total)
  - <slug>.vo_stem.wav   SOLO voz (antes de musica/sidechain) -> silencedetect
                         mide los huecos entre voces sin ambiguedad

Uso:
  python filter_delivery.py <final.mp4> <timeline.json> <vo_stem.wav>
  python filter_delivery.py --selftest
exit 0 = entrega OK ; exit 1 = BLOQUEADA (+ escribe <slug>_delivery_qc.json)
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

FFMPEG = os.environ.get("FFMPEG_BIN", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE_BIN", "ffprobe")

# ---- umbrales P0 (el hueco nominal del diseno = LEAD+TAIL-XFADE = 1.0s) ----
GAP_MIN = 0.60     # silencio minimo continuo en cada costura entre voces
GAP_CRIT = 0.35    # < esto = voces pisandose (la clase de bug que se escapo 4x)
PLACE_TOL = 0.30   # |borde del silencio medido - aud_end/aud_start esperado|
LUFS_LO, LUFS_HI = -16.5, -11.5   # integrado (target -16)
TP_MAX = -1.0      # true-peak dBTP (limite duro -0.9; margen a -1.0)
DUR_TOL = 0.06     # |dur(mp4) - total| y |dur(v) - dur(a)| ~ 1-2 frames


# ----------------------------- mediciones --------------------------------
def silences(wav, noise=-40, d=0.30):
    """Intervalos (start, end) de silencio en el wav."""
    p = subprocess.run(
        [FFMPEG, "-i", str(wav), "-af",
         f"silencedetect=noise={noise}dB:d={d}", "-f", "null", "-"],
        capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start:\s*([\-\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([\-\d.]+)", p.stderr)]
    return list(zip(starts, ends))  # zip ignora un silence_start final sin end (EOF)


def fmt_dur(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def stream_dur(path, sel):
    r = subprocess.run([FFPROBE, "-v", "error", "-select_streams", sel,
                        "-show_entries", "stream=duration", "-of", "csv=p=0",
                        str(path)], capture_output=True, text=True)
    out = r.stdout.strip().splitlines()
    if not out:
        return None
    tok = out[0].split(",")[0].strip()  # csv=p=0 deja una coma final; tomar el 1er campo
    return float(tok) if tok and tok != "N/A" else None


def loudness(mp4):
    p = subprocess.run([FFMPEG, "-i", str(mp4), "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    txt = p.stderr
    ii = re.findall(r"I:\s+([\-\d.]+)\s+LUFS", txt)      # ultimo = Summary
    pk = re.findall(r"Peak:\s+([\-\d.]+)\s+dBFS", txt)   # Summary true-peak
    I = float(ii[-1]) if ii else None
    tp = max(float(x) for x in pk) if pk else None
    return I, tp


# ------------------------- logica pura (testeable) -----------------------
def eval_seams(beats, sil):
    """Evalua los huecos entre voces a partir del golden + los silencios medidos.
    Funcion PURA (sin ffmpeg) para que el selftest pruebe ambos sentidos:
    detecta el hueco sano Y atrapa el encimado. Devuelve lista de checks."""
    checks = []

    def covering(t):
        for s, e in sil:
            if s - 0.02 <= t <= e + 0.02:
                return (s, e)
        return None

    for m in range(len(beats) - 1):
        ae = beats[m]["aud_end"]
        as1 = beats[m + 1]["aud_start"]
        mid = (ae + as1) / 2.0
        iv = covering(mid)
        measured = (iv[1] - iv[0]) if iv else 0.0
        crit = measured < GAP_CRIT
        checks.append({
            "check": "gap_voces", "seam": m, "t": round(ae, 3),
            "measured_silence": round(measured, 3), "need": GAP_MIN,
            "ok": measured >= GAP_MIN, "critical": crit,
            "detail": (f"hueco {measured:.2f}s en costura {m} "
                       f"(esperado >= {GAP_MIN}s)"
                       + (" — VOCES ENCIMADAS" if crit else "")),
        })
        # coloca_voz: la voz de m termina y la de m+1 entra donde se planeo
        if iv:
            ok2 = abs(iv[0] - ae) <= PLACE_TOL and abs(iv[1] - as1) <= PLACE_TOL
            det = (f"silencio [{iv[0]:.2f},{iv[1]:.2f}] vs esperado "
                   f"[{ae:.2f},{as1:.2f}]")
        else:
            ok2, det = False, "no hay silencio en la costura"
        checks.append({
            "check": "coloca_voz", "seam": m, "t": round(ae, 3),
            "ok": ok2, "detail": det,
        })
    return checks


# ------------------------------- driver ----------------------------------
def run_delivery(mp4, timeline_json, vo_stem):
    tl = json.loads(Path(timeline_json).read_text(encoding="utf-8"))
    beats, total = tl["beats"], tl["total"]
    checks = []

    # #1 + #2 huecos/colocacion de voces sobre el vo_stem (la clase de bug)
    checks += eval_seams(beats, silences(vo_stem))

    # #3 loudness integrado, #4 true-peak
    I, tp = loudness(mp4)
    checks.append({"check": "loudness_I", "ok": I is not None and LUFS_LO <= I <= LUFS_HI,
                   "measured": I, "rango": [LUFS_LO, LUFS_HI],
                   "detail": f"integrado {I} LUFS"})
    checks.append({"check": "true_peak", "ok": tp is not None and tp <= TP_MAX,
                   "measured": tp, "max": TP_MAX, "detail": f"TP {tp} dBTP"})

    # #5 duracion total + match A/V (que no se corto el CTA)
    dmp4 = fmt_dur(mp4)
    dv, da = stream_dur(mp4, "v:0"), stream_dur(mp4, "a:0")
    checks.append({"check": "dur_total", "ok": abs(dmp4 - total) <= DUR_TOL,
                   "measured": round(dmp4, 3), "esperado": round(total, 3),
                   "detail": f"mp4 {dmp4:.2f}s vs golden {total:.2f}s"})
    av_ok = (dv is not None and da is not None and abs(dv - da) <= DUR_TOL)
    checks.append({"check": "av_match", "ok": av_ok,
                   "v": dv, "a": da,
                   "detail": f"video {dv}s vs audio {da}s"})

    fails = [c for c in checks if not c["ok"]]
    report = {"slug": tl.get("slug"), "ok": not fails,
              "n_checks": len(checks), "n_fail": len(fails), "checks": checks}
    out = Path(mp4).with_name(f"{tl.get('slug', 'entrega')}_delivery_qc.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n=== QC ENTREGA  {tl.get('slug')} ===")
    for c in checks:
        mark = "OK  " if c["ok"] else "FAIL"
        print(f"  [{mark}] {c['check']:12} {c.get('detail', '')}")
    print(f"  -> {'ENTREGA OK' if not fails else f'BLOQUEADA ({len(fails)} fallas)'}  "
          f"({out.name})")
    return 0 if not fails else 1


def _selftest():
    # golden: 3 beats, costuras esperadas con ~1.0s de hueco
    beats = [
        {"aud_start": 0.5, "aud_end": 10.0},
        {"aud_start": 11.0, "aud_end": 20.0},
        {"aud_start": 21.0, "aud_end": 30.0},
    ]
    # SANO: silencio real cubre cada costura (10.0->11.0 y 20.0->21.0)
    ok = eval_seams(beats, [(10.0, 11.0), (20.0, 21.0)])
    gaps = [c for c in ok if c["check"] == "gap_voces"]
    assert all(c["ok"] for c in gaps), "caso sano debe pasar"

    # ENCIMADO (el bug): apenas 0.1s de silencio en la 1a costura (wav viejo
    # mas largo -> la voz de b1 invade el hueco). Debe FALLAR y marcar critical.
    bad = eval_seams(beats, [(10.45, 10.55), (20.0, 21.0)])
    seam0 = [c for c in bad if c["check"] == "gap_voces" and c["seam"] == 0][0]
    assert not seam0["ok"], "encimado debe fallar"
    assert seam0["critical"], "encimado < 0.35s debe marcarse critico"
    print("filter_delivery selftest OK (detecta hueco sano y atrapa encimado)")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        _selftest()
        return 0
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    return run_delivery(sys.argv[1], sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    sys.exit(main())
