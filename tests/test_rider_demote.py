"""Adjacent-rider demotion (hosted ISSUE-10 follow-up, 2026-10-25).

A review of a DIFFERENT disease whose abstract echoes the question vocabulary
("B-cell acute lymphoblastic leukemia immunotherapy: a review" for a CAR-T
lymphoma question) cleared every lexical floor. The demote rule sinks public
passages whose TITLES share no title-level discriminating question word - only
when at least two retained public passages do carry one - and never drops them.
"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chatify.pipeline import relevance_gate, Engine
from chatify.store import Store


def ev(n, title, text, source="pubmed", year="2022"):
    return {"n": n, "title": title, "text": text, "score": 1.0 / n, "id": str(n), "source": source, "year": year,
            "url": "https://pubmed.ncbi.nlm.nih.gov/%d/" % (3000 + n), "authors": ["A Author"], "venue": "J Test"}


Q = "main findings of recent trials CAR-T cell therapy lymphoma"
BALL = ev(1, "B-cell acute lymphoblastic leukemia immunotherapy: a review",
          "This review discusses CAR-T cell therapy and trials; findings in lymphoma and leukemia are summarized. " * 5)
CART = ev(2, "CAR T-cell therapy for B-cell lymphoma",
          "CAR-T cell therapy trials in B-cell lymphoma: main findings, response and durability. " * 5)
ADV = ev(3, "Advances in cancer immunotherapy",
         "Cancer immunotherapy including CAR-T cell therapy: trials and findings reviewed. " * 5)
ZUMAT = ev(4, "Axicabtagene ciloleucel CAR T-cell therapy in refractory large B-cell lymphoma",
           "CAR-T cell therapy trials in refractory large B-cell lymphoma: main findings. " * 5)
ZUMAV = ev(5, "ZUMA-1: a phase 2 study",
           "CAR-T cell therapy trials in refractory large B-cell lymphoma: main findings on response. " * 5)
NOTITLE = ev(6, "", "CAR-T cell therapy lymphoma trials findings. " * 5)


class RiderDemote(unittest.TestCase):
    def test_riders_sink_genuine_leads_nothing_dropped(self):
        out = relevance_gate(Q, [BALL, CART, ADV, ZUMAT])
        titles = [e["title"] for e in out]
        self.assertEqual(len(out), 4)  # demote, never drop
        self.assertEqual(titles[:2], [CART["title"], ZUMAT["title"]])
        self.assertEqual(set(titles[2:]), {BALL["title"], ADV["title"]})
        self.assertTrue(out[2].get("_demoted") and out[3].get("_demoted"))
        self.assertFalse(out[0].get("_demoted") or out[1].get("_demoted"))

    def test_vague_title_genuine_study_retained(self):
        out = relevance_gate(Q, [BALL, CART, ZUMAV, ZUMAT])
        self.assertIn(ZUMAV["title"], [e["title"] for e in out])

    def test_missing_title_record_retained(self):
        out = relevance_gate(Q, [BALL, CART, NOTITLE, ZUMAT])
        self.assertEqual(len([e for e in out if not e["title"]]), 1)

    def test_single_strong_match_leaves_order_unchanged(self):
        # One strong title signal is not enough: uncertain sets keep gate order.
        out = relevance_gate(Q, [BALL, CART, ADV])
        self.assertEqual([e["title"] for e in out],
                         [e["title"] for e in relevance_gate(Q, [BALL, CART, ADV])])
        self.assertIn(CART["title"], [e["title"] for e in out])

    def test_private_sources_exempt(self):
        up = ev(7, "glp1-notes.md", "CAR-T cell therapy lymphoma trials findings: notes on response and durability. " * 5, source="uploads")
        out = relevance_gate(Q, [BALL, CART, up, ZUMAT], public_ids={"pubmed"})
        titles = [e["title"] for e in out]
        self.assertIn("glp1-notes.md", titles)
        demoted_titles = {e["title"] for e in out if e.get("_demoted")}
        self.assertNotIn("glp1-notes.md", demoted_titles)

    def test_preview_wording_marks_loosely_matched_tail(self):
        out = relevance_gate(Q, [BALL, CART, ADV, ZUMAT])
        text = Engine.fallback_answer(out, question=Q)
        self.assertIn("matched the question only loosely", text)
        # loose matches are named by citation marker, not by list position
        self.assertIn("[3]", text) and self.assertIn("[4]", text)
        clean = relevance_gate(Q, [CART, ZUMAT])
        self.assertNotIn("loosely", Engine.fallback_answer(clean, question=Q))


class RecencyComposition(unittest.TestCase):
    """Date ordering stays authoritative over title demotion (main 2026-10-25):
    a NEWER demoted rider still outranks an OLDER strong match; equal dates keep
    the demoted order."""

    class FakeConn:
        def __init__(self, sid, hits): self.id = sid; self.hits = hits
        def search(self, q, k, documents=None, recent=False):
            return [dict(e) for e in self.hits][:k]

    def make_engine(self, hits):
        cfg = {"app": {"title": "T", "tagline": ""}, "provider": {"type": "mock"},
               "sources": [{"id": "pubmed", "type": "pubmed", "label": "PubMed"}],
               "retrieval": {"top_k": 6, "min_score": 0.0, "cache_ttl": 0},
               "memory": {"enabled": False}, "permissions": {}, "pipeline_prompts": {}}
        eng = Engine(cfg, Store(":memory:"))
        eng.connectors["pubmed"] = self.FakeConn("pubmed", hits)
        return eng

    def test_newer_rider_keeps_date_priority(self):
        old_strong = ev(1, "CAR T-cell therapy for B-cell lymphoma",
                        "CAR-T cell therapy trials in B-cell lymphoma: main findings. " * 5, year="2024")
        old_strong2 = ev(2, "Axicabtagene ciloleucel CAR T-cell therapy in refractory large B-cell lymphoma",
                         "CAR-T cell therapy trials in refractory large B-cell lymphoma: main findings. " * 5, year="2024")
        new_rider = ev(3, "B-cell acute lymphoblastic leukemia immunotherapy: a review",
                       "This review discusses CAR-T cell therapy and trials; findings in lymphoma and leukemia. " * 5, year="2026")
        eng = self.make_engine([old_strong, old_strong2, new_rider])
        found, _ = eng.retrieve("most recent trials of CAR-T cell therapy lymphoma", owner="visitor:t")
        self.assertEqual(found[0]["title"], new_rider["title"])  # date wins
        self.assertTrue(found[0].get("_demoted"))                # but the rider is LABELED
        # ...and the preview names it by marker even though it leads the list
        self.assertIn("[1] matched the question only loosely",
                      Engine.fallback_answer(found, question="most recent trials of CAR-T cell therapy lymphoma"))

    def test_equal_dates_keep_demote_order(self):
        strong = ev(1, "CAR T-cell therapy for B-cell lymphoma",
                    "CAR-T cell therapy trials in B-cell lymphoma: main findings. " * 5, year="2026")
        strong2 = ev(2, "Axicabtagene ciloleucel CAR T-cell therapy in refractory large B-cell lymphoma",
                     "CAR-T cell therapy trials in refractory large B-cell lymphoma: main findings. " * 5, year="2025")
        rider = ev(3, "B-cell acute lymphoblastic leukemia immunotherapy: a review",
                   "This review discusses CAR-T cell therapy and trials; findings in lymphoma and leukemia. " * 5, year="2026")
        eng = self.make_engine([rider, strong, strong2])
        found, _ = eng.retrieve("most recent trials of CAR-T cell therapy lymphoma", owner="visitor:t")
        self.assertEqual(found[0]["title"], strong["title"])     # equal year: strong first
        self.assertEqual(found[1]["title"], rider["title"])
        self.assertTrue(found[1].get("_demoted"))


if __name__ == "__main__":
    unittest.main()
