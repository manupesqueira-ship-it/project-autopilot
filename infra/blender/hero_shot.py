# -*- coding: utf-8 -*-
"""
hero_shot.py  --  Lane HERO-SHOT bespoke (Dinero IA, Track B3).

El carril para temas con un objeto/evento ICONICO unico que NO esta en el
catalogo de set-pieces (un cohete, un lingote, el edificio de un banco central):
se SOURCEA un modelo 3D libre (Poly Haven CC0 / NASA dominio publico / modelo
propio) y se mete al template premium (studio_premium.py) + un CAMERA MOVE $0
(swing + push-in con motion blur y DoF). Mismo contrato de salida que la moneda
y las graficas 3D: secuencia PNG RGBA -> encode_host.py -> WebM -> Remotion
OffthreadVideo. El dato/cifra NUNCA se hornea en el 3D (la IA/los modelos no son
de fiar con texto): va en overlay controlado en Remotion, como todos los beats.

img2vid de PAGA (Higgsfield/Kling) queda SOLO para cuando el objeto deba moverse
de verdad (un cohete despegando); este lane $0 cubre la mayoria con un camera
move sobre el objeto quieto. El gasto img2vid esta gateado (avisar costo).

GOBERNANZA DE LICENCIA (regla B3, en codigo, no solo en prosa): este script solo
renderiza un asset REGISTRADO en `hero_assets.json` con licencia comercial
confirmada (`comercial_ok`) y sin logos de marca (`brand_safe`). Registrar un
asset = el acto de verificar su licencia. Mismo espiritu que el catalogo cerrado
de set-pieces: no se castea de un prompt en blanco.

Sin `--asset` cae a un HERO PROCEDURAL ($0, render-testable): un lingote de oro
biselado (objeto "dinero" iconico) -> ejercita TODO el lane (auto-encuadre +
camera move + template) sin descargar nada, para validar luz/DoF/blur en R1.

NO renderiza ahora; se ESCRIBE. Render en el lote final (R1):
    cd infra/blender
    # procedural (sin descargar nada):
    blender --background --python hero_shot.py -- --out out_hero --prefix hero_
    # con un modelo libre ya registrado en hero_assets.json:
    blender --background --python hero_shot.py -- --out out_hero --prefix hero_ --asset ingot_polyhaven
    python encode_host.py --dir out_hero --prefix hero_ --out hero.webm --no-upload

Salida: out_hero/hero_#####.png (RGBA transparente, ~84 frames @30fps).
"""
import json
import math
import os
import random
import sys

import bpy  # noqa: E402  (solo dentro de Blender; py_compile no lo ejecuta)
import mathutils  # noqa: E402  (idem; modulo de Blender)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import studio_premium as sp  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
HERO_ASSETS = os.path.join(HERE, "hero_assets.json")
FRAMES = 84  # ~2.8s @30fps: entrada + swing/push-in + asiento


# --------------------------------------------------------- color (sRGB->linear)
def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h, a=1.0):
    """'#D4A574' -> (r,g,b,a) en espacio LINEAL (lo que espera el Principled)."""
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (_srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b), a)


# paleta semantica locked (Style Bible §3 / theme.ts / CLAUDE.md)
PALETTE = {
    "green": "#00D9A5",   # sube / seguro / marca
    "red": "#FF6B6B",     # SOLO perdida
    "teal": "#5BC0BE",    # neutral
    "gold": "#D4A574",    # dinero
}


# ------------------------------------------------------ licencia (gobernanza B3)
def resolve_asset(asset_id):
    """(filepath, entry) del asset si esta REGISTRADO, es comercial-OK y brand-safe.

    None -> procedural. SystemExit si el asset no cumple la gobernanza (la regla
    B3: licencia comercial verificada por asset, sin logos de marca)."""
    if not asset_id:
        return None, None
    if not os.path.exists(HERO_ASSETS):
        raise SystemExit(f"hero_shot: falta {HERO_ASSETS} (registro de licencias).")
    man = json.loads(open(HERO_ASSETS, encoding="utf-8-sig").read())
    entry = next((a for a in man.get("assets", []) if a.get("id") == asset_id), None)
    if entry is None:
        raise SystemExit(
            f"hero_shot: asset '{asset_id}' NO esta en hero_assets.json. Registralo "
            f"con su fuente + licencia ANTES de usarlo (regla B3: licencia comercial "
            f"verificada por asset; el registro ES la verificacion).")
    if not entry.get("comercial_ok"):
        raise SystemExit(
            f"hero_shot: asset '{asset_id}' sin licencia comercial confirmada "
            f"(comercial_ok=false) -> NO se renderiza.")
    if not entry.get("brand_safe", False):
        raise SystemExit(
            f"hero_shot: asset '{asset_id}' brand_safe=false (posible logo de marca) "
            f"-> NO se renderiza.")
    if entry.get("tipo") == "procedural" or entry.get("file") in (None, "", "(procedural)"):
        return None, entry  # registrado pero procedural
    path = entry["file"]
    if not os.path.isabs(path):
        path = os.path.join(HERE, path)
    if not os.path.exists(path):
        raise SystemExit(f"hero_shot: el archivo de '{asset_id}' no existe: {path}")
    return path, entry


