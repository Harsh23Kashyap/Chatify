import json,tempfile,threading,unittest,urllib.request,yaml
from pathlib import Path
from http.server import ThreadingHTTPServer
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
from chatify.server import make_handler

class BuilderLaunch(unittest.TestCase):
 def test_saved_app_starts_separately_preserves_parent(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'docs').mkdir();(root/'docs'/'guide.md').write_text('Evidence for fixture: conversation memory is saved between questions.')
   raw={'app':{'title':'Saved launch fixture'},'sources':[{'id':'docs','type':'local_files','path':'docs'}]};(root/'app.yaml').write_text(yaml.safe_dump(raw));cfg=schema.load(str(root/'app.yaml'));cfg['_path']=str(root/'app.yaml');store=Store(str(root/'data'/'chatify.db'));eng=Engine(cfg,store);server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(cfg,eng));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();url='http://127.0.0.1:'+str(server.server_port)
   try:
    def post(path,body):
     req=urllib.request.Request(url+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
     try:
      with urllib.request.urlopen(req) as r:return json.load(r)
     except urllib.error.HTTPError as e:raise AssertionError(e.read().decode())
    reviewed=post('/api/settings/build/review',{'yaml':yaml.safe_dump(raw),'sections':['app','sources']})
    saved=post('/api/settings/build/save',{'ticket':reviewed['ticket'],'confirmed':True})
    req=urllib.request.Request(url+'/api/settings/build/launch',data=json.dumps({'ticket':saved['launch_ticket']}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req) as r:result=json.load(r)
    with urllib.request.urlopen(result['url']+'/api/config') as r:child=json.load(r)
    self.assertEqual(child['app']['title'],'Saved launch fixture');self.assertTrue((Path(result['workspace'])/'assets'/'source-1'/'guide.md').exists())
    with urllib.request.urlopen(url+'/api/health') as r:self.assertTrue(json.load(r)['ok'])
    with self.assertRaises(AssertionError):post('/api/settings/build/launch',{'ticket':saved['launch_ticket']})
    reviewed=post('/api/settings/build/review',{'yaml':yaml.safe_dump(raw),'sections':['app','sources']})
    saved2=post('/api/settings/build/save',{'ticket':reviewed['ticket'],'confirmed':True})
    (root/'data'/'theme.json').write_text('{}')
    with self.assertRaises(AssertionError) as changed:post('/api/settings/build/launch',{'ticket':saved2['launch_ticket']})
    self.assertIn('Saved setup changed',str(changed.exception))

    with urllib.request.urlopen(url+'/api/nerds') as r:rows=json.load(r)['workspaces']
    stop=urllib.request.Request(url+'/api/nerds/stop',data=json.dumps({'id':rows[0]['id']}).encode(),headers={'Content-Type':'application/json'})
    urllib.request.urlopen(stop).close()
    raw['app']['title']='Unsaved app';bad=urllib.request.Request(url+'/api/settings/build/launch',data=json.dumps({'yaml':yaml.safe_dump(raw),'sections':['app','sources']}).encode(),headers={'Content-Type':'application/json'})
    with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(bad)
    self.assertEqual(error.exception.code,400)
   finally:server.shutdown();server.server_close();thread.join()
