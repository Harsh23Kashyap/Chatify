import pathlib,unittest
class SourceOverlay(unittest.TestCase):
 def test_mobile_sources_have_modal_lifecycle(self):
  w=pathlib.Path(__file__).resolve().parents[1]/'chatify/web';js=(w/'app.js').read_text();css=(w/'style.css').read_text()
  self.assertIn('sourceModal(false)',js);self.assertIn('pane.setAttribute("aria-modal", "true")',js)
  self.assertIn('sourceShield.set(n,n.inert)',js);self.assertIn('newTopic',js)
  self.assertIn('.app.src>.main{grid-column:1;grid-row:1}',css)
