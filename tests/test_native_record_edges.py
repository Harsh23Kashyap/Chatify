"""Synthetic schema-edge fixtures, except documented arXiv error wire shape.

Error schema source: https://info.arxiv.org/help/api/user-manual.html section3.4.
These tests do not claim live API availability or answer-model quality.
"""
import unittest,xml.etree.ElementTree as ET
from unittest.mock import patch
from chatify.connectors.arxiv import Arxiv
from chatify.connectors.open_sources import Crossref
NS='http://www.w3.org/2005/Atom'
def entry(identity='http://arxiv.org/abs/2504.03616v2',title='RAG study',summary='Returned abstract'):
 return '<entry><id>'+identity+'</id><title>'+title+'</title><summary>'+summary+'</summary></entry>'
class ArxivRecordEdges(unittest.TestCase):
 def search(self,xml):
  with patch('chatify.connectors.arxiv._request',return_value=ET.fromstring('<feed xmlns="'+NS+'">'+xml+'</feed>')) as request:
   result=Arxiv({'id':'arxiv','label':'arXiv'}).search('RAG',6)
  request.assert_called_once();return result
 def test_documented_api_error_is_failure_not_evidence(self):
  for identity in ['http://arxiv.org/api/errors#incorrect_id_format_for_1234.12345','https://arxiv.org/api/errors#test','https://export.arxiv.org/api/errors#test']:
   with self.subTest(identity=identity),self.assertRaisesRegex(ValueError,'API error instead of paper'):
    self.search(entry(identity,'Error','incorrect id format'))
 def test_mixed_error_feed_also_fails_not_partial_success(self):
  with self.assertRaises(ValueError):self.search(entry()+entry('http://arxiv.org/api/errors#test','Error'))
 def test_blank_or_missing_identity_or_title_not_evidence(self):
  self.assertEqual(self.search('<entry/>'+entry('')+entry(title=' ')),[])
 def test_empty_feed_valid_empty_result(self):self.assertEqual(self.search(''),[])
 def test_exact_duplicate_identity_deduplicated(self):
  self.assertEqual(len(self.search(entry()+entry())),1)
 def test_versions_not_conflated(self):
  rows=self.search(entry()+entry('http://arxiv.org/abs/2504.03616v1'));self.assertEqual(len(rows),2)
 def test_valid_paper_titled_error_not_blocked(self):
  self.assertEqual(self.search(entry(title='Error'))[0]['title'],'Error')
 def test_title_only_keeps_empty_abstract_not_invented(self):
  self.assertEqual(self.search(entry(summary=''))[0]['text'],'')
 def test_valid_oldstyle_identity_and_metadata_preserved(self):
  row=self.search(entry('http://arxiv.org/abs/hep-ex/0307015v1') .replace('</entry>','<author><name>A. Researcher</name></author><published>2003-07-07</published></entry>'))[0]
  self.assertEqual(row['url'],'http://arxiv.org/abs/hep-ex/0307015v1');self.assertEqual(row['authors'],['A. Researcher']);self.assertEqual(row['year'],'2003')
class CrossrefAuthorEdges(unittest.TestCase):
 def rows(self,authors):
  item={'title':['RAG study'],'DOI':'10.1234/example','author':authors}
  with patch('chatify.connectors.open_sources._get',return_value={'message':{'items':[item]}}):return Crossref({'id':'crossref','label':'Crossref'}).search('RAG',6)
 def test_nonlist_author_field_preserves_other_metadata(self):
  for value in [None,7,'A. Researcher',{'given':'A','family':'Lee'}]:
   with self.subTest(value=value):
    row=self.rows(value)[0];self.assertEqual(row['authors'],[]);self.assertEqual(row['title'],'RAG study');self.assertEqual(row['id'],'doi:10.1234/example')
 def test_malformed_parts_omitted_never_stringified(self):
  self.assertEqual(self.rows([{'given':42,'family':'Lee'},None,{}, {'given':' Ada ','family':['bad']},{'given':False,'family':''}])[0]['authors'],['Lee','Ada'])
 def test_normal_author_order_and_six_author_bound_preserved(self):
  self.assertEqual(self.rows([{'given':'A.','family':str(i)} for i in range(8)])[0]['authors'],['A. '+str(i) for i in range(6)])
class RetrievalEdgeIntegration(unittest.TestCase):
 def test_error_feed_record_never_reaches_evidence_and_other_source_survives(self):
  from chatify import schema
  from chatify.pipeline import Engine
  from chatify.store import Store
  cfg=schema.validate({'provider':{'type':'mock'},'sources':[{'id':'arxiv','type':'arxiv','label':'arXiv'},{'id':'crossref','type':'crossref','label':'Crossref'}],'retrieval':{'rerank':False,'query_rewrite':False,'query_expansion':False,'cache_ttl':0}})
  e=Engine(cfg,Store(':memory:'))
  feed=ET.fromstring('<feed xmlns="'+NS+'">'+entry('http://arxiv.org/api/errors#test','Error','retrieval augmented generation')+'</feed>')
  cross={'title':['Retrieval augmented generation research'],'DOI':'10.1234/example','URL':'https://doi.org/10.1234/example','abstract':'Retrieval augmented generation research compares retrieval methods.','author':[{'given':42,'family':'Lee'}]}
  with patch('chatify.connectors.arxiv._request',return_value=feed),patch('chatify.connectors.open_sources._get',return_value={'message':{'items':[cross]}}),patch.object(e.provider,'complete',side_effect=AssertionError('no model')):
   rows,errors=e.retrieve('retrieval augmented generation')
  self.assertEqual(errors,{'arxiv':'ValueError'});self.assertTrue(rows);self.assertEqual({r['source'] for r in rows},{'crossref'});self.assertEqual(rows[0]['authors'],['Lee']);self.assertNotIn('arxiv.org/api/errors',str(rows))
if __name__=='__main__':unittest.main()
