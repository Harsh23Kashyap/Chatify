"""Sentence boundary contract, prompted by a real answer fragment after 'vs.'."""
import unittest
from chatify.pipeline import Engine
class CitationSentence(unittest.TestCase):
 def test_comparison_abbreviation_does_not_sever_citation(self):
  text='Participants lost 3.2 kg (vs. 0.7 kg in the control group, P < 0.001) with improved risk factors [1].'
  ev=[{'n':1,'title':'Trial','text':text,'year':'2026'}]
  ledger=Engine.ledger(text,ev)
  self.assertEqual(len(ledger),1)
  self.assertEqual(ledger[0]['cites'],[1])
  self.assertIn('Participants lost',ledger[0]['claim'])
 def test_actual_sentence_boundary_is_preserved(self):
  rows=Engine.ledger('One sentence has enough words here. Another cited sentence has enough words [1].',[{'n':1,'text':'Another cited sentence has enough words','title':'Trial'}])
  self.assertEqual(len(rows),2)

 def test_research_prompt_requires_correction_and_study_boundaries(self):
  from chatify import schema
  from chatify.store import Store
  e=Engine(schema.validate({'sources':[]}),Store(':memory:'))
  system=e.prompt('What did a trial find?',[],'standard',[], '')[0]['content']
  self.assertIn('revised primary report',system)
  self.assertIn('Preserve material limitations',system)
  self.assertIn('Do not blend outcomes from different trials',system)

 def test_correction_receives_every_flagged_claim_not_800_character_prefix(self):
  from chatify import schema
  from chatify.store import Store
  e=Engine(schema.validate({}),Store(':memory:'));e.cfg['provider']['type']='openai'
  claims=['Detailed factual sentence '+str(i)+' '+('evidence '*30) for i in range(8)]
  class P:
   def complete(self,m):self.message=m[-1]['content'];return 'unchanged'
  p=P();e.provider=p
  e.correct('Original answer', [{'n':1,'title':'Record','text':'record'}],[{'claim':c,'uncited':True} for c in claims])
  self.assertIn(claims[-1],p.message)
  self.assertIn('missing citations',p.message)
