import unittest
from pathlib import Path

JS = Path(__file__).parents[1] / 'chatify/web/workspace.js'

class WorkspaceReviewConfirm(unittest.TestCase):
 def test_confirm_does_not_gate_on_its_own_disabled_state(self):
  # The shared button() wrapper sets b.disabled=true before invoking the
  # handler and restores it after, so a Confirm handler that re-checks its
  # own disabled state can never run (live evidence 2026-10-25: workspace
  # Remove confirmed, panel stayed silent, workspace persisted).
  js = JS.read_text()
  self.assertIn("const go=button('Confirm',async()=>{if(!consent.checked)return;", js)
  self.assertNotIn("if(!consent.checked||go.disabled)return", js)

 def test_single_review_panel_at_a_time(self):
  # Two stacked review panels left a zombie Confirm behind (live evidence
  # 2026-10-25): a stale panel's controls no longer matched its closure.
  js = JS.read_text()
  self.assertIn("for(const stale of document.querySelectorAll('.workspace-review'))stale.remove();", js)

 def test_confirm_keeps_error_surface_and_working_label(self):
  js = JS.read_text()
  self.assertIn("go.textContent='Working...'", js)
  self.assertIn("err.textContent=(e&&e.message)||'The action did not complete. Nothing was applied - try again.'", js)

if __name__ == '__main__':
 unittest.main()
