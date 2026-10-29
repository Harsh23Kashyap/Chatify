import unittest
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class EarlierEvidence(unittest.TestCase):
 def setup_history(self):
  e=Engine(schema.validate({'sources':[{'id':'s','type':'wikipedia','label':'Source'}]}),Store(':memory:'),connectors={'s':object()})
  chat=e.store.new_chat('u');topic=e.store.new_topic('u','diet')
  ev=[{'n':1,'id':'diet','title':'Diet diabetes','text':'Diet diabetes evidence','source':'s','year':'2023','url':'https://example.org'}]
  first=e.store.add_turn(chat,topic,'Compare diet diabetes evidence','Compare diet diabetes evidence','Diet findings [1].',ev,[],'standard')
  e.store.add_turn(chat,topic,'Personal dose?','Personal dose?','Cannot give personal doses.',[],[],'standard')
  return e,chat,topic,first
 def test_explicit_earlier_named_comparison_reuses_evidence(self):
  e,c,t,_=self.setup_history()
  q='Return to the earlier diet diabetes comparison and explain it more simply using the same cited sources.'
  self.assertEqual(e.simplification_evidence('u',c,t,q)[0]['id'],'diet')
 def test_new_fact_is_not_a_reword(self):
  e,c,t,_=self.setup_history()
  self.assertEqual(e.simplification_evidence('u',c,t,'Return to earlier diet diabetes evidence and compare insulin safety.'),[])
 def test_unmatched_target_is_not_guessed(self):
  e,c,t,_=self.setup_history()
  self.assertEqual(e.simplification_evidence('u',c,t,'Return to the earlier soil fertilizer comparison and explain it more simply using the same sources.'),[])
 def test_scoped_history_remains_excluded(self):
  e,c,t,first=self.setup_history();e.store.save_state('u','scope-'+first,{'source':'s'})
  self.assertEqual(e.simplification_evidence('u',c,t,'Return to the earlier diet diabetes comparison and explain it more simply using the same sources.'),[])
 def test_deselected_sources_remain_excluded(self):
  e,c,t,_=self.setup_history()
  self.assertEqual(e.simplification_evidence('u',c,t,'Return to the earlier diet diabetes comparison and explain it more simply using the same sources.',sources=[]),[])
 def test_sync_and_stream_use_named_return_without_fresh_search(self):
  from unittest.mock import patch
  for stream in (False,True):
   e,c,t,_=self.setup_history()
   q='Return to the earlier diet diabetes comparison and explain it more simply using the same cited sources.'
   with patch.object(e,'retrieve',side_effect=AssertionError('not a fresh-search request')),patch.object(e,'filter_relevant',side_effect=AssertionError('retain selected accepted passages')):
    r=next(d for k,d in e.ask_stream('u',c,q,topic=t) if k=='done') if stream else e.ask('u',c,q,topic=t)
   self.assertEqual(r['evidence'][0]['id'],'diet')
 def test_other_topic_never_selected(self):
  e,c,t,_=self.setup_history();other=e.store.new_topic('u','other')
  self.assertEqual(e.simplification_evidence('u',c,other,'Return to the earlier diet diabetes comparison and explain it more simply using the same sources.'),[])
 def test_ambiguous_matching_turns_not_guessed(self):
  e,c,t,_=self.setup_history()
  e.store.add_turn(c,t,'Compare diet diabetes outcomes','Compare diet diabetes outcomes','Different findings [1].',[{'n':1,'id':'other','title':'Other','text':'Other','source':'s','year':'2024'}],[],'standard')
  self.assertEqual(e.simplification_evidence('u',c,t,'Return to the earlier diet diabetes comparison and explain it more simply using the same sources.'),[])
 def test_other_owner_never_selected(self):
  e,c,t,_=self.setup_history()
  with self.assertRaises(PermissionError):
   e.simplification_evidence('other',c,t,'Return to the earlier diet diabetes comparison and explain it more simply using the same sources.')

 def test_named_return_fallback_uses_unique_same_topic_sources(self):
  e,c,t,_=self.setup_history()
  q='Return to our diet diabetes comparison and explain the design.'
  self.assertEqual(e.named_return_evidence('u',c,t,q)[0]['id'],'diet')
  self.assertEqual(e.named_return_evidence('u',c,t,q,sources=[]),[])
  self.assertEqual(e.named_return_evidence('u',c,t,'Return to our soil fertilizer comparison and explain the design.'),[])
  with self.assertRaises(PermissionError):e.named_return_evidence('other',c,t,q)
 def test_named_return_fallback_rejudges_after_fresh_empty(self):
  from unittest.mock import patch
  for stream in (False,True):
   e,c,t,_=self.setup_history();q='Return to our diet diabetes comparison and explain the design.'
   with patch.object(e,'retrieve',return_value=([],{})),patch.object(e,'filter_relevant',side_effect=lambda q,ev,**kw:ev) as judge:
    r=next(d for k,d in e.ask_stream('u',c,q,topic=t) if k=='done') if stream else e.ask('u',c,q,topic=t)
   self.assertEqual(r['evidence'][0]['id'],'diet')
   self.assertTrue(judge.call_args.kwargs['strict'])
 def test_named_return_retains_target_question_during_fresh_retrieval(self):
  from unittest.mock import patch
  for stream in (False,True):
   e,c,t,_=self.setup_history();q='Return to our diet diabetes comparison and explain randomized assignment.'
   seen=[]
   def retrieve(question,*args,**kwargs):seen.append(question);return [],{}
   with patch.object(e,'standalone',return_value='Explain PREDIMED randomized assignment.'),patch.object(e,'retrieve',side_effect=retrieve),patch.object(e,'filter_relevant',return_value=[]):
    if stream:list(e.ask_stream('u',c,q,topic=t))
    else:e.ask('u',c,q,topic=t)
   self.assertIn('Earlier comparison being revisited: Compare diet diabetes evidence',seen[0])
 def test_deselected_named_target_never_adds_context(self):
  e,c,t,_=self.setup_history()
  self.assertFalse(e.named_return_evidence('u',c,t,'Return to our diet diabetes comparison and explain it.',sources=[],return_question=True))
 def test_later_return_does_not_replace_original_comparison_target(self):
  e,c,t,_=self.setup_history()
  e.store.add_turn(c,t,'Return to our diet diabetes comparison and explain assignment.','Explain assignment','Adjacent trial facts [1].',[{'n':1,'id':'adjacent','title':'Trial','text':'Trial methods','source':'s','year':'2013'}],[],'standard')
  q='Return to our diet diabetes comparison and explain adherence.'
  self.assertEqual(e.named_return_evidence('u',c,t,q,return_question=True),'Compare diet diabetes evidence')
  self.assertEqual(e.named_return_evidence('u',c,t,q)[0]['id'],'diet')
 def test_named_return_relevant_original_preferred_over_adjacent_fresh(self):
  from unittest.mock import patch
  for stream in (False,True):
   for anchor_relevant in (False,True):
    e,c,t,_=self.setup_history();q='Return to our diet diabetes comparison and explain randomized assignment.'
    adjacent=[{'n':1,'id':'adjacent','title':'Different diabetes trial','text':'Adjacent trial','source':'s','year':'2025'}]
    def judge(question,ev,**kw):return ev if not kw.get('strict') or anchor_relevant else []
    with patch.object(e,'retrieve',return_value=(adjacent,{})),patch.object(e,'filter_relevant',side_effect=judge):
     r=next(d for k,d in e.ask_stream('u',c,q,topic=t) if k=='done') if stream else e.ask('u',c,q,topic=t)
    self.assertEqual(r['evidence'][0]['id'],'diet' if anchor_relevant else 'adjacent')
