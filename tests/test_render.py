import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from producao.render import valid_png


class ResumeTests(unittest.TestCase):
    def png(self):
        def chunk(kind,data):
            return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))+
                chunk(b'IDAT',zlib.compress(b'\x00\x00\x00\x00'))+chunk(b'IEND',b''))

    def test_resume_rejects_truncated_corrupt_and_other_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'frame.png'
            p.write_bytes(self.png())
            self.assertTrue(valid_png(p,1,1))
            self.assertFalse(valid_png(p,1920,1080))
            p.write_bytes(self.png()[:-4])
            self.assertFalse(valid_png(p,1,1))
            data=bytearray(self.png());data[25]^=1;p.write_bytes(data)
            self.assertFalse(valid_png(p,1,1))


if __name__=='__main__':unittest.main()
