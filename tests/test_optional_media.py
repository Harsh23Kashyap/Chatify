import json
import tempfile
import unittest
from pathlib import Path
from chatify.optional_media import hosted_video, HOSTED_MEDIA

class OptionalMediaTests(unittest.TestCase):
    def test_missing_known_only(self):
        with tempfile.TemporaryDirectory() as folder:
            web = Path(folder)
            (web/'media/stories').mkdir(parents=True)
            (web/'media/stories/manifest.json').write_text(json.dumps({'stories': [{'id':'mouse-mic','src':'mouse-mic.mp4'}]}))
            self.assertEqual(hosted_video('media/stories/mouse-mic.mp4', web), HOSTED_MEDIA+'stories/mouse-mic.mp4')
            self.assertEqual(hosted_video('media/paperworks-walkthrough.mp4', web), HOSTED_MEDIA+'paperworks-walkthrough.mp4')
            for name in ('media/unknown.mp4','media/../private.mp4','media/stories/../../private.mp4','media/https://evil.invalid/x.mp4','media/stories/manifest.json','private.mp4'):
                self.assertIsNone(hosted_video(name, web), name)
            (web/'media/stories/mouse-mic.mp4').write_bytes(b'local')
            self.assertIsNone(hosted_video('media/stories/mouse-mic.mp4', web))
    def test_bad_manifest_is_not_external_redirect_authority(self):
        with tempfile.TemporaryDirectory() as folder:
            web = Path(folder);(web/'media/stories').mkdir(parents=True)
            (web/'media/stories/manifest.json').write_text(json.dumps({'stories':[{'id':'../private','src':'../private.mp4'},{'id':'mouse-mic','src':'https://evil.invalid/x.mp4'}]}))
            self.assertIsNone(hosted_video('media/stories/mouse-mic.mp4', web))
            self.assertIsNone(hosted_video('media/stories/../private.mp4', web))


class OptionalMediaHttp(unittest.TestCase):
    def test_local_missing_video_redirect(self):
        import threading
        import urllib.request
        import urllib.error
        from http.server import ThreadingHTTPServer
        from unittest.mock import patch
        from chatify import schema, server
        from chatify.pipeline import Engine
        from chatify.store import Store
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args):return None
        with tempfile.TemporaryDirectory() as folder:
            web=Path(folder)/'web';(web/'media/stories').mkdir(parents=True)
            (web/'media/stories/manifest.json').write_text(json.dumps({'stories':[{'id':'mouse-mic','src':'mouse-mic.mp4'}]}))
            cfg=schema.load(str(Path(__file__).resolve().parents[1]/'apps/minimal/app.yaml'))
            engine=Engine(cfg,Store(str(Path(folder)/'test.db')))
            with patch.object(server,'WEB',str(web)):
                srv=ThreadingHTTPServer(('127.0.0.1',0),server.make_handler(cfg,engine))
                thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
                try:
                    base='http://127.0.0.1:'+str(srv.server_port)
                    opener=urllib.request.build_opener(NoRedirect)
                    for path in ('media/stories/mouse-mic.mp4','media/paperworks-walkthrough.mp4'):
                        with self.assertRaises(urllib.error.HTTPError) as cm:
                            opener.open(urllib.request.Request(base+'/'+path,headers={'Range':'bytes=0-31'}))
                        self.assertEqual(cm.exception.code,302)
                        self.assertEqual(cm.exception.headers['Location'],HOSTED_MEDIA+path.removeprefix('media/'))
                    with self.assertRaises(urllib.error.HTTPError) as cm:opener.open(base+'/media/private.mp4')
                    self.assertEqual(cm.exception.code,404)
                finally:srv.shutdown();srv.server_close();thread.join()

if __name__ == '__main__':unittest.main()
