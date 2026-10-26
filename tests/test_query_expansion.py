"""Zero-evidence synonym expansion (ISSUE-10 synonym-recall arm).

When the relevance gate empties the public evidence set, one bounded provider
rewrite adds standard synonyms and the open connectors are re-searched once.
The gate then applies to the UNION vocabulary and every rescued passage must
share at least two union content words, so a single expanded token cannot
launder an off-topic page into the answer. Any provider or contract failure
falls back to the honest no-evidence result.
"""
import unittest

from chatify import pipeline, providers
from chatify.store import Store
from chatify.connectors.base import Evidence

MI = ("Myocardial infarction: acute management and secondary prevention",
      "Acute myocardial infarction is managed with reperfusion, antiplatelet agents, anticoagulation, and secondary prevention including statins, beta blockers and cardiac rehabilitation.")
VALVE = ("Heart valve surgery recovery timeline",
         "Recovery after heart valve surgery takes six to eight weeks. Patients gradually resume activity under cardiac rehabilitation guidance.")
PANTHERA = ("Jaguar (Panthera onca) habitat and range",
            "The jaguar Panthera onca ranges from Mexico to Argentina. Habitat loss fragments the remaining populations.")
CAR = ("Jaguar cars reliability survey",
       "Jaguar cars scored below average in the latest reliability survey. Owners report electrical faults.")
STAFFING = ("Cardiac catheterization lab staffing norms",
            "Catheterization labs staff two nurses and one technician per shift. On-call teams respond within thirty minutes.")


class StubProvider:
    """Records expand calls and returns a canned rewrite; everything else is a stub."""
    def __init__(self, expansion=None, fail=False):
        self.expansion, self.fail, self.expand_calls = expansion, fail, 0

    def complete(self, messages):
        if messages[0]["content"] == pipeline.Engine.stage_prompt(self._eng, "expand"):
            self.expand_calls += 1
            if self.fail:
                raise providers.ProviderError("boom")
            return self.expansion or ""
        return "unused"


def make_engine(hits_by_keyword, provider, with_upload=False):
    class Conn:
        id = "pubmed"

        def search(self, q, k, documents=None):
            out = []
            for i, (kw, (t, x)) in enumerate(hits_by_keyword):
                if kw in q.lower():
                    out.append(Evidence(t, x, "https://example/%d" % i, ["A A"], "2024", "J",
                                        "pubmed", 1.0 / (i + 1), "X:%d" % i))
            return out[:k]

    cfg = {"app": {"title": "T", "tagline": ""}, "provider": {"type": "mock"},
           "sources": [{"id": "pubmed", "type": "pubmed", "label": "PubMed"}],
           "retrieval": {"top_k": 6, "min_score": 0.0, "cache_ttl": 0},
           "memory": {"enabled": False}, "permissions": {}, "pipeline_prompts": {}}
    eng = pipeline.Engine(cfg, Store(":memory:"), provider=provider, connectors={"pubmed": Conn()})
    provider._eng = eng
    return eng


class QueryExpansionTest(unittest.TestCase):
    def test_synonym_rescue_surfaces_zero_overlap_passage(self):
        prov = StubProvider("heart attack treatment options myocardial infarction acute coronary syndrome")
        eng = make_engine([("myocardial", MI)], prov)
        found, _ = eng.retrieve("heart attack treatment options", owner="visitor:t")
        self.assertEqual([e["title"] for e in found], [MI[0]])
        self.assertEqual(prov.expand_calls, 1)

    def test_expansion_call_is_bounded_by_cache(self):
        prov = StubProvider("heart attack treatment options myocardial infarction")
        eng = make_engine([("myocardial", MI)], prov)
        eng.retrieve("heart attack treatment options", owner="visitor:t")
        eng.retrieve("heart attack treatment options", owner="visitor:t")
        self.assertEqual(prov.expand_calls, 1)

    def test_single_token_laundering_is_blocked(self):
        # Animal-intent question; the car page shares only "jaguar" with the union
        # vocabulary, so the two-word rule keeps it out even after expansion.
        prov = StubProvider("jaguar habitat panthera onca range")
        eng = make_engine([("panthera", PANTHERA), ("range", CAR)], prov)
        found, _ = eng.retrieve("jaguar habitat", owner="visitor:t")
        self.assertEqual([e["title"] for e in found], [PANTHERA[0]])

    def test_expansion_dropping_an_original_word_is_rejected(self):
        prov = StubProvider("myocardial infarction acute management")
        eng = make_engine([("myocardial", MI)], prov)
        found, _ = eng.retrieve("heart attack treatment options", owner="visitor:t")
        self.assertEqual(found, [])

    def test_negation_parity_violation_is_rejected(self):
        prov = StubProvider("treatments that cure insomnia myocardial infarction")
        eng = make_engine([("myocardial", MI)], prov)
        found, _ = eng.retrieve("treatments that do not cure insomnia", owner="visitor:t")
        self.assertEqual(found, [])

    def test_corpus_question_never_expands(self):
        prov = StubProvider("my notes add beyond newest public evidence myocardial")
        eng = make_engine([("myocardial", MI)], prov)
        found, _ = eng.retrieve("what do my notes add beyond newest public evidence", owner="visitor:t")
        self.assertEqual(found, [])
        self.assertEqual(prov.expand_calls, 0)

    def test_all_junk_still_abstains(self):
        prov = StubProvider("heart attack treatment options myocardial infarction")
        eng = make_engine([("myocardial", VALVE), ("cardiac", STAFFING)], prov)
        found, _ = eng.retrieve("heart attack treatment options", owner="visitor:t")
        self.assertEqual(found, [])

    def test_provider_failure_falls_back_to_abstention(self):
        prov = StubProvider(fail=True)
        eng = make_engine([("myocardial", MI)], prov)
        found, _ = eng.retrieve("heart attack treatment options", owner="visitor:t")
        self.assertEqual(found, [])

    def test_mock_provider_output_is_rejected_by_contract(self):
        eng = make_engine([("myocardial", MI)], providers.Mock({}))
        found, _ = eng.retrieve("heart attack treatment options", owner="visitor:t")
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
