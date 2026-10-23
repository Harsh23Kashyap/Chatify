"""Wikipedia connector ranking regression pins.

2026-10-23 experiment (see PeaceChat Q&A log): a prototype re-rank that fetched
3x candidates and ranked by query-term coverage in title+intro was measured
live and REVERTED. It failed its goal (the 2009 Malagasy political crisis
intro contains none of the topical words "peace/process/mediation", so
coverage scoring cannot surface it for "How did the peace process in
Madagascar work?") and regressed neighbors:
- "Andry Rajoelina" outranked the topical article for the Madagascar question
- franchise films outranked the country article for "Tell me about Madagascar"

These tests pin the CURRENT contract: the connector preserves the Wikipedia
search service's own relevance order (gsrsearch index), so any future re-rank
attempt must change these tests deliberately.
"""
import io
import json
import unittest
from unittest.mock import patch

from chatify.connectors.base import make_connector


def _pages(*rows):
    return {"query": {"pages": [
        {"title": t, "pageid": i + 1, "index": idx, "extract": x}
        for i, (t, idx, x) in enumerate(rows)]}}


def _fake(payload):
    return lambda req, timeout=20: io.BytesIO(json.dumps(payload).encode())


class WikipediaRankingTests(unittest.TestCase):
    def _search(self, payload, query="q", k=6):
        with patch('chatify.connectors.open_sources._get', return_value=payload):
            return make_connector({"id": "w", "label": "W", "type": "wikipedia"}).search(query, k)

    def test_preserves_service_relevance_order(self):
        # Regression case from the failed experiment: term-coverage re-ranking
        # promoted "Andry Rajoelina" (all query terms in a short intro) over the
        # service's own ordering. Position order must win.
        payload = _pages(
            ("Madagascar", 1, "Madagascar is an island country. Madagascar history and geography."),
            ("Andry Rajoelina", 2, "Andry Rajoelina led the Madagascar peace process transition."),
        )
        out = self._search(payload, "How did the peace process in Madagascar work?")
        self.assertEqual([e["title"] for e in out], ["Madagascar", "Andry Rajoelina"])

    def test_head_term_hub_keeps_position(self):
        # Second regression case: hub article vs franchise pages keeps service order.
        payload = _pages(
            ("Madagascar", 1, "Madagascar is an island country off Africa."),
            ("Madagascar (2005 film)", 2, "Madagascar is a 2005 animated film."),
        )
        out = self._search(payload, "Tell me about Madagascar")
        self.assertEqual([e["title"] for e in out][0], "Madagascar")

    def test_scores_by_service_position_and_asks_service_for_k(self):
        # Current contract: no connector-side slicing or re-ranking; the service
        # is asked for k results and everything returned is kept, scored 1/(n+1)
        # in service order.
        payload = _pages(
            ("One", 1, "first."), ("Two", 2, "second."), ("Three", 3, "third."),
        )
        seen = {}
        def fake(url, timeout=20):
            seen['url'] = url
            return payload
        with patch('chatify.connectors.open_sources._get', side_effect=fake):
            out = make_connector({"id": "w", "label": "W", "type": "wikipedia"}).search("q", 2)
        self.assertEqual([e["title"] for e in out], ["One", "Two", "Three"])
        self.assertEqual([e["score"] for e in out], [1.0, 0.5, 1.0 / 3])
        self.assertIn("gsrlimit=2", seen['url'])

    def test_skips_unusable_pages_and_keeps_order(self):
        payload = _pages(
            ("Sun", 1, "A star."), ("", 2, "no title"), ("Vitamin D", 3, "A vitamin."),
        )
        out = self._search(payload, "q", 6)
        self.assertEqual([e["title"] for e in out], ["Sun", "Vitamin D"])


if __name__ == '__main__':
    unittest.main()
