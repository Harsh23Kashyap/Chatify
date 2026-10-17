import pathlib,unittest
class SourceSummary(unittest.TestCase):
 def test_saved_summary_has_restart_boundary(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'chatify/web';s=(root/'settings.js').read_text();self.assertIn('Saved workspace sources',s);self.assertIn('cc-workspace-saved',s);self.assertIn('window.CCSourceOverview=sourceOverview',s)
  self.assertIn('new CustomEvent("cc-workspace-saved"',(root/'configstate.js').read_text());self.assertIn('window.CCSourceOverview||',(root/'panels.js').read_text())
 def test_builder_swatch_clears_hex_error(self):
  s=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/appbuilder.js').read_text();self.assertIn("hex.value=input.value;hex.setAttribute('aria-invalid','false');hex.setCustomValidity('')",s)
