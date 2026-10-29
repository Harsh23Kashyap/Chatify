import unittest
from chatify.pipeline import Engine
class PopulationAge(unittest.TestCase):
 def test_adult_not_inferred_from_men_women_or_risk(self):
  ev=[{'n':1,'title':'Trial','text':'3541 men and women at high cardiovascular risk were included.'}]
  l=Engine.ledger('The study included 3541 Spanish adults at high cardiovascular risk. [1]',ev)
  self.assertTrue(l[0]['population_age_added']);self.assertFalse(l[0]['supported'])
 def test_explicit_adult_or_age_criteria_not_flagged(self):
  for text in ['3541 adults were enrolled.','3541 participants aged 55 to 80 years were enrolled.']:
   l=Engine.ledger('The study enrolled 3541 adults. [1]',[{'n':1,'title':'Trial','text':text}])
   self.assertFalse(l[0]['population_age_added'])

 def test_children_age_range_does_not_establish_adults(self):
  ev=[{'n':1,'title':'Trial','text':'Participants aged 8 to 12 years were included.'}]
  self.assertTrue(Engine.ledger('Adults were included. [1]',ev)[0]['population_age_added'])
