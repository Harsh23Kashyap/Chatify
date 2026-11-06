"""WeatherAPI adapter using only current and 3-day Free-plan features.

Only current and <=3 daily forecast days. No fallback, retry, top-up or upgrade.
API keys exist only in server environment and outbound requests, never evidence.
Field semantics: https://www.weatherapi.com/docs/realtime-api/
https://www.weatherapi.com/docs/forecast-api/
https://www.weatherapi.com/docs/location-object/
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from weather_sources import _candidates, _slug, WeatherSourceError

BASE = 'https://api.weatherapi.com/v1/'
ATTRIBUTION = 'Weather data by WeatherAPI.com (https://www.weatherapi.com/).'
CURRENT_FIELDS = {'temp_c': ('Temperature', 'C'), 'feelslike_c': ('Feels-like temperature', 'C'),
                  'humidity': ('Relative humidity', '%'), 'wind_kph': ('Wind speed', 'km/h')}
DAILY_FIELDS = {'maxtemp_c': ('High temperature', 'C'), 'mintemp_c': ('Low temperature', 'C'),
                'daily_chance_of_rain': ('Rain chance', '%'),
                'totalprecip_mm': ('Precipitation total', 'mm'), 'maxwind_kph': ('Maximum wind speed', 'km/h')}


def _request(endpoint, params):
    key = os.environ.get('WEATHERAPI_API_KEY', '').strip()
    if not key:
        raise WeatherSourceError('WeatherAPI key is missing [weather:setup:key].')
    url = BASE + endpoint + '?' + urllib.parse.urlencode(dict(params, key=key))
    req = urllib.request.Request(url, headers={'User-Agent': 'WeatherChat-Chatify/1.0', 'Accept': 'application/json'})
    stage = 'geocoding' if endpoint == 'search.json' else 'forecast'
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read(4_000_001)
        if len(raw) > 4_000_000:
            raise ValueError('oversize')
        payload = json.loads(raw)
    except urllib.error.HTTPError as exc:
        raise WeatherSourceError('WeatherAPI lookup failed [weather:%s:http:%s].' % (stage, int(exc.code))) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise WeatherSourceError('WeatherAPI unreachable [weather:%s:network].' % stage) from None
    except (ValueError, UnicodeError):
        raise WeatherSourceError('WeatherAPI unreadable response [weather:%s:json].' % stage) from None
    if isinstance(payload, dict) and 'error' in payload:
        raise WeatherSourceError('WeatherAPI returned an API error [weather:%s:api].' % stage)
    return payload


def _label(place):
    return ', '.join(str(place[x]) for x in ('name', 'region', 'country') if place.get(x))


def _clarify(candidate, matches):
    labels = [_label(p) for p in matches[:5]]
    return {'id': 'weatherapi-clarify-' + _slug(candidate), 'source': 'weatherapi-weather',
            'title': 'Which place did you mean? - ' + candidate,
            'text': 'No weather was fetched: the named place matches several locations. Specify a region and country: ' + '; '.join(labels),
            'url': '', 'venue': 'WeatherAPI.com',
            'year': datetime.now(timezone.utc).strftime('%Y-%m-%d')}


def _evidence(payload, queried):
    location = payload.get('location') or {}
    label = _label(location)
    tz = location.get('tz_id')
    if not label or not isinstance(tz, str) or not re.fullmatch(r'[A-Za-z_+\-/]+', tz):
        raise WeatherSourceError('WeatherAPI location/timezone missing [weather:forecast:metadata].')
    retrieved = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    note = ''
    if queried.casefold() != str(location.get('name', '')).casefold():
        note = 'The question named "%s"; WeatherAPI resolved it to %s.' % (queried, label)
    meta = {'place': label, 'timezone': tz, 'retrieved': retrieved, 'place_note': note}
    out = []

    def add(period, values, fields, forecast):
        typed = [{'field': key, 'value': values[key], 'label': info[0], 'unit': info[1]}
                 for key, info in fields.items() if values.get(key) is not None]
        if not typed:
            return
        text = 'This weather data is for %s.\n%s, valid %s (%s).\n%s\nRetrieved: %s. %s' % (
            label, 'Daily forecast' if forecast else 'Current conditions reported by WeatherAPI', period, tz,
            '\n'.join('%s: %s %s' % (f['label'], f['value'], f['unit']) for f in typed), retrieved, ATTRIBUTION)
        text += '\nWEATHERAPI_FACTS_JSON:' + json.dumps({'meta': dict(meta, valid=period, forecast=forecast), 'fields': typed}, ensure_ascii=False, allow_nan=False)
        out.append({'id': 'weatherapi-%s-%s-%s' % ('daily' if forecast else 'current', _slug(label), _slug(period)),
                    'title': ('Daily forecast' if forecast else 'Current weather') + ' - ' + label + ' - ' + period,
                    'text': text, 'url': '', 'venue': 'WeatherAPI.com',
                    'source': 'weatherapi-weather', 'year': retrieved[:10],
                    'attribution': ATTRIBUTION})
    current = payload.get('current') or {}
    valid = current.get('last_updated')
    if isinstance(valid, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', valid):
        add(valid.replace(' ', 'T'), current, CURRENT_FIELDS, False)
    for day in ((payload.get('forecast') or {}).get('forecastday') or [])[:3]:
        valid = day.get('date')
        if isinstance(valid, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', valid):
            add(valid, day.get('day') or {}, DAILY_FIELDS, True)
    if not out:
        return []
    return [dict(out[0], id='weatherapi-weather-' + _slug(label), title='Current and 3-day weather - ' + label, text='\n\n'.join(e['text'] for e in out))]


def weatherapi(query, k=6):
    """Conservative place matching. Ambiguity returns no weather for that place."""
    out, seen = [], set()
    candidates = _candidates(query)
    # Do not truncate a multi-place request into a misleading partial answer.
    if len(candidates) > 2 or bool(re.search(r'\b(compare|between|versus|vs)\b', query, re.I)):
        return [_clarify('multiple places', [{'name': 'Please ask for one city, region and country at a time.'}])]
    for candidate in candidates[:2]:
        matches = _request('search.json', {'q': candidate})
        if not isinstance(matches, list):
            raise WeatherSourceError('WeatherAPI search malformed [weather:geocoding:json].')
        matches = [p for p in matches if isinstance(p, dict) and p.get('name') and p.get('lat') is not None and p.get('lon') is not None]
        if not matches:
            continue
        if len(matches) > 1:
            return [_clarify(candidate, matches)]
        place = matches[0]
        if type(place.get('id')) is not int:
            raise WeatherSourceError('WeatherAPI search identifier missing [weather:geocoding:metadata].')
        point = 'id:' + str(place['id'])
        if point in seen:
            continue
        seen.add(point)
        payload = _request('forecast.json', {'q': point, 'days': 3, 'aqi': 'no', 'alerts': 'no'})
        if not isinstance(payload, dict):
            raise WeatherSourceError('WeatherAPI forecast malformed [weather:forecast:json].')
        returned = payload.get('location') or {}
        try:
            same_area = abs(float(returned['lat'])-float(place['lat'])) <= 0.05 and abs(float(returned['lon'])-float(place['lon'])) <= 0.05
        except (KeyError,TypeError,ValueError):
            same_area = False
        if not same_area:
            raise WeatherSourceError('WeatherAPI returned a different location [weather:forecast:place].')
        out.extend(_evidence(payload, candidate))
    return out
