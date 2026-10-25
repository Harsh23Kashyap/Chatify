import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chatify.pipeline import relevance_gate


def ev(n, title, text):
    return {"n": n, "title": title, "text": text, "score": 1.0 / n, "id": str(n), "source": "pubmed"}


# Hosted R2 2026-10-25 residual: for "most recent papers on GLP-1 dosing safety"
# the gate kept a pharmacy-students knowledge paper (human-factors genre) beside
# genuine dosing/safety findings.
Q2 = "most recent papers on GLP-1 dosing safety"
GENUINE1 = ev(1, "Efsubaglutide alfa, a long-acting GLP-1 receptor agonist: exposure-response dosing review",
              "GLP-1 dosing safety findings. Dosing was escalated; safety and tolerability recorded. " * 4)
GENUINE2 = ev(2, "Elecoglipron phase 1 pharmacokinetics, fed/fasted dosing, safety and tolerability",
              "GLP-1 dosing safety findings from a phase 1 trial. Dosing cohorts; safety endpoints. " * 4)
RIDER = ev(3, "Pharmacy students' knowledge of GLP-1 receptor agonist adverse effects",
           "GLP-1 dosing safety knowledge among pharmacy students was assessed; dosing safety awareness surveyed. " * 4)


class WebRootNormalization(unittest.TestCase):
    def test_web_root_is_normalized(self):
        # 2026-10-25: an unnormalized sys.path entry ('tests/..', inserted by gate
        # test modules) made chatify.server import with '..' in __file__; WEB then
        # carried '..' and _static's traversal guard compared a normalized full
        # path against the unnormalized WEB prefix - every page 404'd while APIs
        # stayed up. WEB must be normalized at import.
        import os
        from chatify import server
        self.assertEqual(server.WEB, os.path.normpath(server.WEB))
        self.assertTrue(os.path.isfile(os.path.join(server.WEB, "index.html")))


class GenreGate(unittest.TestCase):
    def test_findings_question_drops_genre_rider(self):
        out = relevance_gate(Q2, [GENUINE1, RIDER, GENUINE2])
        titles = [e["title"] for e in out]
        self.assertFalse(any("Pharmacy students" in t for t in titles), titles)
        self.assertTrue(any("Efsubaglutide" in t for t in titles), titles)
        self.assertTrue(any("Elecoglipron" in t for t in titles), titles)

    def test_single_mismatch_drops_to_honest_empty(self):
        # A known mismatch must not be shown as apparently relevant evidence:
        # dropping to empty yields the honest no-evidence reply instead.
        self.assertEqual(relevance_gate(Q2, [RIDER]), [])

    def test_strongest_overlap_mismatch_still_drops(self):
        out = relevance_gate(Q2, [RIDER, GENUINE1])
        self.assertEqual([e["title"] for e in out if "Pharmacy" in e["title"]], [])

    def test_genre_question_keeps_genre_papers(self):
        q = "how much do pharmacy students know about GLP-1 adverse effects"
        out = relevance_gate(q, [RIDER])
        self.assertEqual([e["title"] for e in out], [RIDER["title"]])

    def test_training_question_deactivates_rule(self):
        q = "GLP-1 safety training for pharmacists"
        out = relevance_gate(q, [RIDER])
        self.assertEqual([e["title"] for e in out], [RIDER["title"]])

    def test_statistical_confidence_title_untouched(self):
        ci = ev(4, "Confidence intervals in GLP-1 dosing trials: a simulation study",
                "GLP-1 dosing safety trial simulation; dosing safety intervals computed. " * 4)
        out = relevance_gate(Q2, [ci])
        self.assertEqual([e["title"] for e in out], [ci["title"]])


# ISSUE-10 residual: same-disease/different-intervention - a glofitamab paper
# whose CAR-T mentions are all post-treatment references led a CAR-T question.
QCART = "recent trials of CAR-T cell therapy in DLBCL lymphoma"
ZUMA = ev(1, "Axicabtagene ciloleucel CAR T-cell therapy in refractory large B-cell lymphoma",
          "CAR-T cell therapy was given to patients with DLBCL lymphoma; trials report durable responses. " * 4)
GLOF = ev(2, "Glofitamab for relapsed or refractory DLBCL after CAR-T failure",
          "Patients with DLBCL lymphoma whose disease progressed after CAR-T failure received glofitamab. "
          "Outcomes after CAR-T failure remain poor. " * 3)


class PostAnchorGate(unittest.TestCase):
    def test_post_anchor_reference_dropped(self):
        out = relevance_gate(QCART, [ZUMA, GLOF])
        titles = [e["title"] for e in out]
        self.assertFalse(any("Glofitamab" in t for t in titles), titles)
        self.assertTrue(any("Axicabtagene" in t for t in titles), titles)

    def test_subject_anchor_kept(self):
        out = relevance_gate(QCART, [ZUMA])
        self.assertEqual([e["title"] for e in out], [ZUMA["title"]])

    def test_failure_question_keeps_post_anchor_paper(self):
        q = "what works for DLBCL after CAR-T failure or relapse"
        out = relevance_gate(q, [GLOF])
        self.assertEqual([e["title"] for e in out], [GLOF["title"]])


if __name__ == "__main__":
    unittest.main()
