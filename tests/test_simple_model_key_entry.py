from pathlib import Path
import unittest
class SimpleModelKeyEntry(unittest.TestCase):
 def test_configured_remote_keys_still_allow_replacement_in_simple_mode(self):
  js=(Path(__file__).parents[1]/'chatify/web/settingssimple.js').read_text()
  statement=next(line for line in js.splitlines() if "classList.toggle('simple-key-needed'" in line)
  self.assertIn("state.provider!=='mock'&&state.provider!=='ollama'",statement)
  self.assertNotIn('state.key',statement)
  self.assertIn('#keybox',js)
