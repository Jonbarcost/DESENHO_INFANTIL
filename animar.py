
import bpy
import math
import os

base = r"C:\ESTUDIO_INFANTIL\EPISODIO_01\CENAS"

bpy.ops.wm.open_mainfile(
    filepath=base + r"\personagens.blend"
)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 36
scene.render.fps = 12

# Animar os personagens
for nome in ["Capi", "Teco", "Maya"]:
    objetos = [
        obj for obj in bpy.data.objects
        if obj.name.startswith(nome + "_")
    ]

    for obj in objetos:
        z_original = obj.location.z

        for frame in range(1, 37, 3):
            obj.location.z = z_original + 0.06 * math.sin(
                frame * 0.25
            )
            obj.keyframe_insert(
                data_path="location",
                frame=frame
            )

# Animar a sementinha
semente = bpy.data.objects.get("Sementinha Magica")

if semente:
    for frame in range(1, 37, 3):
        semente.location.z = 0.4 + 0.18 * math.sin(
            frame * 0.20
        )
        semente.rotation_euler.z = frame * 0.035
        semente.keyframe_insert(
            data_path="location", frame=frame
        )
        semente.keyframe_insert(
            data_path="rotation_euler", frame=frame
        )

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 4
scene.render.resolution_x = 480
scene.render.resolution_y = 270
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

pasta = base + r"\FRAMES"
os.makedirs(pasta, exist_ok=True)
scene.render.filepath = pasta + "\\"

bpy.ops.wm.save_as_mainfile(
    filepath=base + r"\animacao_teste.blend"
)

bpy.ops.render.render(animation=True)

print("ANIMACAO CONCLUIDA")
