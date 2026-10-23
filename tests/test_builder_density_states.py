import pathlib,unittest
class BuilderDensity(unittest.TestCase):
 def test_bounded_editor_and_heading_visibility(self):
  s=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/appbuilder.js').read_text();self.assertIn('?14:4;',s);self.assertIn('Math.min(420,Math.max(120,input.scrollHeight+4))',s);self.assertIn("group.addEventListener('toggle'",s);self.assertIn('d.scrollTop+=r.top-top',s)
