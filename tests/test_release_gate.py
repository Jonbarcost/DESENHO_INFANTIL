import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from producao.serie.pipeline import promote_verified,generate_voices


class ReleaseGateTests(unittest.TestCase):
    def test_candidate_is_never_final_without_matching_validation(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);story={'episode':'02'}
            candidate=out/'episodio_02_candidate.mp4';candidate.write_bytes(b'candidate')
            report={'completed':False,'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest()}
            with self.assertRaises(ValueError):promote_verified(story,out,report)
            self.assertFalse((out/'episodio_02_final.mp4').exists())
            report['completed']=True;report['sha256']='wrong'
            with self.assertRaises(ValueError):promote_verified(story,out,report)
            self.assertTrue(candidate.exists())
            report['sha256']=hashlib.sha256(candidate.read_bytes()).hexdigest()
            promote_verified(story,out,report)
            self.assertEqual((out/'episodio_02_final.mp4').read_bytes(),b'candidate')
            self.assertTrue(json.loads((out/'validation.json').read_text())['completed'])

    def test_prepared_production_rejects_provider_change_before_generation(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);saved=out/'voice-provider.json'
            saved.write_text('{"backend":"kokoro"}');(out/'render-config.json').write_text('{}')
            with self.assertRaisesRegex(RuntimeError,'provedor'):
                generate_voices(Path('unused'),Path('unused'),out,'edge')
            self.assertEqual(json.loads(saved.read_text())['backend'],'kokoro')
            self.assertFalse((out/'VOZES').exists())
