"""Key-free food evidence adapters for RecipeChat.

TheMealDB (www.themealdb.com): full recipes - ingredients, measures, method,
cuisine and category. Free v1 API, no key.
Open Food Facts (world.openfoodfacts.org): packaged-food nutrition per 100g
from the crowdsourced product database. Free, no key, polite UA required.
Both return plain evidence dicts; untrusted source text is passed through as
data only.
"""
import json, math, re, unicodedata, urllib.parse, urllib.request, urllib.error

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
    q = _keywords(query)
    # Meal names are substring queries, not natural-language search. Keep taste
    # questions tied to the named dish; dietary constraints remain in the query.
    q = re.sub(r'\btaste like(?: it)?$', '', q, flags=re.I).strip()
    q = re.sub(r'\bclassic\b', '', q, flags=re.I)
    q = re.sub(r'\s+', ' ', q).strip()
    if not q:
        return []
    out = []
    count = max(1, min(int(k), 10))
    # Name search first, then ingredient filter and bounded name-token searches.
    urls = [
        'https://www.themealdb.com/api/json/v1/1/search.php?' + urllib.parse.urlencode({'s': q}),
        'https://www.themealdb.com/api/json/v1/1/filter.php?' + urllib.parse.urlencode({'i': q}),
    ]
    # A name such as margherita pizza can be stored as Pizza Express Margherita.
    # Try at most three name tokens, but require every requested name token in
    # the returned title so a broad pizza match cannot silently replace the dish.
    name_terms = re.findall(r"[\w'-]+", q.lower())
    if len(name_terms) > 1:
        for term in sorted(set(name_terms), key=lambda w: (-len(w), w))[:3]:
            urls.append('https://www.themealdb.com/api/json/v1/1/search.php?' + urllib.parse.urlencode({'s': term}))
    seen = set()
    for request_index, url in enumerate(urls):
        payload = _get(url)
        meals = payload.get('meals') or []
        for m in meals[:50]:
            if not isinstance(m, dict):
                continue
            name = str(m.get('strMeal') or '').strip()
            mid = str(m.get('idMeal') or name)
            if request_index >= 2:
                title_terms = set(re.findall(r"[\w'-]+", name.lower()))
                if not all(term in title_terms for term in name_terms):
                    continue
            if not name or mid in seen:
                continue
            seen.add(mid)
            if 'strInstructions' not in m:  # filter.php returns stubs; look up the full meal
                full = _get('https://www.themealdb.com/api/json/v1/1/lookup.php?' + urllib.parse.urlencode({'i': mid}))
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
            if len(out) >= count:
                break
        if out:
            break
    return out[:count]

def _NUM(value):
    return round(value, 1) if type(value) in (int, float) and math.isfinite(value) and value >= 0 else None

def _nutrition_issue(n):
    if not isinstance(n, dict):
        return ''
    for key in ('energy-kcal_100g', 'fat_100g', 'saturated-fat_100g', 'carbohydrates_100g', 'sugars_100g', 'fiber_100g', 'proteins_100g', 'salt_100g'):
        value = n.get(key)
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0 or key != 'energy-kcal_100g' and value > 100):
            return 'Invalid per-100g nutrient value'
    for part, total in [('saturated-fat_100g', 'fat_100g'), ('sugars_100g', 'carbohydrates_100g')]:
        if type(n.get(part)) in (int, float) and type(n.get(total)) in (int, float) and n[part] > n[total]:
            return 'Nutrient component exceeds its total'
    return ''

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
    # A two-food comparison is two searches, not one impossible product name.
    # Only expand this explicit syntax; do not discard free-form constraints.
    comparison_query = (query or '').rstrip()
    while comparison_query and (comparison_query[-1] in '?？ \ufe0f' or unicodedata.category(comparison_query[-1]) == 'So'):
        comparison_query = comparison_query[:-1].rstrip()
    comparison = re.fullmatch(r"\s*how does (?:the )?nutrition of (.+?) compare to (.+?)\s*", comparison_query, re.I)
    if comparison:
        foods = [x.rstrip(' ?？').strip() for x in comparison.groups()]
        if any(re.search(r'\b(?:compare to|nutrition of)\b', food, re.I) for food in foods):
            return []  # Ambiguous nested comparison is not a two-food query.
        if all(foods) and all(len(x) <= 80 for x in foods):
            count = max(1, min(int(k), 8))
            if count < 2:
                return []  # One result cannot cover both requested foods.
            per_food = count // 2
            groups = [[row for row in offfoods(food, per_food) if 'Nutrition per 100g:' in row['text']] for food in foods]
            if not all(groups):
                return []  # Do not present one food as a complete comparison.
            return [{**row, 'text': 'Requested comparison food: ' + food + '\nProduct-specific example, not a typical value for this food.\n' + row['text']}
                    for food, group in zip(foods, groups) for row in group]
    q = _keywords(query)
    if not q:
        return []
    count = max(1, min(int(k), 8))
    url = ('https://world.openfoodfacts.org/cgi/search.pl?search_simple=1&action=process&json=1&'
           + urllib.parse.urlencode({'search_terms': q, 'page_size': count,
                                     'fields': 'product_name,brands,nutriments,nutrition_grades,ingredients_text,url'}))
    payload = _get(url)
    products = payload.get('products') or []
    out = []
    for p in products[:count]:
        if not isinstance(p, dict):
            continue
        name = str(p.get('product_name') or '').strip()
        if not name:
            continue
        nutrients = p.get('nutriments')
        # Do not turn visibly contradictory crowdsourced numbers into comparison
        # evidence or silently replace them with inferred values.
        if _nutrition_issue(nutrients):
            continue
        line = _nutri_line(nutrients)
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

# Nutrition comparisons and food constraints must not be replaced by a generic
# query ladder. Other recipe and public-search sources keep their own queries.
offfoods.preserve_query = True
