import pathlib,unittest
class SidebarMotion(unittest.TestCase):
 def test_docked_move_is_paired_and_large_changes_are_immediate(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/theme.js').read_text()
  self.assertIn('const sidebarMove=beginSidebarMove(t,root)',js)
  self.assertIn('finishSidebarMove(sidebarMove)',js)
  self.assertIn('layoutAnimations.forEach(a=>a.cancel())',js)
  self.assertIn('innerWidth<=860',js)
  self.assertIn('duration:160,easing:"cubic-bezier(.2,.8,.2,1)"',js)
  self.assertIn('app.classList.contains("side-collapsed")',js)
