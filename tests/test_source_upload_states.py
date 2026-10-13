import pathlib,unittest
class SourceUploadStates(unittest.TestCase):
 def test_perfile_states_and_retained_results(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/app.js').read_text();body=js[js.index(' const upload=async()=>'):js.index('\n files.addEventListener')]
  for state in ['queued','reading','saving','added','error']:self.assertIn(state,body)
  self.assertNotIn('fileStatus.replaceChildren',body)
  self.assertIn('Waiting for this server to finish',body)
