from pathlib import Path
import unittest

class RunLocallyPrivacy(unittest.TestCase):
    def test_local_storage_does_not_promise_offline_processing(self):
        page = (Path(__file__).parents[1] / "chatify/web/run-locally.html").read_text()
        self.assertNotIn("never leave your computer", page)
        self.assertIn("Cloud model providers still receive", page)
        self.assertIn("source passages", page)
        self.assertIn("Browser dictation may use an online speech service", page)
