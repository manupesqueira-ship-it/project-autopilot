# -*- coding: utf-8 -*-
"""
Ledger de videos producidos para Dinero IA.

Fuente de verdad en Python (sirve con o sin n8n). Guarda, por cada video
entregado, su tema, los beats usados y la fecha. El planner y el validador
lo leen para BLOQUEAR:
  - repeticion de TEMA (que no se vuelva a hacer un video del mismo tema), y
  - repeticion de COMBINACION VISUAL de beats (que dos videos no usen el mismo
    set de graficas/visuales -> fuerza variedad).

EMPIEZA VACIO a proposito: los 6 guiones viejos NO se siembran ("esos ya fueron").

Uso como modulo:
    from ledger import Ledger
    led = Ledger()
    rep, slug = led.is_tema_repeated("El Salvador y el bitcoin")
    rep, slug = led.is_combo_repeated(["BeatKinetic", "BeatMapZoom", ...])
    led.append_video(slug, tema, beats, fecha="2026-06-13")

Uso como CLI:
    python ledger.py list
    python ledger.py check guion_x.json          # exit 0 si es novedoso, 1 si repite
    python ledger.py append guion_x.json [--tema "..."] [--fecha YYYY-MM-DD]
"""
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
DEFAULT_LEDGER = HERE / "ledger.json"

# Umbral de similitud de tema (Jaccard de tokens de contenido). >= => repetido.
TEMA_SIMILARITY_THRESHOLD = 0.45

# La FIRMA visual de un video = sus beats del MEDIO. Se EXCLUYEN las puntas del
# arco (hook, climax-cifra y cierre): R4/R5 las obligan en CADA video, asi que no
# distinguen un video de otro ni rotan por la firma -> las rota R11 aparte. Antes
# esto era una lista-BLANCA que se quedaba vieja al crecer el catalogo (listaba
# ~15 de ~39 beats); ahora es una lista-NEGRA: cualquier Beat* nuevo entra a la
# firma solo, sin tocar este archivo.
# Este set debe espejar la UNION de HOOK_TYPES | CLIMAX_TYPES | CTA_TYPES del
# validador (todas las puntas posibles del arco); si abres un slot a un tipo
# nuevo alla, agregalo aqui para que R11 lo gobierne y NO la recencia R10.
SIGNATURE_EXCLUDE = {
    "BeatKinetic",      # hook: kinetic word-by-word (R4)
    "BeatStatCallout",  # hook alterno: cifra-shock de apertura
    "BeatNapkin",       # hook set-piece: formula en servilleta (la castea el director; la rota R11, no la firma)
    "BeatNewspaper",    # hook set-piece: titular de periodico (director; rota R11)
    "BeatPhone",        # hook set-piece: notificacion de telefono (director; rota R11)
    "BeatChalkboard",   # hook set-piece: leccion en pizarron (director; rota R11)
    "BeatTicket",       # hook set-piece: recibo/ticket (director; rota R11)
    "BeatBigNumber",    # climax: la cifra protagonista
    "BeatHeroCoin",     # climax alterno: cifra protagonista en moneda 3D
    "BeatCta",          # cierre: siempre el ultimo beat (R5)
}

_STOPWORDS = {
    "de", "el", "la", "los", "las", "un", "una", "unos", "unas", "que", "en",
    "y", "a", "al", "con", "por", "para", "su", "sus", "lo", "se", "es", "fue",
    "no", "ni", "todo", "toda", "del", "mas", "muy", "ya", "pero", "como",
    "este", "esta", "esto", "esos", "esas", "ese", "esa", "hizo", "hoy", "le",
    "sin", "sobre", "entre", "cuando", "donde", "the", "of", "to",
}


def _strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def _content_tokens(text):
    """Tokens normalizados (sin acentos, sin stopwords, sin numeros sueltos)."""
    text = _strip_accents(str(text).lower())
    toks = re.findall(r"[a-z0-9]+", text)
    return {t for t in toks if t not in _STOPWORDS and not t.isdigit() and len(t) > 2}


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def signature_types(beats):
    """Tipos de beat que forman la FIRMA visual del video (los del medio).

    Cuenta cualquier `Beat*` salvo las puntas del arco (SIGNATURE_EXCLUDE), asi
    que es autosostenible: un beat nuevo del catalogo entra sin tocar nada.
    `beats` = lista de tipos (str) o de dicts con 'type'.
    """
    out = []
    for b in beats:
        t = b.get("type") if isinstance(b, dict) else b
        if isinstance(t, str) and t.startswith("Beat") and t not in SIGNATURE_EXCLUDE:
            out.append(t)
    return out


