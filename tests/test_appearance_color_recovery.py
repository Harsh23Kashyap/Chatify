import pathlib,unittest
class ColorRecovery(unittest.TestCase):
 def test_auto_and_swatch_clear_stale_validation(self):
  s=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/settings.js').read_text();self.assertIn('(f.clearable&&hex.value==="")',s);self.assertIn('hex.value = swatch.value; hex.setAttribute("aria-invalid","false");hex.setCustomValidity("")',s);self.assertIn('hex.value = "";hex.setAttribute("aria-invalid","false");hex.setCustomValidity("")',s)
