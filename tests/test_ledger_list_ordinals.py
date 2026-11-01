"""Formatting ordinals must not become unsupported factual numbers."""
import unittest
from chatify.pipeline import Engine
class ListOrdinals(unittest.TestCase):
 def test_cited_item_not_split_or_numeric_claim(self):
  ev=[{'n':1,'title':'Agreement','text':'The agreement restored self-government through power sharing.'}]
  rows=Engine.ledger('1. The agreement restored self-government through power sharing [1].',ev)
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['bad_numbers'],[]);self.assertTrue(rows[0]['supported'])
 def test_uncited_sentence_inside_item_remains_flagged(self):
  ev=[{'n':1,'title':'Agreement','text':'The agreement included rights and reform.'}]
  rows=Engine.ledger('2. The agreement included important rights and reform. A later sentence states another finding [1].',ev)
  self.assertEqual(len(rows),2);self.assertTrue(rows[0]['uncited']);self.assertEqual(rows[1]['cites'],[1])
 def test_real_quantity_still_checked(self):
  ev=[{'n':1,'title':'Count','text':'Four members participated.'}]
  rows=Engine.ledger('3. There were 50 members participating in the meeting [1].',ev)
  self.assertIn('50',rows[0]['bad_numbers'])
