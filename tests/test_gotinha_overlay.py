"""Real FFmpeg canary for the Episode 04 educational overlays; never a delivery movie."""
import json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
from producao.serie import pipeline as core,audio,qualidade
from producao.gotinha import pipeline as episode
ROOT=Path(__file__).resolve().parents[1]
class OverlayIntegration(unittest.TestCase):
 def test_actual_episode_adapter_encodes_visible_science_and_turn_labels(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'build') as folder:
   out=Path(folder);frame=out/'fixture.png';Image.new('RGB',(160,90),'black').save(frame)
   (out/'timeline.json').write_text(json.dumps(dict(scenes=[dict(mode='discovery',start=0),dict(mode='garden',end=4)],dialogue=[dict(end=0,pause_after=3)])))
   movie=out/'episodio_04_final.partial.mp4'
   def canary():
    core.run(['ffmpeg','-v','error','-y','-loop','1','-i',frame,'-vf','scale=1920:1080','-frames:v','1','-c:v','libx264','-threads','2','-pix_fmt','yuv420p',movie],out/'encode.log')
   argv=['test',str(ROOT/'EPISODIO_04/ROTEIRO/roteiro.json'),'--output',str(out),'--stage','assemble']
   with patch.object(sys,'argv',argv),patch.object(core,'main',canary),patch.object(core,'run',core.run),patch.object(core,'fingerprint',core.fingerprint),patch.object(audio,'compose',audio.compose),patch.object(qualidade,'verify',qualidade.verify),patch.dict(os.environ,{'LP_NUM_THREADS':'4'}):episode.main()
   data=subprocess.check_output(['ffmpeg','-v','error','-i',str(movie),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
   image=np.frombuffer(data,dtype=np.uint8).reshape(1080,1920,3)
   white=np.all(image>200,axis=2);yellow=(image[:,:,0]>170)&(image[:,:,1]>170)&(image[:,:,2]<140)
   self.assertGreater(int(white[900:1050].sum()),500,'Aviso científico ausente')
   self.assertGreater(int(yellow[:200].sum()),150,'Convite de participação ausente')
if __name__=='__main__':unittest.main()
