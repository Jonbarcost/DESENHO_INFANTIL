import mathutils

import bpy
import math
import os

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

base = r"C:\ESTUDIO_INFANTIL\EPISODIO_01"
os.makedirs(base + r"\CENAS", exist_ok=True)

def material(nome, cor, brilho=0):
    m = bpy.data.materials.new(nome)
    m.diffuse_color = (*cor, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*cor, 1)
    if brilho:
        bsdf.inputs["Emission Color"].default_value = (*cor, 1)
        bsdf.inputs["Emission Strength"].default_value = brilho
    return m

grama = material("Grama", (0.17, 0.55, 0.18))
tronco = material("Tronco", (0.38, 0.18, 0.07))
folhas = material("Folhas", (0.07, 0.38, 0.12))
dourado = material("Sementinha magica", (1, 0.65, 0.08), 2)

bpy.ops.mesh.primitive_cylinder_add(
    vertices=48, radius=9, depth=0.3,
    location=(0, 0, -0.2)
)
bpy.context.object.name = "Clareira"
bpy.context.object.data.materials.append(grama)

for x, y in [(-5, 2), (-4, 5), (4, 5), (6, 1), (-6, -2)]:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=10, radius=0.35, depth=3,
        location=(x, y, 1.5)
    )
    bpy.context.object.data.materials.append(tronco)

    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1, radius=1.7,
        location=(x, y, 3.5)
    )
    bpy.context.object.data.materials.append(folhas)

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24, ring_count=12,
    location=(0, 0, 0.4)
)
semente = bpy.context.object
semente.name = "Sementinha Magica"
semente.scale = (0.3, 0.3, 0.5)
semente.data.materials.append(dourado)

for frame, altura in [(1, 0.4), (24, 0.8), (48, 0.4)]:
    semente.location.z = altura
    semente.keyframe_insert(
        data_path="location", frame=frame
    )

bpy.ops.object.light_add(
    type='AREA', location=(0, -3, 7)
)
bpy.context.object.data.energy = 1000
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 8

bpy.ops.object.camera_add(location=(9, -12, 8))
camera = bpy.context.object
direction = (mathutils.Vector((0, 0, 1)) -
             camera.location)
camera.rotation_euler = direction.to_track_quat(
    '-Z', 'Y'
).to_euler()
bpy.context.scene.camera = camera

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 8
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = base + r"\CENAS\teste_clareira.png"
scene.frame_start = 1
scene.frame_end = 48
scene.render.fps = 12

bpy.ops.wm.save_as_mainfile(
    filepath=base + r"\CENAS\clareira_3d.blend"
)
bpy.ops.render.render(write_still=True)

print("CENA 3D CRIADA COM SUCESSO")


