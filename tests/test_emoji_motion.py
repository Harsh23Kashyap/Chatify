import pathlib,unittest
class EmojiMotion(unittest.TestCase):
 def test_local_feedback_has_motion_gates_and_no_overshoot(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web'
  s=(root/'settings.js').read_text()
  self.assertIn('transform:"scale(.98)"',s);self.assertIn('duration:160,easing:"ease-out"',s)
  self.assertIn('if(categoryFade)categoryFade.cancel()',s)
  self.assertIn('grid.animate([{opacity:.65},{opacity:1}]',s)
  self.assertIn('paint(true);dialog.close()',s)
  a=(root/'app.js').read_text();self.assertIn('updatePreviewAvatars()',a)
  self.assertIn('if(node.dataset.iconValue===signature)return',a)
  self.assertIn('["txt_title","txt_tagline","txt_examples","logo"].map(TV)',a)
