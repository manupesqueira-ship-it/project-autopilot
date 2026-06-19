"""
Napkin hero set-piece: servilleta foto-real escrita a mano (regla del 72),
luz de estudio, DoF, motion blur, camara zoom-push. Render OptiX (RTX 4060).

Este es el PRIMER set-piece del catalogo y ademas fija el template premium (#60):
HDRI/estudio + DoF + motion blur + PBR + tipografia. Reusa el patron probado de
coin_hero.py (engine/GPU/denoise/output).

Uso:
  blender --background --python napkin_hero.py -- still           # 1 frame look-test
  blender --background --python napkin_hero.py -- still 1080 160  # still HD
  blender --background --python napkin_hero.py -- anim            # secuencia + zoom-push

Salida: ./out_napkin/napkin_#####.png
El texto escrito es PLACEHOLDER hasta que Manuel confirme la formula y el estilo.
La animacion de write-on (la mano escribiendo) se agrega DESPUES del OK del look.
"""
import bpy, math, os, sys

# ---------- args (despues de "--") ----------
argv = sys.argv
uargs = argv[argv.index("--") + 1:] if "--" in argv else []
MODE = (uargs[0] if len(uargs) > 0 else "still").lower()
if MODE == "still":
    RES_X, RES_Y = (int(uargs[1]) if len(uargs) > 1 else 540), 0
    SAMPLES = int(uargs[2]) if len(uargs) > 2 else 48
else:
    RES_X = int(uargs[1]) if len(uargs) > 1 else 1080
    SAMPLES = int(uargs[2]) if len(uargs) > 2 else 160
# vertical 9:16
if RES_X == 540:
    RES_X, RES_Y = 540, 960
else:
    RES_X, RES_Y = RES_X, int(RES_X * 16 / 9)
FRAMES = 150  # ~5s @30fps (solo anim)
LAYOUT = os.environ.get("NAPKIN_LAYOUT", "inline").lower()  # inline | fraction

OUT_DIR = os.path.join(os.path.dirname(bpy.data.filepath) or os.getcwd(), "out_napkin")
os.makedirs(OUT_DIR, exist_ok=True)

INK_FONT = r"C:\Windows\Fonts\Inkfree.ttf"   # handwriting que ya trae Windows ($0)

# ---------- reset escena ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- render engine + GPU OptiX (patron coin_hero) ----------
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
    except Exception as e:
        print("device try", dev_type, "failed:", e)
scene.cycles.device = "GPU" if chosen != "NONE" else "CPU"
print(f"[blender] compute device = {chosen} ({scene.cycles.device})")

scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
try:
    scene.cycles.denoiser = "OPTIX"
except Exception:
    pass

# ---------- output ----------
scene.render.resolution_x = RES_X
scene.render.resolution_y = RES_Y
scene.render.resolution_percentage = 100
scene.render.film_transparent = False  # escena completa (mesa + servilleta)
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 15
# look filmico (premium): view transform + leve contraste
try:
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
except Exception as e:
    print("view transform set failed:", e)
# motion blur (para el zoom-push)
scene.render.use_motion_blur = True
try:
    scene.render.motion_blur_shutter = 0.5
except Exception:
    pass

if MODE == "still":
    scene.frame_start = scene.frame_end = 1
else:
    scene.frame_start = 1
    scene.frame_end = FRAMES
scene.render.filepath = os.path.join(OUT_DIR, "napkin_")


# ---------- helpers ----------
def set_in(bsdf, name, value):
    if name in bsdf.inputs:
        bsdf.inputs[name].default_value = value
        return True
    return False


