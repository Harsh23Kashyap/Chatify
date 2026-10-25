from pathlib import Path
import unittest
from chatify.pipeline import _chat_title
class ChatTitle(unittest.TestCase):
 def test_word_boundary_truncation(self):
  q='What mechanisms drive CAR-T therapy resistance and relapse in diffuse large B-cell lymphoma?'
  t=_chat_title(q)
  self.assertEqual(t,'What mechanisms drive CAR-T therapy resistance and relapse')
  self.assertFalse(t.endswith((' i',' in',' the',' a')))
 def test_boundary_aligned_keeps_word(self):
  self.assertEqual(_chat_title('What have the latest JWST observations revealed about early galaxy formation?'),'What have the latest JWST observations revealed about early')
 def test_short_and_unbreakable(self):
  self.assertEqual(_chat_title('Short question?'),'Short question?')
  self.assertEqual(len(_chat_title('A'*120)),60)
 def test_call_sites_use_helper(self):
  s=(Path(__file__).resolve().parents[1]/'chatify/pipeline.py').read_text()
  self.assertNotIn('rename_chat(owner, chat, q[:60])',s)
  self.assertEqual(s.count('rename_chat(owner, chat, _chat_title(q))'),2)
  js=(Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text()
  self.assertNotIn('$("#chatTitle").textContent = q.slice(0, 60)',js)
  self.assertIn('function chatTitleFrom(q, limit = 60)',js)
  self.assertIn('$("#chatTitle").textContent = chatTitleFrom(q)',js)
if __name__=='__main__':unittest.main()
