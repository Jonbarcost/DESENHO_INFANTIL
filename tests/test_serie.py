import copy
import json
import tempfile
import unittest
import hashlib
import subprocess
import sys
from pathlib import Path

from producao.serie.historia import load_story, make_timeline, voice_signature, require_final
from producao.serie.vozes import cache_valid

ROOT=Path(__file__).resolve().parents[1]


class SeriesTests(unittest.TestCase):
    def story(self):return load_story(ROOT/'EPISODIO_02/ROTEIRO/roteiro.json')

    def test_planning_is_not_final_and_has_seven_scenes(self):
        story=self.story();t=make_timeline(story,{},draft=True)
        self.assertEqual(len(t['scenes']),7)
        self.assertTrue(t['provisional'])
        self.assertGreaterEqual(t['duration'],180)
        self.assertLessEqual(t['duration'],300)
        with self.assertRaises(ValueError):require_final(t)

    def test_final_requires_every_voice(self):
        with self.assertRaises(FileNotFoundError):make_timeline(self.story(),{})

    def test_measured_timeline_preserves_all_lines_and_gaps(self):
        story=self.story()
        voices={line['id']:{'duration':3.7,'path':'audio.mp3','envelope':[.3]*45}
                for scene in story['scenes'] for line in scene['dialogue']}
        t=make_timeline(story,voices)
        require_final(t)
        self.assertEqual(len(t['dialogue']),len(voices))
        for a,b in zip(t['dialogue'],t['dialogue'][1:]):self.assertGreaterEqual(b['start']-a['end'],.59)

    def test_voice_signature_tracks_text_and_approved_profile(self):
        s=self.story();line=s['scenes'][0]['dialogue'][0];profile=s['voices'][line['speaker']]
        sig=voice_signature(line,profile)
        self.assertNotEqual(sig,voice_signature({**line,'text':line['text']+'!'},profile))
        self.assertNotEqual(sig,voice_signature(line,{**profile,'pitch':'+0Hz'}))

    def test_overlong_measured_speech_is_not_silently_truncated(self):
        s=self.story();voices={l['id']:{'duration':40,'path':'audio.mp3','envelope':[.1]*480}
                                  for scene in s['scenes'] for l in scene['dialogue']}
        with self.assertRaises(ValueError):make_timeline(s,voices)

    def test_duplicate_line_ids_are_rejected(self):
        s=self.story();s['scenes'][1]['dialogue'][0]['id']=s['scenes'][0]['dialogue'][0]['id']
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text(json.dumps(s))
            with self.assertRaises(ValueError):load_story(p)

    def test_voice_cache_rejects_tampering_and_profile_change(self):
        story=self.story();line=story['scenes'][0]['dialogue'][0];profile=story['voices'][line['speaker']]
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'voice.mp3';p.write_bytes((ROOT/'EPISODIO_01/VOZES/cena_01_001_narradora.mp3').read_bytes())
            meta=p.with_suffix('.json')
            meta.write_text(json.dumps(dict(signature=voice_signature(line,profile),sha256=hashlib.sha256(p.read_bytes()).hexdigest())))
            self.assertTrue(cache_valid(p,line,profile))
            self.assertFalse(cache_valid(p,line,{**profile,'rate':'+0%'}))
            p.write_bytes(p.read_bytes()+b'changed')
            self.assertFalse(cache_valid(p,line,profile))

    def test_output_cannot_be_the_episode_one_directory(self):
        original=ROOT/'EPISODIO_01/CENAS/personagens.blend'
        before=hashlib.sha256(original.read_bytes()).hexdigest()
        result=subprocess.run([sys.executable,'-m','producao.serie',str(ROOT/'EPISODIO_02/ROTEIRO/roteiro.json'),
                               '--stage','layout','--output',str(ROOT/'build/episodio_01')],capture_output=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('Saída não pode tocar'.encode(),result.stderr)
        self.assertEqual(before,hashlib.sha256(original.read_bytes()).hexdigest())

    def test_external_output_is_rejected_before_work_starts(self):
        with tempfile.TemporaryDirectory() as d:
            result=subprocess.run([sys.executable,'-m','producao.serie',str(ROOT/'EPISODIO_02/ROTEIRO/roteiro.json'),
                                   '--stage','verify','--output',d],capture_output=True)
            self.assertEqual(result.returncode,2)
            self.assertIn('dentro do repositório'.encode(),result.stderr)
            self.assertEqual(list(Path(d).iterdir()),[])

    def test_planning_music_cannot_replace_final_mix_metadata(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as d:
            out=Path(d);sentinel=b'{"dialogue_included":true,"sentinel":"final"}'
            (out/'audio-report.json').write_bytes(sentinel)
            result=subprocess.run([sys.executable,'-m','producao.serie',str(ROOT/'EPISODIO_02/ROTEIRO/roteiro.json'),
                                   '--stage','music','--output',str(out)],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr.decode())
            self.assertEqual((out/'audio-report.json').read_bytes(),sentinel)
            self.assertTrue((out/'MUSICA_PLANEJAMENTO/musica_original.wav').is_file())
