import pathlib,unittest
class AboutIntroStates(unittest.TestCase):
 def test_intro_only_fades_once_and_finishes_in_220ms(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/about.js').read_text()
  self.assertIn("sessionStorage.getItem('cc_about_intro_seen')",js)
  self.assertIn("duration:180,delay:40",js)
  self.assertIn("document.querySelector('main>h1')?.animate([{opacity:0},{opacity:1}]",js)
  self.assertIn("['none','calm'].includes",js)
