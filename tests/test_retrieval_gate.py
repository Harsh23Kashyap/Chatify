import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from chatify.pipeline import relevance_gate, _gate_stems, _NO_KEY_WHY, Engine
from chatify import providers


def ev(n, title, text):
    return {"n": n, "title": title, "text": text, "score": 1.0 / n, "id": str(n), "source": "wikipedia"}


class Gate(unittest.TestCase):
    Q = "How often should I water tomatoes on a balcony - and what do deep watering and drainage really mean?"
    # The exact irrelevant citation set the live demo returned for Q before this fix.
    JUNK = [ev(1, "Halloween (franchise)", "Halloween is an American slasher media franchise that consists of thirteen films."),
            ev(2, "Vanilla Ice", "Robert Matthew Van Winkle, known professionally as Vanilla Ice, is a rapper."),
            ev(3, "Elite (TV series)", "Elite is a Spanish teen drama series created for Netflix."),
            ev(4, "West Side Story (2021 film)", "West Side Story is a 2021 American musical romantic drama film.")]
    GOOD = ev(5, "Gardening in restricted spaces",
              "Restricted space gardens can be located on small lawns, balconies, patios, porches, rooftops, inside the home, and watering and drainage need attention in containers.")

    def test_irrelevant_popular_pages_dropped(self):
        out = relevance_gate(self.Q, self.JUNK + [self.GOOD])
        self.assertEqual([e["title"] for e in out], ["Gardening in restricted spaces"])

    def test_all_irrelevant_returns_empty_for_clarify(self):
        self.assertEqual(relevance_gate(self.Q, self.JUNK), [])

    def test_single_shared_word_is_a_mention_not_a_match(self):
        weak_only = ev(6, "Permanente Quarry", "The Permanente Quarry is a limestone quarry and cement plant in California.")
        self.assertEqual(relevance_gate("How do I prune a money plant and when is the best season?", [weak_only]), [])

    def test_no_question_words_passes_through(self):
        self.assertEqual(relevance_gate("???", self.JUNK), self.JUNK)
        self.assertEqual(relevance_gate(self.Q, []), [])

    def test_relative_floor_keeps_strong_drops_weak(self):
        q = "What is a good weekly strength training routine for beginners?"
        strong = ev(1, "Strength training", "Strength training or resistance training is the performance of physical exercises designed to improve strength; beginners often follow a weekly routine.")
        weak = ev(2, "Shinmai Fukei Kiruko-san", "A weekly manga series about a former soldier.")
        titles = [e["title"] for e in relevance_gate(q, [strong, weak])]
        self.assertIn("Strength training", titles)
        self.assertNotIn("Shinmai Fukei Kiruko-san", titles)

    def test_variant_stemming_matches_inflections(self):
        s = _gate_stems("watering the tomatoes on balconies")
        self.assertIn("water", s)
        self.assertIn("tomato", s)
        self.assertIn("balcony", s)


class QueryWords(unittest.TestCase):
    def test_short_query_drops_question_words(self):
        eng = Engine.__new__(Engine)
        eng.cfg = {"retrieval": {}, "provider": {"type": "mock"}, "sources": [{"type": "wikipedia"}]}
        qs = eng.queries("How often should I water tomatoes on a balcony - and what do deep watering and drainage really mean?")
        self.assertEqual(qs[0], "How often should I water tomatoes on a balcony - and what do deep watering and drainage really mean?")
        # Query ladder: raw question + focused content-word windows (6, 3, 2).
        self.assertLessEqual(len(qs), 4)
        self.assertEqual(len(qs), len(set(q.lower() for q in qs)))
        words = qs[1].lower().split()
        for w in ("how", "often", "should", "i", "really", "mean"):
            self.assertNotIn(w, words)
        for w in ("water", "tomatoes", "balcony", "drainage"):
            self.assertIn(w, words)
        self.assertEqual(qs[1].lower().split(), "water tomatoes balcony deep watering drainage".split())


