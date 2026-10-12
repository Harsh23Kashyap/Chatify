import copy,json,tempfile,unittest,yaml
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
