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
