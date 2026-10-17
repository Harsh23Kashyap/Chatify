"""Explicit credential import/export transport. No credential values in review output."""
import copy,json,re
from . import schema,secrets
MAX_KEYS=40
def extract(raw):
 if not isinstance(raw,dict):return raw,{}
 raw=copy.deepcopy(raw);keys=raw.pop('api_keys',{})
 if not isinstance(keys,dict) or len(keys)>MAX_KEYS:raise ValueError('Invalid api_keys mapping')
 p=raw.get('provider',{})
 if isinstance(p,dict) and 'api_key' in p:
  key=p.pop('api_key')
  if key:keys[p.get('type','')]=key
 for source in raw.get('sources',[]) if isinstance(raw.get('sources',[]),list) else []:
  if isinstance(source,dict) and 'api_key' in source:
   key=source.pop('api_key')
   if key:keys['source:'+str(source.get('id',''))]=key
 clean={}
 from . import source_credentials
 for source in raw.get('sources',[]) if isinstance(raw.get('sources',[]),list) else []:
  if not isinstance(source,dict):continue
  for env in (source.get('header_env') or {}).values():
   if 'env:'+env in keys:keys[source_credentials.name(source.get('id',''),env,source.get('url',''))]=keys.pop('env:'+env)
 for name,value in keys.items():
  if not value:continue
  if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9_:-]{1,120}',name) or not isinstance(value,str) or len(value)>4096 or any(c.isspace() for c in value):raise ValueError('Invalid imported API key entry')
  if name not in schema.PROVIDERS and not name.startswith(('source:','search:','env:','http:','catalog:')):raise ValueError('Unrecognized API key destination')
  clean[name]=value
 return raw,clean
def export_keys(cfg):
 """Only called after explicit local-owner export choice."""
 if not secrets.STORE:return {}
 keys={}
 names=set(schema.PROVIDERS)
 from . import websearch
 names.update('search:'+k for k in websearch.PROVIDERS)
 names.add('catalog:openalex')
 from . import source_credentials
 for item in source_credentials.declared(cfg):names.add(source_credentials.name(item['source'],item['env'],item['url']))
 for source in cfg['sources']:
  names.add('source:'+source['id'])
  if source.get('api_key_env'):names.add('env:'+source['api_key_env'])
 for name in sorted(names):
  value=secrets.STORE.get(name)
  if value:keys[name]=value
 return keys
