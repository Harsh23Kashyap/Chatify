import pathlib,unittest
class RecommendationMotion(unittest.TestCase):
 def test_status_and_cards_update_without_rebuild(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/settings.js').read_text()
  self.assertIn('if(!cp.querySelector(".cpick"))',js)
  self.assertIn('button.textContent=selected?"Selected":"Use"',js)
  self.assertIn('Key needed. Not saved.',js)
  self.assertIn('if(!card.querySelector(".pvm-provider-name"))',js)
  self.assertIn('r?.innerText',js)
