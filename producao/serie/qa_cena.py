"""Blender checks: butterfly, gait, visibility and editorial camera coverage."""
import json
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view


def main():
    args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]);final=len(args)>1 and args[1]=='final'
    t=json.loads((out/('timeline.json' if final else 'timeline_planejamento.json')).read_text())
    if final and t['provisional']:raise ValueError('Cena provisória não pode ser aprovada como final')
    scene=bpy.context.scene;visible=[];foot=[];wing=[];positions=[]
    for sc in t['scenes']:
        actor_seen={n:0 for n in ('Capi','Teco','Maya')};butterfly_seen=0
        for fraction in (.025,.2,.4,.6,.8,.96):
            time=sc['start']+(sc['end']-sc['start'])*fraction
            scene.frame_set(round(time*t['fps'])+1)
            def inside(point):
                v=world_to_camera_view(scene,scene.camera,point)
                return 0.02<v.x<.98 and .02<v.y<.98 and v.z>0
            for name in actor_seen:
                if inside(bpy.data.objects[name+'_cabeca'].matrix_world.translation):actor_seen[name]+=1
            butterfly=bpy.data.objects['EP2_Borboleta']
            butterfly_seen+=int(inside(butterfly.matrix_world.translation))
            foot.append(bpy.data.objects['Teco_EP2_Foot1'].rotation_euler.x)
            wing.append(bpy.data.objects['EP2_Asa_1'].rotation_euler.z)
            positions.append(list(butterfly.location))
        if not all(actor_seen.values()) or not butterfly_seen:
            raise ValueError(f'Cobertura de câmera incompleta em {sc["id"]}: {actor_seen}, borboleta={butterfly_seen}')
        visible.append(dict(scene=sc['id'],characters=actor_seen,butterfly=butterfly_seen))
    if max(foot)-min(foot)<.2:raise ValueError('Marcha sem articulação visível')
    if max(wing)-min(wing)<1:raise ValueError('Asas não articuladas')
    if max(p[0] for p in positions)-min(p[0] for p in positions)<2:raise ValueError('Trajetória sem deslocamento')
    report=dict(provisional=t['provisional'],camera_markers=len([m for m in scene.timeline_markers if m.camera]),
                visibility=visible,foot_rotation_range=max(foot)-min(foot),wing_rotation_range=max(wing)-min(wing),
                butterfly_position_range=[min(p[0] for p in positions),max(p[0] for p in positions)],checks='passed')
    (out/'scene-qa.json').write_text(json.dumps(report,indent=2))
    print('SCENE_QA_PASSED',report['camera_markers'],len(visible),flush=True)


if __name__=='__main__':main()
