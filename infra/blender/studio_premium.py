# -*- coding: utf-8 -*-
"""
studio_premium.py  --  Template de LOOK premium para Blender (Dinero IA, Track A3).

UNA fuente de verdad para el acabado 3D que HEREDA cada beat 3D (moneda hero,
hero-shots B3, graficas 3D A4): HDRI + DoF + motion blur + PBR + tipografia 3D
EXTRUIDA con bisel. Antes cada script (coin_hero.py) cableaba a mano el engine,
las luces y los materiales -> look inconsistente, imposible de subir en bloque.
Aqui el acabado queda en un solo lugar y se afina una vez.

NO renderiza nada por si mismo: es una libreria de helpers. Un script de escena
hace `import studio_premium as sp`, arma sus objetos y llama `sp.render(scene)`.
Salida = secuencia PNG RGBA transparente (mismo contrato que coin_hero.py), que
`encode_host.py` vuelve WebM VP9 yuva420p para componer en Remotion.

Convenciones heredadas de coin_hero.py:
  - engine CYCLES, GPU OptiX (fallback CUDA -> CPU), denoiser OptiX,
  - `film_transparent = True`, PNG RGBA -> se posiciona libre en Remotion,
  - cuadrado por defecto (1080) para no atarse a un encuadre.

HDRI $0: si no hay archivo .hdr/.exr a la mano, `world_studio()` arma un
"HDRI procedural" de estudio (gradiente + halo de softbox en nodos) -> reflejos
premium SIN descargar nada. Cuando Manuel tenga un HDRI CC0 (Poly Haven, B3)
basta pasar su ruta: world_studio(scene, hdri_path=".../studio.hdr").

Uso tipico (en un script de escena, corrido con
  blender --background --python escena.py -- --out out_x):

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import studio_premium as sp

    scene = sp.fresh_scene()
    sp.setup_render(scene, res=1080, samples=160, motion_blur=True)
    sp.world_studio(scene)                       # HDRI procedural (o hdri_path=...)
    sp.set_output(scene, "out_x", "frame_")
    mat = sp.pbr_metal("Gold", (0.95, 0.72, 0.26, 1), rough=0.22)
    sp.extruded_text("$209M", size=1.2, material=mat)
    sp.add_camera(scene, (0, -5.2, 1.4), look_at=(0, 0, 0.4), fstop=2.8)
    sp.studio_lights(scene)
    sp.render(scene)
"""
import math
import os

import bpy  # noqa: E402  (solo existe dentro de Blender; py_compile no lo ejecuta)


# ------------------------------------------------------------------ escena base
def fresh_scene():
    """Escena vacia y limpia (como coin_hero: read_factory_settings empty)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


# ----------------------------------------------------------------------- GPU
def setup_gpu(scene):
    """Selecciona OptiX (RTX 4060) -> CUDA -> CPU. Devuelve el tipo elegido."""
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    chosen = "NONE"
    for dev_type in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = dev_type
            prefs.get_devices()
            gpu_found = False
            for d in prefs.devices:
                d.use = (d.type == dev_type)
                if d.type == dev_type:
                    gpu_found = True
            if gpu_found:
                chosen = dev_type
                break
        except Exception as e:  # pragma: no cover (depende del host)
            print("device try", dev_type, "failed:", e)
    scene.cycles.device = "GPU" if chosen != "NONE" else "CPU"
    print(f"[studio] compute device = {chosen} ({scene.cycles.device})")
    return chosen


# --------------------------------------------------------------------- render
def setup_render(scene, res=1080, res_y=None, samples=160, fps=30,
                 transparent=True, motion_blur=True, shutter=0.5):
    """Engine + GPU + muestras + denoise + salida transparente + motion blur.

    `motion_blur` da el rastro cinematografico a lo que se mueve (lo que separa
    el look 'premium' del 'render duro'); el shutter 0.5 = medio cuadro (default
    cine). `transparent` = film alpha para componer en Remotion.
    """
    setup_gpu(scene)
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = "OPTIX"
    except Exception:
        pass

    scene.render.resolution_x = res
    scene.render.resolution_y = res_y or res
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.render.film_transparent = bool(transparent)

    img = scene.render.image_settings
    img.file_format = "PNG"
    img.color_mode = "RGBA"
    img.compression = 15

    # motion blur (Cycles): el rastro cinematografico de lo que se mueve.
    scene.render.use_motion_blur = bool(motion_blur)
    try:
        scene.render.motion_blur_shutter = shutter
        scene.cycles.motion_blur_position = "CENTER"
    except Exception:
        pass

    # filmico AgX (Blender 4+) para highlights premium que no se queman.
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    return scene


def set_output(scene, out_dir, prefix="frame_", frame_start=1, frame_end=60):
    """Ruta de salida = <dir-del-.blend o cwd>/<out_dir>/<prefix>#####.png."""
    base = os.path.dirname(bpy.data.filepath) or os.getcwd()
    full = os.path.join(base, out_dir)
    os.makedirs(full, exist_ok=True)
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    scene.render.filepath = os.path.join(full, prefix)
    return full


