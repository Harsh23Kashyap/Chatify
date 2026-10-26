"""retrieve() rerank branch routing (2026-10-26 fix).

Before the fix the rerank call sat in an `else` of "any owner-corpus hit",
so PURE owner-corpus retrievals (every local_files app, incl. the whole
hosted gallery) never reached it. These tests pin: pure owner corpus and
pure open-API results get the semantic re-order; only genuinely mixed
corpora keep the historical owner-score ordering.
"""
import unittest

from chatify import pipeline, rerank
from chatify.store import Store
from chatify.connectors.base import Evidence

NOTE = ("# GLP-1 notes\n- Titration slower than label for glp-1 receptor agonists.\n"
        "- Nausea clustered early after each escalation of glp-1 dosing.\n")
HITS = [
    ("GLP-1 receptor agonist dosing study", "GLP-1 receptor agonist dosing and titration outcomes in a randomized study."),
    ("Semaglutide adherence real world", "Adherence to GLP-1 receptor agonist therapy and dosing persistence."),
]
Q = "glp-1 receptor agonist dosing"


class FakeConn:
    def __init__(self, sid, hits):
        self.id, self.hits = sid, hits

    def search(self, q, k, documents=None):
        return [Evidence(t, x, "https://example.test/%d" % i, ["A Author"], "2024",
                         "J Test", "pubmed", 1.0 / (i + 1), "E%d" % i)
                for i, (t, x) in enumerate(self.hits)][:k]


def engine(with_upload, with_hits):
    cfg = {"app": {"title": "T", "tagline": ""}, "provider": {"type": "mock"},
           "sources": [{"id": "pubmed", "type": "pubmed", "label": "PubMed"}],
           "retrieval": {"top_k": 6, "min_score": 0.0, "cache_ttl": 0},
           "memory": {"enabled": False}, "permissions": {}, "pipeline_prompts": {}}
    store = Store(":memory:")
    if with_upload:
        store.q("INSERT INTO uploads VALUES(?,?,?,?,?)", ("up1", "visitor:t", "glp1.md", NOTE, 1.0), write=True)
    conn = FakeConn("pubmed", HITS if with_hits else [])
    return pipeline.Engine(cfg, store, connectors={"pubmed": conn})


class Recorder:
    def __init__(self):
        self.calls = []

    def __call__(self, question, found, enabled=True):
        self.calls.append([e.get("title") for e in found])
        return list(reversed(found))


class RerankRoutingTest(unittest.TestCase):
    def run_case(self, with_upload, with_hits):
        rec = Recorder()
        orig = rerank.rerank
        rerank.rerank = rec
        try:
            eng = engine(with_upload, with_hits)
            found, _ = eng.retrieve(Q, owner="visitor:t")
        finally:
            rerank.rerank = orig
        return rec, found

    def test_pure_owner_corpus_reaches_rerank(self):
        rec, found = self.run_case(True, False)
        self.assertTrue(rec.calls, "pure owner corpus must reach the rerank stage")
        self.assertTrue(found)

    def test_pure_open_api_reaches_rerank(self):
        rec, found = self.run_case(False, True)
        self.assertTrue(rec.calls, "pure open-API results must reach the rerank stage")
        self.assertTrue(found)

    def test_mixed_corpus_keeps_score_order_and_skips_rerank(self):
        rec, found = self.run_case(True, True)
        self.assertFalse(rec.calls, "mixed corpus must keep owner score ordering, no rerank call")
        self.assertTrue(found)

    def test_failure_fallback_order_preserved(self):
        def boom(question, found, enabled=True):
            raise RuntimeError("onnxruntime missing")
        orig = rerank.rerank
        rerank.rerank = boom
        try:
            eng = engine(True, False)
            try:
                found, _ = eng.retrieve(Q, owner="visitor:t")
                raised = False
            except RuntimeError:
                raised = True
        finally:
            rerank.rerank = orig
        self.assertFalse(raised, "a rerank-stage failure must not break retrieval")


if __name__ == "__main__":
    unittest.main()
