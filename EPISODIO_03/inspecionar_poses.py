"""Blender pre-render QA: native final frames, retained for the full render."""
import json
import sys
from pathlib import Path

import bpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from producao.render import valid_png


def main():
    out=ROOT/'EPISODIO_03/ARTEFATOS';t=json.loads((out/'timeline.json').read_text())
    frames=out/'frames';frames.mkdir(exist_ok=True);samples=[]
    for scene in t['scenes']:
        clip=next(c for c in t['dialogue'] if c['scene']==scene['id'] and c['speaker']!='NARRADORA')
        envelope=clip['envelope'];peak=max(range(len(envelope)),key=envelope.__getitem__)
        time=min(clip['end']-.1,clip['start']+peak/t['fps'])
        samples.append(dict(scene=scene['id'],time=time,frame=round(time*t['fps'])+1))
    for clip in t['dialogue']:
        if clip.get('event') in ('stumble','cleanup') or 'peixinho' in clip['text'].lower() or 'sapinho respondeu' in clip['text'].lower():
            time=clip['start']+.8;samples.append(dict(scene=clip['id'],time=time,frame=round(time*t['fps'])+1))
    s=bpy.context.scene
    for item in samples:
        f=item['frame'];dest=frames/f'{f:04}.png'
        if valid_png(dest,1920,1080):continue
        s.frame_set(f);s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
    (out/'poses-inspecionadas.json').write_text(json.dumps(samples,indent=2))
    print('FINAL_POSES_RENDERED',len(samples),flush=True)


if __name__=='__main__':main()
