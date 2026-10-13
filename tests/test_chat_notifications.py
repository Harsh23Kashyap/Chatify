import pathlib,unittest
class Notices(unittest.TestCase):
 def test_readable_lifetime_and_no_focus_steal(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/app.js').read_text();body=js[js.index('function toast(msg,'):js.index('function inline(')]
  self.assertIn('getBoundingClientRect().top',body);self.assertIn('Dismiss notification',body);self.assertIn('String(msg).length*65',body)
  self.assertIn('focusin',body);self.assertNotIn('.focus(',body)

 def test_action_and_position_cleanup(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/app.js').read_text();body=js[js.index('function toast(msg,'):js.index('function inline(')]
  self.assertIn('observer?.disconnect()',body);self.assertIn('ResizeObserver(place)',body);self.assertIn('if(!action)timer=',body);self.assertIn('button.disabled=true',body);self.assertIn('button.disabled=false',body)
  self.assertEqual(js.count('class:"toast"'),1);self.assertNotIn('Click to undo',js);self.assertIn('Your new draft is still here',js)
