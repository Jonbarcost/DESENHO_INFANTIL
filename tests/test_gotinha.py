import unittest,subprocess,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class GotinhaTests(unittest.TestCase):
 def test_script_has_real_response_pauses_and_science(self):
  from producao.serie.historia import load_story,make_timeline
  story=load_story(ROOT/'EPISODIO_04/ROTEIRO/roteiro.json')
  self.assertEqual(story['episode'],'04')
  lines=[l for s in story['scenes'] for l in s['dialogue']]
  self.assertGreaterEqual(sum(l.get('pause_after',0)>=3 for l in lines),3)
  text=' '.join(l['text'] for l in lines)
  for phrase in ['invisível','evaporação','condensação','gotinhas','precipitação']:self.assertIn(phrase,text)
  self.assertTrue(180<=make_timeline(story,{},True)['duration']<=300)
 def test_previous_destinations_and_story_rejected(self):
  for episode in ('01','02','03'):
   cmd=['python','-m','producao.gotinha','EPISODIO_04/ROTEIRO/roteiro.json','--stage','layout',f'--output=EPISODIO_{episode}/ARTEFATOS']
   result=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('protegida',result.stderr)
 def test_portable_dispatch(self):
  from producao.gotinha.pipeline import adapt_command
  for name in ('cena.py','qa_cena.py'):
   self.assertEqual(adapt_command([f'C:\\Projeto\\producao\\serie\\{name}']),[str(ROOT/'producao/gotinha'/name)])
if __name__=='__main__':unittest.main()
