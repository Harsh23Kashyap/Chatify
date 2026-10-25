from pathlib import Path
import unittest
from chatify.exports import pdf_bytes
class PdfSourceKeep(unittest.TestCase):
 def test_keep_together_logic_present(self):
  s=(Path(__file__).resolve().parents[1]/'chatify/exports.py').read_text()
  self.assertIn("if kind=='source':",s)
  self.assertIn('Keep one source entry',s)
 def test_long_source_list_renders(self):
  titles=['Source %d with a deliberately long title that wraps across two full lines of the narrow PDF column width for pagination testing.'%i for i in range(1,12)]
  ev=[{'n':i,'title':t,'url':'https://example.com/%d'%i,'source':'web'} for i,t in enumerate(titles,1)]
  turn={'question':'Q?','answer':'Body text.\n\n- bullet [1]','evidence':ev,'source_errors':[]}
  out=pdf_bytes('App',turn)
  self.assertGreater(len(out),5000)
  self.assertTrue(out.startswith(b'%PDF'))
 def test_math_operator_coverage(self):
  from chatify.exports import _covered_chars
  cov=_covered_chars()
  for cp in (0x221E,0x2202,0x2207,0x222B,0x2208,0x2209,0x2282,0x222A,0x2260,0x2264,0x2265,0x2248,0x221D,0x221A,0x2211,0x220F):
   self.assertIn(cp,cov,'U+%04X must be covered after bundling Noto Sans Math'%cp)
 def test_infinity_turn_renders(self):
  ev=[{'n':1,'title':'Infinity Galaxy','url':'https://en.wikipedia.org/wiki/Infinity_Galaxy','source':'wikipedia'}]
  turn={'question':'JWST finds?','answer':'- The Infinity Galaxy (∞ Galaxy), z ≈ 14.4, Δt ≤ 280 Myr. [1]','evidence':ev,'source_errors':[]}
  out=pdf_bytes('App',turn)
  self.assertTrue(out.startswith(b'%PDF'))
if __name__=='__main__':unittest.main()
