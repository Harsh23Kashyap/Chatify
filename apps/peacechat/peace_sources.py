"""PeaceChat report adapters. ReliefWeb requires RELIEFWEB_APPNAME.

GDELT is retained for existing configs.

GDELT DOC 2.0 (api.gdeltproject.org): recent world news coverage, free and
key-less. Rate limit: one request per 5 seconds, so calls are spaced and the
plain-text rate-limit notice is retried with backoff. Returns plain evidence
dicts; untrusted source text is passed through as data only.
"""
import json, re, time, os, urllib.parse, urllib.request, urllib.error

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


_RELIEFWEB_HOST = 'https://api.reliefweb.int/v2/reports'
_RELIEFWEB_TERMS = '("peace agreement" OR "peace process" OR "peace talks" OR peacebuilding OR reconciliation OR mediation OR ceasefire)'

def reliefweb(query, k=12):
    appname = os.environ.get('RELIEFWEB_APPNAME', '').strip()
    if not appname:
        raise ValueError('ReliefWeb needs an approved RELIEFWEB_APPNAME environment setting.')
    count = max(1, min(int(k), 15))
    clean_query = re.sub(r"['’]s\b", "", query or "")
    ignored = _STOP | _PEACE_WORDS | {'recent', 'latest', 'today', 'news', 'current',
                                    'role', 'play', 'played', 'examples', 'example', 'successful', 'success'}
    words = [w for w in re.findall(r"[\w]+", clean_query, flags=re.UNICODE)
             if len(w) > 2 and w.lower() not in ignored][:4]
    terms = ' AND '.join('"%s"' % w for w in words)
    search = ('(%s) AND %s' % (terms, _RELIEFWEB_TERMS)) if terms else _RELIEFWEB_TERMS
    params = {
        'appname': appname, 'limit': count, 'query[value]': search,
        'fields[include][]': ['title', 'body', 'url_alias', 'date.original', 'source.name'],
    }
    if re.search(r'\b(recent|latest|today|news|current)\b', query or '', re.I):
        params['sort[]'] = 'date:desc'
    url = _RELIEFWEB_HOST + '?' + urllib.parse.urlencode(params, doseq=True)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=25) as reply:
            raw = reply.read(4_000_001)
        if len(raw) > 4_000_000:
            raise ValueError('response too large')
        payload = json.loads(raw)
    except Exception as exc:
        raise ValueError('ReliefWeb reports could not be retrieved (%s).' % type(exc).__name__) from None
    if not isinstance(payload, dict) or payload.get('error'):
        raise ValueError('ReliefWeb returned an invalid reports response.')
    out, seen = [], set()
    for item in payload.get('data') or []:
        if not isinstance(item, dict):
            continue
        f = item.get('fields') or {}
        if not isinstance(f, dict):
            continue
        title = re.sub(r'\s+', ' ', str(f.get('title') or '')).strip()
        link = str(f.get('url_alias') or '').strip()
        body = str(f.get('body') or '').strip()
        parsed = urllib.parse.urlparse(link)
        if not title or not body or parsed.scheme != 'https' or parsed.hostname != 'reliefweb.int' or link in seen:
            continue
        seen.add(link)
        date = str((f.get('date') or {}).get('original') or '')[:10]
        sources = ', '.join(str(v.get('name')) for v in f.get('source', []) if isinstance(v, dict) and v.get('name'))
        text = 'Humanitarian report on ReliefWeb.\nTitle: %s\nSource: %s\nPublished: %s\n\n%s' % (title, sources or 'unspecified', date or 'undated', body[:12000])
        out.append({'id': link, 'title': title, 'text': text, 'url': link,
                    'year': date[:4] if date[:4].isdigit() else '',
                    'venue': 'ReliefWeb (%s)' % (sources or 'humanitarian reports'),
                    'source': 'reliefweb', 'score': 1.0 / (len(out) + 1)})
    return out[:count]


