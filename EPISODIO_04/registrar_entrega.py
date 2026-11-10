"""Write delivery record only for a real, validated and independently checked MP4."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'EPISODIO_04/ARTEFATOS';reports=ROOT/'EPISODIO_04/RELATORIOS'
 movie=out/'episodio_04_final.mp4';qa=json.loads((out/'validation.json').read_text());timeline=json.loads((out/'timeline.json').read_text())
 sha=hashlib.sha256(movie.read_bytes()).hexdigest()
 assert qa['completed'] and qa['sha256']==sha
 motion=json.loads((out/'motion-report.json').read_text());lip=json.loads((out/'lip-sync-validation.json').read_text());scene=json.loads((out/'scene-qa.json').read_text())
 assert qa['independent_checks']=='passed'
 for name,h in qa['proofs'].items():
  proof=json.loads((out/name).read_text());assert hashlib.sha256((out/name).read_bytes()).hexdigest()==h and proof['video_sha256']==sha and proof['scene_sha256']==qa['scene_sha256']
 assert lip['passed'] and lip['dialogue_checks']==sum(c['speaker']!='NARRADORA' for c in timeline['dialogue']) and motion['shots']==len(json.loads((out/'shots.json').read_text())) and scene['checks']=='passed'
 subs=subprocess.check_output(['ffmpeg','-v','error','-i',str(movie),'-map','0:s:0','-f','srt','-'],text=True)
 for clip in timeline['dialogue']:assert clip['text'] in subs,clip['id']
 preservation=json.loads((reports/'preservacao-inicial.json').read_text())
 for p,h in preservation.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 record=dict(**qa,motion_shots=motion['shots'],lip_sync=lip['minimum_correlation'],subtitle_text_checks=len(timeline['dialogue']),previous_files_preserved=len(preservation),youtube_published=False)
 (reports/'validacao-final.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
 (reports/'STATUS.json').write_text(json.dumps(dict(completed=True,sha256=sha,file=movie.relative_to(ROOT).as_posix(),duration=qa['duration']),indent=2))
 (out/'status.json').write_text(json.dumps(dict(completed=True,stage='verified',sha256=sha),indent=2))
 (ROOT/'EPISODIO_04/ENTREGA.md').write_text(f'''# Episódio 04 — A Viagem da Gotinha

MP4 real validado: `{movie.relative_to(ROOT)}`. Duração {qa['duration']:.3f} s, 1920×1080 nativos, 12 fps, H.264/AAC e legendas em português. {qa['speech_count']} falas, {motion['shots']} tomadas com movimento medido, 33 falas com sincronismo de energia verificado. Decodificação integral, volume, quadros pretos e congelamentos: aprovados.

SHA-256: `{sha}`.

Cena editável, áudios individuais, música, efeitos, timeline, legendas e relatórios em ARTEFATOS. Roteiro, scripts e instruções versionados. {len(preservation)} arquivos anteriores preservados por hash. Nenhuma publicação no YouTube.

O sincronismo é aproximado pela energia das falas, sem visemas fonéticos. O supervisor adulto é mencionado na narração e permanece fora de quadro. O lançador Windows está preparado; a execução e validação desta entrega ocorreram no Linux com Blender 4.3.2.
''')
 print('DELIVERY_RECORDED',sha)
if __name__=='__main__':main()
