"""Metadata control-flow coverage, not live retrieval or model qualification."""
import copy, importlib.util, json, os, unittest
from pathlib import Path
from unittest.mock import Mock, patch
from chatify import schema, providers
from chatify.pipeline import Engine
from chatify.diagnostics import retrieval_diagnostic
from chatify.store import Store
from chatify.connectors.base import Evidence

Q='Show current USGS magnitude and depth records'
EV=Evidence('USGS magnitude record', 'USGS magnitude 5.0 depth km: 20. Current past-day record.', 'https://example.invalid/private-id',source='private-source',score=1,id='private-id')
class Diagnostics(unittest.TestCase):
 def engine(self, rows=None):
  c=Mock();c.search.return_value=copy.deepcopy([EV] if rows is None else rows)
  # No refresh contract unless explicitly tested.
  del c.refresh
  cfg=schema.validate({'provider':{'type':'mock'},'sources':[{'id':'private-source','type':'python','label':'Private','entry':'unused:unused'}], 'retrieval':{'query_rewrite':False,'query_expansion':False,'cache_ttl':0},'memory':{'enabled':False}})
  e=Engine(cfg,Store(':memory:'),connectors={'private-source':c});e.provider=Mock();return e,c
 def events(self,log):return [json.loads(c.args[1]) for c in log.warning.call_args_list]
 def test_default_off_and_filter(self):
  for v in ('','0','true','yes'):
   with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':v}),patch('chatify.diagnostics.logging.getLogger') as log:
    retrieval_diagnostic('feed','parsed',feature_count=8);log.assert_not_called()
  with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'1'}),patch('chatify.diagnostics.logging.getLogger') as log:
   retrieval_diagnostic('feed','parsed',feature_count=8,output_count=True,input_count=-1,source_count='secret',question='secret',source='private-id',raw_verdict='secret')
   retrieval_diagnostic('private','parsed');retrieval_diagnostic('feed','secret');retrieval_diagnostic('relevance','parsed')
   self.assertEqual(self.events(log.return_value),[{'stage':'feed','outcome':'parsed','feature_count':8}])
 def test_retrieval_empty_nonempty_errors_and_caches_do_not_change(self):
  for kind in ('valid','empty','error','offtopic','unusable','low_score','duplicate','no_sources','memory','disk','refresh_error'):
   answers=[]
   for mode in ('off','on','logger_failure'):
    rows={'empty':[],'offtopic':[dict(EV,title='Tennis tournament',text='Tennis tournament score tennis player')],'unusable':[dict(EV,text='')],'low_score':[dict(EV,score=-1)],'duplicate':[EV,EV]}.get(kind,[EV])
    e,c=self.engine(rows)
    if kind=='error':c.search.side_effect=OSError('private server details')
    if kind=='disk':e._disk_get=Mock(return_value=[copy.deepcopy(EV)])
    if kind=='refresh_error':c.refresh=Mock(side_effect=OSError('private file path'))
    with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'0' if mode=='off' else '1'}),patch('chatify.diagnostics.logging.getLogger',side_effect=RuntimeError('broken') if mode=='logger_failure' else None) as log:
     a=e.retrieve(Q,source_ids=[] if kind=='no_sources' else None)
     if kind=='memory':a=e.retrieve(Q)
     answers.append((a,c.search.call_count))
     if mode=='on':
      ev=self.events(log.return_value);self.assertTrue(ev);self.assertNotIn('private',json.dumps(ev));self.assertNotIn(Q,json.dumps(ev));self.assertTrue(all(set(x)<={'stage','outcome','source_count','evidence_count','error_count','denied_count','unusable_count','duplicate_count','below_score_count'} for x in ev))
      expected={'memory':'memory_cache','disk':'disk_cache','no_sources':'selected','refresh_error':'os_error','error':'os_error'}.get(kind,'complete');self.assertIn(expected,[x['outcome']for x in ev])
   self.assertEqual(answers[0],answers[1],kind);self.assertEqual(answers[0],answers[2],kind)
 def test_connector_exception_categories_and_partial_results(self):
  from chatify.connectors.open_sources import SetupRequired
  for exc,expected in [(OSError('private host'),'os_error'),(ValueError('private parser'),'value_error'),(SetupRequired('private setup'),'setup_required'),(RuntimeError('private failure'),'error')]:
   e,c=self.engine();e.queries=Mock(return_value=['first','second']);c.search.side_effect=[[copy.deepcopy(EV)],exc]
   with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'1'}),patch('chatify.diagnostics.logging.getLogger') as log:
    found,errors=e.retrieve(Q);self.assertEqual(len(found),1);self.assertEqual(len(errors),1);self.assertIn(expected,[x['outcome']for x in self.events(log.return_value)]);self.assertNotIn('private',json.dumps(self.events(log.return_value)))
 def test_generator_connector_not_changed_by_count(self):
  e,c=self.engine();c.search.return_value=(x for x in [copy.deepcopy(EV)])
  with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'1'}):self.assertEqual(len(e.retrieve(Q)[0]),1)
 def test_question_and_relevance_outcomes_preserve_behavior_calls(self):
  for stage in ('question','relevance'):
   for kind in ('disabled','mock','empty','accepted','none','refused','invalid','provider_error','no_key'):
    results=[]
    for mode in ('off','on','logger_failure'):
     e,_=self.engine();e.cfg['provider']['type']='mock' if kind=='mock' else 'openai';e._llm_on=Mock(return_value=kind!='disabled')
     if kind in ('provider_error','no_key'):e.provider.complete.side_effect=providers.ProviderError('No API key yet' if kind=='no_key' else 'private error')
     else:e.provider.complete.return_value={'none':'NONE','refused':'INVALID: private reason','invalid':'private malformed','accepted':'VALID' if stage=='question' else '1'}.get(kind,'VALID' if stage=='question' else '1')
     with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'0' if mode=='off' else '1'}),patch('chatify.diagnostics.logging.getLogger',side_effect=RuntimeError('bad logger') if mode=='logger_failure' else None) as log:
      a=e.check_question(Q) if stage=='question' else (e.filter_relevant(Q,[] if kind=='empty' else [dict(EV,n=1)],strict=False),e.filter_relevant(Q,[] if kind=='empty' else [dict(EV,n=1)],strict=True))
      results.append((a,e.provider.complete.call_count))
      if mode=='on':
       ev=self.events(log.return_value);self.assertNotIn('private',json.dumps(ev))
       expected=({'disabled':'disabled','none':'invalid_contract','refused':'refused','invalid':'invalid_contract','provider_error':'provider_error','no_key':'no_key'}.get(kind,'accepted') if stage=='question' else {'disabled':'disabled','mock':'mock','empty':'empty_input','none':'none','refused':'invalid_contract','invalid':'invalid_contract','provider_error':'provider_error','no_key':'provider_error'}.get(kind,'selected'))
       self.assertEqual(ev[-1]['outcome'],expected,(stage,kind))
    self.assertEqual(results[0],results[1],(stage,kind));self.assertEqual(results[0],results[2],(stage,kind))

 def test_scope_and_document_permission_empties(self):
  e,c=self.engine();e.cfg['sources'][0]['read_users']=[]
  with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'1'}),patch('chatify.diagnostics.logging.getLogger') as log:
   self.assertEqual(e.retrieve(Q,scope={'source':'private-source','document':'private-file'}),([],{}));self.assertEqual(self.events(log.return_value)[-1]['outcome'],'scope_denied');c.search.assert_not_called()
  e,c=self.engine([dict(EV,document='private-file')]);e.cfg['sources'][0]['document_users']={'private-file':['permitted']};c.docs=[{'document':'private-file'}]
  with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'1'}),patch('chatify.diagnostics.logging.getLogger') as log:
   self.assertEqual(e.retrieve(Q,owner='not-permitted'),([],{}));self.assertTrue(any(x.get('denied_count')==1 for x in self.events(log.return_value)))
 def test_stream_and_sync_answer_equality_default_optin_broken_logger(self):
  for stream in (False,True):
   for empty in (False,True):
    results=[]
    for mode in ('off','on','logger_failure'):
     e,c=self.engine([] if empty else [EV]);e.provider=providers.Mock(e.cfg['provider'])
     with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'0' if mode=='off' else '1'}),patch('chatify.diagnostics.logging.getLogger',side_effect=RuntimeError('bad logger') if mode=='logger_failure' else None):
      chat=e.store.new_chat('owner')
      answer=list(e.ask_stream('owner',chat,Q))[-1][1] if stream else e.ask('owner',chat,Q)
      results.append({k:answer[k] for k in ('answer','evidence','ledger','source_errors','model_status') if k in answer})
    self.assertEqual(results[0],results[1]);self.assertEqual(results[0],results[2])

