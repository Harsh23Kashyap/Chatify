import pathlib,unittest
class AboutContinuity(unittest.TestCase):
 def test_catalog_keeps_existing_items(self):
  w=pathlib.Path(__file__).resolve().parents[1]/'chatify/web';js=(w/'about.js').read_text();css=(w/'about.css').read_text()
  self.assertIn('while(tabs.children.length>6)',js);self.assertIn('i<tabs.children.length',js)
  self.assertIn('if(!panel.children.length||(!expanded&&active>5))',js)
  self.assertIn('i>=6&&i<10',js);self.assertIn('@keyframes feature-reveal',css)
