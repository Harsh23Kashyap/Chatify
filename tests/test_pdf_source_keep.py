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
if __name__=='__main__':unittest.main()
