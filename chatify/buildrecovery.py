"""Recover reviewed, config-only bundles into new owner drafts, never jobs."""
import hashlib,json
from . import appbuilder
HISTORY_NAMES=('REVIEW-HISTORY.txt','FINAL-REVIEW-CONCERNS.txt')
MAX_HISTORY=65536

def prepare(files,cfg,code,imported_keys):
 """No execution, keys, documents or active Python connectors cross this route."""
 if code or imported_keys or any(s.get('type') in ('python','local_files') for s in cfg['sources']):
  raise ValueError('Editable draft recovery supports configuration-only bundles without Python, local documents or imported keys. Use the normal import review for this bundle.')
 allowed={'app.yaml','README.md','README.txt','provenance.json','manifest.json','API-SUGGESTIONS.json','data/theme.json','data/prompts.json','data/code-drafts.json',*HISTORY_NAMES}
 if set(files)-allowed:raise ValueError('Editable recovery would omit companion files. Use the normal import review instead.')
 for name,key in [('data/theme.json','appearance'),('data/prompts.json','pipeline_prompts'),('data/code-drafts.json','helper_drafts'),('API-SUGGESTIONS.json','api_suggestions')]:
  if name not in files:continue
  try:matches=json.loads(files[name].decode('utf-8'))==cfg.get(key)
  except (ValueError,UnicodeDecodeError):matches=False
  if not matches:raise ValueError('Companion configuration differs from app.yaml: '+name+'. Use normal import review; no editable draft was saved.')
 text=files['app.yaml'].decode('utf-8');appbuilder.validate(text)
 note='Recovered from an imported bundle, not a resumed AI job. Historical text is unverified and may describe an older configuration. No model, helper or source was run. No safety or deployment readiness established.\nBundle-normalized YAML SHA256: '+hashlib.sha256(files['app.yaml']).hexdigest()+'\n'
 for name in (*HISTORY_NAMES,'provenance.json'):
  if name in files:
   if len(files[name])>MAX_HISTORY:raise ValueError('Recovery companion exceeds 64 KB: '+name)
   try:companion=files[name].decode('utf-8')
   except UnicodeDecodeError:raise ValueError('Recovery companions must be UTF-8: '+name) from None
   note+='\nUnverified companion '+name+':\n'+companion+'\n'
 if not any(name in files for name in HISTORY_NAMES):note+='No review history was included. This does not mean a review passed.\n'
 if len(note.encode('utf-8'))>MAX_HISTORY:raise ValueError('Combined recovery history exceeds 64 KB. No draft was saved.')
 return {'yaml':text,'title':cfg['app']['title'],'sections':list(cfg),'review_note':note}
