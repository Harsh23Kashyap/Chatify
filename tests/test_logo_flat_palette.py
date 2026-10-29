import unittest,struct,zlib
from chatify.buildimages import flat_palette

def png(pixels):
 def c(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d))
 return b'\x89PNG\r\n\x1a\n'+c(b'IHDR',struct.pack('>IIBBBBB',2,2,8,2,0,0,0))+c(b'IDAT',zlib.compress(b'\0'+pixels[:6]+b'\0'+pixels[6:]))+c(b'IEND',b'')
class Palette(unittest.TestCase):
 def test_flat_palette_retains_shape_and_uses_requested_colors(self):
  original=png(bytes([0,0,0,255,255,255]*2));out=flat_palette(original,'#173f35','#d7ef72');pos=8;data=b''
  while pos<len(out):
   n=struct.unpack('>I',out[pos:pos+4])[0]
   if out[pos+4:pos+8]==b'IDAT':data+=out[pos+8:pos+8+n]
   pos+=12+n
  row=zlib.decompress(data);self.assertEqual(row,b'\0'+bytes.fromhex('173f35d7ef72')+b'\0'+bytes.fromhex('173f35d7ef72'));self.assertNotEqual(original,out)
 def test_invalid_colors_and_blank_shape_rejected(self):
  raw=png(bytes([255]*12))
  with self.assertRaises(ValueError):flat_palette(raw,'red','#ffffff')
  with self.assertRaisesRegex(ValueError,'separation'):flat_palette(raw,'#173f35','#ffffff')

 def test_provenance_survives_theme_validation(self):
  import base64
  from chatify import theme,appbuilder
  original='data:image/png;base64,'+base64.b64encode(png(bytes([0,0,0,255,255,255]*2))).decode()
  look=theme.DEFAULT_CLEAN();look.update(logo=original,logo_original=original,logo_rendering='flat-palette-v1')
  out=appbuilder.validate_extras({'appearance':look})['appearance']
  self.assertEqual(out['logo_original'],original);self.assertEqual(out['logo_rendering'],'flat-palette-v1')
