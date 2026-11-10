"""One Windows command, no execution-policy bypass, paid API or disabled TLS."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import venv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from producao.serie.local_voice import CHECKSUMS


def run(args,env):subprocess.run(list(map(str,args)),check=True,cwd=ROOT,env=env)


def ensure_tool(name,roots):
    current=shutil.which(name)
    if current:return Path(current)
    for root in roots:
        if root.is_dir():
            candidates=sorted(root.rglob(name+'.exe'),reverse=True)
            if candidates:return candidates[0]
    raise RuntimeError(f'Instale {name} e inclua sua pasta no PATH antes de executar este comando.')


def download_model(name,dest):
    if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest()==CHECKSUMS[name]:return
    dest.parent.mkdir(parents=True,exist_ok=True)
    url='https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/'+name
    tmp=dest.with_suffix(dest.suffix+'.partial')
    digest=hashlib.sha256()
    # urllib retains standard certificate verification and configured HTTPS proxies.
    with urllib.request.urlopen(url,timeout=90) as response,open(tmp,'wb') as output:
        while chunk:=response.read(1024*1024):output.write(chunk);digest.update(chunk)
    if digest.hexdigest()!=CHECKSUMS[name]:raise ValueError(f'Checksum publicado não confere: {name}')
    os.replace(tmp,dest)


def windows_preservation():
    expected=json.loads((ROOT/'EPISODIO_02/RELATORIOS/preservacao-inicial.json').read_text(encoding='utf-8'))
    target=ROOT/'EPISODIO_02/ARTEFATOS/preservacao-windows.json'
    if target.exists():return target
    available={};missing=[]
    for relative,sha in expected.items():
        p=ROOT/relative
        if p.exists():
            if hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
                raise RuntimeError(f'Arquivo anterior difere do inventário: {relative}. Transfira o projeto sem converter finais de linha.')
            available[relative]=sha
        elif relative.startswith('build/episodio_01/'):
            missing.append(relative)  # Generated files may not have been transferred to this machine.
        else:raise FileNotFoundError(f'Recurso original obrigatório ausente: {relative}')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(available,indent=2),encoding='utf-8')
    target.with_name('nao-transferidos-episodio01.json').write_text(json.dumps(missing,indent=2),encoding='utf-8')
    return target


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tts',choices=['auto','edge','kokoro'],default='kokoro')
    p.add_argument('--width',choices=[1280,1920],type=int,default=1920)
    p.add_argument('--output',type=Path,default=Path('EPISODIO_02/ARTEFATOS'))
    a=p.parse_args()
    if os.name!='nt':raise RuntimeError('Este lançador destina-se ao Windows; no Linux use python3 -m producao.serie.')
    out=(ROOT/a.output).resolve();final=out/'episodio_02_final.mp4'
    if ROOT not in out.parents or any(out==p or p in out.parents for p in (ROOT/'EPISODIO_01',ROOT/'build/episodio_01')):
        raise ValueError('Use uma pasta nova do Episódio 02 dentro do projeto.')
    if final.exists() and (out/'validation.json').exists() and (out/'render-config.json').exists():
        report=json.loads((out/'validation.json').read_text(encoding='utf-8'))
        config=json.loads((out/'render-config.json').read_text(encoding='utf-8'))
        provider=json.loads((out/'voice-provider.json').read_text(encoding='utf-8'))['backend']
        same_inputs=all((ROOT/p).exists() and hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
                        for p,h in config['files'].items())
        if (report.get('completed') and report.get('sha256')==hashlib.sha256(final.read_bytes()).hexdigest()
            and same_inputs and config['width']==a.width and a.tts in ('auto',provider)):
            print('MP4 previamente validado; hash e recursos conferem. Nenhuma etapa refeita:',final)
            return
    env={**os.environ,'PYTHONUTF8':'1'}
    programs=Path(os.environ.get('PROGRAMFILES',r'C:\Program Files'))
    blender=ensure_tool('blender',[programs/'Blender Foundation',ROOT/'BLENDER'])
    ffmpeg=ensure_tool('ffmpeg',[ROOT/'ffmpeg',programs/'ffmpeg'])
    ffprobe=ensure_tool('ffprobe',[ffmpeg.parent,ROOT/'ffmpeg'])
    env['PATH']=os.pathsep.join([str(blender.parent),str(ffmpeg.parent),str(ffprobe.parent),env.get('PATH','')])
    version=subprocess.check_output([str(blender),'--version'],env=env).decode().splitlines()[0]
    if not version.startswith('Blender 4.3.'):
        raise RuntimeError('Este builder foi validado com Blender 4.3.x. Instale Blender 4.3.2 ou aponte o PATH para essa versão.')
    folder=ROOT/'build/venv-windows';python=folder/'Scripts/python.exe'
    if not python.exists():venv.EnvBuilder(with_pip=True).create(folder)
    reqs=[ROOT/'producao/serie/requirements.txt',ROOT/'producao/serie/requirements-local.txt']
    signature=hashlib.sha256(b''.join(r.read_bytes() for r in reqs)).hexdigest();marker=folder/'requirements.sha256'
    if not marker.exists() or marker.read_text()!=signature:
        run([python,'-m','pip','install','-r',reqs[0],'-r',reqs[1]],env)
        marker.write_text(signature)
    if a.tts!='edge':
        for name in CHECKSUMS:download_model(name,ROOT/'build/tts-models'/name)
    manifest=windows_preservation()
    run([python,'-m','producao.serie','EPISODIO_02/ROTEIRO/roteiro.json',
         '--tts',a.tts,'--width',a.width,'--output',out,'--preservation-manifest',manifest],env)


if __name__=='__main__':
    try:main()
    except Exception as exc:print('ERRO:',str(exc),file=sys.stderr);raise SystemExit(1)
