"""Reuse finished flowers/stream without touching their original scenes."""
import json,sys,hashlib
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'EPISODIO_04/ASSETS';records=[]
for source,target,prefixes in [('EPISODIO_02/ARTEFATOS/episodio_02_final.blend','flores_reutilizadas.blend',('EP2_Flor_','EP2_Caule_','EP2_Folha_','EP2_Petala_','EP2_Miolo_')),('EPISODIO_03/ARTEFATOS/episodio_03_final.blend','riacho_reutilizado.blend',('EP3_Agua','EP3_Margem','EP3_Pedra_'))]:
 path=ROOT/source;bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(bpy.context.scene.frame_end-150)
 objects={o for o in bpy.data.objects if o.name.startswith(prefixes)}
 for o in objects:
  o.animation_data_clear()
  if o.name.startswith('EP2_Flor_'):o.scale=(1,1,1);o.rotation_euler=(0,0,0)
 bpy.data.libraries.write(str(out/target),objects,fake_user=True,compress=True)
 records.append(dict(source=source,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),file=target,objects=len(objects)))
(out/'origem.json').write_text(json.dumps(records,indent=2))
