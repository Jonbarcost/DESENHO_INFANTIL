"""Make and validate a mobile copy derived from the approved 1080p movie."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from producao.timeline import probe

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'EPISODIO_04/ARTEFATOS';source=out/'episodio_04_final.mp4';report=json.loads((out/'validation.json').read_text())
 assert report['completed'] and sha(source)==report['sha256']
 target=out/'episodio_04_leve.mp4';tmp=out/'episodio_04_leve.partial.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-map','0:v:0','-map','0:a:0','-map','0:s?',
                 '-vf','scale=1280:720:flags=lanczos','-c:v','libx264','-crf','25','-preset','fast','-threads','4',
                 '-pix_fmt','yuv420p','-c:a','copy','-c:s','mov_text','-movflags','+faststart',str(tmp)],check=True)
 info=probe(tmp);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
 assert (v['width'],v['height'],v['codec_name'],a['codec_name'])==(1280,720,'h264','aac')
 assert int(v['nb_frames'])==report['frames'] and abs(float(info['format']['duration'])-report['duration'])<.1
 subprocess.run(['ffmpeg','-v','error','-i',str(tmp),'-map','0:v','-map','0:a','-f','null','-'],check=True)
 def audio_digest(path):
  return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a','-c:a','copy','-f','adts','-'])).hexdigest()
 assert audio_digest(source)==audio_digest(tmp),'Áudio da cópia difere da mixagem aprovada'
 assert sha(source)==report['sha256'];os.replace(tmp,target)
 result=dict(completed=True,sha256=sha(target),source_sha256=report['sha256'],width=1280,height=720,duration=float(info['format']['duration']),frames=int(v['nb_frames']),full_decode='passed',audio_identical=True)
 (out/'leve-validation.json').write_text(json.dumps(result,indent=2));print('MOBILE_COPY_VERIFIED',target.stat().st_size)
if __name__=='__main__':main()
