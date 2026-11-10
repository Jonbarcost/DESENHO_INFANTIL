"""Real FFmpeg fixture: tests encoding/paths/transitions, never an episode delivery."""
import shutil
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np
from PIL import Image,ImageDraw

from producao.serie.pipeline import assemble
from producao.timeline import probe

ROOT=Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg necessário')
class EncodingIntegrationTests(unittest.TestCase):
    def test_real_encoder_produces_only_candidate_with_audio_subtitles_and_transitions(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as d:
            out=Path(d);(out/'frames').mkdir()
            for i in range(1,49):
                im=Image.new('RGB',(160,90),(90,160,110))
                ImageDraw.Draw(im).rectangle((i,25,i+20,50),fill=(40,80,230))
                im.save(out/'frames'/f'{i:04}.png')
            rate=44100;t=np.arange(rate*4)/rate
            with wave.open(str(out/'master.wav'),'wb') as w:
                w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
                w.writeframes((np.sin(t*2*np.pi*440)*3000).astype('<i2').tobytes())
            (out/'legendas.srt').write_text('1\n00:00:00,500 --> 00:00:03,500\nTESTE AUTOMÁTICO\n',encoding='utf-8')
            timeline={'provisional':False,'dialogue':[{'path':'synthetic-fixture'}],
                      'frames':48,'fps':12,'duration':4,'scenes':[{'start':0},{'start':2}]}
            assemble({'episode':'teste_encoder','series':'Teste de montagem','title':'Fixture automática'},out,timeline,160)
            video=out/'episodio_teste_encoder_candidate.mp4'
            self.assertTrue(video.is_file())
            self.assertFalse((out/'episodio_teste_encoder_final.mp4').exists())
            info=probe(video);v=next(s for s in info['streams'] if s['codec_type']=='video')
            self.assertEqual((v['width'],v['height'],int(v['nb_frames'])),(1920,1080,48))
            self.assertEqual({s['codec_type'] for s in info['streams']},{'video','audio','subtitle'})
            result=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr.decode())
