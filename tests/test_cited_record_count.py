import unittest
from chatify.pipeline import Engine
class RecordCount(unittest.TestCase):
 def rows(self):return [{'n':1,'id':'a','title':'Alpha','text':'Alpha','year':'','source':'arxiv','url':'https://example.invalid/a'},{'n':2,'id':'b','title':'Beta','text':'Beta','year':'','source':'arxiv','url':'https://example.invalid/b'}]
 def test_exact_distinct_count(self):
  for number in ['Two','2']:
   line=number+' relevant returned records are [1] [2]:';ledger=Engine.ledger(line,self.rows());self.assertTrue(ledger[0]['supported']);self.assertFalse(ledger[0]['bad_numbers']);self.assertFalse(ledger[0]['weak_cites'])
 def test_wrong_duplicate_missing_worldquantity_and_extra_claim_fail(self):
  for line in ['Three relevant returned records are [1] [2]:','Two relevant returned records are [1] [1]:','Two relevant returned records are:','Two million RAG papers exist [1] [2].','Two relevant returned records are guaranteed to prove safety [1] [2].','Patients lost2kg in treatment [1] [2].']:
   with self.subTest(line=line):self.assertFalse(Engine.record_count_supported(line,[int(n) for n in __import__('re').findall(r'\[(\d+)\]',line)],self.rows()))
 def test_distinct_citation_numbers_same_record_not_two(self):
  rows=self.rows();rows[1]['url']=rows[0]['url'];self.assertFalse(Engine.record_count_supported('Two relevant returned records are:',[1,2],rows))
 def test_other_numbers_remain_unsupported(self):
  self.assertTrue(Engine.bad_numbers('The outcome was999kg',[1,2],self.rows()))
if __name__=='__main__':unittest.main()
