import unittest
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class SupportCoverage(unittest.TestCase):
 def test_support_stage_receives_same_passage_extent_as_answer(self):
  e=Engine(schema.validate({}),Store(':memory:'));e.cfg['provider']['type']='openai';e._llm_on=lambda k:True
  class Provider:
   def complete(self,m):self.message=m[-1]['content'];return 'OK'
  pv=Provider();e.provider=pv
  marker='The measured endpoint was 0.72 with protocol deviations addressed.'
  e.check_support(marker,[{'n':1,'title':'Primary report','text':'Background sentence. '*50+marker}])
  self.assertIn(marker,pv.message.split("Evidence:\n",1)[1])

 def test_support_stage_receives_publication_metadata(self):
  e=Engine(schema.validate({}),Store(':memory:'));e.cfg['provider']['type']='openai';e._llm_on=lambda k:True
  class Provider:
   def complete(self,m):self.message=m[-1]['content'];return 'OK'
  pv=Provider();e.provider=pv
  e.check_support('The report is from 2018 [1].',[{'n':1,'title':'Umbrella review','year':'2018','text':'Diet findings.'}])
  evidence=pv.message.split('Evidence:\n',1)[1]
  self.assertIn('Umbrella review',evidence);self.assertIn('2018',evidence)
