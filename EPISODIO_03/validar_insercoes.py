"""Check that the floating leaf stays inside every dedicated insert camera."""
import json,sys
from pathlib import Path
import bpy
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'EPISODIO_03/ARTEFATOS';t=json.loads((out/'timeline.json').read_text());sc=next(x for x in t['scenes'] if x['mode']=='chase');s=bpy.context.scene
shots=[x for x in json.loads((out/'shots.json').read_text()) if sc['start']<=x['start']<sc['end']];checks=[]
for i in (0,1,2,4,7):
 shot=shots[i]
 for fraction in (.1,.5,.9):
  time=shot['start']+(shot['end']-shot['start'])*fraction;s.frame_set(round(time*t['fps'])+1)
  v=world_to_camera_view(s,s.camera,bpy.data.objects['EP3_FolhaFlutuante'].matrix_world.translation)
  assert .08<v.x<.92 and .08<v.y<.92 and v.z>0,(shot['name'],list(v))
  checks.append(dict(shot=shot['name'],time=time,uv=[v.x,v.y]))
(out/'leaf-framing-validation.json').write_text(json.dumps(dict(passed=True,checks=checks),indent=2));print('LEAF_FRAMING_PASSED',len(checks))
