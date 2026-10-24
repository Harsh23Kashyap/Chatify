"""Workspace review Confirm behavior (workspace.js) via a stub-DOM node harness.

The Confirm handler regression fixed in 5e0260c (a2a66c0's ||go.disabled guard
against the shared button() wrapper, which disables the button before invoking)
was previously covered only by source assertions. This drives the real
workspace.js: consent gate, exactly one confirmed remove, failure visibility and
retry, and no stacked review panels. The harness fails against the pre-fix
workspace.js (zero remove requests), so it guards the actual regression."""
import subprocess, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent

class WorkspaceReviewConfirmBehavior(unittest.TestCase):
    def run_scenario(self, name):
        r = subprocess.run(['node', str(ROOT / 'workspace_review_confirm_harness.cjs'), name], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn('PASS', r.stdout)

    def test_confirm_without_consent_fires_no_request(self):
        self.run_scenario('consent-gate')

    def test_consent_confirm_fires_exactly_one_remove(self):
        self.run_scenario('confirm-once')

    def test_failure_is_visible_and_retryable(self):
        self.run_scenario('failure-retry')

    def test_repeated_reviews_do_not_stack_panels(self):
        self.run_scenario('no-zombies')

if __name__ == '__main__':
    unittest.main()
