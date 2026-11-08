"""Copy contract only. Historical answer status belongs to each persisted turn."""
from pathlib import Path
import unittest
class NoKeyTruth(unittest.TestCase):
 def test_notice_does_not_relabel_existing_answers(self):
  text=(Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text();section=text[text.index('function updateModelBadge()'):text.index('async function refreshModelBadge')]
  self.assertNotIn('answers come from source previews',section);self.assertIn('No API key is available in this session.',section);self.assertIn('New requests cannot use this AI provider.',section);self.assertIn('Saved answers keep their original status.',section);self.assertIn('Add a key in Configuration',section);self.assertIn('if (noKey && !bar)',section);self.assertIn('else if (!noKey && bar) bar.remove()',section)
if __name__=='__main__':unittest.main()
