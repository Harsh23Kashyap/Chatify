"""Known provider pages inspected during development. No live requests or key creation."""
import copy,re
PAGES={
 'wikipedia':{'name':'Wikipedia','page':'https://www.mediawiki.org/wiki/API:Main_page','key_required':False,'source':{'id':'wikipedia','label':'Wikipedia','type':'wikipedia','lang':'en'}},
 'brave':{'name':'Brave Search','page':'https://brave.com/search/api/','key_required':True,'docs':'https://api-dashboard.search.brave.com/app/documentation/web-search/get-started','key_page':'https://api-dashboard.search.brave.com/register'},
 'open-meteo':{'name':'Open-Meteo','page':'https://open-meteo.com/en/docs','key_required':False},
 'openrouteservice':{'name':'openrouteservice','page':'https://api.openrouteservice.org/','docs':'https://api.openrouteservice.org/','key_page':'https://openrouteservice.org/dev/#/signup','key_required':True},
 'mapbox':{'name':'Mapbox','page':'https://www.mapbox.com/','docs':'https://docs.mapbox.com/accounts/guides/tokens/','key_page':'https://docs.mapbox.com/accounts/guides/tokens/','key_required':True},
}
def enrich(items):
 result=copy.deepcopy(items)
 for item in result:
  for field in ('provider_page','docs_url','key_url','key_required'):item.pop(field,None)
  name=re.sub(r'[^a-z0-9]','',str(item.get('service','')).lower())
  for key,info in PAGES.items():
   if name in {re.sub(r'[^a-z0-9]','',key),re.sub(r'[^a-z0-9]','',info['name'].lower())}:
    item['provider_page']=info['page'];item['key_required']=info['key_required'];item['docs_url']=info.get('docs',info['page']);item['key_url']=info.get('key_page',info['page']) if info['key_required'] else '';break
 return result
def helper_kind(kind):return 'search' if re.fullmatch(r'search_[a-z0-9_]{1,60}',kind or '') else kind

def complete_drafts(raw,require_helpers=True):
 """Complete generated API setup without activating code or making requests."""
 from . import generators
 raw=copy.deepcopy(raw);raw['api_suggestions']=enrich(raw.get('api_suggestions',[]))
 for i,pick in enumerate(raw['api_suggestions']):
  if not str(pick.get('service','')).strip():raise ValueError('API recommendations must name a concrete service pick')
  helper=pick.get('helper')
  if require_helpers and not helper:raise ValueError('Missing independent code helper for API '+pick['service'])
  if helper:
   ok,problems=generators.review_code('search',helper['code'])
   if not ok:raise ValueError('API helper contract failed: '+'; '.join(problems))
   if 'helper_drafts' in raw:raw['helper_drafts']['search_api_'+str(i+1)]=copy.deepcopy(helper)
  if 'sources' in raw and not pick.get('key_required',True):
   info=next((x for x in PAGES.values() if x['page']==pick.get('provider_page')),None)
   if info and info.get('source') and not any(s.get('type')==info['source']['type'] for s in raw['sources']):raw['sources'].append(copy.deepcopy(info['source']))
 return raw
