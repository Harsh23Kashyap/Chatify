"""OpenAlex title fallback contract; synthetic API shapes, not live API evidence."""
import copy
import unittest
from unittest.mock import patch
from chatify.connectors.open_sources import OpenAlex
from chatify.pipeline import Engine
from chatify import schema
from chatify.store import Store

class OpenAlexTitleProvenance(unittest.TestCase):
 def row(self, inv=None, missing=False):
  item={'id':'https://openalex.org/W123','title':'Soil health','doi':'https://doi.org/10.test/soil','publication_year':2026,'authorships':[{'author':{'display_name':'A Researcher'}}],'primary_location':{'source':{'display_name':'Journal'}}}
  if not missing:item['abstract_inverted_index']=inv
  before=copy.deepcopy(item)
  with patch('chatify.secrets.saved',return_value='test-placeholder'),patch('chatify.connectors.open_sources._get',return_value={'results':[item]}):
   rows=OpenAlex({'id':'oa','label':'OpenAlex'}).search('soil health',2)
  self.assertEqual(item,before)
  return rows[0]
 def test_missing_null_empty_abstract_has_explicit_kind(self):
  for inv in [None,{},[],{'Soil':[]}]:
   with self.subTest(inv=inv):self.assertEqual(self.row(inv)['content_kind'],'title_only')
  self.assertEqual(self.row(missing=True)['content_kind'],'title_only')
 def test_title_and_reference_unchanged(self):
  r=self.row();self.assertEqual(r['text'],r['title']);self.assertEqual(r['title'],'Soil health');self.assertEqual(r['url'],'https://doi.org/10.test/soil');self.assertEqual(r['year'],'2026');self.assertEqual(r['authors'],['A Researcher']);self.assertEqual(r['venue'],'Journal')
 def test_short_real_abstract_not_labelled(self):
  r=self.row({'Soil':[0]});self.assertEqual(r['text'],'Soil');self.assertNotIn('content_kind',r)
 def test_abstract_matching_title_not_labelled(self):
  r=self.row({'Soil':[0],'health':[1]});self.assertEqual(r['text'],r['title']);self.assertNotIn('content_kind',r)
 def test_real_abstract_reconstruction_unchanged(self):
  r=self.row({'soil':[2],'Good':[0],'supports':[1],'health.':[3]});self.assertEqual(r['text'],'Good supports soil health.');self.assertNotIn('content_kind',r)
 def test_generation_support_preview_exports_use_common_marker(self):
  from chatify.pipeline import evidence_text
  from chatify.support_verdicts import unverified_source_preview
  from chatify.exports import bibtex
  r=self.row();r['n']=1
  self.assertIn('Title-only metadata;',evidence_text(r));preview=unverified_source_preview([r]);self.assertEqual(preview['items'][0]['content_kind'],'title_only');self.assertFalse(preview['answer_verified']);self.assertIn('note = {Title only;',bibtex([r]))
 def test_retrieval_cache_retains_explicit_kind(self):
  cfg=schema.validate({'provider':{'type':'mock'},'memory':{'enabled':False},'retrieval':{'cache_ttl':0,'query_rewrite':False,'rerank':False},'sources':[{'id':'oa','type':'openalex','label':'OpenAlex'}]})
  engine=Engine(cfg,Store(':memory:'));row=self.row()
  with patch.object(engine.connectors['oa'],'search',return_value=[row]):
   first,errors=engine.retrieve('soil health');second,_=engine.retrieve('soil health')
  self.assertFalse(errors);self.assertTrue(first);self.assertEqual(first[0]['content_kind'],'title_only');self.assertEqual(second[0]['content_kind'],'title_only')
