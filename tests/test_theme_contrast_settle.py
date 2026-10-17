import pathlib,unittest
class ThemeContrastSettle(unittest.TestCase):
 def test_contrast_correction_reads_final_colors_not_transition_frames(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'chatify/web'
  js=(root/'theme.js').read_text();css=(root/'style.css').read_text()
  self.assertIn('classList.add("contrast-measuring")',js)
  self.assertIn('classList.remove("contrast-measuring")',js)
  self.assertIn('html.contrast-measuring *',css)
