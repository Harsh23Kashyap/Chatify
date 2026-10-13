import pathlib,unittest
class AccountStates(unittest.TestCase):
 def test_validation_and_pending_guards(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web';js=(root/'app.js').read_text();body=js[js.index('async function accountGate()'):js.index('function applyWording()')]
  self.assertIn('signin-error',body);self.assertIn('password-error',body);self.assertIn('aria-describedby',body);self.assertIn('removeAttribute("aria-invalid")',body);self.assertIn("'Signing in...'",body);self.assertIn('if(go.disabled)return',body)
  css=(root/'style.css').read_text();self.assertIn('.toolbar:has(.acct-menu:not([hidden]))',css)
 def test_background_validation_clears_on_remove_or_file(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/settings.js').read_text();self.assertIn('if(!value){link.setAttribute("aria-invalid","false")',js);self.assertIn('link.setAttribute("aria-invalid","false");link.value="";theme.bg_style="image"',js)
