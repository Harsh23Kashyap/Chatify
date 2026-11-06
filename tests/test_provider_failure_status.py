"""Offline transport-status regression tests, not answer-quality certification."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from chatify import providers, schema
from chatify.pipeline import Engine
from chatify.store import Store

EVIDENCE = [{'n': 1, 'title': 'Wing study', 'text': 'Formula One wings generate downforce.',
             'year': '', 'source': 'docs', 'url': 'fixture:source'}]

class ProviderFailureStatus(unittest.TestCase):
    def engine(self, store=None):
        cfg = schema.validate({'provider': {'type': 'openai', 'model': 'gpt-4o-mini'},
                               'memory': {'enabled': False}, 'prompt': {'model_followups': False},
                               'retrieval': {'query_expansion': False}})
        engine = Engine(cfg, store or Store(':memory:'))
        engine.retrieve = lambda *a, **k: (EVIDENCE, {})
        engine._llm_on = lambda key: False
        engine.followups = lambda *a, **k: []
        return engine

    def run_failure(self, stream, message, partial=''):
        engine = self.engine()
        calls = []
        class FailedProvider:
            def complete(self, messages):
                calls.append('complete')
                raise providers.ProviderError(message)
            def stream(self, messages):
                calls.append('stream')
                if partial:
                    yield partial
                raise providers.ProviderError(message)
        engine.provider = FailedProvider()
        chat = engine.store.new_chat('owner')
        result = (list(engine.ask_stream('owner', chat, 'Explain Formula One wings.'))[-1][1]
                  if stream else engine.ask('owner', chat, 'Explain Formula One wings.'))
        return engine, result, calls

    def test_sync_and_stream_report_and_save_failure_status(self):
        for stream in (False, True):
            for message, expected in [('No API key yet: configure the provider', 'no_key'),
                                      ('Connection timed out', 'unreachable')]:
                with self.subTest(stream=stream, expected=expected):
                    engine, result, calls = self.run_failure(stream, message)
                    self.assertEqual(result['model_status'], expected)
                    self.assertEqual(engine.store.turn('owner', result['id'])['model_status'], expected)
                    self.assertEqual(len(calls), 2)  # existing retry budget, not a new policy
                    self.assertFalse(result['answer_verified'])
                    self.assertIn('source preview, not a model answer', result['answer'])

    def test_partial_stream_is_cut_and_never_retried(self):
        engine, result, calls = self.run_failure(True, 'Connection timed out', 'Partial draft [1]')
        self.assertEqual(result['model_status'], 'cut')
        self.assertEqual(engine.store.turn('owner', result['id'])['model_status'], 'cut')
        self.assertEqual(len(calls), 1)
        self.assertIn('cut short', result['answer'])

    def test_successful_sync_retry_is_ok_not_failed(self):
        engine = self.engine()
        engine.provider.complete = Mock(side_effect=[providers.ProviderError('temporary failure'),
                                                      'Formula One wings generate downforce. [1]'])
        result = engine.ask('owner', engine.store.new_chat('owner'), 'Explain Formula One wings.')
        self.assertEqual(result['model_status'], 'ok')
        self.assertEqual(engine.store.turn('owner', result['id'])['model_status'], 'ok')
        self.assertEqual(engine.provider.complete.call_count, 2)
        self.assertFalse(result['answer_verified'])

    def test_failure_status_survives_disk_reopen_branch_and_portable_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'history.db')
            engine = self.engine(Store(path))
            engine.provider.complete = Mock(side_effect=providers.ProviderError('Connection timed out'))
            chat = engine.store.new_chat('owner')
            result = engine.ask('owner', chat, 'Explain Formula One wings.')
            reopened = Store(path)
            saved = reopened.turn('owner', result['id'])
            self.assertEqual(saved['model_status'], 'unreachable')
            target = reopened.add_turn(chat, None, 'Branch target', '', 'Target', [], [], 'standard')
            branch = reopened.branch('owner', target, 'Followup')
            self.assertEqual(reopened.turns('owner', branch['chat'])[0]['model_status'], 'unreachable')
            payload = json.loads(json.dumps(reopened.export_all('owner')))
            imported = Store(':memory:')
            imported.import_chats('other', payload)
            turn = imported.export_all('other')[0]['turns'][0]
            self.assertEqual(turn['model_status'], 'unreachable')
            self.assertEqual(turn['answer'], saved['answer'])

if __name__ == '__main__':
    unittest.main()
