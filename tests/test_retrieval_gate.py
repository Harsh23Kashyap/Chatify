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
