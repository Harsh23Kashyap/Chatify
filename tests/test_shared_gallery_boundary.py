import json, tempfile, threading, unittest, urllib.request, urllib.error, time, os
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from chatify import schema, shared_access
from chatify.store import Store
from chatify.pipeline import Engine
from chatify.server import make_handler

class SharedBoundary(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.cfg=schema.validate({'sources':[],'server':{'public':True},'storage':{'path':self.tmp.name+'/store.db'}});self.cfg['_dir']=self.tmp.name;self.cfg['_shared_gallery_builtin']=True
  self.store=Store(self.cfg['storage']['path']);self.engine=Engine(self.cfg,self.store);self.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.cfg,self.engine));threading.Thread(target=self.server.serve_forever,daemon=True).start();self.root='http://127.0.0.1:'+str(self.server.server_port)
 def tearDown(self):self.server.shutdown();self.server.server_close();self.tmp.cleanup()
 def call(self,path,body=None,cookie='a'*32,method=None):
  h={'Content-Type':'application/json','X-Forwarded-For':'127.0.0.1'}
  if cookie:h['Cookie']='cc_visitor='+cookie
  q=urllib.request.Request(self.root+path,data=None if body is None else json.dumps(body).encode(),headers=h,method=method)
  try:
   with urllib.request.urlopen(q) as r:return r.status,r.read(),r.headers
  except urllib.error.HTTPError as r:return r.code,r.read(),r.headers
 def test_all_management_families_denied_reads_and_writes(self):
  families=['configuration-state','settings','settings/build','settings/versions','settings/publish/package','settings/guide','prompts','prompts/save','prompts/reset','prompts/test','prompts/generate','codegen','codegen/draft','codegen/test','websearch/status','websearch/key','catalog/key','source-credentials','provider/status','provider/key','provider/models','provider/test','budget','docs-freshness','app-export','app-export-check','hardware','states','states/save','states/load','states/delete','ollama/setup','ollama/pull','nerds','nerds/review','nerds/load','nerds/recover','workspace/status','workspace/preflight/run','future-admin-route']
  before=self.engine.prompts._load().copy()
  with patch.object(self.engine.provider,'complete',side_effect=AssertionError('no provider invocation')):
   for family in families:
    for method in ['GET','POST','PUT','PATCH','DELETE','HEAD']:
     with self.subTest(family=family,method=method):self.assertEqual(self.call('/api/'+family,{} if method!='GET' else None,method=method)[0],403 if method in ('GET','POST') else 501)
  self.assertEqual(self.engine.prompts._load(),before)
 def test_shared_theme_and_guide_writes_blocked(self):
  for path in ['/api/theme','/api/guide-seen']:
   self.assertEqual(self.call(path,{'theme':{'mode':'dark'},'key':'cc_tour'})[0],403)
  status,body,_=self.call('/api/theme');self.assertEqual(status,200);self.assertFalse(json.loads(body)['can_edit'])
  self.assertEqual(json.loads(self.call('/api/guide-seen')[1]),{})
 def test_missing_and_bad_cookie_fail_before_shared_local_state(self):
  for cookie in [None,'invalid','../escape']:
   for path in ['/api/chats','/api/profile','/api/export-all']:
    self.assertEqual(self.call(path,cookie=cookie)[0],403)
  self.assertEqual(self.call('/api/health',cookie=None)[0],200)
 def test_public_chat_profile_history_remain_owner_scoped(self):
  chat=json.loads(self.call('/api/chats',{'title':'Visitor A privatechat'})[1])['id']
  self.call('/api/profile',{'text':'A profile'})
  a=json.loads(self.call('/api/chats')[1]);b=json.loads(self.call('/api/chats',cookie='b'*32)[1]);self.assertEqual(a[0]['id'],chat);self.assertEqual(b,[])
  self.assertEqual(json.loads(self.call('/api/profile',cookie='b'*32)[1])['text'],'')
  with patch.object(self.engine,'ask',return_value={'answer':'Fixture answer','evidence':[]}) as ask:
   self.assertEqual(self.call('/api/ask',{'chat':chat,'question':'Fixture question'})[0],200);self.assertEqual(ask.call_args.args[0],'visitor:'+'a'*32)
 def test_settings_notice_has_no_editor_or_model_requests(self):
  status,body,headers=self.call('/settings.html',cookie=None);self.assertEqual(status,200);text=body.decode();self.assertIn('This shared app is read-only',text);self.assertNotIn('<script',text);self.assertNotIn('<input',text);self.assertIn('cc_visitor=',headers['Set-Cookie'])
  for path in ['/foo/../settings.js','/settings.js','/appbuilder.js','/pipeline.js','/codeeditor.js','/shared-settings.html']:self.assertEqual(self.call(path)[0],403)
 def test_build_page_and_aliases_show_readonly_notice(self):
  for path in ['/build.html','/foo/../settings.html']:
   self.assertIn(b'This shared app is read-only',self.call(path)[1])
 def test_config_and_deephealth_do_not_resolve_or_expose_key_details(self):
  with patch('chatify.providers._key',side_effect=AssertionError('shared config must not inspect keys')):
   status,body,_=self.call('/api/config');self.assertEqual(status,200)
  view=json.loads(body);self.assertEqual(set(view['provider']),{'type','model'})
  health=json.loads(self.call('/api/health?deep=1')[1]);self.assertEqual(health,{'ok':True})
 def test_visitor_uploads_and_foreign_chat_operations_remain_isolated(self):
  chat=json.loads(self.call('/api/chats',{'title':'A'})[1])['id']
  self.call('/api/uploads',{'name':'A.txt','text':'Only A'})
  self.assertEqual(json.loads(self.call('/api/uploads',cookie='b'*32)[1]),[])
  self.assertEqual(len(json.loads(self.call('/api/uploads')[1])),1)
  self.assertNotEqual(self.call('/api/delete',{'chat':chat},cookie='b'*32)[0],200)
  self.assertEqual(len(json.loads(self.call('/api/chats')[1])),1)
 def test_visitor_note_action_stays_private(self):
  ticket=json.loads(self.call('/api/actions/prepare',{'tool':'save_note','args':{'title':'A note','text':'private A'}})[1])['ticket']
  self.assertNotEqual(self.call('/api/actions/execute',{'ticket':ticket},cookie='b'*32)[0],200)
  self.assertTrue(json.loads(self.call('/api/actions/execute',{'ticket':ticket})[1])['saved'])
 def test_shared_flag_not_public_or_portable_user_setting(self):
  view=json.loads(self.call('/api/config')[1]);self.assertNotIn('_shared_gallery_builtin',view);self.assertEqual(view['auth'],'none');self.assertNotIn('key_present',view['provider'])
 def test_nonshared_standalone_keeps_local_edit_permission(self):
  self.cfg.pop('_shared_gallery_builtin');self.assertEqual(self.call('/api/settings')[0],200);self.assertTrue(json.loads(self.call('/api/settings')[1])['can_edit'])
 def test_default_deny_method_matrix(self):
  for method in ['GET','POST','PUT','PATCH','DELETE','HEAD','OPTIONS']:
   self.assertFalse(shared_access.allowed('/api/new-admin-method',method))
  for p in shared_access.VISITOR_POSTS:self.assertTrue(shared_access.allowed(p,'POST'));self.assertFalse(shared_access.allowed(p,'DELETE'))
