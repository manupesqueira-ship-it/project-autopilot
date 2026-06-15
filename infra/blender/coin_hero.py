"""
Hero 3D procedural: moneda peso glossy, luz de estudio, alpha, render OptiX (RTX 4060).
Uso:
  blender --background --python coin_hero.py
Salida: ./out/coin_#####.png (RGBA, fondo transparente), 60 frames, loop 360.
"""
import bpy, math, os, sys

# ---------- config ----------
OUT_DIR   = os.path.join(os.path.dirname(bpy.data.filepath) or os.getcwd(), "out")
FRAMES    = 60          # loop completo (2s @30fps)
RES       = 1080        # cuadrado, alpha -> se posiciona libre en Remotion
SAMPLES   = 160
GOLD      = (0.95, 0.72, 0.26, 1.0)
EMBOSS    = "$"         # relieve en la cara

os.makedirs(OUT_DIR, exist_ok=True)

# ---------- reset escena ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- render engine + GPU OptiX ----------
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
scene.render.resolution_x = RES
scene.render.resolution_y = RES
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.compression = 15
scene.frame_start = 1
scene.frame_end = FRAMES
scene.render.filepath = os.path.join(OUT_DIR, "coin_")

# ---------- world (gradiente de estudio para reflejos) ----------
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.use_nodes = True
wnt = world.node_tree
for n in list(wnt.nodes):
    wnt.nodes.remove(n)
bg = wnt.nodes.new("ShaderNodeBackground")
grad = wnt.nodes.new("ShaderNodeTexGradient")
mapping = wnt.nodes.new("ShaderNodeMapping")
texco = wnt.nodes.new("ShaderNodeTexCoord")
ramp = wnt.nodes.new("ShaderNodeValToRGB")
wout = wnt.nodes.new("ShaderNodeOutputWorld")
ramp.color_ramp.elements[0].color = (0.04, 0.05, 0.07, 1)
ramp.color_ramp.elements[1].color = (0.24, 0.28, 0.34, 1)
mapping.inputs["Rotation"].default_value = (math.radians(90), 0, 0)
wnt.links.new(texco.outputs["Generated"], mapping.inputs["Vector"])
wnt.links.new(mapping.outputs["Vector"], grad.inputs["Vector"])
wnt.links.new(grad.outputs["Color"], ramp.inputs["Fac"])
wnt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.0
wnt.links.new(bg.outputs["Background"], wout.inputs["Surface"])

# ---------- materiales ----------
def gold_mat(name, rough=0.24, coat=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = GOLD
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = rough
    for cn in ("Coat Weight", "Clearcoat"):
        if cn in b.inputs:
            b.inputs[cn].default_value = coat
    return m

def dark_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.06, 0.045, 0.02, 1)
    b.inputs["Metallic"].default_value = 0.7
    b.inputs["Roughness"].default_value = 0.55
    return m

# ---------- moneda ----------
bpy.ops.mesh.primitive_cylinder_add(vertices=192, radius=1.0, depth=0.14, location=(0,0,0))
coin = bpy.context.active_object
coin.name = "Coin"
bev = coin.modifiers.new("Bevel", "BEVEL")
bev.width = 0.03
bev.segments = 8
bpy.ops.object.shade_smooth()
try:
    coin.data.use_auto_smooth = True
    coin.data.auto_smooth_angle = math.radians(40)
except Exception:
    pass
coin.data.materials.append(gold_mat("GoldCoin"))

# anillo de borde elevado (detalle de moneda)
bpy.ops.mesh.primitive_torus_add(location=(0, 0, 0.072),
    major_radius=0.86, minor_radius=0.025, major_segments=192, minor_segments=12)
ring = bpy.context.active_object
ring.name = "Ring"
ring.scale = (1, 1, 0.5)
bpy.ops.object.shade_smooth()
ring.data.materials.append(gold_mat("GoldRing", rough=0.16))
ring.parent = coin

# relieve "$" en la cara (oscuro, contrastado, anclado a la moneda)
bpy.ops.object.text_add(location=(0, 0, 0.06))
txt = bpy.context.active_object
txt.data.body = EMBOSS
txt.data.align_x = "CENTER"
txt.data.align_y = "CENTER"
txt.data.extrude = 0.03
txt.data.size = 1.05
bpy.ops.object.convert(target="MESH")
txt.data.materials.append(dark_mat("EmbossDark"))
txt.parent = coin

# ---------- softboxes con Track-To al centro ----------
bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
target = bpy.context.active_object
target.name = "Target"

def area(name, loc, size, power, color=(1,1,1)):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = "RECTANGLE"
    ld.size = size; ld.size_y = size * 0.7
    ld.energy = power
    ld.color = color
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    scene.collection.objects.link(o)
    c = o.constraints.new("TRACK_TO")
    c.target = target; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    return o

# rig que orbita -> barrido de brillo (highlight sweep) sobre el metal
rig = bpy.data.objects.new("LightRig", None)
scene.collection.objects.link(rig)
key = area("Key", (2.8, -0.4, 3.2), 5, 1300, (1.0, 0.96, 0.88)); key.parent = rig
rim = area("Rim", (-2.6, 0.8, 2.6), 4, 750, (0.68, 0.84, 1.0)); rim.parent = rig
# luces base estáticas (relleno parejo)
area("Top",  (0.0, 0.0, 4.6), 4.5, 520, (1, 1, 1))
area("Fill", (0.0, -3.6, 1.4), 6, 300, (1, 1, 1))

# ---------- cámara (casi cenital, ligero tilt para dimensión) ----------
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 80
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 6.7
cam_data.dof.aperture_fstop = 3.4
cam = bpy.data.objects.new("Cam", cam_data)
cam.location = (0, -1.4, 6.6)
cam.rotation_euler = (math.radians(12), 0, 0)
scene.collection.objects.link(cam)
scene.camera = cam

# ---------- animación: highlight sweep (luz orbita), moneda fija ----------
try:
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
except Exception as e:
    print("interp pref failed:", e)
rig.rotation_mode = "XYZ"
rig.rotation_euler = (0, 0, 0)
rig.keyframe_insert("rotation_euler", frame=1)
rig.rotation_euler = (0, 0, math.radians(360))
rig.keyframe_insert("rotation_euler", frame=FRAMES + 1)

# ---------- render ----------
print(f"[blender] rendering {FRAMES} frames @ {RES}x{RES} -> {OUT_DIR}")
bpy.ops.render.render(animation=True)
print("[blender] DONE")