class FallbackWording(unittest.TestCase):
    def test_default_is_labeled_source_preview(self):
        a = Engine.fallback_answer([{"n": 1, "text": "A refund passage."}])
        self.assertIn("source preview, not a model answer", a)
        self.assertIn("could not be reached", a)

    def test_missing_key_wording_points_to_configuration(self):
        a = Engine.fallback_answer([{"n": 1, "text": "A refund passage."}], why=_NO_KEY_WHY)
        self.assertIn("no API key saved yet", a)
        self.assertIn("Configuration", a)
        self.assertIn("not a model answer", a)

    def test_no_key_error_shape(self):
        e = providers.ProviderError("No API key yet. Paste one under Model, Save key, or set the OPENAI_API_KEY environment variable.", 401)
        self.assertTrue(str(e).startswith("No API key yet"))
        self.assertEqual(e.code, 401)


if __name__ == "__main__":
    unittest.main()


class QueryLadder(unittest.TestCase):
    def engine(self):
        from chatify.store import Store
        from chatify import schema
        cfg = schema.validate({'sources': [{'id': 'wikipedia', 'type': 'wikipedia', 'label': 'Wikipedia', 'lang': 'en'}]})
        return Engine(cfg, Store(':memory:'))

    def test_ladder_emits_focused_heads(self):
        # Regression for the 2026-10-24 live recall hole: "How long does a vegetable
        # stir fry take on a weeknight?" only searched the raw question and a noisy
        # 6-word window, both of which Wikipedia answers with popular junk; the
        # content-word head "vegetable stir fry" finds "Stir frying".
        qs = self.engine().queries("How long does a vegetable stir fry take on a weeknight?")
        self.assertEqual(qs[0], "How long does a vegetable stir fry take on a weeknight?")
        self.assertIn("vegetable stir fry", qs)
        self.assertIn("vegetable stir", qs)
        self.assertLessEqual(len(qs), 4)
        self.assertNotIn("weeknight", " ".join(qs[1:]))

    def test_ladder_dedups_and_keeps_raw_first(self):
        qs = self.engine().queries("Tomato?")
        self.assertEqual(qs[0], "Tomato?")
        self.assertEqual(len(qs), len(set(q.lower() for q in qs)))

    def test_no_search_sources_keeps_single_query(self):
        from chatify.store import Store
        from chatify import schema
        cfg = schema.validate({'sources': [{'id': 'docs', 'type': 'local_files', 'label': 'Docs', 'path': 'docs'}]})
        e = Engine(cfg, Store(':memory:'))
        self.assertEqual(e.queries("How long does a stir fry take?"), ["How long does a stir fry take?"])

    def test_gate_keeps_stir_frying_for_stir_fry_question(self):
        q = "How long does a vegetable stir fry take on a weeknight?"
        good = ev(1, "Stir frying", "Stir frying is a Chinese cooking technique in which vegetables are fried in a small amount of very hot oil while being stirred in a wok.")
        junk = ev(2, "List of America's Test Kitchen episodes", "Episodes of an American cooking show.")
        out = relevance_gate(q, [junk, good])
        self.assertEqual([e["title"] for e in out], ["Stir frying"])

class QuestionCheckNoKey(unittest.TestCase):
    def engine(self):
        from chatify.store import Store
        from chatify import schema
        cfg = schema.validate({'sources': [{'id': 'wikipedia', 'type': 'wikipedia', 'label': 'Wikipedia', 'lang': 'en'}],
                               'provider': {'type': 'openai', 'model': 'gpt-4o-mini', 'api_key_env': 'CC_TEST_MISSING_KEY_ENV'}})
        e = Engine(cfg, Store(':memory:'))
        e.prompts._d = {'on': {'question_check': True}, 'text': {}}
        return e

    def test_no_key_skips_stage_instead_of_blocking_turn(self):
        # Regression for 2026-10-24 live failure: a no-key app with question_check
        # enabled answered EVERY question with "No evidence found" because the
        # stage's ProviderError became a blocking message before retrieval ran.
        self.assertEqual(self.engine().check_question("How long does a vegetable stir fry take?"), "")

    def test_other_provider_errors_still_surface(self):
        e = self.engine()
        def boom(messages):
            raise providers.ProviderError("model overloaded", 500)
        e.provider.complete = boom
        self.assertIn("could not be completed", e.check_question("q"))


