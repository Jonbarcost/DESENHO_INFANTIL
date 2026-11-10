
import bpy
from mathutils import Vector

base = r"C:\ESTUDIO_INFANTIL\EPISODIO_01\CENAS"
bpy.ops.wm.open_mainfile(filepath=base + r"\clareira_melhorada.blend")

def mat(nome, cor):
    m = bpy.data.materials.new(nome)
    m.diffuse_color = (*cor, 1)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*cor, 1)
    return m

marrom = mat("Capi marrom", (0.58, 0.32, 0.16))
laranja = mat("Teco laranja", (1.0, 0.48, 0.08))
roxo = mat("Maya lilas", (0.65, 0.38, 0.85))
branco = mat("Olhos brancos", (1, 1, 1))
preto = mat("Pupilas", (0.02, 0.02, 0.03))

def esfera(nome, pos, escala, material):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=8, location=pos
    )
    obj = bpy.context.object
    obj.name = nome
    obj.scale = escala
    obj.data.materials.append(material)
    return obj

def personagem(nome, x, y, cor):
    esfera(nome+"_corpo", (x,y,0.65), (0.52,0.42,0.65), cor)
    esfera(nome+"_cabeca", (x,y,1.35), (0.55,0.48,0.48), cor)

    for lado in [-1,1]:
        esfera(nome+"_olho", (x+lado*0.22,y-0.43,1.43),
               (0.13,0.08,0.16), branco)
        esfera(nome+"_pupila", (x+lado*0.22,y-0.50,1.43),
               (0.055,0.04,0.08), preto)
        esfera(nome+"_braco", (x+lado*0.53,y,0.75),
               (0.18,0.2,0.38), cor)
        esfera(nome+"_pe", (x+lado*0.28,y-0.12,0.13),
               (0.22,0.32,0.15), cor)

    esfera(nome+"_nariz", (x,y-0.50,1.23),
           (0.14,0.10,0.09), preto)

personagem("Capi", -2.2, -0.5, marrom)
personagem("Teco", 2.2, -0.5, laranja)
personagem("Maya", 0, 1.8, roxo)

# Camera enquadrando os personagens
camera = bpy.context.scene.camera
camera.location = (8, -12, 7)
direcao = Vector((0,0,1)) - camera.location
camera.rotation_euler = direcao.to_track_quat('-Z','Y').to_euler()

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 8
scene.render.filepath = base + r"\personagens_teste.png"
scene.render.image_settings.file_format = 'PNG'

bpy.ops.wm.save_as_mainfile(
    filepath=base + r"\personagens.blend"
)
bpy.ops.render.render(write_still=True)

print("PERSONAGENS CRIADOS COM SUCESSO")
