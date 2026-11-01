"""Vendor-schema metadata preservation, not live search/news qualification."""
import unittest
from unittest.mock import patch
from chatify import websearch
from chatify.connectors.web_search import WebSearch
class PublicationMetadata(unittest.TestCase):
 def normalize(self,date):return websearch.normalize('exa',{'results':[{'title':'Report','url':'https://example.invalid/report','publishedDate':date,'author':'Reporter','highlights':['An extract.']}]},3)
 def retrieve(self,rows):
  with patch.object(websearch,'has_key',return_value=True),patch.object(websearch,'search',return_value=rows):return WebSearch({'id':'news','label':'News','providers':['exa']}).search('peace report')
 def test_reported_date_and_author_survive(self):
  rows=self.retrieve(self.normalize('2026-10-30T12:00:00Z'));self.assertEqual(rows[0]['year'],'2026');self.assertEqual(rows[0]['published_date'],'2026-10-30T12:00:00Z');self.assertEqual(rows[0]['authors'],['Reporter']);self.assertIn('not independently verified',rows[0]['date_provenance'])
 def test_missing_date_does_not_invent_year(self):
  row=self.retrieve(self.normalize(None))[0];self.assertEqual(row['year'],'');self.assertNotIn('published_date',row)
 def test_invalid_date_does_not_become_year(self):
  row=self.retrieve(self.normalize('2026-99-99'))[0];self.assertEqual(row['year'],'');self.assertNotIn('published_date',row)
 def test_passage_year_is_not_publication_metadata(self):
  row=self.retrieve([{'title':'History in2026','url':'','text':'Events in2026.'}])[0];self.assertEqual(row['year'],'')
