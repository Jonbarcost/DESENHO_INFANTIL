
import bpy
import math
import random
from mathutils import Vector

random.seed(42)

base = r"C:\ESTUDIO_INFANTIL\EPISODIO_01\CENAS"
bpy.ops.wm.open_mainfile(filepath=base + r"\clareira_3d.blend")

def mat(nome, cor, emissao=0):
    m = bpy.data.materials.new(nome)
    m.diffuse_color = (*cor, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*cor, 1)
    if emissao:
        bsdf.inputs["Emission Color"].default_value = (*cor, 1)
        bsdf.inputs["Emission Strength"].default_value = emissao
    return m

rosa = mat("Rosa", (1, 0.25, 0.55))
amarelo = mat("Amarelo", (1, 0.85, 0.12))
azul = mat("Azul", (0.15, 0.55, 1))
branco = mat("Branco", (1, 0.95, 0.85))
verde = mat("Verde claro", (0.22, 0.65, 0.18))
pedra = mat("Pedras", (0.55, 0.62, 0.65))

cores = [rosa, amarelo, azul, branco]

# Flores espalhadas pela clareira
for i in range(28):
    ang = random.uniform(0, 2 * math.pi)
    raio = random.uniform(2.5, 7.5)
    x = math.cos(ang) * raio
    y = math.sin(ang) * raio

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8, ring_count=4,
        location=(x, y, 0.07)
    )
    flor = bpy.context.object
    flor.name = "Flor_%02d" % i
    flor.scale = (0.15, 0.15, 0.08)
    flor.data.materials.append(random.choice(cores))

# Arbustos
for i in range(14):
    ang = random.uniform(0, 2 * math.pi)
    raio = random.uniform(5, 8)
    x = math.cos(ang) * raio
    y = math.sin(ang) * raio

    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1,
        radius=random.uniform(0.35, 0.65),
        location=(x, y, 0.3)
    )
    bpy.context.object.data.materials.append(verde)

# Pedras decorativas
for i in range(8):
    ang = random.uniform(0, 2 * math.pi)
    raio = random.uniform(3, 7)
    x = math.cos(ang) * raio
    y = math.sin(ang) * raio

    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1, radius=0.3,
        location=(x, y, 0.08)
    )
    obj = bpy.context.object
    obj.scale = (1.2, 0.8, 0.4)
    obj.data.materials.append(pedra)

# Ceu azul
mundo = bpy.context.scene.world
mundo.use_nodes = True
bg = mundo.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.35, 0.65, 1, 1)
bg.inputs["Strength"].default_value = 0.8

# Camera e render
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 8
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = base + r"\clareira_melhorada.png"

# Salvar como novo projeto
bpy.ops.wm.save_as_mainfile(
    filepath=base + r"\clareira_melhorada.blend"
)

bpy.ops.render.render(write_still=True)

print("CLAREIRA MELHORADA COM SUCESSO")
