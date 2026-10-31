"""Known provider pages inspected during development. No live requests or key creation."""
import copy,re
PAGES={
 'pubmed':{'name':'PubMed','page':'https://www.ncbi.nlm.nih.gov/books/NBK25501/','docs':'https://eutilities.github.io/site/API_Key/usageandkey/','key_required':False,'source':{'id':'pubmed','label':'PubMed','type':'pubmed'}},
 'openalex':{'name':'OpenAlex','page':'https://developers.openalex.org/api-reference/introduction','docs':'https://developers.openalex.org/guides/authentication','key_page':'https://openalex.org/settings/api','key_required':False,'key_optional':True},
 'arxiv':{'name':'arXiv','page':'https://info.arxiv.org/help/api/index.html','docs':'https://info.arxiv.org/help/api/user-manual.html','key_required':False,'source':{'id':'arxiv','label':'arXiv','type':'arxiv'}},
 'crossref':{'name':'Crossref','page':'https://www.crossref.org/documentation/retrieve-metadata/rest-api/','key_required':False,'source':{'id':'crossref','label':'Crossref','type':'crossref'}},
 'wikipedia':{'name':'Wikipedia','page':'https://www.mediawiki.org/wiki/API:Main_page','key_required':False,'source':{'id':'wikipedia','label':'Wikipedia','type':'wikipedia','lang':'en'}},
 'brave':{'name':'Brave Search','page':'https://brave.com/search/api/','key_required':True,'docs':'https://api-dashboard.search.brave.com/app/documentation/web-search/get-started','key_page':'https://api-dashboard.search.brave.com/register'},
 'open-meteo':{'name':'Open-Meteo','page':'https://open-meteo.com/en/docs','key_required':False},
 'openrouteservice':{'name':'openrouteservice','page':'https://api.openrouteservice.org/','docs':'https://api.openrouteservice.org/','key_page':'https://openrouteservice.org/dev/#/signup','key_required':True},
 'mapbox':{'name':'Mapbox','page':'https://www.mapbox.com/','docs':'https://docs.mapbox.com/accounts/guides/tokens/','key_page':'https://docs.mapbox.com/accounts/guides/tokens/','key_required':True},
}
ALIASES={'openalexworksapi':'openalex','crossrefrestapi':'crossref','pubmedandthencbientrezeutilities':'pubmed'}
def enrich(items):
 result=copy.deepcopy(items)
 for item in result:
  for field in ('provider_page','docs_url','key_url','key_required'):item.pop(field,None)
  name=re.sub(r'[^a-z0-9]','',str(item.get('service') or item.get('name','')).lower())
  name=ALIASES.get(name,name)
  for key,info in PAGES.items():
   if name in {re.sub(r'[^a-z0-9]','',key),re.sub(r'[^a-z0-9]','',info['name'].lower())}:
    item['provider_page']=info['page'];item['key_required']=info['key_required'];item['docs_url']=info.get('docs',info['page']);item['key_url']=info.get('key_page',info['page']) if info['key_required'] or info.get('key_optional') else '';break
 return result
def helper_kind(kind):return 'search' if re.fullmatch(r'search_[a-z0-9_]{1,60}',kind or '') else kind

def check_description(pick):
 service=re.sub(r'[^a-z0-9]','',str(pick.get('service','')).lower())
 for field in ('what','reason'):
  text=str(pick.get(field,'')).strip()
  if len(text)<40 or len(text.split())<7 or re.sub(r'[^a-z0-9]','',text.lower())==service:raise ValueError('API '+field+' must be a useful sentence, not only a service name or short label')

def complete_drafts(raw,require_helpers=True,activate_sources=True):
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
   if 'helper_drafts' in raw and pick.get('selected',True):raw['helper_drafts']['search_api_'+str(i+1)]=copy.deepcopy(helper)
  if activate_sources and 'sources' in raw and pick.get('selected',True) and not pick.get('key_required',True):
   info=next((x for x in PAGES.values() if x['page']==pick.get('provider_page')),None)
   if info and info.get('source') and not any(s.get('type')==info['source']['type'] for s in raw['sources']):raw['sources'].append(copy.deepcopy(info['source']))
 return raw
