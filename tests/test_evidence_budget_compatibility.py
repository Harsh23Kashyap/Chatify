import unittest
from chatify import schema
from chatify.pipeline import Engine,evidence_record
from chatify.store import Store
class EvidenceBudget(unittest.TestCase):
 def test_compact_missing_fields_keep_explicit_year_authors_and_legacy_provenance(self):
  text=evidence_record({'n':1,'title':'A','text':'B'});self.assertIn('(n.d.; source: unknown)',text);self.assertIn('"year": ""',text);self.assertIn('"authors": []',text);self.assertNotIn('"published_date": ""',text)
 def test_small_context_keeps_evidence_question_and_history_without_exceeding_limit(self):
  for n in [8000,8500,9000]:
   e=Engine(schema.validate({}),Store(':memory:'));e.cfg['memory']['context_chars']=n
   messages=e.prompt('CURRENT QUESTION',[{'n':1,'title':'Source','text':'SOURCE '+1900*'s'}],'standard',[{'question':'Old','answer':'a'*90000}],'')
   text=messages[1]['content'];self.assertIn('SOURCE',text);self.assertIn('CURRENT QUESTION',text);self.assertIn('middle omitted',text);self.assertLessEqual(sum(len(m['content']) for m in messages),n)
if __name__=='__main__':unittest.main()
