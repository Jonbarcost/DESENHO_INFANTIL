"""Acceptance gates for real exports. Provisional layouts can never pass."""
import json
import re
from pathlib import Path

from producao.pipeline import validate_loudness
from producao.timeline import probe
from .historia import require_final


def verify(story,out,t,width):
    from .pipeline import ROOT,run,sha
    from .vozes import collect,voice_context
    require_final(t)
    actual,folder=voice_context(story,out)
    measured=collect(actual,folder,ROOT)
    if len(measured)!=len(t['dialogue']):raise ValueError('Falas ausentes')
    for a,b in zip(t['dialogue'],t['dialogue'][1:]):
        if b['start']<a['end']+.59:raise ValueError('Falas sobrepostas')
    for c in t['dialogue']:
        if abs(c['end']-c['start']-measured[c['id']]['duration'])>.002:
            raise ValueError('Duração da fala não corresponde ao MP3')
    candidate=out/f"episodio_{story['episode']}_candidate.mp4"
    video=candidate if candidate.exists() else out/f"episodio_{story['episode']}_final.mp4"
    info=probe(video)
    v=next(c for c in info['streams'] if c['codec_type']=='video')
    a=next(c for c in info['streams'] if c['codec_type']=='audio')
    if (v['width'],v['height'],v['codec_name'],a['codec_name'])!=(1920,1080,'h264','aac'):
        raise ValueError('Formato final incorreto')
    if int(v['nb_frames'])!=t['frames'] or v['r_frame_rate']!=f"{t['fps']}/1":raise ValueError('Cadência/quadros incorretos')
    if abs(float(info['format']['duration'])-t['duration'])>.1:raise ValueError('Duração de exportação incorreta')
    if not story['target_duration'][0]<=t['duration']<=story['target_duration'][1]:raise ValueError('Duração fora da meta')
    run(['ffmpeg','-v','error','-i',video,'-map','0:v','-map','0:a','-f','null','-'],out/'decode.log')
    run(['ffmpeg','-hide_banner','-i',video,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json',
         '-f','null','-'],out/'loudness.log');loudness=validate_loudness((out/'loudness.log').read_text())
    run(['ffmpeg','-hide_banner','-i',video,'-an','-vf','blackdetect=d=0.5:pix_th=0.05:pic_th=0.98,freezedetect=n=-50dB:d=3',
         '-f','null','-'],out/'visual-detection.log')
    visual=(out/'visual-detection.log').read_text()
    if 'freeze_start:' in visual:raise ValueError('Possível cena congelada; revisar visual-detection.log')
    for start,duration in re.findall(r'black_start:([\d.]+).*?black_duration:([\d.]+)',visual):
        if .6<float(start)<t['duration']-1.5 and float(duration)>.5:raise ValueError('Trecho preto não previsto')
    levels=json.loads((out/'audio-report.json').read_text())
    if not levels['dialogue_included'] or len(levels['speech_background'])!=len(t['dialogue']):
        raise ValueError('Mixagem sem todas as falas')
    if min(c['voice_background_db'] for c in levels['speech_background'])<12:raise ValueError('Música encobrindo fala')
    run(['blender','-b',out/f"episodio_{story['episode']}_final.blend",'-t','1','--python-exit-code','1',
         '--python',ROOT/'producao/serie/qa_cena.py','--',out,'final'],out/'scene-qa.log')
    report=dict(completed=True,duration=t['duration'],frames=t['frames'],
        speech_count=len(measured),render_width=width,export_width=1920,loudness=loudness,
        full_decode='passed',black_and_freeze_detection='passed',sha256=sha(video))
    print('CANDIDATE_VERIFIED',video,flush=True)
    return report
