"""Control-flow diagnostics only, no model-semantic acceptance claim."""
import json,os,unittest
from unittest.mock import Mock,patch
from chatify import schema,providers
from chatify.pipeline import Engine
from chatify.store import Store
EV=[{'n':1,'title':'Private source title','text':'The mountain has a steep profile.'}]
ANSWER='The mountain has a steep profile. [1]'
NOTE='Note: the sources may not fully support this: private unsupported detail'
class Diagnostics(unittest.TestCase):
 def engine(self):
  e=Engine(schema.validate({}),Store(':memory:'));e.cfg['provider']['type']='openai';e.provider=Mock();e.prompts.save('faithfulness',on=True);return e
 def events(self,logger):return [json.loads(c.args[1]) for c in logger.warning.call_args_list]
 def test_default_off_and_exact_optin(self):
  for value in ('','true','0','yes'):
   with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':value}),patch('chatify.pipeline.logging.getLogger') as log:
    Engine._support_diagnostic('repair','provider_error',evidence_count=1);log.assert_not_called()
 def test_fixed_metadata_drops_context_secrets_and_invalid_values(self):
  with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'1'}),patch('chatify.pipeline.logging.getLogger') as log:
   Engine._support_diagnostic('repair','started',evidence_count=1,question='private question',context='private profile',provider_error='secret',flagged_rows=True,uncited_rows=-1,contract_errors='secret')
   self.assertEqual(self.events(log.return_value),[{'stage':'repair','outcome':'started','evidence_count':1}])
   Engine._support_diagnostic('private context','started');Engine._support_diagnostic('check','private verdict');self.assertEqual(log.return_value.warning.call_count,1)
 def test_check_outcomes_and_unchanged_returns(self):
  cases=[('OK','accepted',''),('UNSUPPORTED: private claim','unsupported','may not fully'),('OK with extra private text','invalid_contract','invalid result'),(providers.ProviderError('private credential error'),'provider_error','could not be completed')]
  for result,reason,expected in cases:
   e=self.engine()
   if isinstance(result,Exception):e.provider.complete.side_effect=result
   else:e.provider.complete.return_value=result
   with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'1'}),patch('chatify.pipeline.logging.getLogger') as log:
    actual=e.check_support(ANSWER,EV,context='private question and history')
    if expected:self.assertIn(expected,actual)
    else:self.assertEqual(actual,'')
    events=self.events(log.return_value);self.assertEqual(events[-1]['outcome'],reason)
    self.assertNotIn('private',json.dumps(events));self.assertEqual(e.provider.complete.call_count,1)
 def test_all_repair_failure_branches_and_success(self):
  cases=['provider_error','invalid_contract','short_candidate','no_selected_evidence','local_ledger_rejected','recheck_rejected','accepted']
  for reason in cases:
   e=self.engine();e.provider.complete.return_value=ANSWER
   if reason=='provider_error':e.provider.complete.side_effect=providers.ProviderError('private error')
   if reason=='invalid_contract':e.provider.complete.return_value=ANSWER+' [999]'
   if reason=='short_candidate':e.provider.complete.return_value=''
   e.tidy=Mock(return_value=(ANSWER,[] if reason=='no_selected_evidence' else EV))
   e.ledger=Mock(return_value=[{'claim':'private claim','supported':reason!='local_ledger_rejected','uncited':reason=='local_ledger_rejected'}])
   e.check_support=Mock(return_value='unverified' if reason=='recheck_rejected' else '')
   with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'1'}),patch('chatify.pipeline.logging.getLogger') as log:
    a,v,l,n=e.repair_support(ANSWER,EV,'private question',NOTE,context='private context')
    events=self.events(log.return_value);self.assertEqual(events[-1]['outcome'],reason)
    if reason=='accepted':self.assertEqual(a,ANSWER);self.assertEqual(n,'')
    else:self.assertIn('No recommendation is provided',a);self.assertEqual(l,[]);self.assertIn('withheld',n)
    self.assertNotIn('private',json.dumps(events));self.assertEqual(e.provider.complete.call_count,1)
 def test_diagnostic_failure_does_not_change_safety_result(self):
  e=self.engine();e.provider.complete.side_effect=providers.ProviderError('secret')
  with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'1'}),patch('chatify.pipeline.logging.getLogger',side_effect=RuntimeError('logger unavailable')):
   result=e.repair_support(ANSWER,EV,'question',NOTE);self.assertIn('No recommendation is provided',result[0])
 def test_warning_only_does_not_trigger_repair_or_diagnostic(self):
  e=self.engine()
  with patch.dict(os.environ,{'CHATIFY_SUPPORT_DIAGNOSTICS':'1'}),patch('chatify.pipeline.logging.getLogger') as log:
   result=e.repair_support(ANSWER,EV,'q','Note: the support check returned an invalid result; support was not verified.')
   self.assertEqual(result[0],ANSWER);e.provider.complete.assert_not_called();log.assert_not_called()
