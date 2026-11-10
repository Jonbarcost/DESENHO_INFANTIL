"""Align diagram visibility to actual camera marker frames; preserve geometry and motion."""
import json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from producao.animacao import key
out=ROOT/'EPISODIO_04/ARTEFATOS';t=json.loads((out/'timeline.json').read_text());shots=json.loads((out/'shots.json').read_text());s=bpy.context.scene;sc={x['mode']:x for x in t['scenes']};board=bpy.data.objects['EP4_Modelo'];rain_start=round(sc['garden']['start']*t['fps']);rain_end=round((sc['care']['start']+3)*t['fps'])
for f in range(1,t['frames']+1):
 seconds=(f-1)/t['fps'];shot=next(x for x in reversed(shots) if round(x['start']*t['fps'])+1<=f)
 board.scale=(1 if shot['kind']=='diagram' else .001,)*3;key(board,'scale',f)
 if f==1 or rain_start<=f<=rain_end+1:
  visible=1 if rain_start<f<=rain_end and (shot['kind']=='diagram' or seconds>=sc['garden']['end']-3) else .001
  for i in range(44):
   d=bpy.data.objects['EP4_Chuva'+str(i)];d.scale=(visible,)*3;key(d,'scale',f)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'episodio_04_final.blend'))
