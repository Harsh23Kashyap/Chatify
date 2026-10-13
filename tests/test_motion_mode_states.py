import pathlib,unittest
class MotionModeStates(unittest.TestCase):
 def test_demo_is_local_and_stops_immediately_on_calm(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web'
  app=(root/'app.js').read_text();settings=(root/'settings.js').read_text()
  self.assertIn("document.querySelectorAll('.row:not(.u)')",app)
  self.assertIn('window.ccStopPreviewMotion()',app)
  self.assertIn('demoAnimation.cancel()',app)
  self.assertIn('if(["calm","none"].includes(input.value))$("#pv")?.contentWindow?.ccStopPreviewMotion?.()',settings)
  self.assertIn('outline:"2px solid #78917d"',settings)
