import pathlib,unittest
class ProviderMotionStates(unittest.TestCase):
 def test_provider_identity_and_network_state_are_preserved(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web'
  js=(root/'settings.js').read_text();css=(root/'refinements.css').read_text()
  self.assertIn('existing=new Map([...seg.querySelectorAll("[data-p]")]',js)
  self.assertIn('seg.insertBefore(button,seg.children[i]||null)',js)
  self.assertIn('button.textContent="Testing..."',js)
  self.assertIn('button.removeAttribute("aria-busy")',js)
  self.assertIn('connection-status-icon',js)
  self.assertIn('tc.dataset.running==="true"',js)
  self.assertIn('#seg .provider-selected',css)
