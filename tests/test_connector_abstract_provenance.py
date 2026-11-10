"""Connector-owned content-kind contract, not a semantic support bypass.

Synthetic Atom/Crossref fixtures check parser provenance. The preserved Nov9
provider rejection motivates explicit provenance, but is not a passing model run.
"""
import copy,io,json,pathlib,tempfile,unittest
from unittest.mock import Mock,patch
from chatify import schema
from chatify.connectors.arxiv import Arxiv
from chatify.connectors.open_sources import Crossref
from chatify.pipeline import Engine,evidence_record,evidence_text
from chatify.store import Store

LABEL='[Connector returned abstract text; not full-paper text] '

class ConnectorAbstractProvenance(unittest.TestCase):
 def arxiv(self,summary):
  import xml.etree.ElementTree as ET
  root=ET.fromstring('<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>https://arxiv.org/abs/test</id><title>Record title</title><summary>'+summary+'</summary></entry></feed>')
  with patch('chatify.connectors.arxiv._request',return_value=root):
   return Arxiv({'id':'ax','label':'arXiv'}).search('retrieval')[0]
 def crossref(self,abstract):
  item={'title':['Record title'],'abstract':abstract,'URL':'https://doi.org/test'}
  with patch('chatify.connectors.open_sources._get',return_value={'message':{'items':[item]}}):
   return Crossref({'id':'cr','label':'Crossref'}).search('retrieval')[0]
 def test_connector_origin_not_source_name_or_length(self):
  for row in (self.arxiv('Sparse retrieval compares methods.'),self.crossref('<jats:p>Sparse retrieval.</jats:p>')):
   self.assertEqual(row['content_kind'],'abstract');self.assertIn(LABEL,evidence_text(row));self.assertNotIn('[Connector returned',row['text'])
 def test_empty_summaries_and_abstracts_are_not_marked_abstract(self):
  for row in (self.arxiv('  '),self.crossref(''),self.crossref('<jats:p> </jats:p>')):
   self.assertEqual(row['content_kind'],'title_only');self.assertNotIn(LABEL,evidence_text(row))
 def test_title_unknown_and_fulltext_controls_no_inferred_abstract(self):
  for kind in (None,'unknown','fulltext','full_text','title_only'):
   row={'n':1,'title':'An abstract about retrieval','text':'Abstract: full paper body','source':'arxiv'}
   if kind is not None:row['content_kind']=kind
   before=copy.deepcopy(row);wire=evidence_record(row)
   self.assertNotIn(LABEL,wire);self.assertEqual(row,before)
   if kind=='title_only':self.assertIn('[Title-only metadata;',wire)
 def test_label_keeps_exact_bounded_text_nonmutating(self):
  row=self.arxiv('Sparse retrieval compares methods.');before=copy.deepcopy(row)
  self.assertEqual(evidence_text(row,6),LABEL+'Sparse');self.assertEqual(row,before)
 def engine(self):
  e=Engine(schema.validate({'provider':{'type':'openai','model':'gpt-4o-mini'},'sources':[]}),Store(':memory:'));e.provider=Mock();e._llm_on=lambda k:True;return e
 def test_answer_revision_correction_relevance_support_repair_same_view(self):
  e=self.engine();row=self.arxiv('Sparse retrieval compares methods.');row['n']=1;rows=[row]
  def check(messages):
   text=messages[-1]['content'];self.assertIn(LABEL+'Sparse retrieval compares methods.',text);self.assertIn('"content_kind": "abstract"',text)
  check(e.prompt('Explain more simply',rows,'standard',[],''))
  e.provider.complete.return_value='Sparse retrieval compares methods. [1]'
  e.revise('Sparse retrieval compares methods. [1]',rows,'Explain more simply');check(e.provider.complete.call_args.args[0])
  e.correct('Sparse retrieval compares methods. [1]',rows,[{'claim':'Sparse retrieval compares methods.','uncited':True}]);check(e.provider.complete.call_args.args[0])
  e.provider.complete.return_value='1';e.filter_relevant('retrieval',rows);check(e.provider.complete.call_args.args[0])
  e.provider.complete.return_value='UNSUPPORTED: example';note=e.check_support('Sparse retrieval compares methods. [1]',rows);check(e.provider.complete.call_args.args[0]);self.assertTrue(note.startswith('Note: the sources may not fully support this:'))
  e.provider.complete.reset_mock();e.provider.complete.return_value='Sparse retrieval compares methods. [1]'
  e.repair_support('Sparse retrieval compares methods. [1]',rows,'Explain more simply',note);check(e.provider.complete.call_args_list[0].args[0])
 def test_retrieval_cache_history_and_export_retain_kind(self):
  cfg=schema.validate({'provider':{'type':'mock'},'memory':{'enabled':False},'retrieval':{'cache_ttl':0,'query_rewrite':False,'rerank':False},'sources':[{'id':'ax','type':'arxiv','label':'arXiv'}]})
  with tempfile.TemporaryDirectory() as d:
   store=Store(d+'/proof.db');e=Engine(cfg,store);row=self.arxiv('Sparse retrieval compares methods.')
   with patch.object(e.connectors['ax'],'search',return_value=[row]):
    first,_=e.retrieve('sparse retrieval');second,_=e.retrieve('sparse retrieval')
   self.assertEqual(first[0]['content_kind'],'abstract');self.assertEqual(second[0]['content_kind'],'abstract')
   chat=store.new_chat('u')
   with patch.object(e,'retrieve',return_value=(first,{})):
    result=e.ask('u',chat,'Explain sparse retrieval',new_topic=True)
   reopened=Store(d+'/proof.db');self.assertEqual(reopened.turns('u',chat)[0]['evidence'][0]['content_kind'],'abstract')
   self.assertEqual(reopened.export_all('u')[0]['turns'][0]['evidence'][0]['content_kind'],'abstract')

if __name__=='__main__':unittest.main()
