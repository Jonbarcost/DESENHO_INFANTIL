import unittest
import tempfile
from pathlib import Path
from producao.serie.local_voice import local_profile, verify_models
from producao.serie.historia import voice_signature


class LocalVoiceTests(unittest.TestCase):
    def test_profiles_keep_character_differences_and_provider_is_signed(self):
        capi=local_profile('CAPI');teco=local_profile('TECO')
        maya=local_profile('MAYA');narrator=local_profile('NARRADORA')
        self.assertEqual(capi['language'],'pt-br')
        self.assertGreater(teco['speed'],capi['speed'])
        self.assertGreater(teco['pitch_semitones'],capi['pitch_semitones'])
        self.assertGreater(maya['pitch_semitones'],narrator['pitch_semitones'])
        line={'text':'Bom dia!'}
        self.assertNotEqual(voice_signature(line,capi),voice_signature(line,teco))
        self.assertNotEqual(voice_signature(line,capi),voice_signature(line,{**capi,'model_sha256':'modified'}))

    def test_models_without_published_checksum_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'kokoro-v1.0.int8.onnx').write_bytes(b'corrupt model')
            (p/'voices-v1.0.bin').write_bytes(b'corrupt voices')
            with self.assertRaises(ValueError):verify_models(p)
