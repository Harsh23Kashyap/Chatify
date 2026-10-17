import pathlib,unittest
class ThemeColorStates(unittest.TestCase):
 def test_preview_and_editor_theme_states_stay_separate(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'chatify/web'
  css=(root/'settings.css').read_text();js=(root/'settings.js').read_text()
  self.assertIn('#pv.preview-changing{opacity:.88}',css)
  self.assertIn('html[data-motion=none] #pv.preview-changing{opacity:1}',css)
  self.assertIn('setPvMode(b.dataset.m); pushPreview()',js)
  self.assertIn('editMode = m; syncColorEditor(sec); pushPreview()',js)
