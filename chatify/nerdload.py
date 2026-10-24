"""Review portable Nerds without importing code, then launch in a separate local workspace."""
import base64,hashlib,hmac,io,json,os,re,shutil,socket,subprocess,sys,threading,zipfile
from pathlib import Path,PurePosixPath
import yaml
from . import schema
from .portable import _check_values,ExportError
# When a gallery dispatcher hosts this process, serve_gallery points this at its
# child-port registry so loaded Nerds are reachable at same-origin /<slug>/ paths
# instead of loopback URLs that only work on the host computer.
READY_POLLS=240  # 240 x READY_INTERVAL = 60s readiness budget; throttled free hosts boot a child Python slowly
READY_INTERVAL=.25

GALLERY_CHILDREN = None
# A spawned guest workspace runs in its own process, where the registry above is
# absent. The dispatcher hands down a loopback registration endpoint + bearer so
# workspaces launched from inside a workspace still land at same-origin /<slug>/.
GALLERY_REGISTER = None
def _reg_token(slug):
 # Per-workspace registration credential: HMAC of the dispatcher's master
 # secret with the workspace slug. The dispatcher re-computes it server-side,
 # so a workspace can only register descendants under itself, never under an
 # arbitrary owner or parent.
 return hmac.new(GALLERY_REGISTER['token'].encode(),slug.encode(),hashlib.sha256).hexdigest()
def _global_cap():
 try:return int(os.environ.get('CHATIFY_NERD_GLOBAL_CAP') or 0) or 4
 except ValueError:return 4
def _hosted():
 return GALLERY_CHILDREN is not None or bool(os.environ.get('CHATIFY_GALLERY_REGISTER'))
def _nerd_limit():
 # A hosted gallery shares one small server with its built-in apps, so it runs
 # fewer guest workspaces than a desktop install unless the host sets a limit.
 try:return int(os.environ.get('CHATIFY_NERD_LIMIT') or 0) or (2 if _hosted() else 4)
 except ValueError:return 2 if _hosted() else 4
