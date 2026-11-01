"""Prompt/data construction only; actual response checked separately."""
import unittest
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class ReportingBoundaries(unittest.TestCase):
 def setUp(self):self.e=Engine(schema.validate({}),Store(':memory:'))
 def test_exact_metadata_and_provenance(self):
  ev=[{'n':1,'title':'Truce report','year':'2026','text':'Officials said a temporary ceasefire held.','published_date':'2026-10-29T01:48:26Z','date_provenance':'provider-reported publication date, not independently verified'}]
  m=self.e.prompt('What did this ceasefire achieve?',ev,'standard',[],'');self.assertIn('2026-10-29T01:48:26Z; provider-reported',m[1]['content'])
 def test_missing_date_preserves_year_fallback(self):
  m=self.e.prompt('What happened?',[{'n':1,'title':'Report','year':'','text':'Report text.'}],'standard',[],'');self.assertIn('(n.d.; source:',m[1]['content']);self.assertNotIn('2026-',m[1]['content'])
