import pathlib,unittest
class BackgroundTransition(unittest.TestCase):
 def test_background_only_fades_and_cancels_stale_cover(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'chatify/web'
  js=(root/'theme.js').read_text();css=(root/'style.css').read_text()
  self.assertIn('previous === signature || reduced',js)
  self.assertIn('if (backgroundFade) backgroundFade.remove()',js)
  self.assertIn('cover.animate([{opacity:1},{opacity:0}]',js)
  self.assertIn('duration:180',js)
  self.assertIn('background-fade{position:fixed;inset:0;pointer-events:none;z-index:0}',css)
  self.assertIn('@media(prefers-reduced-motion:reduce){.background-fade{display:none!important}}',css)
 def test_disclosure_checks_device_and_saved_motion(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/settings.js').read_text()
  self.assertIn('d.addEventListener("toggle",()=>{if(d.open',js)
  self.assertIn('revealMotion(grid,[{opacity:0,transform:"translateY(4px)"}',js)