def _register_remote(payload):
 import urllib.request,urllib.error
 req=urllib.request.Request(os.environ['CHATIFY_GALLERY_REGISTER'],data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','X-CC-Token':os.environ.get('CHATIFY_GALLERY_TOKEN','')},method='POST')
 try:
  with urllib.request.urlopen(req,timeout=5) as resp:resp.read()
 except urllib.error.HTTPError as e:
  try:msg=json.loads(e.read().decode('utf-8','replace')).get('error','')
  except Exception:msg=''
  raise ValueError(msg or 'The workspace could not register with the demo server.') from None
MAX_UPLOAD=8*1024*1024
MAX_EXPANDED=32*1024*1024
_ALLOWED={'.yaml','.yml','.json','.md','.txt','.csv','.pdf','.py'}
class NerdLoader:
 def __init__(self,folder):
  self.root=Path(folder)/'nerds';self.pending={};self.children=[];self.workspaces={};self.lock=threading.Lock()
  if self.root.is_dir():
   for folder in self.root.glob('nerd-*'):
    if folder.is_symlink() or not folder.is_dir():continue
    try:
     config=yaml.safe_load((folder/'app.yaml').read_text());title=str(config['app']['title'])[:120]
     self.workspaces[folder.name]={'folder':folder,'process':None,'title':title,'url':''}
    except (OSError,ValueError,TypeError,KeyError):pass
 def review(self,name,encoded):
  try:data=base64.b64decode(encoded,validate=True)
  except Exception:raise ValueError('Invalid upload') from None
  if sum(p.poll() is None for p in self.children)>=_nerd_limit():raise ValueError('Up to %d Nerds can run here. Stop a running workspace before loading more.'%_nerd_limit())
  if len(data)>MAX_UPLOAD:raise ValueError('Bundle limit is 8 MB')
  files={}
  if name.lower().endswith('.zip'):
   try:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
     if len(z.infolist())>500:raise ValueError('Too many files')
     # Validate paths and private names before ignoring benign metadata.
     for info in z.infolist():
      path=PurePosixPath(info.filename)
      if path.is_absolute() or '..' in path.parts or '\\' in info.filename or re.match(r'^[A-Za-z]:',info.filename):raise ValueError('Unsafe path in bundle: '+info.filename)
      if (info.external_attr>>16)&0o170000==0o120000:raise ValueError('Symlinks are not allowed: '+info.filename)
      if any(re.match(r'^\.env(?:$|[._-])',part,re.I) or part.lower() in ('.ssh','.aws','.azure','.gnupg','.npmrc','.pypirc','.netrc') for part in path.parts):raise ValueError('Private file is not allowed: '+info.filename)
     names={str(PurePosixPath(i.filename).name) for i in z.infolist() if not i.is_dir()}
     if 'pyproject.toml' in names and any('/chatify/__init__.py' in '/'+i.filename for i in z.infolist()):raise ValueError('This is the Chatify source ZIP, not a Nerd bundle. Install it to run Chatify. To share a Nerd, use Download app ZIP in Configuration.')
     total=0
     for info in z.infolist():
      path=PurePosixPath(info.filename)
      if path.is_absolute() or '..' in path.parts or '\\' in info.filename or re.match(r'^[A-Za-z]:',info.filename):raise ValueError('Unsafe path in bundle')
      if (info.external_attr>>16)&0o170000==0o120000:raise ValueError('Symlinks are not allowed')
      if info.is_dir():continue
      benign={'.gitignore','.gitattributes','.editorconfig','.DS_Store','.github','.git','__MACOSX'}
      hidden=[x for x in path.parts if x.startswith('.') or x=='__MACOSX']
      if hidden:
       if all(x in benign or x.startswith('._') for x in hidden):continue
       raise ValueError('Unsupported hidden file: '+info.filename)
      if re.search(r'(secret|credential|password|token|chatify\.db|accounts|sessions)',info.filename,re.I):raise ValueError('Private file is not allowed: '+info.filename)
      if len(info.filename)>240:raise ValueError('Path too long')
      if path.suffix.lower() not in _ALLOWED:raise ValueError('Unsupported file: '+info.filename)
      total+=info.file_size
      if total>MAX_EXPANDED:raise ValueError('Expanded bundle is too large')
      if info.filename in files:raise ValueError('Duplicate path')
      files[info.filename]=z.read(info)
   except zipfile.BadZipFile:raise ValueError('Invalid ZIP') from None
  elif name.lower().endswith(('.yaml','.yml','.json')):files['app.yaml']=data
  else:raise ValueError('Choose a Nerd ZIP or YAML/JSON app file')
  apps=[n for n in files if PurePosixPath(n).name in ('app.yaml','app.yml','app.json')]
  if len(apps)!=1:raise ValueError('Bundle must contain exactly one app.yaml (or app.json)')
  prefix=str(PurePosixPath(apps[0]).parent)
  if prefix!='.':
   if any(not n.startswith(prefix+'/') for n in files):raise ValueError('All files must be inside the app folder')
   files={n[len(prefix)+1:]:v for n,v in files.items()}
  appname=next(n for n in files if PurePosixPath(n).name in ('app.yaml','app.yml','app.json'))
  try:raw=yaml.safe_load(files[appname].decode('utf-8'))
  except Exception:raise ValueError('Invalid app YAML/JSON') from None
  if isinstance(raw,dict) and 'articles' in raw and 'app' not in raw and 'provider' not in raw and 'sources' not in raw:
   raise ValueError('This looks like an API response, not a Nerd app. In Code helpers, open Search connector, then Match a real response and paste this JSON there. It will not be imported or run.')
  from .keybundle import extract
  raw,imported_keys=extract(raw)
  try:cfg=schema.validate(raw);_check_values(cfg)
  except (schema.ConfigError,ExportError) as e:raise ValueError(str(e)) from None
  files[appname]=yaml.safe_dump(cfg,sort_keys=False).encode()
  for name,content in files.items():
   if name.endswith('.json') and name!=appname:
    try:_check_values(json.loads(content))
    except (ValueError,ExportError):raise ValueError('Invalid or private JSON file: '+name) from None
  if cfg['auth']['mode']!='none':raise ValueError('Local imported Nerds must use auth.mode: none. Set up hosted authentication separately.')
  for name in ('data/theme.json','data/prompts.json'):
   if name in files:
    from . import theme,prompts
    d=json.loads(files[name])
    if name.endswith('theme.json'):files[name]=json.dumps(theme.clean(d)).encode()
    elif not isinstance(d,dict) or set(d)-{'text','on'} or not isinstance(d.get('text',{}),dict) or not isinstance(d.get('on',{}),dict) or any(k not in prompts.STAGES or not isinstance(v,str) or len(v)>prompts.MAX_LEN for k,v in d.get('text',{}).items()) or any(k not in prompts.STAGES or type(v)!=bool for k,v in d.get('on',{}).items()):raise ValueError('Invalid prompt settings')
  empty_sources=[]
  for src in cfg['sources']:
   for field in ('path','module'):
    v=src.get(field)
    if not v:continue
    p=PurePosixPath(v)
    if p.is_absolute() or '..' in p.parts or '\\' in v:raise ValueError('Sources must stay inside the bundle')
   if src['type']=='local_files':
    path=src.get('path','docs').rstrip('/')
    if not any(n.startswith(path+'/') for n in files):empty_sources.append((src['label'],path))
   if src['type']=='python':
    mod=src.get('entry','').partition(':')[0]
    if not re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*',mod):raise ValueError('Invalid Python module entry')
    if mod.replace('.','/')+'.py' not in files:raise ValueError('Python connector module is missing from bundle')
  for src in cfg['sources']:
   if src['type']=='python':src['execution']='bounded'
  cfg['storage']={'path':'data/chatify.db'};cfg['server']['host']='127.0.0.1';cfg['actions']={'allow':[],'writes':False}
  files.pop(appname);files['app.yaml']=yaml.safe_dump(cfg,sort_keys=False).encode()
  code=[n for n in files if n.endswith('.py')]
  if sum(len(files[n]) for n in code)>200000:raise ValueError('Connector code is too large to review here')
  envs=sorted({src.get('api_key_env') for src in cfg['sources'] if src.get('api_key_env')}|({cfg['provider']['api_key_env']} if cfg['provider'].get('api_key_env') else set()))
  from .readiness import check
  readiness=check(cfg,files,raw)
  for label,path in empty_sources:readiness['rows'].append({'kind':'setup','item':label,'message':'No documents included for '+path+'. An empty source folder will be created. Add documents in the new workspace before asking source-backed questions.'})
  if not readiness['can_load']:raise ValueError('Python connector does not compile. Fix it before loading.')
  envs=readiness['required_env']
  token=hashlib.sha256(data).hexdigest()
  with self.lock:
   if len(self.pending)>=4:self.pending.pop(next(iter(self.pending)))
   self.pending[token]=(files,cfg,code,imported_keys)
  from . import theme
  look=theme.clean(json.loads(files['data/theme.json'])) if 'data/theme.json' in files else theme.clean(cfg.get('appearance',{}))
  preview={'title':look.get('txt_title') or cfg['app']['title'],'tagline':look.get('txt_tagline') or cfg['app']['tagline'],'mode':look.get('mode','light'),'colors':look.get('dark' if look.get('mode')=='dark' else 'light',{}),'examples':cfg['app'].get('examples',[])[:3],'files':sorted(files),'static':True}
  if _hosted():warnings_hosted='Hosted workspace: it runs on this demo server, only this browser can open it, and it disappears when the demo restarts or redeploys. Add API keys in the new workspace Configuration; nothing is shared with other visitors.'
  from . import bundle_review
  result_warnings=['Python uses a bounded process, NOT a sandbox. Host files/network remain accessible; code review required.','Separate local workspace. Current app is not overwritten.',str(len(imported_keys))+' API key entries will be placed in this workspace private key storage. Values are not shown. Accounts and chat history are not imported.','Imported local apps disable write actions. Review remote sources before asking a question.']
  if _hosted():result_warnings[1]=warnings_hosted
  return {'hosted':_hosted(),'auto_review':bundle_review.review(cfg,files),'preview':preview,'readiness':readiness,'token':token,'title':cfg['app']['title'],'tagline':cfg['app']['tagline'],'provider':cfg['provider']['type'],'model':cfg['provider']['model'],'sources':[{'id':s['id'],'label':s.get('label',s['id']),'type':s['type']} for s in cfg['sources']],'required_env':envs,'imported_key_count':len(imported_keys),'code':[{'path':n,'text':files[n].decode('utf-8')} for n in code],'warnings':result_warnings}
 def load(self,token,allow_code=False,owner='local'):
  with self.lock:item=self.pending.get(token)
  if not item:raise ValueError('Review the bundle first')
  files,cfg,code,imported_keys=item
  hosted=_hosted()
  if code and not allow_code:raise ValueError('Review Python code and explicitly allow it before loading')
  depth=0
  if hosted:
   try:depth=int(os.environ.get('CHATIFY_NERD_DEPTH') or 0)
   except ValueError:depth=0
   if depth>=2:raise ValueError('Workspaces on this demo server cannot launch further workspaces of their own. Make your changes in the main demo app and use it there.')
  from .launcher import pick_port
  import tempfile
  self.root.mkdir(parents=True,exist_ok=True)
  folder=Path(tempfile.mkdtemp(prefix='nerd-',dir=str(self.root)))
  for name,data in files.items():
   p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  for src in cfg['sources']:
   if src['type']=='local_files':(folder/src.get('path','docs')).mkdir(parents=True,exist_ok=True)
  port=pick_port(8090)
  cfg['server']['port']=port;(folder/'app.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False))
  if imported_keys:
   from .secrets import SecretStore
   key_store=SecretStore(str(folder/'data'))
   for name,value in imported_keys.items():key_store.set(name,value)
  slug=folder.name
  url='/'+slug+'/' if hosted else 'http://127.0.0.1:'+str(port)
  log=open(folder/'run.log','wb')
  # The host's own keys never enter a guest workspace: on a hosted gallery the
  # child gets no key material at all, so each visitor adds their own keys in
  # the workspace Configuration. Desktop loads keep declared env keys only.
  declared_env=set() if hosted else {cfg['provider'].get('api_key_env','')}|{src.get('api_key_env','') for src in cfg['sources']}
  child_env={k:v for k,v in os.environ.items() if not re.search(r'(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)',k,re.I) or k in declared_env}
  if hosted:
   # Nested launches register through the dispatcher: hand the endpoint, this
   # workspace's registration credential (re-added after the key scrub), its
   # slug and depth to the new workspace process.
   if GALLERY_REGISTER:child_env['CHATIFY_GALLERY_REGISTER']=GALLERY_REGISTER['url'];child_env['CHATIFY_GALLERY_TOKEN']=_reg_token(slug)
   else:
    if os.environ.get('CHATIFY_GALLERY_REGISTER'):child_env['CHATIFY_GALLERY_REGISTER']=os.environ['CHATIFY_GALLERY_REGISTER']
    if os.environ.get('CHATIFY_GALLERY_TOKEN'):child_env['CHATIFY_GALLERY_TOKEN']=os.environ['CHATIFY_GALLERY_TOKEN']
   child_env['CHATIFY_NERD_SLUG']=slug
   child_env['CHATIFY_NERD_DEPTH']=str(depth+1)
  with self.lock:
   if sum(p.poll() is None for p in self.children)>=_nerd_limit():
    log.close();raise ValueError('Maximum %d running Nerds. Stop a running workspace before loading more.'%_nerd_limit())
   if GALLERY_CHILDREN is not None and sum(1 for v in GALLERY_CHILDREN.values() if isinstance(v,dict))>=_global_cap():
    log.close();raise ValueError('This demo server is at its workspace limit (%d). Stop a running workspace before loading more.'%_global_cap())
   child=subprocess.Popen([sys.executable,'-m','chatify','run',str(folder/'app.yaml'),'--no-browser'],stdout=log,stderr=subprocess.STDOUT,cwd=str(Path(__file__).resolve().parents[1]),env=child_env)
   self.children.append(child)
  log.close();self.workspaces[folder.name]={'folder':folder,'process':child,'title':cfg['app']['title'],'url':url,'owner':owner,'slug':slug,'hosted':hosted}
  import time,urllib.request
  probe='http://127.0.0.1:'+str(port)
  for _ in range(READY_POLLS):
   if child.poll() is not None:raise ValueError('Nerd could not start. Check dependencies and connector setup in '+str(folder/'run.log'))
   try:
    with urllib.request.urlopen(probe+'/api/health',timeout=.5):
     if hosted:
      if GALLERY_CHILDREN is not None:GALLERY_CHILDREN[slug]={'port':port,'owner':owner,'depth':1}
      else:
       try:_register_remote({'slug':slug,'port':port,'parent':os.environ.get('CHATIFY_NERD_SLUG','')})
       except Exception:
        child.terminate()
        try:child.wait(timeout=3)
        except subprocess.TimeoutExpired:child.kill();child.wait()
        raise ValueError('The workspace started but could not register with the demo server. Try again.')
     return {'url':url,'title':cfg['app']['title'],'workspace':str(folder),'hosted':hosted}
   except OSError:time.sleep(READY_INTERVAL)
  child.terminate();raise ValueError('Nerd did not become ready; current app is unchanged')
 def _unregister(self,slug):
  if not slug:return
  if GALLERY_CHILDREN is not None:GALLERY_CHILDREN.pop(slug,None)
  elif os.environ.get('CHATIFY_GALLERY_REGISTER'):
   try:_register_remote({'slug':slug,'parent':os.environ.get('CHATIFY_NERD_SLUG',''),'unregister':True})
   except Exception:pass
 def list(self,owner=None):
  with self.lock:
   return [{'id':key,'title':v['title'],'url':v['url'],'slug':v.get('slug'),'hosted':bool(v.get('hosted')),'running':v['process'] is not None and v['process'].poll() is None} for key,v in self.workspaces.items() if owner is None or (v.get('owner') or 'local')==owner]
 def stop(self,key,owner=None):
  with self.lock:item=self.workspaces.get(key)
  if not item or (owner is not None and (item.get('owner') or 'local')!=owner):raise ValueError('Unknown imported workspace')
  if GALLERY_CHILDREN is not None and item.get('slug'):
   # Never orphan a nested workspace: a parent cannot stop while a registered
   # descendant is alive. Dead registrations are forgotten on sight.
   alive=[]
   for s,v in list(GALLERY_CHILDREN.items()):
    if isinstance(v,dict) and v.get('parent')==item['slug']:
     try:socket.create_connection(('127.0.0.1',v['port']),timeout=.5).close();alive.append(s)
     except OSError:GALLERY_CHILDREN.pop(s,None)
   if alive:raise ValueError('This workspace has a running workspace of its own (%s). Stop it from inside the workspace first.'%', '.join(sorted(alive)))
  proc=item['process']
  if proc and proc.poll() is None:
   proc.terminate()
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill();proc.wait()
  self._unregister(item.get('slug'))
  return {'stopped':True}
 def remove(self,key,confirmed,owner=None):
  if confirmed is not True:raise ValueError('Confirm removal of this imported workspace')
  with self.lock:item=self.workspaces.get(key)
  if not item or (owner is not None and (item.get('owner') or 'local')!=owner):raise ValueError('Unknown imported workspace')
  self.stop(key,owner=owner);folder=item['folder']
  if folder.is_symlink() or folder.parent.resolve()!=self.root.resolve():raise ValueError('Workspace path changed; removal stopped')
  # A just-stopped child can still be releasing its files on a loaded host; give
  # the removal one short retry before failing honestly. The registry entry is
  # popped only after the files are gone - never leave a ghost entry that claims
  # a removable workspace while its credentials folder is already deleted, and
  # never report removed while files remain.
  import time as _time
  try:
   shutil.rmtree(folder)
  except OSError:
   _time.sleep(0.5)
   try:shutil.rmtree(folder)
   except OSError as exc:raise ValueError('Workspace files could not be deleted yet (%s). The workspace is stopped; try Remove again in a few seconds.'%exc)
  with self.lock:self.workspaces.pop(key,None)
  return {'removed':True}
 def close(self):
  for child in self.children:
   if child.poll() is None:
    child.terminate()
    try:child.wait(timeout=3)
    except subprocess.TimeoutExpired:child.kill();child.wait()
