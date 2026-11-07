"""Defensive generation/repair contracts, not semantic acceptance proof."""
import json
import unittest
from unittest.mock import Mock
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class DefensiveRepair(unittest.TestCase):
 def setup_engine(self, output):
  e=Engine(schema.validate({}),Store(':memory:'));e.cfg['provider']['type']='openai'
  class P:
   def complete(self,m):self.messages=m;return output
  e.provider=P();return e
 def sample(self):
  return ('The survey studied forest habitat conservation across regions.\n\nThe long term outcomes remain uncertain across all regions.', [{'n':1,'title':'Survey','text':'The survey studied forest habitat conservation across regions. The survey lacked a comparator group.'}])
 def test_all_flags_are_forwarded_without_short_warning_truncation(self):
  e=self.setup_engine('unchanged');a,v=self.sample();e.repair_support(a,v,'Survey','Note: the sources may not fully support this: short warning');self.assertIn('long term outcomes',e.provider.messages[-1]['content'])
 def test_invalid_stage_output_withholds_original_and_retains_warning(self):
  e=self.setup_engine('{"replacements": {}}');a,v=self.sample();out,_,_,note=e.repair_support(a,v,'Survey','Note: the sources may not fully support this: uncited');self.assertNotEqual(out,a);self.assertIn("No recommendation is provided",out);self.assertTrue(note)
 def test_answer_prompt_makes_overview_and_uncertainty_subject_to_evidence(self):
  e=self.setup_engine('{}');system=e.prompt('Explain conservation',[],'standard',[], '')[0]['content']
  self.assertIn('not citation-exempt',system);self.assertIn('Do not invent small sample sizes',system)

 def test_semantic_verdict_does_not_get_reduced_to_uncited_only_patch(self):
  e=self.setup_engine('unchanged');a,v=self.sample();e.repair_support(a,v,'Survey','Note: the sources may not fully support this: invented study limitations')
  self.assertNotIn('uncited_sentences',e.provider.messages[-1]['content']);self.assertIn('invented study limitations',e.provider.messages[-1]['content'])
