"""Acceptance checks on actual baked poses, scene coverage and illustrative inserts."""
import json,sys,math
from pathlib import Path
import bpy
from bpy_extras.object_utils import world_to_camera_view

def main():
 out=Path(sys.argv[sys.argv.index('--')+1]);t=json.loads((out/'timeline.json').read_text());s=bpy.context.scene
 seen={n:0 for n in ('Capi','Teco','Maya')};feet=[];arms=[];positions=[];puddles=[];flowers=[]
 for sc in t['scenes']:
  for fraction in (.03,.2,.4,.6,.8,.96):
   s.frame_set(round((sc['start']+(sc['end']-sc['start'])*fraction)*t['fps'])+1)
   for name in seen:
    v=world_to_camera_view(s,s.camera,bpy.data.objects[name+'_cabeca'].matrix_world.translation);seen[name]+=int(.02<v.x<.98 and .02<v.y<.98 and v.z>0)
   feet.append(bpy.data.objects['Teco_EP4_Foot1'].rotation_euler.x);arms.append(bpy.data.objects['Teco_EP4_Arm1'].rotation_euler.y);positions.append(bpy.data.objects['Teco_EP4_Root'].location.x);puddles.append(bpy.data.objects['EP4_Poca'].scale.x);flowers.append(bpy.data.objects['EP2_Flor_0'].rotation_euler.y)
 if not all(seen.values()) or max(feet)-min(feet)<.25 or max(arms)-min(arms)<1.4 or max(positions)-min(positions)<.8 or max(puddles)-min(puddles)<.5 or max(flowers)-min(flowers)<.07:raise ValueError('Cobertura ou amplitude de animação insuficiente')
 mouth=[]
 for c in t['dialogue']:
  if c['speaker']=='NARRADORA':continue
  errors=[]
  for f in range(math.ceil(c['start']*t['fps'])+1,math.floor(c['end']*t['fps'])+1):
   j=int(((f-1)/t['fps']-c['start'])*t['fps'])
   if 0<=j<len(c['envelope']):
    s.frame_set(f);actual=bpy.data.objects[c['speaker'].title()+'_EP4_Mouth'].scale.z;errors.append(abs(actual-(.017+.09*c['envelope'][j])))
  if not errors or max(errors)>1e-6:raise ValueError('Boca dessincronizada: '+c['id'])
  mouth.append(dict(id=c['id'],max_error=max(errors)))
 inserts=[]
 for shot in json.loads((out/'shots.json').read_text()):
  if shot['kind']!='diagram':continue
  for fraction in (.15,.5,.85):
   s.frame_set(round((shot['start']+(shot['end']-shot['start'])*fraction)*t['fps'])+1)
   v=world_to_camera_view(s,s.camera,bpy.data.objects['EP4_Nuvem'].matrix_world.translation)
   if not (.12<v.x<.88 and .12<v.y<.88 and v.z>0):raise ValueError('Nuvem fora do enquadramento')
   inserts.append(dict(shot=shot['name'],uv=[v.x,v.y]))
 report=dict(checks='passed',visibility=seen,foot_range=max(feet)-min(feet),arm_range=max(arms)-min(arms),walk_range=max(positions)-min(positions),puddle_range=max(puddles)-min(puddles),flower_range=max(flowers)-min(flowers),mouth_checks=mouth,diagram_checks=inserts,camera_markers=len([m for m in s.timeline_markers if m.camera]))
 (out/'scene-qa.json').write_text(json.dumps(report,indent=2));print('SCENE_QA_PASSED',len(inserts),len(mouth),flush=True)
if __name__=='__main__':main()
