"""Mechanics only: deterministic fixtures do not establish real answer quality."""
import unittest
from chatify import schema
from chatify.store import Store
from chatify.pipeline import Engine
class WeakCitationRepair(unittest.TestCase):
 def test_extra_weak_citation_is_sent_for_review_not_silently_deleted(self):
  e=Engine(schema.validate({}),Store(':memory:'));e.cfg['provider']['type']='openai'
  answer='Repeated dietary adherence measurements in the Spanish trial population were observational. [1] [2]'
  evidence=[{'n':1,'title':'Diet trial','year':'2023','text':'Repeated dietary adherence measurements in the Spanish trial population were observational.'},{'n':2,'title':'Review','year':'2019','text':'Weight loss and exercise can prevent diabetes.'}]
  class P:
   def complete(self,m):self.message=m[-1]['content'];return answer.replace(' [2]','')
  e.provider=P();ledger=e.ledger(answer,evidence)
  self.assertEqual(ledger[0]['weak_cites'],[2]);fixed=e.correct(answer,evidence,ledger)
  self.assertIn('weak extra citations',e.provider.message);self.assertIn(evidence[1]['text'],e.provider.message)
  self.assertNotIn('[2]',fixed);self.assertIn('observational',fixed)
 def test_failed_or_unimproved_rewrite_keeps_original(self):
  e=Engine(schema.validate({}),Store(':memory:'));e.cfg['provider']['type']='openai'
  answer='Repeated dietary adherence measurements in the Spanish trial population were observational. [1] [2]'
  ev=[{'n':1,'title':'Trial','text':answer},{'n':2,'title':'Review','text':'Exercise diabetes prevention.'}]
  class P:
   def complete(self,m):return answer
  e.provider=P();self.assertEqual(e.correct(answer,ev,e.ledger(answer,ev)),answer)
