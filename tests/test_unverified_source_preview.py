import unittest
from chatify.support_verdicts import unverified_source_preview
class Preview(unittest.TestCase):
 def test_full_exact_passage_negation_and_dates_retained(self):
  text='Officials said the pause held. Aid was NOT delivered. No lasting peace was claimed.';e={'n':7,'title':'Report','text':text,'url':'https://example.invalid','published_date':'2026-10-29','date_provenance':'provider-reported'};r=unverified_source_preview([e]);self.assertFalse(r['answer_verified']);self.assertEqual(r['items'][0]['text'],text);self.assertEqual(r['items'][0]['evidence_id'],7);self.assertEqual(r['items'][0]['published_date'],'2026-10-29');self.assertIn('only part',r['label'])
 def test_oversize_is_omitted_not_cut(self):
  r=unverified_source_preview([{'n':1,'title':'Long','text':'A'*12001}]);self.assertEqual(r['items'],[]);self.assertEqual(r['omitted_sources'],1)
 def test_no_draft_claim_is_present(self):
  r=unverified_source_preview([]);self.assertFalse(r['answer_verified']);self.assertNotIn('answer',r);self.assertEqual(r['items'],[])
 def test_source_count_and_budget_explicit(self):
  es=[{'n':i,'title':'T','text':'Passage'} for i in range(5)];r=unverified_source_preview(es);self.assertEqual(len(r['items']),3);self.assertEqual(r['omitted_sources'],2)
