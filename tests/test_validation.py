import json
import tempfile
import unittest
from pathlib import Path

from producao.pipeline import validate_loudness, prepared_manifest, require_config


class ExportValidationTests(unittest.TestCase):
    def test_true_peak_and_loudness_are_acceptance_checks(self):
        def log(i,tp):
            return 'ffmpeg header\n'+json.dumps(dict(input_i=str(i),input_tp=str(tp),input_lra='6.9'))
        self.assertEqual(validate_loudness(log(-16.68,-1.5))['input_tp'],'-1.5')
        for i,tp in [(-16,.3),(-25,-3),(-7,-1.5),('-inf',-4),(-16,'nan')]:
            with self.subTest(i=i,tp=tp):
                with self.assertRaises(ValueError):validate_loudness(log(i,tp))
        with self.assertRaises(ValueError):validate_loudness('no measurement')

    def test_resume_rejects_manually_edited_scene_and_timeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);config={'width':1920}
            (out/'episodio_01_final.blend').write_bytes(b'prepared scene')
            (out/'timeline.json').write_text('{}')
            manifest=prepared_manifest(out,config)
            (out/'render-config.json').write_text(json.dumps(manifest))
            require_config(out,config)
            (out/'episodio_01_final.blend').write_bytes(b'edited scene')
            with self.assertRaises(RuntimeError):require_config(out,config)
            (out/'episodio_01_final.blend').write_bytes(b'prepared scene')
            (out/'timeline.json').write_text('{"changed":true}')
            with self.assertRaises(RuntimeError):require_config(out,config)
