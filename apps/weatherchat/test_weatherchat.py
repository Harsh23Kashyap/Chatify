"""WeatherChat connector regressions. Network is mocked; the live Open-Meteo
smoke test at the bottom runs only with WEATHERCHAT_LIVE=1."""
import json
import os
import unittest
from unittest.mock import patch
from pathlib import Path
import urllib.error

import weather_sources as w

GEO_BANGALORE = {'results': [{'name': 'Bangalore Town', 'admin1': 'Sindh', 'country': 'Pakistan',
                              'latitude': 24.87, 'longitude': 67.08, 'feature_code': 'PPLX'}]}
GEO_BENGALURU = {'results': [{'name': 'Bengaluru', 'admin1': 'Karnataka', 'country': 'India',
                              'latitude': 12.97, 'longitude': 77.59, 'population': 8495492,
                              'feature_code': 'PPLA'}]}
FORECAST = {
    'timezone': 'Asia/Kolkata',
    'current': {'time': '2026-11-05T10:15', 'temperature_2m': 26.0, 'apparent_temperature': 28.4,
                'relative_humidity_2m': 78, 'is_day': 1, 'precipitation': 0.0, 'weather_code': 2,
                'wind_speed_10m': 9.4, 'wind_direction_10m': 90},
    'hourly': {'time': ['2026-11-05T10:00', '2026-11-05T11:00'],
               'temperature_2m': [26.0, 27.1], 'precipitation_probability': [10, 20],
               'weather_code': [2, 61]},
    'daily': {'time': ['2026-11-05', '2026-11-06', '2026-11-07'],
              'weather_code': [2, 61, 3],
              'temperature_2m_max': [30.1, 28.0, 29.0], 'temperature_2m_min': [21.0, 22.0, 21.5],
              'precipitation_probability_max': [10, 80, 40], 'precipitation_sum': [0.0, 5.2, 1.1],
              'wind_speed_10m_max': [12.0, 15.0, 11.0],
              'sunrise': ['2026-11-05T06:20', '2026-11-06T06:20', '2026-11-07T06:21'],
              'sunset': ['2026-11-05T17:55', '2026-11-06T17:55', '2026-11-07T17:54'],
              'uv_index_max': [6.0, 4.0, 5.0]},
}


class Reply:
    def __init__(self, payload): self.payload = payload
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def read(self, *a): return json.dumps(self.payload).encode()


def fake_urlopen(payloads):
    def _open(req, timeout=0):
        url = req.full_url
        for key in sorted(payloads, key=len, reverse=True):
            if key in url:
                return Reply(payloads[key])
        raise AssertionError('unexpected URL ' + url)
    return _open


BANGALORE_CALLS = {'geocoding-api': GEO_BANGALORE, 'v1/forecast': FORECAST}


class PlaceExtractionTests(unittest.TestCase):
    def test_place_after_preposition(self):
        self.assertEqual(w._candidates('What is the weather in Bangalore right now?'), ['Bangalore'])

    def test_place_before_keyword(self):
        self.assertIn('Bangalore', w._candidates('Bangalore weather today'))

    def test_time_words_stripped(self):
        self.assertEqual(w._candidates('will it rain in Mumbai tomorrow?'), ['Mumbai'])

    def test_generic_question_has_no_place(self):
        self.assertEqual(w._candidates("what is the weather like today?"), [])

    def test_multiword_place(self):
        self.assertIn('New York', w._candidates('How is the weather in New York this weekend?'))

    def test_preposition_only_noise_rejected(self):
        self.assertEqual(w._candidates('is it hot in there?'), [])


class MappingTests(unittest.TestCase):
    def test_wmo_codes(self):
        self.assertEqual(w.WMO[61], 'light rain')
        self.assertEqual(w.WMO[95], 'thunderstorm')

    def test_compass(self):
        self.assertEqual(w._compass(90), 'E')
        self.assertEqual(w._compass(225), 'SW')
        self.assertEqual(w._compass(360), 'N')
        self.assertEqual(w._compass(None), '')


