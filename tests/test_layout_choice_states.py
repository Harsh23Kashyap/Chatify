import pathlib,unittest
class LayoutChoiceStates(unittest.TestCase):
 def test_width_choice_works_without_overwriting_reading_preference(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web'
  css=(root/'style.css').read_text();reading=(root/'reading.js').read_text()
  self.assertIn('max-width:var(--chat-max,980px)!important',css)
  self.assertIn('html.reading-width-selected body .thread>.wrap',css)
  self.assertIn('classList.toggle("reading-width-selected"',reading)
  self.assertIn('transition-duration:160ms!important',css)
