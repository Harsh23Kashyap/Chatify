import pathlib,unittest
W=pathlib.Path(__file__).resolve().parents[1]/'customchat'/'web'
class StreamReading(unittest.TestCase):
 def test_actual_stream_and_no_token_animation(self):
  js=(W/'app.js').read_text();css=(W/'style.css').read_text()
  self.assertIn('live.append(sp)',js);self.assertIn('.tk{animation:none!important}',css)
  self.assertIn('if (follow) th.scrollTop = th.scrollHeight',js)
 def test_reading_indicator_focus_and_composer_placement(self):
  js=(W/'app.js').read_text();css=(W/'style.css').read_text()
  self.assertIn('Reply ready. Scroll to latest',js);self.assertIn('jump.tabIndex = away ? 0 : -1',js)
  self.assertIn('new ResizeObserver(syncLatest)',js);self.assertIn('.main>.jump{z-index:5}',css)
  self.assertIn('focus({preventScroll:true})',js)
