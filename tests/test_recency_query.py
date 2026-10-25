"""Frozen tests: recency intent qualifies the source query (sort + keyword hygiene)."""
import io, json, unittest
from unittest import mock
from chatify.connectors import pubmed, arxiv
from chatify.pipeline import Engine


class PubMedKeywordHygieneTest(unittest.TestCase):
    def test_meta_intent_words_are_dropped(self):
        self.assertEqual(pubmed.keywords("What are the most recent papers on GLP-1 dosing safety?"),
                         "GLP-1 dosing safety")

    def test_content_words_survive(self):
        self.assertEqual(pubmed.keywords("GLP-1 receptor agonist cardiovascular outcomes"),
                         "GLP-1 receptor agonist cardiovascular outcomes")

    def test_empty_question_falls_back(self):
        self.assertEqual(pubmed.keywords("the and of"), "the and of")


class _Resp:
    def __init__(self, payload): self.payload = payload
    def read(self): return self.payload
    def __enter__(self): return self
    def __exit__(self, *a): return False


class PubMedRecencySortTest(unittest.TestCase):
    def _run(self, recent):
        seen = []
        esearch = json.dumps({"esearchresult": {"idlist": ["1"]}}).encode()
        efetch = (b"<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>1</PMID><Article>"
                  b"<ArticleTitle>T</ArticleTitle><Abstract><AbstractText>GLP-1 dosing safety text.</AbstractText></Abstract>"
                  b"</Article></MedlineCitation></PubmedArticle></PubmedArticleSet>")
        def fake_get(path, **params):
            seen.append((path, dict(params)))
            return esearch if path == "esearch.fcgi" else efetch
        with mock.patch.object(pubmed, "_get", side_effect=fake_get):
            pubmed.PubMed({"id": "pm", "label": "PubMed"}).search("GLP-1 dosing safety", 3, recent=recent)
        return dict(seen[0][1])["sort"]

    def test_recent_question_sorts_by_pub_date(self):
        self.assertEqual(self._run(True), "pub date")

    def test_plain_question_keeps_relevance_sort(self):
        self.assertEqual(self._run(False), "relevance")


class ArxivRecencySortTest(unittest.TestCase):
    def test_recent_question_sorts_by_submitted_date(self):
        seen = []
        feed = b'<feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        def fake_open(url, timeout=0):
            seen.append(url)
            return _Resp(feed)
        with mock.patch.object(arxiv.urllib.request, "urlopen", side_effect=fake_open):
            arxiv.Arxiv({"id": "ax", "label": "arXiv"}).search("GLP-1 dosing", 3, recent=True)
        self.assertIn("sortBy=submittedDate", seen[0])

    def test_plain_question_keeps_relevance(self):
        seen = []
        feed = b'<feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        def fake_open(url, timeout=0):
            seen.append(url)
            return _Resp(feed)
        with mock.patch.object(arxiv.urllib.request, "urlopen", side_effect=fake_open):
            arxiv.Arxiv({"id": "ax", "label": "arXiv"}).search("GLP-1 dosing", 3)
        self.assertIn("sortBy=relevance", seen[0])


class RecencyPlumbingTest(unittest.TestCase):
    """retrieve() passes the recency hint only to connectors that accept it."""
    def _engine(self, conn):
        eng = Engine.__new__(Engine)
        eng.cfg = {"sources": [{"id": "s1", "type": "x", "label": "S"}],
                   "retrieval": {"top_k": 5, "min_score": 0.0, "cache_ttl": 0},
                   "provider": {"type": "mock"}, "owner": None}
        eng.connectors = {"s1": conn}
        eng._cache = {}
        eng.store = mock.Mock()
        eng.store.q.return_value = None
        return eng

    def test_recent_flag_reaches_modern_connector(self):
        calls = []
        class Conn:
            def search(self, q, k, recent=False):
                calls.append(recent)
                return [{"title": "GLP-1 dosing safety 2025", "text": "glp-1 dosing safety glp-1 dosing safety recent papers",
                         "url": "http://x", "authors": [], "year": "2025", "source": "S", "sid": "s1",
                         "score": 0.9, "id": "a"}]
        eng = self._engine(Conn())
        eng._uploads_evidence = lambda *a, **k: []
        found, _ = eng.retrieve("What are the most recent papers on GLP-1 dosing safety?")
        self.assertTrue(found)
        self.assertTrue(calls and all(c is True for c in calls))

    def test_recent_not_passed_to_legacy_connector(self):
        calls = []
        class Legacy:
            def search(self, q, k):
                calls.append((q, k))
                return [{"title": "GLP-1 dosing safety 2025", "text": "glp-1 dosing safety glp-1 dosing safety recent papers",
                         "url": "http://x", "authors": [], "year": "2025", "source": "S", "sid": "s1",
                         "score": 0.9, "id": "a"}]
        eng = self._engine(Legacy())
        eng._uploads_evidence = lambda *a, **k: []
        found, errors = eng.retrieve("What are the most recent papers on GLP-1 dosing safety?")
        self.assertTrue(found)
        self.assertFalse(errors)
        self.assertTrue(calls)

    def test_non_recency_question_sends_no_flag(self):
        calls = []
        class Conn:
            def search(self, q, k, recent=False):
                calls.append(recent)
                return [{"title": "GLP-1 dosing safety", "text": "glp-1 dosing safety glp-1 dosing safety mechanism evidence",
                         "url": "http://x", "authors": [], "year": "2020", "source": "S", "sid": "s1",
                         "score": 0.9, "id": "a"}]
        eng = self._engine(Conn())
        eng._uploads_evidence = lambda *a, **k: []
        found, _ = eng.retrieve("What is known about GLP-1 dosing safety?")
        self.assertTrue(found)
        self.assertTrue(all(c is False for c in calls))


if __name__ == "__main__":
    unittest.main()
