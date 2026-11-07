"""Regression for the deployed Weather null-address and retained 30-area failure.

The null provider address is from apps/weatherchat/app.yaml at 17dd921,
confirmed by live /weatherchat/api/settings on 2026-11-07. Model outputs here
are fixtures, not evidence of generated answer quality.
"""
import copy,json,tempfile,time,unittest,yaml
from pathlib import Path
from unittest.mock import patch
from chatify import appbuilder,buildjobs,builddrafts,schema
from test_buildjobs import Fixture

class SavedProviderRecovery(unittest.TestCase):
 def wait(self,jobs,ident):
  for _ in range(500):
   data=jobs.view('owner',ident)
   if data['state']!='running':return data
   time.sleep(.01)
  self.fail('local fixture timed out')
 def test_null_blank_share_runtime_and_builder_contract(self):
  for kind,model in [('openai','gpt-4o-mini'),('ollama','llama3.2')]:
   raw={'provider':{'type':kind,'model':model,'base_url':None}}
   before=copy.deepcopy(raw)
   self.assertEqual(schema.validate(raw)['provider']['base_url'],'')
   self.assertEqual(appbuilder.validate(yaml.safe_dump(raw))['provider']['base_url'],'')
   self.assertEqual(raw,before)
  for value in (False,7,[],{}):
   with self.assertRaisesRegex(ValueError,'Expected text'):
    appbuilder.validate(yaml.safe_dump({'provider':{'base_url':value}}))
 def test_real_weather_config_canonical_address(self):
  cfg=schema.load(str(Path(__file__).resolve().parents[1]/'apps/weatherchat/app.yaml'))
  self.assertEqual(cfg['provider']['base_url'],'')
  checked=appbuilder.validate(yaml.safe_dump({'provider':cfg['provider']}))
  self.assertEqual(checked['provider'],cfg['provider'])
 @patch('chatify.buildimages.capability',return_value={'available':False,'note':'fixture'})
 def test_30_ready_local_recovery_zero_calls_and_saved_reopen(self,cap):
  with tempfile.TemporaryDirectory() as tmp:
   drafts=builddrafts.BuildDrafts(tmp);jobs=buildjobs.BuildJobs(drafts=drafts,spend_dir=tmp)
   cfg=copy.deepcopy(schema.DEFAULTS);cfg['provider'].update(type='openai',model='gpt-4o-mini',api_key_env='OPENAI_API_KEY',base_url=None)
   fixture=Fixture();real_validate=appbuilder.validate
   def legacy_gate(text):
    raw=yaml.safe_load(text)
    if set(raw)=={'provider'} and raw['provider'].get('base_url') is None:raise ValueError('Expected text at .provider.base_url')
    return real_validate(text)
   with patch.object(appbuilder,'validate',side_effect=legacy_gate):
    partial=self.wait(jobs,jobs.start('owner',fixture,cfg,{'brief':'Garden advice'})['id'])
   self.assertEqual(partial['state'],'partial',partial['errors'])
   self.assertEqual(partial['completed'],30)
   self.assertEqual(partial['errors'],{'config:provider':'Expected text at .provider.base_url'})
   ident=partial['id'];ready=copy.deepcopy(jobs.jobs[ident]['parts']);calls=len(fixture.calls);spend=copy.deepcopy(jobs.spend)
   recovered=jobs.review_saved_provider('owner',ident)
   self.assertEqual(recovered['state'],'done');self.assertEqual(recovered['completed'],31)
   self.assertEqual(len(fixture.calls),calls);self.assertEqual(jobs.spend,spend)
   self.assertEqual(recovered['calls'],partial['calls'])
   self.assertEqual(recovered['review']['review_status'],'not_run')
   self.assertIn('not run',recovered['review']['review_note'])
   for key,value in ready.items():self.assertEqual(jobs.jobs[ident]['parts'][key],value,key)
   expected=copy.deepcopy(cfg['provider']);expected['base_url']=''
   self.assertEqual(yaml.safe_load(recovered['yaml'])['provider'],expected)
   self.assertEqual(cfg['provider']['base_url'],None,'caller-owned input unchanged')
   reopened=drafts.get('owner',ident);stored=yaml.safe_load(reopened['yaml']);original=yaml.safe_load(recovered['yaml']);self.assertEqual(stored['provider']['model'],original['provider']['model']);self.assertEqual(stored['provider']['base_url'],'');self.assertEqual(stored['provider']['api_key_env'],'','existing draft privacy policy excludes credential references');self.assertEqual(stored['app'],original['app']);self.assertEqual(stored['pipeline_prompts'],original['pipeline_prompts'])
   self.assertEqual(len(drafts.list('owner')),1);self.assertIn('Final model review was not run',reopened['review_note']);drafts.put('owner',reopened['yaml'],ident=ident);self.assertEqual(drafts.get('owner',ident)['review_note'],reopened['review_note'])
   self.assertEqual(jobs.jobs[ident]['cfg']['provider']['model'],'gpt-4o-mini')
   with self.assertRaisesRegex(ValueError,'not found'):jobs.review_saved_provider('other-owner',ident)
   with self.assertRaisesRegex(ValueError,'isolated'):jobs.review_saved_provider('owner',ident)
 def test_recovery_rejects_other_failures_and_keeps_state(self):
  jobs=buildjobs.BuildJobs();job={'id':'x','owner':'owner','state':'partial','errors':{'config:provider':'Authentication failed'},'parts':{},'cfg':copy.deepcopy(schema.DEFAULTS)};jobs.jobs['x']=job;before=copy.deepcopy(job)
  with self.assertRaisesRegex(ValueError,'not applicable'):jobs.review_saved_provider('owner','x')
  self.assertEqual(job,before)
  job['errors']={'config:provider':'Expected text at .provider.base_url'}
  with self.assertRaisesRegex(ValueError,'Every other'):jobs.review_saved_provider('owner','x')

if __name__=='__main__':unittest.main()
