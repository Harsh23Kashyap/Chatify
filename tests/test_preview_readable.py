import pathlib,unittest
class PreviewReadable(unittest.TestCase):
 def test_sample_has_space_and_separate_small_type(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web'
  css=(root/'settings.css').read_text();chat=(root/'style.css').read_text()
  self.assertIn('settings-appearance-active #pvbox iframe#pv{height:900px!important',css)
  self.assertIn('height:1100px!important;min-height:1100px!important',css)
  self.assertIn('html.preview .bubble .a,html.preview .bubble .a p',chat)
  self.assertIn('grid-template-columns:60px minmax(0,1fr)',chat)