# ----------------------------------------------------------------- importacion
def import_model(path):
    """Importa .glb/.gltf/.obj/.fbx/.stl. Devuelve los objetos NUEVOS creados.

    Tolera los renombres de operador entre Blender 3.x/4.x/5.x (obj/stl pasaron
    a bpy.ops.wm.*_import)."""
    ext = os.path.splitext(path)[1].lower()
    before = set(bpy.data.objects)
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext == ".obj":
        if hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(filepath=path)
        else:  # Blender <=3.x
            bpy.ops.import_scene.obj(filepath=path)
    elif ext == ".stl":
        if hasattr(bpy.ops.wm, "stl_import"):
            bpy.ops.wm.stl_import(filepath=path)
        else:
            bpy.ops.import_mesh.stl(filepath=path)
    else:
        raise SystemExit(f"hero_shot: extension no soportada '{ext}' (usa glb/gltf/obj/fbx/stl)")
    new = [o for o in bpy.data.objects if o not in before]
    if not new:
        raise SystemExit(f"hero_shot: el import no creo objetos desde {path}")
    return new


def _procedural_hero():
    """Hero PROCEDURAL $0 (sin descarga): un lingote de oro biselado -> objeto
    'dinero' iconico que ejercita todo el lane para validar luz/DoF/blur en R1."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    bar = bpy.context.active_object
    bar.name = "HeroIngot"
    bar.scale = (1.7, 0.95, 0.6)
    bev = bar.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.07
    bev.segments = 5
    bpy.ops.object.shade_smooth()
    bar.data.materials.append(
        sp.pbr_metal("Ingot", hex_lin(PALETTE["gold"]), rough=0.17, coat=0.6))
    return [bar]


def _one_coin(loc, rotz=0.0, r=1.0, t=0.16, tiltx=0.0, emblem=False, tag="Coin"):
    """Una moneda: cilindro con canto BISELADO. Si emblem=True le agrega RELIEVE
    en la cara +Z (borde realzado + sol radiante + boton central) -> lee como
    MONEDA, no como ficha/disco. El relieve es geometria, NO texto (brand_safe).
    Se ensambla en el ORIGEN y luego se traslada/inclina rigido (los hijos del
    relieve siguen al cuerpo). Devuelve [cuerpo, *partes_relieve]."""
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=r, depth=t, location=(0, 0, 0))
    body = bpy.context.active_object
    body.name = tag
    bev = body.modifiers.new("Bevel", "BEVEL")
    bev.width = t * 0.18
    bev.segments = 4
    bpy.ops.object.shade_smooth()
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(34))
    except Exception:
        pass

    if emblem:
        zf = t * 0.5  # cara superior
        # borde realzado (anillo): torus aplanado en el canto de la cara
        bpy.ops.mesh.primitive_torus_add(
            location=(0, 0, zf), major_radius=r * 0.88, minor_radius=r * 0.05)
        ring = bpy.context.active_object
        ring.name = tag + "_Ring"
        ring.scale.z = 0.45
        bpy.ops.object.shade_smooth()
        parts.append(ring)
        # sol radiante: rayos finos alrededor del centro (iconografia de moneda LATAM)
        rays = 18
        for k in range(rays):
            a = (2 * math.pi / rays) * k
            cx, cy = math.cos(a) * r * 0.5, math.sin(a) * r * 0.5
            bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, zf + t * 0.18))
            ray = bpy.context.active_object
            ray.name = f"{tag}_Ray{k:02d}"
            ray.rotation_euler = (0, 0, a)
            ray.scale = (r * 0.34, r * 0.028, t * 0.14)  # X largo = radial
            bpy.ops.object.shade_smooth()
            parts.append(ray)
        # boton central
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=48, radius=r * 0.2, depth=t * 0.55, location=(0, 0, zf + t * 0.12))
        boss = bpy.context.active_object
        boss.name = tag + "_Boss"
        bb = boss.modifiers.new("Bevel", "BEVEL")
        bb.width = t * 0.06
        bb.segments = 3
        bpy.ops.object.shade_smooth()
        parts.append(boss)
        for p in parts:  # ensamblar al cuerpo en el ORIGEN (inverse = identidad)
            p.parent = body

    body.rotation_euler = (tiltx, 0.0, rotz)
    body.location = loc
    return [body] + parts


def _procedural_coin_stack(seed=7):
    """Hero PROCEDURAL $0: una COMPOSICION de dinero coherente -> stack de monedas
    de oro (canto abanicado) + UNA moneda hero inclinada hacia camara con relieve
    (sol radiante) + un par de monedas derramadas. El stack da el 'lomo' de cantos;
    la moneda hero muestra la CARA con relieve -> lee inequivoco como dinero, no
    fichas. Todo el mismo material/luz/mundo = UN plano coherente (leccion R1), sin
    texto/logo (brand_safe), $0. La cifra exacta va en overlay Remotion."""
    random.seed(seed)
    # oro-MONEDA: amarillo rico (no el tan #D4A574 de UI, que bajo el HDRI calido
    # lee rosa/cobre). El gold semantico locked es para tipo/UI; el METAL fisico de
    # una moneda lee dinero solo si es amarillo-oro saturado. rough bajo = pulido.
    gold = sp.pbr_metal("CoinGold", hex_lin("#E8B23C"), rough=0.16, coat=0.55)
    r, t = 1.0, 0.16
    objs = []

    # stack abanicado (el 'lomo' de cantos) -> CENTRO-ATRAS, el sujeto principal
    lean = mathutils.Vector((0.0, 0.0))
    for i in range(9):
        lean += mathutils.Vector((random.uniform(-0.012, 0.018),
                                  random.uniform(-0.015, 0.015)))
        loc = (lean.x + random.uniform(-0.02, 0.02),
               0.55 + lean.y + random.uniform(-0.02, 0.02),  # +Y = atras
               t * 0.5 + i * t)
        objs += _one_coin(loc, rotz=random.uniform(-0.38, 0.38), r=r, t=t, tag=f"Stack{i:02d}")

    # moneda HERO: a la IZQUIERDA-frente, inclinada con la CARA a camara (-Y), con
    # relieve. Mas chica que el stack y CORRIDA al carril izquierdo -> NO encima al
    # stack (leccion 'no encimar elementos'); ambos se leen completos.
    objs += _one_coin((-1.55, -1.35, 0.92), rotz=0.14, r=1.15, t=0.18,
                      tiltx=math.radians(62), emblem=True, tag="HeroCoin")

    # monedas derramadas (caras a la vista) -> carril DERECHO-frente
    objs += _one_coin((1.5, -1.15, t * 0.5), rotz=0.5, r=1.05, t=t, tag="Spill0")
    objs += _one_coin((1.15, -0.2, t * 0.5), rotz=-0.7, r=0.95, t=t, tag="Spill1")

    for o in objs:
        if o.type == "MESH" and not o.data.materials:
            o.data.materials.append(gold)
    return objs


# -------------------------------------------------------- material (override)
def _make_material(key):
    """Material PBR de override; None = conservar los materiales importados."""
    if key in (None, "", "keep", "none"):
        return None
    if key == "gold":
        return sp.pbr_metal("HeroGold", hex_lin(PALETTE["gold"]), rough=0.18, coat=0.6)
    if key == "silver":
        return sp.pbr_metal("HeroSilver", (0.95, 0.95, 0.97, 1.0), rough=0.16, coat=0.6)
    if key == "teal":
        return sp.pbr_metal("HeroTeal", hex_lin(PALETTE["teal"]), rough=0.30, coat=0.5)
    if key in ("gold-glow", "glow"):
        return sp.pbr_emission("HeroGlow", hex_lin(PALETTE["gold"]), strength=3.0)
    if key == "green":
        return sp.pbr_emission("HeroGreen", hex_lin(PALETTE["green"]), strength=2.6)
    return None


def _override_material(objs, key):
    mat = _make_material(key)
    if mat is None:
        return
    for o in objs:
        if o.type != "MESH":
            continue
        o.data.materials.clear()
        o.data.materials.append(mat)


# --------------------------------------------------- auto-encuadre + camera move
def _bbox_world(meshes):
    big = 1e18
    mn = mathutils.Vector((big, big, big))
    mx = mathutils.Vector((-big, -big, -big))
    for o in meshes:
        for c in o.bound_box:
            w = o.matrix_world @ mathutils.Vector((c[0], c[1], c[2]))
            mn.x, mn.y, mn.z = min(mn.x, w.x), min(mn.y, w.y), min(mn.z, w.z)
            mx.x, mx.y, mx.z = max(mx.x, w.x), max(mx.y, w.y), max(mx.z, w.z)
    return mn, mx


def frame_objects(objs, target_size=3.2):
    """Centra el modelo en el eje vertical del origen, lo escala a `target_size`
    y lo cuelga de un pivote (para el swing). Devuelve (pivote, altura)."""
    meshes = [o for o in objs if o.type == "MESH"]
    if not meshes:
        raise SystemExit("hero_shot: el modelo no trae mallas para encuadrar")
    mn, mx = _bbox_world(meshes)
    center = (mn + mx) / 2.0
    dims = mx - mn
    biggest = max(dims.x, dims.y, dims.z) or 1.0
    s = target_size / biggest

    # transforma SOLO las raices (los hijos siguen via jerarquia). G es global:
    # primero lleva el centro-base de la bbox al origen, luego escala.
    roots = [o for o in objs if o.parent not in objs]
    T = mathutils.Matrix.Translation((-center.x, -center.y, -mn.z))
    S = mathutils.Matrix.Scale(s, 4)
    G = S @ T
    for o in roots:
        o.matrix_world = G @ o.matrix_world

    pivot = bpy.data.objects.new("HeroPivot", None)
    bpy.context.scene.collection.objects.link(pivot)
    for o in roots:
        o.parent = pivot
        o.matrix_parent_inverse = pivot.matrix_world.inverted()
    return pivot, s * dims.z


def _action_fcurves(ad):
    """F-curves de un animation_data, TOLERANTE entre versiones de Blender.

    <=4.3: `action.fcurves` (modelo legacy). >=4.4 (slotted actions, lo que corre
    Blender 5.1): `action.fcurves` YA NO EXISTE; las curvas viven en el channelbag
    del slot, dentro de layers->strips. Best-effort por-strip: si la API no calza,
    devuelve lo que pudo y el ease se apoya en el default de fabrica (ya BEZIER /
    AUTO_CLAMPED), sin reventar el render."""
    action = getattr(ad, "action", None)
    if action is None:
        return []
    legacy = getattr(action, "fcurves", None)
    if legacy is not None:
        return list(legacy)
    out = []
    slot = getattr(ad, "action_slot", None)
    for layer in getattr(action, "layers", []):
        for strip in getattr(layer, "strips", []):
            cb = None
            if slot is not None and hasattr(strip, "channelbag"):
                try:
                    cb = strip.channelbag(slot)
                except Exception:
                    cb = None
            if cb is not None:
                out.extend(cb.fcurves)
                continue
            for c in getattr(strip, "channelbags", []):  # fallback
                try:
                    out.extend(c.fcurves)
                except Exception:
                    pass
    return out


def _ease(holder):
    """Suaviza (bezier auto) las curvas de animacion de un objeto/dato -> el
    camera move arranca y asienta sin tirones (look cinematografico)."""
    ad = getattr(holder, "animation_data", None)
    if not ad or not ad.action:
        return
    for fc in _action_fcurves(ad):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = "AUTO_CLAMPED"
            kp.handle_right_type = "AUTO_CLAMPED"


def swing(pivot, frames, a0=-0.42, a1=0.34):
    """Giro lento de presentacion (no un turntable completo): el hero se mece de
    a0 a a1 rad alrededor de su eje vertical."""
    pivot.rotation_euler.z = a0
    pivot.keyframe_insert("rotation_euler", index=2, frame=1)
    pivot.rotation_euler.z = a1
    pivot.keyframe_insert("rotation_euler", index=2, frame=frames)
    _ease(pivot)


def camera_move(cam, look, frames, push=0.14):
    """Push-in suave hacia el hero: la camara avanza `push` del trayecto a `look`
    y el foco DoF lo acompaña para que el plano final quede nitido."""
    look_v = mathutils.Vector(look)
    far = cam.location.copy()
    near = far.lerp(look_v, push)
    cam.location = far
    cam.keyframe_insert("location", frame=1)
    cam.location = near
    cam.keyframe_insert("location", frame=frames)
    cam.data.dof.focus_distance = (far - look_v).length
    cam.data.dof.keyframe_insert("focus_distance", frame=1)
    cam.data.dof.focus_distance = (near - look_v).length
    cam.data.dof.keyframe_insert("focus_distance", frame=frames)
    _ease(cam)
    _ease(cam.data)


# ----------------------------------------------------------------------- main
def _args():
    a = sys.argv
    args = a[a.index("--") + 1:] if "--" in a else []

    def g(name, d=None):
        return args[args.index(name) + 1] if name in args else d

    return {
        "asset": g("--asset"),               # id en hero_assets.json (None -> procedural)
        "proc": g("--proc", "coins"),         # forma procedural: coins|ingot
        "material": g("--material", "keep"),  # keep|gold|silver|teal|gold-glow|green
        "frames": int(g("--frames", FRAMES)),
        "size": float(g("--size", "3.2")),
        "hdri": g("--hdri"),                  # ruta a .hdr/.exr CC0 (None -> gradiente procedural)
        "env": float(g("--env", "0.7")),      # fuerza del entorno HDRI (reflejos); <1 = key domina -> drama
        "lens": float(g("--lens", "70")),     # focal (mm); largo = product/tele
        "fill": float(g("--fill", "0.92")),   # fraccion del cuadro que ocupa el hero (margen)
    }


def main():
    opt = _args()
    frames = opt["frames"]

    scene = sp.fresh_scene()
    sp.setup_render(scene, res=1080, samples=180, fps=30, motion_blur=True)

    hdri = opt["hdri"]
    if hdri and not os.path.isabs(hdri):
        hdri = os.path.join(HERE, hdri)
    if hdri and not os.path.exists(hdri):
        raise SystemExit(f"hero_shot: HDRI no existe: {hdri}")
    sp.world_studio(scene, hdri_path=hdri, strength=opt["env"])
    out_dir, prefix = sp.parse_out_arg("out_hero", "hero_")
    sp.set_output(scene, out_dir, prefix, frame_start=1, frame_end=frames)

    path, entry = resolve_asset(opt["asset"])
    if path:
        objs = import_model(path)
        print(f"[hero] modelo = {entry['id']} ({entry.get('licencia')}, {os.path.basename(path)})")
    else:
        shape = opt["proc"] if entry is None else "ingot"
        objs = _procedural_coin_stack() if shape == "coins" else _procedural_hero()
        tag = entry["id"] if entry else f"procedural {shape} $0"
        print(f"[hero] {tag} -> sin descarga")

    _override_material(objs, opt["material"])
    pivot, height = frame_objects(objs, target_size=opt["size"])

    # ENCUADRE robusto p/cualquier forma: distancia de camara desde la esfera
    # envolvente + el FOV de la lente, apuntando a una fraccion `fill` del cuadro
    # (margen). Antes la distancia era fija (size*1.85) y recortaba las formas
    # no-disco (la barra ancha llenaba el cuadro). La esfera tambien cubre el
    # swing -> el hero no se sale al rotar.
    meshes = [o for o in objs if o.type == "MESH"]
    mn, mx = _bbox_world(meshes)
    center = (mn + mx) / 2.0
    radius = (mx - center).length or 1.0
    half_fov = math.atan((36.0 * 0.5) / opt["lens"])  # sensor default 36mm
    dist = radius / max(0.05, opt["fill"] * math.tan(half_fov))

    look = (0.0, 0.0, center.z)
    cam = sp.add_camera(scene, location=(0.0, -dist, center.z + radius * 0.3),
                        look_at=look, lens=opt["lens"], dof=True, fstop=2.8)
    # luz dramatica: key fuerte + fill bajo + HDRI a 0.7 -> contraste direccional
    # (el HDRI solo, a 1.0, lavaba el metal a 'catalogo plano'). El rim separa del fondo.
    sp.studio_lights(scene, target_loc=look, key=2600, rim=1000, fill=140)

    # swing SUTIL: la composicion (hero + stack + spills) solo "cierra" en su
    # orientacion disenada; un giro grande la rompe (encimaria el hero al stack).
    # ~7 grados de deriva + push-in + motion blur = vida, sin perder el layout.
    swing(pivot, frames, a0=-0.14, a1=-0.02)
    camera_move(cam, look, frames)

    sp.render(scene, animation=True)


if __name__ == "__main__":
    main()
