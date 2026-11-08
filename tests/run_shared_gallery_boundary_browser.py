"""Offline real-proxy/browser fixture. Requires Node, Playwright and Chrome locally."""
import os, socket, subprocess, sys, tempfile, time, urllib.request
from test_gallery import _write_gallery
with tempfile.TemporaryDirectory() as folder:
    _write_gallery(folder)
    path=folder+'/gallery.yaml'
    with open(path) as handle: text=handle.read()
    text=text.replace('type: openai, model: gpt-4o-mini, api_key_env: OPENAI_API_KEY','type: mock').replace('dir: alpha, slug: alpha,','dir: alpha, slug: alpha, featured: true,')
    with open(path,'w') as handle: handle.write(text)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
    with tempfile.TemporaryFile() as log:
        proc=subprocess.Popen([sys.executable,'-m','chatify','run',path,'--port',str(port),'--no-browser'],stdout=log,stderr=log)
        try:
            for _ in range(100):
                try:
                    urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/api/health',timeout=1).close(); break
                except OSError: time.sleep(.05)
            else: raise RuntimeError('Fixture failed to start')
            subprocess.run(['node','tests/shared_gallery_boundary_browser.cjs'],env={**os.environ,'CHATIFY_TEST_URL':'http://127.0.0.1:'+str(port)},timeout=45,check=True)
        finally:
            proc.terminate();proc.wait()
