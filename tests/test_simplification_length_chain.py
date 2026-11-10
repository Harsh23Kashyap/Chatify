"""Length instructions survive rewrites; fake replies do not prove answer quality."""
import unittest
from unittest.mock import Mock,patch
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
Q='Explain the previous answer more simply using the same sources. Keep the source links and distinguish returned metadata from full-paper reading.'
EV=[{'n':1,'id':'fixture','source':'arxiv','title':'Sparse retrieval','text':'Sparse retrieval compares methods.','url':'https://example.invalid/record','content_kind':'abstract'}]
class SimplificationLengthChain(unittest.TestCase):
 def engine(self):
  cfg=schema.validate({'provider':{'type':'openai','model':'gpt-4o-mini'},'sources':[], 'memory':{'enabled':False},'retrieval':{'query_rewrite':False,'query_expansion':False},'prompt':{'answer_note':'A fixed application note.'}})
  e=Engine(cfg,Store(':memory:'));e.provider=Mock();e.provider.complete.return_value='Sparse retrieval compares methods. [1]';e._llm_on=lambda k:True;return e
 def assert_length(self,system):
  self.assertIn('at most 116 words',system);self.assertIn('exact links',system);self.assertNotIn('complete returned authors',system);self.assertIn('sentence citations',system)
 def test_note_budget_and_generation_revision_correction_repair(self):
  e=self.engine();self.assert_length(e.prompt(Q,EV,'standard',[], '')[0]['content'])
  e.revise('Sparse retrieval compares methods. [1]',EV,Q);self.assert_length(e.provider.complete.call_args.args[0][0]['content'])
  e.correct('Sparse retrieval compares methods. [1]',EV,[{'claim':'Sparse retrieval compares methods.','uncited':True}],Q);self.assert_length(e.provider.complete.call_args.args[0][0]['content'])
  e.provider.complete.reset_mock();e.check_support=Mock(return_value='')
  e.repair_support('Sparse retrieval compares methods. [1]',EV,Q,'Note: the sources may not fully support this: test');self.assert_length(e.provider.complete.call_args_list[0].args[0][0]['content'])
 def test_explicit_bibliography_depth_and_word_count_preserved(self):
  e=self.engine()
  for q,style in [(Q+' Give the authors and years.','standard'),(Q+' Give a full answer.','standard'),(Q,'deep'),(Q+' Use exactly 300 words.','standard')]:
   with self.subTest(q=q,style=style):
    s=e.answer_constraints(q,style);self.assertIn('complete returned authors',s)
    if '300 words' in q:self.assertIn('exactly 300 words',s)
    if style=='deep' or 'full answer' in q or '300 words' in q:self.assertNotIn('at most 116 words',s)
 def test_custom_policy_unchanged_and_failure_checks_still_apply(self):
  e=self.engine();e.prompts.text=lambda key,fallback='':'CUSTOM ANSWER POLICY' if key=='answer' else fallback
  self.assertIn('CUSTOM ANSWER POLICY',e.answer_constraints(Q))
  e.provider.complete.return_value='Invented result999kg. [1]'
  r=e.repair_support('Sparse retrieval compares methods. [1]',EV,Q,'Note: the sources may not fully support this: test');self.assertIn('withheld',r[3])
 def test_sync_stream_forward_style_into_late_rewrites(self):
  for stream in (False,True):
   with self.subTest(stream=stream):
    e=self.engine();e.cfg['prompt']['auto_repair']=False;e.cfg['prompt']['model_followups']=False;e.followups=lambda *a,**k:[];e._llm_on=lambda k:False;e.retrieve=lambda *a,**k:(EV,{})
    e.provider.stream.return_value=iter(['Sparse retrieval compares methods. [1]'])
    e.check_support=Mock(return_value='Note: the sources may not fully support this: test')
    fixed=('Sparse retrieval compares methods. [1]',EV,[], '')
    with patch.object(e,'_fix',return_value=fixed[:3]) as correction,patch.object(e,'repair_support',return_value=fixed) as repair:
     chat=e.store.new_chat('u')
     if stream:list(e.ask_stream('u',chat,Q,style='deep',new_topic=True))
     else:e.ask('u',chat,Q,style='deep',new_topic=True)
    self.assertEqual(correction.call_args.kwargs['style'],'deep');self.assertEqual(repair.call_args.kwargs['style'],'deep')
if __name__=='__main__':unittest.main()
