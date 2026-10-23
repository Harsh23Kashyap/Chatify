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


def _item(link, title, body, date='2024-04-03T00:00:00'):
    return {'link': link, 'date': date,
            'title': {'rendered': title}, 'content': {'rendered': body}}


def _router(payloads, calls=None):
    def fake(req, timeout=25):
        url = req.full_url
        if calls is not None:
            calls.append(url)
        for marker, payload in payloads.items():
            if marker in url:
                return io.BytesIO(json.dumps(payload).encode())
        return io.BytesIO(b'[]')
    return fake


class SfcgTests(unittest.TestCase):
    def test_provenance_dedup_and_host_validation(self):
        good = _item('https://www.sfcg.org/peace-win/', 'Peace Win', '<p>Documented peacebuilding results.</p>')
        evil = _item('https://evil.invalid/peace', 'Evil', 'bad')
        payloads = {'/posts?': [good, good, evil], '/pages?': []}
        with patch.object(p.urllib.request, 'urlopen', _router(payloads)):
            out = p.sfcg('peace process Madagascar', 5)
        self.assertEqual(len(out), 1)
        self.assertIn('Documented peacebuilding results.', out[0]['text'])
        self.assertNotIn('<p>', out[0]['text'])
        self.assertEqual(out[0]['year'], '2024')
        self.assertIn('Search for Common Ground', out[0]['venue'])
        self.assertEqual(out[0]['source'], 'sfcg')

    def test_keyword_relaxation_until_enough_results(self):
        posts = [_item('https://www.sfcg.org/a%d/' % i, 'Item %d' % i, 'body text') for i in range(3)]
        calls = []

        def fake(req, timeout=25):
            url = req.full_url
            calls.append(url)
            if 'search=media+coverage&' in url:
                return io.BytesIO(json.dumps(posts).encode() if '/posts?' in url else b'[]')
            return io.BytesIO(b'[]')

        with patch.object(p.urllib.request, 'urlopen', fake):
            out = p.sfcg('media coverage reduce tensions', 5)
        self.assertEqual(len(out), 3)
        # tried the over-constrained query first, then relaxed
        self.assertIn('media+coverage+reduce+tensions', calls[0])
        self.assertTrue(any('media+coverage' in c and 'reduce' not in c for c in calls))

    def test_question_words_removed_from_search(self):
        calls = []
        with patch.object(p.urllib.request, 'urlopen', _router({'/posts?': [], '/pages?': []}, calls)):
            p.sfcg('How did the peace process in Madagascar work?', 3)
        args = p.urllib.parse.parse_qs(p.urllib.parse.urlparse(calls[0]).query)
        self.assertEqual(args['search'][0], 'Madagascar')

    def test_junk_titles_filtered(self):
        terms = _item('https://www.sfcg.org/terms/', 'Terms & Conditions', 'legal text')
        real = _item('https://www.sfcg.org/media-peace/', 'Media for Peace', 'real peacebuilding work')
        with patch.object(p.urllib.request, 'urlopen', _router({'/posts?': [terms, real], '/pages?': []})):
            out = p.sfcg('media', 5)
        self.assertEqual([e['title'] for e in out], ['Media for Peace'])

    def test_empty_results(self):
        with patch.object(p.urllib.request, 'urlopen', _router({'/posts?': [], '/pages?': []})):
            self.assertEqual(p.sfcg('peace'), [])

    def test_error_is_honest(self):
        with patch.object(p.urllib.request, 'urlopen', side_effect=OSError('down')):
            with self.assertRaises(ValueError) as ctx:
                p.sfcg('peace')
        self.assertIn('could not be retrieved', str(ctx.exception))
        self.assertNotIn('down', str(ctx.exception))

    def test_fallback_when_everything_empty_uses_default(self):
        calls = []
        with patch.object(p.urllib.request, 'urlopen', _router({'/posts?': [], '/pages?': []}, calls)):
            p.sfcg('???', 3)
        self.assertTrue(any('search=peacebuilding' in u for u in calls))


if __name__ == '__main__':
    unittest.main()