class ImportedProxyPreserved(unittest.TestCase):
 def test_preexisting_owner_bound_child_not_marked_shared(self):
  from chatify import server, nerdload
  from tests.test_gallery import _write_gallery
  old_children,old_register=nerdload.GALLERY_CHILDREN,nerdload.GALLERY_REGISTER
  self.addCleanup(setattr,nerdload,"GALLERY_CHILDREN",old_children);self.addCleanup(setattr,nerdload,"GALLERY_REGISTER",old_register)
  servers=[];real=server.LocalHTTPServer
  def factory(*args,**kwargs):
   address,handler=args
   if address[1]==8080:address=(address[0],0)
   srv=real(address,handler,**kwargs);servers.append(srv);return srv
  with tempfile.TemporaryDirectory() as d:
   _write_gallery(d)
   p=d+'/gallery.yaml';text=open(p).read().replace('type: openai, model: gpt-4o-mini, api_key_env: OPENAI_API_KEY','type: mock');open(p,'w').write(text)
   with patch.object(server,'LocalHTTPServer',side_effect=factory):
    t=threading.Thread(target=server.serve_gallery,args=(p,),kwargs={'host':'127.0.0.1','port':0},daemon=True);t.start()
    for _ in range(100):
     if len(servers)>=3:break
     time.sleep(.01)
   try:
    cfg=schema.validate({'server':{'public':True},'storage':{'path':d+'/imported.db'}});cfg['_dir']=d
    imported=ThreadingHTTPServer(('127.0.0.1',0),make_handler(cfg,Engine(cfg,Store(cfg['storage']['path']))));threading.Thread(target=imported.serve_forever,daemon=True).start()
    nerdload.GALLERY_CHILDREN['nerd-existing']={'port':imported.server_port,'owner':'visitor:'+'a'*32}
    root='http://127.0.0.1:'+str(servers[-1].server_port)
    def read(cookie,path):
     req=urllib.request.Request(root+path,headers={'Cookie':'cc_visitor='+cookie})
     try:
      with urllib.request.urlopen(req) as r:return r.status,r.read()
     except urllib.error.HTTPError as e:return e.code,e.read()
    # Authenticated loopback registration cannot overwrite either built-in
    # or previously registered child entries, even with a valid parent HMAC.
    before=dict(nerdload.GALLERY_CHILDREN)
    nerdload.GALLERY_CHILDREN['nerd-built'] = before['alpha']
    for slug in ['nerd-existing','nerd-built']:
     request=urllib.request.Request(root+'/__cc_nerds',data=json.dumps({'parent':'nerd-existing','slug':slug,'port':imported.server_port}).encode(),headers={'Content-Type':'application/json','X-CC-Token':nerdload._reg_token('nerd-existing')},method='POST')
     with self.assertRaises(urllib.error.HTTPError) as denied:urllib.request.urlopen(request)
     self.assertEqual(denied.exception.code,409)
     self.assertEqual(nerdload.GALLERY_CHILDREN[slug], before.get(slug,before['alpha']))
    status,body=read('a'*32,'/nerd-existing/api/settings');self.assertEqual(status,200);self.assertTrue(json.loads(body)['can_edit'])
    self.assertEqual(read('b'*32,'/nerd-existing/api/settings')[0],403)
    self.assertEqual(read('a'*32,'/alpha/api/settings')[0],403)
   finally:
    imported.shutdown();imported.server_close()
    for srv in reversed(servers):srv.shutdown();srv.server_close()
if __name__=='__main__':unittest.main()
