"""Bounded repair mechanics; fixtures alone do not establish semantic truth."""
import json
import unittest
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store

class UncitedSectionRepair(unittest.TestCase):
 def setup_engine(self, output):
  e=Engine(schema.validate({}),Store(':memory:'));e.cfg['provider']['type']='openai'
  class P:
   def complete(self,m):
    self.messages=m
    if m[0]['content'].startswith('Check each replacement'):
     return json.dumps({'supported':{'0':True,'1':True}})
    return output
  e.provider=P();e.check_support=lambda *args,**kwargs:''
  return e
 def sample(self):
  return ('The survey studied forest habitat conservation across regions.\n\n'+'The survey studied forest habitat conservation across regions. [1]'+'\n\nThe long term outcomes remain uncertain across all regions.', [{'n':1,'title':'Survey','text':'The survey studied forest habitat conservation across regions. The survey lacked a comparator group.'}])
 def run_repair(self,e):
  a,v=self.sample();return e.repair_support(a,v,'What did this survey address?','Note: the sources may not fully support this: '+a[:30])
 def test_all_flags_sent_even_when_warning_truncated(self):
  e=self.setup_engine('{}');self.run_repair(e)
  payload=json.loads(e.provider.messages[-1]['content'])
  self.assertIn('long term outcomes',json.dumps(payload['uncited_sentences']))
 def test_invalid_json_and_wrong_key_count_retain_warning(self):
  for out in ('not json','{"replacements": {"0": "one"}}','{"replacements": []}'):
   e=self.setup_engine(out);a,_,_,n=self.run_repair(e);self.assertEqual(a,self.sample()[0]);self.assertTrue(n)
 def test_invalid_citations_rejected_before_renumbering(self):
  a,v=self.sample();e=self.setup_engine(json.dumps({'replacements':{'0':{'text':'The survey studied forest habitat conservation across regions.','source_id':99},'1':{'text':'The survey lacked a comparator group.','source_id':1}}}));out,_,_,note=self.run_repair(e);self.assertEqual(out,a);self.assertTrue(note)
 def test_unsupported_new_number_retains_original(self):
  e=self.setup_engine(json.dumps({'replacements':{'0':{'text':'The survey studied forest habitat conservation across 99 regions.','source_id':1},'1':{'text':'The survey lacked a comparator group.','source_id':1}}}));a,_,_,n=self.run_repair(e);self.assertEqual(a,self.sample()[0]);self.assertTrue(n)
 def test_valid_patch_preserves_other_answer_text_and_checks(self):
  e=self.setup_engine(json.dumps({'replacements':{'0':{'text':'The survey studied forest habitat conservation across regions.','source_id':1},'1':{'text':'The survey lacked a comparator group.','source_id':1}}}));a,_,ledger,n=self.run_repair(e);self.assertIn('The survey studied forest habitat conservation across regions. [1]',a);self.assertIn('lacked a comparator',a);self.assertFalse(n);self.assertTrue(all(r['supported'] for r in ledger))
 def test_omnibus_reference_pile_does_not_clear_repair(self):
  a,v=self.sample();v=v+[{'n':2,'title':'Survey two','text':v[0]['text']}]
  e=self.setup_engine(json.dumps({'replacements':{'0':'The survey studied forest habitat conservation across regions. [1] [2]','1':{'text':'The survey lacked a comparator group.','source_id':1}}}))
  out,_,_,note=e.repair_support(a,v,'Survey','Note: the sources may not fully support this: intro')
  self.assertEqual(out,a);self.assertTrue(note)
 def test_true_other_topic_borrowed_from_uncited_passage_is_rejected(self):
  a,v=self.sample();v.append({'n':2,'title':'Funding','text':'Crowdfunding conservation mechanisms mobilize funding globally.'})
  e=self.setup_engine(json.dumps({'replacements':{'0':{'text':'Crowdfunding conservation mechanisms mobilize funding globally.','source_id':1},'1':{'text':'The survey lacked a comparator group.','source_id':1}}}))
  out,_,_,note=e.repair_support(a,v,'Survey','Note: the sources may not fully support this: intro')
  self.assertEqual(out,a);self.assertTrue(note)
 def test_source_isolated_negative_verdict_keeps_original(self):
  e=self.setup_engine(json.dumps({'replacements':{'0':{'text':'The survey studied forest habitat conservation across regions.','source_id':1},'1':{'text':'The survey lacked a comparator group.','source_id':1}}}));old=e.provider.complete
  def complete(messages):
   if messages[0]['content'].startswith('Check each replacement'):return '{"supported":{"0":true,"1":false}}'
   return old(messages)
  e.provider.complete=complete;a,_,_,n=self.run_repair(e);self.assertEqual(a,self.sample()[0]);self.assertTrue(n)
 def test_general_check_failure_stays_visible(self):
  e=self.setup_engine(json.dumps({'replacements':{'0':{'text':'The survey studied forest habitat conservation across regions.','source_id':1},'1':{'text':'The survey lacked a comparator group.','source_id':1}}}));e.check_support=lambda *args,**kwargs:'Note: the support check could not be completed; support was not verified.'
  _,_,_,n=self.run_repair(e);self.assertIn('not verified',n)
