"""Focus leaf inserts without changing geometry or earlier shots."""
import json,sys,shutil
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from producao.animacao import key,smooth
out=ROOT/'EPISODIO_03/ARTEFATOS';t=json.loads((out/'timeline.json').read_text());sc=next(s for s in t['scenes'] if s['mode']=='chase');s=bpy.context.scene
shots=[x for x in json.loads((out/'shots.json').read_text()) if sc['start']<=x['start']<sc['end']]
for i,shot in enumerate(shots):
 if i not in (0,1,2,4,7):continue
 cam=bpy.data.objects[shot['camera']];cam.animation_data_clear()
 x=-2.6+5.2*smooth(sc['start'],sc['end'],(shot['start']+shot['end'])/2)
 loc=Vector((x+.5,5.3,6));target=Vector((x,2.8+.32*__import__('math').sin(x*.55),.15))
 cam.location=loc;cam.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler()
 key(cam,'location',round(shot['start']*t['fps'])+1);cam.location+=(target-loc).normalized()*.16;key(cam,'location',round(shot['end']*t['fps']))
 for curve in cam.animation_data.action.fcurves:
  for pt in curve.keyframe_points:pt.interpolation='LINEAR'
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'episodio_03_final.blend'))
