import unittest
from chatify.pipeline import Engine
class ExactUrlBoundary(unittest.TestCase):
 def setUp(self):self.row={'n':1,'title':'A paper','year':'2025','text':'A description of retrieval.','url':'https://example.invalid/record/999'}
 def bad(self,text):return Engine.bad_numbers(text,[1],[self.row])
 def test_exact_bare_markdown_and_sentence_links_are_bibliographic(self):
  for text in ['Source: '+self.row['url'],self.row['url']+'.','[Source]('+self.row['url']+')',self.row['url']+', then cite.']:
   self.assertFalse(self.bad(text))
 def test_prefix_suffix_query_changed_url_not_exempt(self):
  for text in [self.row['url']+'kg',self.row['url']+'888',self.row['url']+'?effect=999kg',self.row['url']+'/999',self.row['url'].replace('999','888')]:
   self.assertTrue(self.bad(text),text)
 def test_source_link_never_supports_same_outcome_number(self):
  self.assertIn('999',self.bad(self.row['url']+' Treatment reduced weight by999kg.'))
 def test_foreign_citation_does_not_exempt_returned_link(self):
  self.assertIn('999',Engine.bad_numbers(self.row['url'],[2],[self.row]))
if __name__=='__main__':unittest.main()
