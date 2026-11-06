"""Offline retrieval ownership and partial-query contracts, not semantic quality."""
import copy
import unittest
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
from chatify.connectors.base import Evidence
from chatify.connectors.open_sources import SetupRequired

class RetrievalTransactionIsolation(unittest.TestCase):
    def row(self):
        row = Evidence('Wings generate downforce', 'Wings generate downforce in Formula One racing.',
                       source='fixture', score=1, id='row', url='fixture:row')
        row['metadata'] = {'tags': ['original']}
        return row

    def engine(self, connector):
        cfg = schema.validate({'provider': {'type': 'mock'},
                               'sources': [{'id': 'fixture', 'type': 'pubmed', 'weight': 2}],
                               'retrieval': {'query_expansion': False, 'rerank': False, 'cache_ttl': 0}})
        engine = Engine(cfg, Store(':memory:'), connectors={'fixture': connector})
        engine.queries = lambda question: [question]
        return engine

    def test_connector_owned_records_are_never_mutated_or_reweighted(self):
        row = self.row()
        original = copy.deepcopy(row)
        class Shared:
            def search(self, question, k): return [row]
        engine = self.engine(Shared())
        first, _ = engine.retrieve('wings downforce')
        second, _ = engine.retrieve('Formula One wings downforce')
        self.assertEqual(row, original)
        self.assertEqual(first[0]['score'], 2)
        self.assertEqual(second[0]['score'], 2)
        self.assertIsNot(first[0], second[0])

    def test_duplicate_shared_rows_are_weighted_once_before_deduplication(self):
        row = self.row()
        class Duplicate:
            def search(self, question, k): return [row, row]
        engine = self.engine(Duplicate())
        found, errors = engine.retrieve('wings downforce')
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['score'], 2)
        self.assertEqual(row['score'], 1)
        self.assertEqual(errors, {})

    def test_returned_evidence_and_errors_cannot_mutate_memory_cache(self):
        row = self.row()
        class Shared:
            calls = 0
            def search(self, question, k):
                self.calls += 1
                return [row]
        conn = Shared()
        engine = self.engine(conn)
        first, errors = engine.retrieve('wings downforce')
        first[0]['n'] = 99
        first[0]['text'] = 'caller overwrite'
        first[0]['metadata']['tags'].append('caller')
        errors['invented'] = 'caller'
        second, errors = engine.retrieve('wings downforce')
        self.assertEqual(second[0]['n'], 1)
        self.assertEqual(second[0]['text'], row['text'])
        self.assertEqual(second[0]['metadata']['tags'], ['original'])
        self.assertEqual(errors, {})
        self.assertEqual(conn.calls, 1)

    def test_success_before_failure_kept_and_setup_error_reported(self):
        row = self.row()
        calls = []
        class Partial:
            def search(self, question, k):
                calls.append(question)
                if question == 'broken': raise SetupRequired('Fixture needs source setup')
                return [row]
        engine = self.engine(Partial())
        engine.queries = lambda question: ['wings downforce', 'broken', 'not attempted']
        found, errors = engine.retrieve('wings downforce')
        self.assertEqual([e['id'] for e in found], ['row'])
        self.assertEqual(errors, {'fixture': 'Partial search; earlier query results retained: Fixture needs source setup'})
        self.assertEqual(calls, ['wings downforce', 'broken'])

    def test_generic_partial_failure_does_not_expose_exception_body(self):
        row = self.row()
        class Partial:
            def search(self, question, k):
                if question == 'broken': raise RuntimeError('private fixture marker')
                return [row]
        engine = self.engine(Partial())
        engine.queries = lambda question: ['wings downforce', 'broken']
        found, errors = engine.retrieve('wings downforce')
        self.assertEqual(len(found), 1)
        self.assertEqual(errors, {'fixture': 'Partial search; earlier query results retained: RuntimeError'})
        self.assertNotIn('private fixture marker', str((found, errors)))

    def test_partial_status_and_evidence_survive_sync_stream_and_saved_turn(self):
        row = self.row()
        class Partial:
            def search(self, question, k):
                if question == 'broken': raise RuntimeError('private fixture marker')
                return [row]
        for stream in (False, True):
            with self.subTest(stream=stream):
                engine = self.engine(Partial())
                engine.cfg['memory']['enabled'] = False
                engine.queries = lambda question: ['wings downforce', 'broken']
                chat = engine.store.new_chat('owner')
                result = (list(engine.ask_stream('owner', chat, 'Explain wings downforce.'))[-1][1]
                          if stream else engine.ask('owner', chat, 'Explain wings downforce.'))
                for turn in (result, engine.store.turn('owner', result['id'])):
                    self.assertEqual(turn['evidence'][0]['id'], 'row')
                    self.assertEqual(turn['source_errors'], {'fixture': 'Partial search; earlier query results retained: RuntimeError'})
                self.assertFalse(result['answer_verified'])

    def test_first_query_failure_stays_empty_without_additional_queries(self):
        calls = []
        class Failed:
            def search(self, question, k):
                calls.append(question)
                raise RuntimeError('private fixture marker')
        engine = self.engine(Failed())
        engine.queries = lambda question: ['broken', 'not attempted']
        found, errors = engine.retrieve('wings downforce')
        self.assertEqual(found, [])
        self.assertEqual(errors, {'fixture': 'RuntimeError'})
        self.assertEqual(calls, ['broken'])

if __name__ == '__main__': unittest.main()
