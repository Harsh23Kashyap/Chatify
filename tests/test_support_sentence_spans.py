import unittest,re
from chatify.support_verdicts import sentence_spans,InvalidVerdict,evaluate_sentences
class SentenceSpans(unittest.TestCase):
 def check(self,text):
  rows=sentence_spans(text);self.assertEqual(''.join(re.sub(r'\s+','',r['text']) for r in rows),re.sub(r'\s+','',text))
  for r in rows:self.assertEqual(text[r['start']:r['end']],r['text'])
  for a,b in zip(rows,rows[1:]):self.assertLessEqual(a['end'],b['start'])
  return rows
 def test_multisentence_citations_and_negation(self):
  rows=self.check('Officials reported 30 hours. [1] Aid was not delivered. [2]\nThe supplied passage does not establish lasting peace. [1]');self.assertEqual(len(rows),3);self.assertEqual(rows[1]['text'],'Aid was not delivered. [2]')
 def test_abbreviations_decimals_and_initials(self):
  rows=self.check('Dr. Mina spoke to A. Smith about 1.5 hours. [1] Next came a pause. [2]');self.assertEqual(len(rows),2)
 def test_table_header_and_unicode_retained(self):
  rows=self.check('# Results\n| Food | Pending. Not done. |\nसूचना उपलब्ध नहीं है। [1] This is a report. [1]');self.assertEqual(len(rows),4)
 def test_compound_negation_not_rewritten(self):
  text='The supplied passage does not establish aid delivery or lasting peace. [1]';self.assertEqual(self.check(text)[0]['text'],text)
 def test_url_kept_and_trailing_clause_covered(self):
  self.check('See https://example.invalid/path. Then consider a question? [1] A trailing fragment')
 def test_quoted_terminal_and_bullet_ordinals(self):
  self.check('1. Officials said "The pause holds." [1] It may not last. [1]')
 def test_overflow_fails_before_model(self):
  class P:
   def complete(self,m):raise AssertionError('should not call')
  self.assertEqual(evaluate_sentences(P(),'A. '*17000,[{'n':1,'text':'source'}])['status'],'unknown')
