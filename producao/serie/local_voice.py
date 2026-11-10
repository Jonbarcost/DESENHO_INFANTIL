"""Offline Brazilian Portuguese neural voices, from checksum-verified public releases."""
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path

from .historia import voice_signature
from .vozes import cache_valid

CHECKSUMS={
 'kokoro-v1.0.int8.onnx':'ae315a79b623f244700e4afb9246c46a26066782e049ba174bf3ba433970ee9c',
 'voices-v1.0.bin':'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d',
}
PROFILES={'CAPI':('pm_alex',1.12,1.2),'TECO':('pm_santa',1.22,2.6),
          'MAYA':('pf_dora',1.08,1.8),'NARRADORA':('pf_dora',1.05,.4)}


def local_profile(speaker,reference=None):
    voice,speed,pitch=PROFILES[speaker]
    if reference:speed=1+float(reference['rate'].rstrip('%'))/100
    return dict(provider='kokoro',client='kokoro-onnx-0.6.1',voice=voice,speed=speed,
                pitch_semitones=pitch,language='pt-br',reference=reference,
                model_sha256=CHECKSUMS['kokoro-v1.0.int8.onnx'],
                voices_sha256=CHECKSUMS['voices-v1.0.bin'])


def verify_models(folder):
    for name,expected in CHECKSUMS.items():
        path=Path(folder)/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError(f'Modelo ausente ou checksum inválido: {name}')


def generate_local(story,folder,models):
    import numpy as np
    import soundfile as sf
    import onnxruntime as ort
    from kokoro_onnx import Kokoro
    from producao.timeline import probe
    verify_models(models)
    options=ort.SessionOptions();options.intra_op_num_threads=4;options.inter_op_num_threads=1
    options.log_severity_level=3
    session=ort.InferenceSession(str(Path(models)/'kokoro-v1.0.int8.onnx'),sess_options=options,
                                providers=['CPUExecutionProvider'])
    kokoro=Kokoro.from_session(session,str(Path(models)/'voices-v1.0.bin'))
    filters=subprocess.check_output(['ffmpeg','-hide_banner','-filters'],stderr=subprocess.DEVNULL).decode()
    rubberband='rubberband' in filters
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    for sc in story['scenes']:
        for line in sc['dialogue']:
            profile=local_profile(line['speaker'],story['voices'][line['speaker']])
            path=folder/(line['id']+'.mp3')
            if cache_valid(path,line,profile):continue
            samples,rate=kokoro.create(line['text'],voice=profile['voice'],speed=profile['speed'],lang='pt-br')
            if len(samples)<rate*.2 or not np.isfinite(samples).all() or np.sqrt(np.mean(samples**2))<.002:
                raise ValueError(f'Síntese vazia/inválida: {line["id"]}')
            wav=path.with_suffix('.source.wav');tmp=path.with_suffix('.partial.mp3')
            sf.write(wav,samples,rate,subtype='PCM_16')
            pitch=2**(profile['pitch_semitones']/12)
            effect=f'rubberband=pitch={pitch:.8f}' if rubberband else f'asetrate={rate*pitch:.6f},aresample={rate},atempo={1/pitch:.8f}'
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),
                            '-af',effect,
                            '-ac','1','-ar','48000','-c:a','libmp3lame','-b:a','128k',str(tmp)],check=True)
            duration=float(probe(tmp)['format']['duration'])
            sha=hashlib.sha256(tmp.read_bytes()).hexdigest();os.replace(tmp,path)
            path.with_suffix('.json').write_text(json.dumps(dict(signature=voice_signature(line,profile),
                sha256=sha,duration=duration,profile=profile,exact_microsoft_voice=False),indent=2))
            print('LOCAL_VOICE_READY',line['id'],round(duration,3),flush=True)


if __name__=='__main__':
    import argparse
    from .historia import load_story
    p=argparse.ArgumentParser();p.add_argument('story',type=Path);p.add_argument('folder',type=Path);p.add_argument('models',type=Path)
    a=p.parse_args();generate_local(load_story(a.story),a.folder,a.models)
