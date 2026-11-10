"""Checks actual baked scene: actor coverage, dry-bank positions, articulation and flow."""
import json,sys,math
from pathlib import Path
import bpy
from bpy_extras.object_utils import world_to_camera_view

def main():
 out=Path(sys.argv[sys.argv.index('--')+1]);t=json.loads((out/'timeline.json').read_text());s=bpy.context.scene
 seen={n:0 for n in ('Capi','Teco','Maya')};feet=[];tails=[];leaves=[];mouth_checks=[];bank_checks=0
 for sc in t['scenes']:
  for fraction in (.03,.2,.4,.6,.8,.96):
   s.frame_set(round((sc['start']+(sc['end']-sc['start'])*fraction)*t['fps'])+1)
   for n in seen:
    point=bpy.data.objects[n+'_cabeca'].matrix_world.translation;v=world_to_camera_view(s,s.camera,point)
    seen[n]+=int(.02<v.x<.98 and .02<v.y<.98 and v.z>0)
    r=bpy.data.objects[n+'_EP3_Root'];x,y,_=r.location
    if y>2.8+.32*math.sin(x*.55)-1.13-.15:raise ValueError('Personagem perto demais da água: '+n)
    bank_checks+=1
   feet.append(bpy.data.objects['Teco_EP3_Foot1'].rotation_euler.x);tails.append(bpy.data.objects['EP3_Cauda'].rotation_euler.z);leaves.append(bpy.data.objects['EP3_FolhaFlutuante'].location.x)
 if not all(seen.values()) or max(feet)-min(feet)<.2 or max(tails)-min(tails)<.5 or max(leaves)-min(leaves)<4:raise ValueError('Movimento/cobertura insuficiente')
 for c in t['dialogue']:
  if c['speaker']=='NARRADORA':continue
  diffs=[]
  for frame in range(math.ceil(c['start']*t['fps'])+1,math.floor(c['end']*t['fps'])+1):
   seconds=(frame-1)/t['fps'];j=int((seconds-c['start'])*t['fps'])
   if not 0<=j<len(c['envelope']):continue
   s.frame_set(frame);actual=bpy.data.objects[c['speaker'].title()+'_EP3_Mouth'].scale.z
   diffs.append(abs(actual-(.017+.09*c['envelope'][j])))
  if not diffs or max(diffs)>1e-6:raise ValueError('Boca não corresponde ao envelope: '+c['id'])
  mouth_checks.append(dict(id=c['id'],max_error=max(diffs,default=0)))
 report=dict(checks='passed',visibility=seen,bank_position_samples=bank_checks,foot_range=max(feet)-min(feet),tail_range=max(tails)-min(tails),leaf_range=max(leaves)-min(leaves),mouth_samples=mouth_checks,camera_markers=len([m for m in s.timeline_markers if m.camera]))
 (out/'scene-qa.json').write_text(json.dumps(report,indent=2));print('SCENE_QA_PASSED',flush=True)
if __name__=='__main__':main()
