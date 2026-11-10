"""Publish reviewed downloads to a dedicated GitHub branch; never uploads to YouTube."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def git(*args,env=None,data=None):return subprocess.check_output(['git',*map(str,args)],cwd=ROOT,env=env,input=data).decode().strip()
def main():
 out=ROOT/'EPISODIO_03/ARTEFATOS';qa=json.loads((ROOT/'EPISODIO_03/RELATORIOS/validacao-final.json').read_text())
 files={'episodio_03_final.mp4':out/'episodio_03_final.mp4','episodio_03_leve.mp4':out/'episodio_03_leve.mp4','Clareira_Episodio03_Projeto.zip':ROOT/'build/Clareira_Episodio03_Projeto.zip'}
 assert qa['completed'] and hashlib.sha256(files['episodio_03_final.mp4'].read_bytes()).hexdigest()==qa['sha256']
 checksums={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()}
 assert all(p.stat().st_size<100*2**20 for p in files.values()),'Arquivo supera limite de blob do GitHub'
 branch='entrega-episodio-03'
 existing=git('ls-remote','--heads','origin',branch)
 if existing:raise RuntimeError('Branch de entrega já existe; preserve-a e revise uma nova versão explicitamente')
 with tempfile.TemporaryDirectory() as tmp:
  readme=Path(tmp)/'README.md'
  readme.write_text('# Episódio 03 — O Segredo do Riachinho\n\nClareira dos Curiosos. Animação educativa em português brasileiro, 4m15s, 48 falas. Sem publicação no YouTube.\n\n'+''.join(f'- [{n}](https://github.com/Jonbarcost/DESENHO_INFANTIL/raw/refs/heads/{branch}/{n}) — {p.stat().st_size/2**20:.1f} MiB\n' for n,p in files.items())+'\nO ZIP contém cena Blender, roteiro, vozes, música, efeitos e scripts. MP4 entregue separadamente. Versão leve: 720p; principal: 1080p nativos.\n\n## SHA-256\n\n'+''.join(f'`{h}` {n}\n\n' for n,h in checksums.items()))
  files['README.md']=readme;env={**os.environ,'GIT_INDEX_FILE':str(Path(tmp)/'index')}
  git('read-tree','--empty',env=env)
  for n,p in files.items():
   obj=git('hash-object','-w',p);git('update-index','--add','--cacheinfo',f'100644,{obj},{n}',env=env)
  tree=git('write-tree',env=env);commit=git('commit-tree',tree,'-m','Deliver validated educational Episode 03')
  subprocess.run(['git','push','origin',commit+':refs/heads/'+branch],cwd=ROOT,check=True)
 record=dict(branch=branch,commit=commit,sha256=checksums,urls={n:f'https://github.com/Jonbarcost/DESENHO_INFANTIL/raw/refs/heads/{branch}/{n}' for n in checksums})
 (ROOT/'EPISODIO_03/RELATORIOS/downloads.json').write_text(json.dumps(record,indent=2));print('DOWNLOADS_PUSHED',commit)
if __name__=='__main__':main()
