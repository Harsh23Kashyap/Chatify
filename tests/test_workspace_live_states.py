import pathlib,unittest
class WorkspaceLiveStates(unittest.TestCase):
 def test_local_job_feedback_is_bound_to_its_original_host(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'customchat/web'
  js=(root/'workspace.js').read_text()
  self.assertIn('poll(r.id,jobStatus,select)',js)
  self.assertIn("jobStatus.setAttribute('aria-live','polite')",js)
  self.assertIn("jobStatus.classList.remove('workspace-check-running')",js)
  self.assertIn('resultHost.append(box)',js)
  self.assertIn('if(resultHost.isConnected)window.scrollTo(scrollX,scrollY)',js)
  self.assertIn('if(requestSequence!==seq)return;',js)
