"""Disposable app configuration/isolation/cleanup, offline only, no provider/source calls."""
import copy,hashlib,io,json,os,pathlib,socket,subprocess,sys,tempfile,time,unittest,urllib.request,urllib.error,zipfile
from unittest.mock import Mock,patch
from chatify import gallery,schema,prompts,providers
from chatify.pipeline import Engine
from chatify.store import Store
from chatify.portable import bundle
ROOT=pathlib.Path(__file__).resolve().parents[1];SLUG='context-qualification-20261107';APP=ROOT/'apps'/SLUG
class Config(unittest.TestCase):
 def test_unique_config_and_unchanged_connector_no_helper(self):
  g=gallery.load(str(ROOT/'apps/gallery.yaml'));t=next(x for x in g['apps']if x['slug']==SLUG)['cfg'];q=next(x for x in g['apps']if x['slug']=='quakebrief')['cfg']
  self.assertTrue(t['memory']['enabled']);self.assertEqual(t['memory']['summary_every'],50);self.assertFalse(q['memory']['enabled']);self.assertTrue(t['server']['public']);self.assertEqual(t['provider']['api_key_env'],'OPENAI_API_KEY');self.assertIn('PUBLIC TEST',t['app']['title']);self.assertEqual(t['storage']['path'],'data/context-qualification-20261107.db');self.assertNotEqual(t['_dir'],q['_dir']);self.assertFalse(t['actions']['allow']);self.assertNotIn('helper_drafts',t);self.assertNotIn('imported_keys',t)
  self.assertEqual((APP/'context_qualification_sources.py').read_bytes(),(ROOT/'apps/quakebrief/quake_sources.py').read_bytes());self.assertNotEqual(t['sources'][0]['id'],q['sources'][0]['id']);self.assertNotEqual(t['sources'][0]['entry'],q['sources'][0]['entry'])
 def test_no_key_export_omits_private_state_and_key_values(self):
  cfg=schema.load(str(APP/'app.yaml'))
  with tempfile.TemporaryDirectory()as folder:
   base=pathlib.Path(folder);cfg['_dir']=folder;cfg['_path']=str(base/'app.yaml');shutil=__import__('shutil');shutil.copy2(APP/'context_qualification_sources.py',base/'context_qualification_sources.py');(base/'data').mkdir();(base/'data/context-qualification-20261107.db').write_text('PRIVATE CHAT MARKER');(base/'data/keys.json').write_text('PRIVATE KEY MARKER')
   with patch.dict(os.environ,{'OPENAI_API_KEY':'PRIVATE ENV KEY MARKER'}):data,_=bundle(cfg,include_keys=False,prompt_value=cfg['pipeline_prompts'])
   with zipfile.ZipFile(io.BytesIO(data))as z:
    text='\n'.join(z.read(n).decode('utf8','replace')for n in z.namelist()if not n.endswith('/'));self.assertNotIn('PRIVATE',text);self.assertTrue(all(not n.endswith('.db') and 'keys.json'not in n for n in z.namelist()))
 def test_summary50_no_generation_after_two_actual_stored_turns(self):
  cfg=schema.load(str(APP/'app.yaml'));e=Engine(cfg,Store(':memory:'),connectors={});e.provider=Mock();chat=e.store.new_chat('visitor:A');topic=e.store.new_topic('visitor:A','synthetic')
  for i in range(2):
   e.store.add_turn(chat,topic,'Synthetic question','Synthetic standalone','Public answer',[],[],'standard');e._summarize('visitor:A',topic,chat)
  e.provider.complete.assert_not_called()
 def test_history_owner_chat_topic_isolation_not_simulated_model_semantics(self):
  cfg=schema.load(str(APP/'app.yaml'));store=Store(':memory:');e=Engine(cfg,store,connectors={});chat=store.new_chat('visitor:A');topic=store.new_topic('visitor:A','synthetic');store.add_turn(chat,topic,'Call first event Cedar','Cedar is a synthetic label','Cedar is USGS fixture event.',[],[],'standard');self.assertTrue(e.conversation_history('visitor:A',chat,topic,'Cedar?'))
  with self.assertRaises(PermissionError):e.conversation_history('visitor:B',chat,topic,'Cedar?')
  other=store.new_chat('visitor:A');self.assertEqual(e.conversation_history('visitor:A',other,topic,'Cedar?'),[]);other_topic=store.new_topic('visitor:A','other');self.assertEqual(e.conversation_history('visitor:A',chat,other_topic,'Cedar?'),[])

 def test_actual_two_visitor_http_chats_and_turns_isolation(self):
  from http.server import ThreadingHTTPServer
  from chatify.server import make_handler
  import threading
  cfg=schema.load(str(APP/'app.yaml'));cfg['server']['public']=True;cfg['provider']['type']='mock'
  with tempfile.TemporaryDirectory()as folder:
   store=Store(str(pathlib.Path(folder)/'context.db'));e=Engine(cfg,store,connectors={});H=make_handler(cfg,e);srv=ThreadingHTTPServer(('127.0.0.1',0),H);thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(srv.server_port)
   A='a1b2c3d4'*4;B='b1c2d3e4'*4
   def req(path,cookie,data=None):
    body=json.dumps(data).encode()if data is not None else None
    request=urllib.request.Request(origin+path,data=body,headers={'Cookie':'cc_visitor='+cookie,'Content-Type':'application/json'})
    try:
     with urllib.request.urlopen(request)as r:return r.status,json.load(r)
    except urllib.error.HTTPError as er:return er.code,json.load(er)
   try:
    status,row=req('/api/chats',A,{'title':'Synthetic Cedar context'});self.assertEqual(status,200);chat=row['id'];topic=store.new_topic('visitor:'+A,'synthetic');store.add_turn(chat,topic,'Cedar label','Cedar','Public fixture answer',[],[],'standard')
    self.assertEqual(len(req('/api/chats',A)[1]),1);self.assertEqual(req('/api/chats',B),(200,[]));self.assertEqual(req('/api/turns?chat='+chat,B)[0],404);self.assertEqual(len(req('/api/turns?chat='+chat,A)[1]),1)
   finally:srv.shutdown();srv.server_close();thread.join()

