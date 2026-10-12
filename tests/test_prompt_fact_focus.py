import unittest
from customchat import schema
from customchat.pipeline import Engine
from customchat.store import Store

class PromptFactFocus(unittest.TestCase):
 def test_missing_date_does_not_replace_requested_fact(self):
  e=Engine(schema.validate({}),Store(':memory:'))
  ev=[{'n':1,'title':'fixture','year':'','source':'b','text':'Source B reports5documents.'}]
  system=e.prompt('How many documents?',ev,'standard',[],'')[0]['content']
  self.assertIn('answer the requested fact first',system)
  self.assertIn('missing date is metadata',system)
  self.assertIn('When the question asks about publication dates',system)
  self.assertIn('different entity in the same passage',system)
 def test_named_entity_sentences_are_verbatim_not_canned(self):
  e=Engine(schema.validate({}),Store(':memory:'))
  ev=[{'n':1,'title':'fixture','year':'','source':'a','text':'Cedar accepts ZIP. The Demo provider is offline. Rowan owns Cedar.'}]
  user=e.prompt('What does Demo use?',ev,'standard',[],'')[1]['content']
  self.assertIn('Sentences mentioning the named entity',user)
  self.assertIn('[1] The Demo provider is offline.',user)
  self.assertNotIn('[1] Cedar accepts ZIP.',user)
