"""A bounded render probe inside Blender: one small EEVEE frame, three native Workbench frames."""
import json
import sys
import time
from pathlib import Path

import bpy


def main():
    out=Path(sys.argv[sys.argv.index('--')+1]);s=bpy.context.scene
    t=json.loads((out/'timeline_planejamento.json').read_text())
    cases=[('BLENDER_EEVEE_NEXT',480,1),('BLENDER_WORKBENCH',1920,3)]
    results=[]
    for engine,width,count in cases:
        s.render.engine=engine;s.render.resolution_x=width;s.render.resolution_y=width*9//16
        s.render.resolution_percentage=100;s.eevee.taa_render_samples=8
        times=[]
        for i in range(count):
            s.frame_set(round(30*t['fps'])+1+i)
            s.render.filepath=str(out/f'benchmark_{engine}_{i}.png');start=time.monotonic()
            bpy.ops.render.render(write_still=True);times.append(time.monotonic()-start)
        steady=sum(times[1:] or times)/len(times[1:] or times)
        results.append(dict(engine=engine,width=width,sample_seconds=times,
                            steady_seconds=steady if count>1 else None,
                            includes_initialization=True,
                            estimated_native_seconds=steady*(1920/width)**2*t['frames'] if count>1 else None))
    fastest=min((r for r in results if r['estimated_native_seconds'] is not None),key=lambda r:r['estimated_native_seconds'])
    (out/'benchmark.json').write_text(json.dumps(dict(provisional_timing=True,frames=t['frames'],results=results,
       recommended=fastest['engine'],estimate_minutes=fastest['estimated_native_seconds']/60,
       note='Estimativa por amostra, não render completo; inclui CPU software e pode variar com a cena.'),indent=2))
    s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1280;s.render.resolution_y=720
    for sec in (10,64,130,182,202):
        s.frame_set(round(sec*t['fps'])+1);s.render.filepath=str(out/f'pose_{sec:03}.png')
        bpy.ops.render.render(write_still=True)
    print('BOUNDED_PROBE_COMPLETE',fastest['engine'],flush=True)


if __name__=='__main__':main()