class ResolutionTests(unittest.TestCase):
    def test_bangalore_alias_prefers_bengaluru(self):
        # The geocoder only knows "Bangalore Town" in Pakistan for the literal
        # query; the rename alias must win so the Indian city answers.
        payloads = {'name=Bangalore': GEO_BANGALORE, 'name=bengaluru': GEO_BENGALURU,
                    'v1/forecast': FORECAST}
        with patch('urllib.request.urlopen', side_effect=fake_urlopen(payloads)):
            items = w.open_meteo('What is the weather in Bangalore right now?', 6)
        self.assertIn('Bengaluru, Karnataka, India', items[0]['title'])
        self.assertIn('resolves to Bengaluru', items[0]['text'])

    def test_unknown_place_returns_nothing(self):
        with patch('urllib.request.urlopen', side_effect=fake_urlopen({'geocoding-api': {'results': []}})):
            self.assertEqual(w.open_meteo('weather in Zzznotaplace', 6), [])

    def test_ambiguous_place_returns_clarification_not_weather(self):
        geo = {'results': [
            {'name': 'Cambridge', 'admin1': 'England', 'country': 'United Kingdom',
             'latitude': 52.2, 'longitude': 0.12, 'population': 145000, 'feature_code': 'PPLA'},
            {'name': 'Cambridge', 'admin1': 'Massachusetts', 'country': 'United States',
             'latitude': 42.37, 'longitude': -71.1, 'population': 118000, 'feature_code': 'PPLA'}]}
        seen_urls = []
        def spy(req, timeout=0):
            seen_urls.append(req.full_url)
            return fake_urlopen({'geocoding-api': geo, 'v1/forecast': FORECAST})(req)
        with patch('urllib.request.urlopen', side_effect=spy):
            items = w.open_meteo('weather in Cambridge', 6)
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0]['id'].startswith('open-meteo-clarify-'))
        self.assertIn('Cambridge, England, United Kingdom', items[0]['text'])
        self.assertIn('Cambridge, Massachusetts, United States', items[0]['text'])
        self.assertIn('no weather data', items[0]['text'])
        self.assertFalse(any('v1/forecast' in u for u in seen_urls), seen_urls)

    def test_dominant_match_resolves_with_alternates_note(self):
        # London UK outweighs London Ontario >10x: resolves, note names alternatives.
        geo = {'results': [
            {'name': 'London', 'admin1': 'England', 'country': 'United Kingdom',
             'latitude': 51.5, 'longitude': -0.12, 'population': 8961989, 'feature_code': 'PPLC'},
            {'name': 'London', 'admin1': 'Ontario', 'country': 'Canada',
             'latitude': 42.98, 'longitude': -81.25, 'population': 346765, 'feature_code': 'PPLA'}]}
        with patch('urllib.request.urlopen', side_effect=fake_urlopen({'geocoding-api': geo, 'v1/forecast': FORECAST})):
            items = w.open_meteo('weather in London', 6)
        self.assertIn('London, England, United Kingdom', items[0]['title'])
        self.assertIn('Ontario', items[0]['text'])
        self.assertEqual(len(items), 4)


class EvidenceTests(unittest.TestCase):
    def _items(self):
        with patch('urllib.request.urlopen', side_effect=fake_urlopen(BANGALORE_CALLS)):
            return w.open_meteo('weather in Bangalore Town', 6)

    def test_current_conditions_fields_and_units(self):
        text = self._items()[0]['text']
        for needle in ['26.0 C', 'feels like 28.4 C', '78%', '9.4 km/h', 'Asia/Kolkata',
                       'valid at 2026-11-05T10:15', 'partly cloudy']:
            self.assertIn(needle, text)

    def test_tomorrow_uses_second_day(self):
        items = self._items()
        tomorrow = [i for i in items if i['title'].startswith('Tomorrow')][0]
        self.assertIn('2026-11-06', tomorrow['text'])
        self.assertIn('rain chance 80%', tomorrow['text'])

    def test_week_lists_each_day(self):
        week = [i for i in self._items() if i['title'].startswith('7-day')][0]
        for day in ['2026-11-05', '2026-11-06', '2026-11-07']:
            self.assertIn(day, week['text'])

    def test_attribution_and_source_url_present(self):
        for item in self._items():
            self.assertIn('Open-Meteo.com', item['text'])
            self.assertTrue(item['url'].startswith('https://api.open-meteo.com/v1/forecast'))
            self.assertNotIn('apikey=', item['url'])

    def test_plain_terms_carry_aspect_words(self):
        # Users ask with adjectives (humid, windy, hot); the gate needs the vocabulary.
        text = self._items()[0]['text']
        for needle in ['humid', 'wind', 'feels']:
            self.assertIn(needle, text)

    def test_retrieval_timestamp_present(self):
        self.assertIn('Retrieved: ', self._items()[0]['text'])

    def test_http_error_is_clear(self):
        def boom(req, timeout=0):
            raise urllib.error.HTTPError(req.full_url, 500, 'err', {}, None)
        with patch('urllib.request.urlopen', side_effect=boom):
            with self.assertRaises(ValueError) as ctx:
                w.open_meteo('weather in Bengaluru', 6)
        self.assertIn('Open-Meteo', str(ctx.exception))

    def test_no_place_makes_no_network_call(self):
        with patch('urllib.request.urlopen') as req:
            self.assertEqual(w.open_meteo('what is the weather like?', 6), [])
            req.assert_not_called()


