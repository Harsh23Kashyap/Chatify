"""Relevance must see a connector's bounded abstract, not only its introduction.
Synthetic transport contract coverage prompted by actual Crossref yield findings
omitted after character400 in the 7Nov Garden Evidence Guide qualification.
"""
import unittest
from chatify import schema,prompts,providers
from chatify.pipeline import Engine
from chatify.store import Store
class Model:
 def __init__(self,output='1'):self.output=output;self.messages=[]
 def complete(self,messages):self.messages.append(messages);return self.output
class FullAbstract(unittest.TestCase):
 def engine(self,output='1'):
  cfg=schema.validate({'provider':{'type':'openai','model':'fixture'},'sources':[]});m=Model(output);e=Engine(cfg,Store(':memory:'),provider=m);e.prompts=prompts.PromptStore('',initial={'on':{'relevance':True}});return e,m
 def test_default_includes_result_beyond_intro_but_remains_bounded(self):
  e,m=self.engine();text=('Introductory methods. '*35)+'RESULT: grafting did not affect fruit yield.'+(' Later details.'*100);row={'n':1,'title':'Synthetic tomato study','text':text}
  self.assertEqual(e.filter_relevant('What happened to yield?',[row]),[row]);sent=m.messages[-1][-1]['content'];self.assertIn('RESULT: grafting did not affect fruit yield.',sent);self.assertLess(len(sent),1650)
 def test_none_and_invalid_number_still_fail_closed_in_strict_path(self):
  row={'n':1,'title':'Study','text':'Findings.'}
  for output,expected in [('NONE',[]),('99',None),('nonsense',None)]:
   e,m=self.engine(output);self.assertEqual(e.filter_relevant('yield',[row],strict=True),expected)
 def test_explicit_narrow_contract_still_supported(self):
  e,m=self.engine();e.filter_relevant('yield',[{'n':1,'title':'Study','text':'A'*500+'RESULT'}],snippet=400);self.assertNotIn('RESULT',m.messages[-1][-1]['content'])
