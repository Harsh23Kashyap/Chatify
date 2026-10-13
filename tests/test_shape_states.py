import pathlib,unittest
class ShapeStates(unittest.TestCase):
 def test_shape_tokens_are_not_scaled_and_styles_survive_old_overrides(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web'
  css=(root/'style.css').read_text();js=(root/'settings.js').read_text()
  self.assertIn('transition:border-radius .16s ease-out',css)
  self.assertIn('html[data-shadow=none] .app{box-shadow:none}',css)
  self.assertIn('html[data-bubble=soft] .bubble.bb{background:var(--bot)',css)
  self.assertIn('html[data-bubble=flat] .bubble.bb{border:0;box-shadow:none',css)
  self.assertIn('section-reset-confirmation',js)
  self.assertIn('reset to defaults. Other sections unchanged.',js)
