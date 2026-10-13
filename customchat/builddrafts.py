"""Owner-scoped local draft snapshots. No provider calls or runtime application."""
import hashlib,json,os,tempfile,threading,time,uuid
from pathlib import Path
class BuildDrafts:
 def __init__(self,folder):self.folder=Path(folder)/'build-drafts';self.lock=threading.RLock()
 def _dir(self,owner):return self.folder/hashlib.sha256(str(owner).encode()).hexdigest()
 def _path(self,owner,ident):
  if not isinstance(ident,str) or len(ident)>64 or not ident.replace('-','').isalnum():raise ValueError('Invalid draft identifier')
  return self._dir(owner)/(ident+'.json')
 def put(self,owner,yaml_text,title='',ident=None,sections=None):
  from .appbuilder import validate
  import yaml
  clean=validate(yaml_text)
  def scrub(value):
   if isinstance(value,dict):return {k:('' if any(x in k.lower() for x in ('api_key','password','secret','token')) else scrub(v)) for k,v in value.items()}
   if isinstance(value,list):return [scrub(v) for v in value]
   return value
  selected=set(yaml.safe_load(yaml_text))
  if sections is not None:
   from .appbuilder import sections as checked_sections
   selected=set(checked_sections(sections))
   if selected-set(yaml.safe_load(yaml_text)):raise ValueError('Draft is missing selected sections')
   if set(yaml.safe_load(yaml_text))-selected:raise ValueError('Draft contains sections outside your selection')
  text=yaml.safe_dump(scrub({key:value for key,value in clean.items() if key in selected}),sort_keys=False)
  if len(text.encode())>8000000:raise ValueError('Draft is too large')
  ident=ident or uuid.uuid4().hex;path=self._path(owner,ident);record={'id':ident,'title':str(title or clean['app']['title'])[:120],'yaml':text,'sections':sections if sections is not None else [key for key in clean if key in selected],'updated':time.time(),'notice':'Saved local draft, not applied. Credential fields excluded; review before use.'}
  with self.lock:
   path.parent.mkdir(parents=True,exist_ok=True);os.chmod(path.parent,0o700)
   fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.draft-')
   try:
    with os.fdopen(fd,'w') as f:json.dump(record,f)
    os.replace(tmp,path);os.chmod(path,0o600)
   finally:
    if os.path.exists(tmp):os.unlink(tmp)
  return record
 def get(self,owner,ident):
  with self.lock:
   path=self._path(owner,ident)
   if not path.is_file():raise ValueError('Draft not found')
   record=json.loads(path.read_text())
   import yaml
   from .appbuilder import sections as checked_sections
   raw=yaml.safe_load(record['yaml'])
   selected=checked_sections(record.get('sections') or list(raw))
   if set(selected)-set(raw):raise ValueError('Saved draft is missing selected sections')
   record['yaml']=yaml.safe_dump({key:value for key,value in raw.items() if key in selected},sort_keys=False)
   record['sections']=selected
   return record
 def list(self,owner):
  with self.lock:
   records=[]
   for path in self._dir(owner).glob('*.json'):
    try:
     d=json.loads(path.read_text());records.append({k:d[k] for k in ('id','title','updated','notice')})
    except (ValueError,OSError,KeyError):continue
   return sorted(records,key=lambda x:x['updated'],reverse=True)[:100]
