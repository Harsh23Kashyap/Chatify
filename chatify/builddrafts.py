"""Owner-scoped local draft snapshots. No provider calls or runtime application."""
import hashlib,json,os,re,tempfile,threading,time,uuid
from pathlib import Path
def review_note(review=None,local_review=None):
 """Retain review findings as a historical note, never a safety verdict."""
 review=review if isinstance(review,dict) else {}
 lines=['Final model review: '+str(review.get('review_status') or 'not recorded')+'. Historical findings, not verification of this draft or deployment readiness.']
 if review.get('review_note'):lines.append(str(review['review_note']))
 if review.get('issues'):lines.append('Model suggestions, not verification: '+' '.join(str(x) for x in review['issues']))
 if review.get('setup_notes'):lines.append('Before deployment: '+' '.join(str(x) for x in review['setup_notes']))
 if local_review:lines.append('Local observations, limited checks: '+' '.join(str(x) for x in local_review))
 lines.append('These findings are not cleared by editing, validation or saving. A model can miss unsafe prompts or code. No findings does not establish safety.')
 return '\n'.join(lines)

class BuildDrafts:
 def __init__(self,folder):self.folder=Path(folder)/'build-drafts';self.lock=threading.RLock()
 def _dir(self,owner):return self.folder/hashlib.sha256(str(owner).encode()).hexdigest()
 def _path(self,owner,ident):
  if not isinstance(ident,str) or len(ident)>64 or not ident.replace('-','').isalnum():raise ValueError('Invalid draft identifier')
  return self._dir(owner)/(ident+'.json')
 def put(self,owner,yaml_text,title='',ident=None,sections=None,review_note=None):
  from .appbuilder import validate_declared
  import yaml
  clean,declared=validate_declared(yaml_text)
  cred_words={'key','apikey','password','passwd','secret','token','credentials'}
  def cred(name):
   return bool(cred_words & set(re.split(r'[^a-z0-9]+',str(name).lower())))
  def scrub(value):
   if isinstance(value,dict):return {k:(scrub(v) if isinstance(v,(dict,list)) else ('' if cred(k) and isinstance(v,str) else v)) for k,v in value.items()}
   if isinstance(value,list):return [scrub(v) for v in value]
   return value
  selected=declared.copy()
  if sections is not None:
   from .appbuilder import sections as checked_sections
   selected=set(checked_sections(sections))
   if selected-declared:raise ValueError('Draft is missing selected sections')
   if declared-selected:raise ValueError('Draft contains sections outside your selection')
  text=yaml.safe_dump(scrub({key:value for key,value in clean.items() if key in selected}),sort_keys=False)
  if len(text.encode())>8000000:raise ValueError('Draft is too large')
  ident=ident or uuid.uuid4().hex;path=self._path(owner,ident);record={'id':ident,'title':str(title or clean['app']['title'])[:120],'yaml':text,'sections':sections if sections is not None else [key for key in clean if key in selected],'updated':time.time(),'notice':'Saved local draft, not applied. Credential fields excluded; review before use.'}
  with self.lock:
   if review_note is None and path.is_file():
    try:review_note=json.loads(path.read_text()).get('review_note')
    except (ValueError,OSError):pass
   if isinstance(review_note,str) and review_note.strip():record['review_note']=review_note
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
