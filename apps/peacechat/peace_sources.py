"""Key-free peace-news adapter for PeaceChat.

GDELT DOC 2.0 (api.gdeltproject.org): recent world news coverage, free and
key-less. Rate limit: one request per 5 seconds, so calls are spaced and the
plain-text rate-limit notice is retried with backoff. Returns plain evidence
dicts; untrusted source text is passed through as data only.
"""
import json, re, time, urllib.parse, urllib.request, urllib.error

_UA = {'User-Agent': 'Chatify-PeaceChat/1.0 (+https://github.com/Harsh23Kashyap/Chatify)', 'Accept': 'application/json'}
_STOP = {'what','whats','is','are','was','were','the','a','an','of','for','how','do','does','can','i','me','my','tell','show','give','about','in','to','and','with','good','best','some','please','did','which','that','when','where','who','whom','have','has','had'}
# already covered by _PEACE_TERMS, so skip them in user keywords
_PEACE_WORDS = {'peace','agreement','agreements','deal','talks','accord','process','ceasefire','reconciliation','peacebuilding','mediation','peacemaking','treaty','treaties'}

_PEACE_TERMS = '("peace agreement" OR "peace deal" OR "peace talks" OR "peace accord" OR "peace process" OR ceasefire OR reconciliation OR peacebuilding OR mediation)'
_HOST = 'https://api.gdeltproject.org/api/v2/doc/doc'
_SPACING = 5.5
_last = [0.0]
_MON = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def _keywords(q):
    words = re.findall(r"[\w'-]+", q or '', flags=re.UNICODE)
    keep = [w for w in words if w.lower() not in _STOP and w.lower() not in _PEACE_WORDS and len(w) > 2]
    return ' '.join(keep[:4])[:80]

def _throttle():
    wait = _SPACING - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()

def _get(url, attempts=3, cap=2_000_001):
    last_err = 'failed'
    for i in range(attempts):
        _throttle()
        req = urllib.request.Request(url, headers=_UA)
        try:
            with urllib.request.urlopen(req, timeout=25) as reply:
                raw = reply.read(cap).decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            last_err = 'HTTP %s' % e.code
        except Exception:
            last_err = 'unreachable'
        else:
            try:
                data = json.loads(raw)
                if isinstance(data, dict):
                    return data
                last_err = 'busy'
            except ValueError:
                last_err = 'busy'  # the rate-limit notice comes back as plain text
        if i + 1 < attempts:
            time.sleep(6)
    raise ValueError('GDELT news API %s; try again shortly.' % last_err)

def _date(raw):
    m = re.match(r'(\d{4})(\d{2})(\d{2})T', str(raw or ''))
    if not m:
        return '', ''
    yyyy, mm, dd = m.groups()
    pretty = '%d %s %s' % (int(dd), _MON[int(mm)], yyyy)
    return yyyy, pretty

def gdelt(query, k=12):
    kw = _keywords(query)
    q = ('%s %s' % (kw, _PEACE_TERMS)) if kw else _PEACE_TERMS
    count = max(1, min(int(k), 15))
    url = _HOST + '?' + urllib.parse.urlencode({
        'query': q + ' sourcelang:english',
        'mode': 'artlist',
        'maxrecords': count,
        'format': 'json',
        'sort': 'hybridrel',
    })
    payload = _get(url)
    articles = payload.get('articles') or []
    out = []
    seen = set()
    for a in articles:
        if not isinstance(a, dict):
            continue
        link = str(a.get('url') or '').strip()
        title = re.sub(r'\s+', ' ', str(a.get('title') or '')).strip()
        if not link or not title or link in seen:
            continue
        seen.add(link)
        domain = str(a.get('domain') or '').strip()
        country = str(a.get('sourcecountry') or '').strip()
        year, pretty = _date(a.get('seendate'))
        text = ('News article indexed by GDELT.\nHeadline: %s\nOutlet: %s%s\nSeen: %s\nLink: %s'
                % (title, domain or 'unknown', (' (%s)' % country) if country else '',
                   pretty or 'undated', link))
        out.append({'id': link, 'title': title, 'text': text, 'url': link,
                    'year': year, 'venue': 'GDELT news index (%s)' % (domain or 'unknown outlet'),
                    'source': 'gdelt', 'score': 1.0 / (len(out) + 1)})
    return out[:count]
