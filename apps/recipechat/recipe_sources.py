"""Food evidence adapters for RecipeChat.

TheMealDB (www.themealdb.com): full recipes - ingredients, measures, method,
cuisine and category. Production key required; explicit educational demo opt-in.
Open Food Facts (world.openfoodfacts.org): packaged-food nutrition per 100g
from the crowdsourced product database. Free, no key, polite UA required.
Both return plain evidence dicts; untrusted source text is passed through as
data only.
"""
import json, os, re, threading, time, urllib.parse, urllib.request, urllib.error
from collections import OrderedDict

_OFF_LOCK = threading.Lock()
_OFF_LAST = 0.0
_OFF_CACHE = OrderedDict()

_UA = {'User-Agent': 'Chatify-RecipeChat/1.0 (+https://github.com/Harsh23Kashyap/Chatify)', 'Accept': 'application/json'}
_STOP = {'what','whats','is','are','the','a','an','of','for','how','do','does','can','i','me','my','tell','show','give','make','recipe','recipes','about','in','to','and','with','good','best','some','please'}

def _keywords(q):
    words = re.findall(r"[\w'-]+", q or '', flags=re.UNICODE)
    keep = [w for w in words if w.lower() not in _STOP and len(w) > 1]
    return ' '.join(keep)[:150]

def _get(url, cap=2_000_001):
    req = urllib.request.Request(url, headers=_UA)
    try:
        with urllib.request.urlopen(req, timeout=20) as reply:
            return json.loads(reply.read(cap).decode('utf-8', 'replace'))
    except urllib.error.HTTPError as e:
        raise ValueError('Food API HTTP %s; try again shortly.' % e.code) from None
    except Exception:
        raise ValueError('Food API unreachable; try again shortly.') from None

def _meal_text(m):
    parts = []
    cat = str(m.get('strCategory') or '').strip()
    area = str(m.get('strArea') or '').strip()
    tags = str(m.get('strTags') or '').strip()
    if cat or area:
        parts.append('Dish: %s%s' % (cat, (' (%s cuisine)' % area) if area else ''))
    if tags:
        parts.append('Tags: %s' % tags.replace(',', ', '))
    ings = []
    for i in range(1, 21):
        ing = str(m.get('strIngredient%d' % i) or '').strip()
        meas = str(m.get('strMeasure%d' % i) or '').strip()
        if ing:
            ings.append(('%s %s' % (meas, ing)).strip())
    if ings:
        parts.append('Ingredients:\n- ' + '\n- '.join(ings))
    instr = re.sub(r'\s+', ' ', str(m.get('strInstructions') or '')).strip()
    if instr:
        parts.append('Method: ' + instr[:3500])
    return '\n'.join(parts)

def mealdb(query, k=6):
    key = os.environ.get('THEMEALDB_API_KEY', '').strip()
    if not key and os.environ.get('CHATIFY_MEALDB_EDUCATIONAL_DEMO') == '1':key = '1'
    if not key or key == '1' and os.environ.get('CHATIFY_MEALDB_EDUCATIONAL_DEMO') != '1':
        raise ValueError('TheMealDB production access is not configured. Add an authorized production key, or use explicit educational demo mode locally.')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,120}',key):raise ValueError('Invalid TheMealDB key format.')
    base = 'https://www.themealdb.com/api/json/v1/' + key + '/'
    q = _keywords(query)
    if not q or int(k) <= 0:
        return []
    out = []
    count = max(1, min(int(k), 10))
    # Name search first; fall back to first-letter and main-ingredient filter.
    urls = [
        base + 'search.php?' + urllib.parse.urlencode({'s': q}),
        base + 'filter.php?' + urllib.parse.urlencode({'i': q}),
    ]
    seen = set()
    for url in urls:
        payload = _get(url)
        meals = payload.get('meals') or []
        for m in meals[:count]:
            if not isinstance(m, dict):
                continue
            name = str(m.get('strMeal') or '').strip()
            mid = str(m.get('idMeal') or name)
            if not name or mid in seen:
                continue
            seen.add(mid)
            if 'strInstructions' not in m:  # filter.php returns stubs; look up the full meal
                full = _get(base + 'lookup.php?' + urllib.parse.urlencode({'i': mid}))
                fm = (full.get('meals') or [None])[0]
                if isinstance(fm, dict):
                    m = fm
            text = _meal_text(m)
            if not text:
                continue
            out.append({'id': mid, 'title': name, 'text': text,
                        'url': 'https://www.themealdb.com/meal/' + mid,
                        'year': '', 'venue': 'TheMealDB community recipe database',
                        'source': 'themealdb', 'score': 1.0 / (len(out) + 1)})
        if out:
            break
    return out[:count]

