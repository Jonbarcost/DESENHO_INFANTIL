
import bpy
import math
from mathutils import Vector

cena = bpy.context.scene
cena.render.fps = 12
cena.frame_start = 1
cena.frame_end = 612

# Preservar os modelos originais
personagens = {}

for nome in ["Capi", "Teco", "Maya"]:
    objetos = [
        obj for obj in bpy.data.objects
        if obj.name.startswith(nome + "_")
    ]
    personagens[nome] = objetos

sementinha = bpy.data.objects.get("Sementinha Magica")

# Animar cada personagem como um conjunto
def mover_personagem(nome, quadro, deslocamento):
    for obj in personagens[nome]:
        original = obj.get("posicao_base")
        if original is None:
            original = tuple(obj.location)
            obj["posicao_base"] = list(original)

        obj.location = Vector(original) + Vector(deslocamento)
        obj.keyframe_insert(data_path="location", frame=quadro)

# Movimentos suaves dos personagens
for nome in personagens:
    mover_personagem(nome, 1, (0, 0, 0))
    mover_personagem(nome, 75, (0, 0, 0.08))
    mover_personagem(nome, 145, (0, 0, 0))
    mover_personagem(nome, 220, (0, 0.15, 0))
    mover_personagem(nome, 300, (0, 0, 0))
    mover_personagem(nome, 450, (0, 0, 0.12))
    mover_personagem(nome, 612, (0, 0, 0))

# Plantio da sementinha
if sementinha:
    posicao = sementinha.location.copy()

    for quadro, altura in [
        (1, 0),
        (220, 0),
        (285, -0.28),
        (345, -0.28),
        (410, -0.28),
    ]:
        sementinha.location = posicao + Vector((0, 0, altura))
        sementinha.keyframe_insert("location", frame=quadro)

    # Desaparecer quando a flor crescer
    sementinha.hide_render = False
    sementinha.keyframe_insert("hide_render", frame=410)
    sementinha.hide_render = True
    sementinha.keyframe_insert("hide_render", frame=411)

# Criar flor simples no mesmo estilo infantil
bpy.ops.mesh.primitive_cylinder_add(
    vertices=12,
    radius=0.07,
    depth=1.0,
    location=(0, 0, 0.55)
)

caule = bpy.context.object
caule.name = "Flor_Caule"

material = bpy.data.materials.new("Verde_Flor")
material.diffuse_color = (0.2, 0.65, 0.2, 1)
caule.data.materials.append(material)

# Crescimento
for quadro, escala in [(1, 0), (410, 0), (470, 1)]:
    caule.scale = (escala, escala, escala)
    caule.keyframe_insert("scale", frame=quadro)

# Petalas
for i in range(6):
    angulo = i * math.tau / 6

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12,
        ring_count=8,
        location=(
            math.cos(angulo) * 0.23,
            math.sin(angulo) * 0.23,
            1.12
        )
    )

    petala = bpy.context.object
    petala.name = f"Flor_Petala_{i}"
    petala.scale = (0.19, 0.12, 0.08)

    mat = bpy.data.materials.new(f"Rosa_{i}")
    mat.diffuse_color = (1, 0.45, 0.65, 1)
    petala.data.materials.append(mat)

    tamanho = petala.scale.copy()

    petala.scale = (0, 0, 0)
    petala.keyframe_insert("scale", frame=410)

    petala.scale = tamanho
    petala.keyframe_insert("scale", frame=470)

# Configuracao leve para VM
cena.render.engine = "CYCLES"
cena.cycles.samples = 8
cena.cycles.device = "CPU"

cena.render.resolution_x = 480
cena.render.resolution_y = 270
cena.render.resolution_percentage = 100

saida = r"C:\ESTUDIO_INFANTIL\EPISODIO_01\CENAS\episodio_01_animado.blend"
bpy.ops.wm.save_as_mainfile(filepath=saida)

print("ANIMACAO DAS SEIS CENAS CONFIGURADA")
print(saida)
