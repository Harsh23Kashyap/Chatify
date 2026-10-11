import unittest,tempfile,threading,json,urllib.request,os
from http.server import ThreadingHTTPServer
from customchat import schema
from customchat.store import Store
from customchat.pipeline import Engine
from customchat.server import make_handler
class SavedAppearance(unittest.TestCase):
 def test_named_state_roundtrip_and_legacy_load(self):
  with tempfile.TemporaryDirectory() as folder:
   cfg=schema.validate({'storage':{'path':os.path.join(folder,'s.db')}});cfg['_dir']=folder
   store=Store(cfg['storage']['path']);engine=Engine(cfg,store);server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(cfg,engine));threading.Thread(target=server.serve_forever,daemon=True).start();root='http://127.0.0.1:'+str(server.server_port)
   def api(path,body=None):
    req=urllib.request.Request(root+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'});return json.load(urllib.request.urlopen(req))
   try:
    theme=api('/api/theme')['theme'];theme['light']['brand']='#123456';theme['font']='space-grotesk';api('/api/theme',{'theme':theme});api('/api/states/save',{'name':'appearance'});api('/api/theme',{'reset':True});restored=api('/api/states/load',{'name':'appearance'});self.assertEqual(restored['theme']['light']['brand'],'#123456');self.assertEqual(restored['theme']['font'],'space-grotesk');self.assertEqual(api('/api/states')['current'],'appearance')
    store.save_state('local','legacy',restored['settings']);self.assertEqual(api('/api/states/load',{'name':'legacy'})['settings'],restored['settings'])
   finally:server.shutdown();server.server_close()
if __name__=='__main__':unittest.main()
