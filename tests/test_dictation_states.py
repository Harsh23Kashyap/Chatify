import pathlib,unittest
class DictationStates(unittest.TestCase):
 def test_truthful_mic_lifecycle(self):
  w=pathlib.Path(__file__).resolve().parents[1]/'chatify'/'web';js=(w/'app.js').read_text();css=(w/'style.css').read_text()
  self.assertIn('active.onstart =',js);self.assertIn('Microphone access was denied.',js)
  self.assertIn('if (rec !== active) return',js);self.assertIn('active.stop(); reset(active)',js)
  self.assertIn('#mic.rec{animation:none!important;box-shadow:none!important}',css)
