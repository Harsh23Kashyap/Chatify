import json,urllib.error,unittest,yaml
from unittest.mock import patch
import test_workspace_api
from customchat import providers,schema,appbuilder
class BuilderHTTP(test_workspace_api.WorkspaceAPITests):
 def setUp(self):
  import tempfile
  from customchat.store import Store
  self.state_tmp=tempfile.TemporaryDirectory()
  with patch('test_workspace_api.Store',side_effect=lambda _:Store(self.state_tmp.name+'/customchat.db')):super().setUp()
 def tearDown(self):
  super().tearDown();self.state_tmp.cleanup()

 def test_owner_gate(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.call(self.clients[1],'/api/settings/build/talk',{'consent':True})
  self.assertIn(e.exception.code,(403,404))
 def test_talk_selected_draft_and_no_state_changes(self):
  before=json.dumps(self.cfg,sort_keys=True);calls=[]
  def transport(url,body,headers,timeout):
   calls.append(body);return {'choices':[{'message':{'content':json.dumps({'message':'Review app','config':{'app':{'title':'New garden'}}})}}]}
  with patch('customchat.providers._key',return_value='fixture-only'),patch('customchat.providers._post',side_effect=transport):
   result=self.call(self.clients[0],'/api/settings/build/talk',{'consent':True,'selection':{'provider':'openai','model':'my-specific-model'},'sections':['app'],'messages':[{'role':'user','content':'A garden app'}]})
  self.assertEqual(calls[0]['model'],'my-specific-model');self.assertEqual(yaml.safe_load(result['yaml'])['app']['title'],'New garden');self.assertEqual(before,json.dumps(self.cfg,sort_keys=True))
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

 def test_download_zip_can_review_and_load(self):
  import io,zipfile,urllib.request,base64
  from customchat.nerdload import NerdLoader
  config=schema.validate({'app':{'title':'Generated garden'}})
  request=urllib.request.Request('http://127.0.0.1:'+str(self.server.server_port)+'/api/settings/build/download',data=json.dumps({'yaml':yaml.safe_dump(config)}).encode(),headers={'Content-Type':'application/json'})
  data=self.clients[0].open(request).read()
  with zipfile.ZipFile(io.BytesIO(data)) as z:self.assertEqual(set(z.namelist()),{'app.yaml','README.md'})
  loader=NerdLoader(self.tmp.name)
  try:
   plan=loader.review('customchat-draft.zip',base64.b64encode(data).decode());self.assertEqual(plan['title'],'Generated garden');self.assertEqual(plan['code'],[])
   loaded=loader.load(plan['token'],False)
   self.assertIn('http://127.0.0.1:',loaded['url'])
   self.assertEqual(json.loads(urllib.request.urlopen(loaded['url']+'/api/health').read())['ok'],True)
  finally:loader.close()
 def test_consent_and_bad_selection_no_transport(self):
  with patch('customchat.providers._post') as transport:
   for body in ({'selection':{'provider':'openai','model':'fixture'},'consent':False,'messages':[{'role':'user','content':'app'}]}, {'selection':{'provider':'not-a-provider','model':'fixture'},'consent':True}):
    with self.assertRaises(urllib.error.HTTPError):self.call(self.clients[0],'/api/settings/build/talk',body)
   self.assertFalse(transport.called)

 def test_parse_no_model_no_save_and_scope(self):
  before=json.dumps(self.cfg,sort_keys=True)
  with patch('customchat.providers._post') as transport:
   result=self.call(self.clients[0],'/api/settings/build/parse',{'yaml':'app: {title: Editable title}'})
  self.assertEqual(set(result['config']),{'app'});self.assertEqual(result['config']['app']['title'],'Editable title')
  self.assertEqual(json.dumps(self.cfg,sort_keys=True),before);self.assertFalse(transport.called)
 def test_parse_owner_gate_and_validation(self):
  for client,source in [(self.clients[1],'app: {title: X}'),(self.clients[0],'app: {typo: X}'),(self.clients[0],'[invalid')]:
   with self.assertRaises(urllib.error.HTTPError):self.call(client,'/api/settings/build/parse',{'yaml':source})

 def test_incomplete_rollback_returns_explicit_uncertain_saved_state(self):
  from pathlib import Path
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump({k:self.cfg[k] for k in schema.DEFAULTS}));self.cfg['_path']=str(path)
  plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':'app: {title: Garden app}','sections':['app']})
  with patch('customchat.appbuilder.save_plan',side_effect=appbuilder.SaveRollbackError('Save failed and rollback could not restore: prompts.json')):
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
  from customchat import prompts
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump({k:self.cfg[k] for k in schema.DEFAULTS}));self.cfg['_path']=str(path)
  self.engine.prompts=prompts.PromptStore('');self.engine.prompts.view(self.cfg['prompt']['system'])
  generated={'pipeline_prompts':{'text':{k:'Trip planning fixture '+k for k in prompts.STAGES},'on':{k:False for k in prompts.STAGES}}}
  plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':yaml.safe_dump(generated),'sections':['pipeline_prompts']})
  self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':True})
  response=self.call(self.clients[0],'/api/prompts')
  self.assertEqual(len(response['stages']),9)
  for stage in response['stages']:self.assertEqual(stage['text'],'Trip planning fixture '+stage['key'])

 def test_edit_one_prompt_after_builder_apply_keeps_other_saved_stages(self):
  from pathlib import Path
  from customchat import prompts
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump({k:self.cfg[k] for k in schema.DEFAULTS}));self.cfg['_path']=str(path)
  self.engine.prompts=prompts.PromptStore('');self.engine.prompts.view(self.cfg['prompt']['system'])
  generated={'pipeline_prompts':{'text':{k:'Trip planning fixture '+k for k in prompts.STAGES},'on':{k:False for k in prompts.STAGES}}}
  plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':yaml.safe_dump(generated),'sections':['pipeline_prompts']})
  self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':True})
  first=next(iter(prompts.STAGES));response=self.call(self.clients[0],'/api/prompts/save',{'key':first,'text':'My newer prompt','on':False})
  for stage in response['stages']:self.assertEqual(stage['text'],'My newer prompt' if stage['key']==first else 'Trip planning fixture '+stage['key'])

 def test_reset_one_prompt_after_builder_apply_keeps_other_saved_stages(self):
  from pathlib import Path
  from customchat import prompts
  path=Path(self.cfg['_dir'])/'app.yaml';path.write_text(yaml.safe_dump({k:self.cfg[k] for k in schema.DEFAULTS}));self.cfg['_path']=str(path)
  self.engine.prompts=prompts.PromptStore('');self.engine.prompts.view(self.cfg['prompt']['system'])
  generated={'pipeline_prompts':{'text':{k:'Trip planning fixture '+k for k in prompts.STAGES},'on':{k:False for k in prompts.STAGES}}}
  plan=self.call(self.clients[0],'/api/settings/build/review',{'yaml':yaml.safe_dump(generated),'sections':['pipeline_prompts']})
  self.call(self.clients[0],'/api/settings/build/save',{'ticket':plan['ticket'],'confirmed':True})
  first=next(iter(prompts.STAGES));response=self.call(self.clients[0],'/api/prompts/reset',{'key':first})
  for stage in response['stages']:self.assertEqual(stage['text'],'' if stage['key']==first else 'Trip planning fixture '+stage['key'])

 def test_download_readme_truthful_when_helper_code_is_bundled(self):
  import io,zipfile,urllib.request
  from customchat import generators
  raw={'helper_drafts':{'search':{'brief':'Offline fixture','code':generators.code_template('search','')}}}
  request=urllib.request.Request('http://127.0.0.1:'+str(self.server.server_port)+'/api/settings/build/download',data=json.dumps({'yaml':yaml.safe_dump(raw)}).encode(),headers={'Content-Type':'application/json'})
  with zipfile.ZipFile(io.BytesIO(self.clients[0].open(request).read())) as z:
   self.assertIn('data/code-drafts.json',z.namelist());readme=z.read('README.md').decode()
   self.assertNotIn('No code included',readme);self.assertIn('inert code for review',readme);self.assertIn('No code is installed or run',readme)
