import pathlib,unittest
class SourceUploadStates(unittest.TestCase):
 def test_perfile_states_and_batch_reset(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text();body=js[js.index(' const upload=async()=>'):js.index('\n files.addEventListener')]
  for state in ['queued','reading','saving','added','error']:self.assertIn(state,body)
  self.assertIn('fileStatus.replaceChildren',body)  # a new batch clears stale rows so an old error never sits beside a fresh success
  self.assertIn('Waiting for this server to finish',body)
  self.assertIn('File is over 8 MB',body)  # the client-side size guard Dennis hit
 def test_close_confirm_guides_to_add_link(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/app.js').read_text()
  self.assertIn('To add it, choose \\\"Add link\\\"',js)  # Dennis: the confirm must say how to add the typed address
  self.assertIn('Sources already added are kept.',js)
