"""Episode 03 editorial and preservation contracts."""
import json,unittest
from pathlib import Path
from producao.serie.historia import load_story,make_timeline
ROOT=Path(__file__).resolve().parents[1]
class Riacho(unittest.TestCase):
 def test_story_education_and_safety(self):
  s=load_story(ROOT/'EPISODIO_03/ROTEIRO/roteiro.json');self.assertEqual(s['episode'],'03')
  self.assertEqual(len(s['scenes']),7);self.assertEqual(set(s['voices']),{'CAPI','TECO','MAYA','NARRADORA'})
  text=' '.join(c['text'] for sc in s['scenes'] for c in sc['dialogue'])
  for fact in ['gravidade','potável','raízes','micróbios','sem entrar','não toque','não transforma']:self.assertIn(fact,text)
  t=make_timeline(s,{},True);self.assertTrue(180<=t['duration']<=300)
 def test_previous_production_preserved(self):
  import hashlib
  expected=json.loads((ROOT/'EPISODIO_03/RELATORIOS/preservacao-inicial.json').read_text())
  for p,h in expected.items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)
 def test_episode_two_destination_rejected_before_writes(self):
  import subprocess,hashlib
  target=ROOT/'EPISODIO_02/ARTEFATOS/timeline_planejamento.json'
  before=hashlib.sha256(target.read_bytes()).hexdigest()
  result=subprocess.run(['python','-m','producao.riacho',str(ROOT/'EPISODIO_03/ROTEIRO/roteiro.json'),'--stage','layout','--output',str(target.parent)],cwd=ROOT,capture_output=True,text=True)
  self.assertNotEqual(result.returncode,0);self.assertIn('Saída protegida',result.stderr)
  self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),before)
 def test_equals_destination_and_old_story_rejected(self):
  import subprocess
  for args in [['EPISODIO_03/ROTEIRO/roteiro.json','--output=EPISODIO_02/ARTEFATOS'],['EPISODIO_02/ROTEIRO/roteiro.json']]:
   result=subprocess.run(['python','-m','producao.riacho',*args,'--stage','layout'],cwd=ROOT,capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertTrue('protegida' in result.stderr or 'somente o Episódio 03' in result.stderr)
 def test_import_has_no_pipeline_side_effects(self):
  from producao.serie import pipeline
  run=pipeline.run
  from producao.riacho import pipeline as adapter
  self.assertIs(pipeline.run,run)
if __name__=='__main__':unittest.main()
