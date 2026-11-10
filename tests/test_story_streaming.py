import json,pathlib,tempfile,unittest,threading,urllib.request,urllib.error
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from chatify.story_media import missing_story_url,CANONICAL_HOST,CANONICAL_BASE
from chatify import schema,server
from chatify.pipeline import Engine
from chatify.store import Store
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
class StoryStreaming(unittest.TestCase):
 def test_bounded_manifest_only_and_no_redirect_loop(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'media/stories';p.mkdir(parents=True)
   (p/'manifest.json').write_text(json.dumps({'stories':[{'id':'beaver-refresh','src':'beaver-refresh-gain24.mp4'}]}))
   name='media/stories/beaver-refresh-gain24.mp4'
   self.assertEqual(missing_story_url(name,d),CANONICAL_BASE+'beaver-refresh-gain24.mp4')
   for bad in ['media/stories/beaver-refresh.mp4','media/stories/unknown.mp4','media/stories/../beaver-refresh-gain24.mp4','https://evil.invalid/file.mp4','media/stories/manifest.json']:
    self.assertEqual(missing_story_url(bad,d),'')
   self.assertEqual(missing_story_url(name,d,CANONICAL_HOST),'')
   (p/'beaver-refresh-gain24.mp4').write_bytes(b'video')
   self.assertEqual(missing_story_url(name,d),'')
 def test_actual_http_missing_selected_redirects_but_local_files_stay_local(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'media/stories';p.mkdir(parents=True)
   (p/'manifest.json').write_text(json.dumps({'stories':[{'id':'beaver-refresh','src':'beaver-refresh-gain24.mp4'}]}))
   cfg=schema.validate({});cfg['_dir']=d;cfg['storage']['path']='data/test.db'
   e=Engine(cfg,Store(':memory:'))
   with patch.object(server,'WEB',d):
    srv=ThreadingHTTPServer(('127.0.0.1',0),server.make_handler(cfg,e));t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
    try:
     url='http://127.0.0.1:'+str(srv.server_port)+'/media/stories/beaver-refresh-gain24.mp4'
     opener=urllib.request.build_opener(NoRedirect)
     with self.assertRaises(urllib.error.HTTPError) as err:opener.open(url)
     self.assertEqual(err.exception.code,302);self.assertEqual(err.exception.headers['Location'],CANONICAL_BASE+'beaver-refresh-gain24.mp4')
     (p/'beaver-refresh-gain24.mp4').write_bytes(b'local video')
     with opener.open(url) as r:self.assertEqual(r.read(),b'local video');self.assertEqual(r.status,200)
    finally:srv.shutdown();srv.server_close();t.join()
