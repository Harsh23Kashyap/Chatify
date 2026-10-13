import pathlib,unittest
class AboutFeatures(unittest.TestCase):
 def test_controlled_feature_copy_motion(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web';self.assertIn("classList.add('feature-copy-arrive')",(root/'about.js').read_text());css=(root/'about.css').read_text();self.assertIn('animation:feature-copy-arrive .16s',css);self.assertIn('translateY(4px)',css);self.assertIn('.feature-copy-arrive{animation:none}',css)

 def test_old_content_fades_without_selection_races(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web';js=(root/'about.js').read_text();css=(root/'about.css').read_text();self.assertIn('clearTimeout(selectionTimer)',js);self.assertIn('setTimeout(reveal,80)',js);self.assertIn('animation:feature-copy-leave .08s',css);self.assertIn('.feature-copy-leave{animation:none}',css)
