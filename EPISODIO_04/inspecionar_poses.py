"""Render a small representative set of real final frames, retained for full production."""
import json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from producao.render import valid_png
out=ROOT/'EPISODIO_04/ARTEFATOS';t=json.loads((out/'timeline.json').read_text());frames=out/'frames';frames.mkdir(exist_ok=True);samples=[]
for scene in t['scenes']:
 c=next(x for x in t['dialogue'] if x['scene']==scene['id'] and x['speaker']!='NARRADORA');j=max(range(len(c['envelope'])),key=c['envelope'].__getitem__);seconds=min(c['end']-.1,c['start']+j/t['fps']);samples.append(dict(scene=scene['id'],time=seconds))
 candidates=[x for x in json.loads((out/'shots.json').read_text()) if x['kind']=='diagram' and scene['start']<=x['start']<scene['end']]
 if candidates:samples.append(dict(scene=scene['id']+'_modelo',time=candidates[len(candidates)//2]['start']+1))
kinds=set()
for shot in json.loads((out/'shots.json').read_text()):
 if shot['kind'] not in kinds:samples.append(dict(scene=shot['kind'],time=shot['start']+(shot['end']-shot['start'])*.5));kinds.add(shot['kind'])
for c in t['dialogue']:
 if c.get('pause_after',0)>=3:samples.append(dict(scene=c['id']+'_interacao',time=c['end']+1))
for item in samples:
 f=round(item['time']*t['fps'])+1;item['frame']=f;dest=frames/f'{f:04}.png'
 if not valid_png(dest,1920,1080):bpy.context.scene.frame_set(f);bpy.context.scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
(out/'poses-inspecionadas.json').write_text(json.dumps(samples,indent=2));print('POSES_READY',len(samples),flush=True)
