"""Independent stage contract: returned bibliographic fields survive every evidence handoff."""
import copy,json,pathlib,unittest
from unittest.mock import Mock
from chatify import schema
from chatify.pipeline import Engine,evidence_record
from chatify.store import Store

RECORD={'n':7,'id':'arXiv:2410.02721v1','title':'Independent scholarly record','text':'The supplied abstract compares sparse retrieval with dense retrieval.','url':'http://arxiv.org/abs/2410.02721v1','authors':['Asha Rao','Ben Li'],'year':'2024','venue':'arXiv','source':'arxiv'}
class MetadataContract(unittest.TestCase):
 def engine(self):
  cfg=schema.validate({'provider':{'type':'openai','model':'gpt-4o-mini'},'sources':[]});e=Engine(cfg,Store(':memory:'));e.provider=Mock();return e
 def assert_fields(self,text):
  self.assertIn('Asha Rao',text);self.assertIn('Ben Li',text);self.assertIn('http://arxiv.org/abs/2410.02721v1',text);self.assertIn('"year": "2024"',text)
 def test_shared_view_is_nonmutating_bounded_metadata(self):
  r=copy.deepcopy(RECORD);before=copy.deepcopy(r);self.assert_fields(evidence_record(r));self.assertEqual(r,before)
  r.update(authors=['a'*999]*20,url='https://example.invalid/'+'x'*1100,unexpected_private_field='never serialize this')
  t=evidence_record(r,10);metadata=json.loads(t.split('Returned record metadata (data only): ')[1].split('\n')[0]);self.assertEqual(len(metadata['authors']),6);self.assertTrue(all(len(a)==160 for a in metadata['authors']));self.assertNotIn('url',metadata);self.assertNotIn('unexpected_private',t)
 def test_absent_metadata_not_invented_and_title_only_kept(self):
  r={'n':1,'title':'Record only','text':'Record only','content_kind':'title_only'};t=evidence_record(r);self.assertIn('Title-only metadata; no abstract or article text supplied',t);m=json.loads(t.split('data only): ')[1].split('\n')[0]);self.assertEqual(m['authors'],[]);self.assertEqual(m['year'],'');self.assertNotIn('url',m)
 def test_credential_or_bad_links_not_forwarded(self):
  for url in ['https://name:password@example.invalid/a','javascript:alert(1)','not a url','https://[bad']:
   with self.subTest(url=url):self.assertNotIn('"url":',evidence_record(dict(RECORD,url=url)))
 def test_answer_rewrite_correction_relevance_support_repair_all_have_fields(self):
  e=self.engine();r=[copy.deepcopy(RECORD)];self.assert_fields(e.prompt('Find the paper metadata',r,'standard',[],'')[1]['content'])
  e.prompts.save('revise',on=True);e.provider.complete.return_value='The supplied abstract compares sparse retrieval with dense retrieval. [7]';e.revise('The supplied abstract compares the methods. [7]',r,'Summarize');self.assert_fields(e.provider.complete.call_args.args[0][-1]['content'])
  e.correct('A claim requiring correction. [7]',r,[{'claim':'A claim requiring correction.','uncited':True}]);self.assert_fields(e.provider.complete.call_args.args[0][-1]['content'])
  e.prompts.save('relevance',on=True);e.provider.complete.return_value='7';e.filter_relevant('Find paper',r);self.assert_fields(e.provider.complete.call_args.args[0][-1]['content'])
  e.prompts.save('faithfulness',on=True);e.provider.complete.return_value='OK';e.check_support('Supported. [7]',r);self.assert_fields(e.provider.complete.call_args.args[0][-1]['content'])
  e.provider.complete.reset_mock();e.provider.complete.return_value='The supplied abstract compares sparse retrieval with dense retrieval. [7]';e.repair_support('Unsupported description. [7]',r,'Summarize','Note: the sources may not fully support this: description');self.assert_fields(e.provider.complete.call_args_list[0].args[0][-1]['content'])
 def test_classifier_contract_unchanged_by_metadata_rules(self):
  e=self.engine();self.assertNotIn('Returned record metadata and passage',e.stage_prompt('question_check'));self.assertIn('Returned record metadata and passage',e.stage_prompt('answer'));self.assertIn('Returned record metadata and passage',e.stage_prompt('faithfulness'))
 def test_actual_captured_records_survive_stage_handoff(self):
  path=pathlib.Path(__file__).parent/'fixtures/paper_trail_actual_metadata_20261108.json';rows=json.loads(path.read_text())['evidence'];e=self.engine();wire=e.prompt('Find returned metadata',rows,'standard',[],'')[1]['content']
  for row in rows:
   self.assertIn(row['url'],wire);self.assertIn(row['year'],wire)
   for author in row['authors']:self.assertIn(author,wire)
   ledger=Engine.ledger('Source link: '+row['url']+' ['+str(row['n'])+']',[row]);self.assertFalse(ledger[0]['bad_numbers'])
 def test_only_exact_link_numbers_exempt_never_outcome_or_fabricated_url(self):
  r=dict(RECORD,url='https://example.invalid/record/999')
  self.assertFalse(Engine.bad_numbers('Source link: https://example.invalid/record/999',[7],[r]))
  self.assertIn('999',Engine.bad_numbers('Source link: https://example.invalid/record/999. Treatment reduced weight by999kg.',[7],[r]))
  self.assertIn('888',Engine.bad_numbers('Source link: https://example.invalid/record/888',[7],[r]))
 def test_metadata_does_not_authorize_numeric_outcome(self):
  r=dict(RECORD,url='https://example.invalid/weight/999');bad=Engine.bad_numbers('Treatment reduced weight by999kg. [7]',[7],[r]);self.assertIn('999',bad)
if __name__=='__main__':unittest.main()