class PipelineIntegrationTests(unittest.TestCase):
    def _items(self, payloads=None):
        with patch('urllib.request.urlopen', side_effect=fake_urlopen(payloads or BANGALORE_CALLS)):
            return w.open_meteo('weather in Bangalore Town', 6)

    def test_items_have_distinct_urls(self):
        # The Chatify pipeline dedups evidence by URL; shared URLs collapse the set.
        urls = [i['url'] for i in self._items()]
        self.assertEqual(len(urls), len(set(urls)))

    def test_relevance_gate_keeps_forecast_items(self):
        from chatify.pipeline import relevance_gate
        items = self._items()
        kept = relevance_gate('Will it rain in Bangalore Town tomorrow?', items)
        titles = [e['title'] for e in kept]
        self.assertTrue(any(t.startswith('Tomorrow') for t in titles), titles)

    def test_bombay_alias_prefers_mumbai(self):
        geo_bombay = {'results': [{'name': 'Bombay', 'admin1': 'Auckland', 'country': 'New Zealand',
                                   'latitude': -37.16, 'longitude': 174.98, 'feature_code': 'PPL'}]}
        geo_mumbai = {'results': [{'name': 'Mumbai', 'admin1': 'Maharashtra', 'country': 'India',
                                   'latitude': 19.07, 'longitude': 72.87, 'population': 12691836,
                                   'feature_code': 'PPLA'}]}
        payloads = {'name=Bombay': geo_bombay, 'name=mumbai': geo_mumbai, 'v1/forecast': FORECAST}
        with patch('urllib.request.urlopen', side_effect=fake_urlopen(payloads)):
            items = w.open_meteo('Bombay weather tomorrow', 6)
        self.assertIn('Mumbai, Maharashtra, India', items[0]['title'])

    def test_local_weather_forecast_makes_no_place(self):
        # Model query-rewrites produce "local weather forecast"; 'local' is not a place.
        with patch('urllib.request.urlopen') as req:
            self.assertEqual(w.open_meteo('local weather forecast', 6), [])
            req.assert_not_called()


class WordingHonestyTests(unittest.TestCase):
    """Main-agent review: model-derived data must not be called an observation,
    and precipitation must carry its backward-looking interval meaning."""

    def _items(self):
        with patch('urllib.request.urlopen', side_effect=fake_urlopen(BANGALORE_CALLS)):
            return w.open_meteo('weather in Bangalore Town', 6)

    def test_current_never_called_observation(self):
        text = self._items()[0]['text']
        self.assertNotIn('observed', text.lower())
        self.assertIn('not a station observation', text)
        self.assertIn('valid at 2026-11-05T10:15', text)

    def test_precipitation_interval_explained(self):
        # Mock has no interval -> default 900s = 15 minutes, backward-looking.
        text = self._items()[0]['text']
        self.assertIn('Precipitation in the 15 minutes up to that time', text)
        self.assertIn('in the past 15 minutes', text)
        self.assertNotIn('so far this hour', text)


