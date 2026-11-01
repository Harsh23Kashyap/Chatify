"""Synthetic recovery controls. Original live captured fixture was lost in reset."""
import unittest
from chatify.pipeline import relevance_gate
class SinglePredicateEntityGate(unittest.TestCase):
 def test_exact_entity_survives_synonymous_predicate(self):
  rows=[{'id':'1','source':'wikipedia','score':1,'title':'Good Friday Agreement','text':'The Good Friday Agreement in Northern Ireland created power sharing institutions.'},{'id':'2','source':'wikipedia','score':.5,'title':'Northern Ireland Executive','text':'The Good Friday Agreement established the Northern Ireland Executive.'},{'id':'3','source':'wikipedia','score':.3,'title':'Northern Ireland','text':'The Good Friday Agreement established government in Northern Ireland.'},{'id':'4','source':'wikipedia','score':.2,'title':'Black Friday shopping','text':'Friday shopping discounts.'}]
  titles={r['title'] for r in relevance_gate('What did the Good Friday Agreement establish in Northern Ireland?',rows,{'wikipedia'})}
  self.assertIn('Good Friday Agreement',titles);self.assertNotIn('Black Friday shopping',titles)
