import pathlib,unittest
class FontFeedback(unittest.TestCase):
 def test_samples_are_stable_and_loading_status_is_truthful(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'chatify/web'
  js=(root/'settings.js').read_text();css=(root/'settings.css').read_text()
  self.assertIn('host.dataset.sample!=="fonts"',js)
  self.assertIn('host.dataset.fontSelection!==signature',js)
  self.assertIn('document.fonts.load',js)
  self.assertIn('A selected font could not load. System fallback is shown',js)
  self.assertIn('heading.animate([{opacity:.5},{opacity:1}]',js)
  self.assertIn('body.style.fontSize=(13*theme.font_size/100)',js)
  self.assertIn('min-height:190px',css)
