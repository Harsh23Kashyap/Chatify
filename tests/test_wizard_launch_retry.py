"""Guided wizard save-and-start retry behavior (build.js) via a stub-DOM node harness."""
import subprocess, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent

class WizardLaunchRetryTest(unittest.TestCase):
    def run_scenario(self, name):
        r = subprocess.run(['node', str(ROOT / 'wizard_launch_retry_harness.cjs'), name], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn('PASS', r.stdout)

    def test_failed_start_retries_with_reissued_ticket(self):
        # First start fails after the review was confirmed: the wizard must retry
        # the start with the server's re-issued ticket, never re-save with the
        # consumed review ticket.
        self.run_scenario('retry-ticket')

    def test_job_id_written_to_url_for_resume(self):
        # A completed draft must survive Back/reload: starting a build writes
        # ?job=<id> into the URL and the boot code resumes from it.
        self.run_scenario('start-wires-url')

    def test_expired_review_ticket_re_reviews_once(self):
        # A consumed/expired review ticket on save re-reviews once, saves with the
        # fresh ticket and starts - one click, no dead end.
        self.run_scenario('expired-review')

if __name__ == '__main__':
    unittest.main()
