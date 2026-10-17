import pathlib,unittest
class WordingStates(unittest.TestCase):
 def test_preview_welcome_and_color_validation_reset(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'chatify/web';self.assertIn('html.preview .thread .hero.mini{display:block',(root/'style.css').read_text());s=(root/'settings.js').read_text();self.assertIn('hex.value=value;hex.setAttribute("aria-invalid","false");hex.setCustomValidity("")',s)
