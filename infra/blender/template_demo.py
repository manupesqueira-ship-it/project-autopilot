# -*- coding: utf-8 -*-
"""
template_demo.py  --  Escena de VALIDACION del look premium (Track A3).

Ejercita LAS CINCO piezas del template a la vez sobre una capacidad NUEVA (no la
moneda ya vista): un NUMERO HERO 3D EXTRUIDO ("$209M") en oro pulido, flotando
con motion blur, DoF que lo separa del fondo, e iluminacion HDRI de estudio.

Esta es la toma que se bate en el LOTE FINAL (R1) para tunear luz/DoF/bloom al
ojo de Manuel. NO se renderiza ahora; este archivo solo se ESCRIBE.

Render (en el lote final, NO ahora):
    cd infra/blender
    blender --background --python template_demo.py -- --out out_demo --prefix demo_
    python encode_host.py            # (ajustar glob a demo_*.png -> webm alpha)

Salida: out_demo/demo_#####.png (RGBA transparente, 60 frames @30fps).
"""
import math
import os
import sys

import bpy  # noqa: E402  (solo existe dentro de Blender)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import studio_premium as sp  # noqa: E402

# --- HDRI opcional: si dejas un .hdr/.exr CC0 (Poly Haven) aqui, se usa solo ---
HDRI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hdri", "studio.hdr")
FRAMES = 60          # 2s @30fps
HERO = "$209M"       # numero hero (placeholder de demo; en pipeline = dato del brief)

scene = sp.fresh_scene()
sp.setup_render(scene, res=1080, samples=180, fps=30, motion_blur=True, shutter=0.5)
sp.world_studio(scene, hdri_path=HDRI if os.path.exists(HDRI) else None, strength=1.0)
out_dir, prefix = sp.parse_out_arg("out_demo", "demo_")
sp.set_output(scene, out_dir, prefix, frame_start=1, frame_end=FRAMES)

# --- numero hero 3D extruido (oro = dinero en la paleta) ---
gold = sp.pbr_metal("HeroGold", (0.95, 0.72, 0.26, 1.0), rough=0.20, coat=0.5)
hero = sp.extruded_text(HERO, size=1.35, extrude=0.12, bevel=0.018, bevel_res=4,
                        material=gold, location=(0, 0, 0.0),
                        rotation=(math.radians(90), 0, 0))  # de pie, encarando la camara

# piso reflectante (da bounce-light y un reflejo tenue del numero -> profundidad)
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -1.15))
floor = bpy.context.active_object
floor.data.materials.append(sp.pbr_plastic("Floor", (0.02, 0.025, 0.03, 1.0),
                                           rough=0.10, coat=0.6))  # piso reflectante

# --- camara con DoF (enfoca el numero, fondo suave) ---
sp.add_camera(scene, location=(0, -5.4, 1.1), look_at=(0, 0, 0.2), lens=85,
              dof=True, fstop=2.6)

# --- luces: HDRI + rig 3-point con barrido de brillo ---
rig = sp.studio_lights(scene, target_loc=(0, 0, 0.2))

# --- animacion sutil (premium, NO bouncy): el numero mece y el rig orbita ->
#     el motion blur tiene de que agarrarse y el metal barre un highlight ---
try:
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "BEZIER"
except Exception as e:
    print("interp pref:", e)

hero.rotation_mode = "XYZ"
hero.keyframe_insert("rotation_euler", frame=1)
hero.rotation_euler = (math.radians(90), 0, math.radians(10))
hero.keyframe_insert("rotation_euler", frame=FRAMES // 2)
hero.rotation_euler = (math.radians(90), 0, math.radians(-10))
hero.keyframe_insert("rotation_euler", frame=FRAMES)

base_z = hero.location.z
hero.keyframe_insert("location", frame=1)
hero.location.z = base_z + 0.12
hero.keyframe_insert("location", frame=FRAMES // 2)
hero.location.z = base_z
hero.keyframe_insert("location", frame=FRAMES)

rig.rotation_mode = "XYZ"
rig.rotation_euler = (0, 0, 0)
rig.keyframe_insert("rotation_euler", frame=1)
rig.rotation_euler = (0, 0, math.radians(40))
rig.keyframe_insert("rotation_euler", frame=FRAMES)

sp.render(scene, animation=True)
