import unittest
from chatify.pipeline import retrieval_topic
class ReportingClause(unittest.TestCase):
 def test_generic_reporting_request_does_not_become_topic(self):
  q='What did EXAMPLE find about cardiovascular outcomes? Include study population and important limits of the evidence.'
  self.assertEqual(retrieval_topic(q),'What did EXAMPLE find about cardiovascular outcomes?')
 def test_population_topic_is_kept(self):
  q='How does population growth affect crop yields?'
  self.assertEqual(retrieval_topic(q),q)
 def test_specific_population_requirement_is_kept(self):
  q='What did EXAMPLE find? Include outcomes for adults over 65.'
  self.assertEqual(retrieval_topic(q),q)
 def test_second_factual_question_is_kept(self):
  q='What did EXAMPLE find? What was the population?'
  self.assertEqual(retrieval_topic(q),q)
 def test_domain_limitation_request_is_kept(self):
  q='What limits water availability? Include population growth.'
  self.assertEqual(retrieval_topic(q),q)
 def test_search_ladder_uses_topic_but_keeps_substantive_constraints(self):
  from chatify import schema
  from chatify.pipeline import Engine
  from chatify.store import Store
  e=Engine(schema.validate({'sources':[{'id':'pm','label':'PubMed','type':'pubmed'}]}),Store(':memory:'))
  q='What did EXAMPLE find about cardiovascular outcomes?'
  self.assertEqual(e.queries(q),e.queries(q+' Include study population and important limits of the evidence.'))
  self.assertIn('Include outcomes for adults over 65',e.queries('What did EXAMPLE find? Include outcomes for adults over 65.')[0])
 def test_gate_preserves_topic_ranking_under_reporting_boilerplate(self):
  from chatify.pipeline import relevance_gate
  q='What did EXAMPLE find about diet cardiovascular outcomes?'
  ev=[{'id':'a','title':'EXAMPLE diet cardiovascular outcomes','text':'A trial of diet cardiovascular outcomes','source':'pm','score':1},{'id':'b','title':'EXAMPLE diet cohort','text':'Population evidence limits research important cardiovascular outcomes','source':'pm','score':1}]
  f=lambda question:[x['id'] for x in relevance_gate(question,[dict(x) for x in ev],public_ids={'pm'})]
  self.assertEqual(f(q),f(q+' Include study population and important limits of the evidence.'))

 def test_numeric_constraint_is_never_stripped(self):
  for q in ['What did trials find? Include evidence 2024.', 'What did trials find? Include study population 65 limits.']:
   self.assertEqual(retrieval_topic(q),q)
