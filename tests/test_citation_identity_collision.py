"""Identifier provenance only. These tests make no semantic-support claim."""
import copy
import unittest
from unittest.mock import Mock
from chatify import schema
from chatify.store import Store
from chatify.pipeline import Engine

class CitationIdentityCollision(unittest.TestCase):
    def evidence(self):
        return [{'n': 2, 'id': 'real-study', 'source': 'docs', 'title': 'Wing study',
                 'text': 'Formula One wings generate downforce.', 'year': '2026',
                 'url': 'fixture:real-study'}]

    def test_unknown_id_cannot_become_valid_when_real_id_is_compacted(self):
        evidence = self.evidence()
        original = copy.deepcopy(evidence)
        answer, selected = Engine.tidy('Invented claim. [1] Wings generate downforce. [2]', evidence)
        rows = Engine.ledger(answer, selected)
        self.assertEqual(rows[0]['invalid'], [1])
        self.assertFalse(rows[0]['supported'])
        self.assertEqual(rows[1]['cites'], [2])
        self.assertEqual(selected[0]['id'], 'real-study')
        self.assertEqual(selected[0]['n'], 2)
        self.assertEqual(evidence, original)

    def test_repeated_tidy_never_launders_unknown_id(self):
        answer, selected = 'Invented claim. [1] Wings generate downforce. [2]', self.evidence()
        for _ in range(3):
            answer, selected = Engine.tidy(answer, selected)
            self.assertEqual(Engine.ledger(answer, selected)[0]['invalid'], [1])
            self.assertEqual(selected[0]['n'], 2)

    def test_grouped_or_ranged_ids_preserve_invalid_members(self):
        for citations in ('[1,2]', '[1-2]', '[1] [2]'):
            with self.subTest(citations=citations):
                answer, selected = Engine.tidy('Wings generate downforce. ' + citations, self.evidence())
                row = Engine.ledger(answer, selected)[0]
                self.assertEqual(row['invalid'], [1])
                self.assertEqual(row['cites'], [2])
                self.assertFalse(row['supported'])

    def test_valid_only_citations_still_compact_in_order_of_use(self):
        evidence = self.evidence() + [{'n': 5, 'id': 'other', 'title': 'Other', 'text': 'Other fact.'}]
        answer, selected = Engine.tidy('Other fact. [5] Wings generate downforce. [2]', evidence)
        self.assertEqual(answer, 'Other fact. [1] Wings generate downforce. [2]')
        self.assertEqual([(e['n'], e['id']) for e in selected], [(1, 'other'), (2, 'real-study')])

    def test_sync_and_stream_withhold_unrepaired_unknown_citation(self):
        # Relevance filtering can leave a gap in retrieved citation numbers.
        # The remaining [2] must not give an invented [1] a real source.
        draft = 'Invented claim. [1] Wings generate downforce. [2]'
        for stream in (False, True):
            with self.subTest(stream=stream):
                cfg = schema.validate({'provider': {'type': 'openai', 'model': 'gpt-4o-mini'},
                                       'sources': [], 'memory': {'enabled': False}})
                engine = Engine(cfg, Store(':memory:'))
                engine.retrieve = lambda *a, **k: (self.evidence(), {})
                engine._llm_on = lambda key: False
                engine.followups = lambda *a, **k: []
                engine.provider.complete = Mock(return_value=draft)
                engine.provider.stream = Mock(return_value=iter([draft]))
                chat = engine.store.new_chat('owner')
                result = (list(engine.ask_stream('owner', chat, 'Explain wings.'))[-1][1]
                          if stream else engine.ask('owner', chat, 'Explain wings.'))
                saved = engine.store.turn('owner', result['id'])
                for turn in (result, saved):
                    self.assertEqual(turn['ledger'], [])
                    self.assertNotIn('Invented claim.', turn['answer'])
                    self.assertIn('No recommendation is provided', turn['answer'])
                    self.assertIn('unsupported answer was withheld', turn['answer'])
                    self.assertEqual(turn['evidence'][0]['id'], 'real-study')
                    self.assertEqual(turn['evidence'][0]['n'], 2)
                self.assertFalse(result['answer_verified'])

    def test_all_invalid_citations_do_not_create_sources(self):
        answer, selected = Engine.tidy('Invented claim. [1]', self.evidence())
        self.assertEqual(selected, [])
        self.assertEqual(Engine.ledger(answer, selected)[0]['invalid'], [1])

if __name__ == '__main__':
    unittest.main()
