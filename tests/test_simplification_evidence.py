import copy
from unittest.mock import patch
from customchat import schema
from customchat.pipeline import Engine
from customchat.store import Store

def test_simple_followup_reuses_accepted_evidence_without_relevance_rerun():
 cfg=copy.deepcopy(schema.DEFAULTS);store=Store(':memory:');cfg['sources']=[{'id':'s','label':'Source','type':'wikipedia'}]
 e=Engine(cfg,store,connectors={'s':object()});chat=store.new_chat('u');topic=store.new_topic('u','soil')
 ev=[{'id':'a','title':'Soil','text':'Compost adds organic matter to soil.','url':'https://example.com/soil','source':'s','score':1,'n':1,'year':'','authors':[],'venue':''}]
 store.add_turn(chat,topic,'How does compost help soil?','How does compost help soil?','Compost adds organic matter [1].',ev,[],'standard')
 with patch.object(e,'retrieve',side_effect=AssertionError('pure simplification must not search')),patch.object(e,'filter_relevant',side_effect=AssertionError('must retain accepted evidence')),patch.object(e,'check_question',return_value=''):
  r=e.ask('u',chat,'Explain the previous answer more simply using the same sources.')
 assert r['evidence'] and r['source_errors']=={}

def test_new_fact_followup_still_runs_relevance():
 cfg=copy.deepcopy(schema.DEFAULTS);store=Store(':memory:');cfg['sources']=[{'id':'s','label':'Source','type':'wikipedia'}]
 e=Engine(cfg,store,connectors={'s':object()});chat=store.new_chat('u');topic=store.new_topic('u','soil')
 ev=[{'id':'a','title':'Soil','text':'Compost adds organic matter.','url':'https://example.com/soil','source':'s','score':1,'n':1,'year':'','authors':[],'venue':''}]
 store.add_turn(chat,topic,'How does compost help soil?','How does compost help soil?','Organic matter [1].',ev,[],'standard')
 with patch.object(e,'retrieve',return_value=([],{})),patch.object(e,'filter_relevant',return_value=[]) as relevance,patch.object(e,'check_question',return_value=''):
  r=e.ask('u',chat,'What does the previous source say about pesticides?')
 assert relevance.called and not r['evidence']

def test_simplification_with_new_subject_must_search():
 cfg=copy.deepcopy(schema.DEFAULTS);store=Store(':memory:');e=Engine(cfg,store,connectors={});chat=store.new_chat('u');topic=store.new_topic('u','soil')
 assert e.simplification_evidence('u',chat,topic,'Explain the previous source more simply and compare pesticide safety.')==[]