class MultilingualAndNumericGate(unittest.TestCase):
    """Live demo 2026-10-25: a Hindi lunch question with "₹200" was answered with
    MRSA child-care, sinus surgery and PHACE papers as "most relevant passages".
    Two escapes made it possible: "200" counted as topical vocabulary and matched
    the abstracts' numbers, and non-Latin question text gave the gate no readable
    stems, so everything passed through."""

    JUNK = [ev(1, "MRSA in child care centers", "Children attending child care centers are at increased risk for infections; nasal colonization preceded infection in 200 children."),
            ev(2, "Failed endoscopic sinus surgery", "Functional endoscopic sinus surgery is performed 200,000 times annually in the United States."),
            ev(3, "PHACE syndrome review", "More than 200 cases have been reported of PHACE syndrome.")]

    def test_numbers_alone_never_establish_topical_overlap(self):
        q = "What healthy lunch can I cook in 200 rupees?"
        self.assertEqual(relevance_gate(q, self.JUNK), [])

    def test_mixed_hindi_english_question_gated_on_english_only(self):
        q = "सप्ताह के दिनों के lunch के लिए कौन से आसान व्यंजन अच्छे हैं? ₹200 में क्या बन सकता है?"
        self.assertEqual(relevance_gate(q, self.JUNK), [])
        good = ev(4, "Lunch meal planning", "Weekday lunch planning on a budget: simple lunch dishes and approximate costs.")
        self.assertEqual([e["title"] for e in relevance_gate(q, self.JUNK + [good])], ["Lunch meal planning"])

    def test_pure_non_latin_question_cannot_pass_everything_through(self):
        self.assertEqual(relevance_gate("कौन से आसान व्यंजन अच्छे हैं?", self.JUNK), [])

    def test_punctuation_only_question_still_passes_through(self):
        # No lexical content at all: the pre-existing behavior for "???".
        self.assertEqual(len(relevance_gate("???", self.JUNK)), 3)

    def test_digit_tokens_are_not_gate_stems(self):
        self.assertNotIn("200", _gate_stems("200 rupees 100 grams"))
        self.assertIn("rupees", _gate_stems("200 rupees"))


class EnglishSpecificityGate(unittest.TestCase):
    """Live demo 2026-10-25, English edition of the shallow-gate defect: an
    AI-trial-design paper was cited for a CAR-T lymphoma question and a
    statistical-physics umbrella-sampling paper for a diffusion-sampling
    question. Generic academic words (recent/main/methods) and variant
    double-counting let a single shared word pass the floor."""

    CART_Q = "What are the main findings of recent trials on CAR-T cell therapy in lymphoma?"
    B_ALL = ev(1, "Immunotherapy in B-Cell Acute Lymphoblastic Leukemia", "In recent years, immunotherapy has been increasingly incorporated into the clinical care of both pediatric and adult patients with B-cell acute lymphoblastic leukemia (B-ALL) to improve outcomes. Four main categories of immunotherapies are used in B-ALL.")
    CRC = ev(2, "Immunotherapy for colorectal cancer", "Colorectal cancer is the third most common cancer and the second most lethal cancer in the world. The treatment of this complex disease is mainly based on traditional treatments, including surgery, radiotherapy, and chemotherapy.")
    AI_TRIAL = ev(3, "Artificial Intelligence for Clinical Trial Design", "Clinical trials consume the latter half of the 10 to 15 year development cycle for bringing a single new drug to market. Hence, a failed trial sinks the investment into the trial itself.")
    CART_REAL = ev(4, "CAR-T cell therapy in relapsed lymphoma: trial results", "Recent trials of CAR-T cell therapy in lymphoma report durable remissions. We review the main findings across pivotal trials of CAR-T cell therapy in relapsed and refractory lymphoma.")

    def test_generic_overlap_alone_is_not_evidence(self):
        self.assertEqual(relevance_gate(self.CART_Q, [self.B_ALL, self.CRC, self.AI_TRIAL]), [])

    def test_real_cart_evidence_kept_broad_papers_dropped(self):
        out = relevance_gate(self.CART_Q, [self.B_ALL, self.CRC, self.AI_TRIAL, self.CART_REAL])
        self.assertEqual([e["title"] for e in out], ["CAR-T cell therapy in relapsed lymphoma: trial results"])

    def test_one_shared_word_counts_once_despite_inflections(self):
        # "trials" matching "trials" is one shared word, not trial+trials.
        out = relevance_gate(self.CART_Q, [self.AI_TRIAL])
        self.assertEqual(out, [])

    def test_same_word_family_different_field_dropped(self):
        q = "What sampling methods improve diffusion model image quality?"
        survey = ev(5, "Text-to-image Diffusion Models in Generative AI: A Survey", "This survey reviews the progress of diffusion models in generating images from text, i.e. text-to-image diffusion models, and how diffusion models work for image synthesis.")
        umbrella = ev(6, "Umbrella sampling: a powerful method to sample tails of distributions", "We present the umbrella sampling (US) technique and show that it can be used to sample extremely low probability areas of the posterior distribution required in statistical analyses of data.")
        self.assertEqual([e["title"] for e in relevance_gate(q, [survey, umbrella])], ["Text-to-image Diffusion Models in Generative AI: A Survey"])

    def test_most_on_question_passage_leads(self):
        # Live demo 2026-10-25: retrieval order led the preview with a broad
        # review whose excerpt did not establish the asked trial findings.
        out = relevance_gate(self.CART_Q, [self.B_ALL, self.CRC, self.AI_TRIAL, self.CART_REAL])
        self.assertTrue(out[0]["title"].startswith("CAR-T cell therapy in relapsed lymphoma"))