def _visual_signature(beats):
    """Firma de combinacion (multiset ordenado de beats de firma) para comparar
    dos videos: misma firma == misma mezcla visual del medio."""
    return tuple(sorted(signature_types(beats)))


class Ledger:
    def __init__(self, path=DEFAULT_LEDGER):
        self.path = Path(path)
        self.data = {"videos": []}
        if self.path.exists():
            raw = self.path.read_text(encoding="utf-8-sig").strip()
            if raw:
                self.data = json.loads(raw)
        self.data.setdefault("videos", [])

    # ---- lecturas ----
    @property
    def videos(self):
        return self.data["videos"]

    def temas(self):
        return [v.get("tema", "") for v in self.videos]

    def combos(self):
        return [tuple(_visual_signature(v.get("beats_usados", []))) for v in self.videos]

    def is_tema_repeated(self, tema, threshold=TEMA_SIMILARITY_THRESHOLD):
        """Devuelve (repetido: bool, slug_match | None, similitud)."""
        toks = _content_tokens(tema)
        best_slug, best_sim = None, 0.0
        for v in self.videos:
            sim = _jaccard(toks, _content_tokens(v.get("tema", "")))
            if sim > best_sim:
                best_slug, best_sim = v.get("slug"), sim
        return (best_sim >= threshold, best_slug, round(best_sim, 3))

    def is_combo_repeated(self, beats):
        """Devuelve (repetido: bool, slug_match | None).

        Repetido = otro video ya uso EXACTAMENTE la misma combinacion de beats
        visuales. Fuerza que cada video estrene una mezcla visual distinta.
        """
        sig = _visual_signature(beats)
        if not sig:
            return (False, None)
        for v in self.videos:
            if _visual_signature(v.get("beats_usados", [])) == sig:
                return (True, v.get("slug"))
        return (False, None)

    def recent_beats(self, n):
        """Conjunto de beats de FIRMA usados en los ultimos n videos producidos.

        Alimenta la regla de RECENCIA del validador (R10): a 3 videos/dia,
        repetir el mismo visual de un dia para otro cansa al espectador diario.
        n<=0 -> vacio (recencia desactivada).
        """
        if n <= 0:
            return set()
        recent = set()
        for v in self.videos[-n:]:
            recent |= set(signature_types(v.get("beats_usados", [])))
        return recent

    def has_slug(self, slug):
        return any(v.get("slug") == slug for v in self.videos)

    # ---- escrituras ----
    def append_video(self, slug, tema, beats, fecha=None, save=True):
        """Registra un video producido. `beats` = lista de tipos o de dicts."""
        types = [(b.get("type") if isinstance(b, dict) else b) for b in beats]
        entry = {
            "slug": slug,
            "tema": tema,
            "beats_usados": types,
            "fecha": fecha or date.today().isoformat(),
        }
        self.videos.append(entry)
        if save:
            self.save()
        return entry

    def save(self):
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8")


# ----------------------------- CLI -----------------------------
def _load_guion(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def _cli(argv):
    if not argv:
        print(__doc__)
        return 0
    cmd = argv[0]
    led = Ledger()

    if cmd == "list":
        if not led.videos:
            print("(ledger vacio)")
            return 0
        for v in led.videos:
            print(f"  {v['fecha']}  {v['slug']:30s}  {v.get('beats_usados')}")
        return 0

    if cmd in ("check", "append"):
        if len(argv) < 2:
            print("falta el guion JSON"); return 2
        g = _load_guion(argv[1])
        slug = g.get("slug", "")
        beats = g.get("beats", [])
        tema = g.get("title", "") or slug
        if "--tema" in argv:
            tema = argv[argv.index("--tema") + 1]
        fecha = None
        if "--fecha" in argv:
            fecha = argv[argv.index("--fecha") + 1]

        rep_t, slug_t, sim = led.is_tema_repeated(tema)
        rep_c, slug_c = led.is_combo_repeated(beats)
        if rep_t:
            print(f"TEMA REPETIDO (sim {sim}) vs '{slug_t}'")
        if rep_c:
            print(f"COMBO VISUAL REPETIDO vs '{slug_c}'")
        if led.has_slug(slug):
            print(f"SLUG '{slug}' ya existe en el ledger")

        if cmd == "check":
            novel = not (rep_t or rep_c or led.has_slug(slug))
            print("NOVEDOSO" if novel else "REPITE")
            return 0 if novel else 1

        # append
        led.append_video(slug, tema, beats, fecha=fecha)
        print(f"REGISTRADO: {slug} ({tema}) {len(beats)} beats -> {led.path.name}")
        return 0

    print(f"comando desconocido: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
