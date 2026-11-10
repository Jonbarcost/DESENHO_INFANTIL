"""Portable editable project bundle, excluding duplicate mixes and rendered PNGs."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'EPISODIO_03/ARTEFATOS';qa=json.loads((out/'validation.json').read_text());video=out/'episodio_03_final.mp4'
 assert qa['completed'] and hashlib.sha256(video.read_bytes()).hexdigest()==qa['sha256']
 files={ROOT/p for p in subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()}
 names=['episodio_03_final.blend','timeline.json','shots.json','legendas.srt','musica_original.wav','efeitos_natureza.wav','audio-report.json','voice-provider.json','validation.json','lip-sync-validation.json','motion-report.json','scene-qa.json','leaf-framing-validation.json']
 required={out/n for n in names}
 timeline=json.loads((out/'timeline.json').read_text())
 for clip in timeline['dialogue']:
  voice=ROOT/clip['path'];required.update((voice,voice.with_suffix('.json')))
 missing=[str(p) for p in required if not p.is_file()]
 if missing:raise FileNotFoundError('Recursos obrigatórios ausentes: '+str(missing))
 files.update(required)
 target=ROOT/'build/Clareira_Episodio03_Projeto.zip'
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(files):
   if not p.is_file():raise FileNotFoundError(p)
   z.write(p,p.relative_to(ROOT))
  z.writestr('ABRIR_PROJETO.txt','Abra EPISODIO_03/ARTEFATOS/episodio_03_final.blend no Blender 4.3.2. Para produzir novamente: EPISODIO_03\\produzir_windows.cmd --output EPISODIO_03/RENDER_WINDOWS. Inclui cena, vozes, música e efeitos. MP4 é entregue separadamente. Modelos TTS gratuitos são baixados e verificados pelo lançador. Masters e PNGs são regenerados; não estão duplicados neste pacote.\n')
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  assert {p.relative_to(ROOT).as_posix() for p in required}.issubset(z.namelist())
 print('PROJECT_ZIP',target.stat().st_size,hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=='__main__':main()
