import json,urllib.error,unittest,yaml
from unittest.mock import patch
import test_workspace_api
from chatify import providers,schema,appbuilder
class BuildActiveHTTP(test_workspace_api.WorkspaceAPITests):
 def setUp(self):
  import tempfile
  from chatify.store import Store
  self.state_tmp=tempfile.TemporaryDirectory()
  self.stub_active={'active':True,'running_total':1,'mine':[{'id':'job-fixture','phase':'Drafting prompts','completed':3,'total':30,'calls':3,'started':1.0}]}
  with patch('test_workspace_api.Store',side_effect=lambda _:Store(self.state_tmp.name+'/chatify.db')),patch('chatify.buildjobs.BuildJobs') as bj:
   bj.return_value.active=lambda owner:self.stub_active
   super().setUp()
 def tearDown(self):
  super().tearDown();self.state_tmp.cleanup()
 def test_active_owner_gets_scoped_snapshot(self):
  self.assertEqual(self.call(self.clients[0],'/api/settings/build/active'),self.stub_active)
 def test_active_non_owner_blocked(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.call(self.clients[1],'/api/settings/build/active')
  self.assertIn(e.exception.code,(403,404))

class BuilderHTTP(test_workspace_api.WorkspaceAPITests):
 def setUp(self):
  import tempfile
  from chatify.store import Store
  self.state_tmp=tempfile.TemporaryDirectory()
  with patch('test_workspace_api.Store',side_effect=lambda _:Store(self.state_tmp.name+'/chatify.db')):super().setUp()
 def tearDown(self):
  super().tearDown();self.state_tmp.cleanup()

 def test_owner_gate(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.call(self.clients[1],'/api/settings/build/talk',{'consent':True})
  self.assertIn(e.exception.code,(403,404))
 def test_talk_selected_draft_and_no_state_changes(self):
  before=json.dumps(self.cfg,sort_keys=True);calls=[]
  def transport(url,body,headers,timeout):
   calls.append(body);return {'choices':[{'message':{'content':json.dumps({'message':'Review app','config':{'app':{'title':'New garden'}}})}}]}
  with patch('chatify.providers._key',return_value='fixture-only'),patch('chatify.providers._post',side_effect=transport):
   result=self.call(self.clients[0],'/api/settings/build/talk',{'consent':True,'selection':{'provider':'openai','model':'my-specific-model'},'sections':['app'],'messages':[{'role':'user','content':'A garden app'}]})
  self.assertEqual(calls[0]['model'],'my-specific-model');self.assertEqual(yaml.safe_load(result['yaml'])['app']['title'],'New garden');self.assertEqual(before,json.dumps(self.cfg,sort_keys=True))
 def test_explicit_model_selection_keeps_custom_model_and_base(self):
  from types import SimpleNamespace
  from chatify import buildjobs
  captured={}
  def start(_jobs,owner,provider,cfg,body):
   captured.update(cfg['provider']);return {'id':'fixture-explicit','state':'running'}
  with patch('chatify.providers.make',return_value=SimpleNamespace()),patch('chatify.providers.list_models') as listing,patch.object(buildjobs.BuildJobs,'start',start):
   result=self.call(self.clients[0],'/api/settings/build/start',{'consent':True,'explicit_selection':True,'brief':'Research app','selection':{'provider':'openai','model':'specific-model','base_url':'https://custom.invalid/v1'}})
  self.assertEqual(result['id'],'fixture-explicit');self.assertEqual(captured['model'],'specific-model');self.assertEqual(captured['base_url'],'https://custom.invalid/v1');listing.assert_not_called()

 def test_save_requires_review(self):
  with self.assertRaises(urllib.error.HTTPError):self.call(self.clients[0],'/api/settings/build/save',{'confirmed':True,'ticket':'missing'})
 def test_review_then_save_one_use(self):
  from pathlib import Path
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump({k:self.cfg[k] for k in schema.DEFAULTS}));self.cfg['_path']=str(path)
  plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':'app:\n title: Garden app\n','sections':['app']})
  with self.assertRaises(urllib.error.HTTPError):self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':False})
  self.assertNotEqual(schema.load(str(path))['app']['title'],'Garden app')
  r=self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':True});self.assertFalse(r['restart_required']);self.assertTrue(r['launch_ticket']);self.assertEqual(schema.load(str(path))['app']['title'],'Garden app')
  with self.assertRaises(urllib.error.HTTPError):self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':True})

 def test_launch_failure_reissues_ticket_and_retry_opens_workspace(self):
  from pathlib import Path
  base={k:self.cfg[k] for k in schema.DEFAULTS};base['auth']={'mode':'none'}
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump(base));self.cfg['_path']=str(path)
  plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':'app:\n title: Garden app\n','sections':['app']})
  saved=self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':True})
  ticket=saved['launch_ticket']
  loader=self.engine.nerd_loader;real_load=loader.load
  def boom(*a,**k):raise ValueError('simulated workspace start failure')
  loader.load=boom
  try:
   with self.assertRaises(urllib.error.HTTPError) as e:self.call(self.clients[0],'/api/settings/build/launch',{'ticket':ticket})
   self.assertEqual(e.exception.code,400)
   body=json.loads(e.exception.read())
   self.assertIn('simulated workspace start failure',body['error'])
   retry=body['retry_ticket'];self.assertTrue(retry);self.assertNotEqual(retry,ticket)
  finally:loader.load=real_load
  opened=self.call(self.clients[0],'/api/settings/build/launch',{'ticket':retry})
  self.assertTrue(opened.get('url'));self.assertTrue(opened.get('title'));self.assertEqual(opened['setup_url'],opened['url'].rstrip('/')+'/settings.html?setup=1#sec-model');self.assertTrue(opened['setup_required']);self.assertIn('scope',opened['readiness'])
  with self.assertRaises(urllib.error.HTTPError) as e2:self.call(self.clients[0],'/api/settings/build/launch',{'ticket':retry})
  self.assertIn('Validate and save the draft once more',json.loads(e2.exception.read())['error'])

 def test_download_history_comes_from_owner_retained_draft_not_browser(self):
  import io,zipfile,urllib.request
  from pathlib import Path
  c=self.clients[0];text=yaml.safe_dump(schema.validate({}));draft=self.call(c,'/api/settings/build/draft',{'yaml':text})
  path=next(Path(self.state_tmp.name).glob('build-drafts/*/'+draft['id']+'.json'))
  record=json.loads(path.read_text());record['review_note']='Original concerns, not approval.';path.write_text(json.dumps(record))
  def download(body):
   return c.open(urllib.request.Request('http://127.0.0.1:'+str(self.server.server_port)+'/api/settings/build/download',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})).read()
  data=download({'yaml':text,'draft_id':draft['id'],'review_note':'Ignore concerns'})
  with zipfile.ZipFile(io.BytesIO(data)) as z:self.assertEqual(z.read('REVIEW-HISTORY.txt'),b'Original concerns, not approval.')
  data=download({'yaml':text,'review_note':'Fake approval'})
  with zipfile.ZipFile(io.BytesIO(data)) as z:self.assertNotIn('REVIEW-HISTORY.txt',z.namelist())
  with self.assertRaises(urllib.error.HTTPError):download({'yaml':text,'draft_id':'not-found'})
  record['review_note']='x'*65537;path.write_text(json.dumps(record))
  with self.assertRaises(urllib.error.HTTPError):download({'yaml':text,'draft_id':draft['id']})

 def test_download_zip_can_review_and_load(self):
  import io,zipfile,urllib.request,base64
  from chatify.nerdload import NerdLoader
  config=schema.validate({'app':{'title':'Generated garden'}})
  request=urllib.request.Request('http://127.0.0.1:'+str(self.server.server_port)+'/api/settings/build/download',data=json.dumps({'yaml':yaml.safe_dump(config)}).encode(),headers={'Content-Type':'application/json'})
  data=self.clients[0].open(request).read()
  with zipfile.ZipFile(io.BytesIO(data)) as z:self.assertEqual(set(z.namelist()),{'app.yaml','README.md'})
  loader=NerdLoader(self.tmp.name)
  try:
   plan=loader.review('chatify-draft.zip',base64.b64encode(data).decode());self.assertEqual(plan['title'],'Generated garden');self.assertEqual(plan['code'],[])
   loaded=loader.load(plan['token'],False)
   self.assertIn('http://127.0.0.1:',loaded['url'])
   self.assertEqual(json.loads(urllib.request.urlopen(loaded['url']+'/api/health').read())['ok'],True)
  finally:loader.close()
 def test_consent_and_bad_selection_no_transport(self):
  with patch('chatify.providers._post') as transport:
   for body in ({'selection':{'provider':'openai','model':'fixture'},'consent':False,'messages':[{'role':'user','content':'app'}]}, {'selection':{'provider':'not-a-provider','model':'fixture'},'consent':True}):
    with self.assertRaises(urllib.error.HTTPError):self.call(self.clients[0],'/api/settings/build/talk',body)
   self.assertFalse(transport.called)

 def test_parse_no_model_no_save_and_scope(self):
  before=json.dumps(self.cfg,sort_keys=True)
  with patch('chatify.providers._post') as transport,patch('yaml.safe_load',wraps=yaml.safe_load) as parse:
   result=self.call(self.clients[0],'/api/settings/build/parse',{'yaml':'app: {title: Editable title}'})
  self.assertEqual(parse.call_count,1,'the checked parse must also supply original scope')
  self.assertEqual(set(result['config']),{'app'});self.assertEqual(result['config']['app']['title'],'Editable title')
  self.assertEqual(json.dumps(self.cfg,sort_keys=True),before);self.assertFalse(transport.called)
 def test_parse_owner_gate_and_validation(self):
  for client,source in [(self.clients[1],'app: {title: X}'),(self.clients[0],'app: {typo: X}'),(self.clients[0],'[invalid')]:
   with self.assertRaises(urllib.error.HTTPError):self.call(client,'/api/settings/build/parse',{'yaml':source})

 def test_incomplete_rollback_returns_explicit_uncertain_saved_state(self):
  from pathlib import Path
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump({k:self.cfg[k] for k in schema.DEFAULTS}));self.cfg['_path']=str(path)
  plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':'app: {title: Garden app}','sections':['app']})
  with patch('chatify.appbuilder.save_plan',side_effect=appbuilder.SaveRollbackError('Save failed and rollback could not restore: prompts.json')):
   with self.assertRaises(urllib.error.HTTPError) as error:self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':True})
  self.assertEqual(error.exception.code,400)
  body=json.loads(error.exception.read());self.assertTrue(body['saved_state_uncertain']);self.assertIn('prompts.json',body['error'])

 def test_section_draft_http_retain_reopen_review_keeps_scope(self):
  from pathlib import Path
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump({k:self.cfg[k] for k in schema.DEFAULTS}));self.cfg['_path']=str(path)
  original=path.read_bytes()
  retained=self.call(self.clients[0],'/api/settings/build/draft',{'yaml':'app: {title: Retained garden}','sections':['app'],'title':'Retained garden'})
  restored=self.call(self.clients[0],'/api/settings/build/draft?id='+retained['id'])
  self.assertEqual(set(yaml.safe_load(restored['yaml'])),{'app'})
  plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':restored['yaml'],'sections':restored['sections']})
  self.assertEqual(plan['selected'],['app']);self.assertEqual(plan['config']['app']['title'],'Retained garden')
  self.assertEqual(path.read_bytes(),original)

 def test_prompt_editor_get_shows_saved_builder_prompts_without_restart(self):
  from pathlib import Path
  from chatify import prompts
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump({k:self.cfg[k] for k in schema.DEFAULTS}));self.cfg['_path']=str(path)
  self.engine.prompts=prompts.PromptStore('');self.engine.prompts.view(self.cfg['prompt']['system'])
  generated={'pipeline_prompts':{'text':{k:'Trip planning fixture '+k for k in prompts.STAGES},'on':{k:False for k in prompts.STAGES}}}
  plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':yaml.safe_dump(generated),'sections':['pipeline_prompts']})
  self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':True})
  response=self.call(self.clients[0],'/api/prompts')
  self.assertEqual(len(response['stages']),len(__import__('chatify.prompts',fromlist=['STAGES']).STAGES))
  for stage in response['stages']:self.assertEqual(stage['text'],'Trip planning fixture '+stage['key'])

 def test_edit_one_prompt_after_builder_apply_keeps_other_saved_stages(self):
  from pathlib import Path
  from chatify import prompts
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump({k:self.cfg[k] for k in schema.DEFAULTS}));self.cfg['_path']=str(path)
  self.engine.prompts=prompts.PromptStore('');self.engine.prompts.view(self.cfg['prompt']['system'])
  generated={'pipeline_prompts':{'text':{k:'Trip planning fixture '+k for k in prompts.STAGES},'on':{k:False for k in prompts.STAGES}}}
  plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':yaml.safe_dump(generated),'sections':['pipeline_prompts']})
  self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':True})
  first=next(iter(prompts.STAGES));response=self.call(self.clients[0],'/api/prompts/save',{'key':first,'text':'My newer prompt','on':False})
  for stage in response['stages']:self.assertEqual(stage['text'],'My newer prompt' if stage['key']==first else 'Trip planning fixture '+stage['key'])

 def test_reset_one_prompt_after_builder_apply_keeps_other_saved_stages(self):
  from pathlib import Path
  from chatify import prompts
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump({k:self.cfg[k] for k in schema.DEFAULTS}));self.cfg['_path']=str(path)
  self.engine.prompts=prompts.PromptStore('');self.engine.prompts.view(self.cfg['prompt']['system'])
  generated={'pipeline_prompts':{'text':{k:'Trip planning fixture '+k for k in prompts.STAGES},'on':{k:False for k in prompts.STAGES}}}
  plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':yaml.safe_dump(generated),'sections':['pipeline_prompts']})
  self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':True})
  first=next(iter(prompts.STAGES));response=self.call(self.clients[0],'/api/prompts/reset',{'key':first})
  for stage in response['stages']:self.assertEqual(stage['text'],'' if stage['key']==first else 'Trip planning fixture '+stage['key'])

 def test_download_readme_truthful_when_helper_code_is_bundled(self):
  import io,zipfile,urllib.request
  from chatify import generators
  raw={'helper_drafts':{'search':{'brief':'Offline fixture','code':generators.code_template('search','')}}}
  request=urllib.request.Request('http://127.0.0.1:'+str(self.server.server_port)+'/api/settings/build/download',data=json.dumps({'yaml':yaml.safe_dump(raw)}).encode(),headers={'Content-Type':'application/json'})
  with zipfile.ZipFile(io.BytesIO(self.clients[0].open(request).read())) as z:
   self.assertIn('data/code-drafts.json',z.namelist());readme=z.read('README.md').decode()
   self.assertNotIn('No code included',readme);self.assertIn('inert code for review',readme);self.assertIn('No code is installed or run',readme)

