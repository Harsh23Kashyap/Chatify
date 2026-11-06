"""Live weather evidence from Open-Meteo for WeatherChat.

Open-Meteo free API: no key, non-commercial use only, up to 10,000 calls/day
(5,000/hour, 600/minute). Data is licenced CC BY 4.0, so attribution is required:
it ships in every answer's source list, the app footer and the README.
Location names resolve through Open-Meteo's geocoding (GeoNames data).
Terms: https://open-meteo.com/en/terms  Licence: https://open-meteo.com/en/license
"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from chatify.connectors.open_sources import SetupRequired


class WeatherSourceError(SetupRequired, ValueError):
    """Public-safe failure with fixed service/stage/category; no response content."""


GEOCODE_URL = 'https://geocoding-api.open-meteo.com/v1/search'
FORECAST_URL = 'https://api.open-meteo.com/v1/forecast'
USER_AGENT = 'WeatherChat-Chatify/1.0 (+https://github.com/Harsh23Kashyap/Chatify)'
ATTRIBUTION = ('Weather data by Open-Meteo.com (CC BY 4.0, free non-commercial tier). '
               'Location data by GeoNames via Open-Meteo.')

WMO = {0: 'clear sky', 1: 'mainly clear', 2: 'partly cloudy', 3: 'overcast',
       45: 'fog', 48: 'depositing rime fog',
       51: 'light drizzle', 53: 'drizzle', 55: 'dense drizzle',
       56: 'light freezing drizzle', 57: 'dense freezing drizzle',
       61: 'light rain', 63: 'moderate rain', 65: 'heavy rain',
       66: 'light freezing rain', 67: 'heavy freezing rain',
       71: 'light snow', 73: 'moderate snow', 75: 'heavy snow', 77: 'snow grains',
       80: 'light rain showers', 81: 'rain showers', 82: 'violent rain showers',
       85: 'light snow showers', 86: 'heavy snow showers',
       95: 'thunderstorm', 96: 'thunderstorm with light hail', 99: 'thunderstorm with hail'}

# Words that are never part of a place name on their own.
_GENERIC = {'what', 'whats', 'is', 'the', 'how', 'hows', 'does', 'do', 'will', 'it', 'be',
            'there', 'like', 'tell', 'me', 'please', 'show', 'give', 'current', 'currently',
            'today', 'tonight', 'tomorrow', 'now', 'right', 'this', 'next', 'week', 'weekend',
            'morning', 'afternoon', 'evening', 'night', 'day', 'daily', 'hourly', 'weather',
            'forecast', 'rain', 'raining', 'rainy', 'snow', 'temperature', 'temp', 'hot',
            'cold', 'warm', 'humid', 'humidity', 'wind', 'windy', 'sunny', 'cloudy',
            'monsoon', 'outside', 'local', 'area', 'here', 'nearby', 'location', 'compare', 'compares', 'compared', 'comparison', 'comparing', 'between', 'difference', 'differences', 'differ', 'versus', 'vs', 'better', 'worse', 'which', 'a', 'an', 'and', 'or', 'of', 'in', 'at', 'for', 'near',
            'around', 'to', 'on', 'any', 'much', 'many', 'going', 'get', 'check'}


def _get(url, params):
    stage = 'geocoding' if url == GEOCODE_URL else 'forecast'
    full = url + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=20) as reply:
            raw = reply.read(4_000_001).decode('utf-8')
    except urllib.error.HTTPError as e:
        raise WeatherSourceError('Open-Meteo ' + stage + ' lookup failed [weather:' + stage + ':http:' + str(int(e.code)) + '].') from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise WeatherSourceError('Open-Meteo ' + stage + ' service is unreachable [weather:' + stage + ':network].') from None
    try:
        return full, json.loads(raw)
    except ValueError:
        raise WeatherSourceError('Open-Meteo ' + stage + ' returned an unreadable response [weather:' + stage + ':json].') from None


def _candidates(query):
    """Possible place names from a question, longest first. Never a location we made up."""
    q = re.sub(r'[?!.,;:"]+', ' ', query or '')
    found = []
    for m in re.finditer(r"\b(?:in|at|for|near|around|between)\s+([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,3})", q, re.I):
        found.append(m.group(1))
    m = re.match(r"^\s*([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,3}?)\s+(?:weather|forecast|rain|temperature)\b", q, re.I)
    if m:
        found.append(m.group(1))
    cleaned = []
    for cand in found:
        words = cand.split()
        while words and words[-1].lower().strip(".'-") in _GENERIC:
            words.pop()
        while words and words[0].lower().strip(".'-") in {'the', 'a', 'an'}:
            words.pop(0)
        if words and any(w.lower().strip(".'-") not in _GENERIC for w in words):
            cleaned.append(' '.join(words))
    seen, ordered = set(), []
    for c in sorted(cleaned, key=len, reverse=True):
        if c.lower() not in seen:
            seen.add(c.lower())
            ordered.append(c)
    return ordered


# Well-known city renames the geocoder does not resolve on its own. The literal
# query is always tried first; aliases only fire when the literal match is weak.
_ALIASES = {
    'bangalore': ['bengaluru'], 'bombay': ['mumbai'], 'madras': ['chennai'],
    'calcutta': ['kolkata'], 'poona': ['pune'], 'mysore': ['mysuru'],
    'trivandrum': ['thiruvananthapuram'], 'cochin': ['kochi'],
    'pondicherry': ['puducherry'], 'benares': ['varanasi'],
    'allahabad': ['prayagraj'], 'gurgaon': ['gurugram'],
}


def _score(result, query):
    name = str(result.get('name') or '').strip().lower()
    q = (query or '').strip().lower()
    score = float(result.get('population') or 0)
    if name == q:
        score += 1e12
    elif name.startswith(q) or q.startswith(name):
        score += 1e6
    fc = str(result.get('feature_code') or '')
    if fc == 'PPLC':
        score += 1e6
    elif fc.startswith('PPLA'):
        score += 5e5
    return score


def _strong(result, query):
    pop = float(result.get('population') or 0)
    fc = str(result.get('feature_code') or '')
    return pop >= 100000 or fc == 'PPLC' or fc.startswith('PPLA')


def _resolve(candidate):
    """Best place for a candidate name: literal query first, rename aliases only
    while matches stay weak. Returns (place, alternates, ambiguous) or None."""
    best = None
    for i, name in enumerate([candidate] + _ALIASES.get(candidate.lower(), [])):
        results = _geocode(name)
        if not results:
            continue
        top = max(results, key=lambda r: _score(r, name))
        score = _score(top, name) - (0.5 if i == 0 else 0)
        if best is None or score > best[0]:
            best = (score, top, results, name)
        if _strong(top, name):
            break
    if best is None:
        return None
    place, results = best[1], best[2]
    key = (round(float(place['latitude']), 2), round(float(place['longitude']), 2))
    alternates = [r for r in results
                  if (round(float(r['latitude']), 2), round(float(r['longitude']), 2)) != key]
    strongs = [r for r in results if _strong(r, best[3])]
    ambiguous = False
    if len(strongs) >= 2:
        pops = sorted((float(r.get('population') or 0) for r in strongs), reverse=True)
        ambiguous = pops[0] < 10 * pops[1]
    return place, alternates, ambiguous


def _geocode(name):
    _, payload = _get(GEOCODE_URL, {'name': name, 'count': 5, 'language': 'en', 'format': 'json'})
    results = payload.get('results')
    return results if isinstance(results, list) else []


def _compass(deg):
    try:
        d = float(deg)
    except (TypeError, ValueError):
        return ''
    return ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][int((d % 360) / 22.5 + 0.5) % 16]


def _label(place):
    return ', '.join(str(x) for x in (place.get('name'), place.get('admin1'), place.get('country')) if x)


def _humidity_word(rh):
    try:
        rh = float(rh)
    except (TypeError, ValueError):
        return 'humidity not reported'
    if rh < 30:
        return 'dry'
    if rh < 60:
        return 'a little humid'
    if rh < 80:
        return 'humid'
    return 'very humid'


def _wind_word(ws):
    try:
        ws = float(ws)
    except (TypeError, ValueError):
        return 'wind not reported'
    if ws < 5:
        return 'calm'
    if ws < 15:
        return 'a light wind'
    if ws < 30:
        return 'breezy'
    if ws < 50:
        return 'windy'
    return 'very windy'


def _feel_word(t):
    try:
        t = float(t)
    except (TypeError, ValueError):
        return 'temperature not reported'
    if t < 5:
        return 'very cold'
    if t < 12:
        return 'cold'
    if t < 20:
        return 'cool'
    if t < 27:
        return 'warm'
    if t < 33:
        return 'hot'
    return 'very hot'


def _day_line(daily, i):
    code = (daily.get('weather_code') or [None] * 7)[i]
    tmax = (daily.get('temperature_2m_max') or [None] * 7)[i]
    tmin = (daily.get('temperature_2m_min') or [None] * 7)[i]
    pprob = (daily.get('precipitation_probability_max') or [None] * 7)[i]
    psum = (daily.get('precipitation_sum') or [None] * 7)[i]
    wind = (daily.get('wind_speed_10m_max') or [None] * 7)[i]
    return ('%s: %s, high %s C, low %s C, rain chance %s%%, rain total %s mm, max wind %s km/h'
            % ((daily.get('time') or ['?'] * 7)[i], WMO.get(code, 'conditions unknown'),
               tmax, tmin, pprob, psum, wind))


def _slug(text):
    return re.sub(r'[^a-z0-9]+', '-', str(text).lower()).strip('-') or 'place'


def _clarification(queried, candidates):
    """Deterministic disambiguation: a balanced place-name match returns the
    candidate list and NO weather, so nothing silently answers for one pick."""
    labels = [_label(c) for c in candidates[:4] if _label(c)]
    example = labels[1] if len(labels) > 1 else labels[0]
    url = GEOCODE_URL + '?name=' + urllib.parse.quote_plus(queried) + '#disambiguation'
    text = ('The question named "%s", which matches several places, so no weather data '
            'was fetched for any of them. Candidates: %s. Ask again with a more specific '
            'place, for example "weather in %s".'
            % (queried, '; '.join(labels), example))
    return {'id': 'open-meteo-clarify-' + _slug(queried), 'title': 'Which place did you mean? - ' + queried,
            'text': text, 'url': url,
            'year': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'venue': 'GeoNames via Open-Meteo', 'source': 'open-meteo-weather'}


def _evidence(place, alternates, queried=''):
    label = _label(place)
    matched = ''
    if queried and str(place.get('name') or '').strip().lower() != queried.strip().lower():
        matched = ' The question named "%s"; this resolves to %s.' % (queried, label)
    params = {
        'latitude': place['latitude'], 'longitude': place['longitude'], 'timezone': 'auto',
        'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m,wind_direction_10m',
        'hourly': 'temperature_2m,precipitation_probability,weather_code',
        'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,sunrise,sunset,uv_index_max,wind_speed_10m_max',
        'forecast_days': 7,
        'temperature_unit': 'celsius', 'wind_speed_unit': 'kmh', 'precipitation_unit': 'mm',
    }
    full_url, payload = _get(FORECAST_URL, params)
    tz = payload.get('timezone') or 'local time'
    now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    current = payload.get('current') or {}
    hourly = payload.get('hourly') or {}
    daily = payload.get('daily') or {}
    alt = ''
    if alternates:
        names = '; '.join(_label(a) for a in alternates[:3] if _label(a))
        if names:
            alt = (' Other places with a matching name, if this is the wrong one: '
                   + names + '. Ask again with a more specific place to switch.')
    note = ''
    if matched or alt:
        note = ' Place note:' + matched + alt
    meta = note + ' Retrieved: %s. All times below are %s. %s' % (now_utc, tz, ATTRIBUTION)
    head = 'This weather data is for %s.%s\n' % (label, note if note else '')

    minutes = int((current.get('interval') or 900) / 60)
    cur_head = ('Live conditions for %s, valid at %s (%s). These are model data from'
                ' weather models, not a station observation:\n'
                '- Condition: %s%s\n- Temperature: %s C (feels like %s C)\n'
                '- Humidity: %s%%\n- Wind: %s km/h from %s\n- Precipitation in the %s minutes up to that time: %s mm'
                % (label, current.get('time'), tz, WMO.get(current.get('weather_code'), 'not reported'),
                   ' (daytime)' if current.get('is_day') == 1 else ' (night-time)' if current.get('is_day') == 0 else '',
                   current.get('temperature_2m'), current.get('apparent_temperature'),
                   current.get('relative_humidity_2m'), current.get('wind_speed_10m'),
                   _compass(current.get('wind_direction_10m')), minutes, current.get('precipitation')))
    plain = ('In plain terms: it feels %s at %s C, the air is %s at %s%% relative humidity, '
             'the wind is %s at %s km/h, and skies are %s with %s mm of precipitation in the past %s minutes.'
             % (_feel_word(current.get('apparent_temperature')), current.get('apparent_temperature'),
                _humidity_word(current.get('relative_humidity_2m')), current.get('relative_humidity_2m'),
                _wind_word(current.get('wind_speed_10m')), current.get('wind_speed_10m'),
                WMO.get(current.get('weather_code'), 'not reported'), current.get('precipitation'), minutes))
    cur_text = (head + cur_head + '\n' + plain + '\n'
                'Units are degrees Celsius, percent, millimetres and kilometres per hour.'
                + meta)

    times = hourly.get('time') or []
    cur_hour = str(current.get('time') or '')[:13]
    start = next((i for i, t in enumerate(times) if str(t)[:13] >= cur_hour), 0)
    hours = []
    for i in range(start, min(start + 12, len(times))):
        hours.append('%s: %s C, rain %s%%, %s'
                     % (str(times[i])[11:16], (hourly.get('temperature_2m') or [])[i],
                        (hourly.get('precipitation_probability') or [None] * len(times))[i],
                        WMO.get((hourly.get('weather_code') or [None] * len(times))[i], '')))
    today_text = (head + 'Today in %s (%s):\n%s\nNext hours, local time: %s.%s'
                  % (label, tz, _day_line(daily, 0),
                     '; '.join(hours) if hours else 'not available',
                     ' Sunrise %s, sunset %s, max UV index %s.'
                     % (str((daily.get('sunrise') or ['?'])[0])[11:16],
                        str((daily.get('sunset') or ['?'])[0])[11:16],
                        (daily.get('uv_index_max') or ['?'])[0]) + meta))

    tomorrow_text = (head + 'Tomorrow in %s (%s):\n%s.%s' % (label, tz, _day_line(daily, 1), meta))

    days = ['Weather for the week ahead in %s (%s), 7 days, one line per day:' % (label, tz)]
    for i in range(min(7, len(daily.get('time') or []))):
        days.append(_day_line(daily, i))
    week_text = head + '\n'.join(days) + '.' + meta

    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    venue = 'Open-Meteo (CC BY 4.0)'
    slug = _slug(label)
    return [
        {'id': 'open-meteo-current-' + slug, 'title': 'Current weather - ' + label, 'text': cur_text,
         'url': full_url + '#current-conditions', 'year': stamp, 'venue': venue, 'source': 'open-meteo-weather'},
        {'id': 'open-meteo-today-' + slug, 'title': 'Today and next hours - ' + label, 'text': today_text,
         'url': full_url + '#today', 'year': stamp, 'venue': venue, 'source': 'open-meteo-weather'},
        {'id': 'open-meteo-tomorrow-' + slug, 'title': 'Tomorrow - ' + label, 'text': tomorrow_text,
         'url': full_url + '#tomorrow', 'year': stamp, 'venue': venue, 'source': 'open-meteo-weather'},
        {'id': 'open-meteo-week-' + slug, 'title': '7-day forecast - ' + label, 'text': week_text,
         'url': full_url + '#7-day-forecast', 'year': stamp, 'venue': venue, 'source': 'open-meteo-weather'},
    ]


def open_meteo(query, k=6):
    """Chatify python-source entry: question -> weather evidence for the place it names.

    Returns [] when the question names no resolvable place; the app then shows its
    no_evidence guidance instead of guessing a location.
    """
    places = []
    clarifies = []
    seen = set()

    def add(resolved, form):
        if not resolved:
            return False
        place, alternates, ambiguous = resolved
        if ambiguous:
            clarifies.append((form, [place] + alternates))
            return True
        key = (round(float(place['latitude']), 2), round(float(place['longitude']), 2))
        if key in seen:
            return True
        seen.add(key)
        places.append((place, alternates, form))
        return True

    for cand in _candidates(query):
        if add(_resolve(cand), cand):
            pass  # whole phrase resolved - keeps "Trinidad and Tobago" together
        else:
            parts = []
            for sep in (' and ', ' or ', ' vs ', ' versus '):
                if sep in cand.lower():
                    parts = [p.strip() for p in re.split(re.escape(sep), cand, flags=re.I) if p.strip()]
                    break
            ok = False
            if len(parts) > 1 and all(any(w.lower().strip(".'-") not in _GENERIC for w in p.split()) for p in parts):
                for part in parts:
                    ok = add(_resolve(part), part) or ok
            if not ok:
                words = cand.split()
                for n in range(len(words) - 1, 0, -1):
                    if add(_resolve(' '.join(words[:n])), ' '.join(words[:n])):
                        break
        if len(places) >= 2:
            break
    out = []
    for form, candidates in clarifies:
        out.append(_clarification(form, candidates))
    for place, alternates, form in places:
        out.extend(_evidence(place, alternates, queried=form))
    return out
