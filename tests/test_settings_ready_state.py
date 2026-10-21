import pathlib,unittest
class SettingsReadyState(unittest.TestCase):
 def test_no_provider_call_on_settings_load(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'chatify/web'
  js=(root/'settings.js').read_text();simple=(root/'settingssimple.js').read_text()
  self.assertNotIn('cc_env_conn_checked',js)
  self.assertNotIn('tc.click()',js)
  self.assertIn('dataset.assumed = "1"',js)
  self.assertIn('delete t.dataset.assumed',js)
  self.assertIn('Ready. A key is configured on the host.',js)
  self.assertIn("assumed=tr?.dataset.assumed==='1'",simple)
  self.assertIn('Ready. A key is configured on the host.',simple)
  self.assertIn('Connected and ready.',simple)
