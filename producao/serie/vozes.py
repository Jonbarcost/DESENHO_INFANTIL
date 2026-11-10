"""Exact requested Edge voices. No offline/silent substitution; atomic signed cache."""
import asyncio
import hashlib
import json
import os
import subprocess
from pathlib import Path

from producao.timeline import probe
from .historia import voice_signature


def cache_valid(path,line,profile):
    meta=path.with_suffix('.json')
    try:
        info=json.loads(meta.read_text())
        return (info['signature']==voice_signature(line,profile) and
                info['sha256']==hashlib.sha256(path.read_bytes()).hexdigest() and
                float(probe(path)['format']['duration'])>0)
    except (OSError,ValueError,KeyError,subprocess.CalledProcessError):return False


async def generate(story,folder):
    import edge_tts
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    for scene in story['scenes']:
        for line in scene['dialogue']:
            profile=story['voices'][line['speaker']]
            path=folder/(line['id']+'.mp3')
            if cache_valid(path,line,profile):continue
            tmp=path.with_suffix('.partial.mp3')
            # Keep known valid audio while a refresh is incomplete or denied.
            try:
                c=edge_tts.Communicate(text=line['text'],**profile,
                                       proxy=os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy'))
                await asyncio.wait_for(c.save(str(tmp)),timeout=60)
                duration=float(probe(tmp)['format']['duration'])
                if duration<=0:raise ValueError('Serviço retornou fala vazia')
                sha=hashlib.sha256(tmp.read_bytes()).hexdigest()
                os.replace(tmp,path)
                path.with_suffix('.json').write_text(json.dumps(dict(signature=voice_signature(line,profile),
                    sha256=sha,duration=duration,profile=profile),indent=2))
                print('VOICE_READY',line['id'],duration,flush=True)
            except Exception as exc:
                # Do not log full service URLs, proxy credentials or auth headers.
                raise RuntimeError(f"Geração de voz bloqueada para {line['id']}: {type(exc).__name__}; "
                                   f"HTTP {getattr(exc,'status','n/a')}. Verifique acesso a speech.platform.bing.com") from None


def collect(story,folder,root):
    from producao.som import decode
    import numpy as np
    from producao.som import RATE
    result={}
    for scene in story['scenes']:
        for line in scene['dialogue']:
            path=Path(folder)/(line['id']+'.mp3')
            if not cache_valid(path,line,story['voices'][line['speaker']]):
                raise FileNotFoundError(f'Áudio ausente ou cache inválido: {path}')
            samples=decode(path);block=round(RATE/story['fps'])
            values=[float(np.sqrt(np.mean(samples[j:j+block]**2))) for j in range(0,len(samples),block)]
            peak=max(values) or 1
            result[line['id']]=dict(path=str(path.relative_to(root)),
                                   duration=float(probe(path)['format']['duration']),
                                   envelope=[round(v/peak,4) for v in values])
    return result


if __name__=='__main__':
    import argparse
    from .historia import load_story
    p=argparse.ArgumentParser();p.add_argument('story',type=Path);p.add_argument('folder',type=Path)
    args=p.parse_args();asyncio.run(generate(load_story(args.story),args.folder))
