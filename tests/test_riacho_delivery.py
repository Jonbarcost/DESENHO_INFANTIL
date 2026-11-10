import hashlib,json,tempfile,unittest
from pathlib import Path
from EPISODIO_03.disponibilizar_download import check_light
class Delivery(unittest.TestCase):
 def fixture(self,out):
  (out/'episodio_03_leve.mp4').write_bytes(b'unit fixture; not media')
  qa=dict(sha256='source',frames=120,duration=10)
  report=dict(completed=True,full_decode='passed',audio_identical=True,source_sha256='source',sha256=hashlib.sha256((out/'episodio_03_leve.mp4').read_bytes()).hexdigest(),width=1280,height=720,frames=120,duration=10)
  return qa,report
 def test_mobile_copy_bound_to_source_and_exact_bytes(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);qa,r=self.fixture(out);(out/'leve-validation.json').write_text(json.dumps(r));check_light(out,qa)
   (out/'episodio_03_leve.mp4').write_bytes(b'altered')
   with self.assertRaises(AssertionError):check_light(out,qa)
 def test_wrong_source_or_unverified_copy_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);qa,r=self.fixture(out)
   for key,value in [('source_sha256','other'),('full_decode','failed'),('audio_identical',False),('width',1920),('duration',1)]:
    broken={**r,key:value};(out/'leve-validation.json').write_text(json.dumps(broken))
    with self.assertRaises(AssertionError):check_light(out,qa)
if __name__=='__main__':unittest.main()
