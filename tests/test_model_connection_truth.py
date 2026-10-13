import pathlib,unittest
class ConnectionTruth(unittest.TestCase):
 def test_endpoint_edits_clear_old_pass(self):
  s=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/settings.js').read_text();self.assertIn('for(const id of ["base","temp"])',s);self.assertIn('Model settings changed. Test this selection when ready.',s);self.assertIn('$("#base").value.trim()===base',s)
