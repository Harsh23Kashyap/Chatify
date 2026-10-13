import pathlib,unittest
class SmallFeedbackStates(unittest.TestCase):
 def test_focus_and_hover_do_not_require_scale(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web'
  css=(root/'refinements.css').read_text();about=(root/'about.css').read_text()
  self.assertIn('#settingsFind:focus-visible',css)
  self.assertIn('box-shadow:0 0 0 3px #64896733',css)
  self.assertIn('footer a:hover{opacity:.9}',about)
  self.assertIn('input[type=color]:hover',css)
