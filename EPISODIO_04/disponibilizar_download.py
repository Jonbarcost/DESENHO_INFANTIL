"""Publish reviewed downloads to a dedicated GitHub branch; never uploads to YouTube."""
import hashlib,json,os,subprocess,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def git(*args,env=None,data=None):return subprocess.check_output(['git',*map(str,args)],cwd=ROOT,env=env,input=data).decode().strip()
def check_light(out,qa):
 light=json.loads((out/'leve-validation.json').read_text())
 assert (light.get('completed') and light.get('full_decode')=='passed' and light.get('audio_identical') is True
         and light.get('source_sha256')==qa['sha256'] and light.get('sha256')==hashlib.sha256((out/'episodio_04_leve.mp4').read_bytes()).hexdigest()
         and (light.get('width'),light.get('height'))==(1280,720)
         and light.get('frames')==qa['frames'] and abs(light['duration']-qa['duration'])<.1),'Versão leve sem validação correspondente'
def check_project(out,qa,target):
 report=json.loads((out/'project-validation.json').read_text())
 if not(report.get('completed') and report.get('source_sha256')==qa['sha256'] and report.get('sha256')==hashlib.sha256(target.read_bytes()).hexdigest() and report.get('crc')=='passed'):
  raise ValueError('ZIP sem validação correspondente')
 with zipfile.ZipFile(target) as z:
  if z.testzip() is not None:raise ValueError('ZIP corrompido')
  required={'EPISODIO_04/ARTEFATOS/episodio_04_final.blend','EPISODIO_04/ROTEIRO/roteiro.json','EPISODIO_04/ASSETS/flores_reutilizadas.blend','EPISODIO_04/ASSETS/riacho_reutilizado.blend','producao/gotinha/cena.py','EPISODIO_04/produzir_windows.cmd'}
  for clip in json.loads((out/'timeline.json').read_text())['dialogue']:required.update((clip['path'],str(Path(clip['path']).with_suffix('.json')).replace(chr(92),'/')))
  if not required.issubset(z.namelist()):raise ValueError('ZIP sem recursos obrigatórios')
def main():
 out=ROOT/'EPISODIO_04/ARTEFATOS';qa=json.loads((ROOT/'EPISODIO_04/RELATORIOS/validacao-final.json').read_text())
 files={'episodio_04_final.mp4':out/'episodio_04_final.mp4','episodio_04_leve.mp4':out/'episodio_04_leve.mp4','Clareira_Episodio04_Projeto.zip':ROOT/'build/Clareira_Episodio04_Projeto.zip'}
 assert qa['completed'] and hashlib.sha256(files['episodio_04_final.mp4'].read_bytes()).hexdigest()==qa['sha256']
 check_light(out,qa)
 check_project(out,qa,files['Clareira_Episodio04_Projeto.zip'])
 checksums={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()}
 assert all(p.stat().st_size<100*2**20 for p in files.values()),'Arquivo supera limite de blob do GitHub'
 branch='entrega-episodio-04'
 existing=git('ls-remote','--heads','origin',branch)
 if existing:raise RuntimeError('Branch de entrega já existe; preserve-a e revise uma nova versão explicitamente')
 with tempfile.TemporaryDirectory() as tmp:
  readme=Path(tmp)/'README.md'
  readme.write_text('# Episódio 04 — A Viagem da Gotinha\n\nClareira dos Curiosos. Animação educativa em português brasileiro, 4m27s, 42 falas. Sem publicação no YouTube.\n\n'+''.join(f'- [{n}](https://github.com/Jonbarcost/DESENHO_INFANTIL/raw/refs/heads/{branch}/{n}) — {p.stat().st_size/2**20:.1f} MiB\n' for n,p in files.items())+'\nO ZIP contém cena Blender, roteiro, vozes, música, efeitos e scripts. MP4 entregue separadamente. Versão leve: 720p; principal: 1080p nativos.\n\n## SHA-256\n\n'+''.join(f'`{h}` {n}\n\n' for n,h in checksums.items()))
  files['README.md']=readme;env={**os.environ,'GIT_INDEX_FILE':str(Path(tmp)/'index')}
  git('read-tree','--empty',env=env)
  for n,p in files.items():
   obj=git('hash-object','-w',p);git('update-index','--add','--cacheinfo',f'100644,{obj},{n}',env=env)
  tree=git('write-tree',env=env);commit=git('commit-tree',tree,'-m','Deliver validated educational Episode 04')
  subprocess.run(['git','push','origin',commit+':refs/heads/'+branch],cwd=ROOT,check=True)
 record=dict(branch=branch,commit=commit,sha256=checksums,urls={n:f'https://github.com/Jonbarcost/DESENHO_INFANTIL/raw/refs/heads/{branch}/{n}' for n in checksums})
 (ROOT/'EPISODIO_04/RELATORIOS/downloads.json').write_text(json.dumps(record,indent=2));print('DOWNLOADS_PUSHED',commit)
if __name__=='__main__':main()
