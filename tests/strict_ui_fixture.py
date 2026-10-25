"""Fresh isolated local fixture server for the strict browser regression scripts.
Run: CHATIFY_TEST_URL=http://127.0.0.1:8145 python tests/strict_ui_fixture.py
No network source or model calls are configured. Data disappears on exit.
"""
import os,tempfile
from urllib.parse import urlparse
from http.server import ThreadingHTTPServer
from chatify import schema
from chatify.store import Store
from chatify.pipeline import Engine
from chatify.server import make_handler

def serve():
 with tempfile.TemporaryDirectory(prefix='chatify-ui-') as folder:
  cfg=schema.validate({'app':{'id':'newsnerd','title':'NewsNerd','tagline':'Understand the news. Check the source.'},'storage':{'path':folder+'/state.db'}});cfg['_dir']=folder
  import yaml as _yaml
  from pathlib import Path as _Path
  _appfile=_Path(folder)/'app.yaml';_appfile.write_text(_yaml.safe_dump({k:cfg[k] for k in schema.DEFAULTS}));cfg['_path']=str(_appfile)
  s=Store(cfg['storage']['path']);owner='local'
  t=s.new_topic(owner,'Multi-chat undo fixture')
  for n in range(2):
   c=s.new_chat(owner,'Multi-chat fixture '+str(n+1));s.add_turn(c,t,'Multi-chat question '+str(n+1),'Multi-chat question '+str(n+1),'Multi-chat answer '+str(n+1),[],[],'standard')
  evidence=[{'n':1,'title':'Sample AI report','source':'Feed','url':'https://example.org/a','year':'2026'}, {'n':2,'title':'Sample energy opinion','source':'Feed','url':'https://example.org/b','year':'2026'}, {'n':3,'title':'Sample India report','source':'Other','url':'https://example.org/c','year':'2026'}]
  c=s.new_chat(owner,'Hindi export fixture');t=s.new_topic(owner,'Hindi export fixture')
  s.add_turn(c,t,'हिंदी में उत्तर','हिंदी में उत्तर','स्रोत के अनुसार नमस्ते [1]।',evidence,[],'standard')
  c=s.new_chat(owner,'Navigation fixture');t=s.new_topic(owner,'Navigation fixture')
  for i in range(6):s.add_turn(c,t,'Navigation question '+str(i+1),'Navigation question '+str(i+1),('Long fixture paragraph for scroll navigation. '*12+'\n')*6,evidence,[],'standard')
  c=s.new_chat(owner,'Cedar fixture');t=s.new_topic(owner,'Cedar fixture')
  s.add_upload(owner,'Fixture A','Cedar accepts ZIP and PDF files. Cedar files are validated on upload. Rowan maintains Cedar.')
  s.add_turn(c,t,'Which files does Cedar accept?','Which files does Cedar accept?','Cedar accepts ZIP files [1].',[{'n':1,'title':'Fixture A','source':'Feed','url':'https://example.org/cedar','year':'2026'}],[],'standard')
  c=s.new_chat(owner,'Verified count sample');t=s.new_topic(owner,'Sample headlines')
  answer='Retrieved headline count by source (this sample only).\n\n| Source | Headline count | Citations |\n| --- | --- | --- |\n| Feed | 2 | [1] [2] |\n| Other | 1 | [3] |'
  s.add_turn(c,t,'Chart headline count by source','Chart headline count by source',answer,evidence,[],'standard')
  url=urlparse(os.environ.get('CHATIFY_TEST_URL','http://127.0.0.1:8145'))
  if url.hostname not in ('127.0.0.1','localhost'):raise ValueError('Fixture binds local only')
  ThreadingHTTPServer((url.hostname,url.port or 8145),make_handler(cfg,Engine(cfg,s))).serve_forever()
if __name__=='__main__':serve()