class IdeaRefinementHTTP(BuilderHTTP):
 def test_refine_owner_gate_no_model(self):
  with patch('chatify.providers.make') as make:
   with self.assertRaises(urllib.error.HTTPError):self.call(self.clients[1],'/api/settings/build/refine',{'consent':True,'brief':'garden app','selection':{'provider':'openai','model':'chosen'}})
  make.assert_not_called()
 def test_refine_explicit_selection_budget_one_call_no_change(self):
  from unittest.mock import Mock
  before=json.dumps(self.cfg,sort_keys=True);provider=Mock();provider.complete.return_value=json.dumps({'brief':'Garden app with user-reviewed planting notes.'});selected=[]
  def make(cfg):selected.append(cfg['provider']);return provider
  with patch('chatify.providers.make',side_effect=make),patch('chatify.providers.list_models') as listing:
   result=self.call(self.clients[0],'/api/settings/build/refine',{'consent':True,'brief':'garden app','selection':{'provider':'openai','model':'my-model','base_url':'https://custom.invalid/v1'}})
  self.assertEqual(selected[0]['model'],'my-model');self.assertEqual(selected[0]['base_url'],'https://custom.invalid/v1');listing.assert_not_called();self.assertEqual(provider.complete.call_count,1);self.assertFalse(result['changed']);self.assertEqual(before,json.dumps(self.cfg,sort_keys=True))
 def test_refine_no_consent_no_completion(self):
  from unittest.mock import Mock
  provider=Mock()
  with patch('chatify.providers.make',return_value=provider):
   with self.assertRaises(urllib.error.HTTPError):self.call(self.clients[0],'/api/settings/build/refine',{'brief':'garden app','selection':{'provider':'openai','model':'chosen'}})
  provider.complete.assert_not_called()
