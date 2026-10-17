import unittest
from pathlib import Path
from chatify import theme
class Calm(unittest.TestCase):
 def test_profile_roundtrip(self):self.assertEqual(theme.clean({'motion':'calm'})['motion'],'calm')
 def test_no_decoration_and_keyboard(self):
  p=Path('chatify/web');self.assertIn('t.motion === "calm" ? "none"',(p/'theme.js').read_text());self.assertIn('e.ctrlKey||e.metaKey',(p/'app.js').read_text())