def new_principled(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    return m, b


# ---------- world (ambiente oscuro calido, no negro puro) ----------
world = bpy.data.worlds.new("NapkinWorld")
scene.world = world
world.use_nodes = True
wnt = world.node_tree
bgn = wnt.nodes.get("Background")
if bgn:
    bgn.inputs["Color"].default_value = (0.02, 0.022, 0.03, 1.0)
    bgn.inputs["Strength"].default_value = 0.35

# ---------- materiales ----------
# papel: blanco roto, muy rugoso, leve subsurface (translucidez del papel)
paper, pb = new_principled("Paper")
set_in(pb, "Base Color", (0.855, 0.84, 0.805, 1.0))
set_in(pb, "Roughness", 0.86)
set_in(pb, "Specular IOR Level", 0.35)
set_in(pb, "Sheen Weight", 0.25)
set_in(pb, "Subsurface Weight", 0.12)
set_in(pb, "Subsurface Radius", (1.2, 1.0, 0.8))
set_in(pb, "Subsurface Scale", 0.05)
# bump fino de fibra de papel
pt = paper.node_tree
ntex = pt.nodes.new("ShaderNodeTexNoise")
ntex.inputs["Scale"].default_value = 320.0
ntex.inputs["Detail"].default_value = 6.0
bump = pt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.10
pt.links.new(ntex.outputs["Fac"], bump.inputs["Height"])
pt.links.new(bump.outputs["Normal"], pb.inputs["Normal"])

# mesa: oscura, casi mate con leve reflejo premium
table, tb = new_principled("Table")
set_in(tb, "Base Color", (0.018, 0.022, 0.028, 1.0))
set_in(tb, "Roughness", 0.42)
set_in(tb, "Specular IOR Level", 0.5)

# tinta: marcador casi negro, leve sheen de boligrafo
ink, ib = new_principled("Ink")
set_in(ib, "Base Color", (0.015, 0.015, 0.022, 1.0))
set_in(ib, "Roughness", 0.55)
set_in(ib, "Metallic", 0.0)

# ---------- mesa ----------
bpy.ops.mesh.primitive_plane_add(size=24, location=(0, 0, 0))
tbl = bpy.context.active_object
tbl.name = "Table"
tbl.data.materials.append(table)

# ---------- servilleta (grid = silueta CUADRADA, no oval) ----------
bpy.ops.mesh.primitive_grid_add(x_subdivisions=140, y_subdivisions=140,
                                size=2.0, location=(0, 0, 0.012))
nap = bpy.context.active_object
nap.name = "Napkin"
nap.scale = (1.5, 1.5, 1.0)
nap.rotation_euler = (0, 0, math.radians(-4))  # leve giro natural
# ondulacion MUY suave (papel casi plano, sin crateres)
wtex = bpy.data.textures.new("Wrinkle", "CLOUDS")
wtex.noise_scale = 1.1
disp = nap.modifiers.new("Wrinkle", "DISPLACE")
disp.texture = wtex
disp.strength = 0.013
disp.mid_level = 0.5
wtex2 = bpy.data.textures.new("Fold", "CLOUDS")
wtex2.noise_scale = 2.6
disp2 = nap.modifiers.new("Fold", "DISPLACE")
disp2.texture = wtex2
disp2.strength = 0.008
disp2.mid_level = 0.5
sol = nap.modifiers.new("Thick", "SOLIDIFY")   # grosor de papel -> el borde lee
sol.thickness = 0.014
bev = nap.modifiers.new("Edge", "BEVEL")        # borde suave
bev.width = 0.006
bev.segments = 2
bpy.ops.object.shade_smooth()
nap.data.materials.append(paper)


# ---------- texto manuscrito ----------
def write(body, size, y, name, z=0.075, x=0.0):
    bpy.ops.object.text_add(location=(x, y, z))
    t = bpy.context.active_object
    t.name = name
    t.data.body = body
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.size = size
    t.data.extrude = 0.004
    try:
        f = bpy.data.fonts.load(INK_FONT)
        t.data.font = f
    except Exception as e:
        print("font load failed:", e)
    bpy.ops.object.convert(target="MESH")
    t.data.materials.append(ink)
    return t


def bar(x, y, half_w, name, z=0.075, half_h=0.011, half_t=0.006):
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
    o = bpy.context.active_object
    o.name = name
    o.scale = (half_w, half_h, half_t)
    o.data.materials.append(ink)
    return o


# PLACEHOLDER — confirmar con Manuel la formula/estilo/layout
if LAYOUT == "fraction":
    write("La regla del 72", 0.20, 0.74, "Heading")
    write("72", 0.42, 0.26, "FracNum", x=-0.55)
    bar(-0.55, 0.02, 0.40, "FracBar")
    write("%", 0.40, -0.24, "FracDen", x=-0.55)
    write("= años", 0.34, 0.00, "RHS", x=0.62)
else:
    write("La regla del 72", 0.22, 0.66, "Heading")
    write("72 ÷ % = años", 0.34, 0.04, "Formula")

# ---------- luces de estudio (suaves, papel pide menos energia que metal) ----------
bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0.05))
target = bpy.context.active_object
target.name = "Target"


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


area("Key",  (2.4, -1.2, 3.6), 4.0, 480, (1.0, 0.95, 0.86))
area("Rim",  (-1.9, 1.7, 2.8), 3.0, 360, (0.70, 0.82, 1.0))
area("Fill", (0.0, -3.2, 1.5), 6.0, 190, (1.0, 0.98, 0.95))
area("Top",  (0.0, 0.2, 4.8), 4.0, 110, (1, 1, 1))

# ---------- camara (picada leve, DoF en la escritura) ----------
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 50
cam_data.dof.use_dof = True
cam_data.dof.focus_object = (bpy.data.objects.get("Formula")
                             or bpy.data.objects.get("FracNum"))
cam_data.dof.aperture_fstop = 2.8
cam = bpy.data.objects.new("Cam", cam_data)
cam.location = (0.0, -2.6, 5.6)
scene.collection.objects.link(cam)
scene.camera = cam
cc = cam.constraints.new("TRACK_TO")
cc.target = target
cc.track_axis = "TRACK_NEGATIVE_Z"
cc.up_axis = "UP_Y"

# ---------- animacion (solo anim): zoom-push al final ----------
if MODE != "still":
    hold_end = FRAMES - 26
    cam.location = (0.0, -2.6, 5.6)
    cam.keyframe_insert("location", frame=1)
    cam.keyframe_insert("location", frame=hold_end)
    cam.location = (0.0, -2.0, 4.7)  # push hacia la servilleta
    cam.keyframe_insert("location", frame=FRAMES)

# ---------- render ----------
print(f"[blender] MODE={MODE} {RES_X}x{RES_Y} samples={SAMPLES} -> {OUT_DIR}")
bpy.ops.render.render(animation=(MODE != "still"), write_still=(MODE == "still"))
print("[blender] DONE")
