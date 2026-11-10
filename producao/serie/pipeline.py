"""One-command episode production from a validated JSON story. No publication step."""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

from producao.pipeline import validate_loudness
from producao.render import valid_png
from producao.timeline import probe
from .historia import load_story, make_timeline, require_final

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(cmd,log):
    with open(log,'w') as f:
        subprocess.run(list(map(str,cmd)),check=True,stdout=f,stderr=subprocess.STDOUT,
                       cwd=ROOT,env={**os.environ,'XDG_CACHE_HOME':str(ROOT/'build/cache')})


def preserve(manifest):
    expected=json.loads(manifest.read_text())
    bad=[p for p,h in expected.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    if bad:raise RuntimeError(f'Arquivo anterior alterado: {bad[:5]}')
    return len(expected)


def fingerprint(story_path,out,timeline,scene,width):
    files=list(Path(__file__).parent.glob('*.py'))+[ROOT/'producao/render.py',ROOT/'producao/animacao.py',
          ROOT/'EPISODIO_01/CENAS/personagens.blend',story_path,scene]
    if not timeline['provisional']:
        files += [out/name for name in ('master.wav','legendas.srt','audio-report.json')]
    if not timeline['provisional']:files += [ROOT/c['path'] for c in timeline['dialogue']]
    return dict(width=width,timeline=timeline,files={str(p.relative_to(ROOT)):sha(p) for p in files})


def scene_path(story,out,draft):
    return out/f"episodio_{story['episode']}_{'planejamento' if draft else 'final'}.blend"


def make_scene(story,t,out,width,draft):
    path=out/('timeline_planejamento.json' if draft else 'timeline.json')
    path.write_text(json.dumps(t,indent=2,ensure_ascii=False))
    run(['blender','-b','-t','4','--python-exit-code','1','--python',ROOT/'producao/serie/cena.py',
         '--','--timeline',path,'--output',out,'--width',width],out/('layout.log' if draft else 'scene.log'))


def generate_voices(story_path,episode,out):
    python=sys.executable
    if importlib.util.find_spec('edge_tts') is None:
        python=ROOT/'.venv/bin/python'
        if not python.is_file():raise RuntimeError('Instale producao/serie/requirements.txt no Python selecionado')
    try:
        run([python,'-m','producao.serie.vozes',story_path,out/'VOZES'],out/'tts.log')
    except subprocess.CalledProcessError:
        raise RuntimeError('Vozes não geradas. Consulte tts.log; libere speech.platform.bing.com se houver HTTP 403. Nenhum render final foi iniciado.') from None


def prepare(story_path,story,out,width):
    from .vozes import collect
    from .audio import compose
    t=make_timeline(story,collect(story,out/'VOZES',ROOT));require_final(t)
    if any((out/'frames').glob('*.png')):
        raise RuntimeError('Cena já tem renders. Retome --stage render ou use outro --output antes de preparar nova versão.')
    make_scene(story,t,out,width,False);compose(t,ROOT,out,True)
    config=fingerprint(story_path,out,t,scene_path(story,out,False),width)
    (out/'render-config.json').write_text(json.dumps(config,indent=2))
    return t


def check_config(story_path,story,out,width):
    t=json.loads((out/'timeline.json').read_text());require_final(t)
    config=fingerprint(story_path,out,t,scene_path(story,out,False),width)
    if json.loads((out/'render-config.json').read_text())!=config:
        raise RuntimeError('Roteiro/áudio/código/cena mudou; use novo --output para não misturar quadros')
    return t


def render(story,out,t,batch,start,end):
    end=end or t['frames']
    if not 1<=start<=end<=t['frames']:raise ValueError('Intervalo de render inválido')
    # The first short batch is retained and reused, not discarded as a benchmark.
    if not (out/'estimate.json').exists():
        first_end=min(end,start+11)
        run(['blender','-b',scene_path(story,out,False),'-t','4','--python-exit-code','1',
             '--python',ROOT/'producao/render.py','--','--output',out,'--start',start,'--end',first_end],out/'first_batch.log')
        progress=json.loads((out/'render-progress.json').read_text())
        estimate=dict(mean_seconds=progress['mean_seconds'],frames=t['frames'],
                      minutes=t['frames']*progress['mean_seconds']/60,
                      recorded_before_full_render=True,first_batch_retained=True)
        (out/'estimate.json').write_text(json.dumps(estimate,indent=2))
        print('FULL_RENDER_ESTIMATE_MINUTES',round(estimate['minutes'],1),flush=True)
    for a in range(start,end+1,batch):
        b=min(end,a+batch-1)
        run(['blender','-b',scene_path(story,out,False),'-t','4','--python-exit-code','1',
             '--python',ROOT/'producao/render.py','--','--output',out,'--start',a,'--end',b],out/f'render_{a:04}_{b:04}.log')


def assemble(story,out,t,width):
    require_final(t)
    missing=[i for i in range(1,t['frames']+1) if not valid_png(out/'frames'/f'{i:04}.png',width,width*9//16)]
    if missing:raise RuntimeError(f'Quadros ausentes/inválidos: {len(missing)}')
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    (out/'title.txt').write_text(story['series']);(out/'episode.txt').write_text(story['title'])
    vf=['scale=1920:1080:flags=lanczos']
    for file,y,size in [('title.txt',65,46),('episode.txt',130,36)]:
        vf.append(f"drawtext=fontfile='{font}':textfile='{out/file}':fontsize={size}:fontcolor=white:box=1:boxcolor=0x15362c@0.65:boxborderw=12:x=(w-text_w)/2:y={y}:enable='between(t,.5,6)'")
    vf.append('fade=t=in:st=0:d=0.5')
    for sc in t['scenes'][1:]:
        start=sc['start']
        vf += [f"fade=t=out:st={start-.18:.4f}:d=0.18:enable='between(t,{start-.18:.4f},{start:.4f})'",
               f"fade=t=in:st={start:.4f}:d=0.18:enable='between(t,{start:.4f},{start+.18:.4f})'"]
    vf.append(f"fade=t=out:st={t['duration']-1}:d=1")
    name=f"episodio_{story['episode']}_final";tmp=out/(name+'.partial.mp4')
    run(['ffmpeg','-v','warning','-y','-framerate',t['fps'],'-start_number',1,'-i',out/'frames/%04d.png',
         '-i',out/'master.wav','-i',out/'legendas.srt','-map','0:v','-map','1:a','-map','2:s','-vf',','.join(vf),
         '-c:v','libx264','-crf','18','-preset','fast','-threads','4','-pix_fmt','yuv420p','-c:a','aac',
         '-b:a','192k','-ar','48000','-c:s','mov_text','-metadata:s:a','language=por',
         '-metadata:s:s','language=por','-t',t['duration'],'-movflags','+faststart',tmp],out/'encode.log')
    os.replace(tmp,out/(name+'.mp4'))


def preview(story,out):
    t=json.loads((out/'timeline_planejamento.json').read_text());test=out/'TESTE';test.mkdir(exist_ok=True)
    chase=next(s for s in t['scenes'] if s['mode']=='chase')
    trip=next((c['start'] for c in t['dialogue'] if c.get('event')=='stumble'),chase['start']+8)
    start=round((trip-1.3)*t['fps'])+1;end=start+47
    scene=scene_path(story,out,True);signature=sha(scene)+sha(ROOT/'producao/render.py')
    manifest=test/'signature.txt'
    if manifest.exists() and manifest.read_text()!=signature:
        raise RuntimeError('Teste tem quadros de outra cena; use novo --output')
    manifest.write_text(signature)
    run(['blender','-b',scene,'-t','4','--python-exit-code','1','--python',ROOT/'producao/render.py',
         '--','--output',test,'--start',start,'--end',end],test/'render.log')
    vf="scale=1280:720,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='TESTE VISUAL - SEM VOZES - TEMPOS ESTIMADOS':fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6:x=(w-text_w)/2:y=24"
    run(['ffmpeg','-v','error','-y','-framerate',t['fps'],'-start_number',start,'-i',test/'frames/%04d.png',
         '-vf',vf,'-frames:v','48','-c:v','libx264','-threads','4','-pix_fmt','yuv420p',test/'teste_visual_sem_vozes.mp4'],test/'encode.log')
    run(['ffmpeg','-v','error','-i',test/'teste_visual_sem_vozes.mp4','-f','null','-'],test/'decode.log')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('story',type=Path)
    p.add_argument('--stage',choices=['all','voices','layout','music','benchmark','preview','prepare','render','assemble','verify'],default='all')
    p.add_argument('--output',type=Path);p.add_argument('--width',type=int,choices=[1280,1920],default=1920)
    p.add_argument('--batch',type=int,default=120);p.add_argument('--start',type=int,default=1);p.add_argument('--end',type=int)
    a=p.parse_args();path=a.story.resolve();story=load_story(path)
    episode=path.parent.parent;out=(a.output or episode/'ARTEFATOS').resolve()
    if ROOT not in out.parents:p.error('Saída deve ficar dentro do repositório')
    if out==ROOT or any(out==protected or protected in out.parents for protected in
                        (ROOT/'EPISODIO_01',ROOT/'build/episodio_01')):
        p.error('Saída não pode tocar no Episódio 01')
    if a.batch<1:p.error('--batch precisa ser positivo')
    out.mkdir(parents=True,exist_ok=True);manifest=episode/'RELATORIOS/preservacao-inicial.json'
    try:
        if manifest.exists():preserve(manifest)
        if a.stage in ('all','voices'):generate_voices(path,episode,out)
        if a.stage=='all' and (out/'render-config.json').exists():t=check_config(path,story,out,a.width)
        elif a.stage in ('all','prepare'):t=prepare(path,story,out,a.width)
        elif a.stage in ('render','assemble','verify'):t=check_config(path,story,out,a.width)
        if a.stage=='layout':make_scene(story,make_timeline(story,{},draft=True),out,a.width,True)
        if a.stage=='music':
            from .audio import compose
            draft_music=out/'MUSICA_PLANEJAMENTO';draft_music.mkdir(exist_ok=True)
            compose(make_timeline(story,{},draft=True),ROOT,draft_music,False)
        if a.stage=='benchmark':
            run(['blender','-b',scene_path(story,out,True),'-t','4','--python-exit-code','1',
                 '--python',ROOT/'producao/serie/amostra.py','--',out],out/'benchmark.log')
        if a.stage=='preview':preview(story,out)
        if a.stage in ('all','render'):render(story,out,t,a.batch,a.start,a.end)
        if a.stage in ('all','assemble'):assemble(story,out,t,a.width)
        if a.stage in ('all','verify'):
            from .qualidade import verify
            verify(story,out,t,a.width)
        if manifest.exists():preserve(manifest)
        print('STAGE_DONE',a.stage,flush=True)
    except Exception as exc:
        (out/'status.json').write_text(json.dumps(dict(completed=False,stage=a.stage,error=str(exc)),ensure_ascii=False,indent=2))
        print('BLOCKED',str(exc),file=sys.stderr,flush=True);raise SystemExit(1)


if __name__=='__main__':main()
