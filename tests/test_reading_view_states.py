import pathlib,unittest
class ReadingView(unittest.TestCase):
 def test_plain_sample_and_direct_reading_change(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web';self.assertIn('Sample text',(root/'reading.js').read_text());self.assertIn('html.reading-view .row .a{transition-property:background-color,color,border-color!important}',(root/'style.css').read_text())
