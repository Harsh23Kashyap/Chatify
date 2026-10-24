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
        self.assertEqual(len(qs), 2)
        words = qs[1].lower().split()
        for w in ("how", "often", "should", "i", "really", "mean"):
            self.assertNotIn(w, words)
        for w in ("water", "tomatoes", "balcony", "drainage"):
            self.assertIn(w, words)


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
