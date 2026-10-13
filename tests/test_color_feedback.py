import pathlib,unittest
class ColorFeedback(unittest.TestCase):
 def test_swatch_and_contrast_feedback_are_local_and_reversible(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web'
  js=(root/'settings.js').read_text();css=(root/'settings.css').read_text()
  self.assertIn('host.dataset.sample!=="colors"',js)
  self.assertIn('row._statusAnimation?.cancel()',js)
  self.assertIn('row.animate([{opacity:.65},{opacity:1}]',js)
  self.assertIn('syncSwatch(); setv(f, hex.value.toLowerCase())',js)
  self.assertIn('background-color:var(--swatch-color)!important',css)
  self.assertIn('html[data-motion=none] .crgrid .crs{transition:none!important}',css)
