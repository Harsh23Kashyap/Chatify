import unittest
from chatify.support_verdicts import review_units,evaluate_answer,InvalidVerdict
class AnswerCoverage(unittest.TestCase):
 def test_every_line_including_negation_table_and_heading_retained(self):
  text='# Reporting\n\n Officials reported 30 hours. [1] Aid has not been confirmed. [1]\n| Claim | Status |\n| Aid delivered | Unknown |\n- Follow-up remains pending. [2]'
  rows=review_units(text);self.assertEqual([r['id'] for r in rows],list(range(1,6)));self.assertEqual([r['text'] for r in rows],[x for x in text.splitlines() if x.strip()]);self.assertIn('not been confirmed',rows[1]['text'])
 def test_unicode_and_decimals_not_split_or_rewritten(self):
  text='Dr. Mina reported 1.5 hours, not 15. [1]\nसूचना उपलब्ध नहीं है। [1]';self.assertEqual([x['text'] for x in review_units(text)],text.splitlines())
 def test_oversized_and_empty_are_unknown_without_model_call(self):
  class P:
   def complete(self,m):raise AssertionError('must not call')
  for text in ['', 'x'*16001, '\n'.join(['sentence']*41)]:self.assertEqual(evaluate_answer(P(),text,[{'n':1,'text':'source'}])['status'],'unknown')
 def test_evidence_limit_never_silently_truncates(self):
  class P:
   def complete(self,m):raise AssertionError('must not call')
  self.assertEqual(evaluate_answer(P(),'Answer',[{'n':1,'text':'x'*40001}])['status'],'unknown')
 def test_complete_answer_units_sent_and_malformed_never_passes(self):
  class P:
   def complete(self,m):self.messages=m;return 'OK'
  p=P();r=evaluate_answer(p,'A statement. Another statement. [1]\nNot established. [1]',[{'n':1,'text':'Evidence'}]);self.assertEqual(r['status'],'unknown');self.assertIn('Another statement.',p.messages[1]['content']);self.assertIn('Not established.',p.messages[1]['content'])
