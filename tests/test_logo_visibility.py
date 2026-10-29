import struct,zlib,unittest
from chatify.buildimages import check_visibility
def png(alpha):
 def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b))
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',2,2,8,6,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+bytes([80,120,40,alpha])*2)*2))+chunk(b'IEND',b'')
class LogoVisibility(unittest.TestCase):
 def test_nearly_invisible_rejected(self):
  with self.assertRaisesRegex(ValueError,'effectively transparent'):check_visibility(png(6))
 def test_opaque_not_quality_certified_but_visible(self):check_visibility(png(255))
