import unittest
from unittest.mock import patch
from chatify.connectors.open_sources import Crossref
from chatify.pipeline import Engine
from chatify import schema
from chatify.store import Store

class CrossrefTitleProvenance(unittest.TestCase):
 def rows(self,abstract=None):
  item={'title':['Soil sampling for soil health assessment'],'DOI':'10.1201/9781351114585-6','URL':'https://doi.org/10.1201/9781351114585-6','issued':{'date-parts':[[2018]]}}
  if abstract is not None:item['abstract']=abstract
  with patch('chatify.connectors.open_sources._get',return_value={'message':{'items':[item]}}) as get:
   rows=Crossref({'id':'crossref','label':'Crossref'}).search('soil health',2)
  get.assert_called_once();return rows
 def test_captured_title_only_shape_preserves_reference(self):
  row=self.rows()[0]
  self.assertEqual(row['content_kind'],'title_only');self.assertEqual(row['text'],row['title']);self.assertEqual(row['year'],'2018');self.assertEqual(row['url'],'https://doi.org/10.1201/9781351114585-6')
 def test_blank_or_markup_only_abstract_is_not_article_text(self):
  for abstract in ['', '  ', '<jats:p> </jats:p>']:
   with self.subTest(abstract=abstract):self.assertEqual(self.rows(abstract)[0]['content_kind'],'title_only')
 def test_short_real_abstract_not_misclassified_by_length(self):
  row=self.rows('<jats:p>Soil testing.</jats:p>')[0]
  self.assertEqual(row['text'],'Soil testing.');self.assertNotIn('content_kind',row)
 def test_prompt_record_has_provenance_without_fabricated_text(self):
  row=self.rows()[0];row['n']=1
  engine=Engine(schema.validate({'sources':[]}),Store(':memory:'))
  text=engine.prompt('soil health',[row],'standard',[],'')[-1]['content']
  self.assertIn('[Title-only metadata; no abstract or article text supplied] '+row['title'],text)
  row.pop('content_kind');text=engine.prompt('soil health',[row],'standard',[],'')[-1]['content']
  self.assertNotIn('[Title-only metadata;',text)

 def test_prompt_does_not_repeat_title_as_unlabeled_entity_passage(self):
  row=self.rows()[0];row['n']=1
  engine=Engine(schema.validate({'sources':[]}),Store(':memory:'))
  text=engine.prompt('Soil sampling',[row],'standard',[],'')[-1]['content']
  self.assertNotIn('Sentences mentioning the named entity',text)
 def test_serialized_evidence_label_keeps_exact_title_text(self):
  from chatify.pipeline import evidence_text
  row=self.rows()[0]
  self.assertEqual(evidence_text(row,4),'[Title-only metadata; no abstract or article text supplied] Soil')
  row.pop('content_kind');self.assertEqual(evidence_text(row,4),'Soil')
 def test_retrieval_and_memory_cache_preserve_explicit_kind(self):
  cfg=schema.validate({'provider':{'type':'mock'},'memory':{'enabled':False},'retrieval':{'cache_ttl':0,'query_rewrite':False,'rerank':False},'sources':[{'id':'crossref','type':'crossref','label':'Crossref'}]})
  engine=Engine(cfg,Store(':memory:'));row=self.rows()[0]
  with patch.object(engine.connectors['crossref'],'search',return_value=[row]):
   first,errors=engine.retrieve('soil sampling health');second,_=engine.retrieve('soil sampling health')
  self.assertFalse(errors);self.assertTrue(first);self.assertEqual(first[0]['content_kind'],'title_only');self.assertEqual(second[0]['content_kind'],'title_only')

 def test_support_check_receives_same_provenance(self):
  from unittest.mock import Mock
  row=self.rows()[0];row['n']=1
  engine=Engine(schema.validate({'sources':[]}),Store(':memory:'));engine._llm_on=lambda stage:True
  engine.provider.complete=Mock(return_value='OK')
  engine.check_support('Soil sampling [1].',[row])
  messages=engine.provider.complete.call_args.args[0]
  self.assertIn('[Title-only metadata; no abstract or article text supplied]',messages[-1]['content'])
