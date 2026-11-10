"""Validate the baked animation and scene actions. Run inside Blender on the derived .blend."""
import json
import sys
from pathlib import Path

import bpy


def main():
    out=Path(sys.argv[sys.argv.index('--')+1])
    t=json.loads((out/'timeline.json').read_text())
    s=bpy.context.scene
    motion={name:{'root':[],'head':[],'arm':[],'mouth':[]} for name in ('Capi','Teco','Maya')}
    for f in range(1,s.frame_end+1):
        s.frame_set(f)
        for name,m in motion.items():
            m['root'].append(tuple(bpy.data.objects[name+'_Controle'].location))
            m['head'].append(tuple(bpy.data.objects[name+'_Expressao'].rotation_euler))
            m['arm'].append(tuple(bpy.data.objects[name+'_Ombro_1'].rotation_euler))
            m['mouth'].append(bpy.data.objects[name+'_BocaAnimada'].scale.z)
    summary={}
    for name,m in motion.items():
        ranges={k:max(max(v[i] for v in values)-min(v[i] for v in values) for i in range(3))
                for k,values in m.items() if k!='mouth'}
        ranges['mouth']=max(m['mouth'])-min(m['mouth'])
        assert ranges['root']>.05 and ranges['head']>.05 and ranges['arm']>1 and ranges['mouth']>.03,(name,ranges)
        summary[name]=ranges
    e=t['events']
    def frame(time):s.frame_set(round(time*t['fps'])+1)
    frame(e['plant_start']);seed_before=bpy.data.objects['Sementinha Magica'].location.z
    frame(e['plant_end']);seed_after=bpy.data.objects['Sementinha Magica'].location.z
    assert seed_before>.8 and seed_after<0
    frame(e['growth_start']);small=bpy.data.objects['Flor_Crescimento'].scale.x
    frame(e['growth_end']);large=bpy.data.objects['Flor_Crescimento'].scale.x
    assert small<.01 and large>.99
    assert len([m for m in s.timeline_markers if m.camera])==14
    result=dict(character_motion_ranges=summary,seed_heights=[seed_before,seed_after],
                flower_scale=[small,large],camera_cuts=14,frames=s.frame_end,
                all_checks='passed')
    (out/'animation-report.json').write_text(json.dumps(result,indent=2))
    print('ANIMATION_VERIFIED',result)


if __name__=='__main__':main()
