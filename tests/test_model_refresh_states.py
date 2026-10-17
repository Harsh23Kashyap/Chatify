import pathlib,unittest
class ModelRefresh(unittest.TestCase):
 def test_latest_model_not_request_snapshot(self):
  s=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/settings.js').read_text();self.assertIn('const currentModel=cur.model||""',s);self.assertIn('if(typed)$("#model").value=currentModel',s);self.assertIn('sel.setAttribute("aria-busy","true")',s);self.assertIn('sel.removeAttribute("aria-busy")',s)
