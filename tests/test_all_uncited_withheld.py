"""Citation-presence boundary, not lexical semantic verification."""
import json,pathlib,unittest,tempfile
from unittest.mock import Mock,patch
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
EV=[{'n':1,'id':'event','title':'USGS event','text':'USGS event. Magnitude 4.6. Depth 103.682 km.','year':'2026','url':'fixture:usgs'}]
class NoCitations(unittest.TestCase):
 def engine(self,output,store=None):
  e=Engine(schema.validate({'provider':{'type':'openai','model':'gpt-4o-mini'},'memory':{'enabled':False},'prompt':{'model_followups':False,'revise':False},'sources':[]}),store or Store(':memory:'));e._llm_on=lambda key:False;e.provider=Mock();e.provider.complete.return_value=output;e.provider.stream.return_value=iter([output[:20],output[20:]]);e.followups=lambda *a:[];e.retrieve=lambda *a,**kw:(EV,{});e.filter_relevant=lambda q,x:x;return e
 def run_answer(self,e,stream):
  c=e.store.new_chat('u')
  if stream:
   events=list(e.ask_stream('u',c,'Show the earthquake records'));r=next(v for k,v in events if k=='done');tokens=''.join(v for k,v in events if k=='token')
  else:r=e.ask('u',c,'Show the earthquake records');tokens=r['answer']
  return r,tokens
 def test_long_short_empty_mixed_refusal_and_unknown_ids_fail_closed(self):
  outputs=['Earthquakes are safe everywhere today. '*8,'Safe today.','', 'I cannot establish safety from these sources, but apply the recommended dose to your farm.', 'No evidence is available, but Delhi is definitely safe today.','Unsupported claim. [999]','Please provide your crop and soil test results.']
  for stream in (False,True):
   for output in outputs:
    with self.subTest(stream=stream,output=output):
     e=self.engine(output)
     with patch.object(e,'_fix',side_effect=AssertionError('No repair/model call after no citations')),patch.object(e,'check_support',side_effect=AssertionError('No semantic support claim for withheld text')):r,tokens=self.run_answer(e,stream)
     self.assertIn('model answer was withheld',r['answer']);self.assertEqual(r['model_status'],'invalid_answer');self.assertEqual(tokens,r['answer']);self.assertEqual(r['evidence'],[]);self.assertEqual(r['ledger'],[]);self.assertFalse(r['answer_verified']);self.assertEqual(e.store.turn('u',r['id'])['answer'],r['answer']);self.assertEqual(e.provider.stream.call_count+e.provider.complete.call_count,1)
 def test_cited_answer_preserved(self):
  output='USGS event magnitude was 4.6. [1]'
  for stream in (False,True):
   e=self.engine(output)
   with patch.object(e,'_fix',side_effect=lambda a,v,l,*args,**kw:(a,v,l)):r,t=self.run_answer(e,stream)
   self.assertEqual(r['answer'],output);self.assertEqual(r['evidence'],EV)
 def test_no_evidence_configured_clarification_unchanged(self):
  for stream in (False,True):
   e=self.engine('must not run');e.retrieve=lambda *a,**kw:([],{});e.cfg['prompt']['no_evidence']='Please provide crop, location, soil test and growth stage.'
   r,t=self.run_answer(e,stream);self.assertEqual(r['answer'],e.cfg['prompt']['no_evidence']);e.provider.complete.assert_not_called();e.provider.stream.assert_not_called()
 def test_scope_refusal_unchanged(self):
  for stream in (False,True):
   e=self.engine('must not run');e.check_question=lambda *a:'Outside app scope.';r,t=self.run_answer(e,stream);self.assertEqual(r['answer'],'Outside app scope.');self.assertEqual(r['response_kind'],'question_refused');e.provider.complete.assert_not_called();e.provider.stream.assert_not_called()
 def test_actual_organic_uncited_list_replayed_without_new_calls(self):
  p=pathlib.Path(__file__).parent/'fixtures/organic_quake_uncited.json';output=json.loads(p.read_text())['answer']
  self.assertIn('significant seismic activity',output);self.assertNotIn('[1]',output)
  for stream in (False,True):
   with tempfile.TemporaryDirectory() as tmp:
    path=tmp+'/history.db';e=self.engine(output,Store(path));r,t=self.run_answer(e,stream);self.assertNotIn('significant seismic',t);self.assertIn('model answer was withheld',t);reopened=Store(path).turn('u',r['id']);self.assertEqual(reopened['answer'],r['answer']);self.assertEqual(reopened['ledger'],[])
