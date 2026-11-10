import json,tempfile,unittest
from pathlib import Path
class ProjectGate(unittest.TestCase):
 def test_interrupted_zip_is_rejected_before_upload(self):
  from EPISODIO_04.disponibilizar_download import check_project
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);target=out/'broken.zip';target.write_bytes(b'PK incomplete')
   (out/'project-validation.json').write_text(json.dumps(dict(completed=True,source_sha256='approved',sha256='wrong')))
   with self.assertRaises((ValueError,AssertionError)):check_project(out,dict(sha256='approved'),target)
if __name__=='__main__':unittest.main()
