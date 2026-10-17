"""Saved state format and malformed input checks against actual HTTP handlers."""
import unittest,tempfile,threading,json,urllib.request,urllib.error,os
from http.server import ThreadingHTTPServer
from chatify import schema
from chatify.store import Store
from chatify.pipeline import Engine
from chatify.server import make_handler
class StateMatrix(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();cfg=schema.validate({'storage':{'path':self.tmp.name+'/s.db'}});cfg['_dir']=self.tmp.name
  self.store=Store(cfg['storage']['path']);self.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(cfg,Engine(cfg,self.store)));threading.Thread(target=self.server.serve_forever,daemon=True).start();self.root='http://127.0.0.1:'+str(self.server.server_port)
 def tearDown(self):self.server.shutdown();self.server.server_close();self.tmp.cleanup()
 def api(self,path,body=None):
  req=urllib.request.Request(self.root+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req) as r:return json.load(r)
 def test_legacy_model_only_retains_current_appearance(self):
  t=self.api('/api/theme')['theme'];t['font']='mono';self.api('/api/theme',{'theme':t});self.store.save_state('local','legacy',{'model':'offline-new'})
  r=self.api('/api/states/load',{'name':'legacy'});self.assertEqual(r['settings']['model'],'offline-new');self.assertEqual(r['theme']['font'],'mono')
 def test_nested_settings_only(self):
  self.store.save_state('local','partial',{'settings':{'temperature':0.4}});r=self.api('/api/states/load',{'name':'partial'});self.assertEqual(r['settings']['temperature'],0.4)
 def test_unknown_settings_retained_without_execution(self):
  self.store.save_state('local','extra',{'settings':{'custom_optional':'anything','model':'offline-new'}});self.assertEqual(self.api('/api/states/load',{'name':'extra'})['settings']['model'],'offline-new')
 def test_partial_theme_falls_back(self):
  self.store.save_state('local','partial-theme',{'settings':{},'theme':{'font':'mono','light':{'brand':'#123456'}}});r=self.api('/api/states/load',{'name':'partial-theme'});self.assertEqual(r['theme']['font'],'mono');self.assertEqual(r['theme']['light']['brand'],'#123456');self.assertTrue(r['theme']['light']['bg'])
 def test_malformed_states_do_not_change_settings_or_theme(self):
  before=self.api('/api/settings')['settings'];theme=self.api('/api/theme')['theme']
  for i,payload in enumerate([None,[],42,'invalid',{'settings':None},{'settings':[]},{'settings':{'model':'wrong'},'theme':'invalid'},{'settings':{'model':'wrong'},'theme':{'font_size':-1}},{'settings':{'model':'wrong'},'theme':{'font_size':100.5}}]):
   with self.subTest(payload=payload):
    self.store.save_state('local','bad'+str(i),payload)
    with self.assertRaises(urllib.error.HTTPError) as cm:self.api('/api/states/load',{'name':'bad'+str(i)})
    self.assertEqual(cm.exception.code,400);self.assertEqual(self.api('/api/settings')['settings'],before);self.assertEqual(self.api('/api/theme')['theme'],theme)
 def test_missing_name_returns_400_without_change(self):
  with self.assertRaises(urllib.error.HTTPError) as cm:self.api('/api/states/load',{'name':'missing'})
  self.assertEqual(cm.exception.code,400)
 def test_named_state_image_roundtrip(self):
  image='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jF8sAAAAASUVORK5CYII='
  t=self.api('/api/theme')['theme'];t.update(bg_style='image',bg_image='https://example.org/background.jpg',logo=image);self.api('/api/theme',{'theme':t});self.api('/api/states/save',{'name':'image'});self.api('/api/theme',{'reset':True});r=self.api('/api/states/load',{'name':'image'});self.assertEqual(r['theme']['bg_image'],'https://example.org/background.jpg');self.assertEqual(r['theme']['logo'],image)
 def test_malformed_chat_import_batch_has_no_partial_writes(self):
  before=self.api('/api/chats')
  for malformed in [42,'invalid',{},[{'title':'good','turns':[{'question':'q','answer':'a'}]},{'turns':42}],[{'turns':[{'question':'q','answer':'a','evidence':'bad'}]}],[{'turns':[{'question':'q','answer':'a','evidence':[42]}]}]]:
   with self.subTest(malformed=malformed):
    with self.assertRaises(urllib.error.HTTPError) as cm:self.api('/api/import',{'chats':malformed})
    self.assertEqual(cm.exception.code,400);self.assertEqual(self.api('/api/chats'),before)

 def test_bad_import_evidence_fields_rejected_before_writes(self):
  for evidence in [[{}],[{'title':'x','url':42}],[{'title':'x','authors':'not-a-list'}]]:
   with self.subTest(evidence=evidence):
    with self.assertRaises(urllib.error.HTTPError) as cm:self.api('/api/import',{'chats':[{'turns':[{'question':'q','answer':'a','evidence':evidence}]}]})
    self.assertEqual(cm.exception.code,400);self.assertEqual(self.api('/api/chats'),[])
 def test_deleted_chat_hidden_from_topic_until_restore(self):
  c=self.store.new_chat('local','chat');t=self.store.new_topic('local','topic');self.store.add_turn(c,t,'q','q','a',[],[],'standard')
  self.assertEqual(len(self.store.topic_turns('local',t)),1)
  self.store.delete_chat('local',c);self.assertEqual(self.store.topic_turns('local',t),[]);self.assertEqual(self.store.topics('local')[0]['turns'],0)
  self.store.restore_chat('local',c);self.assertEqual(len(self.store.topic_turns('local',t)),1);self.assertEqual(self.store.topics('local')[0]['turns'],1)
 def test_deleted_turn_not_counted_in_topic(self):
  c=self.store.new_chat('local','chat');t=self.store.new_topic('local','topic');turn=self.store.add_turn(c,t,'q','q','a',[],[],'standard')
  self.store.delete_turn('local',turn);self.assertEqual(self.store.topics('local')[0]['turns'],0)
