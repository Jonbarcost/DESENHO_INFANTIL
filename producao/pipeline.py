"""python3 -m producao.pipeline --stage all (from the repository root)."""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

from .render import valid_png
from .som import subtitles, synthesize
from .timeline import probe, source_hashes, write_timeline

ROOT=Path(__file__).resolve().parents[1]


def run(command, log=None):
    print('RUN', ' '.join(map(str,command)),flush=True)
    if log:
        with open(log,'w') as f:
            subprocess.run(list(map(str,command)),check=True,stdout=f,stderr=subprocess.STDOUT,
                           env={**os.environ,'XDG_CACHE_HOME':str(ROOT/'build/cache')})
    else:
        subprocess.run(list(map(str,command)),check=True)


def signature(width,engine,samples):
    paths=[ROOT/'producao'/s for s in ('timeline.py','animacao.py','render.py')]
    paths += [ROOT/'EPISODIO_01/CENAS/personagens.blend']
    paths += sorted((ROOT/'EPISODIO_01/VOZES').glob('cena_*.mp3'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    return dict(width=width,height=width*9//16,engine=engine,samples=samples,inputs=hashes)


def check_sources():
    expected=json.loads((ROOT/'docs/auditoria/hashes-originais.json').read_text())
    actual=source_hashes(ROOT)
    changed=[p for p,h in expected.items() if actual.get(p)!=h]
    if changed:raise RuntimeError(f'Originais alterados: {changed}')
    return len(expected)


def prepared_manifest(out,config):
    artifacts={name:hashlib.sha256((out/name).read_bytes()).hexdigest()
               for name in ('episodio_01_final.blend','timeline.json')}
    return {**config,'prepared_artifacts':artifacts}


def validate_loudness(log):
    matches=re.findall(r'\{\s*"input_i"\s*:.*?\}',log,re.DOTALL)
    if not matches:raise ValueError('Medição de loudness ausente')
    values=json.loads(matches[-1])
    integrated,peak=float(values['input_i']),float(values['input_tp'])
    if not math.isfinite(integrated) or not math.isfinite(peak):
        raise ValueError('Medição de loudness não finita')
    if not -18<=integrated<=-14 or peak>-1:
        raise ValueError(f'Áudio fora dos limites: {integrated} LUFS, {peak} dBTP')
    return values


def prepare(out,config):
    out.mkdir(parents=True,exist_ok=True)
    old=out/'render-config.json'
    previous=json.loads(old.read_text()) if old.exists() else None
    if previous is not None:
        previous.pop('prepared_artifacts',None)
    if previous is not None and previous!=config and any((out/'frames').glob('*.png')):
        raise RuntimeError('Configuração mudou; use outro --output para preservar os renders anteriores.')
    check_sources()
    timeline=write_timeline(ROOT,out)
    synthesize(timeline,ROOT,out)
    subtitles(timeline,out/'legendas.srt')
    run(['blender','-b','-t','4','--python-exit-code','1','--python',ROOT/'producao/animacao.py',
         '--','--root',ROOT,'--output',out,'--width',config['width'],'--samples',config['samples'],
         '--engine',config['engine']],out/'build.log')
    old.write_text(json.dumps(prepared_manifest(out,config),indent=2))
    return timeline


def require_config(out,config):
    if json.loads((out/'render-config.json').read_text())!=prepared_manifest(out,config):
        raise RuntimeError('Renders/configuração obsoletos: use um novo --output e --stage prepare.')


def assemble(out,timeline,config):
    frames=out/'frames'
    bad=[f for f in range(1,timeline['frames']+1)
         if not valid_png(frames/f'{f:04}.png',config['width'],config['height'])]
    if bad:raise RuntimeError(f'Quadros ausentes/inválidos: {bad[:20]} ({len(bad)} total)')
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    (out/'title.txt').write_text('CLAREIRA DOS CURIOSOS',encoding='utf-8')
    (out/'episode.txt').write_text('A Sementinha Mágica',encoding='utf-8')
    (out/'bye.txt').write_text('Até a próxima aventura!',encoding='utf-8')
    e=timeline['events'];end=timeline['duration']
    filters=[]

    def text(file,start,stop,y,size):
        filters.append(f"drawtext=fontfile='{font}':textfile='{out/file}':fontsize={size}:"
                       f"fontcolor=white:shadowcolor=0x18382c:shadowx=3:shadowy=3:"
                       f"box=1:boxcolor=0x173e32@0.65:boxborderw=16:"
                       f"x=(w-text_w)/2:y={y}:enable='between(t,{start:.3f},{stop:.3f})'")

    scale=config['width']/1920
    text('title.txt',.35,5.8,int(70*scale),round(49*scale))
    text('episode.txt',.35,5.8,int(140*scale),round(39*scale))
    # These are visual verses from the supplied script, not claimed sung dialogue.
    for i,line in enumerate(['Água, sol e muito amor!', 'Nossa sementinha vai virar uma flor!',
                              'Cresce, cresce, sem parar!', 'Nossa amizade vai florescer no ar!']):
        p=f'verso_{i}.txt';(out/p).write_text(line,encoding='utf-8')
        text(p,e['plant_end']+i*2,e['plant_end']+(i+1)*2-.1,int(62*scale),round(35*scale))
    text('bye.txt',e['goodbye']+.25,end-.4,int(70*scale),round(46*scale))
    filters.extend(['fade=t=in:st=0:d=0.4',f'fade=t=out:st={end-1:.4f}:d=1'])
    tmp=out/'episodio_01_final.partial.mp4'
    run(['ffmpeg','-v','warning','-y','-framerate',str(timeline['fps']),'-start_number','1',
         '-i',frames/'%04d.png','-i',out/'master.wav','-i',out/'legendas.srt',
         '-map','0:v:0','-map','1:a:0','-map','2:s:0','-vf',','.join(filters),
         '-c:v','libx264','-preset','fast','-crf','18','-threads','4','-pix_fmt','yuv420p',
         '-c:a','aac','-b:a','192k','-ar','48000','-c:s','mov_text',
         '-metadata:s:a:0','language=por','-metadata:s:s:0','language=por',
         '-metadata','title=Clareira dos Curiosos — A Sementinha Mágica',
         '-t',str(end),'-movflags','+faststart',tmp],out/'encode.log')
    os.replace(tmp,out/'episodio_01_final.mp4')


def verify(out,timeline,config):
    video=out/'episodio_01_final.mp4'
    info=probe(video)
    v=next(s for s in info['streams'] if s['codec_type']=='video')
    a=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'])==(config['width'],config['height'])
    assert v['codec_name']=='h264' and a['codec_name']=='aac'
    assert v['r_frame_rate']==f"{timeline['fps']}/1"
    assert int(v['nb_frames'])==timeline['frames']
    assert abs(float(info['format']['duration'])-timeline['duration'])<.1
    run(['ffmpeg','-v','error','-i',video,'-map','0:v','-map','0:a','-f','null','-'],out/'decode.log')
    run(['ffmpeg','-hide_banner','-i',video,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json',
         '-f','null','-'],out/'loudness.log')
    loudness=validate_loudness((out/'loudness.log').read_text())
    result=dict(video=info,original_files_verified=check_sources(),
                dialogue_count=len(timeline['dialogue']),full_decode='passed',
                duration=timeline['duration'],frames=timeline['frames'],loudness=loudness)
    (out/'validation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print('VERIFIED',timeline['frames'],'frames',timeline['duration'],'seconds',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',choices=['all','prepare','render','assemble','verify'],default='all')
    p.add_argument('--output',type=Path,default=ROOT/'build/episodio_01')
    p.add_argument('--width',type=int,choices=[480,1280,1920],default=1920)
    p.add_argument('--engine',choices=['BLENDER_WORKBENCH','CYCLES'],default='BLENDER_WORKBENCH')
    p.add_argument('--samples',type=int,default=8)
    p.add_argument('--start',type=int,default=1)
    p.add_argument('--end',type=int)
    a=p.parse_args();out=a.output.resolve()
    # Prevent accidental outputs into original asset directories.
    if out==ROOT or ROOT/'EPISODIO_01'==out or ROOT/'EPISODIO_01' in out.parents:
        p.error('Use build/ ou uma pasta externa para a produção derivada.')
    config=signature(a.width,a.engine,a.samples)
    if a.stage in ('all','prepare'):prepare(out,config)
    else:require_config(out,config)
    timeline=json.loads((out/'timeline.json').read_text())
    if a.stage in ('all','render'):
        cmd=['blender','-b',out/'episodio_01_final.blend','-t','4','--python-exit-code','1',
             '--python',ROOT/'producao/render.py','--','--output',out,'--start',a.start]
        if a.end:cmd+=['--end',a.end]
        run(cmd,out/'render.log')
    if a.stage in ('all','assemble'):assemble(out,timeline,config)
    if a.stage in ('all','verify'):verify(out,timeline,config)


if __name__=='__main__':main()