class RouteCleanup(unittest.TestCase):
 def test_removed_route_returns404_not_just_hidden_card_and_existing_store_untouched(self):
  # Two short-lived MOCK galleries share only an unrelated fixture app store.
  with tempfile.TemporaryDirectory()as folder:
   base=pathlib.Path(folder)
   for name in ('existing',SLUG):
    d=base/name;d.mkdir();(d/'app.yaml').write_text('app: {id: '+name+', title: Fixture}\nprovider: {type: mock}\nsources: []\nstorage: {path: data/private.db}\n')
   existing=base/'existing/data';existing.mkdir();sentinel=existing/'unrelated.txt';sentinel.write_text('unrelated existing-app data')
   def serve(with_test):
    conf=base/'gallery.yaml';conf.write_text('gallery:\n  apps:\n    - {dir: existing, slug: existing}\n'+('    - {dir: '+SLUG+', slug: '+SLUG+'}\n'if with_test else ''))
    sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close();env=dict(os.environ);env.pop('OPENAI_API_KEY',None);p=subprocess.Popen([sys.executable,'-m','chatify','run',str(conf),'--host','127.0.0.1','--port',str(port),'--no-browser'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    origin='http://127.0.0.1:'+str(port)
    for _ in range(80):
     try:
      with urllib.request.urlopen(origin+'/api/health',timeout=1)as r:
       if r.status==200:return p,origin
     except (OSError,urllib.error.URLError):time.sleep(.05)
    p.terminate();p.wait();raise AssertionError('mock gallery failed startup')
   p,origin=serve(True)
   try:
    with urllib.request.urlopen(origin+'/'+SLUG+'/api/config')as r:self.assertEqual(r.status,200)
   finally:p.terminate();p.wait()
   # Cleanup is exact tracked app-directory removal in new image, no broad rm.
   __import__('shutil').rmtree(base/SLUG);p,origin=serve(False)
   try:
    for suffix in ('/','/api/config','/api/chats','/settings.html'):
     with self.assertRaises(urllib.error.HTTPError)as err:urllib.request.urlopen(origin+'/'+SLUG+suffix)
     self.assertEqual(err.exception.code,404)
    with urllib.request.urlopen(origin+'/api/health')as r:self.assertNotIn(SLUG,json.load(r)['apps'])
    with urllib.request.urlopen(origin+'/existing/api/config')as r:self.assertEqual(r.status,200)
    self.assertEqual(sentinel.read_text(),'unrelated existing-app data');self.assertFalse((base/SLUG).exists())
   finally:p.terminate();p.wait()
