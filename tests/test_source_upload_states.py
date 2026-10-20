import pathlib,unittest
class SourceUploadStates(unittest.TestCase):
 def test_perfile_states_and_batch_reset(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text();body=js[js.index(' const upload=async()=>'):js.index('\n files.addEventListener')]
  for state in ['queued','reading','saving','added','error']:self.assertIn(state,body)
  self.assertIn('fileStatus.replaceChildren',body)  # a new batch clears stale rows so an old error never sits beside a fresh success
  self.assertIn('Waiting for this server to finish',body)
