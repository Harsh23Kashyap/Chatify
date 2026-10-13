import pathlib,unittest
class ActionStates(unittest.TestCase):
 def test_human_review_and_guarded_recovery(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'customchat/web/app.js').read_text();body=js[js.index('$("#actionsBtn").onclick'):js.index('$("#hint").textContent = "Answers cite their sources.')]
  self.assertNotIn('JSON.stringify',body);self.assertIn("title:'Note title'",body);self.assertIn('if(confirm.disabled)return',body);self.assertIn('if(preview.disabled)return',body);self.assertIn("text:'Back to edit'",body);self.assertIn('check your notes before saving again',body);self.assertIn('input.value=inputs[name]?.value',body);self.assertIn("text:'No notes saved yet.'",body)
