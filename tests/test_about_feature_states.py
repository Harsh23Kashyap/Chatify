import pathlib,unittest
class AboutFeatures(unittest.TestCase):
 def test_controlled_feature_copy_motion(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web';self.assertIn("classList.add('feature-copy-arrive')",(root/'about.js').read_text());css=(root/'about.css').read_text();self.assertIn('animation:feature-copy-arrive .16s',css);self.assertIn('translateY(4px)',css);self.assertIn('.feature-copy-arrive{animation:none}',css)
