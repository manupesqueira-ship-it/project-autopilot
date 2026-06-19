#!/usr/bin/env python3
"""
build_story.py - Genera el STORY-TEASER (vertical 9:16, ~6s, $0, SIN voz) de un
guion de Dinero LATAM.

Es la pieza CORTA y simple que jala al post del dia: un solo hook kinetico con
sonido (cama Envato + SFX) renderizado por la composicion Remotion `StoryHook`.
NO es el reel del feed (ese lo arma build916.py). Aqui no hay voz ElevenLabs ->
costo $0.

De donde salen los props del Story (en orden de prioridad):
  1) bloque `story` del guion -> control editorial explicito, o
  2) fallback automatico:
       question     = caption.hook  (o 1a frase del vo del primer beat)
       accentWords  = tokens accent:true del primer beat que SI aparecen en el hook
       punch        = ""            (NO se inventa un dato; el hero dorado se omite)
       cta          = default que manda al post

Datos SIEMPRE exactos del guion; si el bloque story no trae `punch`, no se inventa.

Calidad = misma receta que el reel: render --scale=2 (supersampling 2160x3840) ->
downscale lanczos a 1080x1920 con libx264 crf15 (texto sin "shimmer"). El audio que
ya mezclo Remotion (cama + SFX, con su fade) se copia tal cual.

USO:
  python build_story.py guion_edu_regla_72.json
      -> infra/assembler/out/{slug}/{slug}_STORY_916.mp4

Importable desde el orquestador (producir.py):
  from build_story import build_story          # build_story(guion_path) -> Path
"""
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
REMOTION_DIR = ROOT / "infra" / "remotion-render"
ASSEMBLER_OUT = ROOT / "infra" / "assembler" / "out"

COMP = "StoryHook"
STORY_FRAMES = 180          # 6s @ 30fps; CASADO con el fade de audio del componente
FPS = 30
CTA_DEFAULT = "te lo explico en el post de hoy"


class BuildError(RuntimeError):
    """Falla de render/encode del Story (la atrapa producir.py sin matar el post)."""


def _run(args, cwd=None):
    p = subprocess.run(args, capture_output=True, text=True, cwd=cwd, shell=False)
    if p.returncode != 0:
        print("CMD ERR:", " ".join(str(a) for a in args))
        print((p.stderr or p.stdout)[-3000:])
        raise BuildError(f"comando fallo (rc={p.returncode}): {args[0]} ...")
    return p


def _load_guion(path) -> dict:
    if isinstance(path, dict):
        return path
    # utf-8-sig: los guiones escritos desde PowerShell traen BOM
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _norm(w: str) -> str:
    w = unicodedata.normalize("NFD", w)
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r'[¿?¡!.,;:"]', "", w).lower()


def _first_sentence(text: str, limit: int = 90) -> str:
    s = re.split(r"(?<=[.?!])\s", text.strip())[0]
    return s if len(s) <= limit else s[:limit].rstrip() + "…"


def _accent_tokens(beat: dict) -> list:
    """Saca los tokens accent:true del primer beat (BeatKinetic.props.lines)."""
    out = []
    for line in (beat.get("props", {}) or {}).get("lines", []) or []:
        for tok in line:
            if isinstance(tok, dict) and tok.get("accent") and tok.get("text"):
                out.append(tok["text"])
    return out


def derive_props(guion: dict) -> dict:
    """Resuelve los props de StoryHook: bloque `story` -> fallback al caption/beats."""
    story = guion.get("story") or {}
    beats = guion.get("beats") or []
    caption = guion.get("caption") or {}

    # question
    question = story.get("question") or caption.get("hook")
    if not question and beats:
        question = _first_sentence(beats[0].get("vo", ""))
    if not question:
        raise BuildError("no hay de donde sacar la pregunta del Story "
                         "(falta story.question, caption.hook y beats[0].vo)")

    # accentWords
    if "accentWords" in story:
        accent_words = story["accentWords"]
    else:
        qset = {_norm(w) for w in question.split()}
        accent_words = [t for t in (_accent_tokens(beats[0]) if beats else [])
                        if _norm(t) in qset]

    props = {
        "question": question,
        "accentWords": accent_words,
        "punch": story.get("punch", ""),          # vacio = sin hero dorado (no inventar)
        "cta": story.get("cta", CTA_DEFAULT),
        "durationInFrames": STORY_FRAMES,
    }
    if story.get("kicker"):
        props["kicker"] = story["kicker"]
    if story.get("accent"):
        props["accent"] = story["accent"]
    return props


def build_story(guion_path, out_root: Path = ASSEMBLER_OUT) -> Path:
    """Renderiza el Story-teaser. Devuelve la ruta al MP4 1080x1920 listo para IG."""
    guion = _load_guion(guion_path)
    slug = guion["slug"]
    props = derive_props(guion)

    out_dir = Path(out_root) / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    final = out_dir / f"{slug}_STORY_916.mp4"
    raw2x = out_dir / f"_{slug}_story_raw2x.mp4"

    # props sin BOM (encoding="utf-8" NO escribe BOM); --props de Remotion lo exige
    props_file = out_dir / f"{slug}.story.props.json"
    props_file.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")

    print(f"[story] render {COMP} ({STORY_FRAMES}f, scale2) -> {raw2x.name}")
    _run(["npx.cmd", "remotion", "render", COMP, str(raw2x),
          f"--props={props_file}", "--concurrency=4", "--crf=16",
          "--scale=2", "--timeout=600000"],
         cwd=str(REMOTION_DIR))

    # downscale lanczos 2160x3840 -> 1080x1920 (misma receta de calidad que el reel)
    # + fade limpio desde/hacia negro. El audio ya viene mezclado por Remotion -> copy.
    total = STORY_FRAMES / FPS
    vf = (f"scale=1080:1920:flags=lanczos,format=yuv420p,setsar=1,fps={FPS},"
          f"fade=t=in:st=0:d=0.25,fade=t=out:st={max(total - 0.5, 0):.3f}:d=0.5")
    print(f"[story] downscale lanczos -> {final.name}")
    _run(["ffmpeg", "-y", "-i", str(raw2x), "-vf", vf,
          "-c:v", "libx264", "-preset", "slow", "-crf", "15",
          "-pix_fmt", "yuv420p", "-c:a", "copy", str(final)])

    try:
        raw2x.unlink()
    except OSError:
        pass

    print(f"[story] OK {final}")
    return final


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass
    if len(sys.argv) < 2:
        raise SystemExit("USO: python build_story.py <guion.json>")
    guion_path = sys.argv[1]
    if not Path(guion_path).is_absolute():
        # acepta tanto ruta suelta como nombre dentro de infra/assembler
        cand = ROOT / "infra" / "assembler" / guion_path
        if cand.exists():
            guion_path = cand
    out = build_story(guion_path)
    print(out)


if __name__ == "__main__":
    main()
