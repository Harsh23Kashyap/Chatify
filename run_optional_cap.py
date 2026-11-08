import subprocess,tempfile,time,urllib.request,sys,socket,os
from pathlib import Path
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'app.yaml';p.write_text('app: {id: blank, title: Blank Start}\nprovider: {type: mock}\nsources: []\nstorage: {path: data/chatify.db}\n')
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 with open('/downloads/chatify-free-api-flow-20261108/local-server.log','w') as log:
  proc=subprocess.Popen([sys.executable,'-m','chatify','run',str(p),'--port',str(port),'--no-browser'],stdout=log,stderr=log)
  try:
   for _ in range(100):
    try:urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/api/health',timeout=1).close();break
    except OSError:time.sleep(.05)
   subprocess.run(['node','tests/builder_optional_call_cap_browser.cjs'],env={**os.environ,'CHATIFY_TEST_URL':'http://127.0.0.1:'+str(port)},timeout=100,check=True)
  finally:proc.terminate();proc.wait()
