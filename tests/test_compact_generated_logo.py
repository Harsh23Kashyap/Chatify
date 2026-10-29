import pathlib,unittest
class CompactGeneratedLogo(unittest.TestCase):
 def test_logo_scene_uses_compact_reachable_layout(self):
  css=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/style.css').read_text()
  self.assertIn('.playground-intro:has(.playground-logo){display:grid!important;',css)
  self.assertIn('.playground-scene:has(.playground-logo){height:64px;',css)
  self.assertIn('grid-template-columns:minmax(0,1fr) 48px',css)
  self.assertIn('.thread{flex:1;min-height:0;overflow:auto;',css)
