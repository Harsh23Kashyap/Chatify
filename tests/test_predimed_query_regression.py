"""Regression from real generated nutrition app, 2026-10-28.
The question verb 'find' constrained every query to abstracts containing find,
excluding the main PREDIMED outcome paper. These are query-contract tests,
not independent proof of retrieval recall or answer quality.
"""
import unittest
from chatify.connectors.pubmed import keywords
from chatify import schema
from chatify.pipeline import Engine,relevance_gate
from chatify.store import Store
class QueryRegression(unittest.TestCase):
 def test_question_verb_not_pubmed_constraint(self):
  self.assertEqual(keywords('What did PREDIMED find about the Mediterranean diet and cardiovascular outcomes?'),'PREDIMED Mediterranean diet cardiovascular outcomes')
 def test_ladder_keeps_named_trial_not_find(self):
  e=Engine(schema.validate({'sources':[{'type':'pubmed','id':'pm','label':'PubMed'}]}),Store(':memory:'))
  qs=e.queries('What did PREDIMED find about the Mediterranean diet and cardiovascular outcomes?')
  self.assertIn('PREDIMED Mediterranean diet',qs)
  self.assertNotIn('PREDIMED find',qs)
 def test_topic_terms_preserved(self):
  self.assertEqual(keywords('PREDIMED Mediterranean diet cardiovascular outcomes'),'PREDIMED Mediterranean diet cardiovascular outcomes')

class GateQuestionVerb(unittest.TestCase):
 def test_primary_outcome_is_not_dropped_for_question_verb(self):
  q='What did PREDIMED find about Mediterranean diet cardiovascular outcomes?'
  primary={'id':'primary','title':'PREDIMED Mediterranean diet cardiovascular outcomes','text':'Mediterranean diet cardiovascular outcomes in PREDIMED','score':1,'source':'pm'}
  adjacent={'id':'adjacent','title':'PREDIMED Mediterranean diet cardiovascular outcomes','text':'We find findings for PREDIMED Mediterranean diet cardiovascular outcomes','score':1,'source':'pm'}
  other={'id':'other','title':'PREDIMED Mediterranean diet','text':'PREDIMED diet outcomes','score':1,'source':'pm'}
  ids={x['id'] for x in relevance_gate(q,[primary,adjacent,other],public_ids={'pm'})}
  self.assertIn('primary',ids)
