from pathlib import Path
import unittest
class SourcesDrawer(unittest.TestCase):
 def test_drawer_lands_on_support_span(self):
  s=(Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text()
  # The 4-line-clamped drawer card must show the question-relevant span like the
  # evidence row, not the generic chunk head (R1 sources-drawer mismatch 2026-10-25).
  self.assertIn('excerptWindow(plainText(e.text), (S.turns[S.turns.length - 1] || {}).standalone || "", 280)',s)
if __name__=='__main__':unittest.main()
