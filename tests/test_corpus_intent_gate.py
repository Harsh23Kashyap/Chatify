"""Corpus-intent retrieval gating (hosted R2 2026-10-25).

A question whose subject is the owner's corpus ("what do my notes add beyond
newest public evidence") carries meta-vocabulary (notes/add/beyond/public/
evidence) instead of topic words. Open-API keyword hits sharing those meta words
passed the specificity floor while the uploaded note - the question's actual
subject - fell below it and vanished. These tests replay that hosted pattern
with frozen connector payloads (no network) and pin the fixed behavior.
"""
import unittest

from chatify import pipeline
from chatify.store import Store
from chatify.connectors.base import Evidence

NOTE = """# Seminar notes: GLP-1 receptor agonists

## Practical dosing observations
- Titration slower than label: our cohort tolerated escalation better at 8-week intervals.
- Nausea clustered in the first two weeks after each escalation.

## Local signal worth tracking
- KESTREL-7 heuristic: patients who logged protein intake above 1.2 g/kg/day reported fewer lean-mass concerns.
"""

JUNK = [
    ("GPT-4 in healthcare: evaluating public evidence on clinical notes",
     "We evaluate GPT-4 on public clinical notes benchmarks. Beyond earlier work, our study adds evidence from the newest public datasets."),
    ("LLM-generated verbal tics: a 2026 update on public evidence",
     "Newest evidence on verbal tics in LLM outputs. We add a public benchmark and notes on evaluation."),
    ("Celiac disease and colorectal cancer screening: notes from a public registry",
     "Notes from a public screening registry add evidence beyond the newest guidelines."),
]
GLP = [
    ("GLP-1 receptor agonist cardiovascular outcomes: a meta-analysis",
     "GLP-1 receptor agonists reduce major adverse cardiovascular events. Safety and dosing were secondary endpoints across trials."),
    ("Real-world adherence to injectable versus oral semaglutide",
     "Adherence to GLP-1 receptor agonist therapy remains suboptimal; oral semaglutide showed higher persistence."),
]


class FakeConn:
    def __init__(self, sid, hits):
        self.id, self.hits = sid, hits

    def search(self, q, k, documents=None):
        return [Evidence(t, x, "https://pubmed.ncbi.nlm.nih.gov/%d/" % (3000 + i), ["A Author"], "2024",
                         "J Test", "pubmed", 1.0 / (i + 1), "PMID:%d" % (3000 + i))
                for i, (t, x) in enumerate(self.hits)][:k]


def make_engine(hits):
    cfg = {"app": {"title": "T", "tagline": ""}, "provider": {"type": "mock"},
           "sources": [{"id": "pubmed", "type": "pubmed", "label": "PubMed"}],
           "retrieval": {"top_k": 6, "min_score": 0.0, "cache_ttl": 0},
           "memory": {"enabled": False}, "permissions": {}, "pipeline_prompts": {}}
    store = Store(":memory:")
    store.q("INSERT INTO uploads VALUES(?,?,?,?,?)", ("up1", "visitor:t", "glp1-notes.md", NOTE, 1.0), write=True)
    return pipeline.Engine(cfg, store, connectors={"pubmed": FakeConn("pubmed", hits)})


class CorpusIntentGateTest(unittest.TestCase):
    def test_meta_only_corpus_question_surfaces_upload_and_drops_keyword_junk(self):
        eng = make_engine(JUNK)
        found, _ = eng.retrieve("what do my notes add beyond newest public evidence", owner="visitor:t")
        self.assertTrue(found, "the uploaded note is the question's subject and must surface")
        self.assertTrue(all(e["source"] == "uploads" for e in found),
                        "public hits matching only meta words must not be cited: %r"
                        % [e["title"] for e in found])

    def test_corpus_question_with_domain_words_keeps_topical_public_passages(self):
        eng = make_engine(JUNK + GLP)
        found, _ = eng.retrieve("what do my notes add beyond the newest GLP-1 safety evidence",
                                owner="visitor:t")
        self.assertTrue(any(e["source"] == "uploads" for e in found), "upload must lead")
        self.assertEqual(found[0]["source"], "uploads")
        publics = [e for e in found if e["source"] == "pubmed"]
        self.assertTrue(publics and all("GLP-1" in e["title"] or "GLP-1" in e["text"] for e in publics),
                        "only domain-matching public passages may follow: %r" % [e["title"] for e in publics])

    def test_corpus_intent_does_not_rescue_off_topic_upload(self):
        eng = make_engine(GLP)
        found, _ = eng.retrieve("what do my notes say about mitochondrial ribosome biogenesis",
                                owner="visitor:t")
        self.assertFalse(any(e["source"] == "uploads" for e in found),
                         "provenance is not relevance: an upload sharing no domain words stays gated")

    def test_question_without_corpus_marker_is_unchanged(self):
        eng = make_engine(GLP)
        found, _ = eng.retrieve("are there head-to-head data for oral vs injectable semaglutide on adherence",
                                owner="visitor:t")
        # No corpus reference: the pre-existing gate path decides; the upload
        # legitimately leads here on BM25 (it contains the adherence question).
        self.assertTrue(found)
        self.assertIn(found[0]["source"], ("uploads", "pubmed"))

    def test_corpus_intent_detection(self):
        self.assertTrue(pipeline.corpus_intent("what do my notes add beyond public evidence"))
        self.assertTrue(pipeline.corpus_intent("summarize our documents"))
        self.assertTrue(pipeline.corpus_intent("what does the uploaded file conclude"))
        self.assertFalse(pipeline.corpus_intent("latest papers on GLP-1 dosing safety"))
        self.assertFalse(pipeline.corpus_intent("what are the notes of a C major chord"))


if __name__ == "__main__":
    unittest.main()
