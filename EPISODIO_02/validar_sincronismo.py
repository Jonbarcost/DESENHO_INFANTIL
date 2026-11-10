"""Cross-check baked mouth animation against each actual decoded voice clip."""
import json
import math
import subprocess
import sys
from pathlib import Path

import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'EPISODIO_02/ARTEFATOS';t=json.loads((out/'timeline.json').read_text());s=bpy.context.scene
    measurements=[]
    for clip in t['dialogue']:
        if clip['speaker']=='NARRADORA':continue
        data=subprocess.check_output(['ffmpeg','-v','error','-i',str(ROOT/clip['path']),
                                      '-ac','1','-ar','24000','-f','f32le','-'])
        audio=np.frombuffer(data,dtype='<f4');block=round(24000/t['fps'])
        energy=np.array([np.sqrt(np.mean(audio[j:j+block]**2)) for j in range(0,len(audio),block)])
        values=[];reference=[]
        start=math.ceil(clip['start']*t['fps'])+1;end=math.floor(clip['end']*t['fps'])+1
        mouth=bpy.data.objects[clip['speaker'].title()+'_EP2_Mouth']
        for frame in range(start,end+1):
            seconds=(frame-1)/t['fps'];i=int((seconds-clip['start'])*t['fps'])
            if not 0<=i<len(energy):continue
            s.frame_set(frame);values.append(mouth.scale.z);reference.append(energy[i])
        if len(values)<6 or np.std(values)<.003:raise ValueError('Boca sem movimento na fala '+clip['id'])
        correlation=float(np.corrcoef(values,reference)[0,1])
        # A comic reaction intentionally adds a small independent mouth gesture at the stumble.
        threshold=.65 if clip.get('event')=='stumble' else .90
        if not np.isfinite(correlation) or correlation<threshold:
            raise ValueError(f'Sincronismo de energia insuficiente: {clip["id"]} {correlation}')
        measurements.append(dict(id=clip['id'],frames=len(values),energy_mouth_correlation=correlation))
    report=dict(method='Correlação entre RMS de MP3 decodificado e abertura de boca baked na cena',
                limitation='Verifica cadência/energia; não verifica visemas fonéticos',
                dialogue_checks=len(measurements),minimum_correlation=min(m['energy_mouth_correlation'] for m in measurements),
                measurements=measurements,passed=True)
    (out/'lip-sync-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('LIP_SYNC_VALIDATED',len(measurements),report['minimum_correlation'],flush=True)


if __name__=='__main__':main()
