import importlib.util
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('peace_sources', Path(__file__).parents[1] / 'apps/peacechat/peace_sources.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class ReliefWebTests(unittest.TestCase):
    def test_requires_appname(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(ValueError, 'RELIEFWEB_APPNAME'):
            p.reliefweb('Liberia')

    def test_report_body_provenance_and_dedup(self):
        row = {'fields': {'title': 'Peace in Liberia', 'body': 'Documented peacebuilding results.', 'url_alias': 'https://reliefweb.int/report/liberia/peace', 'date': {'original': '2024-04-03T00:00:00Z'}, 'source': [{'name': 'United Nations'}]}}
        bad = {'fields': dict(row['fields'], url_alias='https://evil.invalid/report')}
        with patch.dict(os.environ, {'RELIEFWEB_APPNAME': 'test-app'}), patch.object(p.urllib.request, 'urlopen', return_value=io.BytesIO(json.dumps({'data': [row, row, bad]}).encode())) as call:
            out = p.reliefweb('recent Liberia peace', 3)
        self.assertEqual(len(out), 1)
        self.assertIn('Documented peacebuilding results.', out[0]['text'])
        self.assertIn('United Nations', out[0]['venue'])
        self.assertEqual(out[0]['year'], '2024')
        self.assertIn('/v2/reports?', call.call_args.args[0].full_url)
        self.assertIn('sort%5B%5D=date%3Adesc', call.call_args.args[0].full_url)

    def test_error_is_honest_without_appname_leak(self):
        with patch.dict(os.environ, {'RELIEFWEB_APPNAME': 'private-test-value'}), patch.object(p.urllib.request, 'urlopen', side_effect=OSError('private-test-value')):
            with self.assertRaises(ValueError) as ctx:
                p.reliefweb('peace')
        self.assertNotIn('private-test-value', str(ctx.exception))

    def test_question_keywords_keep_topic_not_question_words(self):
        fresh = lambda *a, **k: io.BytesIO(b'{"data": []}')
        with patch.dict(os.environ, {'RELIEFWEB_APPNAME': 'test'}), patch.object(p.urllib.request, 'urlopen', side_effect=fresh) as call:
            p.reliefweb("What role did women play in Liberia's peace process?", 3)
        # relaxation: the first call ANDs every keyword, later calls drop words
        args = p.urllib.parse.parse_qs(p.urllib.parse.urlparse(call.call_args_list[0].args[0].full_url).query)
        self.assertTrue(args['query[value]'][0].startswith('("women" AND "Liberia") AND'))
        last = p.urllib.parse.parse_qs(p.urllib.parse.urlparse(call.call_args_list[-1].args[0].full_url).query)
        self.assertTrue(last['query[value]'][0].startswith('("women") AND'))

    def test_empty_results(self):
        with patch.dict(os.environ, {'RELIEFWEB_APPNAME': 'test'}), patch.object(p.urllib.request, 'urlopen', return_value=io.BytesIO(b'{"data": []}')):
            self.assertEqual(p.reliefweb('peace'), [])
    def test_keyword_relaxation_recovers_results(self):
        row = {'fields': {'title': 'Media for peace in Kenya', 'body': 'Media programming reduced tensions.', 'url_alias': 'https://reliefweb.int/report/kenya/media-peace', 'date': {'original': '2020-03-01T00:00:00Z'}, 'source': [{'name': 'AFP'}]}}
        calls = []

        def fake(req, timeout=25):
            calls.append(req.full_url)
            strict = 'AND+%22coverage%22' in req.full_url or 'AND %22coverage%22' in req.full_url
            return io.BytesIO(json.dumps({'data': [] if strict else [row]}).encode())

        with patch.dict(os.environ, {'RELIEFWEB_APPNAME': 'test'}), patch.object(p.urllib.request, 'urlopen', fake):
            out = p.reliefweb('media coverage reduce tensions', 3)
        self.assertEqual(len(out), 1)
        first = p.urllib.parse.parse_qs(p.urllib.parse.urlparse(calls[0]).query)['query[value]'][0]
        self.assertIn('"media" AND "coverage"', first)  # strictest level first
        last = p.urllib.parse.parse_qs(p.urllib.parse.urlparse(calls[-1]).query)['query[value]'][0]
        self.assertIn('("media") AND', last)  # relaxed until coverage was dropped

    def test_filler_verbs_and_generic_words_are_not_keywords(self):
        fresh = lambda *a, **k: io.BytesIO(b'{"data": []}')
        with patch.dict(os.environ, {'RELIEFWEB_APPNAME': 'test'}), patch.object(p.urllib.request, 'urlopen', side_effect=fresh) as call:
            p.reliefweb('How did the peace process in Madagascar work?', 3)
        args = p.urllib.parse.parse_qs(p.urllib.parse.urlparse(call.call_args_list[0].args[0].full_url).query)
        self.assertTrue(args['query[value]'][0].startswith('("Madagascar") AND'))  # 'work' is not a topic keyword
        self.assertEqual(call.call_count, 1)

    def test_relaxation_call_count_is_bounded(self):
        fresh = lambda *a, **k: io.BytesIO(b'{"data": []}')
        with patch.dict(os.environ, {'RELIEFWEB_APPNAME': 'test'}), patch.object(p.urllib.request, 'urlopen', side_effect=fresh) as call:
            out = p.reliefweb('alpha beta gamma delta epsilon', 3)
        self.assertEqual(out, [])
        self.assertLessEqual(call.call_count, 4)  # at most one call per keyword level


if __name__ == '__main__':
    unittest.main()
