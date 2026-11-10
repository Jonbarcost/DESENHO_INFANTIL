"""Package source and validated deliverables; omit venvs, models and bulky PNG frames."""
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        while chunk:=f.read(1024*1024):h.update(chunk)
    return h.hexdigest()


def main():
    out=ROOT/'EPISODIO_02/ARTEFATOS';movie=out/'episodio_02_final.mp4'
    validation=json.loads((out/'validation.json').read_text(encoding='utf-8'))
    if not validation.get('completed') or sha(movie)!=validation['sha256']:
        raise ValueError('Somente uma entrega validada pode ser empacotada')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip():
        raise RuntimeError('Registre os scripts/documentação antes de empacotar a versão revisada')
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    files={ROOT/p for p in tracked if p}
    config=json.loads((out/'render-config.json').read_text(encoding='utf-8'))
    files.update(ROOT/p for p in config['files'])
    for name in ('episodio_02_final.mp4','episodio_02_final.blend','timeline.json','shots.json',
                 'render-config.json','validation.json','voice-provider.json','master.wav',
                 'musica_original.wav','efeitos_natureza.wav','dialogos.wav','legendas.srt',
                 'lip-sync-validation.json','motion-report.json','scene-qa.json','audio-report.json',
                 'storyboard-final.jpg','estimate.json'):
        p=out/name
        if p.is_file():files.add(p)
    timeline=json.loads((out/'timeline.json').read_text(encoding='utf-8'))
    for clip in timeline['dialogue']:
        p=ROOT/clip['path'];files.add(p)
        for suffix in ('.json','.source.wav'):
            if p.with_suffix(suffix).is_file():files.add(p.with_suffix(suffix))
    for name in ('episodio_01_final.mp4','episodio_01_final.blend','validation.json'):
        p=ROOT/'build/episodio_01'/name
        if p.is_file():files.add(p)
    dest=ROOT/'build/Clareira_Episodio02_Windows.zip';tmp=dest.with_suffix('.partial.zip')
    manifest=[]
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=4,allowZip64=True) as z:
        for p in sorted(files):
            rel=p.relative_to(ROOT).as_posix();z.write(p,rel)
            manifest.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha(p)))
        z.writestr('CONTEUDO_PORTATIL.json',json.dumps(dict(
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
            final_video_sha256=validation['sha256'],files=manifest,
            omitted='Venvs, modelos baixáveis e sequência PNG. Os originais transferidos permanecem protegidos.'
        ),ensure_ascii=False,indent=2))
    os.replace(tmp,dest)
    dest.with_suffix('.zip.sha256').write_text(f'{sha(dest)}  {dest.name}\n',encoding='utf-8')
    print('PORTABLE_PACKAGE',dest,len(files),dest.stat().st_size,flush=True)


if __name__=='__main__':main()
