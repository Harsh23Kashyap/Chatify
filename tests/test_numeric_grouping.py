import unittest
from chatify.pipeline import Engine
class GroupedNumbers(unittest.TestCase):
 def test_thin_space_grouped_population_matches_million(self):
  ev=[{'n':1,'title':'Umbrella review','text':'Total population 12\u2009800\u2009000 participants.'}]
  self.assertEqual(Engine.bad_numbers('The review covered 12.8 million people.',[1],ev),[])
 def test_different_million_value_still_rejected(self):
  ev=[{'n':1,'title':'Review','text':'Population 12\u2009800\u2009000.'}]
  self.assertIn('12900000',Engine.bad_numbers('12.9 million people.',[1],ev))
 def test_separate_numbers_do_not_merge(self):
  self.assertEqual(Engine.numbers('sample 12 and 800 people'),{'12','800'})
 def test_heading_does_not_join_citations_across_sections(self):
  rows=Engine.ledger('First supported finding. [1] [2]\n\n## Trial context\n\nSecond supported finding. [1]',[{'n':1,'title':'A','text':'First Second supported finding'},{'n':2,'title':'B','text':'First supported finding'}])
  self.assertEqual(len(rows),2);self.assertEqual(rows[1]['cites'],[1]);self.assertIn('Trial context',rows[1]['claim'])

 def test_spelled_compound_number_matches_digits(self):
  self.assertEqual(Engine.bad_numbers('69 studies.',[1],[{'n':1,'title':'Review','text':'Sixty-nine studies were included.'}]),[])
 def test_different_compound_number_stays_rejected(self):
  self.assertEqual(Engine.bad_numbers('68 studies.',[1],[{'n':1,'title':'Review','text':'Sixty-nine studies were included.'}]),['68'])

class SourceReferenceNumbers(unittest.TestCase):
 def test_one_review_is_not_an_invented_result_value(self):
  ev=[{'n':1,'title':'Review','text':'Mediterranean diets may prevent diabetes.'}]
  self.assertEqual(Engine.bad_numbers('One review says Mediterranean diets may prevent diabetes.',[1],ev),[])
  self.assertEqual(Engine.bad_numbers('One review says risk decreased by one percent.',[1],ev),['1'])

def test_one_umbrella_review_is_source_reference_not_precision():
    from chatify.pipeline import Engine
    evidence=[{'n':1,'title':'Meta-analyses','text':'Thirteen meta-analyses included studies.','year':2018}]
    assert Engine.bad_numbers('One umbrella review included meta-analyses.',[1],evidence)==[]
    assert Engine.bad_numbers('One systematic review found a 42 percent reduction.',[1],evidence)==['42']
