import pathlib,unittest
class TransferGuideStates(unittest.TestCase):
 def test_transfer_status_is_local_and_guide_does_not_claim_application(self):
  root=pathlib.Path(__file__).resolve().parents[1]/'chatify/web'
  js=(root/'settings.js').read_text();guide=(root/'settingsguide.js').read_text()
  self.assertIn('Look file created. Download requested; check your downloads.',js)
  self.assertIn('Checking look file...',js)
  self.assertIn('Import cancelled. Appearance unchanged.',js)
  self.assertIn('URL.revokeObjectURL(url)',js)
  self.assertIn("send.textContent=request?'Asking...':'Ask selected model'",guide)
  self.assertIn('Guide received. No settings changed.',guide)
