import pathlib,unittest
class HistorySkeleton(unittest.TestCase):
 def test_delay_scope_actual_replacement_and_reduce(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web'
  js=(root/'app.js').read_text();css=(root/'style.css').read_text()
  self.assertIn('if(!list.querySelector(".item"))',js)
  self.assertIn('"aria-hidden":"true"',js)
  self.assertIn('},250)',js)
  self.assertIn('clearTimeout(historyShimmerTimer)',js)
  self.assertIn('.history-skeleton-row{height:44px',css)
  self.assertIn('@media(prefers-reduced-motion:no-preference){html:not([data-motion=none]) .history-skeleton.slow',css)
