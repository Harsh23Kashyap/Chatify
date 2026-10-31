"""Attributed guidance excerpts and bounded key-free Europe PMC abstract search.

No field-specific application rates. Abstracts are research, not local prescriptions.
"""
import html
import json
import re
import urllib.parse
import urllib.request
import urllib.error
import time
from pathlib import Path
from chatify.connectors.local_files import LocalFiles

BASE=Path(__file__).resolve().parent
URLS={
 'fao-nutrients.md': 'https://openknowledge.fao.org/server/api/core/bitstreams/9a5b9373-3558-43b3-b732-f69326a7314d/content',
 'soil-report.md': 'https://extension.umn.edu/agriculture/crop-production/nutrient-management-for-minnesota-crops/understanding-the-soil-test-report',
}
_index=None

def guidance(query,k=8):
    # Guidance snapshots cannot establish a location-specific research finding.
    # Literature requests use the research connector; an empty search stays empty.
    if re.search(r'\b(research|studies|study|trials?)\b',str(query),re.I):return []
    global _index
    if _index is None:_index=LocalFiles({'id':'agriculture-guides','label':'Guidance snapshots','path':'docs'},str(BASE))
    out=_index.search(query,k)
    for row in out:
        row['url']=URLS.get(row.get('document'),'')
        row['venue']='FAO global principles (2017)' if row.get('document')=='fao-nutrients.md' else 'University of Minnesota Extension (regional guidance)'
        scope='GLOBAL PRINCIPLES: not local research for any named country.' if row.get('document')=='fao-nutrients.md' else 'REGIONAL GUIDANCE: Minnesota, United States only; not validated for other regions.'
        row['text']=scope+' Dated guidance excerpt, checked 31 October 2026. Not a field-specific fertilizer recommendation. '+row['text']
    return out

def _clean(text):return ' '.join(html.unescape(re.sub('<[^>]+>',' ',str(text or ''))).split())

def research(query,k=8):
    # A generic choice question should not promote a random crop experiment to advice.
    if re.search(r'\b(choos\w*|select\w*)\b',str(query),re.I) and re.search(r'\bfertili[sz]er\b',str(query),re.I) and not re.search(r'\b(research|studies|study|trial)\b',str(query),re.I):return []
    stop={'what','does','do','the','a','an','is','are','of','for','and','or','in','on','about','say','research','how','can','i','my','should','please','tell','me','to','with','from','it','help','know','before','choosing','choose','farm','explain','tell','us','you','your','grow','growing','grown','have','has','am','at','which','these','those','please','information'}
    words=[w for w in re.findall(r"[\w'-]+",str(query),flags=re.UNICODE) if w.lower() not in stop][:18]
    if not words:return []
    # Plain user words cannot inject Europe PMC field operators or widen the scope.
    terms=' AND '.join('TITLE_ABS:"'+word.replace('"','')+'"' for word in words)
    scoped='('+terms+') AND (TITLE_ABS:agricultur* OR TITLE_ABS:crop* OR TITLE_ABS:fertiliz* OR TITLE_ABS:fertilis* OR TITLE_ABS:agronom* OR TITLE_ABS:farming) AND HAS_ABSTRACT:Y'
    if int(k)<=0:return []
    count=max(1,min(int(k),10))
    url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':scoped,'format':'json','resultType':'core','pageSize':count})
    req=urllib.request.Request(url,headers={'User-Agent':'Chatify-AgricultureChat/1.0 (+https://github.com/Harsh23Kashyap/Chatify)','Accept':'application/json'})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req,timeout=20) as response:
                raw=response.read(2_000_001)
            break
        except urllib.error.HTTPError as error:
            if attempt or error.code not in (429,500,502,503,504):raise
            time.sleep(2)
    if len(raw)>2_000_000:raise ValueError('Europe PMC response too large; try a narrower crop question.')
    payload=json.loads(raw.decode('utf-8'))
    out=[]
    seen=set()
    for row in (payload.get('resultList') or {}).get('result',[]):
        title,text=_clean(row.get('title')),_clean(row.get('abstractText'))
        sid=str(row.get('id') or '');source=str(row.get('source') or '')
        if not title or not text or not re.fullmatch(r'[A-Z]+',source) or not re.fullmatch(r'[A-Za-z0-9.]+',sid):continue
        doi=str(row.get('doi') or '')
        link='https://doi.org/'+urllib.parse.quote(doi,safe='/') if doi else 'https://europepmc.org/article/'+source+'/'+sid
        identity=(doi.lower() or title.lower().rstrip('.'))
        if identity in seen or title.lower().rstrip('.') in seen:continue
        seen.update((identity,title.lower().rstrip('.')))
        preprint=source=='PPR' or str(row.get('pubTypeList') or '').lower().find('preprint')>=0
        prefix='Research abstract only. '+('PREPRINT: not established peer-reviewed guidance. ' if preprint else '')+'Study findings are not a farm-specific recommendation. '
        out.append({'id':'europepmc:'+source+':'+sid,'title':_clean(title),'text':prefix+text[:4500],'url':link,'authors':[a.get('fullName','') for a in (row.get('authorList') or {}).get('author',[]) if isinstance(a,dict)][:6],'year':str(row.get('pubYear') or ''),'venue':((row.get('journalInfo') or {}).get('journal') or {}).get('title') or 'Europe PMC research abstract','source':'agriculture-research','score':1/(len(out)+1)})
    return out[:count]
