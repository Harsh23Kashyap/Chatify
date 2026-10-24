import os, sys, unittest, yaml
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from chatify import apiterms, appbuilder

class Catalog(unittest.TestCase):
    def test_known_service_gets_verified_terms_and_docs(self):
        s = apiterms.attach({'service': 'OpenAlex', 'docs_url': 'https://invented.example/x', 'key_url': 'https://invented.example/key'})
        self.assertIn('free', s['terms'].lower())
        self.assertEqual(s['docs_url'], 'https://docs.openalex.org/how-to-use-the-api/api-overview')
        self.assertEqual(s['terms_source'], s['docs_url'])
        self.assertTrue(s['terms_verified'])
        self.assertNotIn('invented.example', str(s))
    def test_unknown_service_gets_honest_note_not_invented_terms(self):
        s = apiterms.attach({'name': 'Some Random API'})
        self.assertIn('not verified', s['terms'])
        self.assertNotIn('terms_source', s)
        self.assertNotIn('terms_verified', s)
    def test_every_catalog_entry_carries_source_and_docs(self):
        for keys, entry in apiterms.CATALOG:
            self.assertTrue(entry['docs_url'].startswith('https://'), keys)
            self.assertTrue(entry['source'].startswith('https://'), keys)
            self.assertTrue(entry['terms'].strip(), keys)

class Wiring(unittest.TestCase):
    def validate_with(self, suggestions):
        from chatify import schema, theme, prompts, generators
        raw = schema.validate({})
        raw.update(appearance=theme.DEFAULT_CLEAN(),
                   pipeline_prompts={'text': {k: v['default'] or raw['prompt']['system'] for k, v in prompts.STAGES.items()}, 'on': {k: v['on'] for k, v in prompts.STAGES.items()}},
                   helper_drafts={k: {'brief': 'A reviewed helper draft', 'code': generators.code_template(k, '')} for k in ('search', 'clean_query')},
                   api_suggestions=suggestions)
        return appbuilder.validate(yaml.safe_dump(raw))
    S = {'name': 'OpenAlex', 'service': 'OpenAlex', 'reason': 'It grounds research answers in a broad open scholarly catalog.', 'connector': 'openalex', 'setup': 'Read the provider documentation and configure access before using it.', 'caveat': 'Check current quotas and availability before relying on it.'}
    def test_draft_suggestions_carry_verified_terms(self):
        r = self.validate_with([dict(self.S, docs_url='https://invented.example/', key_url='https://invented.example/key')])
        s = r['api_suggestions'][0]
        self.assertTrue(s['terms_verified'])
        self.assertIn('openalex.org', s['docs_url'])
        self.assertNotIn('invented.example', str(r['api_suggestions']))
    def test_model_written_terms_fields_are_dropped_then_server_attached(self):
        r = self.validate_with([dict(self.S, terms='FREE UNLIMITED FOREVER', terms_source='https://evil.example')])
        s = r['api_suggestions'][0]
        self.assertNotIn('UNLIMITED', s['terms'])
        self.assertNotEqual(s.get('terms_source'), 'https://evil.example')
    def test_unknown_service_gets_note_and_roundtrip_revalidates(self):
        r = self.validate_with([{'name': 'Mystery API', 'reason': 'A useful reason this service fits the app well.', 'connector': 'http_json', 'setup': 'Read the provider documentation and configure access first.', 'caveat': 'Check current quotas and availability before relying on it.'}])
        s = r['api_suggestions'][0]
        self.assertIn('not verified', s['terms'])
        appbuilder.validate(yaml.safe_dump(r))  # attached fields must survive a re-save validation

if __name__ == '__main__':
    unittest.main()
