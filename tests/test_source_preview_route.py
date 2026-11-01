import unittest
from unittest.mock import patch,Mock
from chatify import schema
from chatify.pipeline import Engine
from chatify.store import Store
class PreviewRoute(unittest.TestCase):
 def engine(self):
  cfg=schema.validate({'prompt':{'source_preview_only':True},'memory':{'enabled':False},'sources':[]});e=Engine(cfg,Store(':memory:'));e.check_question=lambda *a:'';return e
 def evidence(self):return [{'n':1,'id':'1','title':'Temporary truce','text':'Officials reported 30 hours.\nAid was NOT delivered. Lasting peace was not claimed.','year':'2026','source':'web','url':'https://example.invalid/report','published_date':'2026-10-29','date_provenance':'provider-reported','score':1}]
 def test_sync_is_source_preview_not_synthesis(self):
  e=self.engine();chat=e.store.new_chat('o');e.provider.complete=Mock(side_effect=AssertionError('must not generate'))
  with patch.object(e,'retrieve',return_value=(self.evidence(),{})),patch.object(e,'filter_relevant',side_effect=lambda q,x:x):r=e.ask('o',chat,'What happened?')
  self.assertEqual(r['response_kind'],'source_preview');self.assertFalse(r['answer_verified']);self.assertEqual(r['ledger'],[]);self.assertIn('not a verified answer',r['answer']);self.assertIn('Aid was NOT delivered.',r['answer']);e.provider.complete.assert_not_called()
 def test_stream_contains_only_preview_no_generated_tokens(self):
  e=self.engine();e.provider.stream=Mock(side_effect=AssertionError('must not stream'));e.provider.complete=Mock(side_effect=AssertionError('must not generate'))
  with patch.object(e,'retrieve',return_value=(self.evidence(),{})),patch.object(e,'filter_relevant',side_effect=lambda q,x:x):events=list(e.ask_stream('o',None,'What happened?',temporary=True))
  r=next(data for kind,data in events if kind=='done');self.assertEqual(r['response_kind'],'source_preview');self.assertEqual(r['followups'],[]);self.assertTrue(all('not a verified answer' in data for kind,data in events if kind=='token'));e.provider.stream.assert_not_called();e.provider.complete.assert_not_called()
 def test_default_off_and_validation(self):
  self.assertFalse(schema.validate({})['prompt']['source_preview_only'])
  for x in ['true',1,None]:self.assertRaises(schema.ConfigError,schema.validate,{'prompt':{'source_preview_only':x}})
 def test_no_evidence_not_misclassified_preview(self):
  e=self.engine()
  with patch.object(e,'retrieve',return_value=([],{})),patch.object(e,'filter_relevant',side_effect=lambda q,x:x):r=e.ask('o',e.store.new_chat('o'),'What happened?')
  self.assertEqual(r['response_kind'],'answer');self.assertEqual(r['evidence'],[])

 def test_question_refusal_preserved_and_not_preview(self):
  e=self.engine();e.check_question=lambda *a:'Question outside this app.'
  with patch.object(e,'retrieve',return_value=(self.evidence(),{})),patch.object(e,'filter_relevant',side_effect=lambda q,x:x):r=e.ask('o',e.store.new_chat('o'),'Unrelated request')
  self.assertEqual(r['response_kind'],'question_refused');self.assertNotIn('not a verified answer',r['answer'])
 def test_omitted_large_passage_explicit_without_draft_replacement(self):
  e=self.engine();ev=self.evidence();ev[0]['text']='UNSAFE PARTIAL '*1500
  with patch.object(e,'retrieve',return_value=(ev,{})),patch.object(e,'filter_relevant',side_effect=lambda q,x:x):r=e.ask('o',e.store.new_chat('o'),'What happened?')
  self.assertEqual(r['response_kind'],'source_preview');self.assertIn('1 retrieved sources omitted',r['answer']);self.assertNotIn('UNSAFE PARTIAL',r['answer']);self.assertFalse(r['answer_verified'])
