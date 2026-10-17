import pathlib,unittest
class RetryState(unittest.TestCase):
 def test_pending_retry_is_not_reenabled_by_poll(self):
  w=pathlib.Path(__file__).resolve().parents[1]/'chatify/web';js=(w/'appbuilder.js').read_text();css=(w/'settings.css').read_text()
  self.assertIn('retry.disabled||busy||retryPending',js);self.assertIn('retry.disabled=busy||retryPending||!failedAreas.length',js)
  self.assertIn('retryPending=false;retry.disabled=busy||!failedAreas.length',js);self.assertIn('.builder-retry{background:transparent!important',css)
