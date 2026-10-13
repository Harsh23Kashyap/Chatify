import copy,json,tempfile,unittest,yaml,os
from unittest import mock
from pathlib import Path
from customchat import appbuilder,schema,editstate
class Fixture:
 def __init__(self,result):self.result=result;self.calls=[]
 def complete(self,messages):self.calls.append(messages);return json.dumps(self.result)
class BuilderTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'app.yaml';self.cfg=schema.validate({});self.path.write_text(yaml.safe_dump(self.cfg));self.cfg['_path']=str(self.path);self.cfg['provider'].update(type='openai',model='user-model')
 def data(self,**kwargs):return {'consent':True,'messages':[{'role':'user','content':'A gardening app for new gardeners'}],'sections':['app'],**kwargs}
 def test_followup(self):
  p=Fixture({'message':'Which sources do you have?','config':None});r=appbuilder.talk(p,self.cfg,self.data());self.assertIsNone(r['yaml']);self.assertFalse(r['changed']);self.assertEqual(len(p.calls),1)
 def test_partial_defaults_complete(self):
  p=Fixture({'message':'Review your draft','config':{'app':{'title':'Garden Chat'}}});r=appbuilder.talk(p,self.cfg,self.data());raw=yaml.safe_load(r['yaml']);self.assertEqual(set(raw),{'app'});self.assertEqual(raw['app']['title'],'Garden Chat');self.assertIn('examples',raw['app'])
 def test_full_draft(self):
  p=Fixture({'message':'Review','config':{'app':{'title':'Garden'}}});r=appbuilder.talk(p,self.cfg,self.data(sections=list(schema.DEFAULTS)));self.assertEqual(set(yaml.safe_load(r['yaml'])),set(schema.DEFAULTS))
 def test_no_private_config_in_prompt(self):
  self.cfg['sources']=[{'type':'http_json','url':'https://private.invalid','label':'PRIVATE_SENTINEL'}];self.cfg['provider']['api_key_env']='PRIVATE_ENV';p=Fixture({'message':'Sources?','config':None});appbuilder.talk(p,self.cfg,self.data());sent=json.dumps(p.calls);self.assertNotIn('PRIVATE_SENTINEL',sent);self.assertNotIn('private.invalid',sent);self.assertNotIn('PRIVATE_ENV',sent)
 def test_consent_gate(self):
  p=Fixture({});self.assertRaises(ValueError,appbuilder.talk,p,self.cfg,self.data(consent=False));self.assertEqual(p.calls,[])
 def test_demo_gate(self):
  self.cfg['provider']['type']='mock';self.assertRaises(ValueError,appbuilder.talk,Fixture({}),self.cfg,self.data())
 def test_secret_brief(self):
  self.assertRaises(ValueError,appbuilder.talk,Fixture({}),self.cfg,self.data(messages=[{'role':'user','content':'password=oops'}]))
 def test_out_of_scope(self):
  self.assertRaises(ValueError,appbuilder.talk,Fixture({'message':'Draft','config':{'server':{'port':8090}}}),self.cfg,self.data())
 def test_unknown_nested(self):self.assertRaises(ValueError,appbuilder.validate,'app:\n  typo: hello\n')
 def test_bad_yaml(self):self.assertRaises(ValueError,appbuilder.validate,'[broken')
 def test_not_mapping(self):self.assertRaises(ValueError,appbuilder.validate,'[]')
 def test_python_rejected(self):self.assertRaises(ValueError,appbuilder.validate,'sources:\n- type: python\n  entry: bad:run\n')
 def test_inline_secret(self):self.assertRaises(ValueError,appbuilder.validate,'provider:\n  api_key: SECRET\n')
 def test_invalid_provider(self):self.assertRaises(ValueError,appbuilder.validate,'provider:\n  type: nope\n')
 def test_invalid_bool(self):self.assertRaises(ValueError,appbuilder.validate,'memory:\n  enabled: 1\n')
 def test_review_no_write(self):
  old=self.path.read_bytes();r=appbuilder.review(self.cfg,'app:\n  title: New app\n',['app']);self.assertEqual(self.path.read_bytes(),old);self.assertEqual(r['config']['app']['title'],'New app');self.assertEqual(r['config']['server'],schema.DEFAULTS['server']);self.assertEqual(r['sections'],['app'])
 def test_review_scope(self):self.assertRaises(ValueError,appbuilder.review,self.cfg,'server:\n port: 8090\n',['app'])
 def test_review_missing(self):self.assertRaises(ValueError,appbuilder.review,self.cfg,'{}',['app'])
 def test_revision_save_stale(self):
  r=appbuilder.review(self.cfg,'app:\n title: New app\n',['app']);self.path.write_text('app:\n title: Intervening edit\n');self.assertRaises(ValueError,editstate.save_config,self.cfg,r['config'],r['revision'])
 def test_revision_save(self):
  r=appbuilder.review(self.cfg,'app:\n title: New app\n',['app']);editstate.save_config(self.cfg,r['config'],r['revision']);self.assertEqual(schema.load(str(self.path))['app']['title'],'New app');self.assertEqual(self.cfg['app']['title'],'My Chat')

 def test_direct_config_response(self):
  p=Fixture({'app':{'title':'Direct draft'}});r=appbuilder.talk(p,self.cfg,self.data());self.assertEqual(yaml.safe_load(r['yaml'])['app']['title'],'Direct draft')
 def test_anchors_rejected(self):self.assertRaises(ValueError,appbuilder.validate,'app: &a {title: X}\nprovider: *a\n')
 def test_sources_mapping_rejected(self):self.assertRaises(ValueError,appbuilder.validate,'sources: {type: local_files, path: docs}')
 def test_source_path_must_be_supplied(self):
  self.assertRaises(ValueError,appbuilder.talk,Fixture({'message':'Draft','config':{'sources':[{'type':'local_files','path':'invented'}]}}),self.cfg,self.data(sections=['sources']))

 def test_tweak_receives_only_draft_not_saved_private_config(self):
  p=Fixture({'message':'New draft','config':{'app':{'title':'Tweaked'}}});appbuilder.talk(p,self.cfg,self.data(draft='app:\n title: Earlier draft\n'));self.assertIn('Earlier draft',json.dumps(p.calls));self.assertNotIn('PRIVATE_ENV',json.dumps(p.calls))
 def test_bad_draft_before_call(self):
  p=Fixture({});self.assertRaises(ValueError,appbuilder.talk,p,self.cfg,self.data(draft='server: {port: 4444}'));self.assertFalse(p.calls)

 def test_field_changes_against_saved_not_model(self):
  result=appbuilder.review(self.cfg,'app: {title: Human title}',['app'])
  title=next(c for c in result['changes'] if c['field']=='app.title')
  self.assertEqual(title['before'],'My Chat');self.assertEqual(title['after'],'Human title')
  self.assertFalse(any(c['field'].startswith('provider') for c in result['changes']))
 def test_no_changes_empty_diff(self):
  result=appbuilder.review(self.cfg,yaml.safe_dump({'app':self.cfg['app']}),['app'])
  self.assertEqual(result['sections'],[]);self.assertEqual(result['changes'],[])

 def complete_config(self):
  from customchat import theme,prompts,generators
  raw=copy.deepcopy(schema.DEFAULTS)
  raw.update(appearance=theme.DEFAULT_CLEAN(),pipeline_prompts={'text':{k:v['default'] or raw['prompt']['system'] for k,v in prompts.STAGES.items()},'on':{k:v['on'] for k,v in prompts.STAGES.items()}},helper_drafts={k:{'brief':'A reviewed helper draft','code':generators.code_template(k,'')} for k in ('search','clean_query')},api_suggestions=[{'name':'PubMed','reason':'Biomedical literature','connector':'pubmed','setup':'Enable after review','caveat':'Verify coverage; no price claim'}])
  return raw
 def test_complete_extensions_and_all_prompts(self):
  raw=self.complete_config();result=appbuilder.validate(yaml.safe_dump(raw));self.assertEqual(len(result['pipeline_prompts']['text']),9)
  self.assertEqual(set(result['appearance']),set(raw['appearance']));self.assertTrue(result['helper_drafts']['search']['code'])
  self.assertEqual(schema.validate(result)['appearance']['font'],'dm-sans')
 def test_blank_pipeline_prompt_rejected(self):
  raw=self.complete_config();raw['pipeline_prompts']['text']['followups']='';self.assertRaises(ValueError,appbuilder.validate,yaml.safe_dump(raw))
 def test_negative_and_numeric_bounds(self):
  cases=[('budget','daily_questions',-26),('budget','daily_model_calls',1.2),('budget','spend_cap_usd',-1),('provider','temperature',-1),('provider','timeout',0),('retrieval','top_k',0),('retrieval','min_score',-1),('retrieval','cache_ttl',-1),('server','port',0),('memory','recent_turns',-1)]
  for area,key,value in cases:
   raw=copy.deepcopy(schema.DEFAULTS);raw[area][key]=value
   with self.subTest(area=area,key=key):self.assertRaises(ValueError,appbuilder.validate,yaml.safe_dump(raw))
 def test_complete_save_no_execute_extensions_restart(self):
  from customchat import prompts,theme
  self.cfg['_dir']=self.tmp.name;raw=self.complete_config();raw['app']['title']='Complete Garden';raw['storage']['path']='data/customchat.db'
  plan=appbuilder.review(self.cfg,yaml.safe_dump(raw),appbuilder.SECTIONS);appbuilder.save_plan(self.cfg,plan)
  saved=schema.load(str(self.path));self.assertEqual(saved['app']['title'],'Complete Garden')
  self.assertEqual(len(saved['pipeline_prompts']['text']),9);self.assertTrue((Path(self.tmp.name)/'data'/'code-drafts.json').exists())
  self.assertEqual(prompts.PromptStore('',saved['pipeline_prompts']).text('followups'),raw['pipeline_prompts']['text']['followups'])
 def test_complete_save_rolls_back_each_setup_replace_failure(self):
  self.cfg['_dir']=self.tmp.name
  folder=Path(self.tmp.name)/'data';folder.mkdir()
  names=['theme.json','prompts.json','code-drafts.json']
  original=self.path.read_bytes();real_replace=os.replace
  for existing in (False,True):
   for failing in names:
    with self.subTest(existing=existing,failing=failing):
     for name in names:
      path=folder/name
      if path.exists():path.unlink()
      if existing:path.write_text('{}')
     old={name:(folder/name).read_bytes() if (folder/name).exists() else None for name in names}
     raw=self.complete_config();raw['app']['title']='Must not survive failed save';raw['storage']['path']='data/customchat.db'
     plan=appbuilder.review(self.cfg,yaml.safe_dump(raw),appbuilder.SECTIONS)
     def replace(src,dst):
      if Path(dst).name==failing:raise OSError('Injected setup replacement failure')
      return real_replace(src,dst)
     with mock.patch('customchat.appbuilder.os.replace',side_effect=replace):
      with self.assertRaisesRegex(OSError,'Injected setup'):appbuilder.save_plan(self.cfg,plan)
     self.assertEqual(self.path.read_bytes(),original)
     for name in names:
      path=folder/name
      self.assertEqual(path.read_bytes() if path.exists() else None,old[name])
     self.assertFalse(list(folder.glob('.setup-*')))
     self.assertFalse(list(Path(self.tmp.name).glob('.app-edit-*')))
 def test_setup_rollback_failure_still_restores_app_and_reports_uncertainty(self):
  self.cfg['_dir']=self.tmp.name
  folder=Path(self.tmp.name)/'data';folder.mkdir()
  for name in ['theme.json','prompts.json','code-drafts.json']:(folder/name).write_text('{}')
  original=self.path.read_bytes();real_replace=os.replace;real_write=Path.write_bytes
  raw=self.complete_config();raw['app']['title']='Must not survive failed save';raw['storage']['path']='data/customchat.db'
  plan=appbuilder.review(self.cfg,yaml.safe_dump(raw),appbuilder.SECTIONS)
  def replace(src,dst):
   if Path(dst).name=='code-drafts.json':raise OSError('Injected setup replacement failure')
   return real_replace(src,dst)
  def write(path,data):
   if path.name=='prompts.json':raise OSError('Injected rollback write failure')
   return real_write(path,data)
  with mock.patch('customchat.appbuilder.os.replace',side_effect=replace),mock.patch.object(Path,'write_bytes',write):
   with self.assertRaises(Exception) as error:appbuilder.save_plan(self.cfg,plan)
  self.assertEqual(self.path.read_bytes(),original,'failed setup rollback must not prevent app restoration')
  self.assertEqual((folder/'theme.json').read_text(),'{}','all independent rollback steps should be attempted')
  self.assertIn('rollback',str(error.exception).lower())
  self.assertIn('prompts.json',str(error.exception))
 def test_deploy_requires_consent_no_execution(self):
  p=Fixture({'plan':'1. Review your app. 2. Set keys in the environment.','prompt':'Create a reviewed deployment plan.'})
  self.assertRaises(ValueError,appbuilder.deployment,p,{'brief':'Local app','consent':False});self.assertEqual(p.calls,[])
  result=appbuilder.deployment(p,{'brief':'Local app','consent':True});self.assertIn('plan',result);self.assertEqual(len(p.calls),1)
