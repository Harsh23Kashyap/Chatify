import unittest
from chatify.management import diagnosis
class DiagnosisActions(unittest.TestCase):
 def test_known_causes_have_private_actionable_guidance(self):
  for text,kind,word in [('400 rejected','configuration','model name'),('401 refused','authentication','credential'),('403 forbidden','authentication','permission'),('429 quota','limit','quota'),('timed out','timeout','address'),('503 unavailable','connection','Retry later'),('404 not found','configuration','service address')]:
   with self.subTest(text=text):
    r=diagnosis(text+' fixture-private-token');self.assertEqual(r['category'],kind);self.assertIn(word,r['message']);self.assertNotIn('fixture-private-token',str(r));self.assertTrue(r['redacted'])
 def test_unknown_cause_does_not_invent_a_network_failure(self):
  r=diagnosis('Something unexpected went wrong while testing. fixture-private-token')
  self.assertEqual(r['category'],'unknown');self.assertIn('cause could not be confirmed',r['message']);self.assertNotIn('fixture-private-token',str(r))
