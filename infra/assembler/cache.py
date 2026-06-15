# -*- coding: utf-8 -*-
"""
Cache content-addressed para el pipeline Dinero IA.

Reemplaza el cache por existencia/mtime. mtime es fragil: NO es contenido. Un
re-TTS, un git checkout/restore, copiar out/ entre maquinas, o las pestanas
paralelas tocando beats compartidos reordenan mtimes -> se reusa un insumo
viejo en SILENCIO. Asi escapo 4 veces el bug de voces encimadas (seg 21/44):
el wav loudnorm viejo seguia en disco aunque el mp3 ya se habia re-grabado.

Regla unica:
    reconstruir  <=>  input_key(insumos) != key guardado en el sidecar.

El key sale del CONTENIDO de los insumos (sha256 de bytes / de texto), no de
su fecha. Sidecar por artefacto: <artefacto>.meta.json
    { input_key, recipe, built_at, output_sha256? }

Modulo aislado de stdlib (sin deps): se puede leer/tocar sin entender FFmpeg.
"""
import hashlib
import json
import time
from pathlib import Path


def file_sha(path) -> str:
    """sha256 de los BYTES del archivo (streaming, sirve para wav/mp4 pesados)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_sha(root, exts=(".ts", ".tsx")) -> str:
    """sha256 del ARBOL de fuentes (ruta relativa + contenido) bajo `root`.

    Por que existe: el render de un beat depende del CODIGO del componente
    (.tsx) y de lo que importa (theme, StudioScene). El key de render no lo
    hasheaba -> editar StudioScene.tsx NO invalidaba el mp4 viejo: el mismo bug
    de artefacto-viejo-en-disco, una capa arriba. Hashear el arbol entero cierra
    el hueco: cualquier cambio de fuente -> key distinto -> re-render.

    Determinista: ordena por ruta relativa POSIX (independiente del OS) e
    incluye la ruta para que un rename tambien invalide. NO depende de mtime.
    """
    root = Path(root)
    h = hashlib.sha256()
    files = sorted(
        (p for p in root.rglob("*") if p.is_file() and p.suffix in exts),
        key=lambda p: p.relative_to(root).as_posix(),
    )
    for p in files:
        h.update(p.relative_to(root).as_posix().encode("utf-8"))
        h.update(b"\x1f")
        h.update(file_sha(p).encode("utf-8"))
        h.update(b"\x1e")
    return h.hexdigest()


def _norm(part) -> str:
    # dict/list -> JSON canonico (orden estable) para que el key no dependa del
    # orden de las llaves. Lo demas -> str.
    if isinstance(part, (dict, list)):
        return json.dumps(part, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":"))
    return str(part)


def key(recipe: str, *parts) -> str:
    """Key determinista = H(recipe + cada insumo). 'recipe' = version de la
    receta (ej. 'loud.v1'); subirla invalida todo a proposito (cambio de logica)."""
    h = hashlib.sha256()
    h.update(recipe.encode("utf-8"))
    for p in parts:
        h.update(b"\x1f")  # separador para que (a,bc) != (ab,c)
        h.update(_norm(p).encode("utf-8"))
    return h.hexdigest()


def _meta_path(artifact: Path) -> Path:
    return artifact.with_name(artifact.name + ".meta.json")


def read_key(artifact: Path):
    mp = _meta_path(Path(artifact))
    if not mp.exists():
        return None
    try:
        return json.loads(mp.read_text(encoding="utf-8")).get("input_key")
    except Exception:
        return None


def stamp(artifact, input_key: str, recipe: str, record_output: bool = False):
    artifact = Path(artifact)
    meta = {
        "input_key": input_key,
        "recipe": recipe,
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if record_output and artifact.exists():
        # el sha del OUTPUT se registra para auditar/diff, NO para decidir
        # rebuild (Remotion/ffmpeg no son bit-identicos entre corridas).
        meta["output_sha256"] = file_sha(artifact)
    _meta_path(artifact).write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


def need_build(artifact, input_key: str, recipe: str, adopt: bool = False) -> bool:
    """True si hay que (re)construir el artefacto.

    adopt=True: si el artefacto EXISTE pero no tiene sidecar (migracion desde el
    cache viejo por-existencia), se ADOPTA: se le estampa el key actual y NO se
    reconstruye. Para insumos caros/externos (VO de ElevenLabs = $, render de
    minutos) evita re-pagar / re-renderizar en la primera corrida tras migrar.
    Para insumos baratos y criticos (wav loudnorm local = epicentro del bug)
    usar adopt=False -> se reconstruye y queda content-addressed de una.
    """
    artifact = Path(artifact)
    if not artifact.exists():
        return True
    saved = read_key(artifact)
    if saved is None:
        if adopt:
            stamp(artifact, input_key, recipe)
            return False
        return True
    return saved != input_key


def _selftest():
    import tempfile
    d = Path(tempfile.mkdtemp())
    a = d / "art.bin"
    a.write_bytes(b"hello")
    k1 = key("r.v1", file_sha(a), "param")
    assert need_build(a, k1, "r.v1"), "sin meta -> debe construir"
    stamp(a, k1, "r.v1")
    assert not need_build(a, k1, "r.v1"), "mismo key -> debe saltar"

    a.write_bytes(b"world")  # el insumo cambio de contenido (mismo nombre)
    k2 = key("r.v1", file_sha(a), "param")
    assert k2 != k1, "contenido distinto -> key distinto"
    assert need_build(a, k2, "r.v1"), "contenido cambio -> debe reconstruir"

    # esto es EXACTO el bug del wav: el insumo (mp3) cambia de bytes pero el
    # artefacto (wav) viejo sigue en disco. Con content-addressing, su key viejo
    # no matchea -> se reconstruye. Sin mtime, sin carrera.
    stamp(a, k2, "r.v1")
    assert not need_build(a, k2, "r.v1")

    # adopt: artefacto preexistente sin sidecar
    b = d / "b.bin"
    b.write_bytes(b"x")
    kb = key("r.v1", file_sha(b))
    assert not need_build(b, kb, "r.v1", adopt=True), "adopt -> no reconstruye"
    assert read_key(b) == kb, "adopt estampa el sidecar"
    assert not need_build(b, kb, "r.v1"), "ya adoptado -> salta sin adopt"

    # tree_sha: editar CUALQUIER fuente del arbol cambia el key del render
    src = d / "src"
    (src / "beats").mkdir(parents=True)
    (src / "theme.ts").write_text("export const c = 1;", encoding="utf-8")
    (src / "beats" / "Big.tsx").write_text("// v1", encoding="utf-8")
    t1 = tree_sha(src)
    assert tree_sha(src) == t1, "tree_sha estable si nada cambia"
    (src / "beats" / "Big.tsx").write_text("// v2 editado", encoding="utf-8")
    assert tree_sha(src) != t1, "editar un componente -> tree_sha distinto"
    print("cache.py selftest OK")


if __name__ == "__main__":
    _selftest()
