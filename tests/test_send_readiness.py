from pathlib import Path
import unittest
class SendReadiness(unittest.TestCase):
 def test_send_disabled_until_init_binds(self):
  w=Path(__file__).resolve().parents[1]/'chatify/web';s=(w/'index.html').read_text()
  self.assertIn('id="send" aria-label="Send" aria-keyshortcuts="Enter Control+Enter Meta+Enter" title="Send question" disabled>',s)
 def test_loading_status_until_ready(self):
  s=(Path(__file__).resolve().parents[1]/'chatify/web/index.html').read_text()
  self.assertIn('<span id="hint">Loading...</span>',s)
 def test_ready_activation_after_binding(self):
  s=(Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text()
  bind=s.index('$("#send").addEventListener("click"')
  rdy=s.index('rdy(); $("#send"')
  self.assertLess(rdy,bind)  # rdy() runs right before the click binding line completes activation
  self.assertIn('s.disabled = !S.busy && !on',s)
  self.assertIn('Could not start: ',s)  # config failure surfaces an error instead of a stuck loader
if __name__=='__main__':unittest.main()
