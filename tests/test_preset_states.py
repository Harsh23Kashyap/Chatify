import pathlib,unittest
class PresetStates(unittest.TestCase):
 def test_preset_cards_keep_identity_and_name_errors_keep_focus(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/settings.js').read_text()
  self.assertIn('previousCards=new Map',js)
  self.assertIn('if(retained){box.append(retained);continue;}',js)
  self.assertIn('preset-selected',js)
  self.assertIn('$("#sname").focus();$("#sname").setAttribute("aria-invalid","true")',js)
