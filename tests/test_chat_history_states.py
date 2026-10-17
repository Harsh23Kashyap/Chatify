import pathlib,unittest
class HistoryStates(unittest.TestCase):
 def test_stale_errors_and_visible_recovery(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text();body=js[js.index('async function loadList()'):js.index('async function openChat(')]
  self.assertIn('aria-busy',body);self.assertIn('Loading history...',body);self.assertIn('No chats match your search',body);self.assertIn('if(seq!==loadList.seq)return;clearTimeout(historySkeletonTimer)',body);self.assertIn('state.replaceChildren(el("span",{text:"History could not load.',body);self.assertIn('e.stopPropagation();loadList()',body)
  css=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/style.css').read_text();self.assertIn('.item:focus-within .acts{display:flex}',css)
