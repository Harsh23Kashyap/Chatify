import pathlib,unittest
class SimpleModeDensity(unittest.TestCase):
 def test_simple_mode_hides_model_list_chatter(self):
  css=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/settings.css').read_text()
  self.assertIn('body.settings-tabs.simple #sec-model #modelh',css)
  self.assertIn('body.settings-tabs.simple #sec-model #modelSuggestionSources',css)
