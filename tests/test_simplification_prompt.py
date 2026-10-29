import unittest
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class SimplificationPrompt(unittest.TestCase):
 def test_plain_explanation_keeps_core_and_limit_not_all_numbers(self):
  e=Engine(schema.validate({}),Store(':memory:'))
  s=e.prompt('Explain that more simply using the same sources.',[],'standard',[], '')[0]['content']
  for phrase in ['noticeably shorter','120 words','most important limitation','Do not turn a hazard ratio into a percentage','every factual sentence cited']:self.assertIn(phrase,s)
 def test_regular_broad_answer_not_forced_short(self):
  e=Engine(schema.validate({}),Store(':memory:'))
  s=e.prompt('Compare randomized and observational evidence.',[],'standard',[], '')[0]['content']
  self.assertNotIn('This is a simplification request',s)

 def test_population_and_gap_claims_do_not_exceed_passage(self):
  e=Engine(schema.validate({}),Store(':memory:'))
  s=e.prompt('Compare research',[],'standard',[],'')[0]['content']
  self.assertIn('men and women does not establish age eligibility',s)
  self.assertIn('name the exact missing field',s)

 def test_negative_measurement_claim_keeps_source_frequency(self):
  e=Engine(schema.validate({}),Store(':memory:'))
  s=e.prompt('Explain that more simply.',[],'standard',[],'')[0]['content']
  self.assertIn('no yearly repeated measurements does not mean no repeated measurements at any interval',s)
  self.assertIn('Do not broaden a source limitation',s)

 def test_absence_claim_scope_stays_with_supplied_excerpt(self):
  e=Engine(schema.validate({}),Store(':memory:'))
  s=e.prompt('Compare randomized and observational studies.',[],'standard',[],'')[0]['content']
  self.assertIn('does not establish that the full paper or review omitted those results',s)
  self.assertIn('Keep this scope explicit in each absence sentence',s)
