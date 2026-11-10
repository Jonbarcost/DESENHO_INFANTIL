import hashlib
import json
import math
from pathlib import Path


def load_story(path):
    s=json.loads(Path(path).read_text())
    if s.get('schema_version')!=1:raise ValueError('Schema de roteiro desconhecido')
    if not s.get('scenes') or not s.get('voices'):raise ValueError('Roteiro sem cenas/vozes')
    ids=set()
    for scene in s['scenes']:
        if not scene.get('dialogue'):raise ValueError('Cena sem diálogos')
        for line in scene['dialogue']:
            if line['id'] in ids:raise ValueError('ID de fala duplicado')
            ids.add(line['id'])
            if not line['text'].strip() or line['speaker'] not in s['voices']:
                raise ValueError('Texto/personagem inválido')
            if '/' in line['id'] or '\\' in line['id'] or '..' in line['id']:
                raise ValueError('ID de fala inválido')
    return s


def voice_signature(line,profile):
    data=dict(text=line['text'],profile=profile,client=profile.get('client','edge-tts-7.2.7'))
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def make_timeline(story,voices,draft=False):
    dialogue=[];scenes=[];cursor=0;fps=story['fps']
    for source in story['scenes']:
        start=cursor;cursor+=1.4
        for line in source['dialogue']:
            data=voices.get(line['id'])
            if data is None:
                if not draft:raise FileNotFoundError(f"Fala ausente: {line['id']}")
                duration=max(1.7,len(line['text'].split())/2.8)
                data=dict(path=None,envelope=[])
            else:duration=float(data['duration'])
            if not math.isfinite(duration) or duration<=0:raise ValueError('Duração inválida')
            dialogue.append(dict(**line,scene=source['id'],start=round(cursor,4),
                                 end=round(cursor+duration,4),path=data['path'],
                                 envelope=data.get('envelope',[])))
            cursor+=duration+max(.6,line.get('pause_after',.65))
        cursor=max(cursor+1.0,start+source['min_duration'])
        cursor=math.ceil(cursor*fps)/fps
        scenes.append(dict(id=source['id'],title=source['title'],mode=source['mode'],
                           start=start,end=cursor))
    frames=round(cursor*fps)
    low,high=story['target_duration']
    if not low<=cursor<=high:raise ValueError(f'Duração {cursor:.2f}s fora da meta {low}–{high}s')
    return dict(episode=story['episode'],title=story['title'],fps=fps,frames=frames,
                duration=frames/fps,provisional=draft,dialogue=dialogue,scenes=scenes)


def require_final(timeline):
    if timeline.get('provisional') or any(not l.get('path') for l in timeline['dialogue']):
        raise ValueError('Layout provisório/vozes ausentes: não pode ser exportado como episódio final')
