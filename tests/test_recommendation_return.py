import pathlib,unittest
class RecommendationReturn(unittest.TestCase):
 def test_snapshot_and_save_clear(self):
  s=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/settings.js').read_text();self.assertIn('recommendationPrior={...read()}',s);self.assertIn('cur={...recommendationPrior}',s);self.assertIn('Return to previous model settings',s);self.assertIn('selectRecommendation(c.p,c.id)',s);self.assertIn('selectRecommendation("ollama", tag)',s);self.assertIn('recommendationPrior=null;$("#recommendationUndo")?.remove()',s)