_NUM = lambda v: round(v, 1) if isinstance(v, (int, float)) else None

def _nutri_line(n):
    if not isinstance(n, dict):
        return ''
    keys = [('energy-kcal_100g', 'Energy', 'kcal'), ('fat_100g', 'Fat', 'g'),
            ('saturated-fat_100g', 'Saturated fat', 'g'), ('carbohydrates_100g', 'Carbs', 'g'),
            ('sugars_100g', 'Sugars', 'g'), ('fiber_100g', 'Fiber', 'g'),
            ('proteins_100g', 'Protein', 'g'), ('salt_100g', 'Salt', 'g')]
    row = []
    for key, label, unit in keys:
        v = _NUM(n.get(key))
        if v is not None:
            row.append('%s %s%s' % (label, v, unit))
    return '; '.join(row)

def offfoods(query, k=6):
    q = _keywords(query)
    if not q:
        return []
    count = max(1, min(int(k), 8))
    url = ('https://world.openfoodfacts.org/cgi/search.pl?search_simple=1&action=process&json=1&'
           + urllib.parse.urlencode({'search_terms': q, 'page_size': count,
                                     'fields': 'product_name,brands,nutriments,nutrition_grades,ingredients_text,url'}))
    # One process-wide request per 6.1s stays below OFF's 10 search/minute/IP
    # limit for this process. Other processes sharing the IP still need coordination.
    global _OFF_LAST
    with _OFF_LOCK:
        cached = _OFF_CACHE.get(url)
        if cached and time.monotonic() - cached[0] < 600:
            payload = cached[1]
        else:
            delay = 6.1 - (time.monotonic() - _OFF_LAST)
            if delay > 0:time.sleep(delay)
            _OFF_LAST = time.monotonic()
            payload = _get(url)
            _OFF_CACHE[url] = (time.monotonic(),payload)
            _OFF_CACHE.move_to_end(url)
            while len(_OFF_CACHE)>64:_OFF_CACHE.popitem(last=False)
    products = payload.get('products') or []
    out = []
    for p in products[:count]:
        if not isinstance(p, dict):
            continue
        name = str(p.get('product_name') or '').strip()
        if not name:
            continue
        line = _nutri_line(p.get('nutriments'))
        grade = str(p.get('nutrition_grades') or '').strip().upper()
        brands = str(p.get('brands') or '').strip()
        ings = re.sub(r'\s+', ' ', str(p.get('ingredients_text') or '')).strip()
        parts = []
        if brands:
            parts.append('Brands: ' + brands)
        if grade and grade != 'UNKNOWN':
            parts.append('Nutri-Score: ' + grade)
        if line:
            parts.append('Nutrition per 100g: ' + line)
        if ings:
            parts.append('Listed ingredients: ' + ings[:1200])
        if not parts:
            continue
        out.append({'id': str(p.get('url') or name), 'title': name,
                    'text': 'Packaged-food data point (per 100g, crowdsourced - check the label you buy).\n' + '\n'.join(parts),
                    'url': str(p.get('url') or ''), 'year': '',
                    'venue': 'Open Food Facts (crowdsourced product data)',
                    'source': 'openfoodfacts', 'score': 1.0 / (len(out) + 1)})
    return out
