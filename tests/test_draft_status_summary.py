import pathlib,unittest
class DraftSummary(unittest.TestCase):
 def test_states_have_grounded_sources(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/appbuilder.js').read_text()
  self.assertIn('failedAreas=[...new Set',js);self.assertIn('retry.disabled=busy||!failedAreas.length',js)
  self.assertIn('retainedTitle=before.title',js);self.assertIn('Kept locally. Validate before saving.',js)
  self.assertIn('Validated locally. Not saved or applied.',js)
 def test_running_heading_reflects_real_server_phase(self):
  js=(pathlib.Path(__file__).resolve().parents[1]/'chatify/web/appbuilder.js').read_text()
  srv=(pathlib.Path(__file__).resolve().parents[1]/'chatify/buildjobs.py').read_text()
  for phase in ('Drafting separate areas','Merged revision and final local validation','Final model review','Generating optional logo draft'):
   self.assertIn("'"+phase+"'",srv)
  self.assertIn("phaseName==='Merged revision and final local validation'?'Validating your app'",js)
  self.assertIn("phaseName==='Final model review'?'Reviewing your draft'",js)
  self.assertIn("phaseName==='Generating optional logo draft'?'Finishing your app'",js)
  self.assertIn(":'Building your app'",js)
  self.assertIn("(busy&&phaseName&&phaseName!=='Drafting separate areas'?phaseName+'",js)
