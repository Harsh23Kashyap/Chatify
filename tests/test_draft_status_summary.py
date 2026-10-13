import pathlib,unittest
class DraftSummary(unittest.TestCase):
 def test_states_have_grounded_sources(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/appbuilder.js').read_text()
  self.assertIn('failedAreas=[...new Set',js);self.assertIn('retry.disabled=busy||!failedAreas.length',js)
  self.assertIn('retainedTitle=before.title',js);self.assertIn('Kept locally. Validate before saving.',js)
  self.assertIn('Validated locally. Not saved or applied.',js)