class MultiPlaceTests(unittest.TestCase):
    GEO_DELHI = {'results': [{'name': 'Delhi', 'admin1': 'National Capital Territory of Delhi',
                              'country': 'India', 'latitude': 28.63, 'longitude': 77.22,
                              'population': 10927986, 'feature_code': 'PPLA'}]}
    GEO_MUMBAI = {'results': [{'name': 'Mumbai', 'admin1': 'Maharashtra', 'country': 'India',
                               'latitude': 19.07, 'longitude': 72.87, 'population': 12691836,
                               'feature_code': 'PPLA'}]}
    GEO_TRINIDAD = {'results': [{'name': 'Trinidad and Tobago', 'country': 'Trinidad and Tobago',
                                 'latitude': 10.69, 'longitude': -61.22, 'feature_code': 'PCLI'}]}

    def test_two_place_comparison_covers_both(self):
        payloads = {'name=Delhi+and+Mumbai': {'results': []}, 'name=Delhi': self.GEO_DELHI,
                    'name=Mumbai': self.GEO_MUMBAI, 'v1/forecast': FORECAST}
        with patch('urllib.request.urlopen', side_effect=fake_urlopen(payloads)):
            items = w.open_meteo('Compare the weather in Delhi and Mumbai today', 12)
        places = {i['title'].split(' - ', 1)[1] for i in items}
        self.assertIn('Delhi, National Capital Territory of Delhi, India', places)
        self.assertIn('Mumbai, Maharashtra, India', places)

    def test_compound_country_stays_one_place(self):
        payloads = {'geocoding-api': self.GEO_TRINIDAD, 'v1/forecast': FORECAST}
        with patch('urllib.request.urlopen', side_effect=fake_urlopen(payloads)):
            items = w.open_meteo('weather in Trinidad and Tobago', 12)
        places = {i['title'].split(' - ', 1)[1] for i in items}
        self.assertEqual(places, {'Trinidad and Tobago, Trinidad and Tobago'})

    def test_alternates_note_on_every_item(self):
        geo = {'results': [
            {'name': 'Cambridge', 'admin1': 'England', 'country': 'United Kingdom',
             'latitude': 52.2, 'longitude': 0.12, 'population': 145000, 'feature_code': 'PPLA'},
            {'name': 'Cambridge', 'admin1': 'Massachusetts', 'country': 'United States',
             'latitude': 42.37, 'longitude': -71.1, 'population': 30000, 'feature_code': 'PPL'}]}
        with patch('urllib.request.urlopen', side_effect=fake_urlopen({'geocoding-api': geo, 'v1/forecast': FORECAST})):
            items = w.open_meteo('weather in Cambridge', 6)
        self.assertTrue(items)
        for item in items:
            self.assertIn('Massachusetts', item['text'], item['title'])

    def test_item_ids_unique_across_places(self):
        payloads = {'name=Delhi+and+Mumbai': {'results': []}, 'name=Delhi': self.GEO_DELHI,
                    'name=Mumbai': self.GEO_MUMBAI, 'v1/forecast': FORECAST}
        with patch('urllib.request.urlopen', side_effect=fake_urlopen(payloads)):
            items = w.open_meteo('Compare the weather in Delhi and Mumbai today', 12)
        ids = [i['id'] for i in items]
        self.assertEqual(len(ids), len(set(ids)), ids)
        self.assertEqual(len(items), 8)


class ConfigTests(unittest.TestCase):
    def test_all_config_fields(self):
        import yaml
        from chatify.schema import DEFAULTS, validate
        def check(raw, base):
            for key, value in base.items():
                self.assertIn(key, raw)
                if isinstance(value, dict):
                    check(raw[key], value)
        for f in Path(__file__).parent.glob('app*.yaml'):
            raw = yaml.safe_load(f.read_text())
            validate(raw)
            check(raw, DEFAULTS)


@unittest.skipUnless(os.environ.get('WEATHERCHAT_LIVE'), 'live Open-Meteo smoke test opt-in')
class LiveTests(unittest.TestCase):
    def test_live_bangalore(self):
        items = w.open_meteo('What is the weather in Bangalore right now?', 6)
        self.assertEqual(len(items), 4)
        self.assertIn('Bengaluru', items[0]['title'])
        self.assertIn('Asia/Kolkata', items[0]['text'])


if __name__ == '__main__':
    unittest.main()
