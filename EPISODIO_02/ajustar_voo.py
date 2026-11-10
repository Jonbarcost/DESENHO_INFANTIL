"""Apply the reviewed flight correction without rebuilding character animation."""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from producao.serie.cena import butterfly_position


def main():
    out=ROOT/'EPISODIO_02/ARTEFATOS';t=json.loads((out/'timeline.json').read_text())
    scenes={sc['mode']:sc for sc in t['scenes']};s=bpy.context.scene
    for frame in range(1,t['frames']+1):
        time=(frame-1)/t['fps'];pos=butterfly_position(time,scenes)
        butterfly=bpy.data.objects['EP2_Borboleta'];butterfly.location=pos
        butterfly.keyframe_insert(data_path='location',frame=frame)
        for i in range(6):
            dot=bpy.data.objects['EP2_Polen_'+str(i)]
            dot.location=pos+Vector((.09*math.sin(time+i),-.06,.1*math.cos(time+i)))
            dot.keyframe_insert(data_path='location',frame=frame)
    s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'episodio_02_final.blend'))
    print('FLIGHT_ONLY_UPDATED',flush=True)


if __name__=='__main__':main()