# ----------------------------------------------------------------------- world
def world_studio(scene, hdri_path=None, strength=1.0, tint=None):
    """Iluminacion de entorno (reflejos premium). Con HDRI real si se pasa una
    ruta valida; si no, un 'HDRI procedural' de estudio (gradiente + halo de
    softbox) -> $0, sin descargar nada.
    """
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)

    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg.inputs["Strength"].default_value = strength

    if hdri_path and os.path.exists(hdri_path):
        env = nt.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(hdri_path)
        nt.links.new(env.outputs["Color"], bg.inputs["Color"])
        print(f"[studio] HDRI = {os.path.basename(hdri_path)}")
    else:
        # HDRI PROCEDURAL: gradiente vertical de estudio + tinte opcional.
        texco = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeMapping")
        grad = nt.nodes.new("ShaderNodeTexGradient")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        lo = (0.035, 0.045, 0.062, 1.0)
        hi = (0.22, 0.26, 0.32, 1.0) if tint is None else tint
        ramp.color_ramp.elements[0].color = lo
        ramp.color_ramp.elements[1].color = hi
        mapping.inputs["Rotation"].default_value = (math.radians(90), 0, 0)
        nt.links.new(texco.outputs["Generated"], mapping.inputs["Vector"])
        nt.links.new(mapping.outputs["Vector"], grad.inputs["Vector"])
        nt.links.new(grad.outputs["Color"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
        print("[studio] HDRI procedural (sin archivo .hdr)")

    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return world


# -------------------------------------------------------------------- materiales
def _principled(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes.get("Principled BSDF")


def _set(bsdf, key, value):
    """Asigna un input del Principled si existe (tolera cambios de version)."""
    if key in bsdf.inputs:
        bsdf.inputs[key].default_value = value


def pbr_metal(name, color, rough=0.24, coat=0.4, anisotropy=0.0):
    """Metal PBR (oro/plata): Metallic=1, clearcoat para brillo premium."""
    m, b = _principled(name)
    _set(b, "Base Color", color)
    _set(b, "Metallic", 1.0)
    _set(b, "Roughness", rough)
    _set(b, "Anisotropic", anisotropy)
    for cn in ("Coat Weight", "Clearcoat"):
        _set(b, cn, coat)
    return m


def pbr_plastic(name, color, rough=0.35, coat=0.3):
    """Plastico/ceramica PBR (no metalico) con clearcoat suave."""
    m, b = _principled(name)
    _set(b, "Base Color", color)
    _set(b, "Metallic", 0.0)
    _set(b, "Roughness", rough)
    for cn in ("Coat Weight", "Clearcoat"):
        _set(b, cn, coat)
    return m


def pbr_emission(name, color, strength=6.0):
    """Material EMISIVO (acentos que brillan: verde marca, dorado dinero)."""
    m, b = _principled(name)
    _set(b, "Base Color", color)
    for en in ("Emission Color", "Emission"):
        _set(b, en, color)
    _set(b, "Emission Strength", strength)
    return m


# ------------------------------------------------------ tipografia 3D extruida
def extruded_text(body, size=1.0, extrude=0.08, bevel=0.012, bevel_res=3,
                  material=None, location=(0, 0, 0), rotation=(0, 0, 0),
                  align=("CENTER", "CENTER"), parent=None, name="Text3D",
                  to_mesh=True):
    """Texto 3D EXTRUIDO con bisel (la 'tipografia 3D extruida' del plan A3).

    El bisel redondea el canto -> atrapa un highlight fino = look premium (no el
    canto plano del extrude crudo). Devuelve el objeto. `material` PBR opcional.
    """
    bpy.ops.object.text_add(location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    d = obj.data
    d.body = body
    d.align_x, d.align_y = align
    d.size = size
    d.extrude = extrude
    d.bevel_depth = bevel
    d.bevel_resolution = bevel_res
    if to_mesh:
        bpy.ops.object.convert(target="MESH")
        bpy.ops.object.shade_smooth()
    if material is not None:
        obj.data.materials.append(material)
    if parent is not None:
        obj.parent = parent
    return obj


# ----------------------------------------------------------------------- camara
def add_camera(scene, location, look_at=(0, 0, 0), lens=80, dof=True,
               fstop=3.2, focus_distance=None):
    """Camara con DoF. Apunta a `look_at` via TRACK_TO; enfoca a esa distancia
    (o `focus_distance` si se pasa). DoF = el desenfoque que separa el sujeto
    del fondo (profundidad cinematografica).
    """
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = lens
    cam_data.dof.use_dof = bool(dof)

    target = bpy.data.objects.new("CamTarget", None)
    target.location = look_at
    scene.collection.objects.link(target)

    cam = bpy.data.objects.new("Cam", cam_data)
    cam.location = location
    scene.collection.objects.link(cam)
    c = cam.constraints.new("TRACK_TO")
    c.target = target
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"

    if dof:
        if focus_distance is None:
            lx, ly, lz = location
            tx, ty, tz = look_at
            focus_distance = math.sqrt((lx - tx) ** 2 + (ly - ty) ** 2 + (lz - tz) ** 2)
        cam_data.dof.focus_distance = focus_distance
        cam_data.dof.aperture_fstop = fstop

    scene.camera = cam
    return cam


# ------------------------------------------------------------------- luces rig
def studio_lights(scene, target_loc=(0, 0, 0), key=1300, rim=750, fill=320):
    """3-point + rim que complementa al HDRI con speculars crujientes. Las luces
    apuntan al target con TRACK_TO. Devuelve el empty 'LightRig' (parentea las
    moviles para un barrido de brillo si se anima su rotacion).
    """
    target = bpy.data.objects.new("LightTarget", None)
    target.location = target_loc
    scene.collection.objects.link(target)

    def area(name, loc, size, power, color=(1, 1, 1)):
        ld = bpy.data.lights.new(name, "AREA")
        ld.shape = "RECTANGLE"
        ld.size = size
        ld.size_y = size * 0.7
        ld.energy = power
        ld.color = color
        o = bpy.data.objects.new(name, ld)
        o.location = loc
        scene.collection.objects.link(o)
        c = o.constraints.new("TRACK_TO")
        c.target = target
        c.track_axis = "TRACK_NEGATIVE_Z"
        c.up_axis = "UP_Y"
        return o

    rig = bpy.data.objects.new("LightRig", None)
    scene.collection.objects.link(rig)
    k = area("Key", (3.0, -2.4, 3.4), 5, key, (1.0, 0.96, 0.88))
    k.parent = rig
    r = area("Rim", (-2.8, 1.2, 2.8), 4, rim, (0.68, 0.84, 1.0))
    r.parent = rig
    area("Fill", (0.0, -3.8, 1.4), 6, fill, (1, 1, 1))
    return rig


# --------------------------------------------------------------------- render
def render(scene, animation=True):
    """Lanza el render (secuencia si animation=True). Igual contrato que coin_hero."""
    n = scene.frame_end - scene.frame_start + 1
    print(f"[studio] rendering {n} frames @ "
          f"{scene.render.resolution_x}x{scene.render.resolution_y} -> "
          f"{scene.render.filepath}")
    bpy.ops.render.render(animation=animation)
    print("[studio] DONE")


# ------------------------------------------------------------------------ CLI
def parse_out_arg(default_dir, default_prefix):
    """Lee `-- --out <dir> --prefix <p>` de argv (Blender pasa lo de tras '--')."""
    import sys
    argv = sys.argv
    args = argv[argv.index("--") + 1:] if "--" in argv else []
    out_dir = default_dir
    prefix = default_prefix
    if "--out" in args:
        out_dir = args[args.index("--out") + 1]
    if "--prefix" in args:
        prefix = args[args.index("--prefix") + 1]
    return out_dir, prefix
