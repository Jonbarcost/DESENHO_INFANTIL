"""Measure real rendered motion per shot and produce a contact sheet, without rerendering."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=Path('build/episodio_01'))
    a=p.parse_args();out=a.output
    t=json.loads((out/'timeline.json').read_text())
    shots=json.loads((out/'shots.json').read_text())
    motion=[];contact=Image.new('RGB',(1280,360*((len(shots)+1)//2)),(21,47,36))
    for i,shot in enumerate(shots):
        # Sample within each cut, never claim that the cut itself is animation.
        duration=shot['end']-shot['start']
        times=[shot['start']+duration*r for r in (.15,.4,.65,.85)]
        frames=[min(t['frames'],round(s*t['fps'])+1) for s in times]
        images=[Image.open(out/'frames'/f'{f:04}.png').convert('RGB') for f in frames]
        arrays=[np.asarray(im.resize((320,180)),dtype=np.float32) for im in images]
        differences=[float(np.mean(np.abs(b-a))) for a,b in zip(arrays,arrays[1:])]
        if min(differences)<=.05:
            raise RuntimeError(f"Tomada sem movimento mensurável: {shot['name']}")
        im=images[1].resize((640,360))
        contact.paste(im,(i%2*640,i//2*360))
        draw=ImageDraw.Draw(contact)
        draw.rectangle((i%2*640,i//2*360,i%2*640+639,i//2*360+24),fill=(21,47,36))
        draw.text((i%2*640+8,i//2*360+6),f"{shot['name']} — {times[1]:.2f}s",fill='white')
        motion.append(dict(shot=shot['name'],frames=frames,mean_absolute_pixel_changes=differences))
        for im in images:im.close()
    contact.save(out/'storyboard-final.jpg',quality=90)
    report=dict(shots=len(shots),motion=motion,
                method='Quatro amostras dentro de cada tomada; diferença absoluta RGB média em 320x180, sem incluir cortes',
                limitation='Métrica demonstra variação visual, não substitui inspeção artística nem prova sincronização fonética')
    (out/'motion-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('MOTION_VERIFIED',len(shots),'shots')


if __name__=='__main__':main()
