"""Offline demo is extractive, not a model-quality verdict."""
import unittest
from chatify import providers,schema
from chatify.pipeline import Engine,evidence_record
from chatify.store import Store
class MockEnvelope(unittest.TestCase):
 def test_structured_envelope_quotes_passage_not_internal_metadata(self):
  e=Engine(schema.validate({}),Store(':memory:'));rows=[{'n':1,'title':'Alpha','text':'Docs about Alpha App. Other details.','authors':['A Person'],'year':'2025'}];messages=e.prompt('What is Alpha App?',rows,'standard',[],'');answer=e.provider.complete(messages);self.assertEqual(answer,'Docs about Alpha App. [1]');self.assertNotIn('Returned record metadata',answer);self.assertNotIn('Passage:',answer);self.assertIn('A Person',messages[1]['content'])
 def test_legacy_evidence_still_supported(self):
  self.assertEqual(providers.Mock({}).complete([{'content':'Evidence:\n[2] Source (2025; source: docs). Original quoted passage. Second sentence.'}]),'Original quoted passage. [2]')
 def test_source_content_marker_not_reinterpreted_as_framing(self):
  row={'n':3,'title':'Title','text':'Passage: This marker is source content. Next sentence.'};answer=providers.Mock({}).complete([{'content':'Evidence:\n'+evidence_record(row)}]);self.assertEqual(answer,'Passage: This marker is source content. [3]')
 def test_stream_matches_complete(self):
  model=providers.Mock({});messages=[{'content':'Evidence:\n'+evidence_record({'n':1,'title':'A','text':'One sentence.'})+'\n'+evidence_record({'n':2,'title':'B','text':'Second record.'})}];self.assertEqual(model.complete(messages),'One sentence. [1] Second record. [2]');self.assertEqual(''.join(model.stream(messages)),model.complete(messages))
if __name__=='__main__':unittest.main()
