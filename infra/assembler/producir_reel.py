"""producir_reel.py — EL MOTOR en un comando: brief → director → QC → reel → Telegram.

El flujo diario del plan maestro (§∞): una noticia con cifras verificadas entra,
un reel del mundo de la página sale a Telegram con etiqueta APROBAR (gate humano).

    python producir_reel.py brief.json <slug> [--no-send]

Pasos (cada uno aborta el pipeline si falla):
  1. news_director.py v3 → tratamiento (menú masters, motion imposible por schema)
  2. QC de datos: TODO número que aparece en props debe existir en el brief
     (chequeo determinista contra los facts; exit si hay cifra huérfana)
  3. assemble_masters.py → VO por palabra → render MastersReel → mezcla → gates
     (motion, empalmes, filter_D — exit 1 = no hay entrega)
  4. Telegram: reel + tratamiento resumido con etiqueta APROBAR (gate de Manuel)

Voz: edge-tts placeholder mientras ELEVENLABS_API_KEY siga vencida.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\manup\projects\project-autopilot")
ASSEMBLER = ROOT / "infra" / "assembler"
DIST = ROOT / "infra" / "distribution"


def run(cmd, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd or ASSEMBLER), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


STRUCT_KEYS = {"accentIndex", "transF", "land", "durF", "min_s", "tail_s"}


def numbers_in(obj) -> set[str]:
    """Extrae tokens numéricos 'significativos' (≥2 dígitos o con decimal) de un objeto."""
    out = set()
    def walk(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if k in STRUCT_KEYS:
                    continue
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, (int, float)):
            out.add(f"{v:g}")
        elif isinstance(v, str):
            for m in re.findall(r"\d[\d,]*\.?\d*", v):
                clean = m.replace(",", "")
                if len(clean.replace(".", "")) >= 2 or "." in clean:
                    out.add(f"{float(clean):g}" if clean.replace(".", "").isdigit() else clean)
    walk(obj)
    return out


def qc_datos(brief: dict, treatment: dict) -> list[str]:
    """Toda cifra en PROPS debe rastrearse al brief. Años (1990-2030) y índices chicos exentos."""
    brief_nums = numbers_in(brief)
    issues = []
    for i, b in enumerate(treatment.get("beats", [])):
        for n in numbers_in(b.get("props", {})):
            try:
                f = float(n)
            except ValueError:
                continue
            if 1990 <= f <= 2030 and f == int(f):     # años/etiquetas de eje
                continue
            if f < 10 and any(abs(f - float(bn)) < 1e-9 for bn in brief_nums):
                continue
            if n in brief_nums or any(abs(f - float(bn)) < 1e-6 for bn in brief_nums if _isnum(bn)):
                continue
            issues.append(f"b{i}: cifra '{n}' en props NO está en el brief (¿inventada/derivada sin fuente?)")
    return issues


def _isnum(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def qc_repeticion(treatment: dict) -> list[str]:
    """RETRO 07-07 ('ya dijiste dos veces… ya ahí me perdiste, se ve hecho con AI'):
    una cifra/frase se dice UNA vez en todo el reel. Detecta (a) el mismo 5-grama
    de palabras en el VO de DOS beats distintos, (b) el mismo número-en-palabras
    largo repetido. El hook puede adelantar la cifra UNA vez; el beat que la
    desarrolla debe decirla distinto (contexto/consecuencia, no repetición)."""
    import re as _re
    import unicodedata as _ud

    def _norm(t: str) -> list[str]:
        t = _ud.normalize("NFD", t.lower())
        t = _re.sub(r"[^a-z0-9ñ ]", " ", t)
        return [w for w in t.split() if w]

    issues = []
    grams: dict[tuple, int] = {}
    for i, b in enumerate(treatment.get("beats", [])):
        ws = _norm(b.get("vo", ""))
        seen_this_beat = set()
        for j in range(len(ws) - 4):
            g = tuple(ws[j:j + 5])
            if g in seen_this_beat:
                continue
            seen_this_beat.add(g)
            if g in grams and grams[g] != i:
                issues.append(f"b{grams[g]}→b{i}: frase repetida en el VO: «{' '.join(g)}…» "
                              f"(cada beat AVANZA; una cifra se dice UNA vez)")
            grams[g] = i
    return issues


def main():
    brief_path = Path(sys.argv[1])
    slug = sys.argv[2]
    send = "--no-send" not in sys.argv
    brief = json.loads(brief_path.read_text(encoding="utf-8-sig"))

    print("═ 0/4 DIRECTOR CREATIVO (agente — gusto del fundador)")
    r = run([sys.executable, "creative_director.py", str(brief_path)])
    print(r.stdout[-800:] if r.stdout else r.stderr[-600:])
    if r.returncode != 0:
        raise SystemExit("director creativo falló")

    print("═ 1/4 DIRECTOR MECÁNICO (ejecuta la visión)")
    r = run([sys.executable, "news_director.py", str(brief_path)])
    print(r.stdout[-1200:] if r.stdout else r.stderr[-600:])
    if r.returncode != 0:
        raise SystemExit("director falló")
    treatment_path = ASSEMBLER / "out" / "_treatments" / "news_treatment.json"
    treatment = json.loads(treatment_path.read_text(encoding="utf-8-sig"))

    print("═ 2/4 QC DE DATOS (props vs brief) + ANTI-REPETICIÓN")
    issues = qc_datos(brief, treatment) + qc_repeticion(treatment)
    for x in issues:
        print("  ⚠", x)
    if issues:
        raise SystemExit("QC falló — revisar tratamiento antes de producir")
    print("  ✔ cifras rastreadas al brief · sin repeticiones en el VO")

    dst = ASSEMBLER / "treatments" / f"{slug}.json"
    dst.write_text(json.dumps(treatment, ensure_ascii=False, indent=2), encoding="utf-8")

    print("═ 3/4 ENSAMBLE (VO → render → mezcla → gates)")
    r = run([sys.executable, "assemble_masters.py", str(dst), slug])
    print(r.stdout[-1500:] if r.stdout else "")
    if r.returncode != 0:
        print(r.stderr[-800:])
        raise SystemExit("ensamble/gates fallaron — no hay entrega")

    final = ASSEMBLER / "out" / slug / f"{slug}_FINAL_916.mp4"
    if not send:
        print(f"═ LISTO (sin enviar): {final}")
        return 0

    print("═ 4/4 TELEGRAM (gate humano)")
    sys.path.insert(0, str(DIST))
    from send_review import send_video_file
    vo_total = sum(len(b.get("vo", "").split()) for b in treatment["beats"])
    arco = " → ".join(b["type"] for b in treatment["beats"])
    cap = (f"APROBAR? · {treatment.get('topic', slug)}\n\n"
           f"HOOK: {treatment.get('hook_text','')}\n"
           f"Arco: {arco} · VO {vo_total} palabras · gates PASS\n\n"
           "Producido 100% por el motor (director→masters→mezcla). "
           "SÍ = listo para publicar (voz placeholder hasta refrescar ElevenLabs) · NO = dime qué falla.")
    mid = send_video_file(final, cap)
    print(f"  enviado msg_id={mid}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