_SFCG_HOST = 'https://www.sfcg.org/wp-json/wp/v2'

def _strip_html(raw):
    text = re.sub(r'(?s)<(script|style).*?</\1>', ' ', raw or '')
    text = re.sub(r'<[^>]+>', ' ', text)
    import html as _html
    return re.sub(r'\s+', ' ', _html.unescape(text)).strip()

def _sfcg_fetch(kind, keywords, per_page):
    params = {'search': keywords, 'per_page': per_page,
              '_fields': 'date,link,title,content'}
    url = '%s/%s?%s' % (_SFCG_HOST, kind, urllib.parse.urlencode(params, doseq=True))
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=25) as reply:
            raw = reply.read(4_000_001)
        if len(raw) > 4_000_000:
            raise ValueError('response too large')
        payload = json.loads(raw)
    except Exception as exc:
        raise ValueError('Search for Common Ground publications could not be retrieved (%s).' % type(exc).__name__) from None
    if not isinstance(payload, list):
        raise ValueError('Search for Common Ground returned an invalid publications response.')
    return payload

def sfcg(query, k=12):
    """Search for Common Ground publications and pages via its public WordPress API.

    Keyless. Covers SFCG case studies, evaluations and program/country pages.
    """
    count = max(1, min(int(k), 15))
    clean_query = re.sub(r"['’]s\b", "", query or "")
    ignored = _STOP | _PEACE_WORDS | {'recent', 'latest', 'today', 'news', 'current',
                                    'role', 'play', 'played', 'examples', 'example', 'successful', 'success',
                                    'work', 'worked', 'help', 'helped', 'change', 'changes', 'countries'}
    words = [w for w in re.findall(r"[\w]+", clean_query, flags=re.UNICODE)
             if len(w) > 2 and w.lower() not in ignored][:4]
    # WordPress ANDs search terms, so relax the query until a level has
    # enough matches; keep the most specific level that reaches 3 results,
    # otherwise the level that matched the most.
    candidates = [' '.join(words[:n]) for n in range(min(len(words), 4), 0, -1)] or ['peacebuilding']
    posts, pages = [], []
    best = ([], [])
    for trial in candidates:
        p_posts = _sfcg_fetch('posts', trial, count)
        p_pages = _sfcg_fetch('pages', trial, count)
        if len(p_posts) + len(p_pages) > len(best[0]) + len(best[1]):
            best = (p_posts, p_pages)
        if len(p_posts) + len(p_pages) >= 3:
            posts, pages = p_posts, p_pages
            break
    if not posts and not pages:
        posts, pages = best
    out, seen = [], set()
    pools = [(p, 'publication') for p in posts] + [(p, 'page') for p in pages]
    for item, kind in pools:
        if not isinstance(item, dict):
            continue
        title = _strip_html(str((item.get('title') or {}).get('rendered') or ''))
        link = str(item.get('link') or '').strip()
        body = _strip_html(str((item.get('content') or {}).get('rendered') or ''))
        parsed = urllib.parse.urlparse(link)
        junk = ('terms & conditions', 'terms and conditions', 'privacy policy', 'cookie', 'careers', 'vacanc')
        if not title or not body or parsed.scheme != 'https' or not (parsed.hostname or '').endswith('sfcg.org') or link in seen:
            continue
        if any(j in title.lower() for j in junk):
            continue
        seen.add(link)
        date = str(item.get('date') or '')[:10]
        text = ('Search for Common Ground %s.\nTitle: %s\nPublished: %s\n\n%s'
                % (kind, title, date or 'undated', body[:6000]))
        out.append({'id': link, 'title': title, 'text': text, 'url': link,
                    'year': date[:4] if date[:4].isdigit() else '',
                    'venue': 'Search for Common Ground (sfcg.org %s)' % kind,
                    'source': 'sfcg', 'score': 1.0 / (len(out) + 1)})
    return out[:count]
