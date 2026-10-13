import pathlib,unittest
class PreviewImmediateStates(unittest.TestCase):
 def test_local_theme_update_is_not_delayed_by_save_queue(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/settings.js').read_text()
  self.assertIn('clearTimeout(sendTimer);pushPreview(); pvExtra()',js)
  self.assertNotIn('sendTimer = setTimeout(pushPreview, 40)',js)
  self.assertIn('setTimeout(async () =>',js)
