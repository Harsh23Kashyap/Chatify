import pathlib,unittest
class PickerLong(unittest.TestCase):
 def test_busy_and_all_disabled_guard(self):
  s=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/customselect.js').read_text();self.assertIn("if(!enabled.length)return",s);self.assertIn("if(sel.getAttribute('aria-busy')==='true')btn.setAttribute('aria-busy','true')",s)