class FeedDiagnostics(unittest.TestCase):
 def module(self):
  spec=importlib.util.spec_from_file_location('quake_diag',Path(__file__).resolve().parents[1]/'apps/quakebrief/quake_sources.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 def test_feed_results_errors_and_cache_unchanged(self):
  feed={'metadata':{'generated':1000000000},'features':[{'id':'private-id','properties':{'type':'earthquake','mag':5.0,'time':1000000000,'url':'https://earthquake.usgs.gov/earthquakes/eventpage/private-id','title':'Private title'},'geometry':{'coordinates':[1,2,30]}}]}
  for kind in ('valid','empty','format','timestamp_invalid','future','stale','http','json','oversize','cached','parse_exception'):
   results=[]
   for mode in ('off','on','logger_failure'):
    m=self.module();data=copy.deepcopy(feed)
    if kind=='empty':data['features']=[]
    if kind=='format':data={}
    if kind=='parse_exception':data['features']=[{'properties':7}]
    if kind=='timestamp_invalid':data['metadata']['generated']='secret'
    if kind=='future':data['metadata']['generated']=1001000000
    if kind=='stale':data['metadata']['generated']=990000000
    response=Mock();response.__enter__=Mock(return_value=response);response.__exit__=Mock(return_value=False);response.read.return_value=b'bad private json' if kind=='json' else b'X'*1000001 if kind=='oversize' else json.dumps(data).encode()
    if kind=='cached':m._CACHE=(1000,data)
    with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'0' if mode=='off' else '1'}),patch('chatify.diagnostics.logging.getLogger',side_effect=RuntimeError('broken') if mode=='logger_failure' else None) as log,patch.object(m.time,'time',return_value=1000000),patch.object(m.time,'monotonic',return_value=1000),patch.object(m.urllib.request,'urlopen',return_value=response,side_effect=OSError('private address') if kind=='http' else None) as http:
     try:answer=('ok',m.quakes(Q))
     except Exception as exc:answer=(type(exc).__name__,str(exc))
     results.append((answer,http.call_count))
     if mode=='on':
      ev=Diagnostics().events(log.return_value);self.assertTrue(ev);self.assertNotIn('private',json.dumps(ev).lower());self.assertNotIn('https',json.dumps(ev))
      expected={'valid':'parsed','empty':'parsed','format':'format_error','timestamp_invalid':'timestamp_invalid','future':'timestamp_future','stale':'timestamp_stale','http':'http_error','json':'json_error','oversize':'oversize','cached':'cached','parse_exception':'parse_error'}[kind]
      self.assertIn(expected,[x['outcome']for x in ev])
   self.assertEqual(results[0],results[1],kind);self.assertEqual(results[0],results[2],kind)
