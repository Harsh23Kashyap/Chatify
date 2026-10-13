import pathlib,unittest
class Notices(unittest.TestCase):
 def test_readable_lifetime_and_no_focus_steal(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/app.js').read_text();body=js[js.index('function toast(msg)'):js.index('function inline(')]
  self.assertIn('getBoundingClientRect().top',body);self.assertIn('Dismiss notification',body);self.assertIn('String(msg).length*65',body)
  self.assertIn('focusin',body);self.assertNotIn('.focus(',body)
