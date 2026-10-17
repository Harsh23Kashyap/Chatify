"""Preserve usable connector data without running or evaluating returned text."""
import json
from .base import Evidence

def recover_evidence(value, source, limit=6):
    limit=max(1,min(int(limit),50))
    if isinstance(value,str):
        raw=value.strip()[:100000]
        if not raw:return []
        try:value=json.loads(raw)
        except ValueError:return [Evidence('Source reply',raw[:4000],source=source)]
    if isinstance(value,dict):
        if value.get('status')=='error' or value.get('errors') or value.get('error'):
            raise ValueError('Connector returned an error, not evidence')
        for key in ('results','items','data','evidence'):
            if isinstance(value.get(key),(list,str)):
                return recover_evidence(value[key],source,limit)
        value=[value]
    if not isinstance(value,list):raise ValueError('Connector returned no usable data')
    out=[]
    for item in value[:limit]:
        if isinstance(item,str):
            out.extend(recover_evidence(item,source,limit-len(out)))
        elif isinstance(item,dict):
            text=item.get('text') or item.get('abstract') or item.get('snippet') or item.get('content')
            if isinstance(text,(dict,list)):text=json.dumps(text,ensure_ascii=False)
            if not isinstance(text,str) or not text.strip():continue
            title=item.get('title') or item.get('name') or 'Source reply'
            url=item.get('url') or item.get('link') or ''
            authors=item.get('authors') or []
            if not isinstance(authors,list):authors=[str(authors)]
            out.append(Evidence(str(title)[:400],text[:10000],str(url)[:2000],authors[:20],item.get('year') or '',str(item.get('venue') or '')[:400],source,1/(len(out)+1),str(item.get('id') or '')[:400]))
        if len(out)>=limit:break
    return out[:limit]
