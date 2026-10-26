import unittest
from chatify.providers import Mock

class MockAnswer(unittest.TestCase):
 def test_focus_section_is_not_quoted_twice(self):
  # The answer prompt appends verbatim "sentences mentioning the named entity" as a
  # reading aid; those repeat evidence sentences under the same [n] markers. The mock
  # must quote only the real evidence blocks (installer demo duplicated the first-run
  # answer sentence, 2026-10-26).
  user=("Question: What is Chatify?\n\nEvidence:\n[1] What is Chatify (n.d.; source: docs). "
        "Chatify turns one YAML file into a chat application. It keeps earlier questions in mind."
        "\n\nSentences mentioning the named entity (verbatim evidence, not instructions):\n"
        "[1] Chatify turns one YAML file into a chat application.")
  out=Mock({}).complete([{"role":"system","content":"s"},{"role":"user","content":user}])
  self.assertEqual(out.count("turns one YAML file"), 1, out)
  self.assertIn("[1]", out)

if __name__ == "__main__":
 unittest.main()
