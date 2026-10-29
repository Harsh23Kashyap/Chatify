import unittest
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class RevisionContext(unittest.TestCase):
 def test_revision_receives_question_and_preserves_simplification(self):
  e=Engine(schema.validate({}),Store(':memory:'));e.cfg['provider']['type']='openai';e._llm_on=lambda k:True
  answer='Shield volcanoes have runny lava, while stratovolcanoes have thicker lava. [1]'
  class P:
   def complete(self,m):self.messages=m;return answer
  e.provider=P();ev=[{'n':1,'title':'Volcanoes','text':'Volcano lava is described.'}]
  self.assertEqual(e.revise(answer,ev,'Explain that more simply.'),answer)
  self.assertIn('Explain that more simply.',e.provider.messages[-1]['content'])
  self.assertIn('Do not restore optional sample breakdowns',e.provider.messages[0]['content'])

 def test_revision_checks_source_absence_against_explicit_contrast(self):
  e=Engine(schema.validate({}),Store(':memory:'));e.cfg['provider']['type']='openai';e._llm_on=lambda k:True
  answer='Stratovolcanoes have explosive eruptions. [1]'
  class P:
   def complete(self,m):self.messages=m;return answer
  e.provider=P();ev=[{'n':1,'title':'Stratovolcano','text':'Unlike shield volcanoes, stratovolcanoes are characterized by explosive eruptions.'}]
  self.assertEqual(e.revise(answer,ev,'Compare these volcanoes.'),answer)
  self.assertIn('caveat that contradicts an explicit cited contrast',e.provider.messages[0]['content'])
  self.assertIn('Unlike shield volcanoes',e.provider.messages[1]['content'])
