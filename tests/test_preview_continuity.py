import pathlib,unittest
class PreviewContinuity(unittest.TestCase):
 def test_theme_does_not_reset_sample(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text();part=js[js.index('  const previewCopy ='):js.index('\nfunction tour(')]
  self.assertNotIn('pvBottom()',part);self.assertIn('if (copy !== lastCopy)',part);self.assertIn('thread.scrollTop = scroll',part)
  self.assertIn('Visual preview only',part)
