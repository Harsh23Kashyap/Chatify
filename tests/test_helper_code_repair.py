import unittest
from chatify.buildjobs import repair_helper_code
class HelperCodeRepair(unittest.TestCase):
 def test_valid_code_is_untouched(self):
  code='def search(query, limit=6):\n    return [str(query)[:limit]]\n'
  self.assertEqual(repair_helper_code(code),code)
 def test_double_escaped_code_is_repaired(self):
  broken='def search(query, limit=6):\\n    return {\\"q\\": query}\\n'
  fixed=repair_helper_code(broken)
  compile(fixed,'<helper-draft>','exec')
  self.assertIn('"q"',fixed)
 def test_genuinely_broken_code_is_returned_as_is(self):
  bad='def search(query, limit=6) oops {'
  self.assertEqual(repair_helper_code(bad),bad)
 def test_legitimate_escapes_are_not_corrupted(self):
  code='x = "line1\\nline2"\n'
  self.assertEqual(repair_helper_code(code),code)
