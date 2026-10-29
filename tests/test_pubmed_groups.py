"""PubMed collective authors are source metadata, not inferred trial aliases."""
import unittest
from unittest.mock import patch
from chatify.connectors.pubmed import PubMed
XML=b'''<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>123</PMID><Article><ArticleTitle>Primary Prevention of Disease</ArticleTitle><Abstract><AbstractText>Observed outcome.</AbstractText></Abstract><AuthorList><Author><CollectiveName>EXAMPLE Trial Investigators</CollectiveName></Author></AuthorList></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'''
class PubmedGroups(unittest.TestCase):
 @patch('chatify.connectors.pubmed._get',side_effect=[b'{"esearchresult":{"idlist":["123"]}}',XML])
 def test_preserves_collective_author_with_passage(self,get):
  row=PubMed({'id':'pm','label':'PubMed'}).search('EXAMPLE disease')[0]
  self.assertIn('EXAMPLE Trial Investigators',row['text'])
  self.assertIn('Observed outcome.',row['text'])
  self.assertEqual(row['title'],'Primary Prevention of Disease')