class RetrieveOrdering(unittest.TestCase):
    """End-to-end ordering through Engine.retrieve: the gate's most-on-question-first
    order must survive to the answer (live demo 2026-10-25: a blanket score re-sort
    after the gate put the Holy Roman Empire lead above Gibbon's Decline and Fall
    for "main causes of the fall of the Roman Empire")."""

    Q = "What were the main causes of the fall of the Roman Empire?"
    HOLY = {"id": "1", "title": "Holy Roman Empire", "source": "w", "score": 0.95, "url": "u1",
            "authors": [], "year": "", "venue": "",
            "text": "The Holy Roman Empire was a polity comprising much of Central Europe and Western Europe, headed by the Holy Roman Emperor and characterized by a decentralized political structure."}
    GIBBON = {"id": "3", "title": "The History of the Decline and Fall of the Roman Empire", "source": "w", "score": 0.5, "url": "u3",
              "authors": [], "year": "", "venue": "",
              "text": "The History of the Decline and Fall of the Roman Empire is a six-volume work by the English historian Edward Gibbon covering the peak and fall of the Roman Empire."}

    def _engine(self, sources, connectors):
        from chatify import schema
        from chatify.store import Store
        import os
        app = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps", "minimal", "app.yaml")
        cfg = schema.load(app)
        cfg["sources"] = sources
        cfg["retrieval"]["min_score"] = 0.0
        cfg["retrieval"]["cache_ttl"] = 0
        e = Engine(cfg, Store(":memory:"))
        e.connectors = connectors
        return e

    def test_pure_search_keeps_gate_order(self):
        class W:
            def search(self, q, k):
                return [dict(RetrieveOrdering.HOLY), dict(RetrieveOrdering.GIBBON)]
        e = self._engine([{"id": "w", "type": "wikipedia", "label": "W"}], {"w": W()})
        found, _ = e.retrieve(self.Q)
        self.assertEqual([f["title"] for f in found],
                         ["The History of the Decline and Fall of the Roman Empire", "Holy Roman Empire"])

    def test_mixed_corpus_keeps_score_order(self):
        own_hit = {"id": "9", "title": "Owner notes on Rome", "source": "loc", "score": 0.99, "url": "u9",
                   "authors": [], "year": "", "venue": "", "text": "My notes on the fall of the Roman Empire and its causes."}
        class W:
            def search(self, q, k):
                return [dict(RetrieveOrdering.HOLY), dict(RetrieveOrdering.GIBBON)]
        class L:
            def search(self, q, k):
                return [own_hit]
        e = self._engine([{"id": "w", "type": "wikipedia", "label": "W"}, {"id": "loc", "type": "local_files", "label": "L"}],
                         {"w": W(), "loc": L()})
        found, _ = e.retrieve(self.Q)
        self.assertEqual(found[0]["title"], "Owner notes on Rome")
